"""
Configuration settings for RemoteLED backend
"""
from backend import SERVICE_UUID
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Database
    DATABASE_URL: str = "postgresql://localhost:5432/remoteled"

    # ServiceUUID|CharacterUUID|
    SERVICE_UUID: str = ""
    CHARACTER_UUID: str = ""
    
    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_DEBUG: bool = True
    API_TITLE: str = "RemoteLED API"
    API_VERSION: str = "1.0.0"
    API_DESCRIPTION: str = "Backend API for RemoteLED QR-to-device activation system"
    
    # CORS
    CORS_ORIGINS: str = "*"
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string"""
        if self.CORS_ORIGINS == "*":
            return ["*"]
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    # Authorization
    AUTH_EXPIRY_MINUTES: int = 5
    
    # Mock Payment
    ENABLE_MOCK_PAYMENT: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = False




settings = Settings()

