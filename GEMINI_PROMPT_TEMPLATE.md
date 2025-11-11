# Gemini AI Trading Analysis Prompt Template

**Version:** 2.2 ENHANCED  
**Model:** Gemini 2.0 Flash  
**Language:** English (with Vietnamese analysis output)  
**Updated:** November 11, 2025  
**Enhancement:** Asset Type Detection + BTC Macro + Altcoin Correlation + Dynamic Risk

## Overview

This document contains the complete prompt structure used to generate trading analysis recommendations from the Gemini 2.0 Flash AI model. The prompt is built dynamically in the `_build_prompt()` method of `gemini_analyzer.py` and includes:

1. **Asset Type Detection** (BTC vs ETH vs Large/Mid/Small Cap Alts vs Meme Coins)
2. **Technical Indicators** (Multi-timeframe RSI/MFI, Stochastic+RSI)
3. **Institutional Indicators** (Volume Profile, Fair Value Gaps, Order Blocks, Smart Money Concepts)
4. **Historical Data** (7-day, 30-day, 90-day price/volume/RSI context)
5. **Pump Detection** (3-layer pump signal scoring)
6. **BTC Macro Analysis** (Dominance, Institutional Flows, ETF, Whale, Miner - for BTC only)
7. **Altcoin Correlation** (BTC/ETH Correlation, Sector Analysis, Project Health - for altcoins only)
8. **Dynamic Risk Adjustments** (Asset-specific position sizing, risk multipliers)
9. **Pattern Recognition** (Market regime, universal patterns from other symbols)
10. **26 Enhanced Guidelines** (Including BTC-specific, Altcoin-specific, Universal enhanced)

## Prompt Structure

### Section 0: Asset Type Detection
```
🎯 ASSET TYPE DETECTION: {asset_type}
• BTC: Bitcoin - Market leader, institutional focus, macro correlations
• ETH: Ethereum - Smart contract platform, DeFi correlation, network metrics  
• LARGE_CAP_ALT: Top 10 coins (>$10B) - Lower risk, institutional interest
• MID_CAP_ALT: Rank 11-50 ($1B-$10B) - Moderate risk, sector leadership potential
• SMALL_CAP_ALT: Rank 51-200 ($100M-$1B) - High risk, high growth potential
• MEME_COIN: Community-driven (<$100M) - Extreme risk, pump/dump cycles

ANALYSIS FOCUS BASED ON ASSET TYPE:
  • BTC: Institutional flows, dominance trends, macro correlations (Fed, DXY, stocks)
  • ETH: Network activity, DeFi TVL, staking metrics, layer 2 competition
  • LARGE_CAP: Sector leadership, institutional adoption, network effects
  • MID/SMALL_CAP: Project fundamentals, correlation dependency, liquidity risks
  • MEME: Pure technicals, community sentiment, volume spikes, dump probability

PURPOSE: Dynamically adjust prompt depth and focus based on asset characteristics
```

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

### Section 11: Cross-Symbol Pattern Recognition
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

### Section 10A: BTC Macro Analysis (Conditional - BTC Only)
```
═══════════════════════════════════════════
🏛️ BITCOIN MACRO & INSTITUTIONAL ANALYSIS  
═══════════════════════════════════════════

🔗 DOMINANCE ANALYSIS:
  • BTC Dominance Trend: {btc_dominance_trend} ({dominance_change}% change)
  • Dominance Support: {dominance_support}% | Resistance: {dominance_resistance}%
  • Market Leadership: {market_leadership_strength}
  • Implication: {dominance_trend_implication}

💰 INSTITUTIONAL FLOWS:
  • Flow Direction: {institutional_flows}
  • ETF Flows (24h): ${etf_flows_millions}M
  • ETF Flow Implication: {etf_implication}
  • Whale Accumulation: {whale_accumulation_level}
  • Accumulated BTC: {total_whale_btc}
  • Miner Selling Pressure: {miner_pressure}
  • Miner Reserve Status: {miner_reserve_status}

📊 MACRO CORRELATIONS:
  • DXY (USD Strength): {dxy_correlation} (Strength: {dxy_strength}%)
  • S&P 500 (Stocks): {sp500_correlation} (Strength: {sp500_strength}%)
  • Gold (Traditional Asset): {gold_correlation}
  • Interest Rate Sensitivity: {rate_sensitivity}
  • Treasury Yield Impact: {treasury_impact}

⚠️ CRITICAL BTC-ONLY FACTORS:
  1. Monitor dominance breaks above resistance for altcoin season rotation
  2. Monitor dominance breaks below support for BTC weakness
  3. ETF flows >$500M/day = strong institutional accumulation
  4. Whale accumulation >10K BTC in last 7 days = bullish signal
  5. Miner reserves <1M BTC = reduced selling pressure (bullish)
  6. DXY strengthening = headwind for BTC (negative correlation)
  7. Fed rate cuts = bullish for BTC (lower opportunity cost)

🚨 BTC MACRO CONFLUENCE LEVELS:
  • Strong Buy Signal: Rising dominance + High ETF inflows + Whale buying + Falling DXY
  • Strong Sell Signal: Falling dominance + ETF outflows + Whale selling + Rising DXY
```

### Section 10B: Altcoin Correlation Analysis (Conditional - Altcoin Only)
```
═══════════════════════════════════════════
🔗 ALTCOIN CORRELATION & SECTOR ANALYSIS
═══════════════════════════════════════════

📊 CORRELATION MATRIX:
  • BTC Correlation: {btc_correlation_direction} (Strength: {btc_correlation_strength}%)
  • ETH Correlation: {eth_correlation_direction} (Strength: {eth_correlation_strength}%) 
  • Sector Correlation: {sector_correlation} (Strength: {sector_correlation_strength}%)
  • Independent Move Probability: {independent_move_probability}%

🏢 SECTOR ANALYSIS:
  • Sector Type: {sector_type} (LAYER_1 / LAYER_2 / DEFI / AI / GAMING / MEME / OTHER)
  • Sector Momentum: {sector_momentum} (STRONG_BULL / WEAK_BULL / NEUTRAL / WEAK_BEAR / STRONG_BEAR)
  • Sector Rotation Risk: {sector_rotation_risk} (LOW / MEDIUM / HIGH)
  • Leadership Position: {sector_leadership} (SECTOR_LEADER / AVERAGE / LAGGARD)
  • Trend vs Sector: {symbol_vs_sector_trend}

💰 MARKET CAP CONTEXT:
  • Tier: {market_cap_tier} (Large: >$10B / Mid: $1B-$10B / Small: $100M-$1B)
  • Liquidity Risk: {liquidity_risk_profile} (Daily volume, spread, slippage)
  • 24h Volume: ${daily_volume_millions}M
  • Volatility Expectation: {volatility_expectation}% (vs BTC 2.34%)
  • Max Recommended Position: {max_position_size}% (Account risk management)

📈 PROJECT FUNDAMENTALS:
  • Health Score: {project_health_score}/100
  • Tokenomics Quality: {tokenomics_quality} (EXCELLENT / GOOD / FAIR / POOR)
  • Centralization Risk: {centralization_risk} (LOW / MEDIUM / HIGH)
  • Ecosystem Growth: {ecosystem_growth}
  • Developer Activity: {dev_activity_trend}
  • Community Strength: {community_strength}

⚠️ CRITICAL ALTCOIN RISK FACTORS:
  1. High BTC correlation (>80%) = Strong dependency, follow BTC direction
  2. Low BTC correlation (<20%) = Higher independent risk, hard to predict
  3. Low liquidity (<$10M daily) = Avoid or max 0.5% position size
  4. Small/micro cap = Expect 2-3x normal volatility
  5. Meme coins = Automatic HIGH risk, max 0.1% portfolio allocation
  6. Sector rotation = Avoid buying into weakening sectors
  7. Falling dominance = Opportunity for altseason, time entries with BTC dips

🎯 ALTCOIN CONFLUENCE RULES:
  • STRONG BUY: Low BTC correlation + Rising sector + Good fundamentals + High volume
  • WEAK BUY: High BTC correlation + Bullish BTC trend + Mid/large cap + Good health
  • WAIT: High BTC correlation + Bearish BTC trend OR Low sector momentum
  • AVOID: Meme coin OR Micro cap + Low volume OR Centralized + High risk
```

### Section 12: Dynamic Risk Adjustments & Position Sizing (Optional)
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

### Section 11: 26 Important Enhanced Guidelines
```
IMPORTANT GUIDELINES (COMPREHENSIVE - 26 GUIDELINES):

=== UNIVERSAL CORE GUIDELINES (Apply to ALL assets) ===

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

=== BTC-SPECIFIC GUIDELINES (Apply ONLY for BTC) ===

13. For BTC, weight institutional flows and ETF activity at 25% of fundamental score

14. Monitor dominance trends - falling dominance often precedes altcoin season rotation

15. Use wider stops (4-6%) due to BTC's macro sensitivity and news volatility (vs 2-3% for alts)

16. Consider miner selling pressure - high pressure requires stronger technical setup for entry

17. In BULL regimes with rising dominance, BTC often significantly outperforms altcoins

18. Watch macro indicators (DXY, Fed decisions, Treasury yields) - BTC highly correlated

19. Whale movement (>100 BTC) signals institutional accumulation/distribution, affects price

=== ALTCOIN-SPECIFIC GUIDELINES (Apply ONLY for Altcoins) ===

20. For altcoins, correlation analysis weights 30% of technical score (vs 15% for universals)

21. Small/micro cap coins require 2x wider stops (6-10%) and 50% reduced position sizes

22. High BTC correlation (>70%) means must wait for BTC direction confirmation before entry

23. Sector rotation risk = reduce holding period by 50% if sector momentum is falling

24. Meme coins automatically get HIGH risk and max 0.1% portfolio allocation (non-negotiable)

25. Project health score <40 = AVOID regardless of technical setup (fundamental risk too high)

26. Low liquidity (<$10M daily) = AVOID or max 0.5% position size (execution risk too high)

=== UNIVERSAL ENHANCED GUIDELINES (Apply to ALL assets with full context) ===

27. AUTOMATICALLY DETECT asset type at start and adjust analysis focus accordingly

28. APPLY dynamic risk multipliers based on market cap, liquidity, and volatility

29. CALCULATE position sizing based on asset type and risk parameters (use formula in Section 12)

30. MONITOR sector rotation - avoid buying into weakening sectors even if technicals look good

31. USE correlation analysis to time entries - align with BTC/ETH macro movements

32. CONSIDER market regime - align strategy with current conditions (BULL/BEAR/SIDEWAYS/ALTSEASON)

33. ADJUST confidence scores DOWN if asset-specific risk factors are high (low liquidity, high correlation)

34. WEIGHT institutional indicators AT 40% minimum for all assets (not negotiable)

35. INCLUDE conflicting signals section - explicit warning of divergences between timeframes

36. RECOMMEND WAIT if confidence <50% OR major conflicting signals OR unclear market regime
```

### Section 12: JSON Response Format Request
```
Return ONLY valid JSON with this EXACT ENHANCED structure (15 + 8 new fields = 23 total):

{
  "recommendation": "BUY" | "SELL" | "HOLD" | "WAIT",
  "confidence": 0-100,
  "trading_style": "scalping" | "swing",
  "entry_point": <price>,
  "stop_loss": <price>,
  "take_profit": [<target1>, <target2>, <target3>],
  "expected_holding_period": "X hours/days",
  "risk_level": "LOW" | "MEDIUM" | "HIGH",
  "reasoning_vietnamese": "Phân tích chi tiết 300-500 từ",
  "key_points": ["Point 1", "Point 2", ...],
  "conflicting_signals": ["Signal 1", "Signal 2", ...],
  "warnings": ["Warning 1", ...],
  "market_sentiment": "BULLISH" | "BEARISH" | "NEUTRAL",
  "technical_score": 0-100,
  "fundamental_score": 0-100,
  
  // === NEW FIELDS FOR ASSET-SPECIFIC ANALYSIS (8 NEW) ===
  
  "asset_type": "BTC" | "ETH" | "LARGE_CAP_ALT" | "MID_CAP_ALT" | "SMALL_CAP_ALT" | "MEME_COIN",
  
  "sector_analysis": {
    "sector": "LAYER_1" | "LAYER_2" | "DEFI" | "AI" | "GAMING" | "MEME" | "OTHER",
    "sector_momentum": "STRONG_BULL" | "WEAK_BULL" | "NEUTRAL" | "WEAK_BEAR" | "STRONG_BEAR",
    "sector_rotation_risk": "LOW" | "MEDIUM" | "HIGH",
    "sector_leadership": "SECTOR_LEADER" | "SECTOR_AVERAGE" | "SECTOR_LAGGARD"
  },
  
  "correlation_analysis": {
    "btc_correlation": {
      "direction": "STRONG_POSITIVE" | "MODERATE_POSITIVE" | "WEAK_POSITIVE" | "NEUTRAL" | "WEAK_NEGATIVE" | "MODERATE_NEGATIVE" | "STRONG_NEGATIVE",
      "strength": 0.0-1.0
    },
    "eth_correlation": {
      "direction": "...(same as btc_correlation)",
      "strength": 0.0-1.0
    },
    "independent_move_probability": 0-100
  },
  
  "fundamental_analysis": {
    "project_health_score": 0-100,
    "tokenomics_quality": "EXCELLENT" | "GOOD" | "FAIR" | "POOR",
    "centralization_risk": "LOW" | "MEDIUM" | "HIGH",
    "ecosystem_growth": "ACCELERATING" | "STABLE" | "DECLINING"
  },
  
  "position_sizing_recommendation": {
    "risk_per_trade": 0.1-5.0,
    "max_position_size_percent": 0.05-5.0,
    "leverage_suggestion": 1-10,
    "position_sizing_notes": "Reason for recommended size"
  },
  
  "macro_context": {
    // FOR BTC ONLY:
    "btc_dominance_trend": "RISING" | "FALLING" | "STABLE",
    "institutional_flows": "STRONG_INFLOW" | "MODERATE_INFLOW" | "NEUTRAL" | "MODERATE_OUTFLOW" | "STRONG_OUTFLOW",
    "etf_flow_signal": "BULLISH" | "NEUTRAL" | "BEARISH",
    "miner_selling_pressure": "LOW" | "MODERATE" | "HIGH",
    
    // FOR ALTCOINS ONLY:
    "sector_trend": "LEADING" | "FOLLOWING" | "LAGGING",
    "rotation_risk": "LOW" | "MODERATE" | "HIGH",
    "liquidity_assessment": "EXCELLENT" | "GOOD" | "FAIR" | "POOR"
  },
  
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

## Fields Summary

**Original 15 Fields (v2.0):**
1. recommendation (BUY/SELL/HOLD/WAIT)
2. confidence (0-100%)
3. trading_style
4. entry_point, stop_loss, take_profit
5. expected_holding_period
6. risk_level
7. reasoning_vietnamese
8. key_points, conflicting_signals, warnings
9. market_sentiment
10. technical_score, fundamental_score
11. historical_analysis (h1/h4/d1 context)

**New 8 Fields (v2.2 Enhancement):**
1. **asset_type** - Dynamic asset classification (BTC/ETH/CAP_TIERS/MEME)
2. **sector_analysis** - Sector classification, momentum, rotation risk, leadership
3. **correlation_analysis** - BTC/ETH correlation strength and direction + independent move probability
4. **fundamental_analysis** - Project health, tokenomics, centralization, ecosystem growth
5. **position_sizing_recommendation** - Dynamic position sizing with reasoning
6. **macro_context** - BTC-specific (dominance, flows, ETF, miner) OR Altcoin-specific (sector, rotation, liquidity)
7-8. (Enhanced historical_analysis with more depth)


## Version History
- **v2.2** (Nov 11, 2025): Asset Type Detection + BTC Macro + Altcoin Correlation + Dynamic Risk (36 guidelines)
- **v2.1** (Nov 11, 2025): Message order restructure (technical analysis first)
- **v2.0** (Sep 2025): Initial comprehensive version with core indicators

## Key Features

### Dynamic Content
The prompt is built dynamically based on:
- **Asset Type**: Detected from symbol, market cap, sector (BTC/ETH/Large/Mid/Small/Meme)
- **Symbol and Market Data**: Current price, dominance, volume, correlation
- **Indicator Data**: RSI/MFI, Stoch+RSI, Volume Profile, FVGs, Order Blocks, SMC
- **Historical Performance**: 7+ days of historical accuracy stats (if available)
- **Market Regime**: BULL/BEAR/SIDEWAYS/ALTSEASON classification
- **Pump Detection**: 3-layer pump signal scoring (>=80% triggers HIGH risk warning)
- **Trading Style**: Scalping (tight stops, quick exits) vs Swing (wider stops, position holding)
- **Macro Context**: BTC dominance, institutional flows, ETF movement, whale activity (for BTC)
- **Sector Context**: Sector momentum, rotation risk, leadership position (for altcoins)

### Conditional Sections
- **Section 10A (BTC Macro)**: Included ONLY when asset_type == "BTC"
  - Dominance analysis, institutional flows, ETF flows, whale accumulation, miner pressure
  - Macro correlations (DXY, S&P500, Gold, Treasury yields)
  
- **Section 10B (Altcoin Correlation)**: Included ONLY when asset_type != "BTC"
  - BTC/ETH correlation analysis with strength ratings
  - Sector analysis with momentum and rotation risk
  - Project health scoring and tokenomics quality
  - Liquidity assessment and market cap context

### AI Guidance
The prompt explicitly tells the AI model to:
1. **Detect asset type** at start and adjust focus accordingly
2. **Analyze all indicators** in systematic way (weighted by type)
3. **Weight institutional indicators** AT 40% minimum (non-negotiable)
4. **Use historical data** to adjust confidence scores
5. **Identify conflicting signals** explicitly between timeframes
6. **Apply dynamic risk multipliers** based on asset-specific factors
7. **Calculate position sizing** using provided formula
8. **Provide Vietnamese reasoning** for regional trader understanding
9. **Return enhanced JSON** with 8 new asset-specific fields
10. **WAIT if unclear** - recommend WAIT when confidence <50% or major conflicts

## Integration with Code

### In `gemini_analyzer.py`
The `_build_prompt()` method must be enhanced to:

1. **Detect asset type** from symbol and market cap
```python
asset_type = detect_asset_type(symbol, market_cap, sector)
```

2. **Include Section 0** (Asset Type Detection)
```python
prompt += f"🎯 ASSET TYPE DETECTION: {asset_type}\n..."
```

3. **Conditionally add Section 10A or 10B**
```python
if asset_type == "BTC":
    prompt += format_btc_macro_section(btc_data)
else:
    prompt += format_altcoin_correlation_section(altcoin_data)
```

4. **Include dynamic risk section** (Section 12)
```python
prompt += format_risk_adjustments_section(asset_type, market_cap, volume, volatility)
```

5. **Add enhanced guidelines** (Section 13) with 36 guidelines
```python
prompt += ENHANCED_GUIDELINES_36  # BTC-specific + Altcoin-specific + Universal
```

6. **Request enhanced JSON** (Section 14) with 8 new fields
```python
prompt += JSON_RESPONSE_SCHEMA_V22  # With all 23 fields
```

### In `telegram_commands.py`
When receiving the response:

1. **Validate against schema** - Check all 23 fields present
```python
validate_response_schema(response, schema_v22)
```

2. **Extract asset type** - Use for routing and display
```python
asset_type = response['asset_type']
```

3. **Format sector/correlation** - Display differently based on asset type
```python
if asset_type == "BTC":
    display_macro_insights(response['macro_context'])
else:
    display_sector_insights(response['sector_analysis'])
```

4. **Apply position sizing** - Use recommendations for risk management
```python
position_size = response['position_sizing_recommendation']['max_position_size_percent']
```

## Prompt Size Estimation

- **Base prompt**: 4,000-5,000 tokens
- **With Section 0 (Asset Detection)**: +200 tokens
- **With Section 10A (BTC Macro)**: +1,000-1,200 tokens
- **With Section 10B (Altcoin Correlation)**: +1,200-1,500 tokens
- **With Section 12 (Dynamic Risk)**: +300-400 tokens
- **Enhanced Section 13 (36 guidelines)**: +400-500 tokens
- **Enhanced Section 14 (New JSON fields)**: +200 tokens
- **Total estimated**: 5,500-8,000 tokens (vs 5,000-7,000 previously)

## Backward Compatibility
✅ **Fully compatible** with existing code
- Original 15 JSON fields still present
- New 8 fields are additions, not replacements
- Conditional sections only include relevant data
- No breaking changes to message format

---

**Last Updated:** November 11, 2025  
**Version:** 2.2 ENHANCED  
**Maintained by:** RSI+MFI Trading Bot Development Team
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
