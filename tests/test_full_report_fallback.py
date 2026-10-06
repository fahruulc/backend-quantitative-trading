"""
Test fallback demo pada /api/v1/full-report:
saat pipeline live gagal (AI error / tanpa sinyal), endpoint harus
menyajikan dataset demo lengkap (5 sinyal + macro) bukan kosong/error.
"""
import asyncio
import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import app
from app.demo_data import build_demo_full_report


@pytest.fixture()
def client():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    TestingSessionLocal = sessionmaker(bind=engine)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        session = TestingSessionLocal()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app, raise_server_exceptions=False)
    app.dependency_overrides.clear()


def test_demo_fallback_shape():
    demo = build_demo_full_report()
    assert len(demo["signals"]) == 5
    for k in ["usd", "oil", "gold", "copper", "btc", "yield_rate", "eido"]:
        assert demo[k] is not None, f"macro field {k} kosong"
    s = demo["signals"][0]
    for k in ["ticker", "price", "ma200", "rsi", "trend", "score", "action", "tag"]:
        assert k in s, f"signal field {k} hilang"


def test_full_report_falls_back_when_no_signals(client):
    # Simulasikan pipeline gagal total → endpoint harus tetap 200 dengan demo.
    # Bypass decorator @cache (butuh Redis) dengan memanggil fungsi aslinya.
    from app.api.endpoints import analysis

    endpoint = analysis.get_full_report
    fn = getattr(endpoint, "__wrapped__", endpoint)

    class FakeRequest:
        pass

    async def run():
        with patch.object(analysis.macro_service, "run", new=AsyncMock(side_effect=Exception("no internet"))):
            return await fn(FakeRequest())

    data = asyncio.run(run())
    payload = data if isinstance(data, dict) else data.model_dump()
    assert len(payload["signals"]) == 5
    assert payload["data_source"] == "DEMO"
    assert payload["yield_rate"] is not None


def test_fixture_file_parseable(sample_outputs):
    """Fixture dari dummydataoutput.txt harus berisi 4 endpoint."""
    assert "/api/v1/analysis/full-report" in sample_outputs
    assert "/api/v1/analysis/stocks" in sample_outputs
    assert len(sample_outputs["/api/v1/analysis/full-report"]["signals"]) > 0
