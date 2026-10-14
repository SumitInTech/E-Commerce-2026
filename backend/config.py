"""
Enterprise Configuration & Environment Settings.
Uses Pydantic BaseSettings for strong typing, environment variable overrides,
and validation of infrastructure secrets.
"""
import os
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "Snitch Luxe AI E-Commerce Platform"
    VERSION: str = "2.0.0"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = False

    # Security & JWT Auth
    SECRET_KEY: str = "snitch-super-secure-production-secret-key-32-chars-long"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # Database
    DATABASE_URL: str = "sqlite:///./ecommerce.db"

    # Gateway & Rate Limiting
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = 120
    BLOCKED_IPS: List[str] = []
    ENABLE_SECURITY_SANITIZER: bool = True

    # Payment Gateway Simulation
    PAYMENT_SIMULATION_MODE: bool = True
    STRIPE_WEBHOOK_SECRET: str = "whsec_mock_production_webhook_secret"

    # CORS
    CORS_ORIGINS: List[str] = ["*"]

    # LLM Settings
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.5-flash"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
