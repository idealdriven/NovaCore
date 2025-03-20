from pydantic import BaseModel, Field, UUID4
from pydantic import field_validator as validator
from pydantic.networks import EmailStr
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
import uuid

# Base schemas with common fields
class BaseSchema(BaseModel):
    id: UUID4 = Field(default_factory=uuid.uuid4)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Owner schemas
class OwnerBase(BaseModel):
    email: EmailStr
    name: str

class OwnerCreate(OwnerBase):
    password: str

class OwnerUpdate(BaseModel):
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None

class OwnerInDB(OwnerBase, BaseSchema):
    is_active: bool = True
    hashed_password: str

class Owner(OwnerBase, BaseSchema):
    is_active: bool = True

# Client schemas
class ClientBase(BaseModel):
    name: str
    description: Optional[str] = None
    industry: Optional[str] = None
    meta_data: Optional[Dict[str, Any]] = None

class ClientCreate(ClientBase):
    owner_id: UUID4

class ClientUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    industry: Optional[str] = None
    is_active: Optional[bool] = None
    meta_data: Optional[Dict[str, Any]] = None

class Client(ClientBase, BaseSchema):
    owner_id: UUID4
    is_active: bool = True

# Brand schemas
class BrandBase(BaseModel):
    name: str
    client_id: UUID4
    description: Optional[str] = None
    meta_data: Optional[Dict[str, Any]] = None

class BrandCreate(BrandBase):
    pass

class BrandUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    meta_data: Optional[Dict[str, Any]] = None

class Brand(BrandBase, BaseSchema):
    pass

# Customer schemas
class CustomerBase(BaseModel):
    name: str
    brand_id: UUID4
    contact_info: Optional[Dict[str, Any]] = None
    meta_data: Optional[Dict[str, Any]] = None

class CustomerCreate(CustomerBase):
    pass

class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    contact_info: Optional[Dict[str, Any]] = None
    meta_data: Optional[Dict[str, Any]] = None

class Customer(CustomerBase, BaseSchema):
    pass

# Memory schemas
class MemoryBase(BaseModel):
    title: str
    content: str
    client_id: UUID4
    customer_id: Optional[UUID4] = None
    brand_id: Optional[UUID4] = None
    memory_type: Optional[str] = None
    tags: Optional[List[str]] = None
    meta_data: Optional[Dict[str, Any]] = None

class MemoryCreate(MemoryBase):
    pass

class MemoryUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    memory_type: Optional[str] = None
    customer_id: Optional[UUID4] = None
    brand_id: Optional[UUID4] = None
    importance_score: Optional[float] = None
    tags: Optional[List[str]] = None
    related_memory_ids: Optional[List[UUID4]] = None
    meta_data: Optional[Dict[str, Any]] = None

class Memory(MemoryBase, BaseSchema):
    embedding: Optional[List[float]] = None
    importance_score: Optional[float] = None
    last_accessed: Optional[datetime] = None
    access_count: int = 0
    related_memory_ids: Optional[List[UUID4]] = None

# Memory Connection Schemas - Temporarily disabled for deployment
"""
class MemoryConnectionBase(BaseModel):
    source_memory_id: UUID4
    target_memory_id: UUID4
    connection_type: str = Field(..., description="Type of connection between memories")
    connection_strength: float = Field(1.0, ge=0.0, le=1.0, description="Strength of the connection")

class MemoryConnectionCreate(MemoryConnectionBase):
    pass

class MemoryConnectionUpdate(BaseModel):
    connection_type: Optional[str] = None
    connection_strength: Optional[float] = Field(None, ge=0.0, le=1.0)

class MemoryConnection(MemoryConnectionBase):
    id: UUID4
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True
"""

# Add connections to the Memory response schema
class Memory(MemoryBase):
    id: UUID4
    created_at: datetime
    updated_at: datetime
    owner_id: UUID4
    client_id: UUID4
    brand_id: Optional[UUID4] = None
    customer_id: Optional[UUID4] = None
    # connections temporarily removed for deployment
    # connections: List[MemoryConnection] = []
    
    class Config:
        orm_mode = True

# Memory with connected memories data - Temporarily simplified for deployment
class MemoryWithConnections(Memory):
    # connected_memories: List["MemoryWithConnections"] = []
    
    class Config:
        orm_mode = True

# Memory Response with connection information - Temporarily simplified for deployment
class ConnectedMemoryResponse(BaseModel):
    memory: Memory
    connected_memories: Dict[str, List[Memory]] = Field(
        default_factory=lambda: {"related": [], "prerequisite": [], "followup": [], "contradicts": []}
    )
    
# Search for Connected Memories
class ConnectedMemoriesSearch(BaseModel):
    memory_id: UUID4
    connection_types: Optional[List[str]] = None
    min_strength: Optional[float] = Field(0.0, ge=0.0, le=1.0)
    limit: Optional[int] = 10
    
    class Config:
        schema_extra = {
            "example": {
                "memory_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "connection_types": ["related", "followup"],
                "min_strength": 0.5,
                "limit": 10
            }
        }

# Update Memory schema to reference the connected memories
Memory.update_forward_refs()
MemoryWithConnections.update_forward_refs()

# Conversation schemas
class ConversationBase(BaseModel):
    client_id: UUID4
    brand_id: Optional[UUID4] = None
    customer_id: Optional[UUID4] = None
    conversation_id: Optional[str] = None  # Used to link related messages

class ConversationCreate(ConversationBase):
    message: str
    response: Optional[str] = None
    message_index: Optional[int] = 0

class ConversationResponse(ConversationBase):
    id: UUID4
    message: str
    response: str
    message_index: int
    created_at: datetime
    
    class Config:
        orm_mode = True

class ConversationMemory(BaseModel):
    client_id: UUID4
    brand_id: Optional[UUID4] = None
    customer_id: Optional[UUID4] = None
    conversation_id: str
    message_index: int
    message: str
    response: str
    referenced_memory_ids: Optional[List[str]] = []
    
    class Config:
        schema_extra = {
            "example": {
                "client_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "brand_id": "3fa85f64-5717-4562-b3fc-2c963f66afa7",
                "conversation_id": "chat_abc123",
                "message_index": 1,
                "message": "What was our marketing strategy for Ruby + Begonia's summer collection?",
                "response": "The marketing strategy for Ruby + Begonia's summer collection focused on...",
                "referenced_memory_ids": ["3fa85f64-5717-4562-b3fc-2c963f66afa8"]
            }
        }

class RelevantMemory(BaseModel):
    id: str
    title: str
    content: str
    memory_type: str
    created_at: Optional[str] = None

class ConversationContext(BaseModel):
    client_id: str
    client_name: str
    brand_id: Optional[str] = None
    detected_topics: List[str]
    context_summary: str
    relevant_memories: List[RelevantMemory]
    
    class Config:
        schema_extra = {
            "example": {
                "client_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "client_name": "RALLY",
                "brand_id": "3fa85f64-5717-4562-b3fc-2c963f66afa7",
                "detected_topics": ["marketing", "summer", "collection"],
                "context_summary": "Client: RALLY\n\nBrand: Ruby + Begonia\n\nRelated memory (brand_strategy): The summer collection launch is planned for May 15th...",
                "relevant_memories": [
                    {
                        "id": "3fa85f64-5717-4562-b3fc-2c963f66afa8",
                        "title": "Summer Collection Strategy",
                        "content": "The summer collection launch is planned for May 15th...",
                        "memory_type": "brand_strategy",
                        "created_at": "2023-04-01T12:00:00Z"
                    }
                ]
            }
        }

# Bridge API Schemas
class GPTRequest(BaseModel):
    client_code: Optional[str] = None
    client_id: Optional[UUID4] = None
    message: str
    conversation_history: Optional[List[Dict[str, str]]] = []
    
    class Config:
        schema_extra = {
            "example": {
                "client_code": "ABC12345",
                "message": "What was our marketing strategy for the summer collection?",
                "conversation_history": [
                    {"role": "user", "content": "Hi, I need help with marketing."},
                    {"role": "assistant", "content": "Hello! I'd be happy to help with your marketing questions."}
                ]
            }
        }

class GPTResponse(BaseModel):
    context: str
    relevant_memories: List[Dict[str, Any]]
    suggested_topics: List[str]
    
    class Config:
        schema_extra = {
            "example": {
                "context": "Client: RALLY\n\nBrand: Ruby + Begonia\n\nRelated memory: The summer collection launch is planned for May 15th...",
                "relevant_memories": [
                    {
                        "id": "3fa85f64-5717-4562-b3fc-2c963f66afa8",
                        "title": "Summer Collection Strategy",
                        "preview": "The summer collection launch is planned for May 15th..."
                    }
                ],
                "suggested_topics": ["summer collection", "marketing strategy", "launch planning"]
            }
        }

# Message schemas
class MessageBase(BaseModel):
    conversation_id: UUID4
    sender: str
    content: str

class MessageCreate(MessageBase):
    pass

class MessageUpdate(BaseModel):
    content: Optional[str] = None

class Message(MessageBase, BaseSchema):
    content_embedding: Optional[List[float]] = None
    sentiment_score: Optional[float] = None
    key_topics: Optional[List[str]] = None
    action_items: Optional[List[str]] = None

# Strategic Plan schemas
class StrategicPlanBase(BaseModel):
    title: str
    client_id: UUID4
    content: str
    goals: Optional[List[str]] = None
    status: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class StrategicPlanCreate(StrategicPlanBase):
    pass

class StrategicPlanUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    goals: Optional[List[str]] = None
    status: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class StrategicPlan(StrategicPlanBase, BaseSchema):
    pass

# Execution Log schemas
class ExecutionLogBase(BaseModel):
    description: str
    client_id: UUID4
    strategic_plan_id: Optional[UUID4] = None
    status: Optional[str] = None

class ExecutionLogCreate(ExecutionLogBase):
    pass

class ExecutionLogUpdate(BaseModel):
    description: Optional[str] = None
    status: Optional[str] = None
    ai_summary: Optional[str] = None
    confidence_score: Optional[float] = None
    related_memory_ids: Optional[List[UUID4]] = None
    impact_score: Optional[float] = None
    decision_factors: Optional[Dict[str, Any]] = None

class ExecutionLog(ExecutionLogBase, BaseSchema):
    ai_summary: Optional[str] = None
    confidence_score: Optional[float] = None
    related_memory_ids: Optional[List[UUID4]] = None
    impact_score: Optional[float] = None
    decision_factors: Optional[Dict[str, Any]] = None

# Task schemas
class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    client_id: UUID4
    assigned_to: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[int] = None
    due_date: Optional[datetime] = None

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    assigned_to: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[int] = None
    due_date: Optional[datetime] = None
    completion_date: Optional[datetime] = None
    related_memory_ids: Optional[List[UUID4]] = None

class Task(TaskBase, BaseSchema):
    completion_date: Optional[datetime] = None
    related_memory_ids: Optional[List[UUID4]] = None

# Authentication schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# Vector search schema
class VectorSearchQuery(BaseModel):
    query: str
    client_id: UUID4
    limit: int = 5
    min_score: float = 0.7

# Enhanced Search Schemas
class EnhancedSearchQuery(BaseModel):
    query: str
    client_id: UUID4
    brand_id: Optional[UUID4] = None
    customer_id: Optional[UUID4] = None
    limit: int = Field(5, ge=1, le=50)
    threshold: float = Field(0.6, ge=0.0, le=1.0)
    hybrid_search: bool = True
    vector_weight: float = Field(0.7, ge=0.0, le=1.0)
    keyword_weight: float = Field(0.3, ge=0.0, le=1.0)
    
    class Config:
        schema_extra = {
            "example": {
                "query": "marketing strategy",
                "client_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "limit": 10,
                "threshold": 0.6,
                "hybrid_search": True,
                "vector_weight": 0.7,
                "keyword_weight": 0.3
            }
        }

class ScoringDetails(BaseModel):
    final_score: float
    vector_similarity: float
    keyword_score: float
    combined_score: float
    recency_factor: float
    importance_factor: float
    matched_terms: List[str]
    total_terms_matched: int
    query_term_count: int

class DetailedSearchResult(BaseModel):
    memory: Memory
    scoring: ScoringDetails
    
    class Config:
        orm_mode = True 