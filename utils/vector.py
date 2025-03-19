import numpy as np
from typing import List, Optional, Tuple, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql import text
import openai
import os
from models import Memory, ConversationMessage
import logging
import json
import traceback
import uuid

# Configure OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY", "")

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def generate_embedding(text: str) -> List[float]:
    """
    Generate an embedding vector for a text using OpenAI's embedding API.
    """
    try:
        # Check if API key is set
        if not openai.api_key:
            logger.warning("OpenAI API key not set. Using random embedding for development.")
            # For development, return a random embedding if API key is not set
            return list(np.random.uniform(-1, 1, 1536))
        
        # Generate embedding using OpenAI
        response = await openai.Embedding.acreate(
            model="text-embedding-ada-002",
            input=text
        )
        
        # Extract the embedding from the response
        embedding = response["data"][0]["embedding"]
        return embedding
    
    except Exception as e:
        logger.error(f"Error generating embedding: {str(e)}")
        logger.error(traceback.format_exc())
        # Return random embedding as fallback
        return list(np.random.uniform(-1, 1, 1536))

async def memory_similarity_search(
    db: AsyncSession,
    query: str,
    client_id: uuid.UUID,
    customer_id: Optional[uuid.UUID] = None,
    brand_id: Optional[uuid.UUID] = None,
    limit: int = 5,
    min_score: float = 0.7
) -> List[Memory]:
    """
    Search for similar memories using vector similarity.
    Can filter by customer_id and/or brand_id if provided.
    """
    try:
        # Generate embedding for query
        query_embedding = await generate_embedding(query)
        
        # Log for debugging
        logger.info(f"Generated embedding for query: {query[:50]}...")
        
        try:
            # Check if pgvector extension is installed
            test_sql = text("SELECT 1 FROM pg_extension WHERE extname = 'vector'")
            result = await db.execute(test_sql)
            if not result.scalar():
                logger.error("pgvector extension is not installed in the database")
                return []
            
            # Convert embedding to PostgreSQL array format
            embedding_string = "{" + ",".join([str(x) for x in query_embedding]) + "}"
            
            # SQL query using cosine similarity with pgvector
            sql_base = """
            SELECT m.id, m.title, m.content, m.client_id, m.customer_id, m.brand_id, m.memory_type,
                   m.importance_score, m.last_accessed, m.access_count, m.tags,
                   m.meta_data, m.created_at, m.updated_at, m.related_memory_ids,
                   1 - (m.embedding <=> :embedding) as similarity
            FROM memories m
            WHERE m.client_id = :client_id
              AND m.embedding IS NOT NULL
              AND 1 - (m.embedding <=> :embedding) > :min_score
            """
            
            # Add customer_id filter if provided
            if customer_id:
                sql_base += " AND m.customer_id = :customer_id"
                
            # Add brand_id filter if provided
            if brand_id:
                sql_base += " AND m.brand_id = :brand_id"
            
            sql_base += """
            ORDER BY similarity DESC
            LIMIT :limit
            """
            
            # Execute query
            params = {
                "embedding": embedding_string,
                "client_id": str(client_id),
                "min_score": min_score,
                "limit": limit
            }
            
            if customer_id:
                params["customer_id"] = str(customer_id)
                
            if brand_id:
                params["brand_id"] = str(brand_id)
                
            search_result = await db.execute(text(sql_base), params)
            
        except Exception as vector_error:
            logger.error(f"Vector search error: {str(vector_error)}")
            logger.error(traceback.format_exc())
            
            # Fallback to non-vector search
            logger.info("Falling back to text-based search without vectors")
            sql_fallback_base = """
            SELECT m.id, m.title, m.content, m.client_id, m.customer_id, m.brand_id, m.memory_type,
                   m.importance_score, m.last_accessed, m.access_count, m.tags,
                   m.meta_data, m.created_at, m.updated_at, m.related_memory_ids,
                   0.7 as similarity
            FROM memories m
            WHERE m.client_id = :client_id
              AND (m.title ILIKE :query OR m.content ILIKE :query)
            """
            
            # Add customer_id filter if provided
            if customer_id:
                sql_fallback_base += " AND m.customer_id = :customer_id"
                
            # Add brand_id filter if provided  
            if brand_id:
                sql_fallback_base += " AND m.brand_id = :brand_id"
                
            sql_fallback_base += " LIMIT :limit"
            
            search_query = f"%{query}%"
            params = {
                "query": search_query,
                "client_id": str(client_id),
                "limit": limit
            }
            
            if customer_id:
                params["customer_id"] = str(customer_id)
                
            if brand_id:
                params["brand_id"] = str(brand_id)
                
            search_result = await db.execute(text(sql_fallback_base), params)
        
        # Get results and create Memory objects
        memories = []
        for row in search_result:
            memory = Memory(
                id=row.id,
                title=row.title,
                content=row.content,
                client_id=row.client_id,
                customer_id=row.customer_id,
                brand_id=row.brand_id,
                memory_type=row.memory_type,
                importance_score=row.importance_score,
                last_accessed=row.last_accessed,
                access_count=row.access_count,
                tags=row.tags,
                meta_data=row.meta_data,
                created_at=row.created_at,
                updated_at=row.updated_at,
                related_memory_ids=row.related_memory_ids
            )
            memories.append(memory)
        
        logger.info(f"Search returned {len(memories)} results")
        return memories
    
    except Exception as e:
        logger.error(f"Error in similarity search: {str(e)}")
        logger.error(traceback.format_exc())
        return []

async def process_memory_embedding(content: str) -> List[float]:
    """
    Process text content to generate an embedding vector.
    """
    try:
        # Generate embedding
        embedding = await generate_embedding(content)
        return embedding
    except Exception as e:
        logger.error(f"Error processing memory embedding: {str(e)}")
        logger.error(traceback.format_exc())
        # Return empty embedding in case of error
        return [] 