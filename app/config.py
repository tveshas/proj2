"""Configuration management for the quiz solver application."""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration."""
    EMAIL = os.getenv("EMAIL", "")
    SECRET = os.getenv("SECRET", "")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "8000"))
    
    # Timeout for quiz solving (3 minutes in seconds)
    QUIZ_TIMEOUT = 180
    
    # Maximum payload size (1MB)
    MAX_PAYLOAD_SIZE = 1024 * 1024

config = Config()

