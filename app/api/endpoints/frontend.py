"""
Frontend Data Endpoints
Serve data from database for frontend pages (Macro Sensors, Sector Rotation, Stock Signals, Heatmap)
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi_cache.decorator import cache
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import List, Optional
from datetime import datetime, timedelta
from app.core.database import get_db
from app.core.cache_coder import SafeJsonCoder
from app.models.stock_fundamental import StockFundamental
from app.models.market_snapshot import MarketSnapshot
from app.models.api_usage import APIUsage
from app.services.chart_service import get_chart_data

# Canonical sector universe (same as phase3_picker.get_universe) — grouping is
# done by membership, NOT by fragile row-index slicing (order of
# db.query(...).all() is not guaranteed, which previously mis-grouped sectors).
SECTOR_UNIVERSE = {
    "IDXBASIC": ["ANTM.JK", "INCO.JK", "MDKA.JK", "TINS.JK", "BRPT.JK",
                 "TPIA.JK", "ADMG.JK", "FPNI.JK", "SULI.JK", "UNIC.JK"],
    "IDXENERGY": ["ADRO.JK", "ITMG.JK", "PTBA.JK", "HRUM.JK", "MEDC.JK", "PGAS.JK"],
    "IDXFINANCE": ["BBCA.JK", "BBRI.JK", "BMRI.JK", "BBNI.JK", "BRIS.JK"],
}
TICKER_TO_SECTOR = {t: s for s, tickers in SECTOR_UNIVERSE.items() for t in tickers}


router = APIRouter()

@router.get("/macro-sensors")
async def get_macro_sensors(db: Session = Depends(get_db)):
    """Get latest macro sensor data for Macro Sensors page"""
    try:
        latest = db.query(MarketSnapshot).order_by(desc(MarketSnapshot.timestamp)).first()

        if not latest:
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "macro_status": "NO DATA",
                "usd": 0, "oil": 0, "gold": 0, "copper": 0,
                "btc": 0, "yield_rate": 0, "eido": 0,
                "top_sector": "N/A",
                "ai_insight": "No market data available yet."
            }

        return {
            "timestamp": latest.timestamp.isoformat(),
            "macro_status": latest.macro_status,
            "macro_reasoning": latest.macro_reasoning,
            "usd": latest.usd,
            "oil": latest.oil,
            "gold": latest.gold,
            "copper": latest.copper,
            "btc": latest.btc,
            "yield_rate": latest.yield_rate,
            "eido": latest.eido,
            "top_sector": latest.top_sector,
            "ai_insight": latest.ai_insight
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.get("/sector-rotation")
async def get_sector_rotation(db: Session = Depends(get_db)):
    """Get sector performance comparison"""
    try:
        all_stocks = db.query(StockFundamental).all()
        sectors = {}
        for s in all_stocks:
            sector = TICKER_TO_SECTOR.get(s.ticker)
            if sector:
                sectors.setdefault(sector, []).append(s)

        sector_data = []
        for sector, stocks in sectors.items():
            if stocks:
                avg_roe = sum(s.roe for s in stocks) / len(stocks)
                avg_score = sum(s.sectors_score for s in stocks if s.sectors_score) / len([s for s in stocks if s.sectors_score]) if any(s.sectors_score for s in stocks) else 0
                avg_growth = sum(s.eps_growth for s in stocks if s.eps_growth) / len([s for s in stocks if s.eps_growth]) if any(s.eps_growth for s in stocks) else 0

                sector_data.append({
                    "sector": sector,
                    "stock_count": len(stocks),
                    "avg_roe": round(avg_roe, 2),
                    "avg_score": round(avg_score, 1),
                    "avg_growth": round(avg_growth, 2),
                    "top_stocks": [{"ticker": s.ticker, "price": s.price, "roe": s.roe, "score": s.sectors_score}
                                   for s in sorted(stocks, key=lambda x: x.sectors_score or 0, reverse=True)[:3]]
                })

        return {"sectors": sector_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.get("/stock-signals")
async def get_stock_signals(
    min_score: Optional[float] = None,
    limit: int = Query(default=20, le=100),
    db: Session = Depends(get_db)
):
    """Get stock signals with filtering"""
    try:
        query = db.query(StockFundamental)
        if min_score:
            query = query.filter(StockFundamental.sectors_score >= min_score)

        stocks = query.order_by(desc(StockFundamental.sectors_score)).limit(limit).all()

        signals = []
        for stock in stocks:
            action = "BUY"
            if stock.roe > 15 and stock.der < 0.5 and stock.pbv < 2:
                action = "STRONG BUY"
            elif stock.roe < 8 or stock.der > 1.5:
                action = "HOLD"

            signals.append({
                "ticker": stock.ticker,
                "price": stock.price,
                "roe": stock.roe,
                "der": stock.der,
                "pbv": stock.pbv,
                "sectors_score": stock.sectors_score,
                "forward_pe": stock.forward_pe,
                "eps_growth": stock.eps_growth,
                "dividend_yield": stock.dividend_yield,
                "action": action,
                "ai_insight": stock.ai_insight,
                # Extended fields (additive — same shape, more data)
                "valuation_score": stock.valuation_score,
                "growth_score": stock.growth_score,
                "dividend_score": stock.dividend_score,
                "ownership_score": stock.ownership_score,
                "intrinsic_value": stock.intrinsic_value,
                "payout_ratio": stock.payout_ratio,
                "revenue_growth": stock.revenue_growth,
                "institutional_flow": stock.institutional_flow,
                "whale_count": stock.whale_count,
                "conglomerate_count": stock.conglomerate_count,
                "ai_model_used": stock.ai_model_used,
                "last_updated": stock.last_updated.isoformat() if stock.last_updated else None
            })

        return {"signals": signals, "total": len(signals)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.get("/heatmap")
async def get_heatmap(db: Session = Depends(get_db)):
    """Get heatmap data"""
    try:
        stocks = db.query(StockFundamental).all()

        heatmap_data = []
        for stock in stocks:
            score = stock.sectors_score or 50
            color = "green" if score >= 80 else "lightgreen" if score >= 70 else "yellow" if score >= 60 else "orange" if score >= 50 else "red"

            heatmap_data.append({
                "ticker": stock.ticker,
                "score": stock.sectors_score,
                "roe": stock.roe,
                "price": stock.price,
                "color": color,
                "eps_growth": stock.eps_growth,
                "revenue_growth": stock.revenue_growth
            })

        grouped = {}
        for item in heatmap_data:
            sector = TICKER_TO_SECTOR.get(item["ticker"], "OTHER")
            grouped.setdefault(sector, []).append(item)

        return {"heatmap": grouped, "all": heatmap_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get("/chart/{ticker}")
@cache(expire=3600, coder=SafeJsonCoder)
async def get_stock_chart(
    ticker: str,
    period: str = Query(default="1y", pattern="^(6mo|1y|2y)$"),
    interval: str = Query(default="1d", pattern="^(1d|1wk)$")
):
    """
    Get OHLC candles + Moving Average lines for technical chart.
    - Daily (1d): MA20, MA50, MA200
    - Weekly (1wk): MA10, MA20, MA40
    Cached 1 hour in Redis.
    """
    # Normalize ticker (allow "BBCA" -> "BBCA.JK")
    symbol = ticker.upper()
    if "." not in symbol:
        symbol = f"{symbol}.JK"

    data = await get_chart_data(symbol, period=period, interval=interval)
    if not data:
        raise HTTPException(status_code=404, detail=f"No chart data for {symbol}")
    return data
