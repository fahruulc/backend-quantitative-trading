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

    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/marketdb"

    # Demo Mode (untuk testing tanpa consume tokens)
    DEMO_MODE: bool = False
    USE_MOCK_DATA: bool = False

    # AI Configuration (Octalabs Router)
    OCTALABS_BASE_URL: str = "https://router.octalabs.id"
    OCTALABS_API_KEY: str = "octa-b9dc4eec136d4025f42782b2d2e7fce0"
    AI_MODELS: str = "qwen3.8-max,minimax-m3-pay,kimi-k3,mimo-v2.5,mimo-v2.6-flash,deepseek-v4.1,minimax-m3,claude-sonnet-5"
    AI_MAX_RETRIES: int = 3

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

@lru_cache()
def get_settings():
    return Settings()

# Global settings instance
settings = get_settings()
