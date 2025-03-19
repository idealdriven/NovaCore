import os
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    """
    API Settings loaded from environment variables or .env file
    """
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Atlas API"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # CORS Configuration
    BACKEND_CORS_ORIGINS: list = ["*"]
    
    # Database Configuration
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://postgres:password@localhost:5432/atlas"
    )
    
    # Security Configuration
    SECRET_KEY: str = os.getenv("SECRET_KEY", "very_secret_key_change_in_production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # OpenAI Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # Vector Search Configuration
    VECTOR_SIMILARITY_THRESHOLD: float = 0.7
    MAX_SEARCH_RESULTS: int = 5
    
    class Config:
        case_sensitive = True
        env_file = ".env"

@lru_cache()
def get_settings():
    """
    Get cached settings instance
    """
    return Settings()

# Create a global instance for easy importing
settings = get_settings() 