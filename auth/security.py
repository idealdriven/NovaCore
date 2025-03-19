from passlib.context import CryptContext
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models import Owner

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify that a password matches the hashed version."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password with bcrypt."""
    return pwd_context.hash(password)

async def authenticate_user(db: AsyncSession, email: str, password: str) -> Optional[Owner]:
    """Authenticate a user by email and password."""
    result = await db.execute(select(Owner).filter(Owner.email == email))
    user = result.scalars().first()
    
    if not user:
        return None
    
    if not verify_password(password, user.hashed_password):
        return None
    
    return user

async def get_user_by_email(db: AsyncSession, email: str) -> Optional[Owner]:
    """Get a user by email."""
    result = await db.execute(select(Owner).filter(Owner.email == email))
    return result.scalars().first() 