# 📊 Live Chart - Hướng Dẫn Sử Dụng

## 🎯 Tính Năng Chính

### ✅ Đã Triển Khai

1. **Real-time Candlestick Chart**
   - Sử dụng LightweightCharts v5.0 (phiên bản mới nhất)
   - Hiển thị nến Nhật (OHLCV) từ Binance API
   - Volume bars với màu tăng/giảm
   - RSI và MFI indicators

2. **Touch Controls (Mobile Optimized)**
   - ✅ **Pinch to Zoom** - Chụm 2 ngón để zoom in/out
   - ✅ **Pan/Scroll** - Vuốt ngang để xem lịch sử
   - ✅ **Double Tap** - Tap 2 lần để reset zoom về mặc định
   - ✅ **Smooth Scrolling** - Cuộn mượt mà không giật lag

3. **Timeframe Buttons**
   - 5M, 1H, 4H, 1D
   - Click để chuyển timeframe
   - Haptic feedback khi nhấn
   - Active state highlighting

4. **Responsive Design**
   - Tự động điều chỉnh kích thước
   - Debounced resize (không lag)
   - Safe area insets cho notch/island
   - Theme-aware (dark/light)

5. **Error Handling**
   - Console debugging logs
   - Visual error messages
   - Reload button khi lỗi
   - Stack trace cho developers

## 🎨 UI/UX Improvements

### Visual Feedback
- **Button Press** - Scale animation (0.95x)
- **Active State** - Blue highlight + shadow
- **Hover Effect** - Lighter background
- **Loading** - Smooth fade in/out
- **Haptic** - Light feedback on interactions

### Performance
- **Data Sorting** - Backend & frontend validation
- **Timestamp Format** - Unix seconds (LightweightCharts standard)
- **RequestAnimationFrame** - Smooth rendering
- **Debounced Events** - Prevent excessive updates

## 🔧 Technical Details

### LightweightCharts v5.0 API

```javascript
// Chart Creation
chart = LightweightCharts.createChart(container, {
    layout: {
        background: { type: 'solid', color: '#1a1a1a' },
        textColor: '#d1d4dc',
    },
    timeScale: {
        timeVisible: true,
        rightOffset: 5,
        barSpacing: 10,
    },
    handleScroll: {
        mouseWheel: true,
        pressedMouseMove: true,
        horzTouchDrag: true,  // Touch pan
        vertTouchDrag: true,
    },
    handleScale: {
        pinch: true,  // Pinch zoom
        mouseWheel: true,
        axisPressedMouseMove: true,
    },
});

// Add Series (v5 syntax)
candlestickSeries = chart.addSeries(LightweightCharts.CandlestickSeries, {
    upColor: '#26a69a',
    downColor: '#ef5350',
    borderVisible: false,
    wickUpColor: '#26a69a',
    wickDownColor: '#ef5350',
});

volumeSeries = chart.addSeries(LightweightCharts.HistogramSeries, {
    priceFormat: { type: 'volume' },
    priceScaleId: '',
});
```

### Data Format

```javascript
// Candle Data (OHLCV)
{
    time: 1730000000,  // Unix timestamp (seconds)
    open: 50000.00,
    high: 51000.00,
    low: 49500.00,
    close: 50500.00,
}

// Volume Data
{
    time: 1730000000,
    value: 1250000,
    color: '#26a69a80',  // Green for up candle
}
```

### Touch Events

```javascript
// Multi-touch Prevention
container.addEventListener('touchstart', (e) => {
    if (e.touches.length > 1) {
        e.preventDefault();  // Allow pinch zoom
    }
}, { passive: false });

// Double Tap to Reset
let lastTapTime = 0;
container.addEventListener('touchend', (e) => {
    const tapGap = currentTime - lastTapTime;
    if (tapGap < 300) {
        chart.timeScale().fitContent();  // Reset zoom
    }
});
```

## 🐛 Troubleshooting

### Chart không hiển thị nến

**Kiểm tra:**
1. Browser console logs
   ```
   === CHART INITIALIZATION START ===
   LightweightCharts available: true
   📊 Initializing chart...
   ✅ Chart initialized successfully
   ```

2. Data format
   - Timestamp phải là Unix seconds (không phải milliseconds)
   - Data phải sorted theo time tăng dần
   - OHLCV values phải là numbers (không phải strings)

3. Railway logs
   ```
   📅 Candles count: 100
   📅 First: 1730000000 (2024-10-27 10:00:00)
   📅 Last: 1730360000 (2024-10-27 20:00:00)
   ```

### Buttons không bấm được

**Kiểm tra:**
1. CSS conflicts
   - `user-select: none` applied?
   - `-webkit-tap-highlight-color: transparent`?
   - `pointer-events` not blocked?

2. JavaScript errors
   - Check console for exceptions
   - Event listeners attached?

3. Telegram WebApp
   - `tg.expand()` called?
   - `tg.ready()` called?

### Zoom/Pan không hoạt động

**Kiểm tra:**
1. Chart options
   ```javascript
   handleScroll: {
       horzTouchDrag: true,
       vertTouchDrag: true,
   },
   handleScale: {
       pinch: true,
   }
   ```

2. CSS conflicts
   ```css
   #chartContainer {
       touch-action: pan-x pan-y;
   }
   ```

3. Touch events
   - Multi-touch not prevented by parent?
   - `stopPropagation()` not blocking?

## 📱 Mobile Gestures

| Gesture | Action | Feedback |
|---------|--------|----------|
| **Single Tap** | Select candle | Crosshair |
| **Double Tap** | Reset zoom | Haptic (medium) |
| **Pinch** | Zoom in/out | Haptic (light) |
| **Pan Horizontal** | Scroll timeline | Smooth |
| **Pan Vertical** | Scroll price | Smooth |

## 🎯 Best Practices

### Performance
- ✅ Use `requestAnimationFrame` for rendering
- ✅ Debounce resize events (100ms)
- ✅ Throttle API calls (30s auto-refresh)
- ✅ Limit console logs in production

### Data Handling
- ✅ Sort data on backend before sending
- ✅ Validate timestamps (seconds not milliseconds)
- ✅ Convert all numbers to float
- ✅ Check for null/undefined values

### User Experience
- ✅ Show loading spinner during fetch
- ✅ Haptic feedback on interactions
- ✅ Visual feedback on button press
- ✅ Error messages with recovery options

## 🚀 Future Enhancements

### Planned Features
- [ ] Drawing tools (trendlines, rectangles)
- [ ] More indicators (MACD, Bollinger Bands)
- [ ] Multiple chart layouts (split view)
- [ ] Save/load chart settings
- [ ] Export chart as image
- [ ] Price alerts on chart
- [ ] Order book visualization
- [ ] Volume profile

### Technical Improvements
- [ ] WebSocket for real-time updates
- [ ] Service Worker for offline support
- [ ] IndexedDB for data caching
- [ ] Progressive Web App (PWA)
- [ ] Chart preloading
- [ ] Lazy loading for historical data

## 📚 References

- [LightweightCharts Docs](https://tradingview.github.io/lightweight-charts/docs)
- [Telegram WebApp API](https://core.telegram.org/bots/webapps)
- [Binance Klines API](https://binance-docs.github.io/apidocs/spot/en/#kline-candlestick-data)

---

**Version:** 1.0.0  
**Last Updated:** November 9, 2025  
**Chart Library:** LightweightCharts v5.0.0
