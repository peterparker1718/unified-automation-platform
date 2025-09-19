"""Configuration module for the backend automation platform."""

import os
from typing import Optional
from pydantic import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # OpenAI Configuration
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4"
    openai_max_tokens: int = 2000
    
    # GitHub Configuration
    github_token: Optional[str] = None
    github_api_base: str = "https://api.github.com"
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    
    # Database Configuration (for future expansion)
    database_url: str = "sqlite:///./automation_platform.db"
    
    # Automation Configuration
    max_concurrent_jobs: int = 5
    job_timeout_seconds: int = 300
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()