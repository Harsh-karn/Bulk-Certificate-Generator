from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    database_url: str = "sqlite:///./bulk_cert.db"
    storage_dir: str = "storage"
    max_recipients: int = 100

    class Config:
        env_file = ".env"

settings = Settings()

os.makedirs(settings.storage_dir, exist_ok=True)
