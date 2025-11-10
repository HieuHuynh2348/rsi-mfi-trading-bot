# 📊 WebApp Features Guide

## 🎯 Overview

Trading bot WebApp với 4 tabs chính và tích hợp AI learning system.

---

## 📱 Tabs

### 1️⃣ **Chart Tab** (Default)
Real-time price chart với technical indicators.

**Features:**
- TradingView-style candlestick chart
- Symbol switcher (15 presets + custom)
- Timeframe selector (1m, 5m, 15m, 1h, 4h, 1D)
- Auto-refresh data

### 2️⃣ **Indicators Tab**
Technical indicators dashboard.

**Indicators Displayed:**
- RSI(6) với zone colors
- MFI(6) với zone colors
- Stoch RSI
- Volume Ratio (current vs average)
- Trading Signal (BUY/SELL/HOLD)
- 24h Statistics (High/Low/Volume)

**Color Coding:**
- 🟢 Green: Oversold zone (good for BUY)
- 🔴 Red: Overbought zone (good for SELL)
- 🟡 Yellow: Neutral zone

### 3️⃣ **AI Analysis Tab**
Gemini AI analysis trigger.

**How to Use:**
1. Click "🧠 Analyze with Gemini AI" button
2. Wait 10-20 seconds
3. Receive analysis in Telegram

**What You Get:**
- Recommendation (BUY/SELL/WAIT/HOLD)
- Confidence % (0-100%)
- Entry point price
- Stop loss price
- Take profit targets (TP1, TP2, TP3)
- Risk level (LOW/MEDIUM/HIGH)
- Detailed reasoning in Vietnamese
- Expected holding period

### 4️⃣ **History Tab** ⭐ NEW
View past AI analyses with statistics.

**Features:**

#### **Statistics Cards** (Top Section)
- Total Analyses
- Wins / Losses
- Win Rate %
- Average Profit %
- Average Loss %

#### **Filters**
- Symbol dropdown (all symbols)
- Recommendation filter (BUY/SELL/WAIT)
- Result filter (WIN/LOSS/EXPIRED/PENDING)

#### **History List**
Each analysis card shows:
- Symbol + emoji (🟢 BUY / 🔴 SELL / 🟡 WAIT)
- Timestamp
- Recommendation + Confidence
- Entry / Stop Loss / Take Profit
- Result badge (✅ WIN / ❌ LOSS / ⏱️ EXPIRED)
- **👍/👎 Review buttons** (manual feedback)
- 📄 Details button (full JSON modal)

#### **Advanced Analytics** (Toggle Button)
Click "📊 Advanced Analytics" to see 4 charts:

1. **📈 Win Rate Over Time**
   - Line chart
   - Shows daily win rate %
   - Tracks improvement

2. **🎯 RSI/MFI Heatmap**
   - Bubble chart
   - Win rate by RSI/MFI zones
   - Find best entry conditions
   - Bubble size = sample size

3. **⏰ Best Entry Times**
   - Bar chart
   - Win rate by day of week
   - Identify best trading days

4. **💰 Profit/Loss Distribution**
   - Histogram
   - Frequency of PnL ranges
   - Understand risk/reward

#### **Export CSV** (Button)
Download all history as CSV file with columns:
- Date, Symbol, Recommendation, Confidence
- Entry, Stop Loss, TP1, TP2, TP3
- Result, PnL %, Exit Price, Exit Reason
- Manual Review

---

## 🎨 UI/UX Features

### **Dark Theme**
- Glass morphism effects
- Smooth animations
- Hover effects on all interactive elements

### **Mobile Responsive**
- Optimized for phones (@768px breakpoint)
- Touch-friendly buttons
- Swipeable tabs

### **Real-time Updates**
- Auto-refresh chart data
- Live indicator updates
- WebSocket price tracking (backend)

---

## 🔧 Technical Details

### **Frontend Stack**
- **Chart:** TradingView Lightweight Charts v5.0
- **Analytics:** Chart.js v4.4.1
- **Styling:** Pure CSS (no frameworks)
- **JavaScript:** Vanilla ES6+

### **Backend API**
```
GET  /api/analysis-history?user_id=X&symbol=Y&days=7
POST /api/ai-analysis
POST /api/review-analysis
```

### **Database**
- PostgreSQL on Railway
- JSONB storage for flexibility
- Auto-cleanup (7-day retention)

---

## 📖 Usage Examples

### **Example 1: Quick Analysis**
```
1. Open webapp in Telegram
2. Symbol auto-loads from current chat context
3. Click "AI Analysis" tab
4. Click "Analyze" button
5. Get recommendation in Telegram
```

### **Example 2: Review Past Analyses**
```
1. Click "📊 History" tab
2. See all past analyses with statistics
3. Filter by symbol: "BTCUSDT"
4. Filter by result: "WIN"
5. View only successful BTC trades
```

### **Example 3: Export Trading Journal**
```
1. Go to History tab
2. Click "📥 Export CSV"
3. Open in Excel/Google Sheets
4. Analyze performance offline
```

### **Example 4: Give Feedback**
```
1. Find an analysis in History
2. Click 👍 if prediction was good
3. Click 👎 if prediction was bad
4. AI learns from your feedback
```

### **Example 5: View Analytics**
```
1. History tab → "📊 Advanced Analytics"
2. See win rate trend over time
3. Check which RSI/MFI zones work best
4. Identify best days to trade
5. Understand PnL distribution
```

---

## 🎯 Best Practices

### **For Trading:**
1. Always check multiple timeframes
2. Wait for RSI+MFI alignment
3. Use stop loss always
4. Take partial profits at TP1/TP2
5. Review past analyses to learn patterns

### **For Learning:**
1. Export CSV weekly for offline analysis
2. Review and rate all analyses (👍/👎)
3. Check analytics to find your edge
4. Focus on high win rate setups
5. Avoid patterns with low win rate

### **For Best Results:**
1. Trade symbols you understand
2. Start small position sizes
3. Track ALL trades (wins AND losses)
4. Learn from mistakes via history
5. Use AI as tool, not gospel

---

## 🚀 Advanced Features

### **Universal Patterns** (AI Learning)
AI detects patterns that work across multiple symbols:
```
Example:
"RSI 25-35 + VP DISCOUNT + BULLISH OB"
→ 78.5% win rate across BTC, ETH, BNB
```

### **Market Regime Detection**
AI adjusts strategy based on market condition:
- **BULL Market** → Favor BUY signals, tight stops
- **BEAR Market** → Favor SELL or WAIT
- **SIDEWAYS** → Range trading, buy support/sell resistance

### **Historical Context**
Every new analysis includes:
- Past 7 days win rate for this symbol
- Patterns that worked before
- Patterns that failed
- AI confidence adjustment based on history

---

## 💡 Tips & Tricks

### **Tip 1: Custom Symbols**
```
1. Click symbol dropdown
2. Select "Enter Custom Symbol"
3. Type: "SOLUSDT" → Auto-adds "USDT" if missing
4. Click "Apply"
```

### **Tip 2: Quick Symbol Switch**
Dropdown has 15 most popular symbols:
- BTCUSDT, ETHUSDT, BNBUSDT
- SOLUSDT, XRPUSDT, DOGEUSDT
- ADAUSDT, AVAXUSDT, DOTUSDT
- And more...

### **Tip 3: Filter History**
Combine filters for specific insights:
```
Symbol: ETHUSDT
Recommendation: BUY
Result: WIN
→ Shows only successful ETH longs
```

### **Tip 4: Analytics Insights**
- **High win rate days?** → Trade only those days
- **RSI 30-40 works best?** → Wait for that zone
- **Most losses at 65+ RSI?** → Avoid overbought entries

### **Tip 5: CSV Analysis**
Open exported CSV in Excel:
1. Create pivot table
2. Group by Symbol
3. Calculate win rate per symbol
4. Focus on best performers

---

## 🛠️ Troubleshooting

### **Problem: History không load**
```
Solution:
1. Check internet connection
2. Reload page (Ctrl+R)
3. Clear browser cache
4. Check DATABASE_URL in Railway
```

### **Problem: Analytics không show charts**
```
Solution:
1. Make sure you have >10 analyses
2. Check browser console for errors
3. Verify Chart.js loaded (Network tab)
```

### **Problem: Export CSV fails**
```
Solution:
1. Check if history loaded
2. Disable popup blocker
3. Try different browser
```

### **Problem: Review button không hoạt động**
```
Solution:
1. Check user_id in URL params
2. Verify database connection
3. Check browser console logs
```

---

## 📈 Performance Tips

### **For Fast Loading:**
- Use WiFi instead of mobile data
- Close unused tabs
- Clear cache periodically

### **For Accurate Analytics:**
- Let bot run for 2+ weeks
- Trade at least 20 times
- Review all analyses honestly
- Export and backup data weekly

### **For Best AI:**
- Provide feedback (👍/👎) consistently
- Focus on one strategy
- Trade same symbols regularly
- Let AI learn your preferences

---

## 🎓 Learning Resources

### **Understanding Indicators:**
- **RSI < 30:** Oversold, potential buy
- **RSI > 70:** Overbought, potential sell
- **MFI:** Like RSI but includes volume
- **Stoch RSI:** Faster RSI for quick trades
- **Volume Ratio > 1.5x:** Strong interest

### **Reading Charts:**
- **Green candles:** Price up
- **Red candles:** Price down
- **Long wicks:** Rejection at that level
- **Small bodies:** Indecision

### **Risk Management:**
- Risk max 1-2% per trade
- Stop loss always
- Take profit in stages
- Don't revenge trade

---

## ✅ Checklist: First Use

- [ ] Open webapp from Telegram bot
- [ ] See chart loading
- [ ] Check indicators tab
- [ ] Trigger one AI analysis
- [ ] Wait for Telegram response
- [ ] Go to History tab
- [ ] See your first analysis
- [ ] Click "Advanced Analytics"
- [ ] (After 10+ analyses) Check charts
- [ ] Export CSV to save data
- [ ] Rate an analysis 👍 or 👎

---

## 🎉 Enjoy Trading!

Bot giờ có:
- ✅ Real-time charts
- ✅ AI analysis
- ✅ Full history tracking
- ✅ Performance analytics
- ✅ Pattern learning
- ✅ Market regime detection
- ✅ Manual feedback system
- ✅ CSV export

**Trade smart, trade safe!** 🚀
