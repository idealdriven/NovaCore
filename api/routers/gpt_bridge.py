from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any, Optional
import uuid
import logging
import json
import traceback

from database import get_db
from schemas import GPTRequest, GPTResponse, ConversationMemory
from models import Client, Memory

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/gpt",
    tags=["gpt bridge"],
    responses={404: {"description": "Not found"}},
)

# In-memory storage for client sessions (replace with database in production)
CLIENT_SESSIONS = {}

@router.post("/bridge", response_model=GPTResponse)
async def gpt_bridge(
    request: GPTRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Main bridge endpoint for Custom GPT to interact with NovaCore.
    
    This endpoint handles:
    1. Authentication (via client_code or client_id)
    2. Context retrieval for the current conversation
    3. Storing the conversation after GPT responds
    """
    try:
        client_id = None
        
        # Handle authentication
        if request.client_code:
            # Authenticate using client code
            from api.routers.conversations import CLIENT_CODES
            if request.client_code not in CLIENT_CODES:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid client code"
                )
            client_id = CLIENT_CODES[request.client_code]
            
            # Store client_id in session for future requests
            session_id = generate_session_id()
            CLIENT_SESSIONS[session_id] = client_id
            
        elif request.client_id:
            # Use provided client_id
            client_id = request.client_id
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either client_code or client_id must be provided"
            )
        
        # Retrieve client information
        from sqlalchemy.future import select
        result = await db.execute(select(Client).filter(Client.id == client_id))
        client = result.scalars().first()
        
        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Client with ID {client_id} not found"
            )
        
        # Extract brand context if mentioned in the message
        brand_id = extract_brand_from_message(request.message, client_id, db)
        
        # Create conversation memory object
        # Generate a stable conversation ID based on the first few messages
        # or reuse one from conversation history if available
        conversation_id = extract_conversation_id(request.conversation_history) or f"chat_{uuid.uuid4().hex[:8]}"
        
        # Create memory object for context retrieval
        memory_request = ConversationMemory(
            client_id=client_id,
            brand_id=brand_id,
            conversation_id=conversation_id,
            message_index=len(request.conversation_history) // 2,  # Rough estimate of message count
            message=request.message,
            response=""  # Will be filled after GPT generates response
        )
        
        # Get context for this conversation
        from api.routers.conversations import get_conversation_context
        context_result = await get_conversation_context(memory_request, db)
        
        # Format response for GPT
        return GPTResponse(
            context=context_result.context_summary,
            relevant_memories=[
                {
                    "id": memory.id,
                    "title": memory.title,
                    "preview": memory.content[:150] + "..." if len(memory.content) > 150 else memory.content
                }
                for memory in context_result.relevant_memories
            ],
            suggested_topics=context_result.detected_topics
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in GPT bridge: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )

@router.post("/store_response", response_model=Dict[str, Any])
async def store_gpt_response(
    conversation: ConversationMemory,
    db: AsyncSession = Depends(get_db)
):
    """
    Store GPT's response to a conversation.
    This should be called after the GPT has generated a response.
    """
    try:
        # Store the conversation as a memory
        from api.routers.conversations import store_conversation_memory
        result = await store_conversation_memory(conversation, db)
        
        return {
            "success": True,
            "memory_id": result["memory_id"],
            "detected_topics": result["detected_topics"]
        }
    
    except Exception as e:
        logger.error(f"Error storing GPT response: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )

# Helper functions
def generate_session_id() -> str:
    """Generate a unique session ID"""
    return f"session_{uuid.uuid4().hex}"

def extract_conversation_id(conversation_history: List[Dict[str, str]]) -> Optional[str]:
    """Extract conversation ID from history if available"""
    if not conversation_history:
        return None
    
    # Check if we stored the conversation ID in a system message
    for message in conversation_history:
        if message.get("role") == "system" and "conversation_id:" in message.get("content", ""):
            # Extract conversation ID
            content = message.get("content", "")
            start_idx = content.find("conversation_id:") + len("conversation_id:")
            end_idx = content.find("\n", start_idx)
            if end_idx == -1:
                end_idx = len(content)
            return content[start_idx:end_idx].strip()
    
    return None

async def extract_brand_from_message(message: str, client_id: uuid.UUID, db: AsyncSession) -> Optional[uuid.UUID]:
    """
    Attempt to extract brand ID based on brand names mentioned in the message
    """
    try:
        # Get all brands for this client
        from sqlalchemy.future import select
        from models import Brand
        
        result = await db.execute(select(Brand).filter(Brand.client_id == client_id))
        brands = result.scalars().all()
        
        # Check if any brand names are mentioned in the message
        message_lower = message.lower()
        for brand in brands:
            if brand.name.lower() in message_lower:
                return brand.id
                
        return None
    except Exception as e:
        logger.error(f"Error extracting brand from message: {str(e)}")
        return None 