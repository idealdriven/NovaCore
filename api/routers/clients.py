from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional
import uuid
import logging
import traceback

from models import Client, Owner
from schemas import Client as ClientSchema
from schemas import ClientCreate, ClientUpdate
from database import get_db
from auth.jwt import get_current_active_user
from api.dependencies import get_client_owner, get_pagination

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/", response_model=ClientSchema, status_code=status.HTTP_201_CREATED)
async def create_client(
    client_in: ClientCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Owner = Depends(get_current_active_user)
):
    """
    Create a new client.
    """
    try:
        # Log inputs for debugging
        logger.info(f"Creating client with data: {client_in.dict()}")
        logger.info(f"Current user: {current_user.id}, {current_user.email}")
        
        # Verify owner exists
        if client_in.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to create clients for other owners"
            )
        
        # Create client with only required fields first
        db_client = Client(
            name=client_in.name,
            owner_id=client_in.owner_id,
        )
        
        # Add optional fields if provided
        if client_in.description is not None:
            db_client.description = client_in.description
            
        if client_in.industry is not None:
            db_client.industry = client_in.industry
            
        if client_in.meta_data is not None:
            logger.info(f"Meta data: {client_in.meta_data}")
            db_client.meta_data = client_in.meta_data
        
        # Add to session
        db.add(db_client)
        await db.commit()
        await db.refresh(db_client)
        
        return db_client
    
    except Exception as e:
        # Log the full exception with traceback
        logger.error(f"Error creating client: {str(e)}")
        logger.error(traceback.format_exc())
        # Re-raise the exception
        raise

@router.get("/", response_model=List[ClientSchema])
async def read_clients(
    db: AsyncSession = Depends(get_db),
    current_user: Owner = Depends(get_current_active_user),
    pagination: dict = Depends(get_pagination)
):
    """
    Get all clients owned by current user.
    """
    # Build query
    query = select(Client).filter(Client.owner_id == current_user.id)
    
    # Apply pagination and ordering
    skip = pagination["skip"]
    limit = pagination["limit"]
    order_by = pagination["order_by"]
    order = pagination["order"]
    
    if order.lower() == "asc":
        query = query.order_by(getattr(Client, order_by).asc())
    else:
        query = query.order_by(getattr(Client, order_by).desc())
    
    query = query.offset(skip).limit(limit)
    
    # Execute query
    result = await db.execute(query)
    clients = result.scalars().all()
    
    return clients

@router.get("/{client_id}", response_model=ClientSchema)
async def read_client(
    client_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Owner = Depends(get_client_owner)
):
    """
    Get a client by ID.
    """
    # Query client
    result = await db.execute(
        select(Client).filter(Client.id == client_id)
    )
    client = result.scalars().first()
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    return client

@router.put("/{client_id}", response_model=ClientSchema)
async def update_client(
    client_id: uuid.UUID,
    client_in: ClientUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Owner = Depends(get_client_owner)
):
    """
    Update a client.
    """
    # Query client
    result = await db.execute(
        select(Client).filter(Client.id == client_id)
    )
    client = result.scalars().first()
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    # Update client attributes
    if client_in.name is not None:
        client.name = client_in.name
    
    if client_in.description is not None:
        client.description = client_in.description
    
    if client_in.industry is not None:
        client.industry = client_in.industry
    
    if client_in.is_active is not None:
        client.is_active = client_in.is_active
        
    if client_in.meta_data is not None:
        client.meta_data = client_in.meta_data
    
    db.add(client)
    await db.commit()
    await db.refresh(client)
    
    return client

@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_client(
    client_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Owner = Depends(get_client_owner)
):
    """
    Delete a client.
    """
    # Query client
    result = await db.execute(
        select(Client).filter(Client.id == client_id)
    )
    client = result.scalars().first()
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    # Delete client
    await db.delete(client)
    await db.commit()
    
    return None