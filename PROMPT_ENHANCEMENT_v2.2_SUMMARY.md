# Prompt & JSON Schema v2.2 Enhancement Summary

**Date:** November 11, 2025  
**Version:** 2.2 ENHANCED  
**Status:** ✅ Documentation Complete

## Overview of Enhancements

This is a major upgrade to the Gemini AI prompt and JSON response schema, adding comprehensive asset-specific analysis for BTC, ETH, and various altcoin tiers with dynamic risk management.

## Files Updated

### 1. GEMINI_PROMPT_TEMPLATE.md (14.5KB → 32KB)
**+119% size increase, +17.5KB added content**

**New Sections Added:**
- **Section 0: Asset Type Detection** (NEW)
  - 6 asset types: BTC, ETH, LARGE_CAP_ALT, MID_CAP_ALT, SMALL_CAP_ALT, MEME_COIN
  - Focus adjustments based on asset type
  - Market cap thresholds defined

- **Section 10A: BTC Macro Analysis** (NEW - Conditional)
  - Dominance analysis and trends
  - Institutional flows (ETF, whale, miner)
  - Macro correlations (DXY, S&P500, Gold, Treasury)
  - 8 critical BTC-only factors
  - Confluence level signals

- **Section 10B: Altcoin Correlation Analysis** (NEW - Conditional)
  - BTC/ETH correlation matrix
  - Sector analysis with momentum and rotation
  - Market cap context and liquidity
  - Project fundamentals
  - Altcoin-specific risk factors
  - Confluence rules for buy/sell/wait

- **Section 12: Dynamic Risk Adjustments & Position Sizing** (NEW)
  - Asset-specific risk multipliers
  - Position sizing by asset type
  - Market regime adjustments (RISK_ON/OFF, ALTSEASON, BTC_DOMINANT)
  - Liquidity & volatility rules
  - Position sizing formula

- **Section 13: 36 Enhanced Guidelines** (12 → 36)
  - 12 Universal Core Guidelines
  - 7 BTC-Specific Guidelines (13-19)
  - 7 Altcoin-Specific Guidelines (20-26)
  - 10 Universal Enhanced Guidelines (27-36)

### 2. AI_RESPONSE_JSON_SCHEMA.md (24.5KB → 31KB)
**+27% size increase, +6.5KB added documentation**

**New Fields Added (8 Total):**
1. **asset_type** - Detected asset classification
2. **sector_analysis** - Sector, momentum, rotation risk, leadership
3. **correlation_analysis** - BTC/ETH correlation + independent move probability
4. **fundamental_analysis** - Project health, tokenomics, centralization, ecosystem
5. **position_sizing_recommendation** - Dynamic sizing with reasoning
6. **macro_context** - Conditional BTC or Altcoin specific data

**Enhanced Documentation:**
- Comprehensive field descriptions for all new fields
- Example values for each field
- Integration guidelines for implementation
- Database schema examples
- API integration examples

## Prompt Structure (14 Sections Total)

```
Section 0:  Asset Type Detection (NEW)
Section 1:  Trading Style Definition
Section 2:  Historical Performance (Optional)
Section 3:  Technical Indicators
Section 4:  Pump Signal Analysis
Section 5:  Institutional Indicators (JSON)
Section 6:  Volume Analysis
Section 7:  Historical Comparison
Section 8:  Extended Historical Klines
Section 9:  24H Market Data
Section 10A: BTC Macro Analysis (BTC ONLY - NEW)
Section 10B: Altcoin Correlation (ALTCOIN ONLY - NEW)
Section 11: Cross-Symbol Pattern Recognition
Section 12: Dynamic Risk Adjustments (NEW)
Section 13: 36 Enhanced Guidelines (NEW)
Section 14: JSON Response Format Request
```

## JSON Schema (23 Fields Total)

### Original 15 Fields (v2.0)
```
recommendation, confidence, trading_style
entry_point, stop_loss, take_profit
expected_holding_period, risk_level
reasoning_vietnamese
key_points, conflicting_signals, warnings
market_sentiment
technical_score, fundamental_score
historical_analysis
```

### New 8 Fields (v2.2)
```
asset_type
sector_analysis (4 sub-fields)
correlation_analysis (3 sub-fields)
fundamental_analysis (4 sub-fields)
position_sizing_recommendation (4 sub-fields)
macro_context (conditional: 4 BTC fields OR 3 altcoin fields)
```

## Key Enhancements

### 1. Asset Type Detection
- **Automatic Classification** from symbol, market cap, sector
- **Dynamic Analysis Focus** based on asset type
- **Risk Adjustments** specific to each tier
- **Position Sizing** from 3-5% (BTC) to 0.05-0.1% (meme coins)

### 2. BTC Macro Analysis
- Dominance trends for market rotation signals
- Institutional flows (ETF/whale/miner) for accumulation detection
- Macro correlations (DXY, stocks, bonds) for timing
- Confluence signals for high-probability setups

### 3. Altcoin Correlation
- BTC/ETH dependency analysis
- Sector momentum and rotation risk
- Project fundamentals scoring
- Liquidity assessment for execution

### 4. Dynamic Risk Management
- Asset-type based position sizing
- Liquidity adjustments (<$10M = 50-70% reduction)
- Volatility-based stop loss widening
- Correlation penalties for high BTC-dependent coins
- Market regime adjustments (BULL/BEAR/ALTSEASON/BTC_DOMINANT)

### 5. Enhanced Guidelines
- **26 total guidelines** (12 core + 7 BTC-specific + 7 altcoin-specific)
- **36 total rules** including universal enhanced guidelines
- BTC-specific rules (wider stops, dominance monitoring, miner pressure)
- Altcoin-specific rules (correlation confirmation, sector rotation, health scoring)
- Universal rules (asset detection, dynamic multipliers, regime alignment)

## Implementation Requirements

### For `gemini_analyzer.py`:
1. Add `detect_asset_type(symbol, market_cap, sector)` function
2. Enhance `_build_prompt()` to include all 14 sections
3. Add conditional logic for Section 10A (BTC) vs 10B (Altcoin)
4. Include dynamic risk section with market cap and liquidity data
5. Ensure all 36 guidelines are in prompt text
6. Request enhanced JSON with 23 fields

### For `telegram_commands.py`:
1. Validate JSON response against 23-field schema
2. Extract and display `asset_type` for context
3. Show sector/correlation analysis based on asset type
4. Apply position sizing recommendations
5. Display macro context appropriately (BTC dominance OR altcoin sector)

### For Database:
1. Store all 23 JSON fields in JSONB column
2. Index `asset_type` for filtering and analysis
3. Track position sizing recommendations for portfolio management
4. Store macro context for post-analysis review

## Token Estimation

- **Base prompt**: 4,000-5,000 tokens
- **Asset Type Detection**: +200 tokens
- **BTC Macro (if BTC)**: +1,000-1,200 tokens
- **Altcoin Correlation (if altcoin)**: +1,200-1,500 tokens
- **Dynamic Risk Section**: +300-400 tokens
- **Enhanced Guidelines (36 vs 12)**: +400-500 tokens
- **Enhanced JSON format**: +200 tokens
- **Total estimated**: 5,500-8,500 tokens (vs 5,000-7,000 previously)

## Backward Compatibility

✅ **Fully Backward Compatible**
- All original 15 fields remain unchanged
- New 8 fields are additions only
- Conditional sections (10A/10B) don't break existing logic
- Old JSON responses still valid (missing new fields = default values)
- No changes to message format or ordering
- Existing code continues to work without modification

## Benefits

1. **Better BTC Analysis** - Macro factors, dominance, institutional flows
2. **Better Altcoin Analysis** - Correlation, sector, project health
3. **Risk Management** - Dynamic position sizing, asset-specific stops
4. **Market Awareness** - Detect asset type, adjust strategy accordingly
5. **Portfolio Safety** - Position size limits by asset tier
6. **Fundamentals** - Include project health in buy/sell decision
7. **Execution Risk** - Liquidity assessment for entry/exit
8. **Sector Timing** - Rotation risk detection for reduced exposure

## Version Progression

```
v2.0 (Sep 2025)   - Core technical analysis with institutional indicators
                    15 fields, 12 guidelines, 9 sections
                    
v2.1 (Nov 11)     - Message order restructuring (technical details first)
                    Same fields, same guidelines, same sections
                    Better UX flow
                    
v2.2 (Nov 11)     - Asset-specific analysis enhancement
                    23 fields (15 + 8 new)
                    36 guidelines (12 core + 24 specialized)
                    14 sections (9 + 5 new/enhanced)
                    Dynamic risk management
                    BTC macro + Altcoin correlation analysis
```

## Next Steps

1. **Code Implementation** - Update `_build_prompt()` in gemini_analyzer.py
2. **Testing** - Run AI analysis with both BTC and altcoin samples
3. **Validation** - Ensure JSON response includes all 23 fields
4. **Deployment** - Push to Railway, monitor token usage
5. **Monitoring** - Track confidence accuracy by asset type
6. **Refinement** - Adjust weights and thresholds based on live data

---

**Documentation Version:** 2.2 ENHANCED  
**Last Updated:** November 11, 2025  
**Status:** Ready for Implementation  
**Maintained by:** RSI+MFI Trading Bot Development Team
