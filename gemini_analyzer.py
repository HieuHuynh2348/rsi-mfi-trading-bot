"""
Gemini AI Trading Analyzer
Integrates Google Gemini 2.5 Pro for comprehensive trading analysis

Author: AI Assistant
Date: November 9, 2025
"""

import google.generativeai as genai
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import time

logger = logging.getLogger(__name__)


class GeminiAnalyzer:
    """
    Google Gemini AI integration for advanced trading analysis
    
    Features:
    - Comprehensive multi-indicator analysis
    - Historical comparison (week-over-week)
    - Scalping and swing trading recommendations
    - Risk assessment and entry/exit points
    - Vietnamese language output
    """
    
    def __init__(self, api_key: str, binance_client, stoch_rsi_analyzer):
        """
        Initialize Gemini analyzer
        
        Args:
            api_key: Google Gemini API key
            binance_client: BinanceClient instance
            stoch_rsi_analyzer: StochRSIAnalyzer instance
        """
        self.api_key = api_key
        self.binance = binance_client
        self.stoch_rsi_analyzer = stoch_rsi_analyzer
        
        # Initialize institutional indicator modules
        from volume_profile import VolumeProfileAnalyzer
        from fair_value_gaps import FairValueGapDetector
        from order_blocks import OrderBlockDetector
        from support_resistance import SupportResistanceDetector
        from smart_money_concepts import SmartMoneyAnalyzer
        
        self.volume_profile = VolumeProfileAnalyzer(binance_client)
        self.fvg_detector = FairValueGapDetector(binance_client, auto_threshold=True)
        self.ob_detector = OrderBlockDetector(binance_client)
        self.sr_detector = SupportResistanceDetector(binance_client)
        self.smc_analyzer = SmartMoneyAnalyzer(binance_client)
        
        # Configure Gemini
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # Cache system (15 minutes)
        self.cache = {}  # {symbol: {'data': result, 'timestamp': time.time()}}
        self.cache_duration = 900  # 15 minutes in seconds
        
        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 1.0  # 1 second between requests
        
        logger.info("Gemini AI Analyzer initialized (Model: gemini-2.0-flash-exp, Institutional indicators loaded)")
    
    def _check_cache(self, symbol: str) -> Optional[Dict]:
        """
        Check if cached result exists and is still valid
        
        Args:
            symbol: Trading symbol
            
        Returns:
            Cached result or None
        """
        if symbol in self.cache:
            cached_data = self.cache[symbol]
            age = time.time() - cached_data['timestamp']
            
            if age < self.cache_duration:
                logger.info(f"Using cached AI analysis for {symbol} (age: {age:.0f}s)")
                return cached_data['data']
            else:
                # Expired, remove from cache
                del self.cache[symbol]
        
        return None
    
    def _update_cache(self, symbol: str, result: Dict):
        """
        Update cache with new result
        
        Args:
            symbol: Trading symbol
            result: Analysis result to cache
        """
        self.cache[symbol] = {
            'data': result,
            'timestamp': time.time()
        }
        logger.info(f"Cached AI analysis for {symbol}")
    
    def _rate_limit(self):
        """Apply rate limiting between requests"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last
            logger.debug(f"Rate limiting: sleeping {sleep_time:.2f}s")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def collect_data(self, symbol: str, pump_data: Optional[Dict] = None) -> Dict:
        """
        Collect all analysis data for a symbol
        
        Args:
            symbol: Trading symbol
            pump_data: Optional pump detector data
            
        Returns:
            Dict with all indicator data
        """
        try:
            # Get current price and 24h data
            ticker_24h = self.binance.get_24h_data(symbol)
            current_price = ticker_24h['last_price'] if ticker_24h else 0
            
            # Get multi-timeframe klines
            timeframes = ['5m', '1h', '4h', '1d']
            klines_dict = self.binance.get_multi_timeframe_data(symbol, timeframes, limit=200)
            
            # RSI+MFI analysis
            from indicators import analyze_multi_timeframe
            import config
            rsi_mfi_result = analyze_multi_timeframe(
                klines_dict,
                config.RSI_PERIOD,
                config.MFI_PERIOD,
                config.RSI_LOWER,
                config.RSI_UPPER,
                config.MFI_LOWER,
                config.MFI_UPPER
            )
            
            # Stoch+RSI analysis
            stoch_rsi_result = self.stoch_rsi_analyzer.analyze_multi_timeframe(
                symbol,
                timeframes=['1m', '5m', '4h', '1d']
            )
            
            # Volume data
            volume_data = {
                'current': ticker_24h['volume'] if ticker_24h else 0,
                'base_volume': ticker_24h['base_volume'] if ticker_24h else 0,
                'trades': ticker_24h['trades'] if ticker_24h else 0
            }
            
            # INSTITUTIONAL INDICATORS
            
            # Volume Profile (4h, 1d)
            vp_result = self.volume_profile.analyze_multi_timeframe(symbol, ['4h', '1d'])
            
            # Fair Value Gaps (1h, 4h, 1d)
            fvg_result = self.fvg_detector.analyze_multi_timeframe(symbol, ['1h', '4h', '1d'])
            
            # Order Blocks (4h, 1d)
            ob_result = self.ob_detector.analyze_multi_timeframe(symbol, ['4h', '1d'])
            
            # Support/Resistance zones (4h, 1d)
            sr_result = self.sr_detector.analyze_multi_timeframe(symbol, ['4h', '1d'])
            
            # Smart Money Concepts (4h, 1d)
            smc_result = self.smc_analyzer.analyze_multi_timeframe(symbol, ['4h', '1d'])
            
            # Historical comparison (week-over-week)
            historical = self._get_historical_comparison(symbol, klines_dict)
            
            # Market data
            market_data = {
                'price': current_price,
                'price_change_24h': ticker_24h['price_change_percent'] if ticker_24h else 0,
                'high_24h': ticker_24h['high'] if ticker_24h else 0,
                'low_24h': ticker_24h['low'] if ticker_24h else 0,
                'volume_24h': ticker_24h['volume'] if ticker_24h else 0
            }
            
            return {
                'symbol': symbol,
                'timestamp': datetime.now().isoformat(),
                'market_data': market_data,
                'rsi_mfi': rsi_mfi_result,
                'stoch_rsi': stoch_rsi_result,
                'pump_data': pump_data,
                'volume_data': volume_data,
                'historical': historical,
                # Institutional indicators
                'volume_profile': vp_result,
                'fair_value_gaps': fvg_result,
                'order_blocks': ob_result,
                'support_resistance': sr_result,
                'smart_money_concepts': smc_result
            }
            
        except Exception as e:
            logger.error(f"Error collecting data for {symbol}: {e}")
            return None
    
    def _get_historical_comparison(self, symbol: str, klines_dict: Dict) -> Dict:
        """
        Compare current data with last week and get previous candle info for H4/D1
        
        Args:
            symbol: Trading symbol
            klines_dict: Multi-timeframe klines data
            
        Returns:
            Dict with historical comparison and previous candle data
        """
        try:
            result = {}
            
            # === WEEKLY COMPARISON (D1 TIMEFRAME) ===
            if '1d' in klines_dict:
                df_1d = klines_dict['1d']
                
                if len(df_1d) >= 14:  # Need at least 2 weeks
                    # Current week (last 7 days)
                    current_week = df_1d.tail(7)
                    # Last week (8-14 days ago)
                    last_week = df_1d.iloc[-14:-7]
                    
                    # Price comparison
                    current_price = float(current_week['close'].iloc[-1])
                    week_ago_price = float(last_week['close'].iloc[-1])
                    price_change_pct = ((current_price - week_ago_price) / week_ago_price) * 100
                    
                    # Volume comparison
                    current_volume = float(current_week['volume'].sum())
                    last_week_volume = float(last_week['volume'].sum())
                    volume_change_pct = ((current_volume - last_week_volume) / last_week_volume) * 100 if last_week_volume > 0 else 0
                    
                    # RSI comparison
                    from indicators import calculate_rsi, calculate_hlcc4
                    
                    current_week_hlcc4 = calculate_hlcc4(current_week)
                    last_week_hlcc4 = calculate_hlcc4(last_week)
                    
                    current_rsi = float(calculate_rsi(current_week_hlcc4, 14).iloc[-1])
                    last_week_rsi = float(calculate_rsi(last_week_hlcc4, 14).iloc[-1])
                    rsi_change = current_rsi - last_week_rsi
                    
                    result.update({
                        'price_change_vs_last_week': round(price_change_pct, 2),
                        'volume_change_vs_last_week': round(volume_change_pct, 2),
                        'rsi_change_vs_last_week': round(rsi_change, 2),
                        'current_price': current_price,
                        'week_ago_price': week_ago_price,
                        'current_volume': current_volume,
                        'last_week_volume': last_week_volume,
                        'current_rsi': current_rsi,
                        'last_week_rsi': last_week_rsi
                    })
                    
                    # === D1 PREVIOUS CANDLE INFO ===
                    if len(df_1d) >= 2:
                        prev_candle = df_1d.iloc[-2]
                        result['d1_prev_candle'] = {
                            'open': float(prev_candle['open']),
                            'high': float(prev_candle['high']),
                            'low': float(prev_candle['low']),
                            'close': float(prev_candle['close']),
                            'volume': float(prev_candle['volume']),
                            'body_size': abs(float(prev_candle['close']) - float(prev_candle['open'])),
                            'is_bullish': float(prev_candle['close']) > float(prev_candle['open']),
                            'upper_wick': float(prev_candle['high']) - max(float(prev_candle['open']), float(prev_candle['close'])),
                            'lower_wick': min(float(prev_candle['open']), float(prev_candle['close'])) - float(prev_candle['low'])
                        }
            
            # === H4 PREVIOUS CANDLE INFO ===
            if '4h' in klines_dict:
                df_4h = klines_dict['4h']
                
                if len(df_4h) >= 2:
                    prev_candle = df_4h.iloc[-2]
                    result['h4_prev_candle'] = {
                        'open': float(prev_candle['open']),
                        'high': float(prev_candle['high']),
                        'low': float(prev_candle['low']),
                        'close': float(prev_candle['close']),
                        'volume': float(prev_candle['volume']),
                        'body_size': abs(float(prev_candle['close']) - float(prev_candle['open'])),
                        'is_bullish': float(prev_candle['close']) > float(prev_candle['open']),
                        'upper_wick': float(prev_candle['high']) - max(float(prev_candle['open']), float(prev_candle['close'])),
                        'lower_wick': min(float(prev_candle['open']), float(prev_candle['close'])) - float(prev_candle['low'])
                    }
            
            return result
            
        except Exception as e:
            logger.error(f"Error in historical comparison: {e}")
            return {}
    
    def _build_prompt(self, data: Dict, trading_style: str = 'swing') -> str:
        """
        Build Gemini prompt from collected data
        
        Args:
            data: Collected analysis data
            trading_style: 'scalping' or 'swing'
            
        Returns:
            Formatted prompt string
        """
        symbol = data['symbol']
        market = data['market_data']
        rsi_mfi = data['rsi_mfi']
        stoch_rsi = data['stoch_rsi']
        pump = data.get('pump_data')
        volume = data['volume_data']
        historical = data.get('historical', {})
        
        # Format RSI/MFI data
        rsi_mfi_text = ""
        if rsi_mfi and 'timeframes' in rsi_mfi:
            for tf, analysis in rsi_mfi['timeframes'].items():
                rsi_mfi_text += f"  {tf}: RSI={analysis['rsi']:.1f}, MFI={analysis['mfi']:.1f}, Signal={analysis['signal']}\n"
            rsi_mfi_text += f"  Consensus: {rsi_mfi['consensus']} (Strength: {rsi_mfi['consensus_strength']}/4)\n"
        
        # Format Stoch+RSI data
        stoch_text = ""
        if stoch_rsi and 'timeframes' in stoch_rsi:
            for tf_data in stoch_rsi['timeframes']:
                tf = tf_data['timeframe']
                stoch_text += f"  {tf}: RSI={tf_data['rsi']:.1f}, Stoch={tf_data['stoch_k']:.1f}, Signal={tf_data['signal_text']}\n"
            stoch_text += f"  Consensus: {stoch_rsi['consensus']} (Strength: {stoch_rsi['consensus_strength']}/4)\n"
        
        # Format pump data (only if high confidence >= 80%)
        pump_text = "No high-confidence pump signal detected"
        if pump and pump.get('final_score', 0) >= 80:
            pump_text = f"""HIGH CONFIDENCE PUMP DETECTED:
  Final Score: {pump['final_score']:.0f}%
  Layer 1 (5m): {pump.get('layer1', {}).get('pump_score', 0):.0f}% - Early detection
  Layer 2 (1h/4h): {pump.get('layer2', {}).get('pump_score', 0):.0f}% - Confirmation
  Layer 3 (1D): {pump.get('layer3', {}).get('pump_score', 0):.0f}% - Long-term trend
  
  Key Indicators:
  - Volume spike: {pump.get('layer1', {}).get('indicators', {}).get('volume_spike', 0)}x
  - Price change 5m: +{pump.get('layer1', {}).get('indicators', {}).get('price_change_5m', 0):.2f}%
  - RSI momentum: +{pump.get('layer1', {}).get('indicators', {}).get('rsi_change', 0):.1f}
"""
        
        # Format historical comparison
        hist_text = "Historical data unavailable"
        if historical:
            hist_text = f"""Week-over-Week Comparison:
  Price: {historical.get('price_change_vs_last_week', 0):+.2f}% (${historical.get('week_ago_price', 0):,.2f} → ${historical.get('current_price', 0):,.2f})
  Volume: {historical.get('volume_change_vs_last_week', 0):+.2f}% change
  RSI: {historical.get('rsi_change_vs_last_week', 0):+.1f} points change ({historical.get('last_week_rsi', 0):.1f} → {historical.get('current_rsi', 0):.1f})
"""
            
            # Add D1 previous candle if available
            if 'd1_prev_candle' in historical:
                candle = historical['d1_prev_candle']
                candle_type = "🟢 Bullish" if candle['is_bullish'] else "🔴 Bearish"
                hist_text += f"""
D1 Previous Candle Analysis:
  Type: {candle_type}
  Open: ${candle['open']:,.4f} | Close: ${candle['close']:,.4f}
  High: ${candle['high']:,.4f} | Low: ${candle['low']:,.4f}
  Body Size: ${candle['body_size']:,.4f}
  Upper Wick: ${candle['upper_wick']:,.4f} | Lower Wick: ${candle['lower_wick']:,.4f}
  Volume: {candle['volume']:,.0f}
"""
            
            # Add H4 previous candle if available
            if 'h4_prev_candle' in historical:
                candle = historical['h4_prev_candle']
                candle_type = "🟢 Bullish" if candle['is_bullish'] else "🔴 Bearish"
                hist_text += f"""
H4 Previous Candle Analysis:
  Type: {candle_type}
  Open: ${candle['open']:,.4f} | Close: ${candle['close']:,.4f}
  High: ${candle['high']:,.4f} | Low: ${candle['low']:,.4f}
  Body Size: ${candle['body_size']:,.4f}
  Upper Wick: ${candle['upper_wick']:,.4f} | Lower Wick: ${candle['lower_wick']:,.4f}
  Volume: {candle['volume']:,.0f}
"""
        
        # Format institutional indicators
        
        # Volume Profile
        vp_text = "Volume Profile data unavailable"
        if data.get('volume_profile'):
            vp_4h = data['volume_profile'].get('4h')
            vp_1d = data['volume_profile'].get('1d')
            
            vp_text = "Volume Profile:\n"
            if vp_1d:
                poc = vp_1d['poc']['price']
                vah = vp_1d['vah']
                val = vp_1d['val']
                position_1d = self.volume_profile.get_current_position_in_profile(market['price'], vp_1d)
                
                vp_text += f"""  1D Timeframe:
    POC (Point of Control): ${poc:,.4f}
    VAH (Value Area High): ${vah:,.4f}
    VAL (Value Area Low): ${val:,.4f}
    Current Position: {position_1d.get('position', 'UNKNOWN')} - {position_1d.get('zone', '')}
    Distance to POC: {position_1d.get('distance_to_poc_percent', 0):+.2f}%
    Bias: {position_1d.get('bias', 'N/A')}
"""
            if vp_4h:
                poc = vp_4h['poc']['price']
                vah = vp_4h['vah']
                val = vp_4h['val']
                position_4h = self.volume_profile.get_current_position_in_profile(market['price'], vp_4h)
                
                vp_text += f"""  4H Timeframe:
    POC: ${poc:,.4f} | VAH: ${vah:,.4f} | VAL: ${val:,.4f}
    Position: {position_4h.get('position', 'UNKNOWN')} ({position_4h.get('distance_to_poc_percent', 0):+.2f}% from POC)
"""
        
        # Fair Value Gaps
        fvg_text = "Fair Value Gaps data unavailable"
        if data.get('fair_value_gaps'):
            fvg_1d = data['fair_value_gaps'].get('1d')
            fvg_4h = data['fair_value_gaps'].get('4h')
            
            fvg_text = "Fair Value Gaps (Imbalance Zones):\n"
            if fvg_1d and fvg_1d.get('nearest_gaps'):
                nearest_bull = fvg_1d['nearest_gaps'].get('bullish')
                nearest_bear = fvg_1d['nearest_gaps'].get('bearish')
                stats = fvg_1d['statistics']
                
                fvg_text += f"""  1D Timeframe:
    Unfilled Bullish FVGs: {stats['unfilled_bullish_gaps']} (Fill rate: {stats['fill_rate_bullish_percent']:.0f}%)
    Unfilled Bearish FVGs: {stats['unfilled_bearish_gaps']} (Fill rate: {stats['fill_rate_bearish_percent']:.0f}%)
"""
                if nearest_bull:
                    fvg_text += f"    Nearest Bullish FVG: ${nearest_bull['bottom']:,.4f} - ${nearest_bull['top']:,.4f} ({nearest_bull['size_percentage']:.2f}% gap)\n"
                if nearest_bear:
                    fvg_text += f"    Nearest Bearish FVG: ${nearest_bear['bottom']:,.4f} - ${nearest_bear['top']:,.4f} ({nearest_bear['size_percentage']:.2f}% gap)\n"
            
            if fvg_4h and fvg_4h.get('statistics'):
                stats = fvg_4h['statistics']
                fvg_text += f"""  4H Timeframe:
    Unfilled Bullish: {stats['unfilled_bullish_gaps']} | Bearish: {stats['unfilled_bearish_gaps']}
"""
        
        # Order Blocks
        ob_text = "Order Blocks data unavailable"
        if data.get('order_blocks'):
            ob_1d = data['order_blocks'].get('1d')
            ob_4h = data['order_blocks'].get('4h')
            
            ob_text = "Order Blocks (Institutional Footprints):\n"
            if ob_1d and ob_1d.get('nearest_blocks'):
                nearest_swing = ob_1d['nearest_blocks'].get('swing')
                nearest_internal = ob_1d['nearest_blocks'].get('internal')
                stats = ob_1d['statistics']
                
                ob_text += f"""  1D Timeframe:
    Active Swing OBs: {stats['active_swing_obs']} | Internal OBs: {stats['active_internal_obs']}
    Mitigation Rate: Swing {stats['mitigation_rate_swing_percent']:.0f}% | Internal {stats['mitigation_rate_internal_percent']:.0f}%
"""
                if nearest_swing:
                    ob_text += f"    Nearest Swing OB ({nearest_swing['bias']}): ${nearest_swing['bottom']:,.4f} - ${nearest_swing['top']:,.4f}\n"
                if nearest_internal:
                    ob_text += f"    Nearest Internal OB ({nearest_internal['bias']}): ${nearest_internal['bottom']:,.4f} - ${nearest_internal['top']:,.4f}\n"
            
            if ob_4h and ob_4h.get('statistics'):
                stats = ob_4h['statistics']
                ob_text += f"""  4H Timeframe:
    Active: Swing {stats['active_swing_obs']} | Internal {stats['active_internal_obs']}
"""
        
        # Support/Resistance
        sr_text = "Support/Resistance zones unavailable"
        if data.get('support_resistance'):
            sr_1d = data['support_resistance'].get('1d')
            sr_4h = data['support_resistance'].get('4h')
            
            sr_text = "Support/Resistance Zones (High Volume):\n"
            if sr_1d and sr_1d.get('nearest_zones'):
                nearest_support = sr_1d['nearest_zones'].get('support')
                nearest_resistance = sr_1d['nearest_zones'].get('resistance')
                stats = sr_1d['statistics']
                
                sr_text += f"""  1D Timeframe:
    Active Support Zones: {stats['active_support_zones']} | Resistance Zones: {stats['active_resistance_zones']}
    Break Rate: Support {stats['break_rate_support_percent']:.0f}% | Resistance {stats['break_rate_resistance_percent']:.0f}%
"""
                if nearest_support:
                    sr_text += f"    Nearest Support: ${nearest_support['price']:,.4f} (Volume: {nearest_support['volume_ratio']:.1f}x avg)\n"
                if nearest_resistance:
                    sr_text += f"    Nearest Resistance: ${nearest_resistance['price']:,.4f} (Volume: {nearest_resistance['volume_ratio']:.1f}x avg)\n"
            
            if sr_4h and sr_4h.get('statistics'):
                stats = sr_4h['statistics']
                sr_text += f"""  4H Timeframe:
    Active: Support {stats['active_support_zones']} | Resistance {stats['active_resistance_zones']}
"""
        
        # Smart Money Concepts
        smc_text = "Smart Money Concepts data unavailable"
        if data.get('smart_money_concepts'):
            smc_1d = data['smart_money_concepts'].get('1d')
            smc_4h = data['smart_money_concepts'].get('4h')
            
            smc_text = "Smart Money Concepts (Market Structure):\n"
            if smc_1d:
                swing_trend = smc_1d['swing_structure']['trend'] or 'NEUTRAL'
                structure_bias = smc_1d['structure_bias']
                stats = smc_1d['statistics']
                
                bias_info = self.smc_analyzer.get_trading_bias(smc_1d)
                
                smc_text += f"""  1D Timeframe:
    Swing Trend: {swing_trend} | Structure Bias: {structure_bias}
    BOS (Break of Structure): Bullish {stats['recent_bullish_bos']} | Bearish {stats['recent_bearish_bos']}
    CHoCH (Change of Character): Bullish {stats['recent_bullish_choch']} | Bearish {stats['recent_bearish_choch']}
    EQH/EQL: {stats['eqh_count']} Equal Highs | {stats['eql_count']} Equal Lows
    Trading Bias: {bias_info['bias']} (Confidence: {bias_info['confidence']}%)
    Reason: {bias_info['reason']}
"""
            
            if smc_4h:
                swing_trend = smc_4h['swing_structure']['trend'] or 'NEUTRAL'
                structure_bias = smc_4h['structure_bias']
                
                smc_text += f"""  4H Timeframe:
    Trend: {swing_trend} | Bias: {structure_bias}
"""
        
        # Build full prompt
        prompt = f"""You are an expert cryptocurrency trading analyst with 10+ years of experience in technical analysis and market psychology.

TRADING STYLE: {trading_style.upper()}
- If scalping: Focus on 1m-15m timeframes, quick entries/exits, tight stop losses
- If swing: Focus on 4h-1D timeframes, position holding 2-7 days, wider stop losses

ANALYZE THIS CRYPTOCURRENCY:

SYMBOL: {symbol}
CURRENT PRICE: ${market['price']:,.2f}

═══════════════════════════════════════════
📊 TECHNICAL INDICATORS (Multi-Timeframe)
═══════════════════════════════════════════

RSI + MFI Analysis:
{rsi_mfi_text}

Stochastic + RSI Analysis:
{stoch_text}

═══════════════════════════════════════════
🚀 PUMP SIGNAL ANALYSIS
═══════════════════════════════════════════
{pump_text}

═══════════════════════════════════════════
🏛️ INSTITUTIONAL INDICATORS
═══════════════════════════════════════════
{vp_text}

{fvg_text}

{ob_text}

{sr_text}

{smc_text}

═══════════════════════════════════════════
💧 VOLUME ANALYSIS
═══════════════════════════════════════════
  24h Volume: ${volume['current']:,.0f} USDT
  24h Trades: {volume['trades']:,}
  Base Volume: {volume['base_volume']:,.4f}

═══════════════════════════════════════════
📈 HISTORICAL COMPARISON (vs Last Week)
═══════════════════════════════════════════
{hist_text}

═══════════════════════════════════════════
📉 24H MARKET DATA
═══════════════════════════════════════════
  Price Change: {market['price_change_24h']:+.2f}%
  24h High: ${market['high_24h']:,.2f}
  24h Low: ${market['low_24h']:,.2f}
  24h Volume: ${market['volume_24h']:,.0f} USDT

═══════════════════════════════════════════
🎯 YOUR TASK
═══════════════════════════════════════════

Provide a comprehensive trading analysis in JSON format with the following structure:

{{
  "recommendation": "BUY" | "SELL" | "HOLD" | "WAIT",
  "confidence": 0-100,
  "trading_style": "{trading_style}",
  "entry_point": price in USD,
  "stop_loss": price in USD,
  "take_profit": [target1, target2, target3],
  "expected_holding_period": "X hours/days",
  "risk_level": "LOW" | "MEDIUM" | "HIGH",
  "reasoning_vietnamese": "Chi tiết phân tích bằng tiếng Việt (300-500 từ)",
  "key_points": ["Point 1", "Point 2", ...],
  "conflicting_signals": ["Signal 1", "Signal 2", ...] or [],
  "warnings": ["Warning 1", ...] or [],
  "market_sentiment": "BULLISH" | "BEARISH" | "NEUTRAL",
  "technical_score": 0-100,
  "fundamental_score": 0-100
}}

IMPORTANT GUIDELINES:
1. Reasoning MUST be in Vietnamese language (300-500 words)
2. **Analyze ALL technical indicators systematically:**
   - RSI+MFI consensus and individual timeframe signals
   - Stochastic+RSI momentum across timeframes
   - Volume patterns and 24h trading activity
   - Pump detection signals (if >=80%, consider high risk/reward)
   - Previous candle patterns on H4 and D1 (wick analysis, body size, bullish/bearish)
3. **Candle Pattern Analysis (CRITICAL):**
   - D1/H4 previous candles show institutional behavior
   - Large wicks indicate rejection or absorption zones
   - Bullish candles with small upper wicks = continuation potential
   - Bearish candles with long lower wicks = support testing
   - Compare body size to average - larger bodies = stronger momentum
4. **Institutional Indicators (CRITICAL - Weight 40%):**
   - **Volume Profile**: Current price position relative to POC/VAH/VAL
     * PREMIUM (above VAH): Expect rejection or strong continuation
     * DISCOUNT (below VAL): Expect bounce or deeper correction
     * AT_POC: High reaction zone, strong S/R level
     * VALUE_AREA: Balanced, watch for breakout
   - **Fair Value Gaps (FVG)**: Imbalance zones where price moved too fast
     * Bullish FVG below price = support magnet (price tends to fill gaps)
     * Bearish FVG above price = resistance magnet
     * High fill rate (>70%) = reliable zones
   - **Order Blocks (OB)**: Institutional accumulation/distribution zones
     * Swing OBs = major institutional levels (higher timeframe)
     * Internal OBs = minor levels (lower timeframe)
     * Active (non-mitigated) OBs act as strong support/resistance
   - **Support/Resistance**: High volume zones with delta volume
     * Volume ratio >2x = very strong zone
     * Broken + retested zones = reliable entry points
   - **Smart Money Concepts (SMC)**: Market structure analysis
     * BOS (Break of Structure) = trend continuation signal
     * CHoCH (Change of Character) = potential reversal signal
     * EQH/EQL = accumulation zones, expect breakout
     * Aligned trends (swing + internal) = high confidence
5. Weight high-confidence pump signals (>=80%) heavily but note dump risk
6. Be specific with entry/exit points based on current price and institutional zones
7. Identify conflicting signals between different timeframes and indicator types explicitly
8. Adjust recommendations based on trading style:
   - **Scalping**: Tight stops (1-2%), quick 3-5% targets, 1-4 hour holding, focus on 4H FVG/OB
   - **Swing**: Wider stops (3-5%), 10-20% targets, 3-7 day holding, focus on 1D Volume Profile/SMC
9. Consider historical trends - strong week-over-week growth is bullish indicator
10. Be conservative - if major conflicting signals exist, recommend WAIT
11. **Scoring methodology (UPDATED):**
    - Technical score = RSI+MFI (15%) + Stoch+RSI (15%) + Volume (10%) + Candles (10%) + Volume Profile (15%) + FVG (10%) + OB (10%) + S/R (10%) + SMC (15%)
    - Fundamental score = volume strength (40%), liquidity (30%), market sentiment (30%)
12. **Entry/Exit Recommendations:**
    - Entry: Near VAL, bullish FVG, bullish OB, support zones
    - Stop Loss: Below nearest support (OB/S/R zone) with 1-2 ATR buffer
    - Take Profit: At VAH, bearish FVG, resistance zones, EQH levels

Return ONLY valid JSON, no markdown formatting.
"""
        
        return prompt
    
    def analyze(self, symbol: str, pump_data: Optional[Dict] = None, 
                trading_style: str = 'swing', use_cache: bool = True) -> Optional[Dict]:
        """
        Perform AI analysis using Gemini
        
        Args:
            symbol: Trading symbol
            pump_data: Optional pump detector data
            trading_style: 'scalping' or 'swing'
            use_cache: Whether to use cached results
            
        Returns:
            Analysis result dict or None
        """
        try:
            # Check cache first
            if use_cache:
                cached = self._check_cache(symbol)
                if cached:
                    return cached
            
            logger.info(f"Starting Gemini AI analysis for {symbol} ({trading_style})")
            
            # Collect data
            data = self.collect_data(symbol, pump_data)
            if not data:
                logger.error(f"Failed to collect data for {symbol}")
                return None
            
            # Build prompt
            prompt = self._build_prompt(data, trading_style)
            
            # Rate limit
            self._rate_limit()
            
            # Call Gemini API
            logger.info(f"Calling Gemini API for {symbol}...")
            response = self.model.generate_content(prompt)
            
            if not response or not response.text:
                logger.error(f"Empty response from Gemini for {symbol}")
                return None
            
            # Parse JSON response
            response_text = response.text.strip()
            
            # Remove markdown code blocks if present
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.startswith('```'):
                response_text = response_text[3:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            
            response_text = response_text.strip()
            
            # Parse JSON
            analysis = json.loads(response_text)
            
            # Add metadata
            analysis['symbol'] = symbol
            analysis['analyzed_at'] = datetime.now().isoformat()
            analysis['data_used'] = {
                'rsi_mfi_consensus': data['rsi_mfi'].get('consensus', 'N/A'),
                'stoch_rsi_consensus': data['stoch_rsi'].get('consensus', 'N/A'),
                'pump_score': pump_data.get('final_score', 0) if pump_data else 0,
                'current_price': data['market_data']['price']
            }
            
            # Cache result
            self._update_cache(symbol, analysis)
            
            logger.info(f"Gemini analysis complete for {symbol}: {analysis['recommendation']} (confidence: {analysis['confidence']}%)")
            
            return analysis
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini response for {symbol}: {e}")
            logger.error(f"Response text: {response_text[:500]}...")
            return None
        except Exception as e:
            logger.error(f"Error in Gemini analysis for {symbol}: {e}")
            return None
    
    def format_response(self, analysis: Dict) -> Tuple[str, str, str]:
        """
        Format analysis into 3 separate messages
        
        Args:
            analysis: Analysis result from Gemini
            
        Returns:
            Tuple of (summary_msg, technical_msg, reasoning_msg)
        """
        try:
            symbol = analysis['symbol']
            rec = analysis['recommendation']
            conf = analysis['confidence']
            entry = analysis['entry_point']
            stop = analysis['stop_loss']
            targets = analysis['take_profit']
            period = analysis['expected_holding_period']
            risk = analysis['risk_level']
            style = analysis.get('trading_style', 'swing')
            
            # Message 1: Summary
            rec_emoji = "🟢" if rec == "BUY" else "🔴" if rec == "SELL" else "🟡" if rec == "HOLD" else "⚪"
            
            summary = f"<b>🤖 GEMINI AI ANALYSIS</b>\n\n"
            summary += f"<b>💎 {symbol}</b>\n"
            summary += f"<b>📊 Trading Style: {style.upper()}</b>\n\n"
            summary += f"{rec_emoji} <b>RECOMMENDATION: {rec}</b>\n"
            summary += f"<b>🎯 Confidence: {conf}%</b>\n"
            summary += f"<b>⚠️ Risk Level: {risk}</b>\n\n"
            
            summary += f"<b>💰 TRADING PLAN:</b>\n"
            summary += f"   • Entry: ${self.binance.format_price(symbol, entry)}\n"
            summary += f"   • Stop Loss: ${self.binance.format_price(symbol, stop)}\n"
            summary += f"   • Take Profit:\n"
            for i, target in enumerate(targets, 1):
                summary += f"     TP{i}: ${self.binance.format_price(symbol, target)}\n"
            summary += f"   • Holding: {period}\n"
            
            # Message 2: Technical Details
            tech = f"<b>📊 TECHNICAL ANALYSIS DETAILS</b>\n\n"
            tech += f"<b>💎 {symbol}</b>\n\n"
            
            # Data used
            data_used = analysis.get('data_used', {})
            tech += f"<b>🔍 Indicators Used:</b>\n"
            tech += f"   • RSI+MFI: {data_used.get('rsi_mfi_consensus', 'N/A')}\n"
            tech += f"   • Stoch+RSI: {data_used.get('stoch_rsi_consensus', 'N/A')}\n"
            
            pump_score = data_used.get('pump_score', 0)
            if pump_score >= 80:
                tech += f"   • 🚀 Pump Signal: {pump_score:.0f}% (High Confidence)\n"
            elif pump_score > 0:
                tech += f"   • Pump Signal: {pump_score:.0f}%\n"
            
            tech += f"   • Current Price: ${self.binance.format_price(symbol, data_used.get('current_price', 0))}\n\n"
            
            # Scores
            tech_score = analysis.get('technical_score', 0)
            fund_score = analysis.get('fundamental_score', 0)
            
            tech += f"<b>📈 Scores:</b>\n"
            tech += f"   • Technical: {tech_score}/100\n"
            tech += f"   • Fundamental: {fund_score}/100\n"
            tech += f"   • Overall: {(tech_score + fund_score)/2:.0f}/100\n\n"
            
            # Market sentiment
            sentiment = analysis.get('market_sentiment', 'NEUTRAL')
            sentiment_emoji = "🟢" if sentiment == "BULLISH" else "🔴" if sentiment == "BEARISH" else "🟡"
            tech += f"<b>💭 Market Sentiment:</b> {sentiment_emoji} {sentiment}\n\n"
            
            # Key points
            tech += f"<b>🎯 Key Points:</b>\n"
            for point in analysis.get('key_points', []):
                tech += f"   ✓ {point}\n"
            
            # Conflicting signals
            conflicts = analysis.get('conflicting_signals', [])
            if conflicts:
                tech += f"\n<b>⚠️ Conflicting Signals:</b>\n"
                for conflict in conflicts:
                    tech += f"   • {conflict}\n"
            
            # Warnings
            warnings = analysis.get('warnings', [])
            if warnings:
                tech += f"\n<b>🚨 Warnings:</b>\n"
                for warning in warnings:
                    tech += f"   ⚠️ {warning}\n"
            
            # Message 3: AI Reasoning
            reasoning = f"<b>🧠 AI DETAILED REASONING</b>\n\n"
            reasoning += f"<b>💎 {symbol}</b>\n\n"
            reasoning += analysis.get('reasoning_vietnamese', 'Không có phân tích chi tiết.')
            reasoning += f"\n\n<b>⏰ Analyzed at:</b> {analysis.get('analyzed_at', 'N/A')}"
            reasoning += f"\n<b>🤖 Model:</b> Gemini 2.5 Pro"
            reasoning += f"\n\n<i>⚠️ Đây là phân tích AI, không phải tư vấn tài chính. Luôn DYOR (Do Your Own Research).</i>"
            
            return summary, tech, reasoning
            
        except Exception as e:
            logger.error(f"Error formatting response: {e}")
            error_msg = f"❌ Lỗi khi format kết quả AI analysis: {str(e)}"
            return error_msg, "", ""
