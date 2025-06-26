from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database settings
    database_url: str = "postgresql://postgres:postgres@localhost:5432/soft_skill_practice_db"
    
    # External services
    feedback_llm_service_url: str = "http://localhost:8001"
    
    # API settings
    api_title: str = "Soft Skill Practice Service"
    api_version: str = "1.0.0"
    api_description: str = "Microservice for managing soft skill practice sessions and progress tracking"
    
    # Security settings
    secret_key: str = "your-secret-key-here"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Event bus settings (for future integration)
    event_bus_url: Optional[str] = None
    
    class Config:
        env_file = ".env"


settings = Settings()
