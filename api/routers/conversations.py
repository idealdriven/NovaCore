from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional, Dict, Any
import uuid
import logging
import json
import traceback
from datetime import datetime

from models import Memory, Owner, Client, Brand, Customer, Conversation
from schemas import ConversationCreate, ConversationResponse, ConversationMemory, ConversationContext
from database import get_db
from auth.jwt import get_current_active_user, get_current_optionally_active_user
from api.dependencies import get_client_owner, get_memory_access, get_brand_access
from utils.vector import memory_similarity_search
from utils.ai import extract_key_topics, calculate_importance_score
from utils.memory_connections import find_memory_connections

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/conversations",
    tags=["conversations"],
    responses={404: {"description": "Not found"}},
)

# Authentication via client code
CLIENT_CODES = {}  # This would be replaced with database storage

@router.post("/register", response_model=Dict[str, str])
async def register_client_code(
    client_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Owner = Depends(get_current_active_user)
):
    """
    Generate a unique code that clients can use to link their ChatGPT conversations.
    """
    try:
        # Verify user has access to this client
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
        
        # Generate a unique code (in production use a secure random generator)
        import random
        import string
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        
        # Store code -> client_id mapping (in production, store in database)
        CLIENT_CODES[code] = str(client_id)
        
        return {"client_code": code, "client_id": str(client_id), "expires_in": "30 days"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating client code: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )

@router.get("/authenticate/{client_code}", response_model=Dict[str, Any])
async def authenticate_client(
    client_code: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Authenticate a client using their client code.
    Returns client details to establish the conversation context.
    """
    try:
        # Check if code exists
        if client_code not in CLIENT_CODES:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invalid client code"
            )
        
        client_id = CLIENT_CODES[client_code]
        
        # Get client details
        result = await db.execute(select(Client).filter(Client.id == client_id))
        client = result.scalars().first()
        
        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Client with ID {client_id} not found"
            )
        
        # Get client's brands
        brands_result = await db.execute(select(Brand).filter(Brand.client_id == client_id))
        brands = brands_result.scalars().all()
        
        # Get client's most recent memories (limit 5)
        memories_result = await db.execute(
            select(Memory)
            .filter(Memory.client_id == client_id)
            .order_by(Memory.created_at.desc())
            .limit(5)
        )
        recent_memories = memories_result.scalars().all()
        
        # Return client context
        return {
            "client_id": str(client.id),
            "client_name": client.name,
            "brands": [{"id": str(brand.id), "name": brand.name} for brand in brands],
            "recent_memories": [
                {
                    "id": str(memory.id),
                    "title": memory.title,
                    "preview": memory.content[:100] + "..." if len(memory.content) > 100 else memory.content,
                    "created_at": memory.created_at.isoformat() if memory.created_at else None
                }
                for memory in recent_memories
            ]
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error authenticating client: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )

@router.post("/context", response_model=ConversationContext)
async def get_conversation_context(
    conversation_data: ConversationMemory,
    db: AsyncSession = Depends(get_db)
):
    """
    Get relevant context for a conversation based on the current message.
    This endpoint retrieves relevant memories and context to enhance the AI's response.
    """
    try:
        client_id = conversation_data.client_id
        message = conversation_data.message
        
        # Get client details
        result = await db.execute(select(Client).filter(Client.id == client_id))
        client = result.scalars().first()
        
        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Client with ID {client_id} not found"
            )
            
        # Extract key topics from the message
        topics = await extract_key_topics(message)
        
        # Perform memory search to find relevant memories
        relevant_memories = await memory_similarity_search(
            db=db,
            query=message,
            client_id=client_id,
            brand_id=conversation_data.brand_id,
            limit=5,
            threshold=0.6,
            hybrid_search=True
        )
        
        # Create a context summary
        context_items = []
        
        # Add client info
        context_items.append(f"Client: {client.name}")
        
        # Add brand info if available
        if conversation_data.brand_id:
            brand_result = await db.execute(select(Brand).filter(Brand.id == conversation_data.brand_id))
            brand = brand_result.scalars().first()
            if brand:
                context_items.append(f"Brand: {brand.name}")
        
        # Add relevant memory snippets
        for memory in relevant_memories:
            # Create a short summary (first 150 chars)
            snippet = memory.content[:150] + "..." if len(memory.content) > 150 else memory.content
            context_items.append(f"Related memory ({memory.memory_type}): {snippet}")
        
        # Combine into a full context string
        context_summary = "\n\n".join(context_items)
        
        # Return the context and relevant memories
        return ConversationContext(
            client_id=str(client_id),
            client_name=client.name,
            brand_id=str(conversation_data.brand_id) if conversation_data.brand_id else None,
            detected_topics=topics,
            context_summary=context_summary,
            relevant_memories=[
                {
                    "id": str(memory.id),
                    "title": memory.title,
                    "content": memory.content,
                    "memory_type": memory.memory_type,
                    "created_at": memory.created_at.isoformat() if memory.created_at else None
                }
                for memory in relevant_memories
            ]
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting conversation context: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )

@router.post("/store", response_model=Dict[str, Any])
async def store_conversation_memory(
    conversation_data: ConversationMemory,
    db: AsyncSession = Depends(get_db)
):
    """
    Store a conversation exchange as a memory.
    """
    try:
        client_id = conversation_data.client_id
        
        # Create a memory from the conversation
        memory = Memory(
            client_id=client_id,
            brand_id=conversation_data.brand_id,
            customer_id=conversation_data.customer_id,
            title=f"Conversation: {conversation_data.message[:50]}..." if len(conversation_data.message) > 50 else conversation_data.message,
            content=f"User: {conversation_data.message}\n\nAssistant: {conversation_data.response}",
            memory_type="conversation",
            importance_score=await calculate_importance_score(conversation_data.message),
            meta_data={
                "conversation_id": conversation_data.conversation_id,
                "message_index": conversation_data.message_index,
                "referenced_memories": conversation_data.referenced_memory_ids
            }
        )
        
        # Extract topics and add as tags
        topics = await extract_key_topics(conversation_data.message + " " + conversation_data.response)
        memory.tags = topics
        
        # Generate embedding for the memory
        from utils.vector import process_memory_embedding
        memory.embedding = await process_memory_embedding(memory.content)
        
        # Save to database
        db.add(memory)
        await db.commit()
        await db.refresh(memory)
        
        # Suggest connections to other memories
        from utils.memory_connections import find_memory_connections
        suggested_connections = await find_memory_connections(str(memory.id), db)
        
        return {
            "memory_id": str(memory.id),
            "success": True,
            "detected_topics": topics,
            "suggested_connections": suggested_connections[:3] if suggested_connections else []
        }
    
    except Exception as e:
        await db.rollback()
        logger.error(f"Error storing conversation memory: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        ) 