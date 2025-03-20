import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.sql import text
import dotenv
from contextlib import asynccontextmanager
import sys

# Load environment variables from .env file
dotenv.load_dotenv()

# Get database connection URL from environment variables
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:password@localhost:5432/atlas"
)

print(f"DEPLOYMENT: Initial DATABASE_URL format: {DATABASE_URL[:15]}...{DATABASE_URL[-5:] if len(DATABASE_URL) > 20 else ''}")

# Force the correct asyncpg driver format regardless of input format
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)
    print("DEPLOYMENT: Converted postgres:// to postgresql+asyncpg://")
elif DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
    print("DEPLOYMENT: Converted postgresql:// to postgresql+asyncpg://")

print(f"DEPLOYMENT: Using database dialect: {DATABASE_URL.split('://')[0]}")

try:
    # Create async engine
    engine = create_async_engine(
        DATABASE_URL,
        pool_size=5,
        max_overflow=10,
        echo=True,
    )
    
    print("DEPLOYMENT: Engine created successfully")

    # Session local
    AsyncSessionLocal = sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    print("DEPLOYMENT: Session factory created successfully")

except Exception as e:
    print(f"DEPLOYMENT ERROR creating engine: {str(e)}", file=sys.stderr)
    raise

# Base class for models
Base = declarative_base()

# Dependency for database session
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            print(f"DEPLOYMENT DB SESSION ERROR: {str(e)}", file=sys.stderr)
            raise
        finally:
            await session.close()

# Initialize database connection and verify it works
async def initialize_db():
    print("DEPLOYMENT: Initializing database connection")
    try:
        async with engine.begin() as conn:
            # Test connection
            print("DEPLOYMENT: Testing database connection")
            result = await conn.execute(text("SELECT 1"))
            one = result.scalar()
            if one != 1:
                raise Exception("Database connection test failed")
            
            print("✅ DEPLOYMENT: Database connection successful")
            
            # Create tables if they don't exist
            print("DEPLOYMENT: Creating or verifying tables")
            # Importing here to avoid circular imports
            from models import Base
            await conn.run_sync(Base.metadata.create_all)
            print("✅ DEPLOYMENT: Database tables created or verified") 
    except Exception as e:
        print(f"DEPLOYMENT DATABASE INITIALIZATION ERROR: {str(e)}", file=sys.stderr)
        import traceback
        print(traceback.format_exc(), file=sys.stderr)
        # Continue instead of crashing - allows app to start even if DB is not ready
        print("⚠️ DEPLOYMENT: Continuing despite database error - some features may not work") 