from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict, Any, List
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.config import settings
from app.services.cache_manager import cache_manager
from app.models.api_usage import APIUsage
from app.models.stock_fundamental import StockFundamental

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.get("/token-usage")
async def get_token_usage(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Get comprehensive token usage statistics

    Returns:
        - total_used: Total tokens consumed
        - budget: Total budget (500 tokens)
        - remaining: Tokens remaining
        - by_provider: Breakdown by provider (SECTORS_API, GEMINI)
        - alert: Alert level (OK, WARNING, CRITICAL)
        - percentage: Usage percentage
        - recent_calls: Last 10 API calls
    """
    summary = await cache_manager.get_token_usage_summary(db)

    # Get recent API calls
    recent_calls = db.query(APIUsage).order_by(
        APIUsage.timestamp.desc()
    ).limit(10).all()

    return {
        **summary,
        "recent_calls": [
            {
                "endpoint": call.endpoint,
                "provider": call.provider,
                "tokens": call.tokens_used,
                "timestamp": call.timestamp.isoformat()
            }
            for call in recent_calls
        ]
    }

@router.get("/token-usage/history")
async def get_token_usage_history(
    days: int = 7,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get token usage history over time

    Args:
        days: Number of days to look back (default 7)
    """
    cutoff = datetime.utcnow() - timedelta(days=days)

    # Daily breakdown
    daily_usage = db.query(
        func.date(APIUsage.timestamp).label('date'),
        APIUsage.provider,
        func.sum(APIUsage.tokens_used).label('tokens')
    ).filter(
        APIUsage.timestamp >= cutoff
    ).group_by(
        func.date(APIUsage.timestamp),
        APIUsage.provider
    ).order_by(
        func.date(APIUsage.timestamp).desc()
    ).all()

    # Format response
    history = {}
    for row in daily_usage:
        date_str = str(row.date)
        if date_str not in history:
            history[date_str] = {}
        history[date_str][row.provider] = row.tokens

    return {
        "days": days,
        "history": history
    }

@router.post("/toggle-demo-mode")
async def toggle_demo_mode(enabled: bool) -> Dict[str, Any]:
    """
    Toggle demo mode on/off

    When enabled, all API calls return mock data without consuming tokens.
    Useful for presentations and testing.

    Args:
        enabled: True to enable demo mode, False to disable
    """
    settings.DEMO_MODE = enabled
    settings.USE_MOCK_DATA = enabled

    return {
        "demo_mode": enabled,
        "message": f"Demo mode {'ENABLED' if enabled else 'DISABLED'}",
        "warning": "No tokens will be consumed" if enabled else "Real API calls will consume tokens"
    }

@router.get("/cache-stats")
async def get_cache_stats(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Get cache statistics

    Returns info about cached stocks in database
    """
    # Count total stocks in DB
    total_stocks = db.query(func.count(StockFundamental.ticker)).scalar()

    # Count fresh stocks (< 24 hours old)
    cutoff = datetime.utcnow() - timedelta(hours=24)
    fresh_stocks = db.query(func.count(StockFundamental.ticker)).filter(
        StockFundamental.last_updated > cutoff
    ).scalar()

    # Get oldest and newest records
    oldest = db.query(StockFundamental).order_by(
        StockFundamental.last_updated.asc()
    ).first()

    newest = db.query(StockFundamental).order_by(
        StockFundamental.last_updated.desc()
    ).first()

    # List all cached tickers
    all_tickers = db.query(StockFundamental.ticker).order_by(
        StockFundamental.ticker
    ).all()

    return {
        "total_stocks": total_stocks,
        "fresh_stocks": fresh_stocks,
        "stale_stocks": total_stocks - fresh_stocks,
        "oldest_update": oldest.last_updated.isoformat() if oldest else None,
        "newest_update": newest.last_updated.isoformat() if newest else None,
        "cached_tickers": [t[0] for t in all_tickers]
    }

@router.post("/prefetch-now")
async def trigger_prefetch() -> Dict[str, Any]:
    """
    Manually trigger pre-fetch job

    WARNING: This will consume tokens!
    Use this only when you need fresh data immediately.
    """
    from app.tasks.prefetch_job import manual_prefetch

    try:
        # Run in background
        import asyncio
        asyncio.create_task(manual_prefetch())

        return {
            "status": "started",
            "message": "Pre-fetch job started in background. Check logs for progress."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Health check endpoint

    Checks:
    - Database connectivity
    - Redis connectivity
    - Token budget status
    """
    health = {
        "status": "healthy",
        "checks": {}
    }

    # Check database
    try:
        db.execute("SELECT 1")
        health["checks"]["database"] = "ok"
    except Exception as e:
        health["checks"]["database"] = f"error: {e}"
        health["status"] = "unhealthy"

    # Check Redis
    try:
        await cache_manager.init_redis()
        if cache_manager.redis_client:
            await cache_manager.redis_client.ping()
            health["checks"]["redis"] = "ok"
        else:
            health["checks"]["redis"] = "not initialized"
    except Exception as e:
        health["checks"]["redis"] = f"error: {e}"
        health["status"] = "degraded"

    # Check token budget
    try:
        token_summary = await cache_manager.get_token_usage_summary(db)
        health["checks"]["token_budget"] = {
            "used": token_summary["total_used"],
            "remaining": token_summary["remaining"],
            "alert": token_summary["alert"]
        }

        if token_summary["alert"] == "CRITICAL":
            health["status"] = "critical"
    except Exception as e:
        health["checks"]["token_budget"] = f"error: {e}"

    return health
