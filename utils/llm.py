import os
import openai
import anthropic
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

# Configure API keys
openai.api_key = os.getenv("OPENAI_API_KEY")
claude_api_key = os.getenv("ANTHROPIC_API_KEY")
claude_client = anthropic.Anthropic(api_key=claude_api_key) if claude_api_key else None

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    client_id: str
    message: str
    chat_history: Optional[List[ChatMessage]] = None
    conversation_id: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None

async def call_llm(system_prompt: str, context: str, user_message: str, model: str = "gpt-4o", provider: str = "openai"):
    """
    Call an LLM (either OpenAI or Anthropic) with the given prompts.
    
    Args:
        system_prompt: System instructions
        context: Relevant context from the memory database
        user_message: The user's message
        model: Model to use (gpt-4o, gpt-3.5-turbo, claude-3-opus, etc.)
        provider: Which provider to use ("openai" or "anthropic")
        
    Returns:
        The LLM's response as a string
    """
    full_prompt = f"{system_prompt}\n\nRELEVANT CONTEXT:\n{context}\n\nUSER MESSAGE: {user_message}\n\nYour response:"
    
    try:
        if provider == "anthropic" and claude_client:
            # Call Claude
            response = claude_client.messages.create(
                model=model,
                max_tokens=1000,
                messages=[
                    {"role": "user", "content": full_prompt}
                ]
            )
            return response.content[0].text
            
        else:
            # Default to OpenAI
            response = openai.ChatCompletion.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"CONTEXT: {context}\n\nUSER: {user_message}"}
                ],
                max_tokens=1000
            )
            return response.choices[0].message.content
            
    except Exception as e:
        print(f"Error calling LLM: {str(e)}")
        return "I'm sorry, I encountered an error while processing your request."

async def get_embedding(text: str, model: str = "text-embedding-ada-002"):
    """
    Get an embedding vector for the given text using OpenAI's embeddings API.
    
    Args:
        text: The text to embed
        model: The embedding model to use
        
    Returns:
        List of floats representing the embedding vector
    """
    try:
        response = openai.Embedding.create(
            input=[text],
            model=model
        )
        return response['data'][0]['embedding']
    except Exception as e:
        print(f"Error generating embedding: {str(e)}")
        return None 