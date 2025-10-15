# Vercel Deployment Alternative - Using GitHub Actions

Nếu bạn dùng Vercel Free Plan (không có Cron Jobs), dùng GitHub Actions để trigger scan.

## Setup

### 1. Push code lên GitHub
```powershell
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

### 2. Deploy Vercel từ GitHub
1. Vào https://vercel.com
2. Import Git Repository
3. Chọn repo của bạn
4. Add Environment Variables (BINANCE_API_KEY, etc.)
5. Deploy

### 3. Tạo GitHub Actions Workflow

Tạo file: `.github/workflows/market-scan.yml`

```yaml
name: Market Scan Every 5 Minutes

on:
  schedule:
    # Runs every 5 minutes
    - cron: '*/5 * * * *'
  workflow_dispatch:
    # Allows manual trigger from GitHub UI

jobs:
  scan:
    runs-on: ubuntu-latest
    
    steps:
      - name: Trigger Vercel Market Scan
        run: |
          response=$(curl -s -w "\n%{http_code}" https://YOUR-APP.vercel.app/api/scan)
          http_code=$(echo "$response" | tail -n1)
          body=$(echo "$response" | head -n-1)
          
          echo "HTTP Status: $http_code"
          echo "Response: $body"
          
          if [ $http_code -ne 200 ]; then
            echo "Error: Scan failed with status $http_code"
            exit 1
          fi
      
      - name: Log Result
        run: |
          echo "Market scan completed successfully at $(date)"
```

### 4. Enable GitHub Actions
1. Vào repository → Settings → Actions → General
2. Chọn "Allow all actions and reusable workflows"
3. Save

### 5. Test Manual Run
1. Vào repository → Actions
2. Chọn "Market Scan Every 5 Minutes"
3. Click "Run workflow"

## Thay thế URL
Trong file `.github/workflows/market-scan.yml`, thay:
```
https://YOUR-APP.vercel.app/api/scan
```
bằng URL Vercel thật của bạn.

## Lợi ích
✅ Hoàn toàn miễn phí
✅ Chạy mỗi 5 phút
✅ Có logs trong GitHub Actions
✅ Có thể trigger thủ công
✅ Không cần Vercel Pro Plan

## Giới hạn
⚠️ GitHub Actions có 2000 phút miễn phí/tháng
- Chạy mỗi 5 phút = 12 lần/giờ = 288 lần/ngày
- Mỗi lần ~1 phút = 288 phút/ngày = ~8,640 phút/tháng
- **Vượt quá free tier!**

### Giải pháp: Tăng interval lên 15 phút
```yaml
on:
  schedule:
    - cron: '*/15 * * * *'  # Every 15 minutes instead
```

Hoặc chỉ scan trong giờ giao dịch:
```yaml
on:
  schedule:
    # Every 5 minutes, only during trading hours (9 AM - 5 PM UTC)
    - cron: '*/5 9-17 * * *'
```
