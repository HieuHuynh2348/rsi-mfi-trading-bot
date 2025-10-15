# RSI + MFI Multi-Timeframe Trading Bot

Bot giao dịch tự động phân tích RSI và MFI trên nhiều khung thời gian, tích hợp với Binance API và Telegram.

## 🌟 Tính năng

- ✅ Kết nối với Binance API để lấy dữ liệu real-time
- ✅ Tự động lọc bỏ các đồng coin BEAR, BULL, UP, DOWN
- ✅ Tính toán RSI và MFI theo thuật toán Pine Script
- ✅ Phân tích đa khung thời gian (5m, 1h, 4h, 1d)
- ✅ Gửi thông báo tự động qua Telegram
- ✅ Tạo và gửi biểu đồ kỹ thuật
- ✅ Lọc theo volume tối thiểu
- ✅ Hệ thống consensus signal (BUY/SELL/NEUTRAL)

## 📋 Yêu cầu

- Python 3.8 trở lên
- Tài khoản Binance với API key
- Telegram Bot Token và Chat ID

## 🚀 Cài đặt

### 1. Cài đặt Python packages

```powershell
pip install -r requirements.txt
```

### 2. Cấu hình API Keys

Mở file `config.py` và điền thông tin của bạn:

```python
# Binance API
BINANCE_API_KEY = "your_binance_api_key_here"
BINANCE_API_SECRET = "your_binance_api_secret_here"

# Telegram Bot
TELEGRAM_BOT_TOKEN = "your_telegram_bot_token_here"
TELEGRAM_CHAT_ID = "your_telegram_chat_id_here"
```

### 3. Lấy Binance API Key

1. Đăng nhập vào Binance
2. Vào **Profile → API Management**
3. Tạo API key mới
4. Lưu lại API Key và Secret Key
5. Bật quyền "Enable Reading" (không cần quyền trading)

### 4. Tạo Telegram Bot

1. Tìm **@BotFather** trên Telegram
2. Gửi lệnh `/newbot`
3. Đặt tên cho bot
4. Lưu lại **Bot Token**

### 5. Lấy Chat ID

1. Tìm **@userinfobot** trên Telegram
2. Bắt đầu chat
3. Bot sẽ gửi cho bạn **Chat ID**

## 🎮 Sử dụng

### Chạy bot

```powershell
python main.py
```

### Tùy chỉnh tham số

Chỉnh sửa trong `config.py`:

```python
# RSI Settings
RSI_PERIOD = 14
RSI_LOWER = 20
RSI_UPPER = 80

# MFI Settings
MFI_PERIOD = 14
MFI_LOWER = 20
MFI_UPPER = 80

# Timeframes
TIMEFRAMES = ['5m', '1h', '4h', '1d']

# Scan interval (seconds)
SCAN_INTERVAL = 300  # 5 phút

# Minimum consensus strength (1-4)
MIN_CONSENSUS_STRENGTH = 3
```

## 📊 Cách hoạt động

### 1. Lấy dữ liệu
- Bot quét tất cả các cặp USDT trên Binance
- Lọc bỏ các đồng có từ khóa BEAR, BULL, UP, DOWN
- Lọc theo volume tối thiểu (mặc định: 1M USDT)

### 2. Phân tích kỹ thuật
- Tính RSI từ giá HLCC/4 (High + Low + Close + Close) / 4
- Tính MFI từ Typical Price (HLC/3) và Volume
- Phân tích trên 4 khung thời gian: 5m, 1h, 4h, 1d

### 3. Tạo tín hiệu
- **BUY**: Khi RSI < 20 VÀ MFI < 20
- **SELL**: Khi RSI > 80 VÀ MFI > 80
- **NEUTRAL**: Các trường hợp khác

### 4. Consensus (Đồng thuận)
- Tổng hợp tín hiệu từ tất cả khung thời gian
- Chỉ gửi cảnh báo khi có ít nhất 3/4 khung thời gian đồng ý

### 5. Gửi thông báo
- Bảng tổng hợp tất cả tín hiệu
- Chi tiết từng đồng coin
- Biểu đồ kỹ thuật (RSI, MFI)

## 📁 Cấu trúc dự án

```
BOT UPGRADE/
│
├── main.py                 # File chính để chạy bot
├── config.py              # Cấu hình API keys và tham số
├── binance_client.py      # Module kết nối Binance API
├── telegram_bot.py        # Module gửi Telegram
├── indicators.py          # Tính toán RSI và MFI
├── chart_generator.py     # Tạo biểu đồ
├── requirements.txt       # Python dependencies
├── README.md             # Hướng dẫn (file này)
└── bot.log               # Log file (tự động tạo)
```

## ⚙️ Tùy chỉnh nâng cao

### Thay đổi coin muốn giao dịch

```python
QUOTE_ASSET = 'USDT'  # Hoặc 'BTC', 'ETH', etc.
```

### Thêm từ khóa loại trừ

```python
EXCLUDED_KEYWORDS = ['BEAR', 'BULL', 'UP', 'DOWN', 'LEVERAGE']
```

### Chỉ nhận tổng hợp (không gửi chi tiết)

```python
SEND_SUMMARY_ONLY = True
```

### Tắt biểu đồ

```python
SEND_CHARTS = False
```

## 🛠️ Xử lý sự cố

### Lỗi kết nối Binance
- Kiểm tra API key và secret
- Đảm bảo API key có quyền "Enable Reading"
- Kiểm tra kết nối internet

### Lỗi Telegram
- Kiểm tra Bot Token
- Kiểm tra Chat ID
- Đảm bảo đã bắt đầu chat với bot

### Bot không tìm thấy tín hiệu
- Giảm `MIN_CONSENSUS_STRENGTH`
- Điều chỉnh ngưỡng RSI/MFI
- Giảm `MIN_VOLUME_USDT`

## 📝 Lưu ý quan trọng

⚠️ **CẢNH BÁO:**
- Bot này chỉ để tham khảo, không phải lời khuyên đầu tư
- Luôn kiểm tra kỹ trước khi giao dịch
- Không bao giờ đầu tư số tiền bạn không thể mất
- Thị trường crypto rất biến động

## 📜 License

MIT License - Tự do sử dụng và chỉnh sửa

## 🤝 Hỗ trợ

Nếu gặp vấn đề, hãy kiểm tra:
1. File `bot.log` để xem lỗi chi tiết
2. Đảm bảo tất cả dependencies đã được cài đặt
3. Kiểm tra API keys đã được cấu hình đúng

---

**Chúc bạn giao dịch thành công! 🚀**
