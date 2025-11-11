# AI Response JSON Schema

**Version:** 2.2 ENHANCED  
**Model:** Gemini 2.0 Flash  
**Format:** JSON  
**Fields:** 23 total (15 original + 8 new)  
**Updated:** November 11, 2025

## Overview

This document defines the complete JSON schema for the AI response from Gemini 2.0 Flash when performing cryptocurrency trading analysis. The schema is tightly structured to ensure programmatic processing, database storage, and Telegram message formatting.

**New in v2.2:**
- Asset Type Detection (BTC/ETH/CAP_TIERS/MEME)
- Sector Analysis (sector momentum, rotation risk, leadership)
- Correlation Analysis (BTC/ETH strength and direction)
- Fundamental Analysis (project health, tokenomics, centralization)
- Position Sizing Recommendation (dynamic sizing with reasoning)
- Macro Context (conditional BTC or Altcoin specific data)

## Complete JSON Schema

```json
{
  "recommendation": {
    "type": "string",
    "enum": ["BUY", "SELL", "HOLD", "WAIT"],
    "description": "Primary trading recommendation. BUY (long entry), SELL (short entry), HOLD (already in position), WAIT (insufficient confidence or conflicting signals)"
  },
  
  "confidence": {
    "type": "integer",
    "minimum": 0,
    "maximum": 100,
    "description": "Confidence score as percentage (0-100). 0=no confidence, 100=absolute certainty. Typically 60+ for BUY/SELL, <40 for WAIT"
  },
  
  "trading_style": {
    "type": "string",
    "enum": ["scalping", "swing"],
    "description": "Trading style for which this analysis was optimized"
  },
  
  "entry_point": {
    "type": "number",
    "description": "Recommended entry price in USD. Should be specific, not a range. Based on current price, nearest support (buy) or resistance (sell), and institutional zones"
  },
  
  "stop_loss": {
    "type": "number",
    "description": "Stop loss price in USD. For BUY: below support zone (typically -3-5% from entry). For SELL: above resistance zone (typically +3-5% from entry). Respects risk management (max 2% account risk)"
  },
  
  "take_profit": {
    "type": "array",
    "items": {
      "type": "number"
    },
    "minItems": 1,
    "maxItems": 5,
    "description": "Array of take profit targets in USD (usually 3 targets). TP1 (quick 5-10%), TP2 (medium 15-25%), TP3 (extended 30-50%). For scalping: tighter (3-8%), for swing: wider (10-50%)"
  },
  
  "expected_holding_period": {
    "type": "string",
    "pattern": "^[0-9]+ (minute|hour|day|week)s?$",
    "description": "Expected holding time for this trade. Examples: '5 minutes', '2 hours', '3 days', '1 week'. Scalping = hours, Swing = days"
  },
  
  "risk_level": {
    "type": "string",
    "enum": ["LOW", "MEDIUM", "HIGH"],
    "description": "Risk assessment. LOW: <1% drawdown risk, MEDIUM: 1-3%, HIGH: 3-5%+. Based on volatility and position sizing"
  },
  
  "reasoning_vietnamese": {
    "type": "string",
    "minLength": 300,
    "maxLength": 500,
    "description": "Detailed analysis explanation in Vietnamese (300-500 words). Must explain:\n- Why this recommendation\n- Which indicators led to this conclusion\n- Key support/resistance levels\n- Risk/reward ratio\n- Market condition context\n- Any warnings or cautions"
  },
  
  "key_points": {
    "type": "array",
    "items": {
      "type": "string"
    },
    "minItems": 3,
    "maxItems": 8,
    "description": "Critical bullet points supporting the recommendation. Each point should be one sentence and actionable"
  },
  
  "conflicting_signals": {
    "type": "array",
    "items": {
      "type": "string"
    },
    "description": "Array of signals that contradict the main recommendation. Empty array if none. Used to warn traders and lower confidence if many conflicts"
  },
  
  "warnings": {
    "type": "array",
    "items": {
      "type": "string"
    },
    "description": "Critical warnings for the trader. Examples: 'High volatility expected', 'Major resistance near TP3', 'Pump signal detected - high dump risk', 'Low liquidity on tighter timeframes'"
  },
  
  "market_sentiment": {
    "type": "string",
    "enum": ["BULLISH", "BEARISH", "NEUTRAL"],
    "description": "Overall market sentiment for this symbol. Based on volume profile position, smart money bias, and trend direction"
  },
  
  "technical_score": {
    "type": "integer",
    "minimum": 0,
    "maximum": 100,
    "description": "Technical analysis score (0-100). Calculated as weighted sum of: RSI+MFI (15%) + Stoch+RSI (15%) + Volume (10%) + Candles (10%) + Volume Profile (15%) + FVG (10%) + OB (10%) + S/R (10%) + SMC (15%)"
  },
  
  "fundamental_score": {
    "type": "integer",
    "minimum": 0,
    "maximum": 100,
    "description": "Fundamental score (0-100). Based on: volume strength (40%) + liquidity (30%) + market sentiment (30%). Less weight than technical for crypto trading"
  },
  
  // === NEW FIELDS (v2.2 Enhancement) - 8 NEW FIELDS ===
  
  "asset_type": {
    "type": "string",
    "enum": ["BTC", "ETH", "LARGE_CAP_ALT", "MID_CAP_ALT", "SMALL_CAP_ALT", "MEME_COIN"],
    "description": "Detected asset type. BTC/ETH = special analysis, LARGE_CAP (>$10B), MID_CAP ($1B-$10B), SMALL_CAP ($100M-$1B), MEME (<$100M or community). Determines analysis focus and position sizing."
  },
  
  "sector_analysis": {
    "type": "object",
    "description": "Sector classification and momentum (included for altcoins)",
    "properties": {
      "sector": {
        "type": "string",
        "enum": ["LAYER_1", "LAYER_2", "DEFI", "AI", "GAMING", "MEME", "OTHER"],
        "description": "Crypto sector classification"
      },
      "sector_momentum": {
        "type": "string",
        "enum": ["STRONG_BULL", "WEAK_BULL", "NEUTRAL", "WEAK_BEAR", "STRONG_BEAR"],
        "description": "Current sector momentum vs broader market"
      },
      "sector_rotation_risk": {
        "type": "string",
        "enum": ["LOW", "MEDIUM", "HIGH"],
        "description": "Risk of sector rotation away from this sector. HIGH = reduce holding period."
      },
      "sector_leadership": {
        "type": "string",
        "enum": ["SECTOR_LEADER", "SECTOR_AVERAGE", "SECTOR_LAGGARD"],
        "description": "How this asset performs vs peers in sector"
      }
    }
  },
  
  "correlation_analysis": {
    "type": "object",
    "description": "Correlation with major cryptocurrencies",
    "properties": {
      "btc_correlation": {
        "type": "object",
        "properties": {
          "direction": {
            "type": "string",
            "enum": ["STRONG_POSITIVE", "MODERATE_POSITIVE", "WEAK_POSITIVE", "NEUTRAL", "WEAK_NEGATIVE", "MODERATE_NEGATIVE", "STRONG_NEGATIVE"],
            "description": "Direction and strength of correlation with BTC"
          },
          "strength": {
            "type": "number",
            "minimum": 0.0,
            "maximum": 1.0,
            "description": "Correlation coefficient (0.0-1.0)"
          }
        }
      },
      "eth_correlation": {
        "type": "object",
        "description": "Same structure as btc_correlation",
        "properties": {
          "direction": {"type": "string"},
          "strength": {"type": "number"}
        }
      },
      "independent_move_probability": {
        "type": "integer",
        "minimum": 0,
        "maximum": 100,
        "description": "Probability (%) this asset moves independently from BTC/ETH"
      }
    }
  },
  
  "fundamental_analysis": {
    "type": "object",
    "description": "Project fundamentals assessment (altcoins focus)",
    "properties": {
      "project_health_score": {
        "type": "integer",
        "minimum": 0,
        "maximum": 100,
        "description": "Overall project health (0-100). <40 = AVOID, 40-70 = risky, >70 = healthy"
      },
      "tokenomics_quality": {
        "type": "string",
        "enum": ["EXCELLENT", "GOOD", "FAIR", "POOR"],
        "description": "Token distribution, emission schedule, lock-up periods quality"
      },
      "centralization_risk": {
        "type": "string",
        "enum": ["LOW", "MEDIUM", "HIGH"],
        "description": "Risk from team/whale concentration, centralized governance"
      },
      "ecosystem_growth": {
        "type": "string",
        "enum": ["ACCELERATING", "STABLE", "DECLINING"],
        "description": "Network/ecosystem growth trend over last 3 months"
      }
    }
  },
  
  "position_sizing_recommendation": {
    "type": "object",
    "description": "Dynamic position sizing based on asset type and risk factors",
    "properties": {
      "risk_per_trade": {
        "type": "number",
        "minimum": 0.1,
        "maximum": 5.0,
        "description": "Recommended risk % per trade (0.1-5.0%). BTC: 1-2%, alts: 0.5-1.5%, microcaps: 0.1-0.5%"
      },
      "max_position_size_percent": {
        "type": "number",
        "minimum": 0.05,
        "maximum": 5.0,
        "description": "Maximum recommended position as % of portfolio. BTC: 3-5%, ETH: 2-3%, alts: <2%, meme: 0.1%"
      },
      "leverage_suggestion": {
        "type": "integer",
        "minimum": 1,
        "maximum": 10,
        "description": "Suggested leverage multiplier (1=spot, 2-5=moderate, >5=high risk). Default 1 for safety."
      },
      "position_sizing_notes": {
        "type": "string",
        "description": "Reason for recommended size (e.g., 'Reduced 30% due to low liquidity')"
      }
    }
  },
  
  "macro_context": {
    "type": "object",
    "description": "Macro context - conditional based on asset_type",
    "properties": {
      // FOR BTC ONLY:
      "btc_dominance_trend": {
        "type": "string",
        "enum": ["RISING", "FALLING", "STABLE"],
        "description": "BTC dominance trend. Rising = BTC strength, Falling = altseason potential"
      },
      "institutional_flows": {
        "type": "string",
        "enum": ["STRONG_INFLOW", "MODERATE_INFLOW", "NEUTRAL", "MODERATE_OUTFLOW", "STRONG_OUTFLOW"],
        "description": "Institutional buying/selling pressure on BTC"
      },
      "etf_flow_signal": {
        "type": "string",
        "enum": ["BULLISH", "NEUTRAL", "BEARISH"],
        "description": "ETF inflow direction signal for BTC momentum"
      },
      "miner_selling_pressure": {
        "type": "string",
        "enum": ["LOW", "MODERATE", "HIGH"],
        "description": "Miner reserve level and selling pressure. LOW = bullish (fewer sellers)"
      },
      
      // FOR ALTCOINS ONLY:
      "sector_trend": {
        "type": "string",
        "enum": ["LEADING", "FOLLOWING", "LAGGING"],
        "description": "How sector is performing vs rest of market"
      },
      "rotation_risk": {
        "type": "string",
        "enum": ["LOW", "MODERATE", "HIGH"],
        "description": "Risk of sector rotation. HIGH = reduce position, shorten timeframe"
      },
      "liquidity_assessment": {
        "type": "string",
        "enum": ["EXCELLENT", "GOOD", "FAIR", "POOR"],
        "description": "Daily volume and orderbook depth assessment for execution risk"
      }
    }
  },
  
  "historical_analysis": {
    "type": "object",
    "description": "Multi-timeframe historical context analysis (REQUIRED FIELD)",
    "properties": {
      "h1_context": {
        "type": "object",
        "description": "1-hour timeframe context (7 days of data)",
        "properties": {
          "rsi_interpretation": {
            "type": "string",
            "description": "RSI current value vs average. Example: 'Current RSI 45.2 vs avg 52.1 (below average, moderately oversold on 1H)'"
          },
          "volume_trend": {
            "type": "string",
            "description": "Volume direction and implications. Example: 'Increasing (+15% this hour) - Strong buying pressure'"
          },
          "price_position": {
            "type": "string",
            "description": "Current price location in range. Example: 'At 65% of 7-day range, near VAH - watch for resistance'"
          },
          "institutional_insights": {
            "type": "string",
            "description": "Summary of institutional indicators on 1H. Example: 'Volume Profile shows DISCOUNT position with 2 unfilled bullish FVGs nearby - strong support zone'"
          }
        }
      },
      
      "h4_context": {
        "type": "object",
        "description": "4-hour timeframe context (30 days of data)",
        "properties": {
          "rsi_interpretation": {
            "type": "string",
            "description": "RSI analysis on 4H"
          },
          "volume_trend": {
            "type": "string",
            "description": "Volume pattern on 4H"
          },
          "price_position": {
            "type": "string",
            "description": "Price position in 30-day range"
          },
          "institutional_insights": {
            "type": "string",
            "description": "Order blocks, FVGs, Volume Profile insights on 4H"
          }
        }
      },
      
      "d1_context": {
        "type": "object",
        "description": "1-day timeframe context (90 days of data)",
        "properties": {
          "rsi_mfi_correlation": {
            "type": "string",
            "description": "How RSI and MFI align/diverge on daily. Example: 'RSI 55.6 and MFI 60.2 both bullish (strong alignment), high probability of continuation'"
          },
          "long_term_trend": {
            "type": "string",
            "description": "90-day trend direction and strength. Example: 'Bullish trend (+12.45% weekly), 68.5% bullish candles, EMA still pointing up'"
          },
          "volatility_assessment": {
            "type": "string",
            "description": "Volatility level and impact. Example: 'Moderate volatility (2.34% 7-day), suitable for swing trading with 3-5% stops'"
          },
          "institutional_insights": {
            "type": "string",
            "description": "Major institutional levels on daily. Example: 'Strong order block at $42,100 (bullish bias, already tested 2x), POC at $43,200 acting as value area foundation'"
          }
        }
      }
    },
    "required": ["h1_context", "h4_context", "d1_context"]
  }
}
```

## Field Details & Examples

### 1. recommendation
**Purpose:** Primary trading signal  
**Values:** BUY, SELL, HOLD, WAIT

| Value | Meaning | Typical Confidence |
|-------|---------|-------------------|
| **BUY** | Long entry recommended | 70-100% |
| **SELL** | Short entry recommended | 70-100% |
| **HOLD** | Already in position, maintain | N/A |
| **WAIT** | Insufficient signals or conflict | <40% or high divergence |

**Example:**
```json
"recommendation": "BUY"
```

### 2. confidence
**Purpose:** Trust score in the recommendation  
**Range:** 0-100%

| Score | Meaning |
|-------|---------|
| 80-100 | Very high confidence, strong confluence |
| 60-79 | Good confidence, most indicators align |
| 40-59 | Moderate, mixed signals |
| 20-39 | Low confidence, many conflicts |
| 0-19 | Avoid, uncertain market |

**Example:**
```json
"confidence": 78
```

### 3. entry_point
**Purpose:** Specific entry price for the trade  
**Rules:**
- Must be concrete number, not range
- For BUY: Usually at nearest support, VAL, bullish OB, or bullish FVG bottom
- For SELL: Usually at nearest resistance, VAH, bearish OB, or bearish FVG top
- Should respect current price ±3% for swing, ±1% for scalping

**Example:**
```json
"entry_point": 43450.00
```

**Logic:**
- Current price: $43,600
- Nearest support (bullish OB): $43,200
- Entry point: $43,450 (between current and support, creates better risk/reward)

### 4. stop_loss
**Purpose:** Maximum loss exit point  
**Rules:**
- Below support zone for BUY (typically -2% to -5%)
- Above resistance zone for SELL (typically +2% to +5%)
- Must respect risk management (max 2% account risk)
- Usually placed below: Support zone, previous swing low, -1 ATR from entry

**Example:**
```json
"stop_loss": 42950.00
```

**Logic:**
- Entry: $43,450
- Nearest support: $43,200
- Stop loss: $42,950 (below all institutional levels, 1.2% account risk)

### 5. take_profit
**Purpose:** Exit targets for profit-taking  
**Rules:**
- Array of 1-3 targets (usually 3)
- Ascending order (TP1 < TP2 < TP3)
- For BUY: Above entry point at resistance/VAH
- For SELL: Below entry point at support/VAL
- Scalping: 3-8% increments, Swing: 10-50% total

**Example:**
```json
"take_profit": [44100.00, 44600.00, 45200.00]
```

**Logic:**
- Entry: $43,450
- TP1: $44,100 (1.5% gain, quick exit if target reached)
- TP2: $44,600 (2.6% gain, medium term)
- TP3: $45,200 (4% gain, extended hold)

### 6. expected_holding_period
**Purpose:** How long to hold this trade  
**Format:** "[Number] [unit]" where unit = minute(s), hour(s), day(s), week(s)

| Trading Style | Typical Period |
|---------------|----------------|
| Scalping | 5 minutes - 2 hours |
| Swing | 3 days - 1 week |
| Position | 1 month+ |

**Examples:**
```json
"expected_holding_period": "45 minutes"
"expected_holding_period": "4 hours"
"expected_holding_period": "3 days"
"expected_holding_period": "1 week"
```

### 7. risk_level
**Purpose:** Position risk assessment  
**Scale:**
- **LOW:** <1% max drawdown, tight stops, low volatility
- **MEDIUM:** 1-3% drawdown, normal stops, moderate volatility
- **HIGH:** 3-5%+ drawdown, wider stops, high volatility

**Example:**
```json
"risk_level": "MEDIUM"
```

### 8. reasoning_vietnamese
**Purpose:** Detailed explanation in Vietnamese  
**Requirements:**
- Length: 300-500 words
- Language: Vietnamese
- Must explain:
  - Why this recommendation
  - Key indicators supporting the signal
  - Price levels and zones
  - Risk/reward ratio
  - Market context
  - Warnings or cautions

**Example:**
```json
"reasoning_vietnamese": "Tín hiệu BUY được xác nhận từ 3 chỉ báo chính: (1) RSI+MFI đạt consensus BUY với độ mạnh 3/4 trên khung 1H, 4H, 1D. (2) Volume Profile hiển thị giá ở vị trí DISCOUNT (dưới POC $43,200), điều này cho biết giá đang rẻ so với mục độ lịch sử. (3) Order Block bullish gần đây tại $43,100 đã được test 2 lần và không bị phá vỡ, đây là vùng support mạnh...[tiếp tục đến 500 từ]"
```

### 9. key_points
**Purpose:** Quick summary bullets supporting recommendation  
**Requirements:**
- 3-8 points
- One sentence each
- Clear and actionable
- Highest priority signals first

**Example:**
```json
"key_points": [
  "RSI+MFI consensus BUY on 1H, 4H, 1D timeframes (strength 3/4)",
  "Volume Profile DISCOUNT position with strong bullish bias suggests price oversold",
  "Unfilled bullish FVG at $42,500 acts as support magnet",
  "Order block at $43,100 tested 2x without breaking - strong zone",
  "Volume increasing (+15%) indicates accumulation phase starting",
  "Previous D1 candle bullish with small upper wick - continuation likely",
  "Market regime BULLISH - favor longs with stops below support"
]
```

### 10. conflicting_signals
**Purpose:** Signals that contradict the recommendation  
**Usage:** Lower confidence if many conflicts, recommend WAIT if critical conflicts

**Example:**
```json
"conflicting_signals": [
  "Stoch+RSI shows overbought on 4H (cross above 80) - short-term pullback possible",
  "Volume showing declining trend last 4 hours - early momentum loss sign"
]
```

**When to Populate:**
- High RSI on some timeframes vs low on others
- Volume declining while price rising
- Bearish candle wicks while indicators show bullish
- Price near resistance on daily while support breaks on hourly

### 11. warnings
**Purpose:** Critical alerts for trader awareness

**Common Warnings:**
- "High volatility expected (3.5% daily) - use wider stops"
- "Pump signal detected (82% confidence) - high dump risk, reduce position size"
- "Major resistance at $44,500 near TP3 target - expect rejection"
- "Spread between buy/sell is high (>0.5%) - avoid limit orders"
- "Volume declining into support - weak bounce expected"
- "Bitcoin showing bearish divergence - risky to stay in alts long"

**Example:**
```json
"warnings": [
  "Pump signal detected (85% confidence) - prepare for potential dump at $44,500",
  "High volatility expected (3.2% 7-day average) - consider 4-5% stops",
  "Volume declining last 4 hours - watch for support break if volume doesn't rebound"
]
```

### 12. market_sentiment
**Purpose:** Overall bias/direction  
**Values:**
- **BULLISH:** Price rising, volume strong, institutional buyers, SMC bullish
- **BEARISH:** Price falling, volume weak, institutional sellers, SMC bearish
- **NEUTRAL:** Sideways, no clear direction, balanced order flow

**Example:**
```json
"market_sentiment": "BULLISH"
```

### 13. technical_score
**Purpose:** Overall technical health score (0-100)

**Weighting:**
- RSI+MFI (15%): Momentum alignment
- Stoch+RSI (15%): Overbought/oversold zones
- Volume (10%): Buying/selling pressure
- Candle Patterns (10%): Institutional behavior
- Volume Profile (15%): Price fairness
- Fair Value Gaps (10%): Price magnets/support
- Order Blocks (10%): Institutional levels
- Support/Resistance (10%): Traditional zones
- Smart Money Concepts (15%): Structure alignment

**Scoring Ranges:**
- 80-100: Excellent technical setup, high probability
- 60-79: Good setup, reasonable entry
- 40-59: Decent setup, mixed signals
- 20-39: Poor setup, avoid
- 0-19: Terrible setup, don't trade

**Example:**
```json
"technical_score": 76
```

### 14. fundamental_score
**Purpose:** Fundamental/market quality score (0-100)

**Components:**
- Volume strength (40%): Is volume supporting the move?
- Liquidity (30%): Can you enter/exit easily?
- Market sentiment (30%): Overall market health

**Interpretation:**
- 80-100: Strong fundamentals, liquid, healthy market
- 60-79: Good fundamentals, decent liquidity
- 40-59: Mixed fundamentals, moderate liquidity
- <40: Poor fundamentals, risky to trade

**Example:**
```json
"fundamental_score": 68
```

### 15. historical_analysis (CRITICAL FIELD)

This field captures multi-timeframe context comparing current price to historical data.

#### h1_context (1-hour, 7 days)

**rsi_interpretation:**
```
"Current RSI 45.2 vs 7-day average 52.3 (below average). Indicator suggests moderate oversold condition on 1H, potential for bounce or consolidation before continuing bullish trend."
```

**volume_trend:**
```
"Volume increasing (+15% this hour to 125M vs 95M average) - strong buying pressure, suggests accumulation phase starting"
```

**price_position:**
```
"Price at $43,600 = 65% of 7-day range ($41,200-$46,500). Above midpoint, near VAH, potential resistance approaching"
```

**institutional_insights:**
```
"Volume Profile POC at $43,200 (current 1.2% above). Fair Value Gap at $42,500 unfilled (73% fill rate historically). Order Block at $43,100 active - strong support zone with 6/10 strength rating."
```

#### h4_context (4-hour, 30 days)

Similar structure but analyzing 4H data over 30-day period:

```json
{
  "rsi_interpretation": "RSI 52.1 vs 30-day avg 48.9 (above average) - moderate strength in 4H, trending higher",
  "volume_trend": "Volume steady, slight increase over last 2 days - accumulation pattern",
  "price_position": "At 58% of 30-day range - well positioned for continuation",
  "institutional_insights": "Order blocks cluster at $42,800-43,200 create strong support zone. No bearish FVGs between current and support."
}
```

#### d1_context (1-day, 90 days)

Most important for swing trading:

```json
{
  "rsi_mfi_correlation": "RSI 55.6 and MFI 60.2 both bullish and aligned - strong convergence signal, high probability continuation",
  "long_term_trend": "90-day trend: +12.45% bullish, 68.5% bullish candles, EMA 20>50>200 perfectly aligned up - clear uptrend",
  "volatility_assessment": "2.34% daily volatility moderate range - suitable for swing trading with 3-5% stops",
  "institutional_insights": "Major volume profile POC at $42,900 creating value area. Smart Money shows bullish bias 75%, 5 recent BOS confirm continuation structure."
}
```

## Complete Response Example

```json
{
  "recommendation": "BUY",
  "confidence": 78,
  "trading_style": "swing",
  "entry_point": 43450.00,
  "stop_loss": 42950.00,
  "take_profit": [44100.00, 44600.00, 45200.00],
  "expected_holding_period": "3 days",
  "risk_level": "MEDIUM",
  "reasoning_vietnamese": "Tín hiệu BUY được xác nhận từ ba chỉ báo chính: Thứ nhất, RSI+MFI đạt consensus BUY với độ mạnh 3/4 trên ba khung thời gian 1H, 4H, và 1D. RSI hiện tại 45.2 dưới trung bình 52.3 cho thấy điều kiện oversold nhẹ, tạo cơ hội bật lên. Thứ hai, Volume Profile hiển thị giá ở vị trí DISCOUNT (dưới POC $43,200), chỉ ra rằng giá đang rẻ so với mục độ lịch sử và khả năng bật lên cao. Fair Value Gap chưa fill ở $42,500 hoạt động như nam châm giá, có tỷ lệ fill 73% lịch sử. Thứ ba, Order Block bullish gần đây tại $43,100 đã được test 2 lần mà không bị phá vỡ, xác nhận đây là vùng support mạnh. Stochastic+RSI bắt đầu bật lên từ oversold, Volume tăng 15% cho thấy người mua tích lũy. Tuy vậy, Stoch+RSI vẫn ở vùng oversold trên 4H, có thể gây giảm giá ngắn hạn trước khi bật. Khuyến nghị vào tại $43,450, đặt stop dưới support tại $42,950.",
  "key_points": [
    "RSI+MFI consensus BUY với độ mạnh 3/4, RSI oversold nhẹ trên 1H mở cơ hội bật",
    "Volume Profile DISCOUNT position với bias bullish - giá rẻ so với lịch sử",
    "Fair Value Gap bullish chưa fill tại $42,500 hoạt động như support magnet (fill rate 73%)",
    "Order block bullish tại $43,100 test 2 lần không phá vỡ - vùng support mạnh mẽ",
    "Volume tăng 15% - dấu hiệu tích lũy của người mua bắt đầu",
    "Nến D1 trước bullish với wick trên nhỏ - khả năng tiếp tục cao",
    "Thị trường ở chế độ BULL - ưu tiên các tín hiệu lên với stops dưới support"
  ],
  "conflicting_signals": [
    "Stoch+RSI overbought trên 4H (vượt 80) - có thể pullback ngắn hạn trước khi tiếp tục",
    "Volume có dấu hiệu giảm trong 4 giờ gần - lỗi dấu hiệu mất momentum"
  ],
  "warnings": [
    "Tín hiệu Pump phát hiện (85% tin cậy) - chuẩn bị cho khả năng dump tại $44,500",
    "Biến động cao dự kiến (3.2% trung bình 7 ngày) - xem xét stops 4-5%",
    "Volume giảm trong 4 giờ gần - theo dõi break support nếu volume không bật lên"
  ],
  "market_sentiment": "BULLISH",
  "technical_score": 76,
  "fundamental_score": 68,
  "historical_analysis": {
    "h1_context": {
      "rsi_interpretation": "RSI hiện tại 45.2 thấp hơn trung bình 7 ngày 52.3. Cho thấy điều kiện oversold nhẹ trên khung 1H, tạo cơ hội bật lên hoặc consolidate trước khi tiếp tục trend bullish.",
      "volume_trend": "Volume tăng +15% lên 125M so với trung bình 95M. Dấu hiệu áp lực mua mạnh, suggest rằng giai đoạn tích lũy đang bắt đầu.",
      "price_position": "Giá $43,600 = 65% của range 7 ngày ($41,200-$46,500). Ở trên điểm giữa, gần VAH, có khả năng kháng cự trước.",
      "institutional_insights": "Volume Profile POC tại $43,200 (hiện tại 1.2% trên). Fair Value Gap chưa fill tại $42,500 (tỷ lệ fill 73% lịch sử). Order Block bullish tại $43,100 đang hoạt động - vùng support mạnh với rating độ mạnh 6/10."
    },
    "h4_context": {
      "rsi_interpretation": "RSI 52.1 so với trung bình 30 ngày 48.9 (cao hơn). Sức mạnh trung bình trên 4H, trend tăng.",
      "volume_trend": "Volume ổn định, tăng nhẹ trong 2 ngày gần - pattern tích lũy.",
      "price_position": "Ở 58% của range 30 ngày - vị trí tốt để tiếp tục.",
      "institutional_insights": "Order blocks tập trung ở $42,800-43,200 tạo vùng support mạnh. Không có FVG bearish giữa hiện tại và support."
    },
    "d1_context": {
      "rsi_mfi_correlation": "RSI 55.6 và MFI 60.2 cả hai bullish và aligned - tín hiệu hội tụ mạnh, xác suất tiếp tục cao.",
      "long_term_trend": "Trend 90 ngày: +12.45% bullish, 68.5% nến bullish, EMA 20>50>200 hoàn hảo aligned lên - uptrend rõ ràng.",
      "volatility_assessment": "Biến động 2.34% hàng ngày - range vừa phải, phù hợp swing trading với stops 3-5%.",
      "institutional_insights": "Volume profile POC lớn tại $42,900 tạo value area. Smart Money show bias bullish 75%, 5 BOS gần đây xác nhận structure tiếp tục."
    }
  }
}
```

## Database Storage

### Schema in PostgreSQL
```sql
CREATE TABLE analyses (
  id SERIAL PRIMARY KEY,
  user_id INT NOT NULL,
  symbol VARCHAR(20),
  timeframe VARCHAR(5),
  ai_response JSONB NOT NULL,  -- Full JSON stored as-is
  market_snapshot JSONB,       -- Price/indicator snapshot at time of analysis
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  analyzed_at TIMESTAMP,
  status VARCHAR(20),          -- PENDING, WINNING, LOSING, CLOSED
  final_profit_loss FLOAT,
  user_feedback INT            -- 1 (good) or -1 (bad) from user review
);
```

### JSON Validation
All responses are validated against this schema before:
1. Storage in database
2. Display in Telegram
3. Use in historical learning

## API Integration

### Sending to Gemini
```python
prompt = self._build_prompt(data, trading_style, user_id)
response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents=prompt,
    generation_config={
        "temperature": 0.3,      # Low temp = consistent, focused responses
        "max_output_tokens": 3000
    }
)
```

### Processing Response
```python
response_text = response.text
analysis = json.loads(response_text)
# Validate against schema
validate_response(analysis)
# Save to database with user_id for historical learning
db.save_analysis(user_id, symbol, analysis, market_snapshot)
```

## Message Formatting Order

**NEW (v2.0):** Messages sent in this order:
1. **Technical Details** (msg1) - All indicators and institutional analysis
2. **Summary with Entry/TP/SL** (msg2) - Trading recommendation  
3. **Reasoning** (msg3) - Detailed Vietnamese explanation

This order allows users to understand the analysis BEFORE seeing the entry/TP/SL numbers.

---

**Last Updated:** November 11, 2025  
**Maintained by:** RSI+MFI Trading Bot Development Team
