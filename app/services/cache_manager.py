import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import logging
from redis import asyncio as aioredis
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.core.config import settings
from app.models.stock_fundamental import StockFundamental
from app.models.api_usage import APIUsage

logger = logging.getLogger(__name__)

class IntelligentCacheManager:
    """
    Three-tier caching strategy:
    1. Redis (fastest, TTL 1 hour)
    2. PostgreSQL (persistent, TTL 24 hours)
    3. API call (expensive, log token usage)
    """

    def __init__(self):
        self.redis_client: Optional[aioredis.Redis] = None

    async def init_redis(self):
        """Initialize Redis connection"""
        if not self.redis_client:
            self.redis_client = await aioredis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True
            )

    async def get_stock_fundamental(
        self,
        ticker: str,
        db: Session,
        sectors_client,
        max_age_hours: int = 24,
        force_refresh: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        Get stock fundamental data with intelligent caching

        Args:
            ticker: Stock ticker symbol
            db: Database session
            sectors_client: AsyncSectorsClient instance
            max_age_hours: Maximum age of cached data in hours
            force_refresh: Force API call even if cache exists

        Returns:
            Dictionary with stock fundamental data
        """
        await self.init_redis()

        # Step 1: Check Redis cache (unless force_refresh)
        if not force_refresh and self.redis_client:
            try:
                cached = await self.redis_client.get(f"stock:{ticker}")
                if cached:
                    logger.info(f"✓ Redis cache HIT for {ticker}")
                    return json.loads(cached)
            except Exception as e:
                logger.warning(f"Redis error: {e}")

        # Step 2: Check Database (if data < max_age_hours)
        if not force_refresh:
            cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)
            db_record = db.query(StockFundamental).filter(
                StockFundamental.ticker == ticker,
                StockFundamental.last_updated > cutoff_time
            ).first()

            if db_record:
                logger.info(f"✓ Database cache HIT for {ticker} (age: {datetime.utcnow() - db_record.last_updated})")
                data = db_record.to_dict()

                # Cache to Redis for 1 hour
                if self.redis_client:
                    try:
                        await self.redis_client.setex(
                            f"stock:{ticker}",
                            3600,
                            json.dumps(data, default=str)
                        )
                    except Exception as e:
                        logger.warning(f"Redis set error: {e}")

                return data

        # Step 3: Fresh API call (LOG TOKEN USAGE!)
        logger.info(f"⚠ Cache MISS for {ticker} - Calling Sectors API (will use ~8 tokens)")

        try:
            api_data = await sectors_client.analyze(ticker)

            # Log token usage to database
            await self.log_token_usage(
                db=db,
                endpoint=f"/company/report/{ticker}",
                provider="SECTORS_API",
                tokens_used=8,
                request_params={"ticker": ticker}
            )

            # Prepare data for database
            db_data = {
                "ticker": ticker,
                "price": api_data.get("price"),
                "roe": api_data.get("roe"),
                "der": api_data.get("der"),
                "pbv": api_data.get("pbv"),
                "sectors_score": api_data.get("sectors_score"),
                "valuation_score": api_data.get("valuation_score"),
                "growth_score": api_data.get("growth_score"),
                "dividend_score": api_data.get("dividend_score"),
                "ownership_score": api_data.get("ownership_score"),
                "forward_pe": api_data.get("forward_pe"),
                "intrinsic_value": api_data.get("intrinsic_value"),
                "eps_growth": api_data.get("eps_growth"),
                "revenue_growth": api_data.get("revenue_growth"),
                "dividend_yield": api_data.get("dividend_yield"),
                "payout_ratio": api_data.get("payout_ratio"),
                "institutional_flow": api_data.get("institutional_flow"),
                "whale_count": api_data.get("whale_count"),
                "conglomerate_count": api_data.get("conglomerate_count"),
                "data_source": "SECTORS_API",
                "last_updated": datetime.utcnow()
            }

            # Save to database (upsert)
            existing = db.query(StockFundamental).filter(
                StockFundamental.ticker == ticker
            ).first()

            if existing:
                for key, value in db_data.items():
                    setattr(existing, key, value)
            else:
                db.add(StockFundamental(**db_data))

            db.commit()

            # Cache to Redis
            if self.redis_client:
                try:
                    await self.redis_client.setex(
                        f"stock:{ticker}",
                        3600,
                        json.dumps(db_data, default=str)
                    )
                except Exception as e:
                    logger.warning(f"Redis set error: {e}")

            return db_data

        except Exception as e:
            logger.error(f"Error fetching {ticker} from Sectors API: {e}")
            return None

    async def log_token_usage(
        self,
        db: Session,
        endpoint: str,
        provider: str,
        tokens_used: int,
        request_params: Optional[Dict] = None
    ):
        """Log API token usage to database"""
        try:
            usage_log = APIUsage(
                endpoint=endpoint,
                provider=provider,
                tokens_used=tokens_used,
                request_params=request_params
            )
            db.add(usage_log)
            db.commit()
            logger.info(f"📊 Logged {tokens_used} tokens for {provider} - {endpoint}")
        except Exception as e:
            logger.error(f"Error logging token usage: {e}")
            db.rollback()

    async def get_token_usage_summary(self, db: Session) -> Dict[str, Any]:
        """Get token usage summary from database"""
        try:
            from sqlalchemy import func

            # Total tokens used
            total_used = db.query(func.sum(APIUsage.tokens_used)).scalar() or 0

            # By provider
            by_provider = db.query(
                APIUsage.provider,
                func.sum(APIUsage.tokens_used).label('total')
            ).group_by(APIUsage.provider).all()

            provider_dict = {row.provider: row.total for row in by_provider}

            # Calculate alert level
            budget = 500
            remaining = budget - total_used

            if total_used > 450:
                alert = "CRITICAL"
            elif total_used > 400:
                alert = "WARNING"
            else:
                alert = "OK"

            return {
                "total_used": total_used,
                "budget": budget,
                "remaining": remaining,
                "by_provider": provider_dict,
                "alert": alert,
                "percentage": round((total_used / budget) * 100, 1)
            }
        except Exception as e:
            logger.error(f"Error getting token usage summary: {e}")
            return {
                "total_used": 0,
                "budget": 500,
                "remaining": 500,
                "by_provider": {},
                "alert": "OK",
                "percentage": 0
            }

# Global instance
cache_manager = IntelligentCacheManager()
