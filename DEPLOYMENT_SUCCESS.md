# 🎉 DEPLOY THÀNH CÔNG LÊN VERCEL!

## ✅ Thông tin deploy:

**Production URL:** https://rsi-mfi-trading-botv2.vercel.app

**Project Dashboard:** https://vercel.com/hieuhuynh234s-projects/rsi-mfi-trading-botv2

## 📡 API Endpoints:

### 1. Health Check
```
https://rsi-mfi-trading-botv2.vercel.app/
```
Kiểm tra bot có hoạt động không

### 2. Market Scan
```
https://rsi-mfi-trading-botv2.vercel.app/api/scan
```
Trigger quét thị trường thủ công

## 🔧 Environment Variables đã cấu hình:

✅ BINANCE_API_KEY
✅ BINANCE_API_SECRET  
✅ TELEGRAM_BOT_TOKEN
✅ TELEGRAM_CHAT_ID

## 🤖 Setup Cron Job (Chạy tự động mỗi 5 phút)

### Vì Vercel FREE không có Cron, dùng Cron-Job.org:

1. **Đăng ký:** https://cron-job.org/en/
2. **Tạo Cronjob mới:**
   - Title: `RSI MFI Bot Scanner`
   - URL: `https://rsi-mfi-trading-botv2.vercel.app/api/scan`
   - Execution schedule: 
     ```
     */5 * * * *
     ```
     (Every 5 minutes)
   - Timeout: 30 seconds
   - Enabled: ✅

3. **Save** và bot sẽ tự động chạy!

## 🧪 Test thủ công:

### Test bằng PowerShell:
```powershell
# Test health check
curl https://rsi-mfi-trading-botv2.vercel.app/

# Test market scan
curl https://rsi-mfi-trading-botv2.vercel.app/api/scan
```

### Test bằng trình duyệt:
Mở: https://rsi-mfi-trading-botv2.vercel.app/api/scan

Bạn sẽ nhận được JSON response với kết quả scan.

## 📊 Kết quả mong đợi:

Sau khi setup Cron Job, bot sẽ:
1. ✅ Quét 348 đồng coin trên Binance mỗi 5 phút
2. ✅ Phân tích RSI + MFI trên 4 timeframes
3. ✅ Gửi tín hiệu BUY/SELL về Telegram
4. ✅ Chỉ gửi khi có consensus ≥ 3/4 timeframes

## 🔍 Xem Logs:

```powershell
vercel logs
```

Hoặc vào Dashboard → Deployments → Click vào deployment → Runtime Logs

## 🎯 Next Steps:

1. ✅ Setup Cron-Job.org (bắt buộc cho FREE plan)
2. ✅ Kiểm tra Telegram nhận được tin nhắn
3. ✅ Monitor logs để đảm bảo hoạt động tốt

## 💡 Tips:

- **Giới hạn Vercel FREE:** 10 giây timeout → Bot chỉ scan 50 coins đầu
- **Nâng cấp Pro:** $20/tháng → 60s timeout + built-in Cron
- **Alternative:** Chạy local 24/7 nếu có máy

## 📞 Support Commands:

```powershell
# Xem danh sách deployments
vercel ls

# Xem logs realtime
vercel logs --follow

# Xem env vars
vercel env ls

# Remove project (nếu cần)
vercel remove rsi-mfi-trading-botv2
```

---

**Chúc mừng! Bot của bạn đã sẵn sàng giao dịch! 🚀📈**
