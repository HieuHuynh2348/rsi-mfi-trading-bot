# Gemini AI Trading Analysis Prompt Template

**Version:** 2.0  
**Model:** Gemini 2.0 Flash  
**Language:** English (with Vietnamese analysis output)  
**Updated:** November 2025

## Overview

This document contains the complete prompt structure used to generate trading analysis recommendations from the Gemini 2.0 Flash AI model. The prompt is built dynamically in the `_build_prompt()` method of `gemini_analyzer.py` and includes:

1. **Technical Indicators** (Multi-timeframe RSI/MFI, Stochastic+RSI)
2. **Institutional Indicators** (Volume Profile, Fair Value Gaps, Order Blocks, Smart Money Concepts)
3. **Historical Data** (7-day, 30-day, 90-day price/volume/RSI context)
4. **Pump Detection** (3-layer pump signal scoring)
5. **Pattern Recognition** (Market regime, universal patterns from other symbols)
6. **Custom Instructions** (12 important guidelines for analysis)

## Prompt Structure

### Section 1: Trading Style Definition
```
TRADING STYLE: [SCALPING | SWING]
- If scalping: Focus on 1m-5m-15m timeframes, quick entries/exits, tight stop losses
- If swing: Focus on 1h-4h-1D timeframes, position holding 2-7 days, wider stop losses
```

### Section 2: Historical Performance Context (Optional)
```
HISTORICAL PERFORMANCE FOR {SYMBOL} (Last 7 days)

📊 ACCURACY STATISTICS:
  • Total Analyses: {count}
  • Wins: {wins} | Losses: {losses}
  • Win Rate: {win_rate}%
  • Avg Profit: +{avg_profit}% | Avg Loss: {avg_loss}%

✅ WINNING PATTERNS:
  • RSI Range: {range} (avg: {avg})
  • MFI Range: {range} (avg: {avg})
  • Best VP Position: {position}
  • Win Rate in This Setup: {rate}%

❌ LOSING PATTERNS:
  • RSI Range: {range}
  • MFI Range: {range}
  • Problem VP Position: {position}

⚠️ CRITICAL: Use this historical data to:
  1. Adjust confidence based on similar past setups
  2. Warn if current conditions match previous losses
  3. Increase confidence if conditions match previous wins
  4. Suggest WAIT if win rate for this setup is <40%
```

### Section 3: Technical Indicators

#### RSI + MFI Analysis
```
RSI + MFI Analysis:
  1H: RSI=45.2, MFI=52.3, Signal=BUY
  4H: RSI=38.9, MFI=41.1, Signal=NEUTRAL
  1D: RSI=55.6, MFI=60.2, Signal=BUY
  Consensus: BUY (Strength: 3/4)
```

#### Stochastic + RSI Analysis
```
Stochastic + RSI Analysis:
  1H: RSI=45.2, Stoch=38.9, Signal=NEUTRAL
  4H: RSI=38.9, Stoch=35.6, Signal=OVERSOLD
  1D: RSI=55.6, Stoch=62.3, Signal=OVERBOUGHT
  Consensus: WAIT (Strength: 2/4)
```

### Section 4: Pump Signal Analysis
```
🚀 PUMP SIGNAL ANALYSIS

HIGH CONFIDENCE PUMP DETECTED:
  Final Score: 85%
  Layer 1 (5m): 90% - Early detection
  Layer 2 (1h/4h): 82% - Confirmation
  Layer 3 (1D): 78% - Long-term trend
  
  Key Indicators:
  - Volume spike: 3.2x
  - Price change 5m: +8.45%
  - RSI momentum: +15.3
```

Or if no pump:
```
No high-confidence pump signal detected
```

### Section 5: Institutional Indicators (JSON)
```json
{
  "volume_profile": {
    "poc": 42500.00,
    "vah": 43200.00,
    "val": 41800.00,
    "current_position": "VALUE_AREA",
    "distance_to_poc_percent": -1.2,
    "bias": "BULLISH",
    "description": "Price is in VALUE_AREA, slightly below POC. Expect support."
  },
  "fair_value_gaps": {
    "total_bullish_gaps": 5,
    "total_bearish_gaps": 3,
    "unfilled_bullish_gaps": 2,
    "unfilled_bearish_gaps": 1,
    "fill_rate_percent": 73.5,
    "nearest_bullish_fvg": {
      "gap_start": 42100.00,
      "gap_end": 42300.00,
      "distance_percent": -1.5
    },
    "nearest_bearish_fvg": {
      "gap_start": 43500.00,
      "gap_end": 43700.00,
      "distance_percent": 2.1
    }
  },
  "order_blocks": {
    "total_bullish_ob": 8,
    "total_bearish_ob": 5,
    "active_swing_obs": 3,
    "active_internal_obs": 4,
    "mitigation_rate_percent": 45.2,
    "nearest_swing_ob": {
      "level": 42200.00,
      "bias": "BULLISH",
      "strength": 6,
      "distance_percent": -1.2
    }
  },
  "support_resistance": {
    "nearest_support": {
      "level": 42100.00,
      "volume_ratio": 2.8,
      "distance_percent": -1.5,
      "zone_width": 300.00
    },
    "nearest_resistance": {
      "level": 43600.00,
      "volume_ratio": 2.4,
      "distance_percent": 2.3,
      "zone_width": 250.00
    }
  },
  "smart_money_concepts": {
    "swing_trend": "BULLISH",
    "internal_trend": "BULLISH",
    "structure_bias": "BULLISH_ALIGNED",
    "trading_bias": "BUY",
    "bias_confidence": 0.82,
    "recent_bullish_bos": 3,
    "recent_bearish_bos": 1,
    "recent_bullish_choch": 0,
    "recent_bearish_choch": 1,
    "eqh_count": 2,
    "eql_count": 1,
    "swing_highs_count": 5,
    "swing_lows_count": 4,
    "bullish_bias_percent": 75.0,
    "bias_reason": "Aligned swing/internal trends + recent BOS confirmation"
  }
}
```

### Section 6: Volume Analysis
```
💧 VOLUME ANALYSIS
  24h Volume: 2,450,000,000 USDT
  24h Trades: 1,234,567
  Base Volume: 58,234.5 BTC
```

### Section 7: Historical Comparison
```
📈 HISTORICAL COMPARISON (vs Last Week)
Week-over-Week Comparison:
  Price: +12.45% ($40,500 → $45,516)
  Volume: +8.23% change
  RSI: +10.5 points change (35.2 → 45.7)

D1 Previous Candle Analysis:
  Type: 🟢 Bullish
  Open: $44,200.00 | Close: $45,400.00
  High: $45,800.00 | Low: $44,100.00
  Body Size: $1,200.00
  Upper Wick: $400.00 | Lower Wick: $100.00
  Volume: 2,345,678
```

### Section 8: Extended Historical Klines Context

#### 1H Context (7 Days)
```
⏰ KHUNG 1H (7 NGÀY QUA - 168 nến):
  
  📈 Giá:
    - Vùng: $41,200.00 - $46,500.00 (Range: 12.85%)
    - Hiện tại: $43,600.00 (Vị trí: 65.3% của range)
    - Trung bình: $43,200.00
  
  📊 Volume:
    - Trung bình: 95,000,000
    - Hiện tại: 125,000,000 (Tỷ lệ: 1.32x)
    - Xu hướng: INCREASING
  
  🎯 RSI:
    - Trung bình: 52.3
    - Hiện tại: 45.6
    - Dao động: 28.5 - 72.3
  
  📉 Xu hướng 7 ngày:
    - Hướng: BULLISH (+9.45%)
    - Độ biến động: 2.34%
    - Tỷ lệ nến tăng: 68.5% (115/168 nến)

  🏛️ Institutional Indicators (1H - 7 ngày):
    • Volume Profile: POC=$43,200, VAH=$44,500, VAL=$41,800
      Position: VALUE_AREA, Distance from POC: +1.17%
    • Fair Value Gaps: 5 bullish, 2 bearish
      Unfilled: 2 bullish, 1 bearish
      Gap Density: 4.17%
    • Order Blocks: 8 bullish, 3 bearish
      Active: 3 bullish, 1 bearish
      OB Density: 6.55%
    • Smart Money Concepts: Structure Bias=BULLISH (72.5% bullish)
      BOS: 5 bullish / 1 bearish
      CHoCH: 0 bullish / 1 bearish
```

#### 4H Context (30 Days)
```
⏰ KHUNG 4H (30 NGÀY QUA - 180 nến):
  [Similar structure to 1H but with 30-day data and 4H indicators]
```

#### 1D Context (90 Days)
```
⏰ KHUNG 1D (90 NGÀY QUA - 90 nến):
  [Similar structure with 90-day data and 1D indicators]
  Also includes: RSI/MFI correlation, long-term trend, volatility assessment
```

### Section 9: 24H Market Data
```
═══════════════════════════════════════════
📉 24H MARKET DATA
═══════════════════════════════════════════
  Price Change: +5.23%
  24h High: $46,500.00
  24h Low: $41,200.00
  24h Volume: $2,450,000,000 USDT
```

### Section 10: Cross-Symbol Pattern Recognition (Optional)
```
═══════════════════════════════════════════
🌍 CROSS-SYMBOL PATTERN RECOGNITION
═══════════════════════════════════════════

🔮 MARKET REGIME: BULL
  • Confidence: 85%
  • EMA Trend: UP
  • Volatility: MODERATE
  • Volume: HIGH

🎯 REGIME-BASED RECOMMENDATIONS:
  • In BULL regime, favor long entries near support zones
  • Watch for FVG fills for quick scalping opportunities
  • Avoid shorting against the main trend

📊 UNIVERSAL PATTERNS (Work across multiple symbols):
  1. "Price bounces from POC in uptrend" Win Rate: 78% (245 trades)
     • Symbols: BTC, ETH, SOL, AVAX

⚠️ CRITICAL: Adjust your analysis based on market regime:
  - BULL market → Favor BUY signals, tighter stops, look for dips to buy
  - BEAR market → Favor SELL signals, avoid longs unless strong reversal
  - SIDEWAYS → Range trading, buy support / sell resistance
  - If universal patterns match current setup → Increase confidence
```

### Section 11: 12 Important Guidelines
```
IMPORTANT GUIDELINES:

1. Reasoning MUST be in Vietnamese language (300-500 words)

2. Analyze ALL technical indicators systematically:
   - RSI+MFI consensus and individual timeframe signals
   - Stochastic+RSI momentum across timeframes
   - Volume patterns and 24h trading activity
   - Pump detection signals (if >=80%, consider high risk/reward)
   - Previous candle patterns on H4 and D1 (wick analysis, body size, bullish/bearish)
   - HISTORICAL DATA ANALYSIS (CRITICAL)

3. Historical Data Analysis (REQUIRED - Fill historical_analysis in JSON):
   - 1H Context (7 days): Compare current RSI vs average RSI, volume trend, price position
   - 4H Context (30 days): RSI context, volume pattern, price position
   - 1D Context (90 days): RSI/MFI correlation, long-term trend, volatility assessment

4. Candle Pattern Analysis (CRITICAL):
   - D1/H4 previous candles show institutional behavior
   - Large wicks indicate rejection or absorption zones
   - Bullish candles with small upper wicks = continuation potential
   - Bearish candles with long lower wicks = support testing

5. Institutional Indicators (Weight 40%):
   - Volume Profile: Position (PREMIUM/DISCOUNT/VALUE_AREA/AT_POC) + bias
   - Fair Value Gaps: Unfilled gaps as price magnets (high fill_rate = reliable)
   - Order Blocks: Active zones = strong S/R, high mitigation_rate = weaker zones
   - Support/Resistance: High volume_ratio (>2x) = very strong zones
   - Smart Money Concepts: Swing/internal trend alignment + trading bias

6. Weight high-confidence pump signals (>=80%) heavily but note dump risk

7. Be specific with entry/exit points based on current price and institutional zones

8. Identify conflicting signals between different timeframes and indicator types explicitly

9. Adjust recommendations based on trading style:
   - Scalping: Tight stops (1-2%), quick 3-5% targets, 1-4 hour holding, focus on 4H FVG/OB
   - Swing: Wider stops (3-5%), 10-20% targets, 3-7 day holding, focus on 1D Volume Profile/SMC

10. Consider historical trends - strong week-over-week growth is bullish indicator

11. Be conservative - if major conflicting signals exist, recommend WAIT

12. Scoring methodology:
    - Technical score = RSI+MFI (15%) + Stoch+RSI (15%) + Volume (10%) + Candles (10%) 
                       + Volume Profile (15%) + FVG (10%) + OB (10%) + S/R (10%) + SMC (15%)
    - Fundamental score = volume strength (40%) + liquidity (30%) + market sentiment (30%)
```

### Section 12: JSON Response Format Request
```
Return ONLY valid JSON with the following structure:
{
  "recommendation": "BUY" | "SELL" | "HOLD" | "WAIT",
  "confidence": 0-100,
  "trading_style": "scalping" | "swing",
  "entry_point": <price in USD>,
  "stop_loss": <price in USD>,
  "take_profit": [<target1>, <target2>, <target3>],
  "expected_holding_period": "X hours/days",
  "risk_level": "LOW" | "MEDIUM" | "HIGH",
  "reasoning_vietnamese": "Chi tiết phân tích bằng tiếng Việt (300-500 từ)",
  "key_points": ["Point 1", "Point 2", ...],
  "conflicting_signals": ["Signal 1", "Signal 2", ...] or [],
  "warnings": ["Warning 1", ...] or [],
  "market_sentiment": "BULLISH" | "BEARISH" | "NEUTRAL",
  "technical_score": 0-100,
  "fundamental_score": 0-100,
  "historical_analysis": {
    "h1_context": {
      "rsi_interpretation": "...",
      "volume_trend": "...",
      "price_position": "...",
      "institutional_insights": "..."
    },
    "h4_context": {...},
    "d1_context": {...}
  }
}
```

## Key Features

### Dynamic Content
The prompt is built dynamically based on:
- Symbol and current market data
- Available indicator data
- Historical performance (if user has 7+ days of history)
- Market regime and pattern recognition results
- Pump detector signals
- Trading style (scalping vs swing)

### AI Guidance
The prompt explicitly tells the AI model to:
1. Analyze all indicators in a systematic way
2. Weight institutional indicators heavily (40%)
3. Use historical data to adjust confidence
4. Identify conflicting signals explicitly
5. Provide Vietnamese reasoning for Asian traders
6. Return structured JSON for programmatic processing

### Output Language
- **Prompt Language:** English (for Gemini comprehension)
- **Analysis Output:** Vietnamese (for end-user understanding)
- **Reasoning:** 300-500 Vietnamese words explaining the analysis

## Integration with Code

### In `gemini_analyzer.py`
```python
def _build_prompt(self, data: Dict, trading_style: str = 'swing', user_id: Optional[int] = None) -> str:
    """Build Gemini prompt from collected data with historical learning"""
    # Builds all sections above into a single prompt string
    # Called by analyze() method before sending to Gemini API
```

### In `telegram_commands.py`
The analysis is sent to Telegram in 3 messages via `format_response()`:
1. **Technical Details** - All indicators and analysis
2. **Summary with Entry/TP/SL** - Trading recommendation
3. **Reasoning** - Detailed Vietnamese explanation

## Prompt Size
- **Typical:** 3,000-4,500 tokens
- **With Full History:** 4,500-6,000 tokens
- **With Pattern Recognition:** 5,000-7,000 tokens

## Version History
- **v2.0** (Nov 2025): Added institutional indicators JSON, pattern recognition, multi-timeframe historical analysis
- **v1.5** (Oct 2025): Added historical performance context, candle pattern analysis
- **v1.0** (Sep 2025): Initial version with RSI/MFI and Stoch+RSI analysis

---

**Last Updated:** November 11, 2025  
**Maintained by:** RSI+MFI Trading Bot Development Team
