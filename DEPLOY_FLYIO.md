# 🚀 Deploy Bot lên Fly.io - Hướng dẫn chi tiết

## ✅ Tại sao chọn Fly.io?

- ✅ **FREE FOREVER** - 3 VMs shared-cpu-1x miễn phí
- ✅ **Singapore Region** - IP châu Á, Binance cho phép
- ✅ **Chạy 24/7** - Không sleep, always-on
- ✅ **Easy deployment** - CLI đơn giản
- ✅ **Auto-restart** - Tự động restart nếu crash
- ✅ **Good performance** - SSD storage, fast network

---

## 📋 BƯỚC 1: Cài đặt Fly.io CLI

### Windows PowerShell:

```powershell
# Mở PowerShell as Administrator
iwr https://fly.io/install.ps1 -useb | iex
```

**Sau khi cài xong, ĐÓNG và MỞ LẠI PowerShell mới!**

### Kiểm tra cài đặt:

```powershell
fly version
# Should show: flyctl v0.x.x
```

---

## 📋 BƯỚC 2: Tạo tài khoản Fly.io

### Login:

```powershell
fly auth login
```

**Sẽ mở browser:**
1. Nếu chưa có account → Đăng ký (miễn phí)
2. Nếu có rồi → Login
3. Authorize CLI

**Lưu ý:** Fly.io yêu cầu **thẻ credit card** để verify (nhưng KHÔNG charge nếu dùng free tier)

---

## 📋 BƯỚC 3: Khởi tạo Fly app

### Di chuyển vào thư mục bot:

```powershell
cd "H:\BOT UPGRADE"
```

### Launch app với Singapore region:

```powershell
fly launch --name rsi-mfi-bot --region sin --no-deploy
```

**Các câu hỏi:**
- Would you like to copy its configuration to the new app? → **No**
- Would you like to set up a Postgresql database? → **No**
- Would you like to set up an Upstash Redis database? → **No**
- Would you like to deploy now? → **No** (chúng ta set secrets trước)

**Kết quả:** Tạo file `fly.toml` trong thư mục

---

## 📋 BƯỚC 4: Configure fly.toml

File `fly.toml` đã được tạo, chúng ta cần chỉnh sửa:

### Nội dung fly.toml:

```toml
app = "rsi-mfi-bot"
primary_region = "sin"

[build]

[env]
  # No public env vars here, use secrets instead

[http_service]
  internal_port = 8080
  force_https = true
  auto_stop_machines = false
  auto_start_machines = false
  min_machines_running = 1

[[vm]]
  cpu_kind = "shared"
  cpus = 1
  memory_mb = 256
```

**Lưu ý:** 
- `auto_stop_machines = false` → Bot chạy liên tục, không sleep
- `min_machines_running = 1` → Luôn có 1 VM running
- `memory_mb = 256` → 256MB RAM (đủ cho bot)

---

## 📋 BƯỚC 5: Set Environment Variables (Secrets)

### Set các API keys:

```powershell
# Binance API Key
fly secrets set BINANCE_API_KEY="v0D4P3dnYFJdrejkJ85mcFlus0aUIG3s8O7bIhT4Xdu6V8wjcKHipVE5U4MHxyv6"

# Binance API Secret
fly secrets set BINANCE_API_SECRET="TGn5TQnwpIRcSFo2yrSjzgwzw9xJwmZqnuIicAYWfL82QQDj33D6PumN0cDGTmtn"

# Telegram Bot Token
fly secrets set TELEGRAM_BOT_TOKEN="5833768074:AAHSfnbTzx-pU5jmikeIwtPfO-_kAneWlXE"

# Telegram Chat ID
fly secrets set TELEGRAM_CHAT_ID="-1002301937119"
```

**Kiểm tra secrets:**

```powershell
fly secrets list
```

---

## 📋 BƯỚC 6: Update config.py (optional)

Fly.io sẽ tự động load secrets, nhưng đảm bảo config.py đọc từ environment variables:

```python
# config.py (đã có sẵn)
import os
from dotenv import load_dotenv

load_dotenv()

BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
```

✅ **Đã OK, không cần sửa!**

---

## 📋 BƯỚC 7: Deploy lên Fly.io

### Deploy:

```powershell
fly deploy
```

**Quá trình:**
1. Building Docker image (2-3 phút)
2. Pushing to Fly.io registry
3. Creating VM in Singapore
4. Starting bot

**Xem logs:**

```powershell
fly logs
```

**Kết quả mong đợi:**
```
🤖 Trading Bot Started!
⏰ Scan interval: 300 seconds
📊 Scanning 348 symbols...
```

---

## 📋 BƯỚC 8: Kiểm tra status

### Check app status:

```powershell
fly status
```

**Output:**
```
Machines
ID              NAME    STATE   REGION  HEALTH  CHECKS  LAST UPDATED
xxxxxxxxx       xxx     started sin     ✓       -       2024-10-15
```

### Check logs real-time:

```powershell
fly logs -f
```

### SSH vào VM (nếu cần debug):

```powershell
fly ssh console
```

---

## 📋 BƯỚC 9: Test bot

Sau khi deploy, bot sẽ:
1. ✅ Tự động chạy trong vòng 1-2 phút
2. ✅ Scan Binance mỗi 5 phút
3. ✅ Gửi signals lên Telegram

**Check Telegram:** Bạn sẽ nhận được messages khi có signals!

---

## 🔧 QUẢN LÝ APP

### Xem danh sách apps:

```powershell
fly apps list
```

### Stop app (tạm dừng):

```powershell
fly apps pause rsi-mfi-bot
```

### Start lại app:

```powershell
fly apps resume rsi-mfi-bot
```

### Scale app (tăng/giảm resources):

```powershell
# Tăng RAM lên 512MB
fly scale memory 512

# Tăng số VMs
fly scale count 2
```

### Xem metrics:

```powershell
fly dashboard
# Mở dashboard trên browser
```

---

## 💰 FREE TIER LIMITS

Fly.io FREE tier includes:

```
✅ 3x shared-cpu-1x VMs (256MB RAM each)
✅ 3GB persistent storage
✅ 160GB outbound bandwidth/month

→ Bot của bạn chỉ dùng 1 VM → VẪN CÒN 2 VMs FREE!
```

**Chi phí dự tính:**
- 1 VM, 256MB RAM: **$0/tháng** (trong free tier)
- Bandwidth ~1GB/tháng: **$0** (free tier 160GB)
- Storage minimal: **$0**

**→ HOÀN TOÀN MIỄN PHÍ!** 🎉

---

## 🔍 TROUBLESHOOTING

### Lỗi: "Error: could not find App"

```powershell
# Re-initialize
fly launch --name rsi-mfi-bot --region sin
```

### Lỗi: Build failed

```powershell
# Check Dockerfile
cat Dockerfile

# Rebuild
fly deploy --local-only
```

### Bot không chạy:

```powershell
# Check logs
fly logs

# SSH vào VM
fly ssh console

# Test Python
python3 main.py
```

### Binance vẫn bị chặn:

```powershell
# Verify region
fly status
# Phải là "sin" (Singapore)

# Nếu không phải:
fly regions set sin
fly deploy
```

### Out of memory:

```powershell
# Tăng RAM lên 512MB
fly scale memory 512
```

---

## 📊 REGIONS AVAILABLE

Fly.io có nhiều regions châu Á:

```bash
sin - Singapore   ✅ RECOMMENDED
hkg - Hong Kong   ✅ Good
nrt - Tokyo       ✅ Good
syd - Sydney      ⚠️  Australia (xa hơn)
```

**Chọn region gần Binance servers nhất = Singapore**

### Thay đổi region:

```powershell
fly regions set sin
fly deploy
```

---

## 🔄 UPDATE CODE

Khi bạn sửa code local:

```powershell
# 1. Sửa file (ví dụ: config.py)

# 2. Deploy lại
fly deploy

# 3. Check logs
fly logs -f
```

**Fly.io sẽ:**
- Build Docker image mới
- Replace VM cũ
- Zero downtime deployment

---

## 📱 MONITORING

### Setup notifications:

1. Vào https://fly.io/dashboard
2. Select app `rsi-mfi-bot`
3. Settings → Alerts
4. Add email/webhook cho failures

### Health checks:

Thêm vào `fly.toml`:

```toml
[[services]]
  internal_port = 8080
  protocol = "tcp"

  [[services.tcp_checks]]
    interval = 60000
    timeout = 5000
```

---

## 🎯 BEST PRACTICES

### 1. Monitoring logs:

```powershell
# Real-time logs
fly logs -f

# Last 100 lines
fly logs -n 100
```

### 2. Regular updates:

```powershell
# Pull latest code
git pull

# Deploy
fly deploy
```

### 3. Backup configuration:

```powershell
# Export secrets (manual backup)
fly secrets list > secrets_backup.txt
```

### 4. Test local trước:

```powershell
# Test local
python main.py

# Nếu OK → Deploy
fly deploy
```

---

## 🆘 SUPPORT

### Fly.io Community:

- Forum: https://community.fly.io
- Docs: https://fly.io/docs
- Discord: https://fly.io/discord

### Common issues:

**Q: App bị sleep?**
A: Check `auto_stop_machines = false` trong fly.toml

**Q: Binance vẫn block?**
A: Verify `fly status` → region phải là `sin`

**Q: Out of free tier?**
A: Check `fly dashboard` → Usage

---

## 🎉 HOÀN TẤT!

Bot của bạn giờ đang chạy trên Fly.io:

- ✅ **FREE** - Không tốn tiền
- ✅ **Singapore** - IP châu Á
- ✅ **24/7** - Always running
- ✅ **Auto-restart** - Tự động khởi động lại nếu crash

### Next steps:

1. ✅ Monitor Telegram để nhận signals
2. ✅ Check logs định kỳ: `fly logs`
3. ✅ Adjust config nếu cần (RSI/MFI thresholds)

---

## 📞 CẦN GIÚP?

Nếu gặp vấn đề, cho tôi biết:

```powershell
# Chạy lệnh này và gửi output cho tôi:
fly status
fly logs -n 50
```

**Happy trading on Fly.io! 🚀📊💰**
