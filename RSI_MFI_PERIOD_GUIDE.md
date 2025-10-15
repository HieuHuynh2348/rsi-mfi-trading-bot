# 📊 RSI & MFI Period Configuration Guide

## ✅ Cấu hình hiện tại: Period = 6

```python
RSI_PERIOD = 6  # Chu kỳ RSI
MFI_PERIOD = 6  # Chu kỳ MFI
```

## 🎯 So sánh Period 6 vs Period 14:

### Period 6 (Hiện tại - Fast/Aggressive) 🚀

**Ưu điểm:**
- ✅ Phản ứng nhanh với biến động giá
- ✅ Tín hiệu sớm hơn (early entry)
- ✅ Tốt cho scalping và day trading
- ✅ Bắt được các swing nhỏ
- ✅ Nhiều cơ hội giao dịch hơn

**Nhược điểm:**
- ⚠️ Nhiều false signals (tín hiệu giả)
- ⚠️ Whipsaw thường xuyên hơn
- ⚠️ Cần theo dõi sát hơn
- ⚠️ Stop loss chặt hơn
- ⚠️ Stress cao hơn

**Phù hợp:**
- 📈 Scalping (1-5 phút)
- 📈 Day trading (< 1 ngày)
- 📈 Thị trường trending mạnh
- 📈 Người có thời gian theo dõi
- 📈 Risk tolerance cao

### Period 14 (Standard/Conservative) 🛡️

**Ưu điểm:**
- ✅ Tín hiệu đáng tin cậy hơn
- ✅ Ít false signals
- ✅ Phù hợp swing trading
- ✅ Ít stress
- ✅ Standard trong technical analysis

**Nhược điểm:**
- ⚠️ Tín hiệu chậm hơn (late entry)
- ⚠️ Bỏ lỡ một số cơ hội
- ⚠️ Ít giao dịch hơn
- ⚠️ Có thể vào sau khi trend đã đi một đoạn

**Phù hợp:**
- 📊 Swing trading (vài ngày - vài tuần)
- 📊 Position trading
- 📊 Thị trường ít biến động
- 📊 Người bận, không theo dõi liên tục
- 📊 Risk tolerance thấp

## 📈 Ví dụ thực tế:

### Với RSI Period 6:
```
Time    Price   RSI(6)   Signal
10:00   100     50       NEUTRAL
10:05   102     75       ⬆️ Tăng nhanh
10:10   104     85       🔴 OVERBOUGHT (SELL)
10:15   103     70       ⬇️ Giảm
10:20   101     45       ⚪ NEUTRAL
```
→ Tín hiệu SELL ở 10:10 (sớm, nhanh)

### Với RSI Period 14:
```
Time    Price   RSI(14)  Signal
10:00   100     50       NEUTRAL
10:05   102     55       Tăng chậm
10:10   104     65       ⚪ Vẫn NEUTRAL
10:15   106     75       ⬆️ Tăng
10:20   108     82       🔴 OVERBOUGHT (SELL)
```
→ Tín hiệu SELL ở 10:20 (muộn hơn, nhưng chắc chắn hơn)

## 🎚️ Các Period phổ biến:

| Period | Style | Timeframe | Risk | Signals |
|--------|-------|-----------|------|---------|
| **6** | Very Fast | 1-5m | Very High | +++++ |
| **9** | Fast | 5-15m | High | ++++ |
| **14** | Standard | 15m-1h | Medium | +++ |
| **21** | Slow | 1h-4h | Low | ++ |
| **50** | Very Slow | 4h-1d | Very Low | + |

## 💡 Khuyến nghị cho Period 6:

### 1. Tăng Consensus Strength
```python
MIN_CONSENSUS_STRENGTH = 3  # Hoặc 4 để chắc chắn hơn
```

### 2. Sử dụng Multiple Timeframes
```python
TIMEFRAMES = ['5m', '15m', '1h', '4h']  # Confirm qua nhiều TF
```

### 3. Giảm ngưỡng Overbought/Oversold
```python
RSI_LOWER = 30  # Thay vì 20
RSI_UPPER = 70  # Thay vì 80
```
→ Ít extreme hơn nhưng đáng tin cậy hơn

### 4. Kết hợp với Volume
- Chỉ trade khi volume > trung bình
- Xác nhận với MFI (money flow)

### 5. Stop Loss chặt hơn
- Period 6 → SL 1-2%
- Period 14 → SL 3-5%

## 🔧 Điều chỉnh theo Trading Style:

### Scalping (< 5 phút):
```python
RSI_PERIOD = 6
MFI_PERIOD = 6
TIMEFRAMES = ['1m', '5m', '15m']
MIN_CONSENSUS_STRENGTH = 2
```

### Day Trading (< 1 ngày):
```python
RSI_PERIOD = 6
MFI_PERIOD = 6
TIMEFRAMES = ['5m', '15m', '1h', '4h']
MIN_CONSENSUS_STRENGTH = 3
```

### Swing Trading (vài ngày):
```python
RSI_PERIOD = 14
MFI_PERIOD = 14
TIMEFRAMES = ['1h', '4h', '1d']
MIN_CONSENSUS_STRENGTH = 3
```

### Position Trading (tuần/tháng):
```python
RSI_PERIOD = 21
MFI_PERIOD = 21
TIMEFRAMES = ['4h', '1d', '1w']
MIN_CONSENSUS_STRENGTH = 4
```

## 📊 Backtest Results (Ví dụ):

### BTC/USDT - Period 6:
```
Timeframe: 1 tháng
Signals: 250
Win rate: 52%
Profit factor: 1.3
Max drawdown: -15%
```

### BTC/USDT - Period 14:
```
Timeframe: 1 tháng
Signals: 80
Win rate: 65%
Profit factor: 1.8
Max drawdown: -8%
```

→ Period 6: Nhiều tín hiệu hơn nhưng win rate thấp hơn
→ Period 14: Ít tín hiệu nhưng chất lượng cao hơn

## ⚠️ Lưu ý quan trọng:

1. **Period càng nhỏ → Risk càng cao**
   - Cần risk management tốt
   - Stop loss chặt
   - Position size nhỏ hơn

2. **Kết hợp với Price Action**
   - Support/Resistance
   - Trendlines
   - Candlestick patterns

3. **Volume Confirmation**
   - Tín hiệu với volume cao > tin cậy hơn
   - MFI giúp xác nhận volume

4. **Multiple Timeframe Analysis**
   - Period 6 trên 5m chart
   - Confirm với Period 14 trên 1h chart
   - Trend trên 4h/1d chart

## 🎯 Kết luận:

**Period 6 phù hợp với bạn nếu:**
- ✅ Có thời gian theo dõi liên tục
- ✅ Kinh nghiệm trading tốt
- ✅ Chấp nhận risk cao
- ✅ Thích trading nhiều
- ✅ Scalping/Day trading

**Nên chuyển sang Period 14 nếu:**
- ❌ Bận, không theo dõi thường xuyên
- ❌ Mới bắt đầu
- ❌ Muốn ít stress
- ❌ Swing/Position trading
- ❌ Thích chất lượng hơn số lượng

---

**Hiện tại bot đang dùng Period 6 - Aggressive mode! 🚀**

**Trade carefully and always use stop loss! 💰**
