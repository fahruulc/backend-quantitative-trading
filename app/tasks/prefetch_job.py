import asyncio
import logging
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.services.cache_manager import cache_manager
from app.utils.sectors_client import AsyncSectorsClient

logger = logging.getLogger(__name__)

# Priority stocks to pre-fetch (17 stocks total = 136 tokens per day)
PRIORITY_STOCKS = [
    # IDXBASIC: 6 stocks
    "ANTM.JK", "INCO.JK", "MDKA.JK", "TINS.JK", "BRPT.JK", "TPIA.JK",
    # IDXENERGY: 6 stocks
    "ADRO.JK", "ITMG.JK", "PTBA.JK", "HRUM.JK", "MEDC.JK", "PGAS.JK",
    # IDXFINANCE: 5 stocks
    "BBCA.JK", "BBRI.JK", "BMRI.JK", "BBNI.JK", "BRIS.JK",
]

async def prefetch_top_stocks():
    """
    Pre-fetch fundamental data for priority stocks
    Runs once per day (e.g., 7 AM before market opens)

    Token budget: 17 stocks × 8 tokens = 136 tokens per day
    For 3-day hackathon: 136 × 3 = 408 tokens (within 500 budget!)
    """
    logger.info("🚀 Starting daily pre-fetch job...")
    start_time = datetime.now()

    db: Session = SessionLocal()
    sectors_client = AsyncSectorsClient()

    success_count = 0
    error_count = 0

    try:
        for ticker in PRIORITY_STOCKS:
            try:
                await cache_manager.get_stock_fundamental(
                    ticker=ticker,
                    db=db,
                    sectors_client=sectors_client,
                    force_refresh=True  # Force API call to get fresh data
                )
                success_count += 1
                logger.info(f"✓ Pre-fetched {ticker} ({success_count}/{len(PRIORITY_STOCKS)})")

                # Rate limiting: 2 second delay between requests
                await asyncio.sleep(2)

            except Exception as e:
                error_count += 1
                logger.error(f"✗ Error pre-fetching {ticker}: {e}")

        # Get token usage summary
        token_summary = await cache_manager.get_token_usage_summary(db)

        elapsed = (datetime.now() - start_time).total_seconds()

        logger.info(f"""
        ✅ Pre-fetch job completed in {elapsed:.1f}s
        - Success: {success_count}/{len(PRIORITY_STOCKS)}
        - Errors: {error_count}
        - Estimated tokens used: {success_count * 8}
        - Total tokens used so far: {token_summary['total_used']}/{token_summary['budget']}
        - Remaining: {token_summary['remaining']} tokens
        - Alert level: {token_summary['alert']}
        """)

    except Exception as e:
        logger.error(f"Pre-fetch job failed: {e}")
    finally:
        db.close()

def start_scheduler():
    """
    Start APScheduler for background tasks
    """
    scheduler = AsyncIOScheduler()

    # Daily pre-fetch at 7:00 AM (before market opens)
    scheduler.add_job(
        prefetch_top_stocks,
        'cron',
        hour=7,
        minute=0,
        id='daily_prefetch',
        name='Daily Stock Pre-fetch'
    )

    # Optional: Also run at 1:00 PM (mid-day update)
    # scheduler.add_job(
    #     prefetch_top_stocks,
    #     'cron',
    #     hour=13,
    #     minute=0,
    #     id='midday_prefetch',
    #     name='Mid-day Stock Pre-fetch'
    # )

    scheduler.start()
    logger.info("📅 Scheduler started - Daily pre-fetch scheduled at 07:00")

    return scheduler

# For manual trigger (testing purposes)
async def manual_prefetch():
    """
    Manually trigger pre-fetch job (for testing)
    Usage: await manual_prefetch()
    """
    logger.info("🔧 Manual pre-fetch triggered")
    await prefetch_top_stocks()
