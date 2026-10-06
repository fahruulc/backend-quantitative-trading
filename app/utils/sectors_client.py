import httpx
from app.core.config import get_settings

settings = get_settings()

class AsyncSectorsClient:
    BASE_URL = "https://api.sectors.app/v2/company/report"

    def __init__(self, timeout=15):
        self.api_key = settings.SECTORS_API_KEY
        self.timeout = timeout

    @staticmethod
    def _to_float(value, default=None):
        try:
            if value is None or value == "":
                return default
            return float(value)
        except (TypeError, ValueError):
            return default

    @staticmethod
    def _pct(value):
        val = AsyncSectorsClient._to_float(value)
        if val is None: return None
        return val * 100 if abs(val) <= 2 else val

    @staticmethod
    def _count_items(value):
        if isinstance(value, (list, tuple, set, dict)):
            return len(value)
        return None

    async def get_report(self, ticker: str):
        symbol = ticker.replace(".JK", "").upper()
        if not self.api_key or self.api_key == "your_sectors_api_key_here":
            return None, "SECTORS_API_KEY is not configured"

        url = f"{self.BASE_URL}/{symbol}/"
        headers = {
            "Authorization": self.api_key,
            "Accept": "application/json",
            "User-Agent": "QuantTrading-FastAPI/1.0"
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=headers, timeout=self.timeout)
                if response.status_code == 401:
                    return None, "Sectors API authentication failed (401)"
                if response.status_code == 403:
                    return None, "Sectors API access forbidden (403)"
                if response.status_code == 404:
                    return None, f"Company report not found for {symbol}"
                response.raise_for_status()
                payload = response.json()
                if not isinstance(payload, dict):
                    return None, "Unexpected response format"
                return payload, None
            except httpx.TimeoutException:
                return None, "Sectors API request timed out"
            except Exception as e:
                return None, f"Sectors API request failed: {e}"

    def _valuation_score(self, forward_pe, intrinsic_value, data):
        points = []
        if forward_pe is not None:
            if forward_pe <= 10: points.append(90)
            elif forward_pe <= 15: points.append(80)
            elif forward_pe <= 20: points.append(70)
            elif forward_pe <= 30: points.append(55)
            else: points.append(40)

        current_price = self._to_float(data.get("last_close_price", data.get("price")))
        if current_price and intrinsic_value and current_price > 0:
            upside = (intrinsic_value - current_price) / current_price
            if upside >= 0.50: points.append(95)
            elif upside >= 0.20: points.append(85)
            elif upside >= 0.05: points.append(75)
            elif upside >= -0.05: points.append(60)
            elif upside >= -0.20: points.append(45)
            else: points.append(30)
        return round(sum(points) / len(points), 1) if points else None

    def _growth_score(self, eps_growth, revenue_growth):
        values = []
        for growth in [eps_growth, revenue_growth]:
            if growth is not None:
                if growth >= 20: values.append(95)
                elif growth >= 10: values.append(85)
                elif growth >= 5: values.append(75)
                elif growth >= 0: values.append(60)
                elif growth >= -10: values.append(45)
                else: values.append(30)
        return round(sum(values) / len(values), 1) if values else None

    def _dividend_score(self, dividend_yield, payout_ratio):
        values = []
        if dividend_yield is not None:
            if dividend_yield >= 7: values.append(95)
            elif dividend_yield >= 5: values.append(85)
            elif dividend_yield >= 3: values.append(75)
            elif dividend_yield >= 1: values.append(60)
            else: values.append(45)
        if payout_ratio is not None:
            if 30 <= payout_ratio <= 70: values.append(85)
            elif 20 <= payout_ratio < 30 or 70 < payout_ratio <= 90: values.append(70)
            elif payout_ratio < 20: values.append(60)
            else: values.append(40)
        return round(sum(values) / len(values), 1) if values else None

    def _ownership_score(self, institutional_flow, whale_investors, conglomerates):
        points = []
        if isinstance(institutional_flow, (list, tuple, dict)):
            n = self._count_items(institutional_flow)
            points.append(min(95, 60 + (n or 0) * 5))
        elif institutional_flow is not None:
            points.append(65)

        whale_count = self._count_items(whale_investors)
        if whale_count is not None: points.append(min(90, 60 + whale_count * 5))

        conglomerate_count = self._count_items(conglomerates)
        if conglomerate_count is not None: points.append(min(85, 55 + conglomerate_count * 5))
        return round(sum(points) / len(points), 1) if points else None

    async def analyze(self, ticker: str):
        # Demo mode: Return mock data without consuming tokens
        if settings.DEMO_MODE and settings.USE_MOCK_DATA:
            print(f"🎭 DEMO MODE: Using mock Sectors data for {ticker} (no tokens used)")
            return {
                "sectors_available": True, "sectors_error": None, "sectors_score": 75.0,
                "valuation_score": 80.0, "growth_score": 70.0,
                "dividend_score": 65.0, "ownership_score": 72.0,
                "forward_pe": 12.5, "intrinsic_value": 3500.0,
                "eps_growth": 15.5, "revenue_growth": 12.3,
                "dividend_yield": 4.2, "payout_ratio": 55.0,
                "institutional_flow": "positive", "whale_count": 3,
                "conglomerate_count": 2,
            }

        data, error = await self.get_report(ticker)
        if not data:
            return {
                "sectors_available": False, "sectors_error": error, "sectors_score": None,
                "valuation_score": None, "growth_score": None, "dividend_score": None,
                "ownership_score": None, "forward_pe": None, "intrinsic_value": None,
                "eps_growth": None, "revenue_growth": None, "dividend_yield": None,
                "payout_ratio": None, "institutional_flow": None, "whale_count": None,
                "conglomerate_count": None,
            }

        valuation = data.get("valuation") or {}
        future = data.get("future") or {}
        financials = data.get("financials") or {}
        dividend = data.get("dividend") or {}
        ownership = data.get("ownership") or {}

        forward_pe = self._to_float(valuation.get("forward_pe") or valuation.get("pe_forward") or valuation.get("forward_pe_ratio"))
        intrinsic_value = self._to_float(valuation.get("intrinsic_value") or valuation.get("fair_value"))

        eps_growth_raw = future.get("eps_growth") or future.get("earnings_growth") or financials.get("eps_growth") or financials.get("earnings_growth") or data.get("eps_growth") or data.get("earnings_growth") or data.get("yoy_quarter_earnings_growth")
        revenue_growth_raw = future.get("revenue_growth") or future.get("sales_growth") or financials.get("revenue_growth") or financials.get("sales_growth") or data.get("revenue_growth") or data.get("sales_growth") or data.get("yoy_quarter_revenue_growth")
        eps_growth = self._pct(eps_growth_raw)
        revenue_growth = self._pct(revenue_growth_raw)

        dividend_yield = self._pct(dividend.get("yield_ttm") or dividend.get("dividend_yield") or data.get("yield_ttm") or data.get("dividend_yield"))
        payout_ratio = self._pct(dividend.get("payout_ratio") or data.get("payout_ratio"))
        institutional_flow = ownership.get("institutional_transaction_flow") or ownership.get("institutional_flow") or data.get("institutional_transaction_flow")
        whale_investors = ownership.get("whale_investors") or data.get("whale_investors")
        conglomerates = ownership.get("conglomerates_group") or data.get("conglomerates_group")

        valuation_score = self._valuation_score(forward_pe, intrinsic_value, data)
        growth_score = self._growth_score(eps_growth, revenue_growth)
        dividend_score = self._dividend_score(dividend_yield, payout_ratio)
        ownership_score = self._ownership_score(institutional_flow, whale_investors, conglomerates)

        components = [x for x in [valuation_score, growth_score, dividend_score, ownership_score] if x is not None]
        sectors_score = round(sum(components) / len(components), 1) if components else None

        return {
            "sectors_available": True, "sectors_error": None, "sectors_score": sectors_score,
            "valuation_score": valuation_score, "growth_score": growth_score,
            "dividend_score": dividend_score, "ownership_score": ownership_score,
            "forward_pe": forward_pe, "intrinsic_value": intrinsic_value,
            "eps_growth": eps_growth, "revenue_growth": revenue_growth,
            "dividend_yield": dividend_yield, "payout_ratio": payout_ratio,
            "institutional_flow": institutional_flow,
            "whale_count": self._count_items(whale_investors),
            "conglomerate_count": self._count_items(conglomerates),
        }
