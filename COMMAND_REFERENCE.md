# 📋 COMMAND REFERENCE - Inline Keyboard vs Text Commands

## ✅ Commands with Inline Keyboard Buttons

### **Main Menu** (`/menu`)
All these commands have buttons in the main menu:

| Command | Button | Description |
|---------|--------|-------------|
| `/scan` | 📊 Scan Market | Scan all market symbols for signals |
| `/scanwatch` | ⭐ Scan Watchlist | Scan watchlist coins only |
| `/watchlist` | 📝 View Watchlist | View your watchlist |
| `/clearwatch` | 🗑️ Clear Watchlist | Remove all coins from watchlist |
| `/volumescan` | 🔥 Volume Scan | Scan for volume spikes |
| `/volumesensitivity` | 🎯 Volume Settings | Adjust sensitivity (Low/Medium/High) |
| `/startmonitor` | 🔔 Start Monitor | Start auto-notifications |
| `/stopmonitor` | ⏸️ Stop Monitor | Stop auto-notifications |
| `/monitorstatus` | 🔔 Monitor Status | Check monitor status |
| `/top` | 📈 Top Coins | Top 10 volume coins |
| `/status` | 📊 Bot Status | Bot status & settings |
| `/settings` | ⚙️ Settings | View bot settings |
| `/performance` | ⚡ Performance | Scan performance metrics |
| `/help` | ℹ️ Help | Command list (this message) |
| `/about` | ℹ️ About | Bot information |

### **Quick Analysis Menu**
Click "🔍 Quick Analysis" button to get:

| Button | Command Equivalent | Symbol |
|--------|-------------------|--------|
| ₿ BTC | `/BTC` or `/BTCUSDT` | Bitcoin |
| Ξ ETH | `/ETH` or `/ETHUSDT` | Ethereum |
| ₿ BNB | `/BNB` or `/BNBUSDT` | Binance Coin |
| 🔗 LINK | `/LINK` or `/LINKUSDT` | Chainlink |
| ⚪ DOT | `/DOT` or `/DOTUSDT` | Polkadot |
| 🔵 ADA | `/ADA` or `/ADAUSDT` | Cardano |
| 🟣 SOL | `/SOL` or `/SOLUSDT` | Solana |
| ⚫ AVAX | `/AVAX` or `/AVAXUSDT` | Avalanche |
| 🔴 MATIC | `/MATIC` or `/MATICUSDT` | Polygon |

### **Volume Sensitivity Menu**
Click "🎯 Volume Settings" to get:

| Button | Sensitivity | Threshold |
|--------|-------------|-----------|
| 🔴 Low | Low | 3x normal volume |
| 🟡 Medium | Medium | 2.5x normal volume |
| 🟢 High | High | 2x normal volume |

---

## ⌨️ Commands Requiring Text Input

These commands **MUST be typed** (no buttons available because they need parameters):

### **Symbol Analysis**
```
/SYMBOL - Analyze any coin
```
**Examples:**
- `/BTC` - Analyze Bitcoin
- `/ETH` - Analyze Ethereum  
- `/LINK` - Analyze Chainlink
- `/SOLUSDT` - Analyze with full symbol

### **Market Info**
```
/price SYMBOL - Get current price
/24h SYMBOL - Get 24h market data
```
**Examples:**
- `/price BTC` - Get BTC price
- `/24h ETH` - Get ETH 24h stats

### **Technical Indicators**
```
/rsi SYMBOL - RSI indicator only
/mfi SYMBOL - MFI indicator only  
/chart SYMBOL - View candlestick chart
```
**Examples:**
- `/rsi BTC` - BTC RSI across timeframes
- `/mfi ETH` - ETH MFI across timeframes
- `/chart LINK` - LINK candlestick chart

### **Watchlist Management**
```
/watch SYMBOL - Add coin to watchlist
/unwatch SYMBOL - Remove coin from watchlist
```
**Examples:**
- `/watch BTC` - Add Bitcoin to watchlist
- `/unwatch ETH` - Remove Ethereum from watchlist

---

## 🎯 Usage Recommendations

### **For Quick Actions:** Use `/menu` 🎛️
- One-click access to common functions
- No typing required
- Mobile-friendly
- Visual navigation

### **For Specific Symbols:** Type Commands ⌨️
- Analyze any coin instantly: `/SYMBOL`
- Get specific data: `/price`, `/24h`, `/rsi`, `/mfi`
- Manage watchlist: `/watch`, `/unwatch`
- View charts: `/chart SYMBOL`

### **Best Workflow:**
1. **Start with `/menu`** - See all available options
2. **Use Quick Analysis** - For popular coins (BTC, ETH, etc.)
3. **Type `/SYMBOL`** - For other coins
4. **Set up monitoring** - Use buttons to start/stop monitor

---

## 📱 Mobile vs Desktop

### **Mobile Users** 📱
✅ **Use inline keyboards:**
- `/menu` for main navigation
- Quick Analysis for popular coins
- Buttons for monitor control
- Volume sensitivity buttons

### **Desktop/Power Users** 💻
✅ **Mix both:**
- Type `/SYMBOL` for quick analysis
- Use `/menu` when browsing
- Type commands with parameters
- Keyboard shortcuts

---

## 🔄 Command Compatibility Matrix

| Feature | Inline Button | Text Command | Symbol Parameter |
|---------|--------------|--------------|------------------|
| Market Scan | ✅ Yes | ✅ Yes | ❌ No |
| Watchlist Scan | ✅ Yes | ✅ Yes | ❌ No |
| View Watchlist | ✅ Yes | ✅ Yes | ❌ No |
| Clear Watchlist | ✅ Yes | ✅ Yes | ❌ No |
| Volume Scan | ✅ Yes | ✅ Yes | ❌ No |
| Volume Settings | ✅ Yes | ✅ Yes | ❌ No |
| Start Monitor | ✅ Yes | ✅ Yes | ❌ No |
| Stop Monitor | ✅ Yes | ✅ Yes | ❌ No |
| Monitor Status | ✅ Yes | ✅ Yes | ❌ No |
| Top Coins | ✅ Yes | ✅ Yes | ❌ No |
| Bot Status | ✅ Yes | ✅ Yes | ❌ No |
| Settings | ✅ Yes | ✅ Yes | ❌ No |
| Performance | ✅ Yes | ✅ Yes | ❌ No |
| Help | ✅ Yes | ✅ Yes | ❌ No |
| About | ✅ Yes | ✅ Yes | ❌ No |
| **Analyze Symbol** | ✅ Limited* | ✅ Yes | ✅ Yes |
| **Price Check** | ❌ No | ✅ Yes | ✅ Yes |
| **24h Data** | ❌ No | ✅ Yes | ✅ Yes |
| **RSI Only** | ❌ No | ✅ Yes | ✅ Yes |
| **MFI Only** | ❌ No | ✅ Yes | ✅ Yes |
| **View Chart** | ❌ No | ✅ Yes | ✅ Yes |
| **Add to Watchlist** | ❌ No | ✅ Yes | ✅ Yes |
| **Remove from Watchlist** | ❌ No | ✅ Yes | ✅ Yes |

\* Quick Analysis menu only has 9 popular coins (BTC, ETH, BNB, LINK, DOT, ADA, SOL, AVAX, MATIC)

---

## 💡 Pro Tips

### **Fastest Analysis:**
```
/BTC          # Instant BTC analysis (fastest)
/menu → Quick Analysis → ₿ BTC    # Button method
```

### **Custom Coin Analysis:**
```
/DOGE         # Any coin, just type /SYMBOL
/SHIBUSDT     # Works with full symbol too
```

### **Add to Watchlist & Monitor:**
```
1. /watch BTC
2. /watch ETH
3. /menu → 🔔 Start Monitor
4. Bot auto-checks every 5 minutes!
```

### **Volume Spike Hunting:**
```
1. /menu → 🎯 Volume Settings
2. Click 🟢 High (most sensitive)
3. /menu → 🔥 Volume Scan
4. Get instant volume spike alerts!
```

### **One-Time vs Monitoring:**
```
One-time check:    /BTC or /scan
Continuous:        /startmonitor (auto-scans watchlist every 5min)
```

---

## 🎨 Visual Guide

### Main Menu Layout:
```
┌─────────────────────────────────────┐
│         🤖 MAIN MENU               │
├─────────────────────────────────────┤
│  [📊 Scan Market] [⭐ Scan Watchlist]  │
│  [📝 View Watchlist] [🗑️ Clear]       │
│  [🔥 Volume Scan] [🎯 Settings]       │
│  [🔔 Start] [⏸️ Stop]                 │
│  [📈 Top] [🔍 Quick Analysis]         │
│  [📊 Status] [⚙️ Settings]            │
│  [🔔 Monitor] [⚡ Performance]        │
│  [ℹ️ Help] [ℹ️ About]                 │
└─────────────────────────────────────┘
```

### Quick Analysis Menu:
```
┌─────────────────────────────────────┐
│       🔍 Quick Analysis            │
├─────────────────────────────────────┤
│    [₿ BTC] [Ξ ETH] [₿ BNB]         │
│    [🔗 LINK] [⚪ DOT] [🔵 ADA]      │
│    [🟣 SOL] [⚫ AVAX] [🔴 MATIC]    │
│    [🔙 Main Menu]                   │
└─────────────────────────────────────┘
```

### Volume Settings Menu:
```
┌─────────────────────────────────────┐
│      🎯 Volume Sensitivity         │
├─────────────────────────────────────┤
│         [🔥 Scan Now]              │
│    [🔴 Low] [🟡 Med] [🟢 High]     │
│         [🔙 Main Menu]             │
└─────────────────────────────────────┘
```

---

## 📊 Summary

### ✅ **DO use buttons for:**
- ✅ Market scanning
- ✅ Watchlist operations (view, scan, clear)
- ✅ Monitor control (start/stop/status)
- ✅ Volume scanning & settings
- ✅ Bot info (status, settings, performance)
- ✅ Quick analysis of popular coins

### ⌨️ **DO use text commands for:**
- ⌨️ Specific symbol analysis (`/SYMBOL`)
- ⌨️ Price checks (`/price SYMBOL`)
- ⌨️ 24h market data (`/24h SYMBOL`)
- ⌨️ Individual indicators (`/rsi`, `/mfi`, `/chart`)
- ⌨️ Watchlist management (`/watch`, `/unwatch`)
- ⌨️ Any coin not in Quick Analysis menu

---

**Updated:** October 20, 2025  
**Version:** 3.1 - Enhanced Inline Keyboards
