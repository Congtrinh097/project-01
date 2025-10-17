from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/cv_analyzer"
    
    # OpenAI
    OPENAI_API_KEY: str = ""
    OPENAI_EMBED_API_KEY: str = ""  # Separate key for embeddings (falls back to OPENAI_API_KEY if not set)
    HF_TOKEN: str = ""
    HF_MODEL_NAME: str = "meta-llama/Llama-3.1-8B"
    
    # File upload settings
    UPLOAD_DIR: str = "/tmp/uploads"
    MAX_FILE_SIZE: int = 10485760  # 10MB
    ALLOWED_EXTENSIONS: List[str] = ["pdf", "docx"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create settings instance
settings = Settings()

# Ensure upload directory exists
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

