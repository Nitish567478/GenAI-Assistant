from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    google_api_key: str
    port: int = 8000
    host: str = "0.0.0.0"
    similarity_threshold: float = 0.7
    top_k: int = 3
    embedding_model: str = "models/gemini-embedding-001"
    llm_model: str = "models/gemini-flash-latest"

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()
