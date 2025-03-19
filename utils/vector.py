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

async def generate_embedding(text: str, model: str = "text-embedding-3-small") -> List[float]:
    """
    Generate an embedding vector for a text using OpenAI's embedding API.
    
    Args:
        text: The text to embed
        model: The embedding model to use:
               - text-embedding-3-small (1536 dimensions, faster/cheaper)
               - text-embedding-3-large (3072 dimensions, more powerful)
    
    Returns:
        A list of floats representing the embedding vector
    """
    try:
        # Check if API key is set
        if not openai.api_key:
            logger.warning("OpenAI API key not set. Using random embedding for development.")
            # For development, return a random embedding if API key is not set
            return list(np.random.uniform(-1, 1, 1536 if "small" in model else 3072))
        
        # Generate embedding using OpenAI
        response = await openai.Embedding.acreate(
            model=model,
            input=text,
            encoding_format="float"  # Get raw float values
        )
        
        # Extract the embedding from the response
        embedding = response["data"][0]["embedding"]
        return embedding
    
    except Exception as e:
        logger.error(f"Error generating embedding: {str(e)}")
        logger.error(traceback.format_exc())
        # Return random embedding as fallback
        return list(np.random.uniform(-1, 1, 1536 if "small" in model else 3072))

# Function to calculate vector similarity
def calculate_similarity(vec1: List[float], vec2: List[float]) -> float:
    """
    Calculate cosine similarity between two vectors.
    
    Args:
        vec1: First vector
        vec2: Second vector
        
    Returns:
        Cosine similarity score (0-1)
    """
    # Convert to numpy arrays for efficient computation
    array1 = np.array(vec1)
    array2 = np.array(vec2)
    
    # Calculate dot product
    dot_product = np.dot(array1, array2)
    
    # Calculate magnitudes
    magnitude1 = np.linalg.norm(array1)
    magnitude2 = np.linalg.norm(array2)
    
    # Calculate cosine similarity
    if magnitude1 == 0 or magnitude2 == 0:
        return 0.0
    
    cosine_similarity = dot_product / (magnitude1 * magnitude2)
    return float(cosine_similarity)

# Function to calculate BM25 text relevance
def calculate_bm25_score(query: str, text: str) -> float:
    """
    Calculate BM25 relevance score (simplified version).
    
    Args:
        query: Search query
        text: Text to score against query
        
    Returns:
        BM25 relevance score (0-1)
    """
    # Simple implementation with normalized score
    query_terms = set(query.lower().split())
    doc_terms = set(text.lower().split())
    
    if not query_terms or not doc_terms:
        return 0.0
    
    # Count term matches
    matches = len(query_terms.intersection(doc_terms))
    
    # Calculate score based on percentage of query terms present
    score = matches / len(query_terms)
    
    # Apply a length penalty for extremely long or short documents
    length_ratio = min(len(doc_terms), 100) / 100  # Cap at 100 terms
    length_factor = 0.5 + (length_ratio * 0.5)  # 0.5-1.0 range
    
    return score * length_factor

async def memory_similarity_search(
    db: AsyncSession,
    query: str,
    client_id: uuid.UUID,
    brand_id: Optional[uuid.UUID] = None,
    customer_id: Optional[uuid.UUID] = None,
    limit: int = 5,
    threshold: float = 0.6,
    hybrid_search: bool = True,
    vector_weight: float = 0.7,
    keyword_weight: float = 0.3
) -> List[Memory]:
    """
    Search for memories similar to the query using a hybrid approach combining:
    1. Vector embeddings similarity (semantic search)
    2. Keyword matching (lexical search)
    
    Args:
        db: Database session
        query: The search query text
        client_id: Client ID to filter memories
        brand_id: Optional brand ID to filter memories
        customer_id: Optional customer ID to filter memories
        limit: Maximum number of results to return
        threshold: Minimum combined similarity score (0-1)
        hybrid_search: Whether to use hybrid search (if False, uses only vector search)
        vector_weight: Weight to give to vector similarity (0-1)
        keyword_weight: Weight to give to keyword matching (0-1)
        
    Returns:
        List of Memory objects sorted by relevance
    """
    try:
        # Generate embedding for the search query
        query_embedding = await generate_embedding(query)
        
        # Fetch memories for this client/brand/customer
        stmt = select(Memory).where(Memory.client_id == client_id)
        
        if brand_id:
            stmt = stmt.where(Memory.brand_id == brand_id)
        
        if customer_id:
            stmt = stmt.where(Memory.customer_id == customer_id)
            
        result = await db.execute(stmt)
        memories = result.scalars().all()
        
        # Calculate similarity scores for each memory
        scored_memories = []
        
        for memory in memories:
            # Get or calculate the memory's embedding
            memory_embedding = json.loads(memory.embedding) if memory.embedding else await process_memory_embedding(memory.content)
            
            # Calculate vector similarity
            vector_similarity = calculate_similarity(query_embedding, memory_embedding)
            
            if hybrid_search:
                # Calculate keyword relevance (BM25 score)
                keyword_score = calculate_bm25_score(query, memory.content)
                
                # Calculate hybrid score with weights
                combined_score = (vector_similarity * vector_weight) + (keyword_score * keyword_weight)
            else:
                # Use only vector similarity
                combined_score = vector_similarity
            
            # Calculate recency boost (newer memories get slight preference)
            days_old = (memory.updated_at - memory.created_at).days if memory.updated_at else 0
            recency_factor = 1.0 - (min(days_old, 365) / 365 * 0.1)  # Max 10% penalty for old memories
            
            # Apply importance boost
            importance_boost = memory.importance_score if memory.importance_score is not None else 0.5
            
            # Final relevance score with boosts
            final_score = combined_score * recency_factor * (0.8 + (importance_boost * 0.2))
            
            if final_score >= threshold:
                scored_memories.append((memory, final_score))
        
        # Sort by score (descending) and return top results
        scored_memories.sort(key=lambda x: x[1], reverse=True)
        
        # Extract just the memories from scored_memories
        result_memories = [memory for memory, score in scored_memories[:limit]]
        
        logger.info(f"Memory search for '{query}' returned {len(result_memories)} results")
        return result_memories
        
    except Exception as e:
        logger.error(f"Error in memory search: {str(e)}")
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

async def detailed_memory_search(
    db: AsyncSession,
    query: str,
    client_id: uuid.UUID,
    brand_id: Optional[uuid.UUID] = None,
    customer_id: Optional[uuid.UUID] = None,
    limit: int = 5,
    threshold: float = 0.6,
    vector_weight: float = 0.7,
    keyword_weight: float = 0.3
) -> List[Dict[str, Any]]:
    """
    Search for memories with detailed scoring information for diagnostics.
    
    Args:
        Same as memory_similarity_search
        
    Returns:
        List of dictionaries with memory and detailed scoring information
    """
    try:
        # Generate embedding for the search query
        query_embedding = await generate_embedding(query)
        
        # Fetch memories for this client/brand/customer
        stmt = select(Memory).where(Memory.client_id == client_id)
        
        if brand_id:
            stmt = stmt.where(Memory.brand_id == brand_id)
        
        if customer_id:
            stmt = stmt.where(Memory.customer_id == customer_id)
            
        result = await db.execute(stmt)
        memories = result.scalars().all()
        
        # Calculate similarity scores for each memory
        detailed_results = []
        
        for memory in memories:
            # Get or calculate the memory's embedding
            memory_embedding = json.loads(memory.embedding) if memory.embedding else await process_memory_embedding(memory.content)
            
            # Calculate vector similarity
            vector_similarity = calculate_similarity(query_embedding, memory_embedding)
            
            # Calculate keyword relevance (BM25 score)
            keyword_score = calculate_bm25_score(query, memory.content)
            
            # Calculate hybrid score with weights
            combined_score = (vector_similarity * vector_weight) + (keyword_score * keyword_weight)
            
            # Calculate recency boost
            days_old = (memory.updated_at - memory.created_at).days if memory.updated_at else 0
            recency_factor = 1.0 - (min(days_old, 365) / 365 * 0.1)
            
            # Apply importance boost
            importance_boost = memory.importance_score if memory.importance_score is not None else 0.5
            importance_factor = 0.8 + (importance_boost * 0.2)
            
            # Final relevance score with boosts
            final_score = combined_score * recency_factor * importance_factor
            
            if final_score >= threshold:
                # Calculate matched query terms
                query_terms = set(query.lower().split())
                memory_terms = set(memory.content.lower().split())
                matched_terms = list(query_terms.intersection(memory_terms))
                
                # Create detailed result
                detailed_result = {
                    "memory": memory,
                    "scoring": {
                        "final_score": round(final_score, 4),
                        "vector_similarity": round(vector_similarity, 4),
                        "keyword_score": round(keyword_score, 4),
                        "combined_score": round(combined_score, 4),
                        "recency_factor": round(recency_factor, 4),
                        "importance_factor": round(importance_factor, 4),
                        "matched_terms": matched_terms,
                        "total_terms_matched": len(matched_terms),
                        "query_term_count": len(query_terms)
                    }
                }
                detailed_results.append(detailed_result)
        
        # Sort by final score (descending)
        detailed_results.sort(key=lambda x: x["scoring"]["final_score"], reverse=True)
        
        logger.info(f"Detailed memory search for '{query}' returned {len(detailed_results)} results")
        return detailed_results[:limit]
        
    except Exception as e:
        logger.error(f"Error in detailed memory search: {str(e)}")
        logger.error(traceback.format_exc())
        return [] 