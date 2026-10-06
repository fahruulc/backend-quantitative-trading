import yfinance as yf
import asyncio
import logging
from datetime import datetime
from sqlalchemy.orm import Session
from app.schemas.macro import MacroData
from app.schemas.sector import SectorData
from app.schemas.stock import StockPicksData, StockAudit
from app.utils.multi_ai_client import MultiAIClient
from app.utils.sectors_client import AsyncSectorsClient
from app.models.stock_fundamental import StockFundamental
from app.services.cache_manager import IntelligentCacheManager

logger = logging.getLogger(__name__)

class StockAuditorProService:
    @staticmethod
    async def audit(ticker: str):
        try:
            # Menjalankan YFinance secara non-blocking di background thread
            def _fetch_yf():
                stock = yf.Ticker(ticker)
                info = stock.info
                fast = stock.fast_info
                fin = stock.financials
                bal = stock.balance_sheet
                return info, fast, fin, bal

            info, fast, fin, bal = await asyncio.to_thread(_fetch_yf)

            def _safe_val(df, key):
                try: return float(df.loc[key].iloc[0]) if key in df.index else 0.0
                except: return 0.0

            price = fast.get('last_price', 0)
            if price == 0: price = info.get('currentPrice', 0)
            if price == 0: return None

            net_inc = _safe_val(fin, "Net Income")
            equity = _safe_val(bal, "Stockholders Equity")
            debt = _safe_val(bal, "Total Debt")

            roe = (net_inc / equity * 100) if equity else 0
            der = (debt / equity) if equity else 0

            score = 50
            if roe > 15: score += 20
            elif roe > 10: score += 10
            if der < 0.5: score += 15
            elif der < 1.0: score += 10

            pbv = price / (equity / info.get('sharesOutstanding', 1)) if equity else 0
            if pbv < 1.0: score += 10
            elif pbv < 2.0: score += 5

            return {
                "price": price,
                "score": score,
                "roe": roe,
                "der": der,
                "pbv": pbv
            }
        except Exception:
            return None


class Phase3HybridSystem:
    def __init__(self):
        self.ai = MultiAIClient()

    def get_universe(self, sector: str):
        fallback_universe = {
            "IDXBASIC": ["ANTM.JK", "INCO.JK", "MDKA.JK", "TINS.JK", "BRPT.JK", "TPIA.JK", "ADMG.JK", "FPNI.JK", "SULI.JK", "UNIC.JK"],
            "IDXENERGY": ["ADRO.JK", "ITMG.JK", "PTBA.JK", "HRUM.JK", "MEDC.JK", "PGAS.JK"],
            "IDXFINANCE": ["BBCA.JK", "BBRI.JK", "BMRI.JK", "BBNI.JK", "BRIS.JK"]
        }
        return fallback_universe.get(sector, ["ANTM.JK", "INCO.JK", "MDKA.JK"])

    @staticmethod
    def _fundamental_consensus(existing_score, sectors_score):
        if sectors_score is None: return "SECTORS UNAVAILABLE"
        if existing_score is None: return "SECTORS ONLY"
        gap = abs(float(existing_score) - float(sectors_score))
        if gap <= 10: return "CONFIRMED"
        elif gap <= 20: return "MILD DIVERGENCE"
        else: return "DIVERGENCE"

    async def _fetch_and_save_stock(
        self,
        ticker: str,
        db: Session,
        sectors_client: AsyncSectorsClient,
        cache_manager: IntelligentCacheManager
    ):
        """
        CRITICAL: Fetch from APIs and SAVE TO DATABASE IMMEDIATELY
        This ensures data is persisted even if AI processing fails later
        """
        try:
            yf_task = StockAuditorProService.audit(ticker)
            sectors_task = sectors_client.analyze(ticker)

            # Fetch from both APIs in parallel
            yf_res, sectors_res = await asyncio.gather(yf_task, sectors_task)

            if not yf_res:
                logger.warning(f"⚠️ Skipping {ticker} - no yfinance data")
                return None

            # Convert institutional_flow to string if it's a list/dict
            institutional_flow_str = None
            if sectors_res.get('institutional_flow'):
                inst_flow = sectors_res['institutional_flow']
                if isinstance(inst_flow, (list, dict)):
                    institutional_flow_str = "positive" if inst_flow else "neutral"
                else:
                    institutional_flow_str = str(inst_flow)[:50]

            # CREATE database record IMMEDIATELY (before AI processing)
            stock_record = StockFundamental(
                ticker=ticker,
                price=yf_res['price'],
                roe=yf_res['roe'],
                der=yf_res['der'],
                pbv=yf_res['pbv'],
                sectors_score=sectors_res.get('sectors_score'),
                valuation_score=sectors_res.get('valuation_score'),
                growth_score=sectors_res.get('growth_score'),
                dividend_score=sectors_res.get('dividend_score'),
                ownership_score=sectors_res.get('ownership_score'),
                forward_pe=sectors_res.get('forward_pe'),
                intrinsic_value=sectors_res.get('intrinsic_value'),
                eps_growth=sectors_res.get('eps_growth'),
                revenue_growth=sectors_res.get('revenue_growth'),
                dividend_yield=sectors_res.get('dividend_yield'),
                payout_ratio=sectors_res.get('payout_ratio'),
                institutional_flow=institutional_flow_str,
                whale_count=sectors_res.get('whale_count'),
                conglomerate_count=sectors_res.get('conglomerate_count'),
                sectors_fetched_at=datetime.utcnow(),
                ai_processed=False,  # Not yet processed by AI
                data_source="SECTORS_API",
                last_updated=datetime.utcnow()
            )

            # SAVE TO DATABASE NOW (this is the critical fix!)
            db.merge(stock_record)  # Use merge to handle updates
            db.commit()
            db.refresh(stock_record)

            # Log token usage
            await cache_manager.log_token_usage(
                endpoint="phase3_picker",
                provider="SECTORS_API",
                tokens_used=8,
                request_params={"ticker": ticker}
            )

            logger.info(f"✅ Saved {ticker} to DB (Sectors API data secured, 8 tokens logged)")

            # Return both raw data and DB record
            return {
                "record": stock_record,
                "yf_data": yf_res,
                "sectors_data": sectors_res,
                "consensus": self._fundamental_consensus(yf_res.get('score'), sectors_res.get('sectors_score'))
            }

        except Exception as e:
            logger.error(f"❌ Error fetching/saving {ticker}: {e}")
            return None

    async def run(self, macro_data: MacroData, sector_data: SectorData, db: Session) -> StockPicksData:
        """
        Modified flow: FETCH & SAVE FIRST, then AI analysis
        This ensures no token waste if AI fails
        """
        macro_dict = {
            "USD": macro_data.usd,
            "Oil": macro_data.oil,
            "Gold": macro_data.gold,
            "Copper": macro_data.copper,
            "BTC": macro_data.btc
        }
        sector = sector_data.top_sector
        universe = self.get_universe(sector)

        sectors_client = AsyncSectorsClient()
        cache_manager = IntelligentCacheManager()
        await cache_manager.init_redis()

        # =====================================================================
        # STAGE 1: FETCH & SAVE ALL STOCKS (Secure the data!)
        # =====================================================================
        logger.info("📥 Stage 1: Fetching and saving stock data to database...")

        fetch_tasks = []
        for ticker in universe:
            fetch_tasks.append(
                self._fetch_and_save_stock(ticker, db, sectors_client, cache_manager)
            )

        fetch_results = await asyncio.gather(*fetch_tasks)
        valid_stocks = [r for r in fetch_results if r is not None]

        logger.info(f"✅ Stage 1 Complete: Saved {len(valid_stocks)}/{len(universe)} stocks to database")

        if not valid_stocks:
            logger.error("❌ No valid stocks fetched, cannot proceed")
            return StockPicksData(insight="No valid stock data available", picks=[])

        # =====================================================================
        # STAGE 2: AI ANALYSIS (Optional, can fail safely)
        # =====================================================================
        logger.info("🤖 Stage 2: Running AI analysis with multi-model fallback...")

        ai_result = None
        try:
            candidate_tickers = [s["record"].ticker for s in valid_stocks[:10]]

            ai_result = await self.ai.analyze_context_with_fallback(
                macro=macro_dict,
                sector=sector,
                candidates=candidate_tickers,
                max_retries=3
            )

            logger.info(f"✅ AI analysis completed with model: {ai_result.get('model_used')}")

            # Update database with AI insights
            ai_picks = ai_result.get('picks', [])
            ai_rationale = ai_result.get('rationale', {})

            for stock_data in valid_stocks:
                record = stock_data["record"]
                if record.ticker in ai_picks:
                    record.ai_processed = True
                    record.ai_model_used = ai_result.get('model_used')
                    record.ai_insight = ai_rationale.get(record.ticker, '')
                    record.ai_processed_at = datetime.utcnow()
                    record.ai_error = None

            db.commit()
            logger.info(f"✅ Updated {len(ai_picks)} stocks with AI insights")

        except Exception as e:
            logger.error(f"❌ AI analysis failed: {e}")

            # Update DB with error, but DON'T fail the request
            for stock_data in valid_stocks:
                record = stock_data["record"]
                record.ai_error = str(e)[:500]  # Truncate long errors

            db.commit()

            # Create fallback AI result
            ai_result = {
                "insight": f"AI temporarily unavailable: {str(e)[:100]}",
                "picks": [],
                "rationale": {},
                "model_used": "NONE"
            }

        # =====================================================================
        # STAGE 3: Build Response (with or without AI insights)
        # =====================================================================
        ai_insight = ai_result.get('insight', 'No AI insight available')
        ai_picks = ai_result.get('picks', [])
        ai_rationale = ai_result.get('rationale', {})

        # Convert to StockAudit objects for response
        stock_audits = []
        for stock_data in valid_stocks:
            record = stock_data["record"]
            sectors_data = stock_data["sectors_data"]
            yf_data = stock_data["yf_data"]

            is_ai = record.ticker in ai_picks
            ai_reason = ai_rationale.get(record.ticker, "-")

            audit = StockAudit(
                ticker=record.ticker,
                price=record.price,
                score=yf_data['score'],
                roe=record.roe,
                der=record.der,
                pbv=record.pbv,
                is_ai=is_ai,
                ai_reason=ai_reason,
                sectors_available=sectors_data.get('sectors_available', False),
                sectors_error=sectors_data.get('sectors_error'),
                sectors_score=record.sectors_score,
                sectors_valuation_score=record.valuation_score,
                sectors_growth_score=record.growth_score,
                sectors_dividend_score=record.dividend_score,
                sectors_ownership_score=record.ownership_score,
                forward_pe=record.forward_pe,
                intrinsic_value=record.intrinsic_value,
                eps_growth=record.eps_growth,
                revenue_growth=record.revenue_growth,
                dividend_yield=record.dividend_yield,
                payout_ratio=record.payout_ratio,
                institutional_flow=record.institutional_flow,
                whale_count=record.whale_count,
                conglomerate_count=record.conglomerate_count,
                fundamental_consensus=stock_data["consensus"],
                ai_insight=ai_insight
            )
            stock_audits.append(audit)

        # Sort: AI picks first, then by score
        stock_audits = sorted(stock_audits, key=lambda x: (not x.is_ai, -(x.score or 0)))

        logger.info(f"🎯 Final result: {len(stock_audits)} stocks, AI model: {ai_result.get('model_used')}")

        return StockPicksData(insight=ai_insight, picks=stock_audits)

