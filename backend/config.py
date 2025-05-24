"""
Application configuration management
Loads settings from environment variables
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional, Literal
from pathlib import Path


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # API Keys
    openai_api_key: Optional[str] = Field(None, env='OPENAI_API_KEY')
    anthropic_api_key: Optional[str] = Field(None, env='ANTHROPIC_API_KEY')
    
    # LLM Configuration
    llm_provider: Literal['openai', 'anthropic'] = Field('openai', env='LLM_PROVIDER')
    llm_model: str = Field('gpt-4', env='LLM_MODEL')
    
    # Database
    database_url: str = Field('sqlite:///./database/app.db', env='DATABASE_URL')
    
    # Application
    app_env: Literal['development', 'production'] = Field('development', env='APP_ENV')
    debug: bool = Field(True, env='DEBUG')
    secret_key: str = Field('change-me-in-production', env='SECRET_KEY')
    
    # Server
    host: str = Field('0.0.0.0', env='HOST')
    port: int = Field(8000, env='PORT')
    
    # Frontend
    frontend_url: str = Field('http://localhost:8501', env='FRONTEND_URL')
    
    # Session Configuration
    session_timeout_minutes: int = Field(60, env='SESSION_TIMEOUT_MINUTES')
    max_session_length_minutes: int = Field(120, env='MAX_SESSION_LENGTH_MINUTES')
    
    # Rate Limiting
    rate_limit_per_minute: int = Field(60, env='RATE_LIMIT_PER_MINUTE')
    llm_rate_limit_per_minute: int = Field(20, env='LLM_RATE_LIMIT_PER_MINUTE')
    
    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
        case_sensitive = False
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode"""
        return self.app_env == 'development'
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode"""
        return self.app_env == 'production'
    
    def get_llm_api_key(self) -> Optional[str]:
        """Get the appropriate LLM API key based on provider"""
        if self.llm_provider == 'openai':
            return self.openai_api_key
        elif self.llm_provider == 'anthropic':
            return self.anthropic_api_key
        return None
    
    def validate_settings(self) -> None:
        """Validate that required settings are configured"""
        errors = []
        
        # Check LLM configuration
        api_key = self.get_llm_api_key()
        if not api_key:
            errors.append(f"No API key configured for {self.llm_provider}")
        
        # Check secret key in production
        if self.is_production and self.secret_key == 'change-me-in-production':
            errors.append("SECRET_KEY must be changed in production")
        
        if errors:
            raise ValueError("Configuration errors: " + "; ".join(errors))


# Create global settings instance
settings = Settings()

# Validate settings on import (can be disabled for testing)
if settings.app_env != 'testing':
    try:
        settings.validate_settings()
    except ValueError as e:
        print(f"Warning: {e}")
