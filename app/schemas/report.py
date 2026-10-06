from pydantic import BaseModel
from typing import List, Optional
from app.schemas.stock import StockAudit

class TradeSignal(StockAudit):
    action: str
    tag: str
    ma200: Optional[float] = None
    rsi: Optional[float] = None
    trend: Optional[str] = None
    vol_spike: Optional[bool] = None
    sl_level: Optional[float] = None

class ConsolidatedReportResponse(BaseModel):
    timestamp: str
    macro_status: str
    macro_reasoning: str
    top_sector: str
    ai_insight: str
    signals: List[TradeSignal]

    # Macro indicators (opsional — diisi oleh demo fallback / pipeline)
    usd: Optional[float] = None
    oil: Optional[float] = None
    gold: Optional[float] = None
    copper: Optional[float] = None
    btc: Optional[float] = None
    yield_rate: Optional[float] = None
    eido: Optional[float] = None
    ai_model_used: Optional[str] = None
    data_source: Optional[str] = None
