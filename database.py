import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.sql import text
import dotenv
from contextlib import asynccontextmanager

# Load environment variables from .env file
dotenv.load_dotenv()

# Get database connection URL from environment variables
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:password@localhost:5432/atlas"
)

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    pool_size=5,
    max_overflow=10,
    echo=True,
)

# Session local
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Base class for models
Base = declarative_base()

# Dependency for database session
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

# Initialize database connection and verify it works
async def initialize_db():
    async with engine.begin() as conn:
        # Test connection
        result = await conn.execute(text("SELECT 1"))
        one = result.scalar()
        if one != 1:
            raise Exception("Database connection test failed")
        
        print("✅ Database connection successful")
        
        # Create tables if they don't exist
        # Importing here to avoid circular imports
        from models import Base
        await conn.run_sync(Base.metadata.create_all)
        print("✅ Database tables created or verified") 