# 📱 Telegram WebApp (Mini App) - Complete Implementation Guide

## 🎯 Mục Tiêu Đã Đạt Được

✅ **Live Chart hiển thị TRONG Telegram** (không mở browser bên ngoài)
✅ **Interactive candlestick chart** với LightWeight Charts
✅ **Real-time price updates** mỗi 30 giây
✅ **Multi-timeframe support** (5M, 1H, 4H, 1D)
✅ **RSI & MFI indicators** hiển thị trực tiếp
✅ **Touch gestures** (pinch zoom, swipe pan)
✅ **Dark theme** matching Telegram interface

---

## 📚 Kiến Thức Nền Tảng

### 1. Telegram WebApp (Mini App) là gì?

Telegram WebApp là **HTML5 applications** chạy TRỰC TIẾP trong Telegram client:

- **Không cần browser bên ngoài** ✅
- **Seamless integration** với Telegram UI
- **Access Telegram APIs** (user info, theme, storage)
- **Native-like experience** (buttons, haptic feedback)
- **Cross-platform** (iOS, Android, Desktop, Web)

### 2. Kiến Trúc Hoạt Động

```
┌─────────────────┐
│  Telegram App   │
│                 │
│  ┌───────────┐  │
│  │ WebView   │  │ ← Renders HTML/JS/CSS
│  │           │  │
│  │ chart.html│  │ ← Your WebApp
│  │           │  │
│  └─────┬─────┘  │
│        │        │
│        ↓        │
│   Telegram SDK  │ ← Provides APIs
└────────┬────────┘
         │
         ↓
    Your Flask API
    (webapp/app.py)
         │
         ↓
    Binance API
```

### 3. Các Loại Launch Methods

Telegram hỗ trợ **7 cách** mở WebApp:

#### ✅ **1. Inline Keyboard Button (Đang dùng)**
```python
from telebot import types

button = types.InlineKeyboardButton(
    "📊 Live Chart",
    web_app=types.WebAppInfo(url="https://your-app.com")
)
```
- **Use case**: Comprehensive analysis, chart viewing
- **Opens in**: Current chat context
- **Access to**: User info, chat type

#### 2. Reply Keyboard Button
```python
keyboard = types.ReplyKeyboardMarkup()
keyboard.add(types.KeyboardButton(
    "Open Chart",
    web_app=types.WebAppInfo(url="https://your-app.com")
))
```
- **Use case**: Persistent quick access
- **Opens in**: Any chat with bot

#### 3. Menu Button
```python
# Via BotFather: /setmenubutton
# Or Bot API:
bot.set_chat_menu_button(
    menu_button=types.MenuButtonWebApp(
        text="Open App",
        web_app=types.WebAppInfo(url="https://your-app.com")
    )
)
```
- **Use case**: Main app launcher
- **Replaces**: Default commands menu

#### 4. Main Mini App (Profile Button)
```
Via @BotFather:
/mybots → Select Bot → Bot Settings → Configure Mini App
```
- **Use case**: Full-fledged standalone app
- **Features**: App Store listing, preview videos

#### 5. Direct Link
```
https://t.me/your_bot/app_name?startapp=param
```
- **Use case**: Shareable links
- **Opens**: Directly in Telegram

#### 6. Inline Mode
```python
bot.answer_inline_query(
    inline_query.id,
    results=[],
    button=types.InlineQueryResultsButton(
        text="Open App",
        web_app=types.WebAppInfo(url="https://your-app.com")
    )
)
```
- **Use case**: Search-based access

#### 7. Attachment Menu
```
Via @BotFather: /setattach
```
- **Use case**: Quick access from any chat
- **Requirements**: Major advertisers only (or test environment)

---

## 🏗️ Implementation Details

### Phần 1: Frontend (webapp/chart.html)

#### 1.1 Required Scripts
```html
<head>
  <!-- Telegram WebApp SDK (REQUIRED) -->
  <script src="https://telegram.org/js/telegram-web-app.js?59"></script>
  
  <!-- LightWeight Charts for candlesticks -->
  <script src="https://unpkg.com/lightweight-charts@4.0.1/dist/lightweight-charts.standalone.production.js"></script>
</head>
```

#### 1.2 Telegram SDK Initialization
```javascript
// Access Telegram WebApp API
const tg = window.Telegram.WebApp;

// IMPORTANT: Tell Telegram app is ready
tg.ready();

// Expand to full height
tg.expand();

// Access user info (if needed)
console.log(tg.initDataUnsafe.user);

// Access theme colors
console.log(tg.themeParams.bg_color);
```

#### 1.3 Core Functions

**a. Chart Initialization**
```javascript
function initChart() {
    const chart = LightweightCharts.createChart(container, {
        layout: {
            background: { color: tg.themeParams.bg_color || '#1E222D' },
            textColor: tg.themeParams.text_color || '#D9D9D9',
        },
        grid: {
            vertLines: { color: '#2B2B43' },
            horzLines: { color: '#363C4E' },
        }
    });
    
    return chart;
}
```

**b. Data Loading**
```javascript
async function loadChartData(timeframe) {
    const url = `/api/chart?symbol=${symbol}&timeframe=${timeframe}`;
    const response = await fetch(url);
    const data = await response.json();
    
    // Update chart
    candlestickSeries.setData(data.candles);
    
    // Update indicators
    document.getElementById('rsi').textContent = data.rsi.toFixed(2);
    document.getElementById('mfi').textContent = data.mfi.toFixed(2);
}
```

**c. Auto-refresh**
```javascript
setInterval(() => {
    loadChartData(currentTimeframe);
}, 30000); // 30 seconds
```

#### 1.4 Touch Gestures
```javascript
chart.applyOptions({
    handleScroll: {
        mouseWheel: true,
        pressedMouseMove: true,
        horzTouchDrag: true,  // Swipe to scroll
        vertTouchDrag: true   // Pinch to zoom
    },
    handleScale: {
        axisPressedMouseMove: true,
        mouseWheel: true,
        pinch: true  // IMPORTANT for mobile
    }
});
```

### Phần 2: Backend (webapp/app.py)

#### 2.1 Flask Setup
```python
from flask import Flask, jsonify, send_file
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # IMPORTANT: Allow WebApp to fetch data

@app.route('/')
def index():
    # Serve HTML file
    chart_path = os.path.join(os.path.dirname(__file__), 'chart.html')
    return send_file(chart_path)
```

#### 2.2 API Endpoint
```python
@app.route('/api/chart')
def get_chart_data():
    symbol = request.args.get('symbol', 'BTCUSDT')
    timeframe = request.args.get('timeframe', '1h')
    
    # Get klines from Binance
    df = binance.get_klines(symbol, timeframe, limit=168)
    
    # Calculate indicators
    df = calculate_rsi(df, RSI_PERIOD)
    df = calculate_mfi(df, MFI_PERIOD)
    
    # Format for LightWeight Charts
    candles = []
    for idx, row in df.iterrows():
        candles.append({
            'time': int(idx.timestamp()),  # Unix timestamp
            'open': float(row['open']),
            'high': float(row['high']),
            'low': float(row['low']),
            'close': float(row['close']),
            'volume': float(row['volume'])
        })
    
    return jsonify({
        'symbol': symbol,
        'timeframe': timeframe,
        'candles': candles,
        'rsi': float(df['rsi'].iloc[-1]),
        'mfi': float(df['mfi'].iloc[-1]),
        'currentPrice': float(df['close'].iloc[-1])
    })
```

#### 2.3 Production Server (Waitress)
```python
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    
    # Use production WSGI server
    from waitress import serve
    serve(app, host='0.0.0.0', port=port, threads=4)
```

### Phần 3: Bot Integration

#### 3.1 Keyboard Creation
```python
def create_chart_keyboard(symbol, webapp_url):
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    
    # WebApp button (opens IN Telegram)
    if webapp_url:
        chart_url = f"{webapp_url}?symbol={symbol}&timeframe=1h"
        keyboard.row(
            types.InlineKeyboardButton(
                "📊 Live Chart (in Telegram)",
                web_app=types.WebAppInfo(url=chart_url)
            )
        )
    
    # TradingView buttons (fallback)
    keyboard.row(
        types.InlineKeyboardButton(
            "📈 TradingView 1H",
            url=get_tradingview_url(symbol, '60')
        )
    )
    
    return keyboard
```

#### 3.2 Auto-detect Railway URL
```python
import os

def get_webapp_url():
    # Railway auto-provides this
    railway_domain = os.getenv("RAILWAY_PUBLIC_DOMAIN", "")
    if railway_domain:
        return f"https://{railway_domain}"
    
    # Fallback to manual config
    return os.getenv("WEBAPP_URL", "")
```

### Phần 4: Deployment

#### 4.1 Requirements
```txt
flask>=2.3.0
flask-cors>=4.0.0
waitress>=2.1.2
importlib-metadata>=4.0.0,<5.0.0
```

#### 4.2 Procfile (Railway)
```
web: python webapp/app.py
```

#### 4.3 Environment Variables
```bash
# Railway auto-provides:
RAILWAY_PUBLIC_DOMAIN=your-app.up.railway.app

# Bot needs:
TELEGRAM_BOT_TOKEN=your_token
BINANCE_API_KEY=your_key
BINANCE_API_SECRET=your_secret
```

---

## 🔧 Advanced Features

### 1. Theme Synchronization
```javascript
// Auto-update when user changes theme
tg.onEvent('themeChanged', () => {
    chart.applyOptions({
        layout: {
            background: { color: tg.themeParams.bg_color },
            textColor: tg.themeParams.text_color
        }
    });
});
```

### 2. Main Button
```javascript
// Show button at bottom of WebApp
tg.MainButton.text = "Close Chart";
tg.MainButton.show();
tg.MainButton.onClick(() => {
    tg.close();
});
```

### 3. Haptic Feedback
```javascript
// When user clicks button
tg.HapticFeedback.impactOccurred('medium');

// When loading complete
tg.HapticFeedback.notificationOccurred('success');

// On error
tg.HapticFeedback.notificationOccurred('error');
```

### 4. Cloud Storage
```javascript
// Save user preferences
tg.CloudStorage.setItem('favorite_timeframe', '4h', (error, saved) => {
    if (saved) console.log('Saved!');
});

// Load preferences
tg.CloudStorage.getItem('favorite_timeframe', (error, value) => {
    if (value) currentTimeframe = value;
});
```

### 5. Full-screen Mode (Bot API 8.0+)
```javascript
// Request fullscreen
tg.requestFullscreen();

// Exit fullscreen
tg.exitFullscreen();

// Listen for changes
tg.onEvent('fullscreenChanged', () => {
    console.log('Fullscreen:', tg.isFullscreen);
});
```

### 6. Safe Area Insets
```javascript
// Respect device notches/navigation bars
const safeTop = tg.safeAreaInset.top;
const safeBottom = tg.safeAreaInset.bottom;

document.body.style.paddingTop = `${safeTop}px`;
document.body.style.paddingBottom = `${safeBottom}px`;
```

---

## 🐛 Common Issues & Solutions

### Issue 1: "Chart không load"
**Nguyên nhân:** CORS not configured
**Fix:**
```python
from flask_cors import CORS
CORS(app)
```

### Issue 2: "Button không xuất hiện"
**Nguyên nhân:** `WEBAPP_URL` không được set
**Fix:**
```python
# Check logs for:
logger.info(f"✅ Using Railway domain: {webapp_url}")
# or
logger.warning("⚠️ No WEBAPP_URL found")
```

### Issue 3: "Timestamp format sai"
**Nguyên nhân:** LightWeight Charts cần Unix timestamp (seconds)
**Fix:**
```python
# NOT milliseconds!
time = int(idx.timestamp())  # ✅ Correct

# NOT this:
time = int(idx.timestamp() * 1000)  # ❌ Wrong
```

### Issue 4: "Chart không responsive trên mobile"
**Nguyên nhân:** Touch gestures not enabled
**Fix:**
```javascript
handleScale: {
    pinch: true  // IMPORTANT!
}
```

### Issue 5: "Development server warning"
**Nguyên nhân:** Using Flask built-in server
**Fix:** Use Waitress (already implemented)

---

## 📊 Testing Checklist

### Local Testing
```bash
# 1. Start Flask server
python webapp/app.py

# 2. Test health endpoint
curl http://localhost:8080/health

# 3. Test chart API
curl "http://localhost:8080/api/chart?symbol=BTCUSDT&timeframe=1h"

# 4. Open in browser (for dev testing)
http://localhost:8080
```

### Production Testing (Railway)

1. **Check Logs:**
```
✅ Binance client initialized
✅ Using Railway domain for WebApp: https://...
✅ Using Waitress production WSGI server
Serving on http://0.0.0.0:8080
```

2. **Test Endpoints:**
```bash
curl https://your-app.up.railway.app/health
curl https://your-app.up.railway.app/api/chart?symbol=BTCUSDT
```

3. **Test in Telegram:**
```
/analyzer BTCUSDT
→ Click 📊 Chart button
→ Click 📊 Live Chart (in Telegram)
→ Chart should open IN Telegram
```

---

## 📚 Resources

### Official Documentation
- **Telegram WebApps**: https://core.telegram.org/bots/webapps
- **Bot API**: https://core.telegram.org/bots/api
- **pyTelegramBotAPI**: https://github.com/eternnoir/pyTelegramBotAPI

### Libraries Used
- **LightWeight Charts**: https://tradingview.github.io/lightweight-charts/
- **Flask**: https://flask.palletsprojects.com/
- **Waitress**: https://docs.pylonsproject.org/projects/waitress/

### Examples
- **pyTelegramBotAPI Mini App**: https://github.com/eternnoir/pyTelegramBotAPI/tree/master/examples/mini_app_web
- **Live Demo**: https://pytelegrambotminiapp.vercel.app

---

## 🎓 Best Practices

### Performance
1. **Lazy load** large datasets
2. **Debounce** user inputs
3. **Cache** API responses (Redis)
4. **Compress** assets (gzip)
5. **Use CDN** for static files

### UX
1. **Match Telegram theme** (dark/light)
2. **Show loading indicators**
3. **Handle errors gracefully**
4. **Provide fallback options**
5. **Test on real devices**

### Security
1. **Validate initData** from Telegram
2. **Sanitize user inputs**
3. **Use HTTPS only**
4. **Implement rate limiting**
5. **Don't expose API keys**

### Accessibility
1. **Respect safe area insets**
2. **Support touch gestures**
3. **Provide haptic feedback**
4. **Use semantic HTML**
5. **Test with screen readers**

---

## 🚀 Future Enhancements

### Short-term
- [ ] WebSocket for real-time updates
- [ ] More chart types (line, area, bar)
- [ ] Drawing tools (trendlines, Fibonacci)
- [ ] Multiple indicators (MACD, Bollinger Bands)

### Medium-term
- [ ] Price alerts directly from WebApp
- [ ] Portfolio tracking
- [ ] Multi-symbol comparison
- [ ] Trade execution integration

### Long-term
- [ ] Social trading features
- [ ] Backtesting tools
- [ ] AI-powered predictions
- [ ] NFT/Web3 integration

---

## 💡 Tips & Tricks

### 1. Debug Mode
```javascript
// Log all Telegram events
['themeChanged', 'viewportChanged', 'mainButtonClicked'].forEach(event => {
    tg.onEvent(event, () => console.log(event));
});
```

### 2. URL Parameters
```javascript
// Get symbol from URL
const params = new URLSearchParams(window.location.search);
const symbol = params.get('symbol') || 'BTCUSDT';
```

### 3. Error Handling
```javascript
try {
    const data = await loadChartData(timeframe);
} catch (error) {
    tg.showAlert(`Error: ${error.message}`);
    tg.HapticFeedback.notificationOccurred('error');
}
```

### 4. Performance Monitoring
```javascript
console.time('chartLoad');
await loadChartData('1h');
console.timeEnd('chartLoad');
// Expected: < 500ms
```

---

## 📞 Support

### Issues?
1. Check Railway logs
2. Test API endpoints
3. Verify environment variables
4. Review test results (TEST_RESULTS_WEBAPP.md)

### Need Help?
- GitHub: https://github.com/eternnoir/pyTelegramBotAPI/issues
- Telegram: @pyTelegramBotAPI
- Docs: https://pytba.readthedocs.io/

---

**Tạo bởi:** AI Assistant  
**Ngày:** November 9, 2025  
**Version:** 1.0.0  
**Status:** ✅ Production Ready
