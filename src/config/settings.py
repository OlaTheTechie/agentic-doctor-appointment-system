"""
centralized configuration management for the appointment system
"""

import os
from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings


class APISettings(BaseSettings):
    """api server configuration"""
    
    host: str = Field(default="127.0.0.1", env="API_HOST")
    port: int = Field(default=8000, env="API_PORT")
    debug: bool = Field(default=False, env="DEBUG")
    request_timeout: int = Field(default=15, env="REQUEST_TIMEOUT")
    
    # ai api keys
    groq_api_key: str = Field(default="", env="GROQ_API_KEY")
    openai_api_key: str = Field(default="", env="OPENAI_API_KEY")
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": False,
        "extra": "ignore"  # ignore extra environment variables
    }


class CORSSettings(BaseSettings):
    """cors configuration"""
    
    allowed_origins: List[str] = Field(
        default=["http://localhost:8501", "http://localhost:8502"],
        env="ALLOWED_ORIGINS"
    )
    allow_credentials: bool = Field(default=True)
    allow_methods: List[str] = Field(default=["GET", "POST", "OPTIONS"])
    allow_headers: List[str] = Field(default=["*"])
    max_age: int = Field(default=3600)
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": False,
        "extra": "ignore"
    }


class DatabaseSettings(BaseSettings):
    """database configuration"""
    
    data_file_path: str = Field(default="data/doctor_availability.csv", env="DATA_FILE_PATH")
    backup_enabled: bool = Field(default=True, env="BACKUP_ENABLED")
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": False,
        "extra": "ignore"
    }


class LoggingSettings(BaseSettings):
    """logging configuration"""
    
    level: str = Field(default="INFO", env="LOG_LEVEL")
    format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        env="LOG_FORMAT"
    )
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": False,
        "extra": "ignore"
    }


class AppSettings:
    """main application settings container"""
    
    def __init__(self):
        self.api = APISettings()
        self.cors = CORSSettings()
        self.database = DatabaseSettings()
        self.logging = LoggingSettings()
    
    @property
    def debug(self) -> bool:
        return self.api.debug


# global settings instance
settings = AppSettings()