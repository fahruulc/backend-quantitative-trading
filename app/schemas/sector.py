from pydantic import BaseModel
from typing import Dict

class SectorData(BaseModel):
    sorted_sectors: Dict[str, float]
    top_sector: str
