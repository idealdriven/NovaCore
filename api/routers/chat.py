from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
import uuid
import logging
import traceback

from utils.llm import ChatRequest, call_llm
from database import get_db
from models import Client, Conversation, ConversationMessage
from utils.vector import memory_similarity_search

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/")
async def chat_with_atlas(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Chat with Atlas. This endpoint:
    1. Retrieves relevant context from memories
    2. Calls an LLM (OpenAI or Claude)
    3. Stores the conversation
    4. Returns the response
    """
    try:
        client_id = request.client_id
        message = request.message
        
        # Get relevant memories
        memories = await memory_similarity_search(
            db=db,
            query=message,
            client_id=client_id,
            limit=5,
            threshold=0.6
        )
        
        # Format context from memories
        context = ""
        if memories:
            context = "Here are some relevant memories:\n\n"
            for i, memory in enumerate(memories):
                context += f"Memory {i+1}: {memory.title}\n{memory.content}\n\n"
        else:
            context = "No relevant memories found."
        
        # Create or retrieve conversation
        conversation_id = request.conversation_id
        if not conversation_id:
            # Create a new conversation
            conversation = Conversation(
                client_id=client_id,
                title=message[:50] + "..." if len(message) > 50 else message
            )
            db.add(conversation)
            await db.commit()
            await db.refresh(conversation)
            conversation_id = conversation.id
        
        # System prompt
        system_prompt = """
        You are Atlas, an AI assistant with access to the user's memories.
        You can search for relevant information and provide helpful responses.
        If you don't have relevant memories, just say so and offer to remember new information.
        Keep responses concise, friendly, and helpful.
        """
        
        # Call LLM
        response = await call_llm(
            system_prompt=system_prompt,
            context=context,
            user_message=message,
            model="gpt-4o",
            provider="openai"
        )
        
        # Store the conversation
        message_count = await db.execute(
            f"SELECT COUNT(*) FROM conversation_messages WHERE conversation_id = '{conversation_id}'"
        )
        count = message_count.scalar_one()
        
        # Store user message
        user_message = ConversationMessage(
            conversation_id=conversation_id,
            sender="user",
            content=message,
            index=count
        )
        db.add(user_message)
        
        # Store assistant response
        assistant_message = ConversationMessage(
            conversation_id=conversation_id,
            sender="assistant",
            content=response,
            index=count + 1
        )
        db.add(assistant_message)
        
        await db.commit()
        
        return {
            "client_id": client_id,
            "conversation_id": str(conversation_id),
            "message": message,
            "response": response,
            "memories_used": [{"id": str(m.id), "title": m.title} for m in memories]
        }
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        ) 