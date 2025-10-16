# 🔥 VOLUME ANOMALY DETECTION SYSTEM

## ✨ Tính Năng Mới: Phát Hiện Volume Bất Thường

### 🎯 Mục Đích:
Tự động phát hiện và thông báo khi có **volume giao dịch bất thường** trên các coin trong watchlist - dấu hiệu của breakout/breakdown sắp xảy ra!

---

## 📊 Cách Hoạt Động:

### 1. **Volume Detector Engine**
- **File**: `volume_detector.py`
- **Thuật toán**: Statistical anomaly detection
- **Phương pháp**:
  - So sánh volume hiện tại với trung bình 20-50 nến trước
  - Tính Z-score (độ lệch chuẩn)
  - Phát hiện spike khi volume > 2-3x bình thường

### 2. **Multi-Timeframe Scanning**
- Quét đồng thời nhiều timeframe: **5m, 1h, 4h**
- Xác định **STRONG** spike (2+ timeframes) hoặc **MODERATE** (1 timeframe)

### 3. **Auto-Monitoring**
- **Thread riêng** chạy song song với signal monitoring
- Check mỗi **60 giây** (nhanh hơn signal check 5 phút)
- Tự động gửi alert khi phát hiện spike

---

## 🎚️ Volume Sensitivity Levels:

### **LOW (Conservative)**
```python
Volume Multiplier: 3.0x        # Chỉ alert khi volume gấp 3 lần
Min Increase: 200%             # Tăng ít nhất 200%
Lookback: 50 candles           # So sánh với 50 nến
```
**→ Chỉ bắt được spike CỰC MẠNH**

### **MEDIUM (Balanced)** ⭐ Default
```python
Volume Multiplier: 2.5x        # Volume gấp 2.5 lần
Min Increase: 150%             # Tăng ít nhất 150%
Lookback: 30 candles           # So sánh với 30 nến
```
**→ Cân bằng giữa độ nhạy và độ chính xác**

### **HIGH (Aggressive)**
```python
Volume Multiplier: 2.0x        # Volume gấp 2 lần
Min Increase: 100%             # Tăng ít nhất 100%
Lookback: 20 candles           # So sánh với 20 nến
```
**→ Rất nhạy, nhiều alert hơn**

---

## 📱 Commands Mới:

### 1. `/volumescan` - Quét Volume Thủ Công
```
Công dụng: Quét toàn bộ watchlist tìm volume spike
Timeframes: 5m, 1h, 4h
Output: 
  - Summary số coin có spike
  - Chi tiết từng coin
  - Volume ratio, Z-score, price change
```

**Ví dụ:**
```
/volumescan

🔥 VOLUME SPIKE ALERT!

📊 Summary:
• 3 coin(s) with unusual volume
• Sensitivity: MEDIUM
• Time: 14:30:45

🔴 STRONG SIGNALS (2):
  🚨 BTCUSDT - 2 timeframe(s)
  🚨 ETHUSDT - 3 timeframe(s)

🟡 MODERATE SIGNALS (1):
  ⚡ LINKUSDT
```

### 2. `/volumesensitivity [level]` - Thay Đổi Độ Nhạy

**Xem setting hiện tại:**
```
/volumesensitivity

🎯 Volume Detection Sensitivity

Current: MEDIUM

Settings:
• Volume multiplier: 2.5x
• Min increase: 150%
• Lookback period: 30 candles

Available levels:
• low - Only extreme spikes (3x volume)
• medium - Moderate spikes (2.5x volume)
• high - Sensitive (2x volume)

💡 Usage: /volumesensitivity <level>
```

**Thay đổi:**
```
/volumesensitivity high

✅ Sensitivity updated!

Changed from: MEDIUM
Changed to: HIGH

New settings:
• Volume multiplier: 2.0x
• Min increase: 100%
• Lookback: 20 candles

💡 Test with /volumescan
```

### 3. `/monitorstatus` - Cập Nhật Hiển Thị Volume Info
```
🟢 Monitor Status: RUNNING

⏱️ Check interval: 5 min (300s)
📊 Watchlist: 5 coins
💾 Signal history: 12 records

🔔 Auto-notifications: ON
📊 Volume monitoring: 1 min interval
🎯 Volume sensitivity: MEDIUM

💡 Use /stopmonitor to pause
```

---

## 🔔 Auto-Alert System:

### **Dual-Thread Monitoring:**
1. **Signal Thread** (5 min) - RSI/MFI signals
2. **Volume Thread** (1 min) - Volume spikes ⚡ FASTER!

### **Alert Cooldown:**
- Mỗi coin chỉ alert **1 lần / giờ** để tránh spam
- Lưu history trong `watchlist_volume_history.json`

### **Notification Flow:**
```
1. Phát hiện spike
   ↓
2. Gửi Volume Summary (top coins)
   ↓
3. Chi tiết Volume Analysis (ratio, z-score, spike type)
   ↓
4. Full Technical Analysis (RSI, MFI, consensus)
   ↓
5. Chart (multi-timeframe)
```

---

## 📈 Spike Classification:

### **BULLISH_BREAKOUT** 🚀
- Volume spike + Price up > 2%
- Dấu hiệu: Mua mạnh, có thể tăng tiếp

### **BEARISH_BREAKDOWN** ⚠️
- Volume spike + Price down > 2%
- Dấu hiệu: Bán tháo, cẩn thận

### **NEUTRAL_SPIKE** ⚡
- Volume spike nhưng price ít thay đổi
- Dấu hiệu: Tranh chấp mua/bán, chờ xem

---

## 🔧 Technical Details:

### **Volume Metrics Calculated:**
```python
1. Current Volume - Volume nến hiện tại
2. Average Volume - TB của N nến trước
3. Volume Ratio - current / average
4. Volume Increase % - (current - avg) / avg * 100
5. Z-Score - (current - avg) / std_deviation
```

### **Spike Detection Logic:**
```python
is_spike = (
    volume_ratio >= multiplier AND
    volume_increase >= min_percent AND
    z_score >= 2.0  # At least 2 standard deviations
)
```

### **Example Output:**
```
📊 VOLUME ANALYSIS

Symbol: BTCUSDT
Timeframe: 5m

Current Volume: $1.5B
Volume Ratio: 3.2x average
Increase: +220.5%
Z-Score: 4.5σ

Status: 🚀 BULLISH BREAKOUT
Price Change: +3.5%
```

---

## 🚀 Usage Guide:

### **Setup:**
```bash
1. Add coins to watchlist:
   /watch BTC
   /watch ETH
   /watch LINK

2. Start auto-monitor:
   /startmonitor
   
   → Signals check: every 5 min
   → Volume check: every 1 min ⚡

3. Adjust sensitivity (optional):
   /volumesensitivity medium
```

### **Manual Scan:**
```bash
# Quick volume check
/volumescan

# Will scan all watchlist coins across 3 timeframes
# Returns only coins with unusual volume
```

### **Best Practices:**
1. **Start with MEDIUM sensitivity** - Cân bằng tốt
2. **Use HIGH for active trading** - Bắt sóng nhanh
3. **Use LOW for long-term** - Chỉ alert cực mạnh
4. **Combine with RSI/MFI** - Volume + Technical = Perfect!

---

## 📊 Files Created/Modified:

### **New Files:**
1. **volume_detector.py** (370 lines)
   - VolumeDetector class
   - Statistical analysis
   - Multi-timeframe scanning

### **Modified Files:**
1. **watchlist_monitor.py**
   - Added volume monitoring thread
   - Dual-thread architecture
   - Volume alert notifications

2. **telegram_commands.py**
   - `/volumescan` command
   - `/volumesensitivity` command
   - Updated help text

---

## 💡 Pro Tips:

### **🎯 Volume + Price Pattern:**
- **Spike + Strong BUY signal** = 🚀 Entry point
- **Spike + Strong SELL signal** = ⚠️ Exit warning
- **Spike + NEUTRAL** = 😐 Wait for confirmation

### **⏰ Timeframe Strategy:**
- **5m spike** = Short-term scalp
- **1h spike** = Intraday trade
- **4h spike** = Swing position

### **🔥 Strength Levels:**
- **STRONG** (2+ TF) = High confidence
- **MODERATE** (1 TF) = Watch closely

---

## ✅ Deployment Status:

- ✅ Code implemented
- ✅ Tested locally
- ✅ Committed to GitHub
- ✅ Pushed to Railway
- ✅ Auto-deploy in progress

---

## 🎉 Summary:

**Hệ thống giờ có thể:**
1. ✅ Tự động phát hiện volume bất thường
2. ✅ Quét multi-timeframe (5m, 1h, 4h)
3. ✅ Auto-alert mỗi 1 phút (nhanh!)
4. ✅ Phân loại spike (bullish/bearish/neutral)
5. ✅ Gửi đầy đủ analysis + chart
6. ✅ Tùy chỉnh sensitivity (low/medium/high)
7. ✅ Cooldown để tránh spam

**Lợi ích:**
- 🚀 Bắt được breakout sớm
- ⚠️ Cảnh báo breakdown kịp thời
- 📊 Kết hợp volume + technical
- 🎯 Tăng độ chính xác entry/exit

---

**Ngày triển khai**: October 16, 2025
**Status**: ✅ PRODUCTION READY
