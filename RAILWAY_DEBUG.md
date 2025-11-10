# Railway Deployment Debug Guide

## Current Issue
Bot WebApp button opens JSON health check instead of chart.html

## Root Cause Analysis

### ✅ Code is Correct (Local)
```python
# telegram_bot.py line 255, 316, 399
chart_webapp_url = f"{webapp_url}/webapp/chart.html?symbol={symbol}&timeframe=1h"
```

### ❌ Railway May Be Running Old Code
Git commits show fix was pushed, but Railway needs to redeploy.

## Solution Steps

### 1. Check Railway Deployment Status
```bash
# Go to Railway dashboard
https://railway.app/project/<your-project-id>

# Check "Deployments" tab
# Look for commit: "Fix: Add /webapp/chart.html path to WebApp URLs" (df973f5)
# Status should be: ✅ Success (deployed)
```

### 2. Check Railway Logs
```bash
# In Railway dashboard > Deployments > View Logs

# Look for these log entries when bot starts:
✅ Using Railway domain for WebApp: https://rsi-mfi-trading-bot-production.up.railway.app

# When user clicks button, should see:
📂 Serving file: chart.html from webapp/chart.html
```

### 3. Force Railway Redeploy
If Railway is stuck on old code:

**Option A: Push empty commit**
```bash
git commit --allow-empty -m "Force Railway redeploy"
git push origin main
```

**Option B: Railway Dashboard**
1. Go to Railway project
2. Click "Deployments"
3. Find latest deployment
4. Click "⋮" menu → "Redeploy"

**Option C: Restart Service**
1. Go to Railway project
2. Click service name
3. Click "Settings" tab
4. Scroll to bottom
5. Click "Restart" button

### 4. Test After Redeploy
Wait 2-3 minutes for deployment, then:

```bash
# Test from command line
python test_railway.py

# Test in Telegram
1. Send /btc to bot
2. Click "📊 Live Chart" button
3. Should open chart.html (not JSON)
```

### 5. Debug URL Being Sent
Add this temporary debug code to see what URL bot is sending:

```python
# In telegram_bot.py, find where WebAppInfo is created
# Add logging before creating button:

logger.info(f"🔗 Creating WebApp button with URL: {chart_webapp_url}")
web_app=types.WebAppInfo(url=chart_webapp_url)
```

Then check Railway logs when clicking button.

## Environment Variables Check

Make sure Railway has correct env vars:

```bash
# Required:
TELEGRAM_BOT_TOKEN=<your-token>
BINANCE_API_KEY=<your-key>
BINANCE_API_SECRET=<your-secret>

# Optional (Railway provides RAILWAY_PUBLIC_DOMAIN automatically):
RAILWAY_PUBLIC_DOMAIN=rsi-mfi-trading-bot-production.up.railway.app
WEBAPP_URL=https://rsi-mfi-trading-bot-production.up.railway.app/webapp/chart.html
```

## Expected Behavior

### ✅ Correct Flow
1. User sends `/btc`
2. Bot creates button with URL: `https://rsi-mfi-trading-bot-production.up.railway.app/webapp/chart.html?symbol=BTCUSDT&timeframe=1h`
3. User clicks button
4. Telegram WebApp opens chart.html
5. Chart loads data from Binance API
6. User sees candlestick chart

### ❌ Current (Wrong) Flow
1. User sends `/btc`
2. Bot creates button with URL: `https://rsi-mfi-trading-bot-production.up.railway.app` (missing /webapp/chart.html)
3. User clicks button
4. Telegram WebApp opens root `/`
5. Server returns JSON health check
6. User sees JSON instead of chart

## Quick Fix Command

```bash
# Force redeploy with all fixes
cd "h:\BOT UPGRADE"
git add .
git commit --allow-empty -m "Force redeploy - fix WebApp URL"
git push origin main

# Wait 2-3 minutes
# Then test in Telegram
```

## Files to Check

1. `telegram_bot.py` lines 255, 316, 399 - should have `/webapp/chart.html`
2. `server.py` - should have routes for `/webapp/<path:filename>`
3. `Procfile` - should be `web: python server.py`
4. Railway deployment logs - check if latest commit deployed

## Contact Points

If issue persists after redeploy:
- Check Railway service logs for errors
- Verify Procfile is correct: `web: python server.py`
- Ensure no other services are running on same port
- Check Railway project settings for correct start command
