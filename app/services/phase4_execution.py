import yfinance as yf
import pandas as pd
# import pandas_ta as ta  # TODO: Add back when pandas_ta is compatible
import asyncio
from typing import List
from app.schemas.stock import StockPicksData, StockAudit
from app.schemas.report import TradeSignal

class ExecutionSniperProService:

    @staticmethod
    def calculate_rsi(series, period=14):
        """Calculate RSI manually without pandas_ta"""
        delta = series.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    @staticmethod
    async def analyze_technical(ticker: str):
        def _fetch_tech():
            try:
                df = yf.download(ticker, period="1y", interval="1d", progress=False)
                if len(df) < 50: return None

                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]

                close = df['Close']
                ma200 = close.rolling(200).mean().iloc[-1]
                if pd.isna(ma200):
                    ma200 = close.rolling(50).mean().iloc[-1]

                # Use manual RSI calculation instead of pandas_ta
                rsi = ExecutionSniperProService.calculate_rsi(close, 14).iloc[-1]
                vol_spike = bool(df['Volume'].iloc[-1] > (1.5 * df['Volume'].rolling(20).mean().iloc[-1]))
                sl_level = float(df['Low'].tail(20).min())
                price = float(close.iloc[-1])
                trend = "UP" if price > ma200 else "DOWN"

                return {
                    "price": price,
                    "ma200": float(ma200),
                    "rsi": float(rsi),
                    "trend": trend,
                    "vol_spike": vol_spike,
                    "sl_level": sl_level
                }
            except Exception as e:
                print(f"Technical Analysis Error on {ticker}: {e}")
                return None

        return await asyncio.to_thread(_fetch_tech)

    def determine_signal(self, target: StockAudit, tech: dict):
        fund_score = target.score or 0
        ai_pick = target.is_ai
        trend = tech['trend']
        rsi = tech['rsi']

        action = "WAIT"
        tag = "NEUTRAL"

        if trend == "UP":
            if fund_score >= 60:
                if rsi < 45: action, tag = "BUY", "ON WEAKNESS"
                elif rsi < 70: action, tag = "BUY", "MOMENTUM"
                else: action, tag = "WAIT", "OVERBOUGHT"
            elif ai_pick:
                if rsi < 70: action, tag = "BUY", "SPECULATIVE"
                else: action, tag = "WAIT", "PULLBACK"
        else:
            if fund_score >= 80 and rsi < 30: action, tag = "BUY", "BOTTOM FISH"
            else: action, tag = "WAIT", "DOWNTREND"

        return action, tag

    async def run(self, stock_picks: StockPicksData) -> List[TradeSignal]:
        targets = stock_picks.picks
        if not targets:
            return []

        # Analyze technicals concurrently for all targets
        tasks = [self.analyze_technical(t.ticker) for t in targets]
        tech_results = await asyncio.gather(*tasks)

        orders = []
        for target, tech in zip(targets, tech_results):
            if tech:
                action, tag = self.determine_signal(target, tech)
                
                # Menggabungkan data target (fundamental) dengan technical
                signal_data = target.model_dump()
                signal_data.update({
                    "action": action,
                    "tag": tag,
                    "ma200": tech['ma200'],
                    "rsi": tech['rsi'],
                    "trend": tech['trend'],
                    "vol_spike": tech['vol_spike'],
                    "sl_level": tech['sl_level']
                })
                orders.append(TradeSignal(**signal_data))

        return orders
