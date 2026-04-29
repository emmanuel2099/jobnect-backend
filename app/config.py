from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/jobnect_db"
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

settings = Settings()
