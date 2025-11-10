# 🚀 Deployment Guide - AI Learning System

## Overview

This guide covers deploying the enhanced bot with:
- **PostgreSQL Database** (Railway) for analysis history
- **WebSocket Price Tracking** for auto TP/SL monitoring
- **AI Historical Learning** system

---

## 📋 Prerequisites

1. Railway account (railway.app)
2. Existing bot deployed on Railway
3. Access to Railway dashboard

---

## 🗄️ Step 1: Add PostgreSQL to Railway

### 1.1 Add Database Addon

1. Go to your Railway project dashboard
2. Click **"+ New"** → **"Database"** → **"PostgreSQL"**
3. Wait for provisioning (1-2 minutes)

### 1.2 Get DATABASE_URL

1. Click on the PostgreSQL service
2. Go to **"Variables"** tab
3. Find `DATABASE_URL` - it looks like:
   ```
   postgresql://postgres:PASSWORD@HOST:PORT/railway
   ```
4. Copy this entire URL

### 1.3 Add to Bot Environment

1. Go to your **Bot service** (not database)
2. Click **"Variables"** tab
3. Click **"+ New Variable"**
4. Add:
   - **Name:** `DATABASE_URL`
   - **Value:** (paste the URL you copied)
5. Click **"Add"**

---

## 📦 Step 2: Deploy Updated Code

### 2.1 Verify Files

Make sure these files exist in your repository:
```
✓ database.py               (PostgreSQL module)
✓ price_tracker.py          (WebSocket tracker)
✓ gemini_analyzer.py        (Updated with history)
✓ requirements.txt          (psycopg2-binary, websockets)
```

### 2.2 Push to Repository

```bash
git add .
git commit -m "Add AI learning system with PostgreSQL"
git push origin main
```

### 2.3 Railway Auto-Deploy

Railway will automatically:
1. Detect changes
2. Install new dependencies (psycopg2, websockets)
3. Restart the bot
4. Initialize database schema on first run

---

## ✅ Step 3: Verify Deployment

### 3.1 Check Logs

In Railway dashboard:
1. Click on your bot service
2. Go to **"Deployments"** tab
3. Click latest deployment → **"View Logs"**

Look for:
```
✅ Database and Price Tracker modules loaded
✅ Database and Price Tracker initialized
✅ Database schema initialized
```

### 3.2 Test Analysis

1. Open Telegram
2. Send `/analyze BTCUSDT`
3. Wait for AI response
4. Check logs for:
   ```
   ✅ Saved analysis to database: btcusdt_20251110_123456_789
   ✅ Started price tracking for btcusdt_20251110_123456_789
   ```

### 3.3 Verify Database

In Railway PostgreSQL service:
1. Go to **"Data"** tab
2. Run query:
   ```sql
   SELECT COUNT(*) FROM analysis_history;
   ```
3. Should return: `1` (or more if you ran multiple analyses)

---

## 🎯 Step 4: How It Works

### 4.1 Analysis Flow

```
User sends /analyze BTCUSDT
         ↓
Bot fetches market data
         ↓
Check historical performance (if exists)
         ↓
Enhanced AI prompt with history
         ↓
Gemini generates analysis
         ↓
Save full JSON to PostgreSQL
         ↓
Start WebSocket price tracking
         ↓
Monitor TP/SL for 7 days
         ↓
Auto-save result when hit
         ↓
Next analysis learns from this
```

### 4.2 Price Tracking

- **Automatic:** No notifications, silent tracking
- **WebSocket:** Real-time price monitoring via Binance
- **Candle Close:** Only checks on 1m candle close (reliable)
- **Duration:** 7 days max tracking per analysis
- **Result:** Saves PnL, duration, exit reason to DB

### 4.3 AI Learning

**Example: BTCUSDT Analysis**

First analysis:
```
No historical data → Standard analysis
```

After 5 analyses (3 wins, 2 losses):
```
Historical Performance:
- Total: 5 analyses
- Win Rate: 60%
- Winning Patterns: RSI 25-35, VP DISCOUNT
- Losing Patterns: RSI 70-80, VP PREMIUM

Current Setup: RSI 28, VP DISCOUNT
✅ STRONG SIGNAL: Matches previous wins (85% similarity)
→ AI increases confidence to 90%
```

---

## 🔧 Troubleshooting

### Database Connection Failed

**Error:**
```
psycopg2.OperationalError: could not connect to server
```

**Solution:**
1. Check `DATABASE_URL` is correctly set in bot variables
2. Verify PostgreSQL service is running (green status)
3. Check database is in same Railway project

### Module Import Error

**Error:**
```
ImportError: No module named 'psycopg2'
```

**Solution:**
1. Check `requirements.txt` includes:
   ```
   psycopg2-binary>=2.9.0
   websockets>=12.0
   ```
2. Force redeploy:
   - Railway dashboard → Bot service → **"Redeploy"**

### WebSocket Connection Failed

**Error:**
```
ConnectionClosed: WebSocket connection closed
```

**Solution:**
- This is normal if market closed or symbol delisted
- Tracker will auto-reconnect
- Check Binance symbol still exists

### No Historical Data Showing

**Issue:** AI still says "No historical data"

**Possible Causes:**
1. **First analysis:** Need at least 1 completed analysis (wait 7 days or until TP/SL hit)
2. **Different user_id:** History is per-user (check user_id in logs)
3. **Database empty:** Check `analysis_history` table has records

**Check:**
```sql
SELECT symbol, status, tracking_result 
FROM analysis_history 
WHERE user_id = YOUR_USER_ID;
```

---

## 📊 Database Schema

### analysis_history Table

| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL | Primary key |
| analysis_id | VARCHAR(100) | Unique ID (symbol_timestamp_user) |
| user_id | BIGINT | Telegram user ID |
| symbol | VARCHAR(20) | Trading pair (BTCUSDT) |
| timeframe | VARCHAR(10) | Chart timeframe (1h, 4h) |
| created_at | TIMESTAMP | Analysis time |
| expires_at | TIMESTAMP | Auto-delete after 7 days |
| ai_full_response | JSONB | Complete AI JSON |
| market_snapshot | JSONB | Indicators at analysis time |
| tracking_result | JSONB | TP/SL hit result |
| status | VARCHAR(20) | PENDING_TRACKING/COMPLETED |

### Indexes

- `idx_user_symbol`: Fast lookup by user + symbol
- `idx_symbol_created`: Fast symbol history queries
- `idx_expires`: Fast cleanup of old records

---

## 🎨 Future Enhancements (Pending)

1. **History Tab UI** (WebApp)
   - View all past analyses
   - Win rate charts (Chart.js)
   - Filters by symbol/timeframe/result

2. **Flask API Endpoints**
   ```python
   GET /api/history?user_id=123&symbol=BTCUSDT
   GET /api/stats?user_id=123
   ```

3. **Review Feature**
   - Manual review of AI analysis
   - Flag good/bad predictions
   - Improve learning accuracy

4. **Pattern Visualization**
   - Heatmaps of winning RSI/MFI zones
   - Volume Profile success rates
   - Best entry timing patterns

---

## 📞 Support

If you encounter issues:

1. **Check Railway Logs** (most issues visible here)
2. **Verify Environment Variables** (all required vars set?)
3. **Check PostgreSQL Status** (green = running)
4. **Test Locally** (run with local PostgreSQL first)

---

## 🎉 Success Indicators

You'll know it's working when:

✅ No import errors in logs
✅ `DATABASE_URL` connects successfully
✅ Schema created automatically
✅ First analysis saved to DB
✅ Price tracking started
✅ Second analysis shows historical context in logs
✅ TP/SL hit result saved after 7 days (or when hit)

---

## 📝 Notes

- **7-day retention:** Old analyses auto-delete after 7 days
- **No notifications:** Price tracking is silent
- **Per-user learning:** Each user has separate history
- **Symbol-specific:** AI learns patterns per trading pair
- **Graceful degradation:** Bot works even if DB fails (just no learning)

---

**Version:** 1.0  
**Date:** November 10, 2025  
**Status:** Production Ready ✅
