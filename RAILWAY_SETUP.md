# 🚂 Railway Deployment Setup

## ✅ Completed Steps

1. ✅ Code pushed to GitHub
2. ✅ Railway connected to GitHub repo
3. ✅ WebApp URL identified: `https://rsi-mfi-trading-bot-production.up.railway.app`

## 🔧 Required: Set Environment Variable on Railway

### Step 1: Go to Railway Dashboard
Visit: https://railway.app

### Step 2: Select Your Project
Click on: **rsi-mfi-trading-bot**

### Step 3: Go to Variables Tab
1. Click on your service
2. Click **Variables** tab
3. Click **+ New Variable**

### Step 4: Add WEBAPP_URL
```
Name: WEBAPP_URL
Value: https://rsi-mfi-trading-bot-production.up.railway.app
```

Click **Add** button

### Step 5: Redeploy
Railway will automatically redeploy with new variable.

## 🧪 Testing After Deployment

### Check Logs
In Railway dashboard, go to **Deployments** → Click latest deployment → View logs

Look for:
```
✅ Using manual WEBAPP_URL: https://rsi-mfi-trading-bot-production.up.railway.app
```

or
```
✅ Using Railway domain for WebApp: rsi-mfi-trading-bot-production.up.railway.app
```

### Test in Telegram
1. Send: `/analyzer BTCUSDT`
2. You should see **3 buttons**:
   - 🤖 AI Phân Tích
   - 📊 Chart
   - **📊 Live Chart (in Telegram)** ← This is the new WebApp button!
3. Click **Live Chart** → Opens IN Telegram (not browser)

## ⚠️ Alternative: Let Railway Auto-Detect

Instead of setting `WEBAPP_URL`, Railway automatically provides `RAILWAY_PUBLIC_DOMAIN`.

The code already handles this in `telegram_bot.py`:
```python
railway_domain = os.getenv("RAILWAY_PUBLIC_DOMAIN", "")
if railway_domain:
    webapp_url = f"https://{railway_domain}"
```

So you can skip setting WEBAPP_URL and let Railway auto-detect it!

## 🎉 Expected Result

After deployment, when you send `/analyzer BTCUSDT`, you'll see:

```
🤖 AI Phân Tích  |  📊 Chart
📊 Live Chart (in Telegram)
```

Click **Live Chart** → Interactive chart opens IN Telegram! 🎉

## 📝 Notes

- Local `.env` has WEBAPP_URL set for local testing
- Railway will use either RAILWAY_PUBLIC_DOMAIN (auto) or WEBAPP_URL (manual)
- Both work the same way
- Don't commit `.env` to git (already in .gitignore)
