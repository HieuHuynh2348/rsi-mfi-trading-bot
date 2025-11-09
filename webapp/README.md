# Live Chart WebApp

## 🌐 Hosted on GitHub Pages (External Resource)

**Live URL:** https://hieuhhuynh2348.github.io/rsi-mfi-trading-bot/webapp/chart.html

## 📊 Features

- ✅ Real-time candlestick charts powered by LightweightCharts v5
- ✅ RSI and MFI indicators
- ✅ Multiple timeframes (5m, 15m, 1h, 4h, 1d)
- ✅ Volume analysis
- ✅ Price change tracking
- ✅ Touch gestures support (pinch zoom, swipe)
- ✅ Dark theme optimized for Telegram
- ✅ AI Analysis tab with Gemini integration

## 🎯 Architecture

### Separation of Concerns:
- **Bot Backend** → Railway (Python Telegram bot)
- **Live Chart Frontend** → GitHub Pages (Static HTML/JS)
- **No conflicts!** → They run independently

### Data Sources (External):
- **Chart Library:** `unpkg.com/lightweight-charts@5.0.0`
- **Market Data:** `api.binance.com/api/v3/klines`
- **Telegram SDK:** `telegram.org/js/telegram-web-app.js`

## 🔗 Integration

The bot sends WebApp buttons with URLs like:
```
https://hieuhhuynh2348.github.io/rsi-mfi-trading-bot/webapp/chart.html?symbol=BTCUSDT&timeframe=1h
```

Users click the button → Opens in Telegram WebApp → Chart loads data directly from Binance API

## 🚀 No Backend Required!

All chart functionality works client-side:
- Fetches data from Binance public API
- Calculates indicators in JavaScript
- No server needed for charts
- Railway only runs the Telegram bot

## 📱 Usage in Telegram

1. Send `/btc` or any crypto command to bot
2. Bot sends message with "📊 View Chart" button
3. Click button → Opens live chart in Telegram
4. Chart loads instantly from GitHub Pages
5. Data fetched directly from Binance

## ✅ Benefits

- ✅ **No Railway conflicts** - Separate hosting
- ✅ **Fast loading** - CDN served
- ✅ **Always available** - GitHub Pages 99.9% uptime
- ✅ **Free hosting** - No costs
- ✅ **Easy updates** - Just push to main branch
