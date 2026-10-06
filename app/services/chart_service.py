"""
Chart Data Service
Fetch OHLC price history from yfinance + compute Moving Averages.
Pattern follows phase1_macro.py / phase4_execution.py: asyncio.to_thread + MultiIndex flatten.
"""
import asyncio
import logging
from typing import Optional

import pandas as pd
import yfinance as yf

logger = logging.getLogger(__name__)

# MA windows per interval
MA_WINDOWS = {
    "1d": [("ma20", 20), ("ma50", 50), ("ma200", 200)],
    "1wk": [("ma10", 10), ("ma20", 20), ("ma40", 40)],
}

ALLOWED_INTERVALS = {"1d", "1wk"}
ALLOWED_PERIODS = {"6mo", "1y", "2y"}


def _flatten_columns(data: pd.DataFrame) -> pd.DataFrame:
    """Flatten yfinance MultiIndex columns (same as phase1_macro.py)."""
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = [col[0] if isinstance(col, tuple) else col for col in data.columns]
    return data


def _download(ticker: str, period: str, interval: str) -> pd.DataFrame:
    """Blocking yfinance download — run inside asyncio.to_thread."""
    data = yf.download(ticker, period=period, interval=interval, progress=False, auto_adjust=True)
    return _flatten_columns(data)


async def get_chart_data(ticker: str, period: str = "1y", interval: str = "1d") -> Optional[dict]:
    """
    Fetch OHLC candles + MA lines for a ticker.

    Returns:
        {
          "ticker": "BBCA.JK",
          "period": "1y",
          "interval": "1d",
          "currency": "IDR",
          "last_price": 10250.0,
          "change_pct": 1.23,
          "candles": [{"date": "2025-10-06", "open":.., "high":.., "low":.., "close":.., "volume":..}],
          "ma": {"ma20": [{"date","value"}], ...}
        }
        or None when no data.
    """
    if interval not in ALLOWED_INTERVALS:
        interval = "1d"
    if period not in ALLOWED_PERIODS:
        period = "1y"

    try:
        data = await asyncio.to_thread(_download, ticker, period, interval)
    except Exception as e:
        logger.error(f"Chart download error for {ticker}: {e}")
        return None

    if data is None or data.empty:
        logger.warning(f"No chart data for {ticker}")
        return None

    data = data.dropna(subset=["Close"])
    if data.empty:
        return None

    # Candles
    candles = []
    for idx, row in data.iterrows():
        candles.append({
            "date": idx.strftime("%Y-%m-%d"),
            "open": round(float(row["Open"]), 2),
            "high": round(float(row["High"]), 2),
            "low": round(float(row["Low"]), 2),
            "close": round(float(row["Close"]), 2),
            "volume": int(row["Volume"]) if pd.notna(row.get("Volume")) else 0,
        })

    # Moving averages
    ma_data = {}
    close = data["Close"]
    dates = [c["date"] for c in candles]
    for name, window in MA_WINDOWS.get(interval, MA_WINDOWS["1d"]):
        series = close.rolling(window=window).mean()
        ma_data[name] = [
            {"date": d, "value": round(float(v), 2)}
            for d, v in zip(dates, series)
            if pd.notna(v)
        ]

    # Summary stats
    last_close = float(close.iloc[-1])
    prev_close = float(close.iloc[-2]) if len(close) >= 2 else last_close
    change_pct = ((last_close - prev_close) / prev_close * 100) if prev_close else 0.0

    last_ma200 = ma_data.get("ma200") or ma_data.get("ma40") or []
    ma200_value = last_ma200[-1]["value"] if last_ma200 else None

    return {
        "ticker": ticker,
        "period": period,
        "interval": interval,
        "last_price": round(last_close, 2),
        "change_pct": round(change_pct, 2),
        "ma_slow_value": ma200_value,
        "above_ma_slow": (last_close >= ma200_value) if ma200_value else None,
        "candles": candles,
        "ma": ma_data,
    }
