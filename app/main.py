from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    description="REST API for Quant Trading using Gemini and Sectors API",
    version="1.0.0"
)

# Konfigurasi Keamanan CORS (Cross-Origin Resource Sharing)
origins = [
    "http://localhost:3000",      # Diizinkan untuk testing lokal (Next.js/React)
    "https://your-frontend.com"   # Ganti dengan nama domain frontend produksi Anda
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    # Setup Redis Cache
    redis = aioredis.from_url(settings.REDIS_URL, encoding="utf8", decode_responses=True)
    FastAPICache.init(RedisBackend(redis), prefix="quant-api-cache")
    print("✅ Redis Cache Initialized")

@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "Quant Trading API is running!"}

# Register Router Utama
from app.api.endpoints import analysis
app.include_router(analysis.router, prefix="/api/v1/analysis", tags=["Analysis"])

