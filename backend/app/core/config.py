"""
Configuration settings for RemoteLED backend
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Database - individual parameters (for Docker)
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "remoteled"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = ""
    
    # Database - full URL (takes precedence if set)
    DATABASE_URL: str = ""
    
    @property
    def database_url(self) -> str:
        """Get database URL, construct from parts if not explicitly set"""
        if self.DATABASE_URL:
            return self.DATABASE_URL
        # Construct from individual parameters
        password_part = f":{self.DB_PASSWORD}" if self.DB_PASSWORD else ""
        return f"postgresql://{self.DB_USER}{password_part}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
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

