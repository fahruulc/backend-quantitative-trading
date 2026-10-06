"""
Backfill missing (NULL) fundamental fields with realistic dummy values.

Dijalankan SEKALI setelah pipeline live menimpa data seeder dengan NULL
(untuk saham yang gagal di-fetch Sectors API). Hanya mengisi field yang NULL —
data asli yang sudah ada tidak diubah.

Run: docker compose exec api python -m app.scripts.backfill_dummy
"""
import random
from datetime import datetime
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.stock_fundamental import StockFundamental

random.seed(42)  # deterministic supaya demo konsisten


def backfill(db: Session):
    stocks = db.query(StockFundamental).all()
    print(f"Checking {len(stocks)} stocks...")

    patched = 0
    for s in stocks:
        changed = False

        def fill(attr, value):
            nonlocal changed
            if getattr(s, attr) is None:
                setattr(s, attr, value)
                changed = True

        fill("sectors_score", round(random.uniform(55, 78), 1))
        fill("valuation_score", round(random.uniform(60, 82), 1))
        fill("growth_score", round(random.uniform(62, 85), 1))
        fill("dividend_score", round(random.uniform(50, 78), 1))
        fill("ownership_score", round(random.uniform(58, 84), 1))
        fill("forward_pe", round(random.uniform(9, 18), 2))
        fill("intrinsic_value", round((s.price or 1000) * random.uniform(1.05, 1.2), 0))
        fill("eps_growth", round(random.uniform(6, 24), 2))
        fill("revenue_growth", round(random.uniform(8, 26), 2))
        fill("dividend_yield", round(random.uniform(1.2, 4.5), 2))
        fill("payout_ratio", round(random.uniform(25, 55), 2))
        fill("institutional_flow", random.choice(["positive", "positive", "neutral"]))
        fill("whale_count", random.randint(3, 8))
        fill("conglomerate_count", random.randint(1, 4))
        fill("ai_model_used", random.choice(["demo-model", "qwen3.8-max"]))
        fill("ai_insight", (
            f"{s.ticker.replace('.JK','')} menunjukkan fundamental yang cukup solid "
            f"dengan ROE sekitar {round(s.roe or 12, 1)}%. Valuasi dan pertumbuhan "
            "berada pada kisaran wajar sektornya."
        ))

        if changed:
            s.last_updated = datetime.utcnow()
            patched += 1
            print(f"  ✔ backfilled {s.ticker}")

    db.commit()
    print(f"\n✅ Backfill done: {patched}/{len(stocks)} stocks patched")


def main():
    db = SessionLocal()
    try:
        backfill(db)
    finally:
        db.close()


if __name__ == "__main__":
    main()
