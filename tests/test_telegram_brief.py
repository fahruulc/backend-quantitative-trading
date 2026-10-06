"""
Test telegram_service:
- build_morning_brief membaca dari DB (tanpa API), format benar.
- send_message di-mock (tidak benar-benar mengirim ke Telegram).
"""
import asyncio
from datetime import datetime
from unittest.mock import patch, AsyncMock

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base
from app.models.stock_fundamental import StockFundamental
from app.models.market_snapshot import MarketSnapshot
from app.services import telegram_service


@pytest.fixture()
def db():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Session = sessionmaker(bind=engine)
    Base.metadata.create_all(bind=engine)
    session = Session()
    yield session
    session.close()


def _seed(db):
    db.add(MarketSnapshot(
        timestamp=datetime.utcnow(), macro_status="RISK ON",
        macro_reasoning="USD/IDR stabil", top_sector="IDXENERGY",
        usd=16000.0, oil=80.0, gold=2300.0, copper=4.2,
        btc=100000.0, yield_rate=4.3, eido=23.0,
        ai_insight="Sektor energi memimpin.",
    ))
    for i, t in enumerate(["ITMG.JK", "ADRO.JK", "BBCA.JK"]):
        db.add(StockFundamental(
            ticker=t, price=1000.0 + i * 100, roe=20.0, der=0.3, pbv=1.5,
            sectors_score=90.0 - i, last_updated=datetime.utcnow(),
        ))
    db.commit()


def test_brief_from_db(db):
    _seed(db)
    brief = telegram_service.build_morning_brief(db)
    assert "Morning Brief" in brief
    assert "RISK ON" in brief
    assert "IDXENERGY" in brief
    assert "ITMG" in brief  # top score pertama


def test_brief_empty_db_returns_none(db):
    assert telegram_service.build_morning_brief(db) is None


def test_send_message_skips_without_token():
    with patch.object(telegram_service.settings, "TELEGRAM_BOT_TOKEN", ""), \
         patch.object(telegram_service.settings, "TELEGRAM_CHAT_ID", ""):
        assert asyncio.run(telegram_service.send_message("hi")) is False


def test_send_message_posts_to_telegram():
    class FakeResp:
        status_code = 200
        text = '{"ok":true}'

    with patch.object(telegram_service.settings, "TELEGRAM_BOT_TOKEN", "tok"), \
         patch.object(telegram_service.settings, "TELEGRAM_CHAT_ID", "123"), \
         patch("app.services.telegram_service.httpx.AsyncClient") as mock_client:
        instance = mock_client.return_value.__aenter__.return_value
        instance.post = AsyncMock(return_value=FakeResp())
        assert asyncio.run(telegram_service.send_message("hi")) is True
        instance.post.assert_called_once()
