export const mockData = {
    timestamp: "2024-03-12 10:00:00",
    macro_status: "RISK ON",
    macro_reasoning: "Yield Rate mengalami penurunan, Gold mencapai titik All-Time-High mendongkrak pergerakan aset berisiko. USD terpantau sedikit melemah terhadap mata uang regional.",
    top_sector: "IDXENERGY",
    ai_insight: "Sektor energi mendominasi pergerakan hari ini berkat kenaikan harga Oil secara global dan pelemahan USD sementara. Saham-saham andalan sektor ini menunjukkan fundamental solid (ROE tinggi, DER terjaga).",
    macro_details: {
        yield_rate: 4.15,
        oil: 82.5,
        gold: 2160.5,
        usd: 15450.0,
        btc: 71200.0,
        copper: 4.25
    },
    signals: [
        { ticker: "ADRO.JK", action: "BUY", tag: "ON WEAKNESS", price: 2700.0, ma200: 2650.0, rsi: 42.5, trend: "UP", score: 85.0, sectors_score: 82.3 },
        { ticker: "PTBA.JK", action: "WAIT", tag: "CONSOLIDATION", price: 2900.0, ma200: 3000.0, rsi: 55.0, trend: "DOWN", score: 60.0, sectors_score: 55.0 },
        { ticker: "MEDC.JK", action: "BUY", tag: "BREAKOUT", price: 1450.0, ma200: 1300.0, rsi: 65.0, trend: "UP", score: 78.5, sectors_score: 75.0 },
        { ticker: "ITMG.JK", action: "WAIT", tag: "OVERBOUGHT", price: 26500.0, ma200: 25000.0, rsi: 76.0, trend: "UP", score: 50.0, sectors_score: 65.4 },
        { ticker: "PGAS.JK", action: "BUY", tag: "REVERSAL", price: 1100.0, ma200: 1150.0, rsi: 35.0, trend: "FLAT", score: 72.0, sectors_score: 68.0 }
    ]
};
