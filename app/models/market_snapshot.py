from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON
from sqlalchemy.sql import func
from app.core.database import Base

class MarketSnapshot(Base):
    __tablename__ = "market_snapshots"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Timestamp
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)

    # Macro Data
    macro_status = Column(String(50), nullable=False)  # RISK ON | RISK OFF
    macro_reasoning = Column(Text, nullable=True)

    # Sector Data
    top_sector = Column(String(20), nullable=True)

    # Commodity & FX Prices
    usd = Column(Float, nullable=True)
    oil = Column(Float, nullable=True)
    gold = Column(Float, nullable=True)
    copper = Column(Float, nullable=True)
    btc = Column(Float, nullable=True)
    yield_rate = Column(Float, nullable=True)
    eido = Column(Float, nullable=True)

    # AI Insight
    ai_insight = Column(Text, nullable=True)

    # Signals (stored as JSON array)
    signals = Column(JSON, nullable=True)

    # Created timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def to_dict(self):
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "macro_status": self.macro_status,
            "macro_reasoning": self.macro_reasoning,
            "top_sector": self.top_sector,
            "usd": self.usd,
            "oil": self.oil,
            "gold": self.gold,
            "copper": self.copper,
            "btc": self.btc,
            "yield_rate": self.yield_rate,
            "eido": self.eido,
            "ai_insight": self.ai_insight,
            "signals": self.signals,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
