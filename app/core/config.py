import os
from pathlib import Path
from pydantic import BaseModel

class Settings(BaseModel):
    # Project Paths
    PROJECT_NAME: str = "Ethiopian Document Verification System"
    API_V1_PREFIX: str = "/api/v1"
    
    # Server configuration
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", 8000))
    
    # Client configuration (used by Streamlit)
    API_URL: str = os.getenv("API_URL", "http://127.0.0.1:8000")
    
    # Verification & File constraints
    MAX_FILE_SIZE_MB: int = 10
    ALLOWED_IMAGE_TYPES: set[str] = {"image/jpeg", "image/png", "image/jpg"}
    
    # OCR Confidence threshold
    DEFAULT_CONFIDENCE_THRESHOLD: float = 0.80

settings = Settings()