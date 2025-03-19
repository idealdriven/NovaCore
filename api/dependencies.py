from fastapi import Depends, HTTPException, status, Query
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List, Dict, Any
import uuid
import logging
import traceback

from database import get_db
from auth.jwt import get_current_user, get_current_active_user, get_current_optionally_active_user
from models import Owner, Client, Memory, Customer, Brand
from sqlalchemy.future import select

# Dependencies for authentication and authorization
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Set up logging
logger = logging.getLogger(__name__)

# Custom dependencies for authorization
async def get_client_owner(
    client_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Dependency to check if the current user owns the specified client.
    """
    try:
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
            
        return current_user
    except Exception as e:
        logger.error(f"Error in get_client_owner: {str(e)}")
        logger.error(traceback.format_exc())
        raise

async def get_memory_owner(
    memory_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Dependency to check if the current user has access to the specified memory.
    """
    try:
        result = await db.execute(select(Memory).filter(Memory.id == memory_id))
        memory = result.scalars().first()
        
        if not memory:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Memory with ID {memory_id} not found"
            )
            
        result = await db.execute(select(Client).filter(Client.id == memory.client_id))
        client = result.scalars().first()
        
        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Client with ID {memory.client_id} not found"
            )
            
        if client.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions to access this memory"
            )
            
        return current_user
    except Exception as e:
        logger.error(f"Error in get_memory_owner: {str(e)}")
        logger.error(traceback.format_exc())
        raise

async def get_customer_access(
    customer_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Dependency to check if the current user has access to the specified customer.
    """
    try:
        result = await db.execute(select(Customer).filter(Customer.id == customer_id))
        customer = result.scalars().first()
        
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Customer with ID {customer_id} not found"
            )
            
        result = await db.execute(select(Brand).filter(Brand.id == customer.brand_id))
        brand = result.scalars().first()
        
        if not brand:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Brand with ID {customer.brand_id} not found"
            )
            
        result = await db.execute(select(Client).filter(Client.id == brand.client_id))
        client = result.scalars().first()
        
        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Client with ID {brand.client_id} not found"
            )
            
        if client.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions to access this customer"
            )
            
        return current_user
    except Exception as e:
        logger.error(f"Error in get_customer_access: {str(e)}")
        logger.error(traceback.format_exc())
        raise

async def get_brand_access(
    brand_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Dependency to check if the current user has access to the specified brand.
    """
    try:
        result = await db.execute(select(Brand).filter(Brand.id == brand_id))
        brand = result.scalars().first()
        
        if not brand:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Brand with ID {brand_id} not found"
            )
            
        result = await db.execute(select(Client).filter(Client.id == brand.client_id))
        client = result.scalars().first()
        
        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Client with ID {brand.client_id} not found"
            )
            
        if client.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions to access this brand"
            )
            
        return current_user
    except Exception as e:
        logger.error(f"Error in get_brand_access: {str(e)}")
        logger.error(traceback.format_exc())
        raise

# Pagination dependency
def get_pagination(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    """
    Common pagination parameters
    """
    return {"skip": skip, "limit": limit} 