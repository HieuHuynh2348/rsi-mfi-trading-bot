"""
Smart Money Concepts (SMC) Analyzer
Converted from Pine Script: Smartmoneyconcept by LuxAlgo

Detects institutional trading patterns through market structure analysis:
- BOS (Break of Structure)
- CHoCH (Change of Character)
- Internal vs Swing structure
- EQH/EQL (Equal High/Low)

Author: AI Assistant
Date: November 9, 2025
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class SmartMoneyAnalyzer:
    """
    Smart Money Concepts analysis for cryptocurrency trading
    
    Identifies institutional footprints through market structure:
    
    BOS (Break of Structure):
    - Bullish BOS: Price breaks previous swing high in uptrend
    - Bearish BOS: Price breaks previous swing low in downtrend
    - Continuation pattern
    
    CHoCH (Change of Character):
    - Price breaks counter-trend structure
    - Potential trend reversal signal
    
    EQH/EQL (Equal High/Low):
    - Multiple swing points at same level
    - Accumulation/distribution zones
    """
    
    def __init__(self, binance_client,
                 swing_length: int = 33,
                 internal_length: int = 5,
                 eqh_eql_threshold_percent: float = 0.5):
        """
        Initialize Smart Money analyzer
        
        Args:
            binance_client: BinanceClient instance
            swing_length: Period for swing structure detection (default: 33)
            internal_length: Period for internal structure detection (default: 5)
            eqh_eql_threshold_percent: Threshold for equal high/low detection (default: 0.5%)
        """
        self.binance = binance_client
        self.swing_length = swing_length
        self.internal_length = internal_length
        self.eqh_eql_threshold = eqh_eql_threshold_percent / 100.0
        
        logger.info(f"Smart Money analyzer initialized (swing={swing_length}, internal={internal_length})")
    
    def _find_swing_points(self, df: pd.DataFrame, length: int) -> Tuple[pd.Series, pd.Series]:
        """
        Find swing highs and lows
        
        Returns:
            Tuple of (swing_highs, swing_lows)
        """
        try:
            high = df['high']
            low = df['low']
            
            swing_highs = pd.Series(index=df.index, dtype=float)
            swing_lows = pd.Series(index=df.index, dtype=float)
            
            # Find swing highs
            for i in range(length, len(df) - length):
                window = high[i-length:i+length+1]
                if high.iloc[i] == window.max():
                    swing_highs.iloc[i] = high.iloc[i]
            
            # Find swing lows
            for i in range(length, len(df) - length):
                window = low[i-length:i+length+1]
                if low.iloc[i] == window.min():
                    swing_lows.iloc[i] = low.iloc[i]
            
            return swing_highs, swing_lows
            
        except Exception as e:
            logger.error(f"Error finding swing points: {e}")
            return pd.Series(dtype=float), pd.Series(dtype=float)
    
    def _detect_equal_levels(self, levels: List[float], threshold: float) -> List[Dict]:
        """
        Detect equal high/low levels (multiple touches at same price)
        
        Args:
            levels: List of price levels
            threshold: Threshold for considering levels equal (as ratio)
            
        Returns:
            List of equal level groups
        """
        try:
            if not levels or len(levels) < 2:
                return []
            
            equal_groups = []
            used_indices = set()
            
            for i in range(len(levels)):
                if i in used_indices:
                    continue
                
                group = [levels[i]]
                group_indices = [i]
                
                for j in range(i+1, len(levels)):
                    if j in used_indices:
                        continue
                    
                    # Check if levels are equal within threshold
                    diff_percent = abs(levels[j] - levels[i]) / levels[i]
                    if diff_percent <= threshold:
                        group.append(levels[j])
                        group_indices.append(j)
                
                if len(group) >= 2:  # At least 2 equal levels
                    used_indices.update(group_indices)
                    equal_groups.append({
                        'price': sum(group) / len(group),  # Average price
                        'count': len(group),
                        'levels': group
                    })
            
            return equal_groups
            
        except Exception as e:
            logger.error(f"Error detecting equal levels: {e}")
            return []
    
    def _analyze_market_structure(self, df: pd.DataFrame, length: int, structure_type: str) -> Dict:
        """
        Analyze market structure (BOS, CHoCH detection)
        
        Args:
            df: DataFrame with OHLCV data
            length: Period for swing detection
            structure_type: 'SWING' or 'INTERNAL'
            
        Returns:
            Dict with structure analysis
        """
        try:
            swing_highs, swing_lows = self._find_swing_points(df, length)
            
            bos_levels = []
            choch_levels = []
            current_trend = None  # 'BULLISH' or 'BEARISH'
            
            last_swing_high = None
            last_swing_low = None
            prev_swing_high = None
            prev_swing_low = None
            
            for i in range(len(df)):
                high_i = float(df['high'].iloc[i])
                low_i = float(df['low'].iloc[i])
                close_i = float(df['close'].iloc[i])
                
                # Update swing points
                if not pd.isna(swing_highs.iloc[i]):
                    prev_swing_high = last_swing_high
                    last_swing_high = float(swing_highs.iloc[i])
                
                if not pd.isna(swing_lows.iloc[i]):
                    prev_swing_low = last_swing_low
                    last_swing_low = float(swing_lows.iloc[i])
                
                # Need at least one previous swing point
                if last_swing_high is None or last_swing_low is None:
                    continue
                
                # Detect structure breaks
                
                # Bullish BOS: Price breaks previous swing high in uptrend
                if current_trend == 'BULLISH' and prev_swing_high is not None:
                    if close_i > prev_swing_high:
                        bos_levels.append({
                            'type': 'BOS',
                            'bias': 'BULLISH',
                            'price': prev_swing_high,
                            'bar_index': i,
                            'structure_type': structure_type
                        })
                
                # Bearish BOS: Price breaks previous swing low in downtrend
                if current_trend == 'BEARISH' and prev_swing_low is not None:
                    if close_i < prev_swing_low:
                        bos_levels.append({
                            'type': 'BOS',
                            'bias': 'BEARISH',
                            'price': prev_swing_low,
                            'bar_index': i,
                            'structure_type': structure_type
                        })
                
                # CHoCH: Change of Character (counter-trend break)
                
                # Bullish CHoCH: Price breaks swing high while in downtrend
                if current_trend == 'BEARISH' or current_trend is None:
                    if last_swing_high is not None and close_i > last_swing_high:
                        choch_levels.append({
                            'type': 'CHoCH',
                            'bias': 'BULLISH',
                            'price': last_swing_high,
                            'bar_index': i,
                            'structure_type': structure_type
                        })
                        current_trend = 'BULLISH'
                
                # Bearish CHoCH: Price breaks swing low while in uptrend
                if current_trend == 'BULLISH' or current_trend is None:
                    if last_swing_low is not None and close_i < last_swing_low:
                        choch_levels.append({
                            'type': 'CHoCH',
                            'bias': 'BEARISH',
                            'price': last_swing_low,
                            'bar_index': i,
                            'structure_type': structure_type
                        })
                        current_trend = 'BEARISH'
            
            # Detect Equal Highs (EQH)
            all_swing_highs = [float(h) for h in swing_highs.dropna()]
            eqh_groups = self._detect_equal_levels(all_swing_highs, self.eqh_eql_threshold)
            
            # Detect Equal Lows (EQL)
            all_swing_lows = [float(l) for l in swing_lows.dropna()]
            eql_groups = self._detect_equal_levels(all_swing_lows, self.eqh_eql_threshold)
            
            return {
                'trend': current_trend,
                'bos_levels': bos_levels,
                'choch_levels': choch_levels,
                'eqh_groups': eqh_groups,
                'eql_groups': eql_groups,
                'last_swing_high': last_swing_high,
                'last_swing_low': last_swing_low
            }
            
        except Exception as e:
            logger.error(f"Error analyzing market structure: {e}")
            return {
                'trend': None,
                'bos_levels': [],
                'choch_levels': [],
                'eqh_groups': [],
                'eql_groups': [],
                'last_swing_high': None,
                'last_swing_low': None
            }
    
    def analyze_smart_money_concepts(self, df: pd.DataFrame, max_levels: int = 5) -> Optional[Dict]:
        """
        Comprehensive Smart Money Concepts analysis
        
        Args:
            df: DataFrame with OHLCV data
            max_levels: Maximum number of recent BOS/CHoCH to return
            
        Returns:
            Dict with SMC analysis
        """
        try:
            if df is None or df.empty or len(df) < self.swing_length + 10:
                logger.warning("Insufficient data for SMC analysis")
                return None
            
            # Ensure numeric types
            df = df.copy()
            df['high'] = pd.to_numeric(df['high'], errors='coerce')
            df['low'] = pd.to_numeric(df['low'], errors='coerce')
            df['close'] = pd.to_numeric(df['close'], errors='coerce')
            
            current_price = float(df['close'].iloc[-1])
            
            # Analyze Swing structure (higher timeframe perspective)
            swing_structure = self._analyze_market_structure(df, self.swing_length, 'SWING')
            
            # Analyze Internal structure (lower timeframe perspective)
            internal_structure = self._analyze_market_structure(df, self.internal_length, 'INTERNAL')
            
            # Get recent BOS/CHoCH levels
            recent_bos_swing = swing_structure['bos_levels'][-max_levels:] if swing_structure['bos_levels'] else []
            recent_choch_swing = swing_structure['choch_levels'][-max_levels:] if swing_structure['choch_levels'] else []
            recent_bos_internal = internal_structure['bos_levels'][-max_levels:] if internal_structure['bos_levels'] else []
            recent_choch_internal = internal_structure['choch_levels'][-max_levels:] if internal_structure['choch_levels'] else []
            
            # Find nearest important levels
            nearest_bos = None
            nearest_choch = None
            nearest_eqh = None
            nearest_eql = None
            
            all_bos = recent_bos_swing + recent_bos_internal
            all_choch = recent_choch_swing + recent_choch_internal
            
            if all_bos:
                nearest_bos = min(all_bos, key=lambda x: abs(x['price'] - current_price))
                nearest_bos['distance_percent'] = ((nearest_bos['price'] - current_price) / current_price * 100)
            
            if all_choch:
                nearest_choch = min(all_choch, key=lambda x: abs(x['price'] - current_price))
                nearest_choch['distance_percent'] = ((nearest_choch['price'] - current_price) / current_price * 100)
            
            if swing_structure['eqh_groups']:
                nearest_eqh = min(swing_structure['eqh_groups'], 
                                 key=lambda x: abs(x['price'] - current_price))
                nearest_eqh['distance_percent'] = ((nearest_eqh['price'] - current_price) / current_price * 100)
            
            if swing_structure['eql_groups']:
                nearest_eql = min(swing_structure['eql_groups'], 
                                 key=lambda x: abs(x['price'] - current_price))
                nearest_eql['distance_percent'] = ((nearest_eql['price'] - current_price) / current_price * 100)
            
            # Determine overall structure bias
            swing_trend = swing_structure['trend']
            internal_trend = internal_structure['trend']
            
            if swing_trend == internal_trend:
                structure_bias = f"{swing_trend}_ALIGNED"  # Strong trend
            elif swing_trend and internal_trend:
                structure_bias = f"{swing_trend}_SWING_{internal_trend}_INTERNAL"  # Divergence
            else:
                structure_bias = "NEUTRAL"
            
            # Count recent patterns
            recent_bullish_bos = len([b for b in all_bos if b['bias'] == 'BULLISH'])
            recent_bearish_bos = len([b for b in all_bos if b['bias'] == 'BEARISH'])
            recent_bullish_choch = len([c for c in all_choch if c['bias'] == 'BULLISH'])
            recent_bearish_choch = len([c for c in all_choch if c['bias'] == 'BEARISH'])
            
            return {
                'swing_structure': {
                    'trend': swing_structure['trend'],
                    'bos_levels': recent_bos_swing,
                    'choch_levels': recent_choch_swing,
                    'eqh_groups': swing_structure['eqh_groups'],
                    'eql_groups': swing_structure['eql_groups'],
                    'last_swing_high': swing_structure['last_swing_high'],
                    'last_swing_low': swing_structure['last_swing_low']
                },
                'internal_structure': {
                    'trend': internal_structure['trend'],
                    'bos_levels': recent_bos_internal,
                    'choch_levels': recent_choch_internal,
                    'last_swing_high': internal_structure['last_swing_high'],
                    'last_swing_low': internal_structure['last_swing_low']
                },
                'structure_bias': structure_bias,
                'nearest_levels': {
                    'bos': nearest_bos,
                    'choch': nearest_choch,
                    'eqh': nearest_eqh,
                    'eql': nearest_eql
                },
                'statistics': {
                    'total_bos': len(all_bos),
                    'total_choch': len(all_choch),
                    'recent_bullish_bos': recent_bullish_bos,
                    'recent_bearish_bos': recent_bearish_bos,
                    'recent_bullish_choch': recent_bullish_choch,
                    'recent_bearish_choch': recent_bearish_choch,
                    'eqh_count': len(swing_structure['eqh_groups']),
                    'eql_count': len(swing_structure['eql_groups'])
                },
                'current_price': current_price
            }
            
        except Exception as e:
            logger.error(f"Error in SMC analysis: {e}")
            return None
    
    def analyze_multi_timeframe(self, symbol: str, timeframes: List[str] = None) -> Dict:
        """
        Analyze Smart Money Concepts across multiple timeframes
        
        Args:
            symbol: Trading symbol
            timeframes: List of timeframes (default: ['4h', '1d'])
            
        Returns:
            Dict with SMC analysis for each timeframe
        """
        try:
            if timeframes is None:
                timeframes = ['4h', '1d']
            
            results = {}
            
            for tf in timeframes:
                # Need more data for structure analysis
                limit = 200 if self.swing_length > 30 else 150
                df = self.binance.get_klines(symbol, tf, limit=limit)
                
                if df is not None and not df.empty:
                    smc = self.analyze_smart_money_concepts(df)
                    if smc:
                        results[tf] = smc
                        
                        swing_trend = smc['swing_structure']['trend'] or 'NEUTRAL'
                        structure_bias = smc['structure_bias']
                        logger.info(f"SMC {symbol} {tf}: {swing_trend}, Bias: {structure_bias}")
            
            return results
            
        except Exception as e:
            logger.error(f"Error in multi-timeframe SMC analysis: {e}")
            return {}
    
    def get_trading_bias(self, smc: Dict) -> Dict:
        """
        Get actionable trading bias from SMC analysis
        
        Args:
            smc: SMC dict from analyze_smart_money_concepts()
            
        Returns:
            Dict with trading recommendations
        """
        try:
            if not smc:
                return {'bias': 'NEUTRAL', 'confidence': 0}
            
            swing_trend = smc['swing_structure']['trend']
            internal_trend = smc['internal_structure']['trend']
            structure_bias = smc['structure_bias']
            
            # Count recent bullish vs bearish signals
            stats = smc['statistics']
            bullish_score = stats['recent_bullish_bos'] + stats['recent_bullish_choch']
            bearish_score = stats['recent_bearish_bos'] + stats['recent_bearish_choch']
            
            # Calculate confidence
            total_signals = bullish_score + bearish_score
            if total_signals == 0:
                return {'bias': 'NEUTRAL', 'confidence': 0, 'reason': 'No clear structure breaks'}
            
            # Determine bias
            if swing_trend == 'BULLISH' and internal_trend == 'BULLISH':
                bias = 'STRONG_BULLISH'
                confidence = min(90, 60 + (bullish_score * 10))
                reason = 'Both swing and internal structure aligned bullish'
            elif swing_trend == 'BEARISH' and internal_trend == 'BEARISH':
                bias = 'STRONG_BEARISH'
                confidence = min(90, 60 + (bearish_score * 10))
                reason = 'Both swing and internal structure aligned bearish'
            elif swing_trend == 'BULLISH':
                bias = 'BULLISH'
                confidence = 50 + (bullish_score * 5)
                reason = 'Swing structure bullish, internal divergence'
            elif swing_trend == 'BEARISH':
                bias = 'BEARISH'
                confidence = 50 + (bearish_score * 5)
                reason = 'Swing structure bearish, internal divergence'
            elif bullish_score > bearish_score:
                bias = 'WEAK_BULLISH'
                confidence = 40
                reason = 'More bullish structure breaks recently'
            elif bearish_score > bullish_score:
                bias = 'WEAK_BEARISH'
                confidence = 40
                reason = 'More bearish structure breaks recently'
            else:
                bias = 'NEUTRAL'
                confidence = 20
                reason = 'Mixed signals, no clear direction'
            
            # Check for CHoCH (potential reversal)
            recent_choch = (stats['recent_bullish_choch'] > 0 or stats['recent_bearish_choch'] > 0)
            if recent_choch:
                reason += ' (CHoCH detected - potential reversal)'
            
            # Check for EQH/EQL (accumulation zones)
            if stats['eqh_count'] > 1:
                reason += f' (EQH x{stats["eqh_count"]} - resistance accumulation)'
            if stats['eql_count'] > 1:
                reason += f' (EQL x{stats["eql_count"]} - support accumulation)'
            
            return {
                'bias': bias,
                'confidence': min(100, confidence),
                'reason': reason,
                'swing_trend': swing_trend,
                'internal_trend': internal_trend,
                'structure_bias': structure_bias
            }
            
        except Exception as e:
            logger.error(f"Error getting trading bias: {e}")
            return {'bias': 'NEUTRAL', 'confidence': 0, 'reason': 'Error analyzing structure'}
