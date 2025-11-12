"""
Configuration settings for RemoteLED backend
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Database
    DATABASE_URL: str = "postgresql://remoteled:remoteled_dev_password@localhost:5432/remoteled"

    # BLE Configuration
    BLE_SERVICE_UUID: str = "000088F4-0000-1000-8000-00805f9b34fb"
    BLE_CHAR_UUID: str = "00000E32-0000-1000-8000-00805f9b34fb"
    BLE_KEY: str = "A920"
    BLE_DEVICE_NAME: str = "Remote LED"

    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 9999
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

    # Stripe Configuration
    STRIPE_SECRET_KEY: str = ""  # Provide via environment (.env) for each environment

    # LED GPIO Configuration (BCM numbering)
    # Unified pin mapping for all LED control implementations
    GPIO_PIN_GREEN: int = 17   # Success
    GPIO_PIN_YELLOW: int = 19  # Processing
    GPIO_PIN_RED: int = 27     # Failed

    @property
    def gpio_pins(self) -> dict:
        """Get GPIO pin mapping as a dictionary"""
        return {
            "green": self.GPIO_PIN_GREEN,
            "yellow": self.GPIO_PIN_YELLOW,
            "red": self.GPIO_PIN_RED
        }

    @property
    def led_color_mapping(self) -> dict:
        """Map payment status to LED colors"""
        return {
            "success": "green",
            "failed": "red",
            "fail": "red",  # Support both forms
            "processing": "yellow"
        }

    class Config:
        env_file = ".env"
        case_sensitive = False




settings = Settings()

