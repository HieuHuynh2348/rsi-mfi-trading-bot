# ✅ DEPLOY LÊN RAILWAY - HƯỚNG DẪN NHANH

## 🎉 Code đã được push lên GitHub thành công!

**Repository:** https://github.com/HieuHuynh2348/rsi-mfi-trading-bot

---

## 📋 CÁC BƯỚC DEPLOY TRÊN RAILWAY:

### Bước 1: Vào Railway
👉 https://railway.app

### Bước 2: Login với GitHub
- Click **"Login with GitHub"**
- Authorize Railway access

### Bước 3: Tạo Project Mới
1. Click **"New Project"**
2. Chọn **"Deploy from GitHub repo"**
3. Tìm và chọn repo: **"rsi-mfi-trading-bot"**

Railway sẽ tự động:
- ✅ Detect Python project
- ✅ Đọc `Procfile` → `worker: python main.py`
- ✅ Đọc `runtime.txt` → Python 3.9
- ✅ Install dependencies từ `requirements.txt`

### Bước 4: Add Environment Variables

Click vào project → Tab **"Variables"** → Add các biến sau:

```
BINANCE_API_KEY
v0D4P3dnYFJdrejkJ85mcFlus0aUIG3s8O7bIhT4Xdu6V8wjcKHipVE5U4MHxyv6

BINANCE_API_SECRET
TGn5TQnwpIRcSFo2yrSjzgwzw9xJwmZqnuIicAYWfL82QQDj33D6PumN0cDGTmtn

TELEGRAM_BOT_TOKEN
5833768074:AAHSfnbTzx-pU5jmikeIwtPfO-_kAneWlXE

TELEGRAM_CHAT_ID
-1002301937119
```

**Cách add:**
1. Click "Add Variable"
2. Variable name: `BINANCE_API_KEY`
3. Variable value: `v0D4P3dnYFJdrejkJ85mcFlus0aUIG3s8O7bIhT4Xdu6V8wjcKHipVE5U4MHxyv6`
4. Click "Add"
5. Lặp lại cho 3 biến còn lại

### Bước 5: Deploy Tự Động!

Sau khi add variables, Railway sẽ **TỰ ĐỘNG DEPLOY**!

**Theo dõi deployment:**
- Tab **"Deployments"** → Xem build progress
- Tab **"Logs"** → Xem bot output

**Expected logs:**
```
🤖 Trading Bot Started!
⏰ Scan interval: 300 seconds
📊 Scanning 348 symbols on Binance...

[12:00:00] 🔍 Scanning market...
[12:00:05] ✅ Found 15 signals
[12:00:06] 📱 Sent to Telegram
```

---

## 🎯 SAU KHI DEPLOY:

### ✅ Bot sẽ:
- Chạy 24/7 trên Railway
- Scan Binance mỗi 5 phút
- Gửi signals lên Telegram
- Tự động restart nếu crash

### 📱 Check Telegram:
Bạn sẽ nhận messages với format:
```
━━━━━━━━━━━━━━━━━━━━━━
📊 BTCUSDT - BUY Signal

⏱️ Timeframe Analysis:
  5M:  🟢 RSI 25, MFI 20
  1H:  🟢 RSI 35, MFI 30
  3H:  🟢 RSI 40, MFI 35
  1D:  - RSI 55, MFI 50

📈 Consensus: 3/4 🟢🟢🟢
━━━━━━━━━━━━━━━━━━━━━━
```

---

## 💰 CHI PHÍ:

**Free Tier:**
- ✅ **$5 credit miễn phí**
- ✅ ~500 hours (~20 ngày chạy 24/7)
- ✅ Shared resources

**Bot này tiêu thụ:**
- ~$0.01-0.02/hour
- = ~$7-15/tháng

**→ $5 credit = chạy free ~1 tuần!**

**Sau khi hết credit:**
- Add payment method
- Pay $5-10/tháng

---

## 🔧 QUẢN LÝ BOT:

### Xem Logs:
```
Railway Dashboard → Project → Logs tab
```

### Stop/Start:
```
Railway Dashboard → Settings → Pause/Resume Service
```

### Update Code:
```powershell
# 1. Sửa code local
# 2. Commit
git add .
git commit -m "Update code"

# 3. Push
git push

# 4. Railway tự động deploy lại! 🚀
```

---

## ⚠️ LƯU Ý QUAN TRỌNG:

### Về Region/IP:

Railway servers ở **US West** → **CÓ THỂ** bị Binance chặn!

**Nếu thấy lỗi trong logs:**
```
APIError: Service unavailable from a restricted location
```

**Giải pháp:**
1. **Upgrade Railway Pro** ($20/tháng) → Chọn region khác
2. **Dùng Fly.io** (Singapore, FREE) - Đã có Dockerfile sẵn
3. **Chạy LOCAL** (FREE, IP Việt Nam)

---

## 🆘 TROUBLESHOOTING:

### Build failed:
```
Check: Logs → Build logs
Fix: requirements.txt có đúng không
```

### Bot không chạy:
```
Check: Variables đã add đủ chưa
Fix: Re-add environment variables
```

### Không nhận Telegram:
```
Check: TELEGRAM_CHAT_ID đúng chưa (có dấu -)
Test: Bot token còn active không
```

---

## 📞 SUPPORT:

**Railway Community:**
- Discord: https://discord.gg/railway
- Docs: https://docs.railway.app

**Nếu cần help:**
- Screenshot logs
- Error messages
- Cho tôi biết!

---

## 🎊 DONE!

Bot của bạn giờ đang:
- ✅ On GitHub: https://github.com/HieuHuynh2348/rsi-mfi-trading-bot
- 🚀 Ready to deploy on Railway
- 📱 Sẵn sàng gửi signals!

**Next:** Vào Railway.app và deploy theo 5 bước trên! 🚀

---

**Happy Trading! 📊💰🚀**
