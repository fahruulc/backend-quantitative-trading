from sqlalchemy import Column, String, Float, Integer, DateTime, Boolean, JSON
from sqlalchemy.sql import func
from app.core.database import Base

class StockFundamental(Base):
    __tablename__ = "stock_fundamentals"

    # Primary Key
    ticker = Column(String(20), primary_key=True, index=True)

    # Price & Basic Metrics
    price = Column(Float, nullable=True)
    roe = Column(Float, nullable=True)
    der = Column(Float, nullable=True)
    pbv = Column(Float, nullable=True)

    # Sectors API Scores
    sectors_score = Column(Float, nullable=True)
    valuation_score = Column(Float, nullable=True)
    growth_score = Column(Float, nullable=True)
    dividend_score = Column(Float, nullable=True)
    ownership_score = Column(Float, nullable=True)

    # Sectors API Details
    forward_pe = Column(Float, nullable=True)
    intrinsic_value = Column(Float, nullable=True)
    eps_growth = Column(Float, nullable=True)
    revenue_growth = Column(Float, nullable=True)
    dividend_yield = Column(Float, nullable=True)
    payout_ratio = Column(Float, nullable=True)
    institutional_flow = Column(String(50), nullable=True)
    whale_count = Column(Integer, nullable=True)
    conglomerate_count = Column(Integer, nullable=True)

    # Metadata
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    data_source = Column(String(20), default="SECTORS_API")  # SECTORS_API | YFINANCE | MANUAL

    def to_dict(self):
        return {
            "ticker": self.ticker,
            "price": self.price,
            "roe": self.roe,
            "der": self.der,
            "pbv": self.pbv,
            "sectors_score": self.sectors_score,
            "valuation_score": self.valuation_score,
            "growth_score": self.growth_score,
            "dividend_score": self.dividend_score,
            "ownership_score": self.ownership_score,
            "forward_pe": self.forward_pe,
            "intrinsic_value": self.intrinsic_value,
            "eps_growth": self.eps_growth,
            "revenue_growth": self.revenue_growth,
            "dividend_yield": self.dividend_yield,
            "payout_ratio": self.payout_ratio,
            "institutional_flow": self.institutional_flow,
            "whale_count": self.whale_count,
            "conglomerate_count": self.conglomerate_count,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None,
            "data_source": self.data_source
        }
