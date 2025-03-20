from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import logging
import os
from contextlib import asynccontextmanager

from api.config import settings
from api.routers import api_router
from database import initialize_db

# Import routers individually to avoid circular imports
from api.routers import owners, clients, memories, brands, customers, conversations
# Uncomment these as they are implemented
# from api.routers import strategic_plans, execution_logs, tasks
# Add new routers
# Temporarily disabled for deployment
# from api.routers import memory_connections, knowledge_graph
# Custom GPT integration
from api.routers import conversations, gpt_bridge
from api.routers import chat

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
    title="Atlas Memory API",
    description="API for the Atlas AI memory system",
    version="0.1.0",
    lifespan=lifespan,
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
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
# app.include_router(execution_logs.router, prefix=f"{settings.API_V1_STR}/execution-logs", tags=["execution logs"])
# app.include_router(tasks.router, prefix=f"{settings.API_V1_STR}/tasks", tags=["tasks"])

# Root path
@app.get("/")
async def read_root():
    return FileResponse("index.html")

# Health check
@app.get("/health")
async def health_check():
    return {"status": "ok"}

# Remove or comment out this duplicate route
# @app.get("/")
# async def root():
#     return {"message": "Welcome to Atlas API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
