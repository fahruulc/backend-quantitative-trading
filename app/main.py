import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis
from app.core.config import get_settings
from app.core.database import engine, Base

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    description="REST API for Quant Trading using Gemini and Sectors API with Token Optimization",
    version="2.0.0"
)

# Konfigurasi Keamanan CORS (Cross-Origin Resource Sharing)
origins = [
    "http://localhost:3000",      # Frontend Vue dev server
    "http://localhost:5173",      # Vite dev server
    "http://localhost:5174",      # Vite dev server (alt port)
    "http://localhost:5175",      # Vite dev server (alt port)
    "http://localhost:5180",      # Vite dev server (current)
    "http://localhost:8080",      # Alternative frontend port
    "https://your-frontend.com"   # Ganti dengan nama domain frontend produksi Anda
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    # Create database tables
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created/verified")
    except Exception as e:
        logger.error(f"❌ Database initialization error: {e}")

    # Setup Redis Cache
    try:
        redis = aioredis.from_url(settings.REDIS_URL, encoding="utf8", decode_responses=True)
        FastAPICache.init(RedisBackend(redis), prefix="quant-api-cache")
        logger.info("✅ Redis Cache Initialized")
    except Exception as e:
        logger.error(f"❌ Redis initialization error: {e}")

    # Start background scheduler for pre-fetching
    try:
        from app.tasks.prefetch_job import start_scheduler
        start_scheduler()
        logger.info("✅ Background scheduler started")
    except Exception as e:
        logger.warning(f"⚠️  Scheduler not started: {e}")

    logger.info(f"🚀 Market Intelligence API started - Demo Mode: {settings.DEMO_MODE}")

@app.on_event("shutdown")
async def shutdown():
    logger.info("👋 Shutting down Market Intelligence API")

@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "message": "Market Intelligence API is running!",
        "demo_mode": settings.DEMO_MODE,
        "version": "2.0.0"
    }

# Register Routers
from app.api.endpoints import analysis, admin, frontend

app.include_router(analysis.router, prefix="/api/v1", tags=["Analysis"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["Admin"])
app.include_router(frontend.router, prefix="/api/v1/frontend", tags=["Frontend"])

