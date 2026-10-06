# Changelog: Token Loss Fix + Multi-AI Router Integration

**Date**: 2026-10-06
**Priority**: CRITICAL - Fixes actual token wastage

---

## Problem Statement

**Critical Issue:**
- User melakukan request → Sectors API dipanggil (80 tokens terpakai) → Gemini AI gagal (quota exceeded) → **Data hilang tanpa tersimpan** → 80 tokens terbuang percuma

**Root Cause:**
- Current flow: `Fetch API → AI Process → Save All Together`
- Jika AI gagal di tengah, data dari Sectors API (yang sudah menghabiskan tokens) tidak pernah sampai ke database
- Gemini hardcoded - single point of failure

---

## Solution Implemented

### ✅ 1. Multi-AI Router dengan Octalabs

**File Created/Modified:**
- `app/utils/multi_ai_client.py` (NEW) - Multi-model AI client with auto-fallback
- `requirements.txt` - Added `anthropic>=0.40.0`
- `.env` - Added Octalabs configuration
- `app/core/config.py` - Added Octalabs settings

**How it works:**
```python
# Try models in order: qwen3.8-max → minimax-m3-pay → kimi-k3 → etc.
# If one fails, automatically try the next
ai_result = await multi_ai_client.analyze_context_with_fallback(
    macro, sector, candidates, max_retries=3
)
```

**Models supported (in priority order):**
1. qwen3.8-max
2. minimax-m3-pay
3. kimi-k3
4. mimo-v2.5
5. mimo-v2.6-flash
6. deepseek-v4.1
7. minimax-m3
8. claude-sonnet-5

---

### ✅ 2. Database Model with AI Tracking

**File Modified:**
- `app/models/stock_fundamental.py` - Added AI tracking fields

**New Columns:**
- `ai_processed` (Boolean) - Whether AI analysis completed
- `ai_model_used` (String) - Which model succeeded (e.g. "qwen3.8-max")
- `ai_insight` (Text) - AI-generated insight for this stock
- `ai_processed_at` (DateTime) - When AI analysis ran
- `ai_error` (Text) - Error message if AI failed
- `sectors_fetched_at` (DateTime) - When Sectors API was called

**Purpose:** Track AI processing status separately from data fetching

---

### ✅ 3. Refactored Phase3: Save Immediately

**File Modified:**
- `app/services/phase3_picker.py` - Complete rewrite with 2-stage flow

**Old Flow (BROKEN):**
```
Fetch from APIs → AI Analysis → Save Everything
                      ↓ FAIL
                  All data lost!
```

**New Flow (FIXED):**
```
STAGE 1: Fetch & Save
├─ For each stock:
│  ├─ Fetch from Sectors API (8 tokens)
│  ├─ Fetch from YFinance (free)
│  └─ SAVE TO DATABASE IMMEDIATELY ✅
│
STAGE 2: AI Analysis (Safe to fail)
├─ Try Model 1
├─ Try Model 2 (if Model 1 fails)
├─ Try Model 3 (if Model 2 fails)
└─ Update DB with AI insights (or log error)
```

**Key Changes:**
- New method: `_fetch_and_save_stock()` - Saves immediately after fetch
- Uses `db.merge()` to handle updates
- Logs token usage per stock (8 tokens each)
- AI failure doesn't prevent returning stock data
- Graceful degradation: Returns data with or without AI insights

---

## Technical Details

### Import Changes

**Before:**
```python
from app.utils.gemini_client import AsyncGeminiAnalyst
```

**After:**
```python
from app.utils.multi_ai_client import MultiAIClient
from app.models.stock_fundamental import StockFundamental
from app.services.cache_manager import IntelligentCacheManager
```

### Database Integration

```python
# Create record immediately after fetch
stock_record = StockFundamental(
    ticker=ticker,
    price=yf_res['price'],
    sectors_score=sectors_res.get('sectors_score'),
    # ... all other fields ...
    sectors_fetched_at=datetime.utcnow(),
    ai_processed=False,  # Not yet processed
)

# SAVE NOW (critical fix!)
db.merge(stock_record)
db.commit()

# Log token usage
await cache_manager.log_token_usage(
    endpoint="phase3_picker",
    provider="SECTORS_API",
    tokens_used=8,
    request_params={"ticker": ticker}
)
```

### AI Fallback Logic

```python
try:
    ai_result = await self.ai.analyze_context_with_fallback(
        macro=macro_dict,
        sector=sector,
        candidates=candidate_tickers,
        max_retries=3
    )
    
    # Update DB with AI results
    for stock in stocks:
        if stock.ticker in ai_result['picks']:
            stock.ai_processed = True
            stock.ai_model_used = ai_result['model_used']
            stock.ai_insight = ai_result['rationale'][stock.ticker]
    
    db.commit()
    
except Exception as e:
    logger.error(f"AI failed: {e}")
    
    # Log error but DON'T fail request
    for stock in stocks:
        stock.ai_error = str(e)
    db.commit()
    
    # Return fallback AI result
    ai_result = {
        "insight": f"AI temporarily unavailable: {e}",
        "picks": [],
        "rationale": {},
        "model_used": "NONE"
    }

# Return stocks (with or without AI)
return StockPicksData(...)
```

---

## Configuration

### Environment Variables (.env)

```env
# AI Configuration (Octalabs Router)
OCTALABS_BASE_URL=https://router.octalabs.id
OCTALABS_API_KEY=octa-b9dc4eec136d4025f42782b2d2e7fce0
AI_MODELS=qwen3.8-max,minimax-m3-pay,kimi-k3,mimo-v2.5,mimo-v2.6-flash,deepseek-v4.1,minimax-m3,claude-sonnet-5
AI_MAX_RETRIES=3
```

---

## Benefits

### ✅ No More Token Loss
- Sectors API data saved immediately to database
- Even if AI fails, data persists
- Token usage logged accurately

### ✅ Multi-Model Resilience
- Not dependent on single AI provider
- Auto-fallback to next model on failure
- Logs which model succeeded

### ✅ Graceful Degradation
- Returns stock data even if all AI models fail
- Users still get fundamental analysis
- AI insights optional, not required

### ✅ Better Observability
- Database tracks: which model used, when, success/failure
- Can analyze which models are most reliable
- Can retry failed AI processing later

---

## Migration Required

After deploying, run:

```bash
docker-compose exec api alembic revision --autogenerate -m "add ai tracking fields"
docker-compose exec api alembic upgrade head
```

---

## Testing Checklist

- [ ] Sectors API data persists even if AI fails
- [ ] Multi-AI fallback works (Model 1 → Model 2 → Model 3)
- [ ] Token usage logged correctly (80 tokens for 10 stocks)
- [ ] Response includes `ai_model_used` field
- [ ] Database has new AI tracking columns
- [ ] Old data still readable

---

## Known Issues

- None currently

---

## Future Improvements

1. Add retry mechanism for failed AI processing
2. Background job to process AI for stocks with `ai_processed=false`
3. A/B test different models for quality comparison
4. Cache AI results per macro condition
