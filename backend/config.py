"""
Enterprise Configuration & Environment Settings.
Uses Pydantic V2 BaseSettings with strong typing, environment variable overrides,
and validation of infrastructure secrets and microservice ports.
"""
import os
from typing import List
from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    model_config = ConfigDict(extra="ignore", env_file=".env", env_file_encoding="utf-8")

    PROJECT_NAME: str = "Snitch Luxe AI E-Commerce Platform"
    VERSION: str = "2.5.0"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = False

    # Security & JWT Auth
    SECRET_KEY: str = "snitch-super-secure-production-secret-key-32-chars-long"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # Supabase & PostgreSQL Configuration
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""
    SUPABASE_DB_URL: str = ""
    DATABASE_URL: str = "sqlite:///./ecommerce.db"

    # Microservice Ports (For autonomous execution)
    PORT_GATEWAY: int = 8000
    PORT_AUTH: int = 8001
    PORT_PAYMENT: int = 8002
    PORT_CATALOG: int = 8003
    PORT_ORDER: int = 8004
    PORT_ADMIN: int = 8005
    PORT_AI_FIT: int = 8006
    PORT_CHATBOT: int = 8007

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


settings = Settings()
