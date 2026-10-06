import yfinance as yf
import asyncio
from app.schemas.macro import MacroData
from app.schemas.sector import SectorData
from app.schemas.stock import StockPicksData, StockAudit
from app.utils.gemini_client import AsyncGeminiAnalyst
from app.utils.sectors_client import AsyncSectorsClient

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
        self.ai = AsyncGeminiAnalyst()

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

    async def _audit_single_stock(self, ticker: str, is_ai: bool, ai_reason: str, sectors_client: AsyncSectorsClient):
        yf_task = StockAuditorProService.audit(ticker)
        sectors_task = sectors_client.analyze(ticker)

        # Eksekusi Yahoo Finance & Sectors API secara paralel (bersamaan)
        yf_res, sectors_res = await asyncio.gather(yf_task, sectors_task)

        if not yf_res:
            return None # Skip jika data bermasalah/harga tidak ada

        consensus = self._fundamental_consensus(yf_res.get('score'), sectors_res.get('sectors_score'))

        return StockAudit(
            ticker=ticker,
            price=yf_res['price'],
            score=yf_res['score'],
            roe=yf_res['roe'],
            der=yf_res['der'],
            pbv=yf_res['pbv'],
            is_ai=is_ai,
            ai_reason=ai_reason,
            sectors_available=sectors_res['sectors_available'],
            sectors_error=sectors_res['sectors_error'],
            sectors_score=sectors_res['sectors_score'],
            sectors_valuation_score=sectors_res['valuation_score'],
            sectors_growth_score=sectors_res['growth_score'],
            sectors_dividend_score=sectors_res['dividend_score'],
            sectors_ownership_score=sectors_res['ownership_score'],
            forward_pe=sectors_res['forward_pe'],
            intrinsic_value=sectors_res['intrinsic_value'],
            eps_growth=sectors_res['eps_growth'],
            revenue_growth=sectors_res['revenue_growth'],
            dividend_yield=sectors_res['dividend_yield'],
            payout_ratio=sectors_res['payout_ratio'],
            institutional_flow=sectors_res['institutional_flow'],
            whale_count=sectors_res['whale_count'],
            conglomerate_count=sectors_res['conglomerate_count'],
            fundamental_consensus=consensus,
            ai_insight=""
        )

    async def run(self, macro_data: MacroData, sector_data: SectorData) -> StockPicksData:
        macro_dict = {
            "USD": macro_data.usd,
            "Oil": macro_data.oil,
            "Gold": macro_data.gold,
            "Copper": macro_data.copper,
            "BTC": macro_data.btc
        }
        sector = sector_data.top_sector
        candidates = self.get_universe(sector)

        # 1. Gemini AI Analysis (Mendapatkan sentimen secara asinkron)
        ai_res = await self.ai.analyze_context(macro_dict, sector, candidates)
        ai_tickers = ai_res.get('picks', [])
        ai_insight = ai_res.get('insight', 'No specific narrative')
        ai_rationale = ai_res.get('rationale', {})

        # 2. Audit concurrently using asyncio.gather untuk 5-10 kandidat saham secara paralel
        sectors_client = AsyncSectorsClient()
        tasks = []
        for ticker in candidates:
            is_ai = ticker in ai_tickers
            reason = ai_rationale.get(ticker, "-")
            tasks.append(self._audit_single_stock(ticker, is_ai, reason, sectors_client))

        results = await asyncio.gather(*tasks)
        valid_results = [res for res in results if res is not None]

        # 3. Sorting & Populating AI Insight
        valid_results = sorted(valid_results, key=lambda x: (not x.is_ai, -(x.score or 0)))
        for r in valid_results:
            r.ai_insight = ai_insight

        return StockPicksData(insight=ai_insight, picks=valid_results)
