# HƯỚNG DẪN DEPLOY LÊN VERCEL - KHÔNG CẦN CLI

## 🚀 Cách 1: Deploy qua Vercel Dashboard (Đơn giản nhất)

### Bước 1: Tạo tài khoản GitHub (nếu chưa có)
1. Vào https://github.com
2. Đăng ký tài khoản miễn phí

### Bước 2: Push code lên GitHub

#### Nếu chưa có Git, tải tại: https://git-scm.com/download/win

Sau đó chạy trong PowerShell:

```powershell
cd "H:\BOT UPGRADE"

# Khởi tạo git
git init

# Thêm tất cả files
git add .

# Commit
git commit -m "Initial commit - RSI MFI Trading Bot"

# Tạo repo trên GitHub rồi kết nối (thay YOUR_USERNAME và YOUR_REPO)
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git branch -M main
git push -u origin main
```

### Bước 3: Deploy từ Vercel

1. **Vào https://vercel.com**
2. **Sign Up** với GitHub
3. **New Project** → **Import Git Repository**
4. Chọn repository vừa tạo
5. **Configure Project:**
   - Framework Preset: `Other`
   - Root Directory: `./`
   - Build Command: (để trống)
   - Output Directory: (để trống)
6. **Environment Variables** - Thêm 4 biến:
   ```
   BINANCE_API_KEY = v0D4P3dnYFJdrejkJ85mcFlus0aUIG3s8O7bIhT4Xdu6V8wjcKHipVE5U4MHxyv6
   BINANCE_API_SECRET = TGn5TQnwpIRcSFo2yrSjzgwzw9xJwmZqnuIicAYWfL82QQDj33D6PumN0cDGTmtn
   TELEGRAM_BOT_TOKEN = 5833768074:AAHSfnbTzx-pU5jmikeIwtPfO-_kAneWlXE
   TELEGRAM_CHAT_ID = -1002301937119
   ```
7. Click **Deploy**

### Bước 4: Setup Cron (Chạy tự động)

**Vì FREE plan không có Cron, dùng Cron-Job.org:**

1. Vào https://cron-job.org/en/
2. Sign Up miễn phí
3. **Create Cronjob:**
   - Title: `RSI MFI Bot Scan`
   - URL: `https://YOUR-APP.vercel.app/api/scan`
   - Schedule: Every 5 minutes → `*/5 * * * *`
   - Enabled: ✅
4. Save

**XONG!** Bot sẽ tự động chạy mỗi 5 phút.

---

## 🚀 Cách 2: Deploy không cần GitHub (Upload trực tiếp)

### Cài Vercel CLI bằng Scoop (Windows Package Manager)

```powershell
# Cài Scoop
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
irm get.scoop.sh | iex

# Cài Node.js
scoop install nodejs

# Cài Vercel
npm install -g vercel

# Deploy
cd "H:\BOT UPGRADE"
vercel login
vercel
```

---

## 🚀 Cách 3: Dùng Python Script tự động (Không cần Vercel)

Nếu không muốn dùng Vercel, chạy bot local 24/7:

```powershell
# Tạo Task Scheduler để tự khởi động
cd "H:\BOT UPGRADE"
& ".venv\Scripts\python.exe" main.py
```

Hoặc dùng `pythonw.exe` để chạy nền:

```powershell
Start-Process -WindowStyle Hidden ".venv\Scripts\pythonw.exe" "main.py"
```

---

## 🎯 Khuyến nghị

**Nếu bạn:**
- ✅ Muốn FREE hoàn toàn → Cách 1 (Vercel + Cron-Job.org)
- ✅ Có máy chạy 24/7 → Cách 3 (Chạy local)
- ✅ Muốn đơn giản → Cách 1

Bạn chọn cách nào? Tôi sẽ hướng dẫn chi tiết!
