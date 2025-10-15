# 🚀 Deploy Bot lên Railway.app - Hướng dẫn chi tiết

## ✅ Tại sao chọn Railway.app?

- ✅ **$5 FREE credit** - Không cần thẻ credit card
- ✅ **DỄ NHẤT** - Git push to deploy
- ✅ **Chạy 24/7** - Always-on
- ✅ **Environment variables** - Easy setup
- ✅ **Logs real-time** - Monitor dễ dàng
- ✅ **Auto-deploy** - Mỗi khi push code

---

## 📋 BƯỚC 1: Chuẩn bị GitHub Repository

### Option A: Tạo repo mới trên GitHub

1. Vào https://github.com/new
2. Tạo repository:
   - Name: `rsi-mfi-trading-bot`
   - Private hoặc Public (tùy bạn)
   - Không init với README (đã có code)
3. Create repository

### Option B: Nếu đã có repo

Bỏ qua bước này, dùng repo hiện tại.

---

## 📋 BƯỚC 2: Push code lên GitHub

### Init Git (nếu chưa có):

```powershell
cd "H:\BOT UPGRADE"

# Init git
git init

# Add remote (thay YOUR_USERNAME bằng username GitHub của bạn)
git remote add origin https://github.com/YOUR_USERNAME/rsi-mfi-trading-bot.git
```

### Tạo .gitignore để không push API keys:

```powershell
# File .gitignore
.env
.venv/
venv/
__pycache__/
*.pyc
*.log
.vercel/
```

### Add và commit:

```powershell
git add .
git commit -m "Initial commit for Railway deployment"
git branch -M main
git push -u origin main
```

**⚠️ LƯU Ý:** File `.env` sẽ KHÔNG được push (trong .gitignore) để bảo vệ API keys!

---

## 📋 BƯỚC 3: Deploy trên Railway

### 1. Đăng ký Railway:

- Vào: https://railway.app
- Click **"Start a New Project"**
- Login với **GitHub**

### 2. Tạo project mới:

- Click **"Deploy from GitHub repo"**
- Authorize Railway access to GitHub
- Chọn repository `rsi-mfi-trading-bot`

### 3. Configure deployment:

Railway sẽ tự động:
- ✅ Detect Python
- ✅ Đọc `Procfile` (worker: python main.py)
- ✅ Đọc `runtime.txt` (python-3.9)
- ✅ Install dependencies từ `requirements.txt`

---

## 📋 BƯỚC 4: Thêm Environment Variables

### Trong Railway Dashboard:

1. Click vào project vừa tạo
2. Click tab **"Variables"**
3. Thêm các biến:

```
BINANCE_API_KEY = v0D4P3dnYFJdrejkJ85mcFlus0aUIG3s8O7bIhT4Xdu6V8wjcKHipVE5U4MHxyv6
BINANCE_API_SECRET = TGn5TQnwpIRcSFo2yrSjzgwzw9xJwmZqnuIicAYWfL82QQDj33D6PumN0cDGTmtn
TELEGRAM_BOT_TOKEN = 5833768074:AAHSfnbTzx-pU5jmikeIwtPfO-_kAneWlXE
TELEGRAM_CHAT_ID = -1002301937119
```

4. Click **"Add"** cho mỗi biến

---

## 📋 BƯỚC 5: Deploy!

Railway sẽ tự động deploy sau khi thêm variables:

1. Xem tab **"Deployments"**
2. Theo dõi build process
3. Chờ status: **"Success"** ✅

**Build time:** ~2-3 phút

---

## 📋 BƯỚC 6: Kiểm tra Logs

### Xem logs real-time:

1. Click tab **"Logs"**
2. Xem output:

```
🤖 Trading Bot Started!
⏰ Scan interval: 300 seconds
📊 Scanning 348 symbols...
```

### Expected output:

```
[12:00:00] 🔍 Scanning market...
[12:00:05] ✅ Found 15 signals
[12:00:06] 📱 Sent to Telegram
```

---

## 🔧 QUẢN LÝ APP

### Stop/Start app:

1. Vào Railway Dashboard
2. Click project
3. Settings → **Pause Service** hoặc **Resume Service**

### Restart app:

1. Deployments tab
2. Click **"Redeploy"**

### Update code:

```powershell
# Sửa code local
# ...

# Commit và push
git add .
git commit -m "Update code"
git push

# Railway tự động deploy lại! 🚀
```

---

## 💰 PRICING & USAGE

### Free Tier:

```
✅ $5 credit miễn phí
✅ ~500 hours runtime (~20 ngày nếu chạy 24/7)
✅ 100GB egress
✅ Shared resources
```

**Chi phí thực tế cho bot này:**
- ~$0.01-0.02/hour = ~$7-15/tháng
- **$5 credit → chạy free ~1 tuần**

**Sau khi hết credit:**
- Add payment method
- Pay-as-you-go: ~$5-10/tháng

### Check usage:

1. Dashboard → **"Usage"**
2. Xem credit remaining
3. Xem estimated monthly cost

---

## 🔍 TROUBLESHOOTING

### Lỗi: "Build failed"

**Kiểm tra:**
```powershell
# Xem requirements.txt có đúng không
cat requirements.txt

# Test local
pip install -r requirements.txt
python main.py
```

### Lỗi: "Worker crashed"

**Check logs:**
1. Railway Logs tab
2. Tìm error message
3. Fix code và push lại

**Common issues:**
- Missing environment variables
- Wrong Python version
- Dependencies conflict

### Bot không gửi Telegram:

**Verify:**
1. Environment variables đã set đúng chưa
2. Check logs có lỗi API không
3. Test Telegram token:
```python
import telebot
bot = telebot.TeleBot("YOUR_TOKEN")
print(bot.get_me())
```

### Binance API bị chặn:

**Railway servers location:**
- US West (default)
- Có thể bị Binance chặn

**Giải pháp:**
1. Contact Railway support để request Asia region
2. Hoặc dùng Fly.io (có Singapore)
3. Hoặc chạy LOCAL

---

## 🌏 REGION SELECTION

⚠️ **Railway không cho chọn region trong free tier**

Servers mặc định: **US West**

**Nếu Binance chặn:**
1. Upgrade to Pro plan ($20/tháng) → Chọn region
2. Hoặc dùng platform khác (Fly.io Singapore)

---

## 📊 MONITORING

### View metrics:

1. Railway Dashboard
2. Click project
3. **"Metrics"** tab:
   - CPU usage
   - Memory usage
   - Network traffic

### Setup alerts:

Railway Pro plan có alerts, Free tier không có.

**Workaround:**
- Monitor logs manually
- Bot tự gửi Telegram (đó là alert rồi!)

---

## 🔄 AUTO-DEPLOY

Railway tự động deploy khi:

```
git push → Railway detect changes → Auto rebuild → Auto deploy
```

**Disable auto-deploy:**
1. Settings
2. Uncheck **"Auto Deploy"**

---

## 🎯 BEST PRACTICES

### 1. Separate branches:

```powershell
# Development branch
git checkout -b dev
# ... make changes
git push origin dev

# Production branch (main)
git checkout main
git merge dev
git push origin main  # → Triggers Railway deploy
```

### 2. Environment-specific configs:

```python
# config.py
import os

ENV = os.getenv("ENVIRONMENT", "production")

if ENV == "development":
    SCAN_INTERVAL = 60  # 1 minute for testing
else:
    SCAN_INTERVAL = 300  # 5 minutes for production
```

### 3. Health checks:

```python
# Add to main.py
import time
last_scan_time = time.time()

def scan_market():
    global last_scan_time
    # ... scanning logic
    last_scan_time = time.time()
    
# Monitor: nếu last_scan_time > 10 phút → có vấn đề
```

---

## 🆘 SUPPORT

### Railway Community:

- Discord: https://discord.gg/railway
- Docs: https://docs.railway.app
- Help: https://railway.app/help

### Common Questions:

**Q: Làm sao biết bot đang chạy?**
A: Check Telegram, sẽ nhận messages định kỳ

**Q: Credit hết thì sao?**
A: Add payment method, ~$5-10/tháng

**Q: Có thể chọn region không?**
A: Free tier không, Pro plan ($20) có

---

## 📝 FILES ĐÃ TẠO

```
H:\BOT UPGRADE\
├── Procfile          ← Railway process definition
├── runtime.txt       ← Python version
├── requirements.txt  ← Dependencies (đã có)
├── .gitignore        ← Files to ignore
└── main.py           ← Bot code
```

**Procfile:**
```
worker: python main.py
```

**runtime.txt:**
```
python-3.9
```

---

## 🎉 HOÀN TẤT!

Sau khi deploy, bot sẽ:

- ✅ **Chạy 24/7** trên Railway
- ✅ **Auto-restart** nếu crash
- ✅ **Auto-deploy** khi push code
- ✅ **Gửi signals** lên Telegram

### Next Steps:

1. ✅ Monitor Telegram messages
2. ✅ Check Railway logs định kỳ
3. ✅ Track credit usage
4. ✅ Adjust config nếu cần

---

## ⚠️ LƯU Ý QUAN TRỌNG

### Về IP location:

Railway servers ở **US West** → **CÓ THỂ** bị Binance chặn!

**Nếu bị chặn:**
- Logs sẽ hiện: `Service unavailable from a restricted location`
- **Giải pháp:**
  1. Upgrade Railway Pro → Chọn region khác
  2. Dùng Fly.io (Singapore, FREE)
  3. Chạy LOCAL (FREE, IP Việt Nam)

---

## 📞 CẦN GIÚP?

Nếu gặp vấn đề, cho tôi biết:

1. Railway deployment logs
2. Error messages
3. Bot logs

**Happy trading on Railway! 🚀📊💰**
