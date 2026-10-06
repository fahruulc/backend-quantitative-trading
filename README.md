# Quant Trading — Market Intelligence

REST API + dashboard untuk analisis pasar saham Indonesia (IDX): macro sensors,
sector rotation, stock picker berbasis AI, dan technical chart — dengan token
optimization (cache Redis + pre-fetch harian) agar konsumsi API minimal.

**Stack:** FastAPI · Vue 3 (Vite + Tailwind + ApexCharts) · PostgreSQL · Redis · Docker Compose

---

## 1. Quick Start (untuk anggota tim)

```bash
# 1) Clone & masuk folder
git clone <repo-url> && cd program-fahrul

# 2) Siapkan environment
cp .env.example .env
#    → isi GEMINI_API_KEY & SECTORS_API_KEY (boleh dikosongkan dulu untuk mode demo)

# 3) Nyalakan backend (postgres :5433, redis :6379, api :8000)
docker compose up -d

# 4) Isi database dengan data demo (sekali saja)
docker compose exec api python -m app.scripts.seed_database

# 5) Nyalakan frontend (di terminal terpisah)
cd frontend
npm install
npm run dev        # → http://localhost:5173 (proxy /api → :8000, tanpa CORS)
```

Buka `http://localhost:5173` — Overview, Macro Sensors, Sector Rotation,
Stock Signals, Heatmap, dan Technical Chart (`/technical/:ticker`) sudah terisi.

---

## 2. Arsitektur Singkat

```
frontend/ (Vue 3)  ──proxy /api──▶  app/ (FastAPI :8000)
                                      ├─ api/endpoints/analysis.py   → pipeline Fase 1–4 (/macro, /sectors, /stocks, /full-report)
                                      ├─ api/endpoints/frontend.py   → data untuk dashboard (/frontend/*, /frontend/chart/{ticker})
                                      ├─ api/endpoints/admin.py      → token usage, prefetch, health
                                      ├─ services/                   → phase1–4, chart_service, telegram_service, cache_manager
                                      ├─ tasks/prefetch_job.py       → pre-fetch harian 07:00 + morning brief Telegram
                                      └─ models/                     → StockFundamental, MarketSnapshot, APIUsage, AnomalyScore
PostgreSQL :5433 (internal 5432)  ·  Redis :6379 (cache 1 jam + stock:{ticker})
```

**Endpoint utama**
| Endpoint | Isi |
|---|---|
| `GET /api/v1/full-report` | Pipeline lengkap Fase 1–4 (macro → sector → picks → signals) |
| `GET /api/v1/frontend/macro-sensors` | Snapshot makro terbaru (dari DB) |
| `GET /api/v1/frontend/sector-rotation` | Perbandingan sektor (dari DB) |
| `GET /api/v1/frontend/stock-signals` | Sinyal saham + fundamental (dari DB) |
| `GET /api/v1/frontend/heatmap` | Heatmap per sektor (dari DB) |
| `GET /api/v1/frontend/chart/{ticker}?interval=1d\|1wk` | OHLC + MA (yfinance, cache 1 jam) |

---

## 3. Mode Demo vs API Asli

| | Demo (default, tanpa API key) | Live (API asli) |
|---|---|---|
| Yang berubah | — | isi `GEMINI_API_KEY` + `SECTORS_API_KEY` valid di `.env`, lalu `docker compose restart api` |
| `/full-report` | fallback demo (5 sinyal + macro lengkap, `data_source: "DEMO"`) | hasil pipeline nyata |
| Data `/frontend/*` | dari seeder/backfill dummy di DB | ditimpa pipeline saat fetch berhasil |

Fallback demo **otomatis nonaktif** saat pipeline sukses — tidak ada flag yang perlu diubah.
Label model AI ditampilkan apa adanya di UI (mis. `demo-model`, `qwen3.8-max`).

---

## 4. Telegram — Morning Brief (1x per hari, jam 07:00)

- Scheduler `daily_prefetch` (07:00) menarik data fundamental → simpan ke DB → **kirim morning brief ke Telegram** berisi kondisi makro + top 5 stock picks **yang dibaca dari DB** (bukan panggil API lagi).
- **Tidak ada pemanggilan API ke-2** — Telegram hanya membaca hasil yang sudah ada.
- Kalau token belum diisi atau DB kosong → skip dengan aman (sistem tetap jalan).

**Setup:**
1. Buat bot via [@BotFather](https://t.me/BotFather) → dapat `TELEGRAM_BOT_TOKEN`.
2. Dapatkan `chat_id` (kirim pesan ke bot, lalu buka `https://api.telegram.org/bot<TOKEN>/getUpdates`).
3. Isi keduanya di `.env` → `docker compose restart api`.

**Estimasi konsumsi API (untuk persiapan beli API):**
| Item | Token |
|---|---|
| Pre-fetch 17 saham × 8 token | **136 / hari** |
| Telegram sendMessage | 0 (Bot API gratis) |
| AI analysis (jika aktif) | ±10–30 / hari |
| **Total** | **~136–166 / hari** |
| **Per bulan (pre-fetch saja)** | **~4.080 token** |

**Batasan konsumsi:** tiap saham maksimal di-fetch **1x per hari** — job memeriksa
`last_updated >= hari ini 00:00` di DB dan me-skip yang sudah fresh (0 token),
meskipun job terpicu berkali-kali / container restart.

---

## 5. Testing

```bash
pip install -r requirements.txt -r requirements-dev.txt
pytest tests/ -v
```

Test berjalan **tanpa internet / API key / Postgres / Redis**:
- `test_frontend_endpoints.py` — shape & grouping endpoint `/frontend/*` (SQLite in-memory)
- `test_chart.py` — candles + MA20/50/200 dengan yfinance di-mock
- `test_telegram_brief.py` — brief dari DB + send_message di-mock
- `test_full_report_fallback.py` — fallback demo memakai fixture `tests/fixtures/dummydataoutput.txt`

---

## 6. Troubleshooting

| Masalah | Solusi |
|---|---|
| Frontend "Failed to load data" | Cek API hidup: `curl localhost:8000/health`. Frontend pakai proxy Vite (`/api`→`:8000`), jadi tidak ada masalah CORS/port. |
| Edit backend tapi tidak berubah | Container tidak me-mount kode lokal: `docker cp <file> quant_api:/app/<file> && docker compose restart api` (atau rebuild: `docker compose up -d --build api`). |
| Data lama/nge-cache | Flush Redis: `docker compose exec redis redis-cli FLUSHALL` |
| Port 5173 dipakai proses lama | Vite otomatis pindah port (5174/5175…); pakai port yang muncul di log. |
| Semua halaman kosong | Jalankan seeder: `docker compose exec api python -m app.scripts.seed_database` |
