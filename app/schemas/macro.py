from pydantic import BaseModel

class MacroData(BaseModel):
    timestamp: str
    status: str
    reasoning: str
    usd: float
    usd_chg: float
    oil: float
    oil_chg: float
    gold: float
    gold_chg: float
    copper: float
    copper_chg: float
    yield_rate: float
    yield_chg: float
    eido: float
    eido_val: float
    btc: float
    btc_chg: float
