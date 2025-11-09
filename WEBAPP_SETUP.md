# 🚀 QUICK SETUP - TELEGRAM WEBAPP

## ✅ Setup trên Railway (5 phút)

### Bước 1: Add Environment Variable

Trong Railway Dashboard:
```
Settings → Variables → Add Variable:

Name: WEBAPP_URL
Value: https://YOUR-APP-NAME.up.railway.app/webapp/chart.html
```

**Lưu ý:** Thay `YOUR-APP-NAME` bằng tên app thực tế của bạn trên Railway.

### Bước 2: Verify Procfile

File `Procfile` đã update:
```
web: python webapp/app.py
worker: bash start.sh
```

Railway sẽ tự động chạy cả 2 processes.

### Bước 3: Deploy

Railway auto-deploy khi push code lên GitHub. Đợi ~2-3 phút.

### Bước 4: Test

1. **Check Health:**
   ```
   https://YOUR-APP-NAME.up.railway.app/health
   ```
   
   Expected response:
   ```json
   {
     "status": "ok",
     "binance_connected": true,
     "timestamp": "2025-11-09T..."
   }
   ```

2. **Test API:**
   ```
   https://YOUR-APP-NAME.up.railway.app/api/chart?symbol=BTCUSDT&timeframe=1h
   ```
   
   Should return JSON with candles data.

3. **Test WebApp:**
   ```
   https://YOUR-APP-NAME.up.railway.app/webapp/chart.html?symbol=BTCUSDT
   ```
   
   Should show interactive chart in browser.

4. **Test in Telegram:**
   - Send `/analyze BTCUSDT` to bot
   - Click **📊 Chart** button
   - Click **📊 Live Chart (in Telegram)**
   - Chart should open INSIDE Telegram app! 🎉

---

## 🔧 Troubleshooting

### Problem: WebApp button not showing

**Solution:**
1. Check WEBAPP_URL is set correctly in Railway
2. Restart bot: `/restart` command
3. Check Railway logs for errors

### Problem: API returns 404

**Solution:**
1. Verify `webapp/` folder deployed
2. Check Railway logs: `View Logs`
3. Ensure Flask is running: Look for "Running on http://0.0.0.0:8080"

### Problem: Chart shows "Loading..." forever

**Solution:**
1. Check API endpoint in browser first
2. Open browser DevTools (F12) → Console for errors
3. Verify CORS is enabled (check Network tab)

### Problem: "Binance client not initialized"

**Solution:**
1. Check BINANCE_API_KEY and BINANCE_API_SECRET in Railway
2. Restart deployment
3. Check health endpoint

---

## 📱 How to Use

### For Users:

1. Get signal alert from bot
2. Click **📊 Chart** button
3. See static preview + buttons:
   - **📊 Live Chart (in Telegram)** ← Click this!
   - Opens interactive chart IN Telegram
   - No external browser needed

### Chart Features:

- **Zoom**: Pinch gesture (mobile) or scroll (desktop)
- **Pan**: Swipe left/right to see history
- **Crosshair**: Tap & hold to see exact values
- **Timeframes**: Tap 5M/1H/4H/1D to switch
- **Auto-refresh**: Updates every 30 seconds

---

## 🎯 Verify Deployment

### Check Railway Dashboard:

1. **Deployments** → Should see latest commit
2. **Logs** → Should see:
   ```
   ✅ Binance client initialized
   Running on http://0.0.0.0:8080
   ```
3. **Metrics** → Should show 2 processes running

### Check Telegram Bot:

```bash
# Send to bot:
/analyze BTCUSDT

# Expected:
- Signal alert appears
- 📊 Chart button visible
- Click it → Static chart + buttons
- 📊 Live Chart (in Telegram) button appears
- Click it → WebApp opens IN Telegram! ✅
```

---

## 🎉 Success Indicators

✅ Railway shows "Deployed successfully"
✅ Health endpoint returns OK
✅ API endpoint returns chart data
✅ WebApp loads in browser
✅ Telegram bot sends chart with buttons
✅ **WebApp button opens chart IN Telegram!** 🚀

---

## 📊 Expected Behavior

### Before (Static Only):
```
Click Chart → Static PNG sent → Done
```

### After (Hybrid + WebApp):
```
Click Chart → Static PNG sent
              ↓
            Buttons appear:
            - 📊 Live Chart (in Telegram) ← NEW!
            - 📈 TradingView 1H (browser)
            - 📈 TradingView 4H (browser)
            - 📈 TradingView 1D (browser)
            - 🔄 Refresh
            - 🤖 AI Phân Tích
              ↓
         Click "Live Chart"
              ↓
         Opens IN Telegram!
         - Interactive chart
         - Touch gestures
         - Real-time updates
         - No browser switch!
```

---

## 💡 Tips

1. **Mobile First**: WebApp optimized for mobile, test on phone
2. **Telegram Version**: Need Telegram 6.0+ for WebApp support
3. **Internet**: WebApp needs internet (fetches live data)
4. **Performance**: Chart loads ~1-2 seconds, very smooth
5. **Updates**: Any changes to `webapp/` → push → auto-deploy!

---

## 🔗 Important URLs

Replace `YOUR-APP-NAME` with actual Railway app name:

- **WebApp**: `https://YOUR-APP-NAME.up.railway.app/webapp/chart.html`
- **API**: `https://YOUR-APP-NAME.up.railway.app/api/chart`
- **Health**: `https://YOUR-APP-NAME.up.railway.app/health`

Set `WEBAPP_URL` to first URL in Railway environment variables.

---

## ✅ Final Check

```bash
# 1. Environment variable set? 
WEBAPP_URL=https://...

# 2. Railway deployed?
git push → Railway auto-deploys

# 3. Health check OK?
curl https://YOUR-APP.railway.app/health

# 4. API works?
curl https://YOUR-APP.railway.app/api/chart?symbol=BTCUSDT&timeframe=1h

# 5. Bot sends buttons?
/analyze BTCUSDT → Chart button → Buttons appear

# 6. WebApp opens in Telegram?
Click "📊 Live Chart" → Opens IN Telegram! ✅
```

---

## 🎊 You're Done!

Bot now has **professional live chart** that opens **INSIDE Telegram**!

Best user experience, no external browser, seamless navigation! 🚀

Need help? Check `TELEGRAM_WEBAPP_GUIDE.md` for detailed docs!
