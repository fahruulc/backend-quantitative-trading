"""
Demo / fallback dataset for the Consolidated Full Report.

Dipakai oleh endpoint /api/v1/full-report ketika pipeline live
(Sectors API / yfinance / AI) tidak menghasilkan sinyal — misalnya saat
demo tanpa koneksi API eksternal. Shape mengikuti ConsolidatedReportResponse
(TradeSignal mewarisi StockAudit) dan field yang dirender OverviewPage
(macro cards + signals table: ticker, price, ma200, rsi, trend, score, action, tag).

data_source = "DEMO" agar jelas bukan hasil pipeline live,
ai_model_used = "demo-model" ditampilkan apa adanya di chip model UI.
"""

from datetime import datetime


def _signal(ticker, action, tag, price, ma200, rsi, trend, score, sectors_score,
            roe, der, pbv):
    """Bangun satu TradeSignal lengkap (field StockAudit wajib diisi)."""
    return {
        # StockAudit required
        "ticker": ticker,
        "price": price,
        "score": score,
        "roe": roe,
        "der": der,
        "pbv": pbv,
        "is_ai": False,
        "ai_reason": "Demo data (bukan hasil model AI)",
        "sectors_available": True,
        "sectors_score": sectors_score,
        "fundamental_consensus": "DEMO",
        "ai_insight": (
            f"{ticker.replace('.JK','')} menunjukkan fundamental solid pada sektor "
            f"energi dengan ROE {roe}% dan DER {der}. Momentum teknikal: {trend}."
        ),
        # TradeSignal
        "action": action,
        "tag": tag,
        "ma200": ma200,
        "rsi": rsi,
        "trend": trend,
        "vol_spike": False,
        "sl_level": round(ma200 * 0.97, 2),
        # extras (chip model di UI)
        "ai_model_used": "demo-model",
        # a few optional fundamentals so detail views stay filled
        "forward_pe": round(price / 300.0, 2),
        "intrinsic_value": round(price * 1.1, 2),
        "eps_growth": 15.0,
        "revenue_growth": 12.0,
        "dividend_yield": 2.5,
        "payout_ratio": 35.0,
        "institutional_flow": "positive",
        "whale_count": 5,
        "conglomerate_count": 2,
    }


def build_demo_full_report():
    """Kembalikan dict siap untuk ConsolidatedReportResponse (timestamp runtime)."""
    return {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "macro_status": "RISK ON",
        "macro_reasoning": (
            "Yield Rate mengalami penurunan, Gold mencapai titik All-Time-High "
            "mendongkrak pergerakan aset berisiko. USD terpantau sedikit melemah "
            "terhadap mata uang regional."
        ),
        # Macro fields (dirender kartu Overview via marketStore.macroData)
        "usd": 15450.0,
        "oil": 82.5,
        "gold": 2160.5,
        "copper": 4.25,
        "btc": 71200.0,
        "yield_rate": 4.15,
        "eido": 23.50,
        "top_sector": "IDXENERGY",
        "ai_insight": (
            "Sektor energi mendominasi pergerakan hari ini berkat kenaikan harga Oil "
            "secara global dan pelemahan USD sementara. Saham-saham andalan sektor ini "
            "menunjukkan fundamental solid (ROE tinggi, DER terjaga)."
        ),
        "ai_model_used": "demo-model",
        "data_source": "DEMO",
        "signals": [
            _signal("ADRO.JK", "BUY", "ON WEAKNESS", 2700.0, 2650.0, 42.5, "UP", 85.0, 82.3, 25.6, 0.32, 1.8),
            _signal("PTBA.JK", "WAIT", "CONSOLIDATION", 2900.0, 3000.0, 55.0, "DOWN", 60.0, 55.0, 20.5, 0.18, 1.5),
            _signal("MEDC.JK", "BUY", "BREAKOUT", 1450.0, 1300.0, 65.0, "UP", 78.5, 75.0, 15.2, 0.65, 1.2),
            _signal("ITMG.JK", "WAIT", "OVERBOUGHT", 26500.0, 25000.0, 76.0, "UP", 50.0, 65.4, 28.3, 0.22, 2.1),
            _signal("PGAS.JK", "BUY", "REVERSAL", 1100.0, 1150.0, 35.0, "FLAT", 72.0, 68.0, 11.8, 0.78, 0.9),
        ],
    }
