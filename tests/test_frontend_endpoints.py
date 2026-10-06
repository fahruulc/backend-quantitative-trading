"""
Test shape & grouping untuk endpoint /api/v1/frontend/*.

Endpoint ini membaca langsung dari DB (SQLAlchemy Session). Test men-seed
DB SQLite in-memory via override dependency get_db, lalu memanggil endpoint
lewat TestClient — tanpa Postgres/Redis/internet/API key.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import app
from app.models.stock_fundamental import StockFundamental
from app.models.market_snapshot import MarketSnapshot

SECTOR_UNIVERSE = {
    "IDXBASIC": ["ANTM.JK", "INCO.JK", "MDKA.JK", "TINS.JK", "BRPT.JK",
                 "TPIA.JK", "ADMG.JK", "FPNI.JK", "SULI.JK", "UNIC.JK"],
    "IDXENERGY": ["ADRO.JK", "ITMG.JK", "PTBA.JK", "HRUM.JK", "MEDC.JK", "PGAS.JK"],
    "IDXFINANCE": ["BBCA.JK", "BBRI.JK", "BMRI.JK", "BBNI.JK", "BRIS.JK"],
}


@pytest.fixture()
def client():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    TestingSessionLocal = sessionmaker(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    # seed satu saham per sektor + satu snapshot
    from datetime import datetime
    for sector, tickers in SECTOR_UNIVERSE.items():
        for t in tickers:
            db.add(StockFundamental(
                ticker=t, price=1000.0, roe=15.0, der=0.5, pbv=1.5,
                sectors_score=75.0, forward_pe=12.0, eps_growth=10.0,
                revenue_growth=11.0, dividend_yield=2.0,
                institutional_flow="positive", last_updated=datetime.utcnow(),
            ))
    db.add(MarketSnapshot(
        timestamp=datetime.utcnow(), macro_status="RISK ON",
        macro_reasoning="test", top_sector="IDXENERGY",
        usd=16000.0, oil=80.0, gold=2300.0, copper=4.2,
        btc=100000.0, yield_rate=4.3, eido=23.0, ai_insight="test",
    ))
    db.commit()
    db.close()

    def override_get_db():
        session = TestingSessionLocal()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_heatmap_grouping_by_sector(client):
    """Regresi: grouping heatmap harus berdasarkan membership sektor,
    bukan slicing index (bug sebelumnya)."""
    data = client.get("/api/v1/frontend/heatmap").json()
    for sector, tickers in SECTOR_UNIVERSE.items():
        got = sorted(s["ticker"] for s in data["heatmap"][sector])
        assert got == sorted(tickers), f"{sector} salah grouping"


def test_heatmap_no_null_fields(client):
    for stocks in client.get("/api/v1/frontend/heatmap").json()["heatmap"].values():
        for s in stocks:
            assert s["score"] is not None
            assert s["eps_growth"] is not None


def test_stock_signals_shape(client):
    data = client.get("/api/v1/frontend/stock-signals", params={"limit": 100}).json()
    assert data["total"] == 21
    s = data["signals"][0]
    for field in ["ticker", "price", "roe", "der", "pbv", "sectors_score",
                  "forward_pe", "eps_growth", "dividend_yield", "action",
                  "institutional_flow", "ai_model_used"]:
        assert field in s, f"field {field} hilang dari stock-signals"


def test_sector_rotation(client):
    data = client.get("/api/v1/frontend/sector-rotation").json()
    assert len(data["sectors"]) == 3
    for sec in data["sectors"]:
        assert sec["stock_count"] > 0
        assert sec["avg_score"] > 0


def test_macro_sensors(client):
    data = client.get("/api/v1/frontend/macro-sensors").json()
    assert data["macro_status"] == "RISK ON"
    assert data["top_sector"] == "IDXENERGY"
    assert data["yield_rate"] == 4.3
