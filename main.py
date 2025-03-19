from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
import logging
import os
from contextlib import asynccontextmanager

from api.config import settings
from api.routers import api_router
from database import initialize_db

# Import routers individually to avoid circular imports
from api.routers import owners, clients, memories, brands, customers
# Uncomment these as they are implemented
# from api.routers import conversations, strategic_plans, execution_logs, tasks

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Startup and shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize database
    try:
        await initialize_db()
        logger.info("Application startup complete")
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}")
        raise e
    
    yield
    
    # Shutdown: Close connections
    logger.info("Application shutdown")

# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API for the Atlas AI memory system",
    version="0.1.0",
    lifespan=lifespan,
)

# Set up CORS
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

# Include routers individually
app.include_router(owners.router, prefix=f"{settings.API_V1_STR}/owners", tags=["owners"])
app.include_router(clients.router, prefix=f"{settings.API_V1_STR}/clients", tags=["clients"])
app.include_router(brands.router, prefix=f"{settings.API_V1_STR}/brands", tags=["brands"])
app.include_router(customers.router, prefix=f"{settings.API_V1_STR}/customers", tags=["customers"])
app.include_router(memories.router, prefix=f"{settings.API_V1_STR}/memories", tags=["memories"])
# Uncomment these as they are implemented
# app.include_router(conversations.router, prefix=f"{settings.API_V1_STR}/conversations", tags=["conversations"])
# app.include_router(strategic_plans.router, prefix=f"{settings.API_V1_STR}/strategic-plans", tags=["strategic plans"])
# app.include_router(execution_logs.router, prefix=f"{settings.API_V1_STR}/execution-logs", tags=["execution logs"])
# app.include_router(tasks.router, prefix=f"{settings.API_V1_STR}/tasks", tags=["tasks"])

@app.get("/")
async def root():
    """
    Root endpoint for health check and API information.
    """
    return {
        "status": "online",
        "app_name": settings.PROJECT_NAME,
        "api_version": settings.API_V1_STR,
        "hierarchy": {
            "owner": {
                "description": "The account owner/administrator who logs in",
                "endpoints": "/api/v1/owners/"
            },
            "clients": {
                "description": "Organizations managed by owners (e.g., RALLY)",
                "endpoints": "/api/v1/clients/",
                "parent": "owner"
            },
            "brands": {
                "description": "Brands managed by clients (e.g., Ruby + Begonia)",
                "endpoints": "/api/v1/brands/",
                "parent": "clients"
            },
            "customers": {
                "description": "Customers associated with brands",
                "endpoints": "/api/v1/customers/",
                "parent": "brands"
            },
            "memories": {
                "description": "Knowledge items associated with clients and customers",
                "endpoints": "/api/v1/memories/",
                "parent": ["clients", "customers"]
            }
        },
        "documentation": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
