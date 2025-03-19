from fastapi import APIRouter
from api.config import settings

# Create API router
api_router = APIRouter()

# We'll include routers individually in main.py
# to avoid circular imports 