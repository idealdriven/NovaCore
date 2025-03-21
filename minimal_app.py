from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
import logging
import os
import json
import uuid
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

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

# Create app
app = FastAPI(
    title="Atlas Minimal",
    description="Minimalist knowledge system for testing",
    version="0.1.0",
)

# Configure CORS
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

# Simple in-memory data store for testing
memories = []
clients = [{"id": "00000000-0000-0000-0000-000000000000", "name": "Atlas Admin"}]
brands = [{"id": "11111111-1111-1111-1111-111111111111", "name": "Test Brand", "client_id": "00000000-0000-0000-0000-000000000000"}]
conversations = []

# Error handling
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": f"An unexpected error occurred: {str(exc)}"},
    )

# Authentication routes
@app.post("/api/v1/direct-login")
async def direct_login(form_data: OAuth2PasswordRequestForm = Depends()):
    # Hard-coded test credentials
    if form_data.username == "admin@atlas.com" and form_data.password == "Atlas123!":
        # Create mock access token
        logger.info(f"Direct login successful for {form_data.username}")
        
        return {
            "access_token": "mock-token-for-testing-purposes-only",
            "token_type": "bearer",
            "owner": {
                "id": "00000000-0000-0000-0000-000000000000",
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

# Client routes
@app.get("/api/v1/clients")
async def get_clients():
    return clients

# Brand routes
@app.get("/api/v1/brands")
async def get_brands(client_id: Optional[str] = None):
    if client_id:
        return [brand for brand in brands if brand["client_id"] == client_id]
    return brands

# Memory routes
@app.post("/api/v1/memories")
async def create_memory(memory: Dict[str, Any]):
    memory_id = str(uuid.uuid4())
    memory["id"] = memory_id
    memory["created_at"] = datetime.now().isoformat()
    memory["updated_at"] = datetime.now().isoformat()
    memories.append(memory)
    return memory

@app.get("/api/v1/memories/search")
async def search_memories(query: str, limit: int = 5, brand_id: Optional[str] = None):
    # Simple search implementation (case-insensitive substring match)
    results = []
    query = query.lower()
    
    for memory in memories:
        content = memory.get("content", "").lower()
        title = memory.get("title", "").lower()
        
        if query in content or query in title:
            if not brand_id or memory.get("brand_id") == brand_id:
                results.append(memory)
                if len(results) >= limit:
                    break
    
    return results

# Chat endpoint
@app.post("/api/v1/chat")
async def chat(request: Dict[str, Any]):
    try:
        message = request.get("message", "")
        conversation_id = request.get("conversation_id")
        client_id = request.get("client_id")
        brand_id = request.get("brand_id")
        save_as_memory = request.get("save_as_memory", False)
        
        # Simple echo bot for testing
        response = f"You said: {message}"
        
        # Create conversation if it doesn't exist
        if not conversation_id:
            conversation_id = str(uuid.uuid4())
            conversations.append({
                "id": conversation_id,
                "client_id": client_id,
                "brand_id": brand_id,
                "messages": []
            })
        
        # Find or create conversation
        conversation = None
        for conv in conversations:
            if conv["id"] == conversation_id:
                conversation = conv
                break
        
        if not conversation:
            conversation = {
                "id": conversation_id,
                "client_id": client_id,
                "brand_id": brand_id,
                "messages": []
            }
            conversations.append(conversation)
        
        # Add messages to conversation
        conversation["messages"].append({
            "sender": "user",
            "content": message,
            "timestamp": datetime.now().isoformat()
        })
        
        conversation["messages"].append({
            "sender": "assistant",
            "content": response,
            "timestamp": datetime.now().isoformat()
        })
        
        # Save as memory if requested
        memory_id = None
        if save_as_memory:
            memory = {
                "id": str(uuid.uuid4()),
                "title": f"Conversation: {message[:30]}...",
                "content": f"User: {message}\n\nAtlas: {response}",
                "client_id": client_id,
                "brand_id": brand_id,
                "memory_type": "conversation",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            memories.append(memory)
            memory_id = memory["id"]
        
        # Find relevant memories for this conversation
        memories_used = []
        query = message.lower()
        for memory in memories:
            content = memory.get("content", "").lower()
            if query in content:
                if not brand_id or memory.get("brand_id") == brand_id:
                    memories_used.append(memory)
                    if len(memories_used) >= 3:
                        break
        
        return {
            "client_id": client_id,
            "brand_id": brand_id,
            "conversation_id": conversation_id,
            "message": message,
            "response": response,
            "memories_used": memories_used,
            "memory_created": memory_id
        }
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )

# Root path
@app.get("/")
async def root():
    return {"status": "ok", "message": "Welcome to Atlas Minimal API"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "minimal_app:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8000")),
        reload=True,
    ) 