"""
Configuration settings for the Multi-Model Sizing and Recommendation Service.
Follows 12-factor application methodology using Pydantic BaseSettings.
"""
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    APP_NAME: str = "Multimodal Anthropometric & Styling Intelligence API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    CORS_ORIGINS: List[str] = ["*"]

    # Model 1 Paths
    MODEL_1_ARTIFACT_DIR: str = "models/measurement/artifacts"
    REGRESSOR_MODEL_PATH: str = "models/measurement/artifacts/regressor_model.pkl"
    METADATA_PATH: str = "models/measurement/artifacts/metadata.json"

    # Model 4 RAG & LLM Settings
    GEMINI_API_KEY: str = Field(default="", description="Google Gemini API Key")
    GEMINI_MODEL: str = "gemini-1.5-flash"
    VECTOR_DB_DIR: str = "data/chroma_db"
    KNOWLEDGE_DOCS_DIR: str = "data/docs"


settings = Settings()
