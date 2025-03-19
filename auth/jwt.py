from datetime import datetime, timedelta
from typing import Optional, Any, Dict
import jwt
from jwt.exceptions import PyJWTError
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, HTTPBearer, HTTPAuthorizationCredentials
from fastapi.security.utils import get_authorization_scheme_param
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import ValidationError

from database import get_db
from auth.security import get_user_by_email
from schemas import TokenData
import os

# JWT configuration
SECRET_KEY = os.getenv("SECRET_KEY", "very_secret_key_change_in_production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# OAuth2 scheme - update tokenUrl to match our endpoint structure
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/owners/token")

# Optional OAuth2 scheme for endpoints that can work with or without authentication
class OptionalOAuth2PasswordBearer(OAuth2PasswordBearer):
    async def __call__(self, request: Request) -> Optional[str]:
        authorization = request.headers.get("Authorization")
        scheme, param = get_authorization_scheme_param(authorization)
        if not authorization or scheme.lower() != "bearer":
            return None
        return param

optionally_oauth2_scheme = OptionalOAuth2PasswordBearer(tokenUrl="/api/v1/owners/token")

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token with optional expiration time.
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    """
    Verify JWT token and return the current user.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode JWT token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        
        if email is None:
            raise credentials_exception
        
        token_data = TokenData(email=email)
    except (PyJWTError, ValidationError):
        raise credentials_exception
    
    # Get user from database
    user = await get_user_by_email(db, email=token_data.email)
    
    if user is None:
        raise credentials_exception
    
    return user

async def get_current_active_user(current_user = Depends(get_current_user)):
    """
    Check if the current user is active.
    """
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    return current_user

async def get_current_optionally_active_user(token: Optional[str] = Depends(optionally_oauth2_scheme), db: AsyncSession = Depends(get_db)):
    """
    Get the current user without requiring them to be active.
    Returns None if no valid token is provided.
    This is useful for endpoints that can work with or without authentication.
    """
    if not token:
        return None
        
    try:
        # Try to get current user
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        
        if email is None:
            return None
        
        # Get user from database
        user = await get_user_by_email(db, email=email)
        return user
    except (PyJWTError, ValidationError):
        return None 