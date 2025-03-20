from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
import logging
import os
import sys
from contextlib import asynccontextmanager

from database import initialize_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Global flag to track if database initialization succeeded
db_initialized = False

# Startup and shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    global db_initialized
    # Startup: Initialize database
    try:
        print("DEPLOYMENT: Application startup beginning")
        await initialize_db()
        db_initialized = True
        logger.info("DEPLOYMENT: Application startup complete - database initialized")
    except Exception as e:
        logger.error(f"DEPLOYMENT ERROR during startup: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        # We'll continue even if database initialization fails
        # This allows the app to start in a degraded state
        print("⚠️ DEPLOYMENT: Application starting in degraded state - database not available", file=sys.stderr)
    
    yield
    
    # Shutdown: Close connections
    logger.info("DEPLOYMENT: Application shutdown")

# Create FastAPI application
app = FastAPI(
    title="Atlas API",
    description="API for the Atlas memory system",
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

# Mount static files if the directory exists
static_dir = "static"
if os.path.isdir(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
    print(f"DEPLOYMENT: Static files mounted from {static_dir}")
else:
    print(f"DEPLOYMENT WARNING: Static directory {static_dir} not found")

# Minimal API endpoints for initial deployment
@app.get("/")
async def read_root():
    return {"message": "Welcome to Atlas API"}

@app.get("/health")
async def health_check():
    if db_initialized:
        return {"status": "ok", "database": "connected"}
    else:
        return JSONResponse(
            status_code=500,
            content={"status": "degraded", "database": "not connected"}
        )

# Only include routers if database is available
# This pattern allows the app to start even if DB is not available
@app.on_event("startup")
async def include_routers():
    global db_initialized
    
    if not db_initialized:
        print("DEPLOYMENT WARNING: Database not initialized, skipping router inclusion")
        return
        
    try:
        # Import API router
        print("DEPLOYMENT: Importing API routers")
        from api.config import settings
        from api.routers import api_router
        
        # Include API router
        app.include_router(api_router, prefix=settings.API_V1_STR)
        
        # Import routers individually to avoid circular imports
        from api.routers import owners, clients, memories, brands, customers, conversations
        from api.routers import chat
        
        # Include routers individually
        print("DEPLOYMENT: Including API routers")
        app.include_router(owners.router, prefix=f"{settings.API_V1_STR}/owners", tags=["owners"])
        app.include_router(clients.router, prefix=f"{settings.API_V1_STR}/clients", tags=["clients"])
        app.include_router(brands.router, prefix=f"{settings.API_V1_STR}/brands", tags=["brands"])
        app.include_router(customers.router, prefix=f"{settings.API_V1_STR}/customers", tags=["customers"])
        app.include_router(memories.router, prefix=f"{settings.API_V1_STR}/memories", tags=["memories"])
        app.include_router(conversations.router, prefix=f"{settings.API_V1_STR}/conversations", tags=["conversations"])
        app.include_router(chat.router, prefix=f"{settings.API_V1_STR}/chat", tags=["chat"])
        
        print("DEPLOYMENT: All routers included successfully")
    except Exception as e:
        db_initialized = False
        print(f"DEPLOYMENT ERROR including routers: {str(e)}", file=sys.stderr)
        import traceback
        print(traceback.format_exc(), file=sys.stderr)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8000)),
        reload=True,
    )
