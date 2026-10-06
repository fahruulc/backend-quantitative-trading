"""
Telegram Service — kirim morning brief ke Telegram.

Prinsip:
- Data dibaca dari DATABASE (MarketSnapshot + StockFundamental).
  TIDAK memanggil Sectors API / yfinance lagi → 0 token tambahan.
- Kalau TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID kosong → skip dengan aman
  (anggota tim tanpa bot tetap bisa menjalankan sistem).
- Kirim cukup via httpx (sudah jadi dependency) ke Telegram Bot API,
  tanpa library telegram tambahan.
"""
import logging
from typing import Optional

import httpx
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.core.config import get_settings
from app.models.market_snapshot import MarketSnapshot
from app.models.stock_fundamental import StockFundamental

logger = logging.getLogger(__name__)
settings = get_settings()

TELEGRAM_API = "https://api.telegram.org/bot{token}/sendMessage"


def _action(stock: StockFundamental) -> str:
    """Turunan aksi sederhana dari fundamental (sama seperti endpoint stock-signals)."""
    if stock.roe is not None and stock.der is not None and stock.pbv is not None:
        if stock.roe > 15 and stock.der < 0.5 and stock.pbv < 2:
            return "STRONG BUY"
        if stock.roe < 8 or stock.der > 1.5:
            return "HOLD"
    return "BUY"


def build_morning_brief(db: Session, top_n: int = 5) -> Optional[str]:
    """
    Bangun teks morning brief dari data yang SUDAH ada di DB.
    Return None kalau tidak ada data sama sekali (jangan kirim pesan kosong).
    """
    snapshot = db.query(MarketSnapshot).order_by(desc(MarketSnapshot.timestamp)).first()
    stocks = (
        db.query(StockFundamental)
        .filter(StockFundamental.sectors_score.isnot(None))
        .order_by(desc(StockFundamental.sectors_score))
        .limit(top_n)
        .all()
    )

    if not snapshot and not stocks:
        return None

    lines = ["🌅 *Morning Brief — Market Intelligence*", ""]

    if snapshot:
        status_icon = "🟢" if "RISK ON" in (snapshot.macro_status or "") else \
                      "🔴" if "RISK OFF" in (snapshot.macro_status or "") else "🟡"
        lines += [
            "🌍 *Kondisi Makro:*",
            f"{status_icon} Status: *{snapshot.macro_status}*",
        ]
        if snapshot.macro_reasoning:
            lines.append(f"• {snapshot.macro_reasoning}")
        if snapshot.top_sector:
            lines.append(f"🏆 Sektor fokus: *{snapshot.top_sector}*")
        if snapshot.ai_insight:
            lines += ["", f"🤖 {snapshot.ai_insight}"]
        lines.append("")

    if stocks:
        lines.append(f"📈 *Top {len(stocks)} Stock Picks:*")
        for s in stocks:
            price = f"{int(s.price):,}".replace(",", ".") if s.price else "—"
            score = f"{s.sectors_score:.0f}" if s.sectors_score is not None else "—"
            lines.append(
                f"• *{s.ticker.replace('.JK','')}* — {_action(s)} | "
                f"Score {score} | Rp {price}"
            )

    return "\n".join(lines)


async def send_message(text: str) -> bool:
    """
    Kirim pesan ke Telegram. Return True kalau terkirim.
    Skip (return False) kalau token/chat_id belum dikonfigurasi.
    """
    token = settings.TELEGRAM_BOT_TOKEN
    chat_id = settings.TELEGRAM_CHAT_ID

    if not token or not chat_id:
        logger.info("Telegram not configured (TELEGRAM_BOT_TOKEN/CHAT_ID empty) — skipping send")
        return False

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(
                TELEGRAM_API.format(token=token),
                json={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"},
            )
        if resp.status_code == 200:
            logger.info("✅ Telegram message sent")
            return True
        logger.error(f"Telegram API error {resp.status_code}: {resp.text[:200]}")
        return False
    except Exception as e:
        logger.error(f"Telegram send failed: {e}")
        return False
