from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import computed_field
from typing import Self


class Settings(BaseSettings):
    """Application settings and configuration."""
    
    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/fastapi_db"
    
    # Application
    APP_NAME: str = "Cinema Ticket Booking"
    PROJECT_NAME: str = "Cinema Ticket Booking"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"
    BASE_URL: str = "http://localhost:8000"
    front_url: str = "http://localhost:4200"  
    
    # Authentication
    SECRET_KEY: str = "your-secret-key-here-change-in-production-use-openssl-rand-hex-32"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 43200  # 30 days
    
    # Email Settings
    SMTP_TLS: bool = True
    SMTP_SSL: bool = False
    SMTP_PORT: int = 587
    SMTP_HOST: str | None = None
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None
    EMAILS_FROM_EMAIL: str | None = None
    EMAILS_FROM_NAME: str | None = None
    SUPPORT_EMAIL: str = "support@cinema.com"  # Email to receive contact form messages
    
    @computed_field
    @property
    def emails_enabled(self) -> bool:
        """Check if email configuration is available."""
        return bool(self.SMTP_HOST and self.EMAILS_FROM_EMAIL)
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )


settings = Settings()
