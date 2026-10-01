from pydantic import BaseModel
from typing import Optional, List, Any

class StockAudit(BaseModel):
    ticker: str
    price: float
    score: Optional[float]
    roe: Optional[float]
    der: Optional[float]
    pbv: Optional[float]
    
    is_ai: bool
    ai_reason: str
    
    # Sectors API Additions
    sectors_available: bool
    sectors_error: Optional[str] = None
    sectors_score: Optional[float] = None
    sectors_valuation_score: Optional[float] = None
    sectors_growth_score: Optional[float] = None
    sectors_dividend_score: Optional[float] = None
    sectors_ownership_score: Optional[float] = None
    
    forward_pe: Optional[float] = None
    intrinsic_value: Optional[float] = None
    eps_growth: Optional[float] = None
    revenue_growth: Optional[float] = None
    dividend_yield: Optional[float] = None
    payout_ratio: Optional[float] = None
    institutional_flow: Any = None
    whale_count: Optional[int] = None
    conglomerate_count: Optional[int] = None
    
    fundamental_consensus: str
    ai_insight: str

class StockPicksData(BaseModel):
    insight: str
    picks: List[StockAudit]
