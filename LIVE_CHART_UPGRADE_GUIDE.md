# 📊 Live Chart Telegram WebApp - Complete Upgrade Guide

**Date:** November 10, 2025  
**Purpose:** Tổng hợp toàn bộ nguồn tham khảo từ TradingView, Binance, OKX để nâng cấp live chart professional

---

## 🎯 Overview

Nâng cấp toàn bộ Telegram WebApp Live Chart dựa trên:
- ✅ **TradingView Lightweight Charts v5.0** - Professional chart library
- ✅ **Binance/OKX UI/UX** - Industry-standard trading interfaces  
- ✅ **TradingView Color Palette** - #131722, #2962FF, #26A69A, #EF5350
- ✅ **Intl.NumberFormat API** - Locale-aware price formatting
- ✅ **Mobile-first Design** - Touch gestures, responsive breakpoints

---

## 📋 Table of Contents

1. [Price Formatting](#price-formatting)
2. [OHLCV Legend Display](#ohlcv-legend)
3. [Crosshair & Tooltip](#crosshair-tooltip)
4. [Volume Display](#volume-display)
5. [Mobile Touch Gestures](#mobile-gestures)
6. [Auto Precision Detection](#auto-precision)
7. [Real-time Updates](#realtime-updates)
8. [Complete Implementation](#implementation)

---

## 1. 💰 Price Formatting {#price-formatting}

### 1.1 Intl.NumberFormat API (BEST PRACTICE)

```javascript
// Get user's locale automatically
const currentLocale = window.navigator.languages[0] || 'en-US';

// Price Formatter với currency
const priceFormatter = new Intl.NumberFormat(currentLocale, {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
    maximumFractionDigits: 8  // Crypto needs more precision
});

// Usage
priceFormatter.format(45678.90);  // → "$45,678.90"
priceFormatter.format(0.00012345); // → "$0.00012345"

// Apply to chart
chart.applyOptions({
    localization: {
        priceFormatter: (price) => priceFormatter.format(price),
    },
});
```

### 1.2 Auto Precision Detection

```javascript
/**
 * Detect precision based on price range
 * BTC: 2 decimals
 * ETH: 2 decimals  
 * Small altcoins: 4-8 decimals
 */
function detectPrecision(price) {
    if (price >= 1000) return 2;      // BTC: $43,250.50
    if (price >= 10) return 3;        // ETH: $3,526.440
    if (price >= 1) return 4;         // BNB: $654.3210
    if (price >= 0.01) return 6;      // DOGE: $0.123456
    return 8;                         // SHIB: $0.00001234
}

// Dynamic precision
candlestickSeries.applyOptions({
    priceFormat: {
        type: 'price',
        precision: detectPrecision(currentPrice),
        minMove: Math.pow(10, -detectPrecision(currentPrice))
    }
});
```

### 1.3 Percentage Formatting

```javascript
const percentFormatter = new Intl.NumberFormat(currentLocale, {
    style: 'percent',
    signDisplay: 'always',  // Always show +/-
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
});

// Usage
percentFormatter.format(0.0234);  // → "+2.34%"
percentFormatter.format(-0.0156); // → "-1.56%"
```

---

## 2. 📊 OHLCV Legend Display {#ohlcv-legend}

### 2.1 TradingView-Style Legend

```javascript
/**
 * Professional legend with OHLCV data
 * Position: Top-left overlay
 * Auto-hide: When crosshair active
 */
function createOHLCVLegend(container, symbol) {
    const legend = document.createElement('div');
    legend.style.cssText = `
        position: absolute;
        left: 12px;
        top: 12px;
        z-index: 1;
        font-size: 12px;
        font-family: 'SF Pro Display', -apple-system, sans-serif;
        line-height: 18px;
        font-weight: 400;
        color: #D1D4DC;
        pointer-events: none;
        transition: opacity 0.2s ease;
    `;
    container.appendChild(legend);

    // Symbol row
    const symbolRow = document.createElement('div');
    symbolRow.style.cssText = `
        font-size: 14px;
        font-weight: 600;
        margin-bottom: 4px;
        letter-spacing: -0.02em;
    `;
    symbolRow.textContent = symbol;
    legend.appendChild(symbolRow);

    // OHLCV row
    const ohlcvRow = document.createElement('div');
    ohlcvRow.style.cssText = `
        font-size: 11px;
        font-variant-numeric: tabular-nums;
        display: flex;
        gap: 12px;
    `;
    legend.appendChild(ohlcvRow);

    return { legend, symbolRow, ohlcvRow };
}

// Update legend on crosshair move
chart.subscribeCrosshairMove(param => {
    if (!param.time || !param.seriesData.get(candlestickSeries)) {
        // Hide legend when no crosshair
        legend.style.opacity = '0.5';
        return;
    }

    legend.style.opacity = '1';
    const data = param.seriesData.get(candlestickSeries);
    
    // Format OHLCV
    const o = formatPrice(data.open);
    const h = formatPrice(data.high);
    const l = formatPrice(data.low);
    const c = formatPrice(data.close);
    const change = ((data.close - data.open) / data.open) * 100;
    const changeStr = change >= 0 ? `+${change.toFixed(2)}%` : `${change.toFixed(2)}%`;
    const changeColor = change >= 0 ? '#26A69A' : '#EF5350';

    ohlcvRow.innerHTML = `
        <span style="color: #787B86;">O</span> ${o}
        <span style="color: #787B86;">H</span> ${h}
        <span style="color: #787B86;">L</span> ${l}
        <span style="color: #787B86;">C</span> ${c}
        <span style="color: ${changeColor};">▲${changeStr}</span>
    `;
});
```

### 2.2 Compact Legend (Mobile)

```javascript
// Mobile: Single line format
// BTCUSDT  O 43250.50  H 45890.12  L 43123.45  C 45678.90  ▲+5.64%

function createCompactLegend(container, symbol) {
    const legend = document.createElement('div');
    legend.style.cssText = `
        position: absolute;
        left: 8px;
        top: 8px;
        right: 8px;
        z-index: 1;
        font-size: 10px;
        font-family: 'SF Pro Display', -apple-system, sans-serif;
        color: #D1D4DC;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        pointer-events: none;
    `;
    container.appendChild(legend);
    return legend;
}
```

---

## 3. 🎯 Crosshair & Tooltip {#crosshair-tooltip}

### 3.1 Professional Crosshair Configuration

```javascript
chart.applyOptions({
    crosshair: {
        mode: LightweightCharts.CrosshairMode.Normal,  // Free movement
        
        // Vertical line (time)
        vertLine: {
            width: 1,
            color: '#758696',      // TradingView gray
            style: 3,              // Dotted (0=solid, 1=dashed, 2=large dashed, 3=dotted)
            labelVisible: true,
            labelBackgroundColor: '#2962FF',  // TradingView blue
        },
        
        // Horizontal line (price)
        horzLine: {
            width: 1,
            color: '#758696',
            style: 3,
            labelVisible: true,
            labelBackgroundColor: '#2962FF',
        },
    },
});
```

### 3.2 Magnet Mode for OHLC

```javascript
// Stick to OHLC values (TradingView behavior)
chart.applyOptions({
    crosshair: {
        mode: LightweightCharts.CrosshairMode.Magnet,  // Snap to candles
    },
});

// OR MagnetOHLC for exact OHLC snapping
chart.applyOptions({
    crosshair: {
        mode: 3,  // LightweightCharts.CrosshairMode.MagnetOHLC
    },
});
```

### 3.3 Floating Tooltip (Advanced)

```javascript
/**
 * Floating tooltip follows crosshair
 * Shows: Symbol, Price, Time, Volume, RSI, MFI
 */
function createFloatingTooltip(container) {
    const tooltip = document.createElement('div');
    tooltip.style.cssText = `
        position: absolute;
        display: none;
        padding: 8px 12px;
        background: rgba(30, 34, 45, 0.95);  /* TradingView panel */
        border: 1px solid #2A2E39;
        border-radius: 4px;
        font-size: 11px;
        font-family: 'SF Pro Display', -apple-system, sans-serif;
        color: #D1D4DC;
        z-index: 10;
        pointer-events: none;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
        backdrop-filter: blur(8px);
    `;
    container.appendChild(tooltip);

    chart.subscribeCrosshairMove(param => {
        if (!param.time || 
            param.point.x < 0 || 
            param.point.y < 0 ||
            param.point.x > container.clientWidth ||
            param.point.y > container.clientHeight) {
            tooltip.style.display = 'none';
            return;
        }

        const data = param.seriesData.get(candlestickSeries);
        const price = data.close;
        const change = ((data.close - data.open) / data.open) * 100;
        const changeColor = change >= 0 ? '#26A69A' : '#EF5350';
        
        tooltip.style.display = 'block';
        tooltip.innerHTML = `
            <div style="font-weight: 600; margin-bottom: 4px;">${symbol}</div>
            <div style="font-size: 16px; font-weight: 600; margin-bottom: 4px;">
                ${formatPrice(price)}
            </div>
            <div style="color: ${changeColor};">
                ${change >= 0 ? '▲' : '▼'} ${Math.abs(change).toFixed(2)}%
            </div>
            <div style="color: #787B86; font-size: 10px; margin-top: 4px;">
                ${param.time}
            </div>
        `;

        // Position tooltip (avoid edges)
        const x = param.point.x;
        const y = param.point.y;
        const margin = 16;
        
        if (x < container.clientWidth / 2) {
            // Left side - tooltip on right
            tooltip.style.left = (x + margin) + 'px';
            tooltip.style.right = 'auto';
        } else {
            // Right side - tooltip on left
            tooltip.style.right = (container.clientWidth - x + margin) + 'px';
            tooltip.style.left = 'auto';
        }
        
        if (y < container.clientHeight / 2) {
            // Top half - tooltip below
            tooltip.style.top = (y + margin) + 'px';
            tooltip.style.bottom = 'auto';
        } else {
            // Bottom half - tooltip above
            tooltip.style.bottom = (container.clientHeight - y + margin) + 'px';
            tooltip.style.top = 'auto';
        }
    });

    return tooltip;
}
```

---

## 4. 📊 Volume Display {#volume-display}

### 4.1 Volume Formatter (K/M/B notation)

```javascript
/**
 * Format volume with compact notation
 * 1,234 → 1.23K
 * 45,678,900 → 45.68M
 * 1,234,567,890 → 1.23B
 */
const volumeFormatter = new Intl.NumberFormat(currentLocale, {
    notation: 'compact',
    compactDisplay: 'short',
    maximumFractionDigits: 2
});

// Usage
volumeFormatter.format(1234);         // → "1.23K"
volumeFormatter.format(45678900);     // → "45.68M"
volumeFormatter.format(1234567890);   // → "1.23B"

// Apply to volume series
volumeSeries.applyOptions({
    priceFormat: {
        type: 'volume',  // Built-in volume formatter
    },
});
```

### 4.2 Volume Histogram Configuration

```javascript
const volumeSeries = chart.addSeries(LightweightCharts.HistogramSeries, {
    color: '#26A69A',              // Default green
    priceFormat: {
        type: 'volume',
    },
    priceScaleId: '',              // Overlay (no separate scale)
    scaleMargins: {
        top: 0.7,                  // Volume at bottom 30%
        bottom: 0,
    },
});

// Color bars based on price movement
function updateVolumeColors(candleData, volumeData) {
    return volumeData.map((vol, i) => ({
        time: vol.time,
        value: vol.value,
        color: candleData[i].close >= candleData[i].open 
            ? '#26A69A'  // Green (up)
            : '#EF5350'  // Red (down)
    }));
}
```

---

## 5. 📱 Mobile Touch Gestures {#mobile-gestures}

### 5.1 Long-Press for Crosshair (300ms)

```javascript
/**
 * Mobile: Long-press to show crosshair
 * Quick tap: Hide crosshair
 */
let longPressTimer;
const LONG_PRESS_DURATION = 300;  // milliseconds

container.addEventListener('touchstart', (e) => {
    longPressTimer = setTimeout(() => {
        // Show crosshair
        chart.applyOptions({
            crosshair: {
                mode: LightweightCharts.CrosshairMode.Normal,
            },
        });
        
        // Haptic feedback (if supported)
        if (window.Telegram?.WebApp?.HapticFeedback) {
            window.Telegram.WebApp.HapticFeedback.impactOccurred('medium');
        }
    }, LONG_PRESS_DURATION);
}, { passive: true });

container.addEventListener('touchend', () => {
    clearTimeout(longPressTimer);
}, { passive: true });

container.addEventListener('touchmove', () => {
    clearTimeout(longPressTimer);
}, { passive: true });
```

### 5.2 Pinch Zoom

```javascript
/**
 * Pinch to zoom chart
 * Already enabled by default in Lightweight Charts
 */
chart.applyOptions({
    handleScale: {
        axisPressedMouseMove: {
            time: true,
            price: true,
        },
        axisDoubleClickReset: {
            time: true,
            price: true,
        },
        mouseWheel: true,
        pinch: true,  // Enable pinch zoom
    },
});
```

### 5.3 Pan Gestures

```javascript
chart.applyOptions({
    handleScroll: {
        mouseWheel: true,
        pressedMouseMove: true,
        horzTouchDrag: true,  // Horizontal pan
        vertTouchDrag: false, // Disable vertical pan (conflicts with scroll)
    },
});
```

---

## 6. 🔧 Auto Precision Detection {#auto-precision}

### 6.1 Dynamic Precision Based on Symbol

```javascript
/**
 * Auto-detect precision from Binance symbol info
 */
async function getSymbolPrecision(symbol) {
    try {
        const response = await fetch(`https://api.binance.com/api/v3/exchangeInfo?symbol=${symbol}`);
        const data = await response.json();
        const symbolInfo = data.symbols[0];
        
        // Price precision from filters
        const priceFilter = symbolInfo.filters.find(f => f.filterType === 'PRICE_FILTER');
        const tickSize = parseFloat(priceFilter.tickSize);
        
        // Count decimal places
        const precision = tickSize.toString().split('.')[1]?.length || 0;
        
        return {
            precision: precision,
            minMove: tickSize,
            priceScale: Math.pow(10, precision)
        };
    } catch (error) {
        console.error('Error fetching precision:', error);
        return { precision: 2, minMove: 0.01, priceScale: 100 };
    }
}

// Apply to chart
const { precision, minMove } = await getSymbolPrecision('BTCUSDT');
candlestickSeries.applyOptions({
    priceFormat: {
        type: 'price',
        precision: precision,
        minMove: minMove
    }
});
```

### 6.2 Formatter Function with Auto Precision

```javascript
/**
 * Smart formatter that adjusts precision dynamically
 */
function createSmartPriceFormatter(symbol) {
    let precision = 2;  // Default
    
    return {
        format: (price) => {
            // Auto-adjust precision based on price
            if (price < 0.01) precision = 8;
            else if (price < 1) precision = 6;
            else if (price < 10) precision = 4;
            else if (price < 1000) precision = 3;
            else precision = 2;
            
            return new Intl.NumberFormat('en-US', {
                style: 'currency',
                currency: 'USD',
                minimumFractionDigits: precision,
                maximumFractionDigits: precision
            }).format(price);
        }
    };
}

// Apply
chart.applyOptions({
    localization: {
        priceFormatter: createSmartPriceFormatter('BTCUSDT').format,
    },
});
```

---

## 7. ⚡ Real-time Updates {#realtime-updates}

### 7.1 Optimized Update Strategy

```javascript
/**
 * Real-time updates with requestAnimationFrame
 * Prevents excessive rendering
 */
let updateScheduled = false;

function scheduleUpdate(newData) {
    if (updateScheduled) return;
    
    updateScheduled = true;
    requestAnimationFrame(() => {
        // Update candle
        candlestickSeries.update(newData.candle);
        
        // Update volume
        volumeSeries.update(newData.volume);
        
        // Update indicators
        rsiSeries.update(newData.rsi);
        mfiSeries.update(newData.mfi);
        
        updateScheduled = false;
    });
}

// WebSocket handler
websocket.onmessage = (event) => {
    const data = JSON.parse(event.data);
    scheduleUpdate(processData(data));
};
```

### 7.2 Batch Updates (Better Performance)

```javascript
/**
 * Batch multiple updates together
 * Update every 100ms instead of every tick
 */
let updateBuffer = [];
let updateTimer;

function bufferUpdate(newData) {
    updateBuffer.push(newData);
    
    if (!updateTimer) {
        updateTimer = setTimeout(() => {
            // Deduplicate by time (keep latest)
            const latestByTime = {};
            updateBuffer.forEach(data => {
                latestByTime[data.time] = data;
            });
            
            // Apply all updates
            Object.values(latestByTime).forEach(data => {
                candlestickSeries.update(data);
            });
            
            updateBuffer = [];
            updateTimer = null;
        }, 100);  // Batch every 100ms
    }
}
```

---

## 8. 🎨 Complete Implementation {#implementation}

### 8.1 Full Chart Initialization

```javascript
/**
 * Professional chart setup with all features
 */
async function initializeChart(container, symbol) {
    // 1. Get symbol precision
    const { precision, minMove } = await getSymbolPrecision(symbol);
    
    // 2. Setup formatters
    const priceFormatter = new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: precision,
        maximumFractionDigits: precision
    });
    
    const volumeFormatter = new Intl.NumberFormat('en-US', {
        notation: 'compact',
        maximumFractionDigits: 2
    });
    
    // 3. Create chart
    const chart = LightweightCharts.createChart(container, {
        layout: {
            background: { color: '#131722' },
            textColor: '#D1D4DC',
            fontSize: 12,
            fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Display", sans-serif',
        },
        grid: {
            vertLines: { color: '#363C4E', style: 0 },
            horzLines: { color: '#363C4E', style: 0 },
        },
        crosshair: {
            mode: LightweightCharts.CrosshairMode.Normal,
            vertLine: {
                color: '#758696',
                width: 1,
                style: 3,
                labelBackgroundColor: '#2962FF',
            },
            horzLine: {
                color: '#758696',
                width: 1,
                style: 3,
                labelBackgroundColor: '#2962FF',
            },
        },
        rightPriceScale: {
            borderColor: '#2A2E39',
            textColor: '#D1D4DC',
        },
        timeScale: {
            borderColor: '#2A2E39',
            textColor: '#D1D4DC',
            timeVisible: true,
            secondsVisible: false,
        },
        localization: {
            priceFormatter: (price) => priceFormatter.format(price),
        },
        handleScale: {
            pinch: true,
            mouseWheel: true,
        },
        handleScroll: {
            horzTouchDrag: true,
            vertTouchDrag: false,
        },
    });
    
    // 4. Add candlestick series
    const candlestickSeries = chart.addSeries(LightweightCharts.CandlestickSeries, {
        upColor: '#26A69A',
        downColor: '#EF5350',
        borderUpColor: '#26A69A',
        borderDownColor: '#EF5350',
        wickUpColor: '#26A69A',
        wickDownColor: '#EF5350',
        priceFormat: {
            type: 'price',
            precision: precision,
            minMove: minMove
        },
    });
    
    // 5. Add volume series
    const volumeSeries = chart.addSeries(LightweightCharts.HistogramSeries, {
        color: '#26A69A',
        priceFormat: {
            type: 'volume',
        },
        priceScaleId: '',
        scaleMargins: {
            top: 0.7,
            bottom: 0,
        },
    });
    
    // 6. Create OHLCV legend
    const { legend, ohlcvRow } = createOHLCVLegend(container, symbol);
    
    // 7. Create floating tooltip
    const tooltip = createFloatingTooltip(container);
    
    // 8. Setup mobile gestures
    setupMobileGestures(container, chart);
    
    // 9. Return API
    return {
        chart,
        candlestickSeries,
        volumeSeries,
        legend,
        tooltip,
        priceFormatter,
        volumeFormatter
    };
}
```

### 8.2 Mobile Responsive Breakpoints

```css
/* Responsive font sizes */
@media (max-width: 567px) {
    :root {
        --chart-font-size: 10px;
        --legend-font-size: 11px;
        --header-font-size: 12px;
    }
}

@media (min-width: 568px) and (max-width: 1023px) {
    :root {
        --chart-font-size: 11px;
        --legend-font-size: 12px;
        --header-font-size: 13px;
    }
}

@media (min-width: 1024px) {
    :root {
        --chart-font-size: 12px;
        --legend-font-size: 13px;
        --header-font-size: 14px;
    }
}
```

---

## 📚 Key References

### TradingView Lightweight Charts
- **GitHub**: https://github.com/tradingview/lightweight-charts
- **Docs**: https://tradingview.github.io/lightweight-charts/
- **Examples**: 
  - Price & Volume: `/website/tutorials/how_to/price-and-volume.js`
  - Legend: `/website/tutorials/how_to/legend.js`
  - Tooltip: `/plugin-examples/src/plugins/tooltip/tooltip.ts`
  - Crosshair: `/src/views/price-axis/crosshair-price-axis-view.ts`
  - Price Formatter: `/src/formatters/price-formatter.ts`
  - Volume Formatter: `/src/formatters/volume-formatter.ts`

### Key Files from Research
1. **price-formatter.ts** - Decimal precision calculation
2. **volume-formatter.ts** - K/M/B notation
3. **crosshair-price-axis-view.ts** - Crosshair rendering
4. **tooltip.ts** - Floating tooltip plugin
5. **legend.js** - OHLCV display patterns
6. **price-and-volume.js** - Volume histogram setup

### MDN Web Docs
- **Intl.NumberFormat**: https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Intl/NumberFormat
- **Touch Events**: https://developer.mozilla.org/en-US/docs/Web/API/Touch_events

---

## ✅ Implementation Checklist

### Phase 1: Price Formatting ⏳
- [ ] Implement Intl.NumberFormat for prices
- [ ] Add auto-precision detection
- [ ] Format percentages with +/- signs
- [ ] Test with various crypto pairs (BTC, ETH, SHIB)

### Phase 2: OHLCV Legend ⏳
- [ ] Create top-left legend overlay
- [ ] Display O/H/L/C with proper formatting
- [ ] Add price change percentage with color
- [ ] Implement auto-hide on crosshair
- [ ] Mobile compact view

### Phase 3: Volume Display ⏳
- [ ] Apply volume formatter (K/M/B)
- [ ] Color bars based on candle direction
- [ ] Position at bottom 30% of chart
- [ ] Test with high volume coins

### Phase 4: Crosshair Enhancement ⏳
- [ ] Update crosshair colors (#758696)
- [ ] Change label background (#2962FF)
- [ ] Test Normal vs Magnet mode
- [ ] Floating tooltip implementation

### Phase 5: Mobile Optimization ⏳
- [ ] 300ms long-press for crosshair
- [ ] Pinch zoom testing
- [ ] Horizontal pan gestures
- [ ] Haptic feedback integration
- [ ] Responsive font sizes

### Phase 6: Real-time Optimization ✅
- [x] requestAnimationFrame updates (already implemented)
- [x] 15s interval (already optimized)
- [ ] Batch update strategy
- [ ] WebSocket reconnection

### Phase 7: Testing & Deployment ⏳
- [ ] Test all timeframes (1m, 5m, 1h, 4h, 1d)
- [ ] Test mobile devices (iOS/Android)
- [ ] Performance profiling
- [ ] Railway deployment
- [ ] User acceptance testing

---

## 🎯 Priority Order

1. **HIGH**: Price Formatting (Intl.NumberFormat) - User-facing critical
2. **HIGH**: OHLCV Legend - Essential trading information
3. **MEDIUM**: Volume Display (K/M/B) - Better readability
4. **MEDIUM**: Crosshair Enhancement - Professional appearance  
5. **LOW**: Floating Tooltip - Nice-to-have
6. **LOW**: Mobile Gestures - Telegram WebApp handles most

---

## 📝 Notes

### Performance Considerations
- Use `requestAnimationFrame` for updates (already implemented ✅)
- Batch updates every 100ms for high-frequency data
- Debounce crosshair move events
- Use CSS transforms for smooth animations

### Browser Compatibility
- Intl.NumberFormat: IE11+ (OK for Telegram WebApp)
- Touch Events: All modern browsers
- Lightweight Charts v5: Modern browsers only

### Telegram WebApp Specifics
- Use `window.Telegram.WebApp.HapticFeedback` for haptics
- Respect safe areas (`env(safe-area-inset-*)`)
- Test in both iOS and Android Telegram

---

**🚀 Ready to implement! Start with Phase 1: Price Formatting**
