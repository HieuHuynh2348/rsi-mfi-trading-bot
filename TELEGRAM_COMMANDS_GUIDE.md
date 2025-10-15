# 🤖 TELEGRAM COMMANDS - Hướng dẫn sử dụng

## ✨ NÂNG CẤP MỚI: Interactive Commands!

Bot giờ đây có thể nhận lệnh từ Telegram! Không cần chờ auto-scan, bạn có thể yêu cầu phân tích bất kỳ coin nào!

---

## 📊 PHÂN TÍCH SYMBOL (QUAN TRỌNG NHẤT!)

### Cách dùng cực đơn giản:
```
/BTC      → Phân tích Bitcoin (tự động thêm USDT)
/ETH      → Phân tích Ethereum
/LINK     → Phân tích Chainlink
/ADA      → Phân tích Cardano
/SOL      → Phân tích Solana
```

**💡 Hệ thống TỰ ĐỘNG ghép với USDT!**
- Bạn gõ: `/LINK`
- Bot hiểu: `LINKUSDT`

### Kết quả bạn nhận được:
1. ✅ **Phân tích RSI** trên 4 khung thời gian (5m, 1h, 3h, 1d)
2. ✅ **Phân tích MFI** trên 4 khung thời gian
3. ✅ **Consensus** (BUY/SELL/NEUTRAL) với độ mạnh (1-4)
4. ✅ **Giá hiện tại** + thay đổi 24h
5. ✅ **Biểu đồ kỹ thuật** multi-timeframe

---

## 🔍 LỆNH THÔNG TIN THỊ TRƯỜNG

### `/price SYMBOL`
Xem giá hiện tại nhanh

**Ví dụ:**
```
/price BTC
/price ETH
/price LINK
```

**Kết quả:**
```
💰 BTCUSDT
Price: $67,234.5678
```

---

### `/24h SYMBOL`
Xem dữ liệu thị trường 24 giờ

**Ví dụ:**
```
/24h BTC
/24h ETH
```

**Kết quả:**
```
📊 BTCUSDT - 24h Data

💰 Price: $67,234.56
📈 Change: +2.35%

⬆️ High: $68,500.00
⬇️ Low: $65,800.00

💵 Volume: $1,234.56M
```

---

### `/top`
Xem Top 10 coin có volume lớn nhất

**Kết quả:**
```
🏆 Top 10 Volume (24h)

1. BTCUSDT
   $2,345.6M | 📈 +1.23%

2. ETHUSDT
   $1,234.5M | 📉 -0.45%

...
```

---

## ⚙️ LỆNH ĐIỀU KHIỂN BOT

### `/status`
Xem trạng thái bot và cài đặt

**Kết quả:**
```
🤖 Bot Status

⚡ System: ✅ Online
🔗 Binance: ✅ Connected
💬 Telegram: ✅ Connected

⚙️ Settings:
• Scan Interval: 300s
• Min Consensus: 1/4
• RSI Period: 6
• MFI Period: 6
• Timeframes: 5m, 1h, 3h, 1d

📊 Trading Pairs:
• Quote: USDT
• Min Volume: $1,000,000

🕐 Current Time: 2025-10-15 15:30:00
```

---

### `/scan`
Bắt buộc bot quét thị trường ngay lập tức (không cần chờ 5 phút)

**Kết quả:**
```
🔍 Starting market scan...
⏳ Scan in progress... Results will appear shortly.

(Sau đó sẽ nhận được kết quả scan như auto-scan)
```

---

### `/settings`
Xem cài đặt hiện tại (tương tự /status)

---

## ℹ️ LỆNH TRỢ GIÚP

### `/help` hoặc `/start`
Xem danh sách tất cả lệnh

### `/about`
Thông tin về bot

**Kết quả:**
```
🤖 RSI+MFI Trading Bot

Version: 2.0
Platform: Railway.app
Exchange: Binance

Features:
✅ Multi-timeframe RSI+MFI analysis
✅ Real-time price monitoring
✅ Automatic signal detection
✅ Interactive commands
✅ 24/7 cloud operation
```

---

## 📈 VÍ DỤ THỰC TẾ

### Ví dụ 1: Phân tích nhanh Bitcoin
```
Bạn: /BTC

Bot: 
🔍 Analyzing BTCUSDT...

#BTCUSDT
⏰ Current Time: 15:30:45

━━━━━━━━━━━━━━━━━━━━
📊 RSI ANALYSIS
RSI = 25.34 🟢
🔔 Low 🟢🟢 RSI Alert 25-
RSI 5M: 24.12 🟢
RSI 1H: 26.45 🟢
RSI 3H: 25.89 🟢
RSI 1D: 32.10 ⚪

💰 MFI ANALYSIS
MFI = 22.15 🟢
...

🎯 CONSENSUS: RSI + MFI
5M: 23.1 - 🟢 BUY
1H: 24.3 - 🟢 BUY
3H: 25.0 - 🟢 BUY
1D: 31.5 - ⚪ NEUTRAL

🟢 Overall: BUY (3/4)
━━━━━━━━━━━━━━━━━━━━

+ Biểu đồ kỹ thuật
```

---

### Ví dụ 2: Kiểm tra giá nhanh
```
Bạn: /price LINK

Bot:
💰 LINKUSDT
Price: $12.3456
```

---

### Ví dụ 3: Xem top volume
```
Bạn: /top

Bot:
🏆 Top 10 Volume (24h)

1. BTCUSDT - $2,345.6M | 📈 +1.23%
2. ETHUSDT - $1,234.5M | 📉 -0.45%
3. BNBUSDT - $567.8M | 📈 +0.89%
...
```

---

## 💡 TIPS & TRICKS

### 1. Phân tích nhanh nhiều coin:
```
/BTC
/ETH
/LINK
/ADA
/SOL
```
Gõ liền, bot sẽ phân tích lần lượt!

### 2. Không cần viết hoa:
```
/btc     ← OK
/BTC     ← OK
/Btc     ← OK
```
Tất cả đều hoạt động!

### 3. Tự động thêm USDT:
```
/LINK    → Tự động thành LINKUSDT
/ETH     → Tự động thành ETHUSDT
```

### 4. Kiểm tra bot còn sống:
```
/status  → Xem bot có online không
```

---

## 🚨 LƯU Ý QUAN TRỌNG

### ✅ Lệnh HOẠT ĐỘNG:
- `/BTC`, `/ETH`, `/LINK` - Phân tích symbol
- `/price BTC` - Giá hiện tại
- `/24h BTC` - Dữ liệu 24h
- `/top` - Top 10 volume
- `/status` - Trạng thái bot
- `/help` - Trợ giúp

### ❌ Lệnh CHƯA HOẠT ĐỘNG (sẽ update sau):
- `/watch`, `/unwatch`, `/watchlist` - Watchlist feature
- `/rsi`, `/mfi` - Riêng RSI/MFI (có thể thêm sau)
- `/chart` - Chart only (hiện tại chart gửi kèm analysis)

---

## 🔄 AUTO-SCAN VẪN HOẠT ĐỘNG!

**Lưu ý:** Dù có commands, bot vẫn tự động scan mỗi 5 phút!

- ✅ **Auto-scan:** Mỗi 5 phút, bot tự quét 348 symbols
- ✅ **Manual command:** Bạn có thể yêu cầu phân tích bất kỳ lúc nào
- ✅ **Cả hai hoạt động song song!**

---

## 📱 CÁCH SỬ DỤNG HIỆU QUẢ

### Scenario 1: Theo dõi coin cụ thể
```
- Mở Telegram
- Gõ: /BTC
- Nhận phân tích ngay lập tức
- Lặp lại mỗi khi muốn update
```

### Scenario 2: Kiểm tra thị trường tổng quan
```
- Gõ: /top
- Xem top 10 volume
- Chọn coin quan tâm
- Gõ: /SYMBOL để phân tích chi tiết
```

### Scenario 3: Check giá nhanh
```
- Gõ: /price BTC
- Nhận giá ngay (nhanh hơn mở Binance!)
```

---

## 🎯 TÓM TẮT NHANH

| Lệnh | Mục đích | Ví dụ |
|------|----------|-------|
| `/<SYMBOL>` | Phân tích đầy đủ | `/BTC`, `/ETH` |
| `/price <SYMBOL>` | Giá hiện tại | `/price BTC` |
| `/24h <SYMBOL>` | Dữ liệu 24h | `/24h ETH` |
| `/top` | Top 10 volume | `/top` |
| `/status` | Trạng thái bot | `/status` |
| `/help` | Trợ giúp | `/help` |

---

**🎉 Enjoy your upgraded bot!**

*Giờ đây bạn có thể điều khiển bot mọi lúc, mọi nơi qua Telegram!* 🚀
