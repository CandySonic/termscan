"""
Application configuration using Pydantic Settings
"""
from pydantic_settings import BaseSettings
from typing import Literal
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # App
    app_name: str = "TermScan API"
    app_env: str = "development"
    debug: bool = True
    api_version: str = "v1"
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Database
    database_url: str = "postgresql+asyncpg://user:password@localhost:5432/halal_contracts"
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    
    # AI Provider
    ai_provider: Literal["openai", "anthropic", "gemini", "groq"] = "gemini"
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    gemini_api_key: str = ""
    groq_api_key: str = ""
    ai_model: str = "gemini-1.5-flash"
    ai_max_tokens: int = 4096
    ai_temperature: float = 0.3
    
    # Security
    secret_key: str = "change-this-in-production"
    api_key_header: str = "Authorization"
    access_token_expire_minutes: int = 30
    
    # Rate Limiting
    rate_limit_per_minute: int = 60
    rate_limit_per_hour: int = 500
    
    # Company Info (for reports)
    company_name: str = "Halal Contract API"
    company_website: str = "https://halalcontract.com"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


settings = get_settings()
