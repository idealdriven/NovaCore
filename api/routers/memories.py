from fastapi import APIRouter, Depends, HTTPException, status, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime
import logging
import traceback
import json
from sqlalchemy.sql import text
from sqlalchemy.orm import Session
from models import Memory, Client, Customer, Brand, Owner, MemoryConnection
from schemas import Memory as MemorySchema
from schemas import MemoryCreate, MemoryUpdate, ConnectedMemoryResponse, VectorSearchQuery, EnhancedSearchQuery, DetailedSearchResult
from database import get_db
from auth.jwt import get_current_active_user
from api.dependencies import get_client_owner, get_memory_owner, get_pagination, get_customer_access, get_brand_access
from utils.vector import process_memory_embedding, memory_similarity_search, detailed_memory_search
from utils.ai import calculate_importance_score, extract_key_topics
from utils.memory_analyzer import analyze_memory_content

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/simple", status_code=status.HTTP_201_CREATED)
async def create_simple_memory(
    request_data: Dict[str, Any],
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Ultra simplified memory creation for debugging.
    """
    try:
        # Print debug info
        print("==== MEMORY CREATION DEBUG ====")
        print(f"Request data: {request_data}")
        print(f"Current user: {current_user.id}, {current_user.email}")
        
        # Basic validation
        required_fields = ["title", "content", "client_id"]
        for field in required_fields:
            if field not in request_data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Missing required field: {field}"
                )
        
        # Verify client exists and user has access
        client_id = request_data.get("client_id")
        try:
            client_id_uuid = uuid.UUID(client_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid client_id format: {client_id}"
            )
            
        result = await db.execute(select(Client).filter(Client.id == client_id_uuid))
        client = result.scalars().first()
        
        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Client with ID {client_id} not found"
            )
            
        if client.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions to create a memory for this client"
            )
            
        # Verify customer if provided
        customer_id = request_data.get("customer_id")
        if customer_id:
            try:
                customer_id_uuid = uuid.UUID(customer_id)
                result = await db.execute(select(Customer).filter(Customer.id == customer_id_uuid))
                customer = result.scalars().first()
                
                if not customer:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Customer with ID {customer_id} not found"
                    )
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid customer_id format: {customer_id}"
                )
                
        # Verify brand if provided
        brand_id = request_data.get("brand_id")
        if brand_id:
            try:
                brand_id_uuid = uuid.UUID(brand_id)
                result = await db.execute(select(Brand).filter(Brand.id == brand_id_uuid))
                brand = result.scalars().first()
                
                if not brand:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Brand with ID {brand_id} not found"
                    )
                    
                # Check that brand belongs to the client
                if brand.client_id != client_id_uuid:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Brand with ID {brand_id} does not belong to client with ID {client_id}"
                    )
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid brand_id format: {brand_id}"
                )
        
        # Create memory using direct SQL to maximize debuggability
        query = text("""
            INSERT INTO memories (
                id, title, content, client_id, customer_id, brand_id, memory_type, importance_score, 
                created_at, updated_at
            ) VALUES (
                :id, :title, :content, :client_id, :customer_id, :brand_id, :memory_type, :importance_score,
                :created_at, :updated_at
            ) RETURNING id
        """)
        
        memory_id = uuid.UUID(request_data.get("id")) if "id" in request_data else uuid.uuid4()
        now = datetime.now()
        
        params = {
            "id": str(memory_id),
            "title": request_data.get("title"),
            "content": request_data.get("content"),
            "client_id": client_id,
            "customer_id": customer_id,
            "brand_id": brand_id,
            "memory_type": request_data.get("memory_type"),
            "importance_score": request_data.get("importance_score", 0.5),
            "created_at": request_data.get("created_at", now),
            "updated_at": request_data.get("updated_at", now)
        }
        
        print(f"SQL Params: {params}")
        
        result = await db.execute(query, params)
        await db.commit()
        
        return {"message": "Memory created successfully with direct SQL", "id": str(memory_id)}
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        print(f"Error: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while creating the memory: {str(e)}"
        )

@router.post("/", response_model=MemorySchema, status_code=status.HTTP_201_CREATED)
async def create_memory(
    memory_in: MemoryCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Create a new memory.
    """
    try:
        # Verify client exists and user has access
        result = await db.execute(select(Client).filter(Client.id == memory_in.client_id))
        client = result.scalars().first()
        
        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Client with ID {memory_in.client_id} not found"
            )
            
        if client.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions to create a memory for this client"
            )
            
        # Verify customer if provided
        if memory_in.customer_id:
            result = await db.execute(select(Customer).filter(Customer.id == memory_in.customer_id))
            customer = result.scalars().first()
            
            if not customer:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Customer with ID {memory_in.customer_id} not found"
                )
                
        # Verify brand if provided
        if memory_in.brand_id:
            result = await db.execute(select(Brand).filter(Brand.id == memory_in.brand_id))
            brand = result.scalars().first()
            
            if not brand:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Brand with ID {memory_in.brand_id} not found"
                )
                
            # Check that brand belongs to the client
            if brand.client_id != memory_in.client_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Brand with ID {memory_in.brand_id} does not belong to client with ID {memory_in.client_id}"
                )
        
        # Create memory
        memory_data = memory_in.model_dump()
        
        # Process embedding if content is provided
        if memory_data.get("content"):
            embedding = await process_memory_embedding(memory_data["content"])
            memory_data["embedding"] = embedding
            
            # Calculate importance score
            if "importance_score" not in memory_data or memory_data["importance_score"] is None:
                importance_score = await calculate_importance_score(memory_data["content"])
                memory_data["importance_score"] = importance_score
            
        memory = Memory(**memory_data)
        db.add(memory)
        await db.commit()
        await db.refresh(memory)
        
        return memory
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating memory: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while creating the memory: {str(e)}"
        )

@router.get("/", response_model=List[MemorySchema])
async def read_memories(
    client_id: uuid.UUID,
    customer_id: Optional[uuid.UUID] = None,
    brand_id: Optional[uuid.UUID] = None,
    memory_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_client_owner),
    pagination: dict = Depends(get_pagination)
):
    """
    Retrieve memories for a specific client. Can filter by memory_type, customer_id, and brand_id.
    """
    try:
        skip = pagination["skip"]
        limit = pagination["limit"]
        
        # Base query
        query = select(Memory).filter(Memory.client_id == client_id)
        
        # Apply filters
        if memory_type:
            query = query.filter(Memory.memory_type == memory_type)
            
        if customer_id:
            # Check if the customer belongs to this client
            # This is done by checking if the user has access to this customer
            _ = await get_customer_access(customer_id, db, current_user)
            query = query.filter(Memory.customer_id == customer_id)
            
        if brand_id:
            # Check if the brand belongs to this client
            # This is done by checking if the user has access to this brand
            _ = await get_brand_access(brand_id, db, current_user)
            query = query.filter(Memory.brand_id == brand_id)
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        result = await db.execute(query)
        memories = result.scalars().all()
        
        # Update access stats
        for memory in memories:
            memory.last_accessed = datetime.now()
            memory.access_count += 1
        
        await db.commit()
        
        return memories
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving memories: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving memories: {str(e)}"
        )

@router.get("/{memory_id}", response_model=MemorySchema)
async def read_memory(
    memory_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_memory_owner)
):
    """
    Get a specific memory by ID.
    """
    try:
        result = await db.execute(select(Memory).filter(Memory.id == memory_id))
        memory = result.scalars().first()
        
        if not memory:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Memory with ID {memory_id} not found"
            )
        
        # Update access stats
        memory.last_accessed = datetime.now()
        memory.access_count += 1
        await db.commit()
        
        return memory
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving memory: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving the memory: {str(e)}"
        )

@router.put("/{memory_id}", response_model=MemorySchema)
async def update_memory(
    memory_id: uuid.UUID,
    memory_in: MemoryUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_memory_owner)
):
    """
    Update a memory.
    """
    try:
        result = await db.execute(select(Memory).filter(Memory.id == memory_id))
        memory = result.scalars().first()
        
        if not memory:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Memory with ID {memory_id} not found"
            )
        
        # Handle customer_id update
        update_data = memory_in.model_dump(exclude_unset=True)
        if "customer_id" in update_data and update_data["customer_id"] is not None:
            # Verify customer exists and user has access
            result = await db.execute(select(Customer).filter(Customer.id == update_data["customer_id"]))
            customer = result.scalars().first()
            
            if not customer:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Customer with ID {update_data['customer_id']} not found"
                )
                
            # Verify user has access to this customer (through brand and client)
            _ = await get_customer_access(update_data["customer_id"], db, current_user)
        
        # Handle brand_id update
        if "brand_id" in update_data and update_data["brand_id"] is not None:
            # Verify brand exists and user has access
            result = await db.execute(select(Brand).filter(Brand.id == update_data["brand_id"]))
            brand = result.scalars().first()
            
            if not brand:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Brand with ID {update_data['brand_id']} not found"
                )
                
            # Verify user has access to this brand (through client)
            _ = await get_brand_access(update_data["brand_id"], db, current_user)
            
            # Check that brand belongs to the memory's client
            if brand.client_id != memory.client_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Brand with ID {update_data['brand_id']} does not belong to client with ID {memory.client_id}"
                )
        
        # Handle content update - regenerate embedding
        if "content" in update_data and update_data["content"]:
            embedding = await process_memory_embedding(update_data["content"])
            update_data["embedding"] = embedding
            
            # Recalculate importance score if not provided
            if "importance_score" not in update_data or update_data["importance_score"] is None:
                importance_score = await calculate_importance_score(update_data["content"])
                update_data["importance_score"] = importance_score
        
        # Update memory attributes
        for field, value in update_data.items():
            setattr(memory, field, value)
        
        await db.commit()
        await db.refresh(memory)
        
        return memory
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating memory: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while updating the memory: {str(e)}"
        )

@router.delete("/{memory_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_memory(
    memory_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_memory_owner)
):
    """
    Delete a memory.
    """
    try:
        result = await db.execute(select(Memory).filter(Memory.id == memory_id))
        memory = result.scalars().first()
        
        if not memory:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Memory with ID {memory_id} not found"
            )
        
        await db.delete(memory)
        await db.commit()
        
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error deleting memory: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while deleting the memory: {str(e)}"
        )

@router.post("/search", response_model=List[MemorySchema])
async def search_memories(
    search_query: VectorSearchQuery,
    customer_id: Optional[uuid.UUID] = None,
    brand_id: Optional[uuid.UUID] = None,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_client_owner)
):
    """
    Search memories using vector similarity.
    """
    try:
        # Check if user can access this customer if provided
        if customer_id:
            _ = await get_customer_access(customer_id, db, current_user)
            
        # Check if user can access this brand if provided
        if brand_id:
            _ = await get_brand_access(brand_id, db, current_user)
            
            # Check that brand belongs to the search query's client
            result = await db.execute(select(Brand).filter(Brand.id == brand_id))
            brand = result.scalars().first()
            
            if brand.client_id != search_query.client_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Brand with ID {brand_id} does not belong to client with ID {search_query.client_id}"
                )
        
        # Perform search - modify memory_similarity_search to include brand_id
        memories = await memory_similarity_search(
            db, 
            search_query.query, 
            search_query.client_id,
            customer_id=customer_id,
            brand_id=brand_id,
            limit=search_query.limit,
            min_score=search_query.min_score
        )
        
        # Update access stats
        for memory in memories:
            memory.last_accessed = datetime.now()
            memory.access_count += 1
        
        await db.commit()
        
        return memories
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error searching memories: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while searching memories: {str(e)}"
        )

@router.post("/analyze", response_model=Dict[str, Any])
async def analyze_and_suggest_associations(
    request_data: Dict[str, Any],
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Analyze memory content and suggest the most appropriate associations 
    (client, brand, customer) and other metadata.
    
    This endpoint helps determine where a particular piece of information should be stored
    in the hierarchical structure based on its content.
    """
    try:
        # Validate input
        required_fields = ["title", "content", "client_id"]
        for field in required_fields:
            if field not in request_data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Missing required field: {field}"
                )
        
        # Parse client_id
        try:
            client_id = uuid.UUID(request_data["client_id"])
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid client_id format"
            )
            
        # Verify client exists and user has access
        result = await db.execute(select(Client).filter(Client.id == client_id))
        client = result.scalars().first()
        
        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Client with ID {client_id} not found"
            )
            
        if client.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions to access this client"
            )
        
        # Get available brands for this client
        brands_result = await db.execute(select(Brand).filter(Brand.client_id == client_id))
        available_brands = [
            {
                "id": str(brand.id),
                "name": brand.name,
                "description": brand.description
            }
            for brand in brands_result.scalars().all()
        ]
        
        # Get available customers for this client's brands
        if available_brands:
            brand_ids = [uuid.UUID(brand["id"]) for brand in available_brands]
            customers_result = await db.execute(select(Customer).filter(Customer.brand_id.in_(brand_ids)))
            available_customers = [
                {
                    "id": str(customer.id),
                    "name": customer.name,
                    "brand_id": str(customer.brand_id)
                }
                for customer in customers_result.scalars().all()
            ]
        else:
            available_customers = []
        
        # Analyze the memory content
        analysis_result = await analyze_memory_content(
            request_data["title"],
            request_data["content"],
            client_id,
            available_brands,
            available_customers
        )
        
        return {
            "analysis": analysis_result,
            "available_brands": available_brands,
            "available_customers": available_customers
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing memory: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while analyzing the memory: {str(e)}"
        )

# Get a memory with all its connections
@router.get("/{memory_id}/with-connections", response_model=ConnectedMemoryResponse)
async def get_memory_with_connections(
    memory_id: uuid.UUID,
    connection_types: Optional[List[str]] = Query(None, description="Filter by connection types"),
    min_strength: Optional[float] = Query(0.0, description="Minimum connection strength", ge=0.0, le=1.0),
    db: Session = Depends(get_db),
    current_user: Owner = Depends(get_current_active_user)
):
    # First verify the user has access to this memory
    memory = await get_memory_access(memory_id, current_user, db)
    
    # Create the base response
    response = ConnectedMemoryResponse(memory=memory)
    
    # Get all outgoing connections for this memory
    query = db.query(MemoryConnection).filter(
        MemoryConnection.source_memory_id == memory_id
    )
    
    # Apply filters if provided
    if connection_types:
        query = query.filter(MemoryConnection.connection_type.in_(connection_types))
    if min_strength is not None:
        query = query.filter(MemoryConnection.connection_strength >= min_strength)
    
    connections = query.all()
    
    # Organize connections by type
    connected_memories = {}
    
    for connection in connections:
        # Verify access to the target memory
        try:
            target_memory = await get_memory_access(connection.target_memory_id, current_user, db)
            
            if connection.connection_type not in connected_memories:
                connected_memories[connection.connection_type] = []
            
            connected_memories[connection.connection_type].append(target_memory)
        except HTTPException:
            # Skip memories the user doesn't have access to
            continue
    
    response.connected_memories = connected_memories
    return response

# New enhanced search endpoint
@router.post("/enhanced-search", response_model=List[MemorySchema])
async def enhanced_memory_search(
    search_query: EnhancedSearchQuery,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Search memories using enhanced hybrid search combining vector similarity and keyword matching.
    
    - Vector similarity: Finds semantically similar memories even with different wording
    - Keyword matching: Finds memories containing exact search terms
    - Relevance scoring: Combines similarity, recency, and importance
    
    Returns list of memories sorted by relevance.
    """
    try:
        # Verify user has access to the client
        result = await db.execute(select(Client).filter(Client.id == search_query.client_id))
        client = result.scalars().first()
        
        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Client with ID {search_query.client_id} not found"
            )
            
        if client.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions to access this client"
            )
        
        # Verify access to brand if provided
        if search_query.brand_id:
            _ = await get_brand_access(search_query.brand_id, db, current_user)
        
        # Verify access to customer if provided
        if search_query.customer_id:
            _ = await get_customer_access(search_query.customer_id, db, current_user)
            
        # Perform enhanced search
        memories = await memory_similarity_search(
            db=db,
            query=search_query.query,
            client_id=search_query.client_id,
            brand_id=search_query.brand_id,
            customer_id=search_query.customer_id,
            limit=search_query.limit,
            threshold=search_query.threshold,
            hybrid_search=search_query.hybrid_search,
            vector_weight=search_query.vector_weight,
            keyword_weight=search_query.keyword_weight
        )
        
        return memories
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in enhanced search: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during search: {str(e)}"
        )

# Detailed search with scoring information
@router.post("/detailed-search", response_model=List[DetailedSearchResult])
async def detailed_memory_search_endpoint(
    search_query: EnhancedSearchQuery,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Search memories with detailed scoring information.
    
    Returns list of memories with scoring breakdown to help understand
    why certain memories are ranked higher than others.
    """
    try:
        # Verify user has access to the client
        result = await db.execute(select(Client).filter(Client.id == search_query.client_id))
        client = result.scalars().first()
        
        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Client with ID {search_query.client_id} not found"
            )
            
        if client.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions to access this client"
            )
        
        # Verify access to brand if provided
        if search_query.brand_id:
            _ = await get_brand_access(search_query.brand_id, db, current_user)
        
        # Verify access to customer if provided
        if search_query.customer_id:
            _ = await get_customer_access(search_query.customer_id, db, current_user)
            
        # Perform detailed search
        detailed_results = await detailed_memory_search(
            db=db,
            query=search_query.query,
            client_id=search_query.client_id,
            brand_id=search_query.brand_id,
            customer_id=search_query.customer_id,
            limit=search_query.limit,
            threshold=search_query.threshold,
            vector_weight=search_query.vector_weight,
            keyword_weight=search_query.keyword_weight
        )
        
        return detailed_results
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in detailed search: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during detailed search: {str(e)}"
        ) 