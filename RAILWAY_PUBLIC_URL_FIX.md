# 🔧 Fix Railway Public URL for Telegram WebApp

## ❌ Problem
Error: `BUTTON_TYPE_INVALID`

**Nguyên nhân**: Đang dùng internal domain thay vì public domain
- ❌ **Wrong**: `rsi-mfi-trading-bot.railway.internal` (only accessible within Railway)
- ✅ **Correct**: `https://rsi-mfi-trading-bot-production.up.railway.app` (public HTTPS)

## ✅ Solution: Enable Public Networking on Railway

### Step 1: Go to Railway Dashboard
https://railway.app → Select project **rsi-mfi-trading-bot**

### Step 2: Check Public Networking
1. Click on your **web service**
2. Go to **Settings** tab
3. Scroll to **Networking** section
4. Look for **Public Networking**

### Step 3: Generate Public Domain
If you see "Generate Domain" button:
1. Click **Generate Domain**
2. Railway will create: `https://xxx-production.up.railway.app`
3. Copy this URL

### Step 4: Set Environment Variable
Go to **Variables** tab:
```
WEBAPP_URL=https://your-generated-domain.up.railway.app
```

OR let Railway auto-detect (recommended):
- Railway provides `RAILWAY_PUBLIC_DOMAIN` automatically
- Code already handles this in `telegram_bot.py`

### Step 5: Verify Public Access
Test in browser or curl:
```bash
curl https://rsi-mfi-trading-bot-production.up.railway.app/health
```

Should return:
```json
{
  "status": "ok",
  "binance_connected": true
}
```

## 🎯 Final Check

After Railway redeploys:
1. Send `/analyzer BTCUSDT` in Telegram
2. Should see button: **📊 Live Chart (in Telegram)**
3. Click it → Opens IN Telegram (not browser)

## 📝 Notes

**Internal vs Public Domain:**
- `xxx.railway.internal` = Internal only (services communicate within Railway)
- `xxx.up.railway.app` = Public HTTPS (accessible from anywhere, including Telegram)

**Telegram WebApp Requirements:**
- ✅ Must be HTTPS
- ✅ Must be publicly accessible
- ✅ Must be valid domain (not IP address)
- ❌ Cannot be internal/private URL
