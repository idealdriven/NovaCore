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

# Conversation schemas
class ConversationBase(BaseModel):
    title: str
    client_id: UUID4
    summary: Optional[str] = None
    participants: Optional[List[str]] = None

class ConversationCreate(ConversationBase):
    pass

class ConversationUpdate(BaseModel):
    title: Optional[str] = None
    summary: Optional[str] = None
    participants: Optional[List[str]] = None

class Conversation(ConversationBase, BaseSchema):
    pass

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