from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional
from datetime import timedelta

from models import Owner
from schemas import Owner as OwnerSchema
from schemas import OwnerCreate, OwnerUpdate, Token
from database import get_db
from auth.security import get_password_hash, authenticate_user
from auth.jwt import create_access_token, get_current_active_user, ACCESS_TOKEN_EXPIRE_MINUTES
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter()

@router.post("/", response_model=OwnerSchema, status_code=status.HTTP_201_CREATED)
async def create_owner(
    owner_in: OwnerCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new owner.
    """
    # Check if email already exists
    result = await db.execute(select(Owner).filter(Owner.email == owner_in.email))
    existing_owner = result.scalars().first()
    
    if existing_owner:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create owner
    hashed_password = get_password_hash(owner_in.password)
    db_owner = Owner(
        email=owner_in.email,
        name=owner_in.name,
        hashed_password=hashed_password
    )
    
    db.add(db_owner)
    await db.commit()
    await db.refresh(db_owner)
    
    return db_owner

@router.get("/me", response_model=OwnerSchema)
async def read_owner_me(
    current_owner: Owner = Depends(get_current_active_user)
):
    """
    Get current owner.
    """
    return current_owner

@router.put("/me", response_model=OwnerSchema)
async def update_owner_me(
    owner_in: OwnerUpdate,
    current_owner: Owner = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update current owner.
    """
    # Update owner attributes
    if owner_in.email is not None:
        current_owner.email = owner_in.email
    
    if owner_in.name is not None:
        current_owner.name = owner_in.name
    
    if owner_in.password is not None:
        current_owner.hashed_password = get_password_hash(owner_in.password)
    
    if owner_in.is_active is not None:
        current_owner.is_active = owner_in.is_active
    
    db.add(current_owner)
    await db.commit()
    await db.refresh(current_owner)
    
    return current_owner

@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """
    Get access token.
    """
    # Authenticate user
    user = await authenticate_user(db, form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"} 