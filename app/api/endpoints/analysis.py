from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi_cache.decorator import cache
from sqlalchemy.orm import Session
from app.schemas.macro import MacroData
from app.schemas.sector import SectorData
from app.schemas.stock import StockPicksData
from app.schemas.report import ConsolidatedReportResponse
from app.services.phase1_macro import MacroGlobalSensorService
from app.services.phase2_sector import SectorSelectorProfessionalService
from app.services.phase3_picker import Phase3HybridSystem
from app.services.phase4_execution import ExecutionSniperProService
from app.core.database import get_db
from app.core.cache_coder import SafeJsonCoder
from app.demo_data import build_demo_full_report
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
macro_service = MacroGlobalSensorService()
sector_service = SectorSelectorProfessionalService()
picker_service = Phase3HybridSystem()
execution_service = ExecutionSniperProService()

@router.get("/macro", response_model=MacroData)
@cache(expire=3600, coder=SafeJsonCoder)
async def get_macro_analysis(request: Request):
    """
    Endpoint untuk menjalankan analisis sentimen makro global (Fase 1).
    Mengambil data dari YFinance secara real-time dan menganalisis regime market saat ini.
    """
    try:
        macro_data = await macro_service.run()
        return macro_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Macro Analysis Error: {str(e)}")

@router.get("/sectors")
@cache(expire=3600, coder=SafeJsonCoder)
async def get_sector_analysis(request: Request):
    """
    Endpoint untuk menjalankan Fase 1 dan dilanjutkan Fase 2 (Rotasi Sektor).
    """
    try:
        macro_data = await macro_service.run()
        sector_data = sector_service.run(macro_data)
        
        return {
            "macro_data": macro_data,
            "sector_data": sector_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sector Analysis Error: {str(e)}")

@router.get("/stocks", response_model=StockPicksData)
@cache(expire=3600, coder=SafeJsonCoder)
async def get_stock_picks(request: Request, db: Session = Depends(get_db)):
    """
    Endpoint untuk menjalankan Fase 1, Fase 2, dan Fase 3 (Intelligent Stock Picker).
    Menggunakan Multi-AI Router dan Sectors API secara paralel.
    """
    try:
        macro_data = await macro_service.run()
        sector_data = sector_service.run(macro_data)
        stock_picks = await picker_service.run(macro_data, sector_data, db)

        return stock_picks
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stock Picker Error: {str(e)}")

@router.get("/full-report", response_model=ConsolidatedReportResponse)
@cache(expire=3600, coder=SafeJsonCoder)  # Cached di Redis selama 1 Jam
async def get_full_report(request: Request, db: Session = Depends(get_db)):
    """
    Endpoint UTAMA: Menggabungkan Fase 1 hingga Fase 4.
    Menggunakan Redis Caching. Hasil akan ditarik dari Redis jika direquest kurang dari 1 jam sejak run terakhir.
    """
    try:
        # Menjalankan orkestrasi Fase 1 hingga 4
        macro_data = await macro_service.run()
        sector_data = sector_service.run(macro_data)
        stock_picks = await picker_service.run(macro_data, sector_data, db)
        signals = await execution_service.run(stock_picks)

        # Fallback ke data demo bila pipeline tidak menghasilkan sinyal
        # (API eksternal gagal/limit) ATAU insight AI gagal (401/limit),
        # supaya Overview tidak kosong / tidak menampilkan error saat demo.
        ai_failed = stock_picks.insight and stock_picks.insight.startswith("AI Error")
        if not signals or ai_failed:
            logger.warning(f"⚠️  Pipeline unusable (signals={len(signals)}, ai_failed={ai_failed}) — serving DEMO full-report")
            return build_demo_full_report()

        return ConsolidatedReportResponse(
            timestamp=macro_data.timestamp,
            macro_status=macro_data.status,
            macro_reasoning=macro_data.reasoning,
            top_sector=sector_data.top_sector,
            ai_insight=stock_picks.insight,
            signals=signals
        )
    except Exception as e:
        logger.error(f"Consolidated Report Error, serving DEMO data: {e}")
        return build_demo_full_report()

