from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import logging
import os
from contextlib import asynccontextmanager
import json
from datetime import timedelta

from api.config import settings
from api.routers import api_router
from database import initialize_db

# Import routers individually to avoid circular imports
from api.routers import owners, clients, memories, brands, customers, conversations, strategic_plans, execution_logs, tasks
# Uncomment these as they are implemented
# from api.routers import memory_connections, knowledge_graph
# Custom GPT integration
from api.routers import conversations, gpt_bridge
from api.routers import chat

# For direct auth
from fastapi.security import OAuth2PasswordRequestForm
from auth.jwt import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
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
    title="Atlas Memory API",
    description="API for the Atlas AI memory system",
    version="0.1.0",
    lifespan=lifespan,
)

# Set up CORS
origins = [
    "*",
    "http://localhost",
    "http://localhost:8000",
    "http://localhost:3000",
    "https://atlas-api-4t8d.onrender.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

# Include routers individually
app.include_router(owners.router, prefix=f"{settings.API_V1_STR}/owners", tags=["owners"])
app.include_router(clients.router, prefix=f"{settings.API_V1_STR}/clients", tags=["clients"])
app.include_router(brands.router, prefix=f"{settings.API_V1_STR}/brands", tags=["brands"])
app.include_router(customers.router, prefix=f"{settings.API_V1_STR}/customers", tags=["customers"])
app.include_router(memories.router, prefix=f"{settings.API_V1_STR}/memories", tags=["memories"])
# Memory connections and knowledge graph - Temporarily disabled for deployment
# app.include_router(memory_connections.router, prefix=f"{settings.API_V1_STR}/memory-connections", tags=["memory connections"])
# app.include_router(knowledge_graph.router, prefix=f"{settings.API_V1_STR}/knowledge-graph", tags=["knowledge graph"])
# Custom GPT integration
app.include_router(conversations.router, prefix=f"{settings.API_V1_STR}/conversations", tags=["conversations"])
app.include_router(gpt_bridge.router, prefix=f"{settings.API_V1_STR}/gpt", tags=["gpt bridge"])
app.include_router(chat.router, prefix=f"{settings.API_V1_STR}/chat", tags=["chat"])
# Uncomment these as they are implemented
app.include_router(strategic_plans.router, prefix=f"{settings.API_V1_STR}/strategic_plans", tags=["strategic_plans"])
app.include_router(execution_logs.router, prefix=f"{settings.API_V1_STR}/execution_logs", tags=["execution_logs"])
app.include_router(tasks.router, prefix=f"{settings.API_V1_STR}/tasks", tags=["tasks"])

# Add a direct login endpoint for testing
@app.post(f"{settings.API_V1_STR}/direct-login")
async def direct_login(form_data: OAuth2PasswordRequestForm = Depends()):
    # Hard-coded test credentials
    if form_data.username == "admin@atlas.com" and form_data.password == "Atlas123!":
        # Create access token with long expiry for testing
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES * 10)  # 10x normal duration
        access_token = create_access_token(
            data={"sub": "admin@atlas.com", "name": "Atlas Admin"},
            expires_delta=access_token_expires
        )
        
        logger.info(f"Direct login successful for {form_data.username}")
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "owner": {
                "id": "00000000-0000-0000-0000-000000000000",  # Placeholder ID
                "name": "Atlas Admin",
                "email": "admin@atlas.com"
            }
        }
    else:
        logger.warning(f"Failed direct login attempt for {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

# Root path
@app.get("/")
async def read_root():
    return FileResponse("index.html")

# Health check
@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8000")),
        reload=True,
    )
