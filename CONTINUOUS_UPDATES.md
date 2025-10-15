# 🔄 CONTINUOUS UPDATES - Cập nhật liên tục

## ✅ Tính năng mới đã được thêm!

Bot giờ đây có khả năng gửi **cập nhật liên tục** cho các đồng coin bạn quan tâm.

## 🎯 Cách hoạt động:

### Mode 1: Gửi tất cả updates (Mặc định)
```python
SEND_CONTINUOUS_UPDATES = True
```

Bot sẽ gửi thông tin chi tiết cho **TẤT CẢ** các coin đạt điều kiện mỗi lần scan:
- ✅ Gửi update mỗi 5 phút
- ✅ Hiển thị đầy đủ RSI, MFI, Price, 24h data
- ✅ Không cần phải có signal mới
- ✅ Theo dõi xu hướng liên tục

**Ưu điểm:**
- Luôn biết tình hình thị trường
- Dễ spot xu hướng đảo chiều
- Không bỏ lỡ cơ hội

**Nhược điểm:**
- Nhiều tin nhắn hơn
- Có thể bị spam nếu nhiều coin đạt điều kiện

### Mode 2: Chỉ gửi signal mới (Tiết kiệm)
```python
SEND_CONTINUOUS_UPDATES = False
```

Bot chỉ gửi khi có **tín hiệu mới**:
- ✅ Ít tin nhắn hơn
- ✅ Chỉ thông báo khi có thay đổi quan trọng
- ❌ Có thể bỏ lỡ updates nhỏ

## 📊 Ví dụ Message liên tục:

```
#ETHUSDT
⏰ Current Time: 13:45:20

━━━━━━━━━━━━━━━━━━━━
📊 RSI ANALYSIS
RSI = 29.70 🟢
🔔 Low 🟢🟢 RSI Alert 20-
RSI 5M: 85.06 🔴
RSI 1H: 29.70 🟢
RSI 4H: 90.37 🔴
RSI 1D: 70.98 ⚪

💰 MFI ANALYSIS
MFI = 20.50 🟢
🔔 Low 🟢🟢 MFI Alert 20-
MFI 5M: 15.02 🟢
MFI 1H: 20.50 🟢
MFI 4H: 19.65 🟢
MFI 1D: 33.03 ⚪

🎯 CONSENSUS: RSI + MFI
5M: 50.0 - 🟢 BUY
1H: 25.1 - ⚪ NEUTRAL  
4H: 55.0 - ⚪ NEUTRAL
1D: 52.0 - 🔴 SELL

🟢 Overall: BUY (2/4)

━━━━━━━━━━━━━━━━━━━━
🏷️ Price: $3,941.4000
🕒 24h: 📉 -5.06% | Vol: $3.25B
⬆️ High: $4,292.0000 (+8.17%)
⬇️ Low: $3,888.7000 (-1.36%)
━━━━━━━━━━━━━━━━━━━━
```

Tin nhắn này sẽ được gửi **mỗi 5 phút** cho các coin đạt điều kiện!

## 🔧 Cấu hình:

### Trong file `config.py`:

```python
# Bật/tắt continuous updates
SEND_CONTINUOUS_UPDATES = True  # True = Gửi liên tục, False = Chỉ signal mới

# Khoảng thời gian giữa các lần scan
SCAN_INTERVAL = 300  # 5 phút (300 giây)

# Ngưỡng consensus tối thiểu để gửi
MIN_CONSENSUS_STRENGTH = 3  # Cần ít nhất 3/4 timeframes đồng ý

# Số coin tối đa mỗi lần
MAX_COINS_PER_MESSAGE = 10  # Giới hạn để tránh spam
```

## 🎚️ Điều chỉnh tần suất:

### Gửi mỗi 1 phút (Nhanh):
```python
SCAN_INTERVAL = 60  # 1 phút
```

### Gửi mỗi 15 phút (Vừa phải):
```python
SCAN_INTERVAL = 900  # 15 phút
```

### Gửi mỗi 1 giờ (Chậm):
```python
SCAN_INTERVAL = 3600  # 1 giờ
```

## 🎯 Use Cases:

### Day Trading (Scalping):
```python
SCAN_INTERVAL = 60  # 1 phút
TIMEFRAMES = ['1m', '5m', '15m', '1h']
MIN_CONSENSUS_STRENGTH = 2  # Nhanh hơn
```

### Swing Trading:
```python
SCAN_INTERVAL = 300  # 5 phút (mặc định)
TIMEFRAMES = ['5m', '1h', '4h', '1d']
MIN_CONSENSUS_STRENGTH = 3  # An toàn hơn
```

### Position Trading:
```python
SCAN_INTERVAL = 3600  # 1 giờ
TIMEFRAMES = ['1h', '4h', '1d', '1w']
MIN_CONSENSUS_STRENGTH = 4  # Rất chắc chắn
```

## 📱 Telegram Settings:

Để tránh bị flood, thiết lập trong Telegram:
1. Tắt notification âm thanh cho bot
2. Pin group chat để dễ theo dõi
3. Sử dụng Telegram folder để tổ chức

## ⚠️ Lưu ý:

1. **Vercel Free Plan:**
   - Mỗi request tối đa 10 giây
   - Chỉ scan được ~50 coins
   - Nên dùng SCAN_INTERVAL >= 300 (5 phút)

2. **Telegram Rate Limits:**
   - Tối đa 30 messages/giây
   - Bot tự động delay để tránh ban
   - Nếu quá nhiều coins, sẽ gửi theo batch

3. **Binance API Limits:**
   - 1200 requests/phút
   - Bot tự động throttle
   - Delay 0.1s giữa các requests

## 🚀 Deploy với tính năng mới:

### Local:
```powershell
& "H:/BOT UPGRADE/.venv/Scripts/python.exe" main.py
```

### Vercel:
```powershell
vercel --prod
```

### Cron-Job.org:
URL vẫn giữ nguyên:
```
https://rsi-mfi-trading-botv2.vercel.app/api/scan
```

## 📊 Kết quả mong đợi:

Với `SEND_CONTINUOUS_UPDATES = True`:

**Mỗi 5 phút bạn sẽ nhận được:**
1. Bảng tổng hợp tất cả signals
2. Chi tiết từng coin (tối đa 10 coins)
3. Thông tin đầy đủ: RSI, MFI, Price, 24h data
4. Alerts khi có cơ hội tốt (RSI/MFI extreme)

**Timeline ví dụ:**
```
13:00 - Scan 1: Tìm thấy 5 coins → Gửi 5 messages
13:05 - Scan 2: Tìm thấy 7 coins → Gửi 7 messages  
13:10 - Scan 3: Tìm thấy 3 coins → Gửi 3 messages
...
```

---

**Happy Trading với updates liên tục! 🎉📊📈**
