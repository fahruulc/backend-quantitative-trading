# Quant Trading System - API Documentation

Sistem ini adalah API berarsitektur *microservices-pattern* untuk *Algorithmic Trading* (Quant Trading) berbasis Macro-Driven yang dieksekusi secara bertahap (Fase 1 hingga 4).

## 📌 Konteks Alur Kerja (Workflow)
Sistem ini memproses data secara berurutan dan *paralel*:
1. **Fase 1 (Macro Sensor):** Mengambil data ekonomi makro (Yield, Oil, Gold, USD, EIDO, BTC) via YFinance.
2. **Fase 2 (Sector Rotation):** Memilih sektor terkuat (contoh: `IDXENERGY`, `IDXFINANCE`) berdasarkan skor matriks makro dari Fase 1.
3. **Fase 3 (Intelligent Stock Picker):** Menggunakan **Gemini AI** dan **Sectors API** untuk mensortir dan mengaudit skor Fundamental saham-saham teratas di sektor terpilih secara serentak (paralel).
4. **Fase 4 (Execution Sniper):** Menggunakan Analisis Teknikal (`pandas_ta`) untuk menentukan sinyal *trading* final (`BUY`, `WAIT`), level *Stop Loss*, dan tren MA200.

---

## 🔐 Keamanan (Security & CORS)
Demi keamanan dari serangan lintas situs (*Cross-Site Request Forgery*), API ini telah dilengkapi dengan pengaman **CORS**. 
Secara *default*, *endpoint* hanya mengizinkan *request* dari:
- `http://localhost:3000` (Local Frontend/Next.js)
- `https://your-frontend.com` (Domain production frontend Anda)
Untuk menambahkan domain lain, edit array `origins` di file `app/main.py`.

---

## 🚀 Daftar Endpoints

Semua endpoint berawalan dengan *base path*: `/api/v1/analysis`

### 1. `GET /macro`
Menjalankan hanya Fase 1 (Analisis Makro). Berguna untuk menampilkan dasbor status pasar secara umum.
- **Parameters:** None
- **Response (200 OK):**
```json
{
  "yield_rate": 4.5,
  "oil": 85.2,
  "gold": 2100.5,
  "copper": 4.2,
  "usd": 15500.0,
  "eido": 23.5,
  "btc": 65000.0,
  "status": "RISK ON",
  "reasoning": "Yield rate stable, Gold high...",
  "timestamp": "2024-03-12 10:00:00"
}
```

### 2. `GET /sectors`
Menjalankan Fase 1 lalu merotasi sektor terbaik. Berguna jika UI hanya butuh melihat _leaderboard_ sektor tanpa merekomendasikan saham.
- **Parameters:** None
- **Response (200 OK):**
```json
{
  "macro_data": { ... },
  "sector_data": {
    "sorted_sectors": {
      "IDXENERGY": 85.5,
      "IDXFINANCE": 60.0
    },
    "top_sector": "IDXENERGY"
  }
}
```

### 3. `GET /stocks`
(Fase 1-3) Menganalisis sektor lalu memberikan rekomendasi saham berdasarkan skor Fundamental Sectors API dan narasi Gemini AI.
- **Parameters:** None
- **Response (200 OK):**
```json
{
  "insight": "Sektor energi mendominasi karena naiknya harga minyak dan pelemahan USD.",
  "picks": [
    {
      "ticker": "ADRO.JK",
      "price": 2700,
      "score": 85.0,
      "roe": 25.5,
      "is_ai": true,
      "ai_reason": "Korelasi tinggi ke harga Oil",
      "fundamental_consensus": "CONFIRMED"
    }
  ]
}
```

### 4. `GET /full-report` (🌟 MASTER ENDPOINT)
Menjalankan keseluruhan *pipeline* (Fase 1 hingga Fase 4). Menghasilkan Sinyal Eksekusi Final.
⚠️ **Penting:** Endpoint ini di-***Cache*** oleh Redis. Hasilnya disimpan selama 1 Jam. Request berikutnya (dalam 1 jam) akan dikembalikan secara instan dari RAM.
- **Parameters:** None
- **Response (200 OK):**
```json
{
  "timestamp": "2024-03-12 10:00:00",
  "macro_status": "RISK ON",
  "macro_reasoning": "Narrative detail...",
  "top_sector": "IDXENERGY",
  "ai_insight": "Insight summary...",
  "signals": [
    {
      "ticker": "ADRO.JK",
      "action": "BUY",
      "tag": "ON WEAKNESS",
      "price": 2700.0,
      "ma200": 2650.0,
      "rsi": 42.5,
      "trend": "UP",
      "vol_spike": false,
      "sl_level": 2500.0,
      "score": 85.0,
      "sectors_available": true
    }
  ]
}
```
