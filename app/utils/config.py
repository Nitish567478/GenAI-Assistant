from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    google_api_key: str = Field(
        validation_alias=AliasChoices("GOOGLE_API_KEY", "GEMINI_API_KEY")
    )
    port: int = 8000
    host: str = "0.0.0.0"
    similarity_threshold: float = 0.7
    top_k: int = 3
    embedding_model: str = "models/gemini-embedding-001"
    embedding_dimensions: int = 768
    llm_model: str = "gemini-2.5-flash-lite"
    llm_fallback_models: str = "gemini-2.0-flash-lite"

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()
