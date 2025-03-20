from sqlalchemy import Column, String, Text, ForeignKey, Integer, Float, Boolean, TIMESTAMP, JSON, Table, DateTime, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, ARRAY, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from database import Base
from datetime import datetime

class Owner(Base):
    __tablename__ = "owners"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    clients = relationship("Client", back_populates="owner")
    
class Client(Base):
    __tablename__ = "clients"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    description = Column(Text)
    industry = Column(String)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("owners.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    meta_data = Column(JSONB)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    owner = relationship("Owner", back_populates="clients")
    memories = relationship("Memory", back_populates="client")
    conversations = relationship("Conversation", back_populates="client")
    strategic_plans = relationship("StrategicPlan", back_populates="client")
    execution_logs = relationship("ExecutionLog", back_populates="client")
    tasks = relationship("Task", back_populates="client")
    brands = relationship("Brand", back_populates="client")

class Brand(Base):
    __tablename__ = "brands"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id"), nullable=False)
    description = Column(Text)
    meta_data = Column(JSONB)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    client = relationship("Client", back_populates="brands")
    customers = relationship("Customer", back_populates="brand")
    memories = relationship("Memory", back_populates="brand")

class Customer(Base):
    __tablename__ = "customers"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    brand_id = Column(UUID(as_uuid=True), ForeignKey("brands.id"), nullable=False)
    contact_info = Column(JSONB)
    meta_data = Column(JSONB)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    brand = relationship("Brand", back_populates="customers")
    memories = relationship("Memory", back_populates="customer")

class Memory(Base):
    __tablename__ = "memories"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id"), nullable=False)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=True)
    brand_id = Column(UUID(as_uuid=True), ForeignKey("brands.id"), nullable=True)
    embedding = Column(ARRAY(Float))  # Vector embedding for AI retrieval
    memory_type = Column(String)  # e.g., "meeting_note", "insight", "observation"
    importance_score = Column(Float)
    last_accessed = Column(TIMESTAMP)
    access_count = Column(Integer, default=0)
    related_memory_ids = Column(ARRAY(UUID(as_uuid=True)))
    tags = Column(ARRAY(String))
    meta_data = Column(JSONB)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    client = relationship("Client", back_populates="memories")
    customer = relationship("Customer", back_populates="memories")
    brand = relationship("Brand", back_populates="memories")
    # MemoryConnection relationships temporarily disabled for deployment
    # outgoing_connections = relationship("MemoryConnection", 
    #                                   foreign_keys="MemoryConnection.source_memory_id", 
    #                                   back_populates="source_memory",
    #                                   cascade="all, delete-orphan")
    # incoming_connections = relationship("MemoryConnection", 
    #                                   foreign_keys="MemoryConnection.target_memory_id", 
    #                                   back_populates="target_memory",
    #                                   cascade="all, delete-orphan")

class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id"), nullable=False)
    summary = Column(Text)
    participants = Column(ARRAY(String))
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    client = relationship("Client", back_populates="conversations")
    messages = relationship("ConversationMessage", back_populates="conversation")

class ConversationMessage(Base):
    __tablename__ = "conversation_messages"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=False)
    sender = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    content_embedding = Column(ARRAY(Float))  # Vector embedding for semantic search
    sentiment_score = Column(Float)
    key_topics = Column(ARRAY(String))
    action_items = Column(ARRAY(String))
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    
    # Relationships
    conversation = relationship("Conversation", back_populates="messages")

class StrategicPlan(Base):
    __tablename__ = "strategic_plans"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id"), nullable=False)
    content = Column(Text, nullable=False)
    goals = Column(ARRAY(String))
    status = Column(String)  # "draft", "in_progress", "completed"
    start_date = Column(TIMESTAMP)
    end_date = Column(TIMESTAMP)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    client = relationship("Client", back_populates="strategic_plans")
    execution_logs = relationship("ExecutionLog", back_populates="strategic_plan")

class ExecutionLog(Base):
    __tablename__ = "execution_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    description = Column(Text, nullable=False)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id"), nullable=False)
    strategic_plan_id = Column(UUID(as_uuid=True), ForeignKey("strategic_plans.id"))
    status = Column(String)  # e.g., "success", "failure", "in_progress"
    ai_summary = Column(Text)
    confidence_score = Column(Float)
    related_memory_ids = Column(ARRAY(UUID(as_uuid=True)))
    impact_score = Column(Float)
    decision_factors = Column(JSONB)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    
    # Relationships
    client = relationship("Client", back_populates="execution_logs")
    strategic_plan = relationship("StrategicPlan", back_populates="execution_logs")
    
class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    description = Column(Text)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id"), nullable=False)
    assigned_to = Column(String)
    status = Column(String)  # e.g., "pending", "in_progress", "completed"
    priority = Column(Integer)
    due_date = Column(TIMESTAMP)
    completion_date = Column(TIMESTAMP)
    related_memory_ids = Column(ARRAY(UUID(as_uuid=True)))
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    client = relationship("Client", back_populates="tasks")

# Memory Connection Model - temporarily disabled for deployment
"""
class MemoryConnection(Base):
    __tablename__ = "memory_connections"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_memory_id = Column(UUID(as_uuid=True), ForeignKey("memories.id", ondelete="CASCADE"), nullable=False)
    target_memory_id = Column(UUID(as_uuid=True), ForeignKey("memories.id", ondelete="CASCADE"), nullable=False)
    connection_type = Column(String, nullable=False)  # e.g., "related", "prerequisite", "followup", "contradicts"
    connection_strength = Column(Float, default=1.0)  # 0.0 to 1.0
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    source_memory = relationship("Memory", foreign_keys=[source_memory_id], back_populates="outgoing_connections")
    target_memory = relationship("Memory", foreign_keys=[target_memory_id], back_populates="incoming_connections")
    
    __table_args__ = (
        UniqueConstraint('source_memory_id', 'target_memory_id', 'connection_type', 
                         name='unique_memory_connection'),
    )
""" 