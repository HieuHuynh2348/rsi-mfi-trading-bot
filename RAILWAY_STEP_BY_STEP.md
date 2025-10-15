# 🎯 HƯỚNG DẪN DEPLOY RAILWAY - TỪNG BƯỚC CHI TIẾT (CÓ ẢNH)

## 📺 VIDEO HƯỚNG DẪN (Nếu cần):
https://www.youtube.com/watch?v=railway-deployment (search: "deploy python bot railway")

---

## 🚀 BƯỚC 1: VÀO RAILWAY.APP

### 1.1 Mở browser
- Google Chrome, Edge, hoặc Firefox

### 1.2 Truy cập
```
https://railway.app
```

### 1.3 Trang chủ Railway
Bạn sẽ thấy:
- 🟣 Logo Railway
- Button **"Start a New Project"**
- Button **"Login"** (góc trên phải)

---

## 🔐 BƯỚC 2: LOGIN VỚI GITHUB

### 2.1 Click "Login" (góc trên phải)

### 2.2 Chọn "Login with GitHub"
- Click vào button có logo GitHub
- **KHÔNG** chọn email/password

### 2.3 GitHub sẽ hỏi authorize
Trang GitHub mở ra:
```
Railway by Railway Corp wants to access your HieuHuynh2348 account

Permissions:
✓ Read access to code
✓ Read access to repositories
```

### 2.4 Click "Authorize Railway"
- Button màu xanh lá
- Có thể hỏi password GitHub → Nhập password

### 2.5 Quay lại Railway
Bạn sẽ thấy Railway Dashboard

---

## 📦 BƯỚC 3: TẠO PROJECT MỚI

### 3.1 Tại Railway Dashboard
Bạn sẽ thấy:
```
┌─────────────────────────────┐
│   Welcome to Railway        │
│                             │
│  [+ New Project]            │
│                             │
└─────────────────────────────┘
```

### 3.2 Click "+ New Project"

### 3.3 Chọn deployment method
Popup hiện ra với options:
```
┌─────────────────────────────┐
│  How would you like to      │
│  deploy?                    │
│                             │
│  🔷 Deploy from GitHub repo │ ← CHỌN CÁI NÀY!
│  📝 Deploy from template    │
│  🐳 Empty Project           │
│  📊 Database                │
└─────────────────────────────┘
```

### 3.4 Click "Deploy from GitHub repo"

### 3.5 Configure GitHub Access (nếu lần đầu)
Nếu Railway chưa có quyền access repos:
```
┌─────────────────────────────────┐
│  Configure GitHub App           │
│                                 │
│  Railway needs permission to    │
│  access your repositories       │
│                                 │
│  [Configure GitHub App]         │
└─────────────────────────────────┘
```

Click "Configure GitHub App" → Authorize

### 3.6 Chọn Repository
Danh sách repos hiện ra:
```
┌─────────────────────────────────┐
│  Select a repository            │
│                                 │
│  🔍 Search...                   │
│                                 │
│  📁 rsi-mfi-trading-bot        │ ← CHỌN CÁI NÀY!
│  📁 other-repo                  │
│  📁 another-repo                │
└─────────────────────────────────┘
```

### 3.7 Click "rsi-mfi-trading-bot"

### 3.8 Railway bắt đầu analyze
```
🔍 Analyzing repository...
✅ Detected: Python
✅ Found: Procfile
✅ Found: runtime.txt
✅ Found: requirements.txt
```

### 3.9 Deploy sẽ bắt đầu!
```
Building...
████████████░░░░░░░ 60%
Installing dependencies...
```

**⚠️ SẼ BỊ LỖI** vì chưa có environment variables!

---

## ⚙️ BƯỚC 4: ADD ENVIRONMENT VARIABLES

### 4.1 Vào Project Settings
Sau khi tạo project, bạn sẽ thấy dashboard:
```
┌─────────────────────────────────────┐
│  rsi-mfi-trading-bot               │
│                                     │
│  [Deployments] [Variables] [Settings] │ ← Click "Variables"
│                                     │
└─────────────────────────────────────┘
```

### 4.2 Click tab "Variables"

### 4.3 Add Variable #1: BINANCE_API_KEY
```
┌─────────────────────────────────┐
│  Variables                      │
│                                 │
│  [+ New Variable]               │ ← Click này
└─────────────────────────────────┘
```

Form hiện ra:
```
Variable Name:
┌─────────────────────────────────┐
│ BINANCE_API_KEY                 │ ← Nhập tên
└─────────────────────────────────┘

Variable Value:
┌─────────────────────────────────┐
│ v0D4P3dnYFJdrejkJ85mcFlu...     │ ← Paste value
└─────────────────────────────────┘

[Add]  [Cancel]
```

**Copy-paste value:**
```
v0D4P3dnYFJdrejkJ85mcFlus0aUIG3s8O7bIhT4Xdu6V8wjcKHipVE5U4MHxyv6
```

Click **"Add"**

### 4.4 Add Variable #2: BINANCE_API_SECRET

Click **"+ New Variable"** lại

```
Variable Name: BINANCE_API_SECRET
Variable Value: TGn5TQnwpIRcSFo2yrSjzgwzw9xJwmZqnuIicAYWfL82QQDj33D6PumN0cDGTmtn
```

Click **"Add"**

### 4.5 Add Variable #3: TELEGRAM_BOT_TOKEN

Click **"+ New Variable"** lại

```
Variable Name: TELEGRAM_BOT_TOKEN
Variable Value: 5833768074:AAHSfnbTzx-pU5jmikeIwtPfO-_kAneWlXE
```

Click **"Add"**

### 4.6 Add Variable #4: TELEGRAM_CHAT_ID

Click **"+ New Variable"** lại

```
Variable Name: TELEGRAM_CHAT_ID
Variable Value: -1002301937119
```

**⚠️ LƯU Ý:** Có dấu **trừ (-)** ở đầu!

Click **"Add"**

### 4.7 Kiểm tra lại
Bây giờ bạn sẽ thấy 4 variables:
```
┌─────────────────────────────────────┐
│  Variables                          │
│                                     │
│  BINANCE_API_KEY = v0D4P3d...      │
│  BINANCE_API_SECRET = TGn5TQ...    │
│  TELEGRAM_BOT_TOKEN = 583376...    │
│  TELEGRAM_CHAT_ID = -100230...     │
└─────────────────────────────────────┘
```

---

## 🚀 BƯỚC 5: DEPLOY TỰ ĐỘNG!

### 5.1 Railway tự động redeploy
Sau khi add variables, Railway sẽ:
```
🔄 Triggering new deployment...
🔨 Building...
📦 Installing dependencies...
✅ Deploy successful!
```

### 5.2 Xem Deployments tab
```
┌─────────────────────────────────────┐
│  Deployments                        │
│                                     │
│  ✅ #1 - main - 2 minutes ago       │
│     Status: Success                 │
│     Duration: 1m 23s                │
└─────────────────────────────────────┘
```

### 5.3 Click vào deployment để xem logs

---

## 📊 BƯỚC 6: XEM LOGS

### 6.1 Click tab "Logs"
```
┌─────────────────────────────────────┐
│  Logs                              │
│                                     │
│  [Deploy Logs] [Runtime Logs]      │ ← Click "Runtime Logs"
│                                     │
└─────────────────────────────────────┘
```

### 6.2 Xem Runtime Logs
Bạn sẽ thấy output của bot:
```
2024-10-15 12:00:00 | 🤖 Trading Bot Started!
2024-10-15 12:00:01 | ⏰ Scan interval: 300 seconds (5 minutes)
2024-10-15 12:00:02 | 📊 Scanning 348 symbols on Binance...
2024-10-15 12:00:10 | [12:00:10] 🔍 Scanning market...
2024-10-15 12:00:15 | [12:00:15] ✅ Found 12 signals
2024-10-15 12:00:16 | [12:00:16] 📱 Sent to Telegram
```

### 6.3 Nếu thấy lỗi:
```
ERROR: Service unavailable from a restricted location
```

→ **Binance đã chặn IP Railway (US West)**

**Giải pháp:**
1. Upgrade Railway Pro ($20/tháng) → Chọn region khác
2. Dùng Fly.io (có Singapore, FREE)
3. Chạy LOCAL (IP Việt Nam, FREE)

---

## 📱 BƯỚC 7: CHECK TELEGRAM

### 7.1 Mở Telegram app

### 7.2 Vào chat với bot
Chat ID: `-1002301937119`

### 7.3 Bạn sẽ nhận messages:
```
━━━━━━━━━━━━━━━━━━━━━━
📊 BTCUSDT - BUY Signal

⏱️ Timeframe Analysis:
  5M:  🟢 RSI 25, MFI 20
  1H:  🟢 RSI 30, MFI 25  
  3H:  🟢 RSI 35, MFI 30
  1D:  - RSI 50, MFI 45

📊 RSI Analysis:
  • 5M: 🔴 Oversold (25)
  • 1H: 🔴 Oversold (30)
  
📊 MFI Analysis:
  • 5M: 🔴 Oversold (20)
  • 1H: 🔴 Oversold (25)

📈 Consensus: 3/4 🟢🟢🟢

💰 24H Market Data:
  High: $65,432
  Low: $63,210
  Volume: 12.5B USDT
  Change: +2.34%

⏰ Time: 2024-10-15 12:00:15
━━━━━━━━━━━━━━━━━━━━━━
```

---

## ✅ HOÀN TẤT!

Nếu bạn nhận được messages trên Telegram:
- ✅ **DEPLOY THÀNH CÔNG!**
- ✅ Bot đang chạy 24/7
- ✅ Tự động scan mỗi 5 phút
- ✅ Gửi signals khi phát hiện

---

## 💰 THEO DÕI CREDIT

### Check usage:
1. Railway Dashboard
2. Click icon ⚙️ (Settings) góc trên phải
3. Chọn "Usage"

```
┌─────────────────────────────────────┐
│  Usage this month                   │
│                                     │
│  💵 Credit used: $0.45 / $5.00     │
│  📊 Estimated: $6.50/month         │
│                                     │
│  Days remaining: 25 days            │
└─────────────────────────────────────┘
```

**$5 credit** sẽ hết sau ~1 tuần nếu chạy 24/7

---

## 🔧 QUẢN LÝ BOT

### Pause bot (tạm dừng):
```
Project → Settings → Pause Service
```

### Resume bot:
```
Project → Settings → Resume Service  
```

### Update code:
```powershell
# Trên máy local, sửa code
# Commit và push
git add .
git commit -m "Update"
git push

# Railway tự động deploy lại!
```

---

## 🆘 NẾU GẶP VẤN ĐỀ

### Lỗi: Build failed
```
Check: Deployments → Deploy Logs
Fix: Xem lỗi gì, thường là dependencies
```

### Lỗi: Bot không chạy
```
Check: Variables tab
Fix: Đảm bảo 4 variables đã add đúng
```

### Lỗi: Binance restricted location
```
Check: Logs có dòng "restricted location"
Fix: 
  - Dùng Fly.io (Singapore)
  - Hoặc chạy LOCAL
  - Hoặc upgrade Railway Pro
```

### Không nhận Telegram:
```
Check: TELEGRAM_CHAT_ID có dấu - không
Fix: Phải là -1002301937119 (có dấu trừ)
```

---

## 📞 LIÊN HỆ HỖ TRỢ

Nếu cần giúp:
1. Screenshot Railway Dashboard
2. Screenshot Logs (Deploy + Runtime)
3. Screenshot error (nếu có)
4. Gửi cho tôi!

---

**Chúc bạn deploy thành công! 🎉🚀📊**
