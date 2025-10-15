# 🚀 Nơi Deploy Bot - Alternatives cho Vercel

## ❌ Tại sao KHÔNG dùng Vercel?

**Vấn đề:**
- Binance chặn IP US/Europe
- Vercel servers chủ yếu ở US/EU
- FREE plan không có cron jobs
- Function timeout 10s (quá ngắn)

**→ CẦN platforms có servers ở Châu Á hoặc cho phép chọn region!**

---

## ✅ CÁC NỀN TẢNG DEPLOY KHÁC:

### 🥇 1. RAILWAY.APP (RECOMMENDED) ⭐⭐⭐⭐⭐

**Website:** https://railway.app

**Ưu điểm:**
- ✅ **$5 FREE credit/tháng** (đủ cho bot nhỏ)
- ✅ **Servers ở nhiều regions** (có thể chọn Asia)
- ✅ **Chạy 24/7** (không phải serverless)
- ✅ **Cron jobs built-in**
- ✅ **Dễ deploy** (Git push)
- ✅ **Environment variables** easy setup
- ✅ **Logs real-time**

**Nhược điểm:**
- ⚠️ FREE credit hết sau ~150 hours runtime
- ⚠️ Sau đó: $5-10/tháng

**Cách deploy:**

#### Bước 1: Chuẩn bị code
```bash
# Tạo Procfile
echo "worker: python main.py" > Procfile

# Tạo runtime.txt (optional)
echo "python-3.9" > runtime.txt

# requirements.txt (đã có)
```

#### Bước 2: Push lên GitHub
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin <your-github-repo>
git push -u origin main
```

#### Bước 3: Deploy trên Railway
1. Vào https://railway.app
2. Login với GitHub
3. New Project → Deploy from GitHub
4. Chọn repo
5. Add environment variables:
   - BINANCE_API_KEY
   - BINANCE_API_SECRET
   - TELEGRAM_BOT_TOKEN
   - TELEGRAM_CHAT_ID
6. Deploy!

**Region selection:**
- Railway tự động chọn region gần nhất
- Có thể request Asia region

---

### 🥈 2. RENDER.COM ⭐⭐⭐⭐

**Website:** https://render.com

**Ưu điểm:**
- ✅ **FREE tier** (750 hours/tháng)
- ✅ **Servers global** (có Singapore)
- ✅ **Chạy 24/7**
- ✅ **Cron jobs** ($1/tháng/job)
- ✅ **Easy deployment**
- ✅ **Auto-deploy** từ Git

**Nhược điểm:**
- ⚠️ FREE tier sleep sau 15 phút inactive
- ⚠️ Cron jobs tốn $1/tháng

**Pricing:**
- FREE: 750h/tháng, sleep sau 15 min
- Starter: $7/tháng, always-on

**Cách deploy:**

#### Bước 1: Tạo render.yaml
```yaml
# render.yaml
services:
  - type: worker
    name: rsi-mfi-bot
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: python main.py
    envVars:
      - key: BINANCE_API_KEY
        sync: false
      - key: BINANCE_API_SECRET
        sync: false
      - key: TELEGRAM_BOT_TOKEN
        sync: false
      - key: TELEGRAM_CHAT_ID
        sync: false
```

#### Bước 2: Push lên GitHub

#### Bước 3: Deploy
1. Vào https://render.com
2. New → Background Worker
3. Connect GitHub repo
4. Select region: **Singapore**
5. Add environment variables
6. Deploy

---

### 🥉 3. FLY.IO ⭐⭐⭐⭐

**Website:** https://fly.io

**Ưu điểm:**
- ✅ **FREE tier generous** (3 VMs shared-cpu-1x)
- ✅ **Servers toàn cầu** (có Singapore, Hong Kong, Tokyo)
- ✅ **Chọn region dễ dàng**
- ✅ **Chạy 24/7**
- ✅ **Docker-based** (flexible)

**Nhược điểm:**
- ⚠️ Cần biết Docker basics
- ⚠️ CLI-based deployment

**Pricing:**
- FREE: 3 shared-cpu VMs, 160GB bandwidth
- Scale: $1.94/VM/tháng

**Cách deploy:**

#### Bước 1: Tạo Dockerfile
```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
```

#### Bước 2: Install Fly CLI
```powershell
# Windows
iwr https://fly.io/install.ps1 -useb | iex
```

#### Bước 3: Deploy
```bash
# Login
fly auth login

# Launch app
fly launch --name rsi-mfi-bot --region sin

# Set secrets
fly secrets set BINANCE_API_KEY="your_key"
fly secrets set BINANCE_API_SECRET="your_secret"
fly secrets set TELEGRAM_BOT_TOKEN="your_token"
fly secrets set TELEGRAM_CHAT_ID="your_chat_id"

# Deploy
fly deploy

# Check status
fly status
```

**Chọn region:**
```bash
# Singapore
fly regions set sin

# Hong Kong
fly regions set hkg

# Tokyo
fly regions set nrt
```

---

### 4. HEROKU ⭐⭐⭐

**Website:** https://heroku.com

**Ưu điểm:**
- ✅ **Phổ biến nhất**
- ✅ **Easy deployment**
- ✅ **Add-ons ecosystem**
- ✅ **Good documentation**

**Nhược điểm:**
- ❌ **KHÔNG CÒN FREE TIER** (từ Nov 2022)
- ⚠️ Eco plan: $5/tháng
- ⚠️ Basic plan: $7/tháng
- ⚠️ Servers chủ yếu US/EU

**Pricing:**
- Eco: $5/tháng (sleep sau 30 min)
- Basic: $7/tháng (always-on)

**Cách deploy:**
```bash
# Install Heroku CLI
# https://devcenter.heroku.com/articles/heroku-cli

# Login
heroku login

# Create app
heroku create rsi-mfi-bot

# Set env vars
heroku config:set BINANCE_API_KEY=xxx
heroku config:set BINANCE_API_SECRET=xxx
heroku config:set TELEGRAM_BOT_TOKEN=xxx
heroku config:set TELEGRAM_CHAT_ID=xxx

# Create Procfile
echo "worker: python main.py" > Procfile

# Deploy
git push heroku main

# Scale worker
heroku ps:scale worker=1
```

---

### 5. DIGITALOCEAN APP PLATFORM ⭐⭐⭐⭐

**Website:** https://www.digitalocean.com/products/app-platform

**Ưu điểm:**
- ✅ **Servers toàn cầu** (có Singapore)
- ✅ **$5/tháng** basic tier
- ✅ **Always-on**
- ✅ **Good performance**
- ✅ **Managed platform**

**Nhược điểm:**
- ⚠️ Không có free tier
- ⚠️ Minimum $5/tháng

**Pricing:**
- Basic: $5/tháng
- Professional: $12/tháng

**Cách deploy:**
1. Push code lên GitHub
2. Vào DigitalOcean App Platform
3. Create App → GitHub repo
4. Select region: **Singapore**
5. Add environment variables
6. Deploy

---

### 6. AWS EC2 (VPS) ⭐⭐⭐⭐

**Website:** https://aws.amazon.com/ec2

**Ưu điểm:**
- ✅ **FREE tier 12 tháng** (t2.micro)
- ✅ **Regions toàn cầu** (Singapore, Tokyo, Seoul)
- ✅ **Full control**
- ✅ **Reliable**

**Nhược điểm:**
- ⚠️ Phức tạp cho beginners
- ⚠️ Sau 12 tháng: $3-5/tháng

**Cách deploy:**
1. Launch EC2 instance (t2.micro, Singapore)
2. SSH vào server
3. Setup Python + dependencies
4. Upload code
5. Run với systemd hoặc screen

---

### 7. GOOGLE CLOUD RUN ⭐⭐⭐

**Website:** https://cloud.google.com/run

**Ưu điểm:**
- ✅ **FREE tier generous** (2M requests/tháng)
- ✅ **Servers toàn cầu** (có Singapore)
- ✅ **Serverless containers**
- ✅ **Scale to zero**

**Nhược điểm:**
- ⚠️ Phức tạp hơn
- ⚠️ Cần Docker
- ⚠️ Không phù hợp bot chạy liên tục

---

### 8. VULTR / LINODE (VPS) ⭐⭐⭐⭐⭐

**Websites:**
- Vultr: https://vultr.com
- Linode: https://linode.com

**Ưu điểm:**
- ✅ **$5/tháng** (rẻ nhất)
- ✅ **Singapore/Tokyo servers**
- ✅ **Full control**
- ✅ **Simple pricing**
- ✅ **SSD storage**

**Nhược điểm:**
- ⚠️ Phải tự manage server
- ⚠️ Cần biết Linux

**Pricing:**
- $5/tháng: 1 CPU, 1GB RAM, 25GB SSD
- $10/tháng: 1 CPU, 2GB RAM, 55GB SSD

---

### 9. AZURE CONTAINER INSTANCES ⭐⭐⭐

**Website:** https://azure.microsoft.com/en-us/products/container-instances

**Ưu điểm:**
- ✅ **Pay-per-second**
- ✅ **Regions toàn cầu** (Singapore, HK)
- ✅ **Fast deployment**

**Nhược điểm:**
- ⚠️ Phức tạp
- ⚠️ Chi phí khó tính

---

### 10. REPLIT ⭐⭐

**Website:** https://replit.com

**Ưu điểm:**
- ✅ **FREE tier**
- ✅ **Dễ dùng**
- ✅ **Online IDE**

**Nhược điểm:**
- ⚠️ FREE tier sleep nhanh
- ⚠️ Always-on: $7/tháng
- ⚠️ Không chọn được region

---

## 📊 SO SÁNH TỔNG QUAN:

| Platform | FREE? | Chi phí | Region Asia | Độ khó | Khuyến nghị |
|----------|-------|---------|-------------|--------|-------------|
| **Railway** | ✅ $5 credit | $5-10/tháng | ✅ | ⭐ | ⭐⭐⭐⭐⭐ |
| **Render** | ✅ 750h | $7/tháng | ✅ Singapore | ⭐ | ⭐⭐⭐⭐ |
| **Fly.io** | ✅ 3 VMs | $0-2/tháng | ✅ SIN/HKG/NRT | ⭐⭐ | ⭐⭐⭐⭐ |
| **Heroku** | ❌ | $5-7/tháng | ⚠️ US/EU | ⭐ | ⭐⭐ |
| **DO App** | ❌ | $5/tháng | ✅ Singapore | ⭐ | ⭐⭐⭐⭐ |
| **AWS EC2** | ✅ 12 tháng | $3-5/tháng | ✅ Singapore | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Vultr/Linode** | ❌ | $5/tháng | ✅ Singapore | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **GCP Run** | ✅ | Pay-per-use | ✅ Singapore | ⭐⭐⭐ | ⭐⭐⭐ |
| **Replit** | ✅ | $7/tháng | ⚠️ Random | ⭐ | ⭐⭐ |

---

## 🎯 KHUYẾN NGHỊ THEO NHU CẦU:

### 💰 Nếu muốn FREE:
1. **Railway** ($5 credit → ~5 ngày free) ⭐
2. **Fly.io** (3 VMs free forever) ⭐
3. **AWS EC2** (12 tháng free) ⭐

### 🚀 Nếu có budget nhỏ ($5/tháng):
1. **Vultr Singapore** (VPS, full control) ⭐⭐⭐⭐⭐
2. **DigitalOcean Singapore** (VPS hoặc App Platform)
3. **Railway** (managed, easy)

### 😊 Nếu muốn Dễ NHẤT:
1. **Railway** (Git push → deploy) ⭐⭐⭐⭐⭐
2. **Render** (similar, có Singapore)
3. **Replit** (online IDE)

### 🎓 Nếu muốn HỌC:
1. **AWS EC2** (industry standard)
2. **DigitalOcean** (good docs)
3. **Fly.io** (modern stack)

### 🌏 Nếu CẦN Singapore/Asia:
1. **Fly.io** (chọn `sin`, `hkg`, `nrt`) ⭐⭐⭐⭐⭐
2. **Render** (có Singapore)
3. **Vultr Singapore** (VPS)
4. **DigitalOcean Singapore** (VPS/App)

---

## ⭐ TOP 3 KHUYẾN NGHỊ:

### 🥇 1. RAILWAY.APP
```
✅ Dễ nhất
✅ $5 free credit
✅ Git push to deploy
✅ Good for beginners

Setup: 5 phút
```

### 🥈 2. FLY.IO
```
✅ Free forever (3 VMs)
✅ Singapore region
✅ Modern platform

Setup: 15 phút (cần Docker)
```

### 🥉 3. VULTR SINGAPORE
```
✅ $5/tháng
✅ Full control VPS
✅ Singapore IP 100%

Setup: 30 phút (cần Linux)
```

---

## 🛠️ HƯỚNG DẪN DEPLOY NHANH:

### Railway (EASIEST):

```bash
# 1. Tạo Procfile
echo "worker: python main.py" > Procfile

# 2. Push lên GitHub
git init
git add .
git commit -m "Deploy to Railway"
git push origin main

# 3. Vào Railway.app
# - Login với GitHub
# - New Project → Deploy from GitHub
# - Add environment variables
# - Deploy!
```

### Fly.io (BEST VALUE):

```bash
# 1. Install Fly CLI
iwr https://fly.io/install.ps1 -useb | iex

# 2. Create Dockerfile (tôi tạo sẵn cho bạn)

# 3. Deploy
fly auth login
fly launch --name rsi-mfi-bot --region sin
fly secrets set BINANCE_API_KEY="xxx"
fly secrets set BINANCE_API_SECRET="xxx"
fly secrets set TELEGRAM_BOT_TOKEN="xxx"
fly secrets set TELEGRAM_CHAT_ID="xxx"
fly deploy
```

---

## 💡 KẾT LUẬN:

**Thay thế Vercel tốt nhất:**

1. **FREE:** Fly.io (3 VMs, Singapore)
2. **EASY:** Railway ($5 credit free)
3. **CHEAP:** Vultr/Linode VPS ($5/tháng)
4. **PRO:** AWS EC2 (12 tháng free, sau đó $3-5)

**Tránh:**
- Vercel (IP bị chặn)
- Heroku (đắt, không có Asia)
- Platforms không có Singapore region

---

## 📞 NEXT STEPS:

Bạn muốn tôi hướng dẫn deploy lên platform nào?

1. **Railway** → Dễ nhất, $5 credit free
2. **Fly.io** → Free forever, Singapore
3. **Vultr VPS** → $5/tháng, full control
4. **Hoặc chạy LOCAL** → FREE, chạy ngay!

Cho tôi biết lựa chọn của bạn! 🚀
