import yfinance as yf
import pandas as pd
from datetime import datetime
import asyncio
from app.schemas.macro import MacroData

class MacroGlobalSensorService:
    def __init__(self):
        self.tickers = {
            'DXY': 'DX-Y.NYB',
            'US10Y': '^TNX',
            'USD_IDR': 'USDIDR=X',
            'OIL': 'CL=F',
            'GOLD': 'GC=F',
            'COPPER': 'HG=F',
            'BITCOIN': 'BTC-USD',
            'EIDO': 'EIDO'
        }

    async def fetch_data(self):
        ticker_list = list(self.tickers.values())
        try:
            # yf.download bersifat blocking (synchronous), 
            # kita jalankan di thread terpisah agar tidak memblokir event loop FastAPI
            data = await asyncio.to_thread(
                yf.download, 
                tickers=ticker_list, 
                period="5d", 
                interval="1d", 
                progress=False
            )
            
            # Handle YFinance structure (could be MultiIndex depending on version)
            if 'Close' in data:
                data = data['Close']
                
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = [col[0] if isinstance(col, tuple) else col for col in data.columns]

            report = {}
            current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            report['timestamp'] = current_date

            for readable_name, symbol in self.tickers.items():
                if symbol in data.columns:
                    series = data[symbol].dropna()
                    if len(series) >= 2:
                        last_price = series.iloc[-1]
                        prev_price = series.iloc[-2]
                        change_pct = ((last_price - prev_price) / prev_price) * 100
                        report[readable_name] = float(round(last_price, 2))
                        report[f"{readable_name}_Chg"] = float(round(change_pct, 2))
                    else:
                        report[readable_name] = 0.0
                        report[f"{readable_name}_Chg"] = 0.0
            return report
        except Exception as e:
            print(f"Fetch Error: {e}")
            return None

    def analyze_sentiment(self, data):
        if not data: return "NO DATA", "System Error"
        risk_score = 0
        reasons = []

        usd_idr = data.get('USD_IDR', 0)
        if usd_idr > 16500:
            risk_score += 3
            reasons.append(f"IDR Weakness (>16.5k)")
        elif data.get('USD_IDR_Chg', 0) > 0.5:
            risk_score += 1
            reasons.append("IDR Depreciating")

        if data.get('US10Y_Chg', 0) > 1.5:
            risk_score += 2
            reasons.append("US Yield Spike")

        comm_score = 0
        if data.get('OIL_Chg', 0) > 1: comm_score += 1
        if data.get('COPPER_Chg', 0) > 1: comm_score += 1
        if data.get('GOLD_Chg', 0) > 1: comm_score += 1

        if comm_score >= 2:
            risk_score -= 1
            reasons.append("Commodity Rally")

        if data.get('EIDO_Chg', 0) > 0.5:
            risk_score -= 2
            reasons.append("EIDO Inflow")

        if risk_score >= 3:
            sentiment = "RISK OFF (DEFENSIVE)"
        elif risk_score >= 1:
            sentiment = "CAUTIOUS / NEUTRAL"
        elif risk_score <= -2:
            sentiment = "RISK ON (AGGRESSIVE)"
        else:
            sentiment = "NEUTRAL"

        if not reasons: reasons.append("Flat Market")
        return sentiment, ", ".join(reasons)

    async def run(self) -> MacroData:
        data = await self.fetch_data()
        if not data:
            raise Exception("Failed to fetch macro data from Yahoo Finance.")
            
        sentiment, reason = self.analyze_sentiment(data)
        
        # Kembalikan data dalam bentuk objek Stateless (Pydantic Model)
        # Bukan disimpan ke variabel _SHARED_MACRO_DATA lagi
        return MacroData(
            timestamp=data['timestamp'],
            status=sentiment,
            reasoning=reason,
            usd=data.get('USD_IDR', 0),
            usd_chg=data.get('USD_IDR_Chg', 0),
            oil=data.get('OIL', 0),
            oil_chg=data.get('OIL_Chg', 0),
            gold=data.get('GOLD', 0),
            gold_chg=data.get('GOLD_Chg', 0),
            copper=data.get('COPPER', 0),
            copper_chg=data.get('COPPER_Chg', 0),
            yield_rate=data.get('US10Y', 0),
            yield_chg=data.get('US10Y_Chg', 0),
            eido=data.get('EIDO_Chg', 0),
            eido_val=data.get('EIDO', 0),
            btc=data.get('BITCOIN', 0),
            btc_chg=data.get('BITCOIN_Chg', 0)
        )
