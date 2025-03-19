from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
import uuid

from database import get_db
from auth.jwt import get_current_active_user
from models import Memory, Owner, Client, Brand, Customer
from utils.memory_connections import build_memory_knowledge_graph
from api.dependencies import get_client_owner

router = APIRouter(
    prefix="/api/v1/knowledge-graph",
    tags=["knowledge graph"],
    responses={404: {"description": "Not found"}},
)

@router.get("/{client_id}", response_model=Dict[str, Any])
async def get_knowledge_graph(
    client_id: uuid.UUID,
    brand_id: Optional[uuid.UUID] = None,
    threshold: float = 0.6,
    limit_per_memory: int = 5,
    auto_create: bool = False,
    db: Session = Depends(get_db),
    current_user: Owner = Depends(get_current_active_user)
):
    """
    Generate and return a knowledge graph for all memories of a client.
    
    Args:
        client_id: UUID of the client
        brand_id: Optional UUID of a brand to filter memories
        threshold: Minimum similarity threshold for connections
        limit_per_memory: Maximum connections per memory
        auto_create: If True, connections will be saved to the database
        
    Returns:
        A knowledge graph with nodes (memories) and edges (connections)
    """
    # Verify that the user has access to the client
    client = await get_client_owner(client_id, current_user, db)
    
    # If brand_id is provided, verify that it belongs to the client
    if brand_id:
        brand = db.query(Brand).filter(Brand.id == brand_id, Brand.client_id == client_id).first()
        if not brand:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Brand not found or does not belong to this client"
            )
    
    # Build the knowledge graph
    knowledge_graph = await build_memory_knowledge_graph(
        client_id=str(client_id),
        db=db,
        brand_id=str(brand_id) if brand_id else None,
        limit_per_memory=limit_per_memory,
        threshold=threshold,
        auto_create=auto_create
    )
    
    return knowledge_graph

@router.get("/memory/{memory_id}/connections", response_model=List[Dict[str, Any]])
async def get_memory_connections_suggestions(
    memory_id: uuid.UUID,
    limit: int = 10,
    threshold: float = 0.6,
    db: Session = Depends(get_db),
    current_user: Owner = Depends(get_current_active_user)
):
    """
    Suggest potential connections for a specific memory.
    
    Args:
        memory_id: UUID of the memory
        limit: Maximum number of suggestions to return
        threshold: Minimum similarity threshold
        
    Returns:
        List of suggested connections with metadata
    """
    from utils.memory_connections import find_memory_connections
    from api.dependencies import get_memory_access
    
    # Verify the user has access to the memory
    memory = await get_memory_access(memory_id, current_user, db)
    
    # Find potential connections
    suggestions = await find_memory_connections(
        memory_id=str(memory_id),
        db=db,
        limit=limit,
        threshold=threshold
    )
    
    return suggestions 