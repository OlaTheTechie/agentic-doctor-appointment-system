"""
centralized configuration management for the appointment system
"""

import os
from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings


class APISettings(BaseSettings):
    """api server configuration"""
    
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    debug: bool = Field(default=False, env="DEBUG")
    request_timeout: int = Field(default=30, env="REQUEST_TIMEOUT")
    
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
    
    allowed_origins_str: str = Field(
        default="*",
        env="ALLOWED_ORIGINS"
    )
    allow_credentials_str: str = Field(default="false", env="ALLOW_CREDENTIALS")
    allow_methods_str: str = Field(default="GET,POST,PUT,DELETE,OPTIONS", env="ALLOW_METHODS")
    allow_headers_str: str = Field(default="*", env="ALLOW_HEADERS")
    max_age: int = Field(default=3600, env="CORS_MAX_AGE")
    
    @property
    def allow_credentials(self) -> bool:
        """parse allow_credentials string to boolean"""
        return self.allow_credentials_str.lower() in ["true", "1", "yes", "on"]
    
    @property
    def allow_methods(self) -> List[str]:
        """parse comma-separated methods string into list"""
        if not self.allow_methods_str:
            return ["GET", "POST", "OPTIONS"]
        return [method.strip() for method in self.allow_methods_str.split(",") if method.strip()]
    
    @property
    def allow_headers(self) -> List[str]:
        """parse comma-separated headers string into list"""
        if not self.allow_headers_str:
            return ["*"]
        return [header.strip() for header in self.allow_headers_str.split(",") if header.strip()]
    
    @property
    def allowed_origins(self) -> List[str]:
        """parse comma-separated origins string into list"""
        if not self.allowed_origins_str:
            return ["*"]
        
        # handle wildcard case
        if self.allowed_origins_str.strip() == "*":
            return ["*"]
            
        return [origin.strip() for origin in self.allowed_origins_str.split(",") if origin.strip()]
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": False,
        "extra": "ignore"
    }


class DatabaseSettings(BaseSettings):
    """database configuration"""
    
    data_file_path: str = Field(default="/app/data/doctor_availability.csv", env="DATA_FILE_PATH")
    backup_enabled_str: str = Field(default="true", env="BACKUP_ENABLED")
    
    @property
    def backup_enabled(self) -> bool:
        """parse backup_enabled string to boolean"""
        return self.backup_enabled_str.lower() in ["true", "1", "yes", "on"]
    
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