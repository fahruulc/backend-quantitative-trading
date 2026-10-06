"""
Database Seeder for Development
Populate database with realistic dummy data for frontend development
Run: docker-compose exec api python -m app.scripts.seed_database
"""
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine
from app.models.stock_fundamental import StockFundamental
from app.models.market_snapshot import MarketSnapshot
from app.models.api_usage import APIUsage
import random

def clear_all_data(db: Session):
    """Clear existing data"""
    print("🗑️  Clearing existing data...")
    db.query(StockFundamental).delete()
    db.query(MarketSnapshot).delete()
    db.query(APIUsage).delete()
    db.commit()
    print("✅ Data cleared")

def seed_stock_fundamentals(db: Session):
    """Seed stock fundamental data"""
    print("📊 Seeding stock fundamentals...")

    stocks_data = [
        # IDXBASIC Stocks
        {"ticker": "ANTM.JK", "name": "Aneka Tambang", "sector": "IDXBASIC", "price": 1850, "roe": 18.5, "der": 0.35},
        {"ticker": "INCO.JK", "name": "Vale Indonesia", "sector": "IDXBASIC", "price": 4200, "roe": 22.3, "der": 0.28},
        {"ticker": "MDKA.JK", "name": "Merdeka Copper", "sector": "IDXBASIC", "price": 1520, "roe": 16.2, "der": 0.42},
        {"ticker": "TINS.JK", "name": "Timah", "sector": "IDXBASIC", "price": 920, "roe": 12.8, "der": 0.55},
        {"ticker": "BRPT.JK", "name": "Barito Pacific", "sector": "IDXBASIC", "price": 670, "roe": 14.5, "der": 0.48},
        {"ticker": "TPIA.JK", "name": "Chandra Asri", "sector": "IDXBASIC", "price": 2100, "roe": 11.2, "der": 0.62},
        {"ticker": "ADMG.JK", "name": "Adhi Cakra", "sector": "IDXBASIC", "price": 880, "roe": 10.5, "der": 0.58},
        {"ticker": "FPNI.JK", "name": "Lotte Chemical", "sector": "IDXBASIC", "price": 1200, "roe": 9.8, "der": 0.72},
        {"ticker": "SULI.JK", "name": "SLJ Global", "sector": "IDXBASIC", "price": 450, "roe": 8.5, "der": 0.85},
        {"ticker": "UNIC.JK", "name": "Unggul Indah", "sector": "IDXBASIC", "price": 1450, "roe": 13.2, "der": 0.52},

        # IDXENERGY Stocks
        {"ticker": "ADRO.JK", "name": "Adaro Energy", "sector": "IDXENERGY", "price": 3150, "roe": 25.6, "der": 0.32},
        {"ticker": "ITMG.JK", "name": "Indo Tambangraya", "sector": "IDXENERGY", "price": 18500, "roe": 28.3, "der": 0.22},
        {"ticker": "PTBA.JK", "name": "Bukit Asam", "sector": "IDXENERGY", "price": 2850, "roe": 20.5, "der": 0.18},
        {"ticker": "HRUM.JK", "name": "Harum Energy", "sector": "IDXENERGY", "price": 1680, "roe": 22.8, "der": 0.38},
        {"ticker": "MEDC.JK", "name": "Medco Energi", "sector": "IDXENERGY", "price": 1250, "roe": 15.2, "der": 0.65},
        {"ticker": "PGAS.JK", "name": "Perusahaan Gas Negara", "sector": "IDXENERGY", "price": 1420, "roe": 11.8, "der": 0.78},

        # IDXFINANCE Stocks
        {"ticker": "BBCA.JK", "name": "Bank Central Asia", "sector": "IDXFINANCE", "price": 10200, "roe": 18.5, "der": 5.2},
        {"ticker": "BBRI.JK", "name": "Bank Rakyat Indonesia", "sector": "IDXFINANCE", "price": 5150, "roe": 16.8, "der": 4.8},
        {"ticker": "BMRI.JK", "name": "Bank Mandiri", "sector": "IDXFINANCE", "price": 6500, "roe": 15.2, "der": 5.5},
        {"ticker": "BBNI.JK", "name": "Bank Negara Indonesia", "sector": "IDXFINANCE", "price": 5200, "roe": 14.5, "der": 6.2},
        {"ticker": "BRIS.JK", "name": "Bank Syariah Indonesia", "sector": "IDXFINANCE", "price": 2650, "roe": 12.8, "der": 7.5},
    ]

    count = 0
    for stock_data in stocks_data:
        # Calculate derived metrics
        pbv = round(random.uniform(1.2, 3.5), 2)
        sectors_score = round(random.uniform(60, 90), 1)

        stock = StockFundamental(
            ticker=stock_data["ticker"],
            price=stock_data["price"],
            roe=stock_data["roe"],
            der=stock_data["der"],
            pbv=pbv,
            sectors_score=sectors_score,
            valuation_score=round(random.uniform(65, 85), 1),
            growth_score=round(random.uniform(70, 90), 1),
            dividend_score=round(random.uniform(50, 80), 1),
            ownership_score=round(random.uniform(60, 85), 1),
            forward_pe=round(random.uniform(8, 18), 2),
            intrinsic_value=round(stock_data["price"] * random.uniform(1.05, 1.25), 0),
            eps_growth=round(random.uniform(5, 25), 2),
            revenue_growth=round(random.uniform(8, 30), 2),
            dividend_yield=round(random.uniform(1.5, 5.5), 2) if stock_data["sector"] == "IDXFINANCE" else round(random.uniform(0.5, 3.5), 2),
            payout_ratio=round(random.uniform(20, 60), 2),
            institutional_flow="positive" if random.random() > 0.3 else "neutral",
            whale_count=random.randint(2, 8),
            conglomerate_count=random.randint(1, 4),
            sectors_fetched_at=datetime.utcnow(),
            ai_processed=True,
            ai_model_used="qwen3.8-max" if random.random() > 0.5 else "minimax-m3-pay",
            ai_insight=f"Strong fundamentals with {stock_data['sector']} sector tailwinds. ROE at {stock_data['roe']}% indicates solid profitability.",
            ai_processed_at=datetime.utcnow(),
            data_source="SEEDER",
            last_updated=datetime.utcnow()
        )
        db.add(stock)
        count += 1

    db.commit()
    print(f"✅ Seeded {count} stocks")

def seed_market_snapshots(db: Session):
    """Seed market snapshot data (historical)"""
    print("📸 Seeding market snapshots...")

    snapshots = []
    for days_ago in range(7, 0, -1):
        timestamp = datetime.utcnow() - timedelta(days=days_ago)

        macro_status = random.choice(["RISK ON", "CAUTIOUS / NEUTRAL", "RISK OFF"])
        top_sector = random.choice(["IDXBASIC", "IDXENERGY", "IDXFINANCE"])

        snapshot = MarketSnapshot(
            timestamp=timestamp,
            macro_status=macro_status,
            macro_reasoning=f"USD/IDR at {random.randint(15800, 16200)}, Oil ${random.randint(75, 85)}/barrel",
            top_sector=top_sector,
            usd=round(random.uniform(15800, 16200), 2),
            oil=round(random.uniform(75, 85), 2),
            gold=round(random.uniform(2300, 2400), 2),
            copper=round(random.uniform(4.0, 4.5), 2),
            btc=round(random.uniform(95000, 105000), 2),
            yield_rate=round(random.uniform(4.2, 4.6), 3),
            eido=round(random.uniform(22, 24), 2),
            ai_insight=f"Market showing {macro_status.lower()} sentiment. {top_sector} sector leading with strong commodity momentum.",
            signals=[]
        )
        snapshots.append(snapshot)
        db.add(snapshot)

    db.commit()
    print(f"✅ Seeded {len(snapshots)} market snapshots (last 7 days)")

def seed_api_usage(db: Session):
    """Seed API usage tracking data"""
    print("📊 Seeding API usage...")

    providers = ["SECTORS_API", "GEMINI_AI", "MULTI_AI_ROUTER"]
    endpoints = ["phase3_picker", "full_report", "manual_fetch"]

    count = 0
    for _ in range(15):
        usage = APIUsage(
            timestamp=datetime.utcnow() - timedelta(hours=random.randint(1, 72)),
            endpoint=random.choice(endpoints),
            provider=random.choice(providers),
            tokens_used=random.choice([8, 10, 12, 15]),
            request_params={"ticker": random.choice(["ANTM.JK", "BBCA.JK", "ADRO.JK"])}
        )
        db.add(usage)
        count += 1

    db.commit()
    print(f"✅ Seeded {count} API usage records")

def main():
    print("🌱 Starting Database Seeder...")
    print("=" * 50)

    db = SessionLocal()

    try:
        # Step 1: Clear existing data
        clear_all_data(db)

        # Step 2: Seed all tables
        seed_stock_fundamentals(db)
        seed_market_snapshots(db)
        seed_api_usage(db)

        print("=" * 50)
        print("✅ Seeding completed successfully!")
        print("\n📊 Summary:")
        print(f"   - Stocks: {db.query(StockFundamental).count()}")
        print(f"   - Market Snapshots: {db.query(MarketSnapshot).count()}")
        print(f"   - API Usage Records: {db.query(APIUsage).count()}")

    except Exception as e:
        print(f"❌ Error during seeding: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()
