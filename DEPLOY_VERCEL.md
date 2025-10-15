# Deploy RSI + MFI Trading Bot to Vercel

Hướng dẫn deploy bot lên Vercel với Cron Jobs (chạy tự động mỗi 5 phút)

## 📋 Yêu cầu

- Tài khoản Vercel (miễn phí): https://vercel.com
- Vercel CLI đã cài đặt
- API Keys đã cấu hình trong `.env`

## 🚀 Cài đặt Vercel CLI

### Windows PowerShell:
```powershell
npm install -g vercel
```

Hoặc dùng pnpm:
```powershell
pnpm install -g vercel
```

## 📦 Chuẩn bị Deploy

### 1. Đăng nhập Vercel
```powershell
vercel login
```

### 2. Thêm Environment Variables vào Vercel

```powershell
vercel env add BINANCE_API_KEY
# Nhập: v0D4P3dnYFJdrejkJ85mcFlus0aUIG3s8O7bIhT4Xdu6V8wjcKHipVE5U4MHxyv6

vercel env add BINANCE_API_SECRET
# Nhập: TGn5TQnwpIRcSFo2yrSjzgwzw9xJwmZqnuIicAYWfL82QQDj33D6PumN0cDGTmtn

vercel env add TELEGRAM_BOT_TOKEN
# Nhập: 5833768074:AAHSfnbTzx-pU5jmikeIwtPfO-_kAneWlXE

vercel env add TELEGRAM_CHAT_ID
# Nhập: -1002301937119
```

Hoặc thêm trực tiếp trên Vercel Dashboard:
1. Vào project → Settings → Environment Variables
2. Thêm các biến trên cho Production, Preview, và Development

## 🌐 Deploy lên Vercel

### Deploy lần đầu:
```powershell
vercel
```

Trả lời các câu hỏi:
- Set up and deploy? → Yes
- Which scope? → Chọn account của bạn
- Link to existing project? → No
- Project name? → rsi-mfi-trading-bot (hoặc tên bạn muốn)
- Directory? → ./ (Enter)
- Override settings? → No

### Deploy Production:
```powershell
vercel --prod
```

## ⚙️ Cấu hình Cron Jobs

**LƯU Ý QUAN TRỌNG:** Vercel Cron Jobs chỉ có trên **Pro Plan ($20/tháng)**.

### Nếu dùng Free Plan:
Bạn có 2 lựa chọn:

#### Option 1: Dùng Cron-Job.org (Miễn phí)
1. Đăng ký tại: https://cron-job.org
2. Tạo cron job mới:
   - URL: `https://your-vercel-app.vercel.app/api/scan`
   - Schedule: Every 5 minutes (*/5 * * * *)
   - Method: GET

#### Option 2: Dùng GitHub Actions (Miễn phí)
Tạo file `.github/workflows/scan.yml`:
```yaml
name: Market Scan

on:
  schedule:
    - cron: '*/5 * * * *'  # Every 5 minutes
  workflow_dispatch:  # Manual trigger

jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - name: Trigger Vercel Function
        run: |
          curl https://your-vercel-app.vercel.app/api/scan
```

## 🔧 Kiểm tra Deploy

### 1. Health Check
```powershell
curl https://your-vercel-app.vercel.app/
```

### 2. Test Market Scan
```powershell
curl https://your-vercel-app.vercel.app/api/scan
```

### 3. Xem Logs
```powershell
vercel logs
```

## 📊 Cấu trúc Project cho Vercel

```
BOT UPGRADE/
├── api/
│   ├── index.py          # Health check endpoint
│   └── scan.py           # Market scan endpoint (triggered by cron)
├── vercel.json           # Vercel configuration
├── package.json          # Project metadata
├── requirements-vercel.txt # Python dependencies
├── config.py             # Configuration (reads from env)
├── binance_client.py     # Binance API client
├── telegram_bot.py       # Telegram bot
├── indicators.py         # RSI/MFI calculations
├── chart_generator.py    # Chart creation
└── .env                  # Local env (not deployed)
```

## ⚡ Giới hạn Vercel

### Free (Hobby) Plan:
- ✅ 100 GB bandwidth/month
- ✅ Unlimited requests
- ⚠️ **10 giây timeout** (có thể không đủ cho 348 coins)
- ❌ **Không có Cron Jobs** (dùng external service)

### Pro Plan ($20/month):
- ✅ 1 TB bandwidth/month
- ✅ **60 giây timeout**
- ✅ **Cron Jobs** (tích hợp sẵn)
- ✅ Better performance

## 🎯 Tối ưu cho Free Plan

Nếu dùng Free Plan, cập nhật `api/scan.py`:

```python
# Giảm số lượng coins để tránh timeout
for i, symbol_info in enumerate(symbols[:20]):  # Chỉ scan 20 coins
```

Hoặc chia thành nhiều request:
- Scan 1: Top 20 coins theo volume
- Scan 2: Coins tiếp theo
- ...

## 🔄 Alternative: Deploy lên Railway.app (Free Plan có Cron)

Nếu bạn muốn Cron miễn phí, xem xét:
- **Railway.app** - $5/month credit miễn phí
- **Render.com** - Free plan với cron jobs
- **Fly.io** - Free tier tốt

## 📝 Troubleshooting

### Lỗi: Function timeout
→ Giảm số coins scan hoặc upgrade Pro plan

### Lỗi: Module not found
→ Kiểm tra `requirements-vercel.txt`

### Lỗi: Environment variables not found
→ Kiểm tra env vars trong Vercel dashboard

### Cron không chạy
→ Verify bạn đang dùng Pro plan hoặc dùng external cron service

## 🆘 Support

Nếu cần hỗ trợ:
1. Check logs: `vercel logs`
2. Test endpoint: `curl https://your-app.vercel.app/api/scan`
3. Verify env vars trong Vercel dashboard

---

**Chúc bạn deploy thành công! 🚀**
