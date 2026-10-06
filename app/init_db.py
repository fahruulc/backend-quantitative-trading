#!/usr/bin/env python3
"""
Database initialization script
Run this to create all tables and verify database connection
"""
import sys
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import engine, Base
from app.core.config import settings
from app.models import StockFundamental, MarketSnapshot, APIUsage, AnomalyScore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db():
    """Initialize database tables"""
    try:
        logger.info(f"Connecting to database: {settings.DATABASE_URL}")

        # Create all tables
        Base.metadata.create_all(bind=engine)

        logger.info("✅ Database tables created successfully!")
        logger.info(f"Tables: {', '.join(Base.metadata.tables.keys())}")

        # Test connection
        from sqlalchemy.orm import Session
        with Session(engine) as session:
            result = session.execute("SELECT 1")
            logger.info("✅ Database connection test successful")

        return True

    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        return False

if __name__ == "__main__":
    success = init_db()
    sys.exit(0 if success else 1)
