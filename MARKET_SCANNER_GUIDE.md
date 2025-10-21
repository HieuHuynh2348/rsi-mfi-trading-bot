# 🌍 MARKET SCANNER - Automatic Extreme RSI/MFI Detection

## ✅ **New Feature: Auto-Scan ALL Binance for Extreme Conditions**

### **Overview:**
Tự động scan **TẤT CẢ** các USDT pairs trên Binance để tìm coins có RSI/MFI **CỰC ĐOAN** (>80 hoặc <20) trên timeframe **1D**.

---

## 🎯 Mục Đích

### **Vấn Đề:**
- Watchlist monitor chỉ theo dõi coins đã thêm vào watchlist
- Bỏ lỡ cơ hội ở các coins CHƯA watch
- Phải manually scan từng coin

### **Giải Pháp:**
**Market Scanner** tự động:
1. ✅ Scan **TẤT CẢ** Binance USDT pairs
2. ✅ Tính RSI & MFI trên timeframe **1D**
3. ✅ **CHỈ GỬI** coins có extreme conditions
4. ✅ Chạy liên tục trong background
5. ✅ Tự động gửi detailed analysis

---

## 📊 Extreme Conditions

### **Overbought (🔴 Potential Sell):**
- RSI 1D **>= 80**
- MFI 1D **>= 80**

### **Oversold (🟢 Potential Buy):**
- RSI 1D **<= 20**
- MFI 1D **<= 20**

---

## 🎮 Commands

### **1. Start Market Scanner:**
```
/startmarketscan
```

**Response:**
```
✅ Market Scanner Started!

🔍 What it does:
   • Scans ALL Binance USDT pairs
   • Checks 1D RSI & MFI
   • Alerts on extreme levels (>80 or <20)

⏱️ Scan interval: 15 minutes
📊 RSI levels: <20 or >80
💰 MFI levels: <20 or >80
🔔 Cooldown: 1 hour per coin

🚀 Scanner running in background...
💡 Use /stopmarketscan to stop
```

---

### **2. Stop Market Scanner:**
```
/stopmarketscan
```

**Response:**
```
⛔ Market Scanner Stopped

🔕 Auto-scanning disabled
💡 Use /startmarketscan to resume
```

---

### **3. Check Scanner Status:**
```
/marketstatus
```

**Response:**
```
🟢 Market Scanner Status: RUNNING

⏱️ Scan interval: 15 min (900s)
📊 RSI levels: 20-80
💰 MFI levels: 20-80
🔔 Alert cooldown: 1 hour
💾 Tracked coins: 12

🔍 Scanning for:
   🟢 Oversold: RSI/MFI < 20
   🔴 Overbought: RSI/MFI > 80

🚀 Scanner active in background
💡 Use /stopmarketscan to stop
```

---

## 🔄 Workflow

### **Step 1: Start Scanner**
```
User: /startmarketscan
Bot: ✅ Scanner started, running every 15 minutes
```

---

### **Step 2: Scanner Loop (Background)**
```
Every 15 minutes:
1. Get all Binance USDT pairs (~500-1000 coins)
2. Scan in parallel (10 threads)
3. Calculate RSI & MFI for 1D
4. Filter extreme coins
5. Send alerts
```

---

### **Step 3: Alert Notification**
```
🔍 MARKET SCAN ALERT

⚡ Found 3 coins with extreme 1D RSI/MFI:

🟢 LINKUSDT
   📊 RSI: 15.6 | MFI: 18.2
   ⚡ RSI Oversold (15.6), MFI Oversold (18.2)

🔴 XRPUSDT
   📊 RSI: 85.3 | MFI: 82.1
   ⚡ RSI Overbought (85.3), MFI Overbought (82.1)

🟢 ADAUSDT
   📊 RSI: 18.9 | MFI: 22.3
   ⚡ RSI Oversold (18.9)

📤 Sending detailed analysis for each coin...
```

---

### **Step 4: Detailed Analysis**
For each extreme coin, bot sends **full multi-timeframe analysis**:

```
💎 #LINKUSDT
🕐 14:35:20

📊 RSI ANALYSIS
📍 Main RSI: 15.64 ❄️
⏮️ Last RSI: 20.40 📉 (-4.76)
💎 Oversold Alert: 16- 🟢🟢

  ├─ 5M: 15.64 🟢 Oversold ↘
  ├─ 1H: 30.38 🔵 Normal ↘
  ├─ 1D: 52.18 🔵 Normal ↗

💰 MFI ANALYSIS
📍 Main MFI: 28.38 ⚖️
⏮️ Last MFI: 37.23 📉 (-8.85)

  ├─ 5M: 28.38 🔵 Normal ↘
  ├─ 1H: 16.88 🟢 Oversold ↘
  ├─ 1D: 52.55 🔵 Normal ↗

🎯 CONSENSUS: NEUTRAL
💵 PRICE: $18.39 (+6.73%)
📊 VOLUME ANALYSIS
...

[Inline Keyboard Buttons]
```

---

## ⚙️ Configuration

### **Scan Interval:**
```python
scan_interval=900  # 15 minutes (900 seconds)
```

**Adjustable values:**
- 5 minutes: `300`
- 10 minutes: `600`
- 15 minutes: `900` ✅ Default
- 30 minutes: `1800`
- 1 hour: `3600`

---

### **Extreme Levels:**
```python
rsi_upper = 80  # Overbought threshold
rsi_lower = 20  # Oversold threshold
mfi_upper = 80  # Overbought threshold
mfi_lower = 20  # Oversold threshold
```

---

### **Cooldown Period:**
```python
cooldown = 3600  # 1 hour per coin
```

**Purpose:** Prevent spam for same coin
- Coin alerted → Wait 1 hour before alerting again
- Avoids duplicate notifications

---

## 🔍 Detection Logic

### **Filter Criteria:**
```python
is_extreme = (
    current_rsi >= 80 or  # Overbought
    current_rsi <= 20 or  # Oversold
    current_mfi >= 80 or  # Overbought
    current_mfi <= 20     # Oversold
)
```

### **Example Matches:**

| Symbol | RSI 1D | MFI 1D | Match? | Reason |
|--------|--------|--------|--------|--------|
| LINKUSDT | 15.6 | 18.2 | ✅ YES | Both oversold |
| BTCUSDT | 55.3 | 60.1 | ❌ NO | Normal range |
| XRPUSDT | 85.3 | 82.1 | ✅ YES | Both overbought |
| ETHUSDT | 18.9 | 45.0 | ✅ YES | RSI oversold |
| ADAUSDT | 60.0 | 81.5 | ✅ YES | MFI overbought |

---

## 📈 Performance

### **Scanning Speed:**
```
Total symbols: ~800 USDT pairs
Parallel threads: 10
Average time per symbol: ~0.3s
Total scan time: ~24 seconds
```

**Optimization:**
- Parallel processing (ThreadPoolExecutor)
- 10 concurrent API calls
- Efficient DataFrame operations
- Caching to reduce API calls

---

### **Resource Usage:**
- **Memory:** ~50MB for data
- **CPU:** Low (mostly I/O wait)
- **Network:** ~800 API calls per scan
- **Binance Rate Limit:** Safe (under 1200/min limit)

---

## 🎯 Use Cases

### **1. Extreme Oversold Hunt (Buy Opportunities):**
```
Scanner finds:
- LINKUSDT: RSI 15.6, MFI 18.2
- ADAUSDT: RSI 18.9, MFI 22.3

→ Potential bounce plays!
```

---

### **2. Extreme Overbought Warning (Sell Signals):**
```
Scanner finds:
- XRPUSDT: RSI 85.3, MFI 82.1
- DOGEUSDT: RSI 88.1, MFI 85.5

→ Potential reversal zones!
```

---

### **3. Divergence Opportunities:**
```
Scanner finds oversold on 1D:
- Check lower timeframes (1H, 5M)
- Look for bullish divergence
- Plan entry strategy
```

---

### **4. Risk Management:**
```
Holding XRPUSDT:
Scanner alerts: RSI 85+, MFI 82+
→ Consider taking profits!
```

---

## 🔔 Alert System

### **Summary Alert:**
```
🔍 MARKET SCAN ALERT

⚡ Found 5 coins with extreme 1D RSI/MFI:

🟢 LINKUSDT
   📊 RSI: 15.6 | MFI: 18.2
   ⚡ RSI Oversold (15.6), MFI Oversold (18.2)

🟢 ADAUSDT
   📊 RSI: 18.9 | MFI: 45.0
   ⚡ RSI Oversold (18.9)

🔴 XRPUSDT
   📊 RSI: 85.3 | MFI: 82.1
   ⚡ RSI Overbought (85.3), MFI Overbought (82.1)

...

📤 Sending detailed analysis for each coin...
```

---

### **Detailed Analysis:**
- Full RSI/MFI analysis
- Multi-timeframe data
- Price & volume info
- 24h impact analysis
- Inline keyboard for quick actions

---

## 💡 Smart Features

### **1. Cooldown System:**
```python
# Prevent spam for same coin
last_alert_time = last_alerts.get(symbol, 0)
if current_time - last_alert_time > 3600:  # 1 hour
    send_alert(symbol)
    last_alerts[symbol] = current_time
```

**Benefits:**
- No duplicate alerts within 1 hour
- Focus on NEW opportunities
- Reduce noise

---

### **2. Parallel Scanning:**
```python
with ThreadPoolExecutor(max_workers=10) as executor:
    futures = [executor.submit(analyze_coin, symbol) for symbol in all_symbols]
    # Process results
```

**Benefits:**
- 10x faster than sequential
- Complete scan in ~24 seconds
- Efficient resource usage

---

### **3. Auto-Recovery:**
```python
try:
    scan_market()
except Exception as e:
    logger.error(f"Scan error: {e}")
    time.sleep(60)  # Wait 1 minute
    continue  # Retry
```

**Benefits:**
- Continues running on errors
- Self-healing
- Reliable operation

---

## 🔐 Safety Features

### **1. Rate Limiting:**
```python
time.sleep(2)  # 2 seconds between detailed analyses
```

**Prevents:**
- Telegram flood limits
- Binance API throttling
- Bot getting banned

---

### **2. Error Handling:**
```python
try:
    result = analyze_coin(symbol)
except Exception as e:
    logger.debug(f"Skipping {symbol}: {e}")
    continue  # Skip to next
```

**Benefits:**
- Single coin error doesn't stop scan
- Graceful degradation
- Logs for debugging

---

### **3. Authorized Access:**
```python
if not check_authorized(message):
    return
```

**Prevents:**
- Unauthorized users
- Spam attacks
- Resource abuse

---

## 📊 Example Session

### **Full Workflow:**

```
User: /startmarketscan

Bot:
✅ Market Scanner Started!
🔍 Scanning ALL Binance USDT pairs
⏱️ Scan interval: 15 minutes
🚀 Scanner running...

[15 minutes later]

Bot:
🔍 MARKET SCAN ALERT
⚡ Found 3 extreme coins:
🟢 LINKUSDT (RSI: 15.6, MFI: 18.2)
🟢 ADAUSDT (RSI: 18.9, MFI: 45.0)
🔴 XRPUSDT (RSI: 85.3, MFI: 82.1)
📤 Sending details...

[Detailed analysis for each]

💎 #LINKUSDT
📊 RSI: 15.64 🟢 Oversold
💰 MFI: 28.38 ⚖️
...

💎 #ADAUSDT
📊 RSI: 18.90 🟢 Oversold
💰 MFI: 45.00 ⚖️
...

💎 #XRPUSDT
📊 RSI: 85.30 🔴 Overbought
💰 MFI: 82.10 🔴 Overbought
...

[15 minutes later - next scan]
[Continue...]
```

---

## 🆚 Comparison

### **Watchlist Monitor vs Market Scanner:**

| Feature | Watchlist Monitor | Market Scanner |
|---------|-------------------|----------------|
| **Scope** | Only watchlist coins | ALL Binance pairs |
| **Count** | ~10-50 coins | ~800+ coins |
| **Timeframe** | Multi-TF (5m, 1h, 1d) | 1D only |
| **Trigger** | Any signal strength | Extreme only (>80/<20) |
| **Interval** | 5 minutes | 15 minutes |
| **Purpose** | Track favorites | Find new opportunities |

---

### **Use Both Together:**

```
Watchlist Monitor:
- Track your portfolio
- Quick 5-minute updates
- All signal strengths

Market Scanner:
- Discover new coins
- Extreme conditions only
- Daily timeframe focus
```

---

## ✅ Summary

### **What's New:**

1. ✅ **MarketScanner class** - New scanner engine
2. ✅ **3 Commands** - /startmarketscan, /stopmarketscan, /marketstatus
3. ✅ **Auto-scanning** - Background thread, runs continuously
4. ✅ **Parallel processing** - 10 threads, fast scanning
5. ✅ **Smart filtering** - Only extreme RSI/MFI (>80/<20)
6. ✅ **Cooldown system** - 1 hour per coin, no spam
7. ✅ **Full analysis** - Detailed alert for each coin

### **How It Works:**

```
1. User: /startmarketscan
2. Scanner starts background thread
3. Every 15 minutes:
   a. Get all USDT pairs (~800)
   b. Scan in parallel (10 threads)
   c. Calculate 1D RSI/MFI
   d. Filter extreme coins
   e. Send summary alert
   f. Send detailed analysis for each
4. Continues until /stopmarketscan
```

### **Benefits:**

- ✅ Never miss extreme opportunities
- ✅ Auto-discover new coins
- ✅ Daily timeframe focus
- ✅ No manual scanning needed
- ✅ Smart spam prevention
- ✅ Parallel processing (fast!)

---

**Date:** October 21, 2025  
**Version:** 4.0 - Market Scanner  
**Status:** ✅ READY FOR DEPLOY  
**Commit:** `364d098`
