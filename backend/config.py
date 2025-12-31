"""Application configuration using Pydantic Settings."""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/generalbackend"

    # JWT Authentication
    SECRET_KEY: str = "your-super-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # LLM APIs
    OLLAMA_BASE_URL: str = "http://ollama.railway.internal:11434"  # Railway private network
    OLLAMA_MODEL: str = "llama3.2:3b"  # CPU-optimized model on Railway
    GROK_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""

    # ChromaDB
    CHROMA_PERSIST_DIRECTORY: str = "./data/chroma_db"

    # Elasticsearch
    ELASTICSEARCH_HOST: str = "localhost"
    ELASTICSEARCH_PORT: int = 9200
    ELASTICSEARCH_USER: str = "elastic"
    ELASTICSEARCH_PASSWORD: str = ""
    ELASTICSEARCH_USE_SSL: str = "false"

    # Railway
    PORT: int = 8000

    # Admin User (created on first startup)
    ADMIN_EMAIL: str = "admin@dabrock.info"
    ADMIN_PASSWORD: str = "change-me-in-production"

    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:5173,http://localhost:5174,https://www.dabrock.info,https://api.dabrock.info"

    # File Upload
    MAX_UPLOAD_SIZE: int = 10485760  # 10MB in bytes
    UPLOAD_DIR: str = "./data/uploads"

    # Logging
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = True

    @property
    def allowed_origins_list(self) -> List[str]:
        """Parse ALLOWED_ORIGINS into a list."""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]


# Global settings instance
settings = Settings()
