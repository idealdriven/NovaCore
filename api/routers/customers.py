from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional
import uuid
import logging
import traceback

from models import Customer, Brand, Client, Owner
from schemas import Customer as CustomerSchema
from schemas import CustomerCreate, CustomerUpdate
from database import get_db
from auth.jwt import get_current_active_user
from api.dependencies import get_pagination

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter()

# Helper function to check if user has access to the brand via customer
async def get_customer_brand_owner(
    customer_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Owner = Depends(get_current_active_user)
):
    try:
        # Get the customer
        result = await db.execute(select(Customer).filter(Customer.id == customer_id))
        customer = result.scalars().first()
        
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Customer with ID {customer_id} not found"
            )
        
        # Get the brand
        result = await db.execute(select(Brand).filter(Brand.id == customer.brand_id))
        brand = result.scalars().first()
        
        if not brand:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Brand with ID {customer.brand_id} not found"
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
                detail="Not enough permissions to access this customer"
            )
            
        return current_user
    except Exception as e:
        logger.error(f"Error in get_customer_brand_owner: {str(e)}")
        logger.error(traceback.format_exc())
        raise

@router.post("/", response_model=CustomerSchema, status_code=status.HTTP_201_CREATED)
async def create_customer(
    customer_in: CustomerCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Owner = Depends(get_current_active_user)
):
    """
    Create a new customer.
    """
    try:
        # Check if user has access to the brand
        result = await db.execute(select(Brand).filter(Brand.id == customer_in.brand_id))
        brand = result.scalars().first()
        
        if not brand:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Brand with ID {customer_in.brand_id} not found"
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
                detail="Not enough permissions to create a customer for this brand"
            )
        
        # Create new customer
        customer = Customer(**customer_in.model_dump())
        db.add(customer)
        await db.commit()
        await db.refresh(customer)
        return customer
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating customer: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while creating the customer: {str(e)}"
        )

@router.get("/", response_model=List[CustomerSchema])
async def read_customers(
    brand_id: Optional[uuid.UUID] = None,
    db: AsyncSession = Depends(get_db),
    current_user: Owner = Depends(get_current_active_user),
    pagination: dict = Depends(get_pagination)
):
    """
    Retrieve customers. Can filter by brand_id.
    """
    try:
        skip = pagination["skip"]
        limit = pagination["limit"]
        
        # Base query
        query = select(Customer)
        
        # Filter by brand_id if provided
        if brand_id:
            # Check if user has access to the brand
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
                    detail="Not enough permissions to access this brand's customers"
                )
                
            query = query.filter(Customer.brand_id == brand_id)
        else:
            # If no brand_id is provided, only show customers for brands of clients owned by the current user
            client_subquery = select(Client.id).filter(Client.owner_id == current_user.id).scalar_subquery()
            brand_subquery = select(Brand.id).filter(Brand.client_id.in_(client_subquery)).scalar_subquery()
            query = query.filter(Customer.brand_id.in_(brand_subquery))
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        result = await db.execute(query)
        customers = result.scalars().all()
        
        return customers
    except Exception as e:
        logger.error(f"Error retrieving customers: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving customers: {str(e)}"
        )

@router.get("/{customer_id}", response_model=CustomerSchema)
async def read_customer(
    customer_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Owner = Depends(get_customer_brand_owner)
):
    """
    Get a specific customer by ID.
    """
    try:
        result = await db.execute(select(Customer).filter(Customer.id == customer_id))
        customer = result.scalars().first()
        
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Customer with ID {customer_id} not found"
            )
            
        return customer
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving customer: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving the customer: {str(e)}"
        )

@router.put("/{customer_id}", response_model=CustomerSchema)
async def update_customer(
    customer_id: uuid.UUID,
    customer_in: CustomerUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Owner = Depends(get_customer_brand_owner)
):
    """
    Update a customer.
    """
    try:
        result = await db.execute(select(Customer).filter(Customer.id == customer_id))
        customer = result.scalars().first()
        
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Customer with ID {customer_id} not found"
            )
        
        # Update customer attributes
        update_data = customer_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(customer, field, value)
        
        await db.commit()
        await db.refresh(customer)
        
        return customer
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating customer: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while updating the customer: {str(e)}"
        )

@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_customer(
    customer_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Owner = Depends(get_customer_brand_owner)
):
    """
    Delete a customer.
    """
    try:
        result = await db.execute(select(Customer).filter(Customer.id == customer_id))
        customer = result.scalars().first()
        
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Customer with ID {customer_id} not found"
            )
        
        await db.delete(customer)
        await db.commit()
        
        return None
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error deleting customer: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while deleting the customer: {str(e)}"
        ) 