from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    DATABASE_URL: str = None  # Will be set by Railway environment variable
    SECRET_KEY: str = "your-secret-key-change-this"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 43200  # 30 days
    
    # FundsVera Payment Settings
    FUNDSVERA_BASE_URL: str = "https://fundsvera.co/api/v1"
    FUNDSVERA_PUBLIC_KEY: str = ""
    FUNDSVERA_SECRET_KEY: str = ""
    
    class Config:
        env_file = ".env"
        extra = "allow"  # Allow extra fields from environment

def get_settings():
    """Get settings with DATABASE_URL validation"""
    settings = Settings()
    
    # Force DATABASE_URL from environment if not set
    if not settings.DATABASE_URL or settings.DATABASE_URL is None:
        env_db_url = os.getenv("DATABASE_URL")
        if env_db_url:
            settings.DATABASE_URL = env_db_url
        else:
            raise ValueError("DATABASE_URL environment variable is required but not set")
    
    return settings

settings = get_settings()
