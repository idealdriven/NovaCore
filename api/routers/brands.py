from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional
import uuid
import logging
import traceback

from models import Brand, Client, Owner
from schemas import Brand as BrandSchema
from schemas import BrandCreate, BrandUpdate
from database import get_db
from auth.jwt import get_current_active_user
from api.dependencies import get_pagination

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter()

# Helper function to check if user has access to the client
async def get_brand_client_owner(
    brand_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Owner = Depends(get_current_active_user)
):
    try:
        # Get the brand
        result = await db.execute(select(Brand).filter(Brand.id == brand_id))
        brand = result.scalars().first()
        
        if not brand:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Brand with ID {brand_id} not found"
            )
        
        # Check if user has access to the client that owns this brand
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
        logger.error(f"Error in get_brand_client_owner: {str(e)}")
        logger.error(traceback.format_exc())
        raise

@router.post("/", response_model=BrandSchema, status_code=status.HTTP_201_CREATED)
async def create_brand(
    brand_in: BrandCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Owner = Depends(get_current_active_user)
):
    """
    Create a new brand.
    """
    try:
        # Check if user has access to the client
        result = await db.execute(select(Client).filter(Client.id == brand_in.client_id))
        client = result.scalars().first()
        
        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Client with ID {brand_in.client_id} not found"
            )
            
        if client.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions to create a brand for this client"
            )
        
        # Create new brand
        brand = Brand(**brand_in.model_dump())
        db.add(brand)
        await db.commit()
        await db.refresh(brand)
        return brand
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating brand: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while creating the brand: {str(e)}"
        )

@router.get("/", response_model=List[BrandSchema])
async def read_brands(
    client_id: Optional[uuid.UUID] = None,
    db: AsyncSession = Depends(get_db),
    current_user: Owner = Depends(get_current_active_user),
    pagination: dict = Depends(get_pagination)
):
    """
    Retrieve brands. Can filter by client_id.
    """
    try:
        skip = pagination["skip"]
        limit = pagination["limit"]
        
        # Base query
        query = select(Brand)
        
        # Filter by client_id if provided
        if client_id:
            # Check if user has access to the client
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
                    detail="Not enough permissions to access this client's brands"
                )
                
            query = query.filter(Brand.client_id == client_id)
        else:
            # If no client_id is provided, only show brands for clients owned by the current user
            client_subquery = select(Client.id).filter(Client.owner_id == current_user.id).scalar_subquery()
            query = query.filter(Brand.client_id.in_(client_subquery))
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        result = await db.execute(query)
        brands = result.scalars().all()
        
        return brands
    except Exception as e:
        logger.error(f"Error retrieving brands: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving brands: {str(e)}"
        )

@router.get("/{brand_id}", response_model=BrandSchema)
async def read_brand(
    brand_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Owner = Depends(get_brand_client_owner)
):
    """
    Get a specific brand by ID.
    """
    try:
        result = await db.execute(select(Brand).filter(Brand.id == brand_id))
        brand = result.scalars().first()
        
        if not brand:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Brand with ID {brand_id} not found"
            )
            
        return brand
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving brand: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving the brand: {str(e)}"
        )

@router.put("/{brand_id}", response_model=BrandSchema)
async def update_brand(
    brand_id: uuid.UUID,
    brand_in: BrandUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Owner = Depends(get_brand_client_owner)
):
    """
    Update a brand.
    """
    try:
        result = await db.execute(select(Brand).filter(Brand.id == brand_id))
        brand = result.scalars().first()
        
        if not brand:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Brand with ID {brand_id} not found"
            )
        
        # Update brand attributes
        update_data = brand_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(brand, field, value)
        
        await db.commit()
        await db.refresh(brand)
        
        return brand
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating brand: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while updating the brand: {str(e)}"
        )

@router.delete("/{brand_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_brand(
    brand_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Owner = Depends(get_brand_client_owner)
):
    """
    Delete a brand.
    """
    try:
        result = await db.execute(select(Brand).filter(Brand.id == brand_id))
        brand = result.scalars().first()
        
        if not brand:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Brand with ID {brand_id} not found"
            )
        
        await db.delete(brand)
        await db.commit()
        
        return None
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error deleting brand: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while deleting the brand: {str(e)}"
        ) 