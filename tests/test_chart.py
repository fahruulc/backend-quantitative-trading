"""
Test chart_service: candles + Moving Average dihitung benar.
yfinance di-mock — test jalan tanpa internet.
"""
import asyncio
from unittest.mock import patch

import pandas as pd

from app.services.chart_service import get_chart_data


def _fake_df(days=250):
    """DataFrame OHLCV sintetis: harga naik 1 per hari."""
    idx = pd.date_range("2025-01-01", periods=days, freq="B")
    close = [100.0 + i for i in range(days)]
    return pd.DataFrame({
        "Open": [c - 1 for c in close],
        "High": [c + 1 for c in close],
        "Low": [c - 2 for c in close],
        "Close": close,
        "Volume": [1_000_000] * days,
    }, index=idx)


def test_daily_candles_and_ma():
    with patch("app.services.chart_service.yf.download", return_value=_fake_df()):
        data = asyncio.run(get_chart_data("BBCA.JK", period="1y", interval="1d"))

    assert data["ticker"] == "BBCA.JK"
    assert len(data["candles"]) == 250
    assert set(data["ma"].keys()) == {"ma20", "ma50", "ma200"}
    # MA200 punya 250 - 200 + 1 = 51 titik
    assert len(data["ma"]["ma200"]) == 51
    # harga naik linear → MA20 terakhir = rata-rata 20 close terakhir
    expected = sum(100.0 + i for i in range(230, 250)) / 20
    assert abs(data["ma"]["ma20"][-1]["value"] - expected) < 0.01
    assert data["last_price"] == 349.0
    assert data["above_ma_slow"] is True  # harga naik → di atas MA200


def test_weekly_interval_uses_weekly_windows():
    with patch("app.services.chart_service.yf.download", return_value=_fake_df(60)):
        data = asyncio.run(get_chart_data("BBCA.JK", period="1y", interval="1wk"))
    assert set(data["ma"].keys()) == {"ma10", "ma20", "ma40"}


def test_invalid_interval_and_period_fallback():
    with patch("app.services.chart_service.yf.download", return_value=_fake_df(60)) as mock_dl:
        data = asyncio.run(get_chart_data("BBCA.JK", period="99y", interval="1h"))
    # fallback ke default
    assert data["interval"] == "1d"
    assert data["period"] == "1y"
    _, kwargs = mock_dl.call_args
    assert kwargs["interval"] == "1d"


def test_empty_data_returns_none():
    with patch("app.services.chart_service.yf.download", return_value=pd.DataFrame()):
        assert asyncio.run(get_chart_data("XXXX.JK")) is None
