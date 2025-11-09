# 🎮 Trading Bot - Quick Reference Card

## 🚀 Tính Năng Chính (November 9, 2025)

### 1️⃣ Pump Detector (3-Layer System)
```
🎯 Mục tiêu: Phát hiện pump sớm 10-20 phút với 90%+ accuracy

📊 3 Layers:
   Layer 1 (5m)   → Phát hiện sớm     → 60% threshold → Quét 3 phút
   Layer 2 (1h/4h) → Xác nhận         → 70% threshold → Quét 10 phút  
   Layer 3 (1D)    → Xu hướng dài hạn → 80% threshold → Quét 15 phút

✨ Auto-Save: Coins >= 80% tự động vào Watchlist (max 20)
```

**Commands:**
- `/startpumpwatch` - Bật giám sát pump (auto nền)
- `/stoppumpwatch` - Dừng giám sát
- `/pumpstatus` - Xem trạng thái & settings
- `/pumpscan SYMBOL` - Quét thủ công 1 coin

**Buttons:**
- 🌐 Quét TẤT CẢ Coins - Quét top 200 symbols (~2-5 phút)
- ₿ BTC / Ξ ETH / 🔶 BNB / 🟣 SOL - Quick scan

---

### 2️⃣ Bot Monitor
```
🎯 Mục tiêu: Phát hiện bot manipulation và pump schemes

⚙️ Settings:
   Bot Score     → >= 70%
   Pump Score    → >= 70%
   Max Alerts    → 10/scan (sorted by priority)
   Scan Interval → 30 phút

🎖️ Priority Badges:
   🔴 >= 90% - Cực kỳ nguy hiểm
   🟡 80-89% - Nguy hiểm cao
   ⚠️ 70-79% - Bot mạnh
```

**Commands:**
- `/startbotmonitor` - Bật giám sát bot
- `/stopbotmonitor` - Dừng giám sát
- `/botmonitorstatus` - Xem trạng thái
- `/botscan` - Quét thủ công

---

### 3️⃣ Watchlist (Auto-Save)
```
🎯 Mục tiêu: Theo dõi coins yêu thích + Auto-save từ Pump

📋 Features:
   Manual Add    → /watch SYMBOL
   Auto-Save     → Từ Pump Detector (>= 80%)
   Max Size      → 20 coins
   Monitor       → Mỗi 5 phút
```

**Commands:**
- `/watch SYMBOL` - Thêm coin vào watchlist
- `/unwatch SYMBOL` - Xóa coin khỏi watchlist
- `/watchlist` - Xem danh sách
- `/scanwatch` - Quét tất cả coins trong list
- `/clearwatch` - Xóa toàn bộ

---

### 4️⃣ Volume Detector
```
🎯 Mục tiêu: Phát hiện volume spikes bất thường

🔥 Sensitivity Levels:
   Low    → >= 5x volume
   Medium → >= 3x volume  
   High   → >= 2x volume
```

**Commands:**
- `/volumescan` - Quét volume spikes
- `/volumesensitivity [low/medium/high]` - Cài đặt độ nhạy

---

### 5️⃣ Market Scanner
```
🎯 Mục tiêu: Quét thị trường tìm cơ hội trading

⚙️ Settings:
   Scan Interval → 15 phút
   Focus         → Top coins by volume + indicators
```

**Commands:**
- `/startmarketscan` - Bật quét market
- `/stopmarketscan` - Dừng quét
- `/marketstatus` - Xem trạng thái

---

### 6️⃣ Watchlist Monitor
```
🎯 Mục tiêu: Theo dõi coins trong watchlist liên tục

⚙️ Settings:
   Check Interval → 5 phút
   Signals        → RSI/MFI changes, volume spikes
```

**Commands:**
- `/startmonitor` - Bật monitor
- `/stopmonitor` - Dừng monitor
- `/monitorstatus` - Xem trạng thái

---

## 📱 Inline Keyboards

### Main Menu:
```
📊 Quét Thị Trường         ⭐ Quét Watchlist
📝 Watchlist               🗑️ Xóa Watchlist
🔥 Quét Volume             🎯 Cài Đặt Volume
🔔 Bật Monitor             ⏸️ Dừng Monitor
🤖 Bot Monitor (70%)       🛑 Dừng Bot Monitor
🌍 Bật Market Scan         🛑 Dừng Market Scan
🚀 Pump Watch (Auto-Save)  ⏸️ Dừng Pump Watch
📈 Top Coins               🔍 Phân Tích Nhanh
📊 Trạng Thái Bot         ⚙️ Cài Đặt
📡 Monitor Status          🌐 Market Status
🤖 Bot Scan                🚀 Pump Scan
⚡ Hiệu Suất              ℹ️ Trợ Giúp
```

### Pump Detector Menu:
```
🚀 Bật Pump Watch          ⏸️ Dừng Pump Watch
📊 Trạng Thái & Settings
🌐 Quét TẤT CẢ Coins (Top 200)
₿ BTC                     Ξ ETH
🔶 BNB                    🟣 SOL
💡 Auto-Save >= 80%
🔙 Menu Chính
```

---

## 🔔 Alerts & Notifications

### Pump Alert Format:
```
🚀 PHÁT HIỆN PUMP - ĐỘ CHÍNH XÁC CAO

💎 BTCUSDT
📊 Điểm tổng hợp: 85%

⚡ Layer 1 (5m) - Phát hiện sớm:
   • Volume spike: 4.2x
   • Giá tăng 5m: +3.5%
   • RSI momentum: +15
   • Điểm: 75%

✅ Layer 2 (1h/4h) - Xác nhận:
   • RSI 1h: 65.5 (+12)
   • Volume ổn định: 2.8x
   • Điểm: 82%

📈 Layer 3 (1D) - Xu hướng:
   • RSI 1D: 55
   • Vị trí giá: 45%
   • Điểm: 70%

🎯 KẾT LUẬN: CAO (80%+ chính xác)
✅ Đã tự động thêm vào Watchlist
```

### Bot Alert Format:
```
🔴 PHÁT HIỆN BOT TRADING - CỰC KỲ NGUY HIỂM

💎 ETHUSDT
🤖 Bot Score: 85%
🚀 Pump Score: 78%
📊 Tổng: 163%

⚠️ CẢNH BÁO:
   • Bot đang tích cực thao túng
   • Volume bất thường
   • Giá không ổn định

💡 KHUYẾN NGHỊ: TRÁNH GIAO DỊCH
```

---

## ⚙️ System Settings

### Thresholds:
```
Pump Detector:
   Layer 1: >= 60%
   Layer 2: >= 70%
   Final:   >= 80%
   
Bot Monitor:
   Bot Score:  >= 70%
   Pump Score: >= 70%
   
Watchlist:
   Auto-Save: >= 80%
   Max Size:  20 coins
```

### Scan Intervals:
```
Pump Layer 1:    3 minutes  (5m timeframe)
Pump Layer 2:    10 minutes (1h/4h timeframe)
Pump Layer 3:    15 minutes (1D timeframe)
Bot Monitor:     30 minutes
Market Scanner:  15 minutes
Watchlist:       5 minutes
```

### API Usage:
```
Binance Limit:   1200 requests/minute
Bot Usage:       ~300-400 requests/minute
Safety Margin:   65-70% of limit
Status:          ✅ Safe
```

---

## 🎯 Best Practices

### 1. Pump Trading:
```
✅ DO:
   • Chờ Layer 3 confirmation (80%+)
   • Set stop loss -3% to -5%
   • Take profit +5% to +30%
   • Hold 1-3 days max
   
❌ DON'T:
   • Vào lệnh ở Layer 1 only (60%)
   • FOMO vào khi đã pump 10%+
   • Không set stop loss
   • Hold quá lâu (> 1 week)
```

### 2. Bot Avoidance:
```
✅ DO:
   • Tránh coins có Bot Score >= 70%
   • Đợi bot activity giảm
   • Check multiple timeframes
   
❌ DON'T:
   • Trade khi 🔴 Cực kỳ nguy hiểm
   • Ignore bot warnings
   • FOMO vào pump schemes
```

### 3. Watchlist Management:
```
✅ DO:
   • Let auto-save handle high quality pumps
   • Manually add favorites
   • Review và remove dead coins
   • Keep list under 15-20 coins
   
❌ DON'T:
   • Add every coin you see
   • Ignore monitor alerts
   • Keep coins with no activity
```

---

## 🆘 Troubleshooting

### Bot Not Responding:
```
1. Check /status
2. Restart: /stopmonitor → /startmonitor
3. Check Railway logs
```

### No Pump Alerts:
```
1. /pumpstatus - Check if running
2. /startpumpwatch - Enable detector
3. Wait 15-30 minutes for full cycle
4. Market might be slow
```

### Too Many Alerts:
```
1. Thresholds đã tăng lên 70%/80%
2. Check /botmonitorstatus
3. Adjust sensitivity if needed
```

### Watchlist Full:
```
1. /watchlist - Xem danh sách
2. /unwatch SYMBOL - Xóa coins cũ
3. Max 20 coins (auto-managed)
```

---

## 📊 Performance Metrics

### Accuracy Targets:
```
Pump Detector:  90%+ (with 3-layer confirmation)
Bot Monitor:    85%+ (with 70% threshold)
Volume Alerts:  80%+ (dynamic sensitivity)
Market Scanner: 75%+ (top signals)
```

### Response Times:
```
Pump Detection: 10-20 minutes before main pump
Bot Detection:  Real-time (30 min scans)
Volume Spikes:  < 5 minutes
Market Scans:   15 minutes interval
```

---

## 🚀 Quick Start

### First Time Setup:
```
1. /menu - Mở main menu
2. 🚀 Pump Watch (Auto-Save) - Bật pump detector
3. 🤖 Bot Monitor (70%) - Bật bot monitor
4. 📝 Watchlist - Thêm coins yêu thích
5. 🔔 Bật Monitor - Bật watchlist monitor
```

### Daily Usage:
```
1. Check /status mỗi sáng
2. Review alerts từ đêm qua
3. Quét manual: 🌐 Quét TẤT CẢ Coins
4. Analyze signals: 🔍 Phân Tích Nhanh
5. Trade carefully với signals >= 80%
```

---

## 💡 Tips & Tricks

### Maximize Accuracy:
```
✅ Wait for Layer 3 confirmation
✅ Cross-check với bot monitor
✅ Verify volume is real (not bot)
✅ Check multiple timeframes
✅ Use stop loss always
```

### Avoid False Signals:
```
✅ Ignore Layer 1 only alerts (<60%)
✅ Skip coins với high bot score
✅ Verify 24h volume > 1M USDT
✅ Check overall market trend
✅ Don't trade during low volume hours
```

### Optimize Watchlist:
```
✅ Let auto-save populate quality pumps
✅ Add top 20 coins by market cap
✅ Remove coins with no activity for 7 days
✅ Balance between BTC pairs and alts
✅ Monitor list regularly
```

---

## 📞 Support

**GitHub**: HieuHuynh2348/rsi-mfi-trading-bot
**Platform**: Railway.app (auto-deploy)
**Version**: November 9, 2025 Update

**Latest Features:**
- ✅ Auto-save pump coins (>= 80%)
- ✅ Scan all market (Top 200)
- ✅ Updated keyboards with info
- ✅ 70% bot monitor threshold
- ✅ 3-Layer pump detection

**Status**: 🟢 All systems operational

---

**Happy Trading! 🚀📈**

*Remember: This is technical analysis, not financial advice. Always trade responsibly and use stop losses.*
