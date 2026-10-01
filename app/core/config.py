from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    APP_NAME: str = "Quant Trading REST API"
    APP_ENV: str = "development"
    
    # API Keys
    GEMINI_API_KEY: str
    SECTORS_API_KEY: str
    
    # Redis Cache
    REDIS_URL: str = "redis://localhost:6379/0"
    CACHE_EXPIRE_IN_SECONDS: int = 3600
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

@lru_cache()
def get_settings():
    return Settings()
