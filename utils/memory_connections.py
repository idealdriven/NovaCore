import json
from typing import List, Dict, Any, Optional, Tuple
import asyncio
from sqlalchemy.orm import Session

# Temporarily disabled for deployment
# from models import Memory, MemoryConnection
from models import Memory
from utils.ai import extract_key_topics, calculate_importance_score
from utils.vector import memory_similarity_search

# Connection types
CONNECTION_TYPES = {
    "related": "General relationship between memories",
    "prerequisite": "This memory is a prerequisite for understanding the other",
    "followup": "This memory follows up or builds upon the other",
    "contradicts": "This memory contradicts or provides alternative view to the other",
    "elaborates": "This memory provides additional details on the other",
    "summarizes": "This memory summarizes the other",
}

async def analyze_potential_connection(
    source_memory: Memory,
    target_memory: Memory
) -> Tuple[str, float]:
    """
    Analyze two memories and suggest the most appropriate connection type
    and strength based on their content.
    
    Returns a tuple of (connection_type, connection_strength)
    """
    # Use keywords to determine the most likely connection type
    source_topics = set(extract_key_topics(source_memory.content))
    target_topics = set(extract_key_topics(target_memory.content))
    
    # Calculate Jaccard similarity between topics
    common_topics = source_topics.intersection(target_topics)
    all_topics = source_topics.union(target_topics)
    topic_similarity = len(common_topics) / len(all_topics) if all_topics else 0
    
    # Default connection type and strength
    connection_type = "related"
    connection_strength = min(0.4 + topic_similarity, 1.0)  # Base 0.4 plus similarity
    
    # Look for keyword indicators of different connection types
    source_lower = source_memory.content.lower()
    target_lower = target_memory.content.lower()
    
    # Check for contradiction indicators
    contradiction_indicators = ["however", "but", "instead", "contrary", "disagree", "opposite", "unlike"]
    if any(indicator in source_lower for indicator in contradiction_indicators) or \
       any(indicator in target_lower for indicator in contradiction_indicators):
        connection_type = "contradicts"
        connection_strength = 0.7
    
    # Check for prerequisite indicators
    prerequisite_indicators = ["first", "before", "prior", "foundation", "basis", "fundamental"]
    if any(indicator in source_lower for indicator in prerequisite_indicators):
        connection_type = "prerequisite"
        connection_strength = 0.8
    
    # Check for followup indicators
    followup_indicators = ["next", "then", "after", "followup", "following", "subsequently"]
    if any(indicator in source_lower for indicator in followup_indicators):
        connection_type = "followup"
        connection_strength = 0.8
    
    # Check for elaboration indicators
    elaboration_indicators = ["detail", "specifically", "elaborat", "expand", "more on", "further"]
    if any(indicator in source_lower for indicator in elaboration_indicators):
        connection_type = "elaborates"
        connection_strength = 0.9
    
    # Check for summary indicators
    summary_indicators = ["summary", "conclusion", "overview", "in short", "to summarize", "in brief"]
    if any(indicator in source_lower for indicator in summary_indicators):
        connection_type = "summarizes"
        connection_strength = 0.9
    
    # If we have too few common topics, limit the connection strength
    if len(common_topics) < 2 and connection_type == "related":
        connection_strength = min(connection_strength, 0.5)
    
    return connection_type, connection_strength

async def find_memory_connections(
    memory_id: str,
    db: Session,
    limit: int = 10,
    threshold: float = 0.6
) -> List[Dict[str, Any]]:
    """
    Find potential connections for a memory based on content similarity.
    
    Args:
        memory_id: UUID of the memory to find connections for
        db: Database session
        limit: Maximum number of connections to suggest
        threshold: Minimum similarity threshold
        
    Returns:
        List of suggested connections with connection type and strength
    """
    # Get the source memory
    source_memory = db.query(Memory).filter(Memory.id == memory_id).first()
    if not source_memory:
        return []
    
    # Find similar memories using vector search
    similar_memories = await memory_similarity_search(
        query=source_memory.content,
        db=db,
        client_id=source_memory.client_id,
        brand_id=source_memory.brand_id,
        limit=limit * 2,  # Get more results than needed to filter
        threshold=threshold
    )
    
    # Filter out the source memory itself
    similar_memories = [m for m in similar_memories if str(m.id) != str(memory_id)]
    
    # Analyze each potential connection
    suggestions = []
    for target_memory in similar_memories[:limit]:
        connection_type, connection_strength = await analyze_potential_connection(
            source_memory, target_memory
        )
        
        suggestions.append({
            "source_memory_id": str(source_memory.id),
            "target_memory_id": str(target_memory.id),
            "target_memory_title": target_memory.title,
            "target_memory_preview": target_memory.content[:100] + "..." if len(target_memory.content) > 100 else target_memory.content,
            "connection_type": connection_type,
            "connection_strength": connection_strength,
            "common_topics": list(set(extract_key_topics(source_memory.content)) & set(extract_key_topics(target_memory.content)))
        })
    
    # Sort by connection strength
    suggestions.sort(key=lambda x: x["connection_strength"], reverse=True)
    
    return suggestions

# Temporarily disabled for deployment
"""
async def build_memory_knowledge_graph(
    client_id: str,
    db: Session,
    brand_id: Optional[str] = None,
    limit_per_memory: int = 5,
    threshold: float = 0.6,
    auto_create: bool = False
) -> Dict[str, Any]:
    
    # Query for all memories for this client/brand
    query = db.query(Memory).filter(Memory.client_id == client_id)
    if brand_id:
        query = query.filter(Memory.brand_id == brand_id)
    
    memories = query.all()
    
    # Create nodes for the graph
    nodes = [
        {
            "id": str(memory.id),
            "title": memory.title,
            "type": memory.memory_type,
            "importance": memory.importance_score
        }
        for memory in memories
    ]
    
    # Find connections between memories
    edges = []
    connections_to_create = []
    
    for source_memory in memories:
        similar_memories = await memory_similarity_search(
            query=source_memory.content,
            db=db,
            client_id=source_memory.client_id,
            brand_id=source_memory.brand_id,
            limit=limit_per_memory * 2,
            threshold=threshold
        )
        
        # Filter out the source memory itself
        similar_memories = [m for m in similar_memories if str(m.id) != str(source_memory.id)]
        
        for target_memory in similar_memories[:limit_per_memory]:
            connection_type, connection_strength = await analyze_potential_connection(
                source_memory, target_memory
            )
            
            # Only include connections above the threshold
            if connection_strength >= threshold:
                edge = {
                    "source": str(source_memory.id),
                    "target": str(target_memory.id),
                    "type": connection_type,
                    "strength": connection_strength
                }
                edges.append(edge)
                
                if auto_create:
                    # Check if connection already exists
                    existing = db.query(MemoryConnection).filter(
                        MemoryConnection.source_memory_id == source_memory.id,
                        MemoryConnection.target_memory_id == target_memory.id,
                        MemoryConnection.connection_type == connection_type
                    ).first()
                    
                    if not existing:
                        connections_to_create.append(
                            MemoryConnection(
                                source_memory_id=source_memory.id,
                                target_memory_id=target_memory.id,
                                connection_type=connection_type,
                                connection_strength=connection_strength
                            )
                        )
    
    # If auto-creating connections, add them to the database
    if auto_create and connections_to_create:
        db.add_all(connections_to_create)
        db.commit()
    
    return {
        "nodes": nodes,
        "edges": edges,
        "stats": {
            "memory_count": len(nodes),
            "connection_count": len(edges),
            "connection_types": {ctype: edges.count({"type": ctype}) for ctype in set(edge["type"] for edge in edges)}
        }
    }
"""

# Simple version for deployment - only returns memory nodes, no connections
async def build_memory_knowledge_graph(
    client_id: str,
    db: Session,
    brand_id: Optional[str] = None,
    limit_per_memory: int = 5,
    threshold: float = 0.6,
    auto_create: bool = False
) -> Dict[str, Any]:
    """
    Build a simplified knowledge graph of all memories for a client.
    This is a temporary version for deployment that doesn't use MemoryConnection.
    
    Args:
        client_id: UUID of the client
        db: Database session
        brand_id: Optional UUID of a brand to filter memories
        
    Returns:
        Dictionary with nodes (memories) only, no edges (connections)
    """
    # Query for all memories for this client/brand
    query = db.query(Memory).filter(Memory.client_id == client_id)
    if brand_id:
        query = query.filter(Memory.brand_id == brand_id)
    
    memories = query.all()
    
    # Create nodes for the graph
    nodes = [
        {
            "id": str(memory.id),
            "title": memory.title,
            "type": memory.memory_type,
            "importance": memory.importance_score
        }
        for memory in memories
    ]
    
    return {
        "nodes": nodes,
        "edges": [],
        "stats": {
            "memory_count": len(nodes),
            "connection_count": 0,
            "connection_types": {}
        }
    } 