import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    Application Settings configuration.
    Uses pydantic_settings to read from environment variables or .env file.
    """
    # Database connection string (default is SQLite)
    database_url: str = "sqlite:///./bulk_cert.db"
    
    # Directory to store generated certificates
    storage_dir: str = "storage"
    
    # Maximum number of recipients allowed per single bulk request
    max_recipients: int = 100

    class Config:
        env_file = ".env"

# Instantiate settings singleton to be used across the application
settings = Settings()

# Ensure the storage directory exists on startup
os.makedirs(settings.storage_dir, exist_ok=True)
