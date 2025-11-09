"""
Order Blocks (OB) Detector
Converted from Pine Script: Order Blocks & Fair Value Gaps by LuxAlgo

Detects institutional Order Blocks - last opposite candle before 
structure break, representing accumulation/distribution zones.

Author: AI Assistant
Date: November 9, 2025
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class OrderBlockDetector:
    """
    Order Block detection for cryptocurrency trading
    
    Order Blocks represent institutional footprints where smart money
    accumulated/distributed before major price moves.
    
    Types:
    - Swing Order Blocks: Based on longer swing pivots (50-period default)
    - Internal Order Blocks: Based on shorter pivots (5-period default)
    """
    
    def __init__(self, binance_client, 
                 swing_length: int = 50,
                 internal_length: int = 5,
                 use_atr_filter: bool = True,
                 atr_period: int = 14,
                 atr_multiplier: float = 0.1):
        """
        Initialize Order Block detector
        
        Args:
            binance_client: BinanceClient instance
            swing_length: Period for swing pivot detection (default: 50)
            internal_length: Period for internal pivot detection (default: 5)
            use_atr_filter: Filter small OBs using ATR (default: True)
            atr_period: ATR calculation period (default: 14)
            atr_multiplier: ATR multiplier for filtering (default: 0.1)
        """
        self.binance = binance_client
        self.swing_length = swing_length
        self.internal_length = internal_length
        self.use_atr_filter = use_atr_filter
        self.atr_period = atr_period
        self.atr_multiplier = atr_multiplier
        
        logger.info(f"Order Block detector initialized (swing={swing_length}, internal={internal_length})")
    
    def _calculate_atr(self, df: pd.DataFrame) -> pd.Series:
        """Calculate Average True Range"""
        try:
            high = df['high']
            low = df['low']
            close = df['close']
            
            tr1 = high - low
            tr2 = abs(high - close.shift(1))
            tr3 = abs(low - close.shift(1))
            
            tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            atr = tr.rolling(window=self.atr_period).mean()
            
            return atr
        except Exception as e:
            logger.error(f"Error calculating ATR: {e}")
            return pd.Series(dtype=float)
    
    def _find_swing_highs_lows(self, df: pd.DataFrame, length: int) -> Tuple[pd.Series, pd.Series]:
        """
        Find swing highs and lows
        
        Args:
            df: DataFrame with OHLCV data
            length: Period for pivot detection
            
        Returns:
            Tuple of (swing_highs, swing_lows) as Series
        """
        try:
            high = df['high']
            low = df['low']
            
            swing_highs = pd.Series(index=df.index, dtype=float)
            swing_lows = pd.Series(index=df.index, dtype=float)
            
            # Find swing highs (highest high in window)
            for i in range(length, len(df) - length):
                window = high[i-length:i+length+1]
                if high.iloc[i] == window.max():
                    swing_highs.iloc[i] = high.iloc[i]
            
            # Find swing lows (lowest low in window)
            for i in range(length, len(df) - length):
                window = low[i-length:i+length+1]
                if low.iloc[i] == window.min():
                    swing_lows.iloc[i] = low.iloc[i]
            
            return swing_highs, swing_lows
            
        except Exception as e:
            logger.error(f"Error finding swing highs/lows: {e}")
            return pd.Series(dtype=float), pd.Series(dtype=float)
    
    def _detect_order_blocks(self, df: pd.DataFrame, pivot_length: int, ob_type: str) -> List[Dict]:
        """
        Detect Order Blocks based on swing pivots
        
        Args:
            df: DataFrame with OHLCV data
            pivot_length: Period for pivot detection
            ob_type: 'SWING' or 'INTERNAL'
            
        Returns:
            List of Order Block dictionaries
        """
        try:
            order_blocks = []
            
            # Find swing points
            swing_highs, swing_lows = self._find_swing_highs_lows(df, pivot_length)
            
            # Calculate ATR if filtering enabled
            atr = self._calculate_atr(df) if self.use_atr_filter else None
            
            current_price = float(df['close'].iloc[-1])
            
            # Track market structure
            last_swing_high = None
            last_swing_low = None
            
            for i in range(len(df)):
                # Update swing points
                if not pd.isna(swing_highs.iloc[i]):
                    last_swing_high = float(swing_highs.iloc[i])
                
                if not pd.isna(swing_lows.iloc[i]):
                    last_swing_low = float(swing_lows.iloc[i])
                
                # Need both swing points to detect structure break
                if last_swing_high is None or last_swing_low is None:
                    continue
                
                # Detect Bullish Order Block (break of swing high)
                if i > 0 and float(df['close'].iloc[i]) > last_swing_high:
                    # Find last bearish candle before break (opposite candle)
                    for j in range(i-1, max(0, i-10), -1):
                        open_j = float(df['open'].iloc[j])
                        close_j = float(df['close'].iloc[j])
                        high_j = float(df['high'].iloc[j])
                        low_j = float(df['low'].iloc[j])
                        
                        if close_j < open_j:  # Bearish candle
                            ob_top = high_j
                            ob_bottom = low_j
                            ob_size = ob_top - ob_bottom
                            
                            # Apply ATR filter
                            if self.use_atr_filter and atr is not None:
                                threshold = float(atr.iloc[j]) * self.atr_multiplier
                                if ob_size < threshold:
                                    continue
                            
                            # Check if already mitigated (price went back below OB)
                            mitigated = False
                            for k in range(j+1, len(df)):
                                if float(df['low'].iloc[k]) < ob_bottom:
                                    mitigated = True
                                    break
                            
                            distance_to_top = ((ob_top - current_price) / current_price * 100)
                            distance_to_bottom = ((ob_bottom - current_price) / current_price * 100)
                            
                            order_blocks.append({
                                'type': ob_type,
                                'bias': 'BULLISH',
                                'top': ob_top,
                                'bottom': ob_bottom,
                                'midpoint': (ob_top + ob_bottom) / 2.0,
                                'size': ob_size,
                                'size_percentage': (ob_size / ob_bottom * 100) if ob_bottom > 0 else 0,
                                'bar_index': j,
                                'mitigated': mitigated,
                                'distance_to_top_percent': distance_to_top,
                                'distance_to_bottom_percent': distance_to_bottom,
                                'status': 'MITIGATED' if mitigated else 'ACTIVE'
                            })
                            break
                
                # Detect Bearish Order Block (break of swing low)
                if i > 0 and float(df['close'].iloc[i]) < last_swing_low:
                    # Find last bullish candle before break (opposite candle)
                    for j in range(i-1, max(0, i-10), -1):
                        open_j = float(df['open'].iloc[j])
                        close_j = float(df['close'].iloc[j])
                        high_j = float(df['high'].iloc[j])
                        low_j = float(df['low'].iloc[j])
                        
                        if close_j > open_j:  # Bullish candle
                            ob_top = high_j
                            ob_bottom = low_j
                            ob_size = ob_top - ob_bottom
                            
                            # Apply ATR filter
                            if self.use_atr_filter and atr is not None:
                                threshold = float(atr.iloc[j]) * self.atr_multiplier
                                if ob_size < threshold:
                                    continue
                            
                            # Check if already mitigated (price went back above OB)
                            mitigated = False
                            for k in range(j+1, len(df)):
                                if float(df['high'].iloc[k]) > ob_top:
                                    mitigated = True
                                    break
                            
                            distance_to_top = ((ob_top - current_price) / current_price * 100)
                            distance_to_bottom = ((ob_bottom - current_price) / current_price * 100)
                            
                            order_blocks.append({
                                'type': ob_type,
                                'bias': 'BEARISH',
                                'top': ob_top,
                                'bottom': ob_bottom,
                                'midpoint': (ob_top + ob_bottom) / 2.0,
                                'size': ob_size,
                                'size_percentage': (ob_size / ob_top * 100) if ob_top > 0 else 0,
                                'bar_index': j,
                                'mitigated': mitigated,
                                'distance_to_top_percent': distance_to_top,
                                'distance_to_bottom_percent': distance_to_bottom,
                                'status': 'MITIGATED' if mitigated else 'ACTIVE'
                            })
                            break
            
            return order_blocks
            
        except Exception as e:
            logger.error(f"Error detecting order blocks: {e}")
            return []
    
    def detect_order_blocks(self, df: pd.DataFrame, max_blocks: int = 5) -> Optional[Dict]:
        """
        Detect both Swing and Internal Order Blocks
        
        Args:
            df: DataFrame with OHLCV data
            max_blocks: Maximum number of active OBs to return per type
            
        Returns:
            Dict with Swing and Internal Order Blocks
        """
        try:
            if df is None or df.empty or len(df) < self.swing_length + 10:
                logger.warning("Insufficient data for Order Block detection")
                return None
            
            # Ensure numeric types
            df = df.copy()
            df['high'] = pd.to_numeric(df['high'], errors='coerce')
            df['low'] = pd.to_numeric(df['low'], errors='coerce')
            df['close'] = pd.to_numeric(df['close'], errors='coerce')
            df['open'] = pd.to_numeric(df['open'], errors='coerce')
            
            current_price = float(df['close'].iloc[-1])
            
            # Detect Swing Order Blocks (longer timeframe structure)
            swing_obs = self._detect_order_blocks(df, self.swing_length, 'SWING')
            
            # Detect Internal Order Blocks (shorter timeframe structure)
            internal_obs = self._detect_order_blocks(df, self.internal_length, 'INTERNAL')
            
            # Filter only active (non-mitigated) blocks
            active_swing = [ob for ob in swing_obs if not ob['mitigated']]
            active_internal = [ob for ob in internal_obs if not ob['mitigated']]
            
            # Sort by proximity to current price
            active_swing = sorted(active_swing, 
                                 key=lambda x: abs(x['midpoint'] - current_price))[:max_blocks]
            active_internal = sorted(active_internal, 
                                    key=lambda x: abs(x['midpoint'] - current_price))[:max_blocks]
            
            # Find nearest blocks
            nearest_swing = None
            nearest_internal = None
            
            if active_swing:
                nearest_swing = min(active_swing, 
                                   key=lambda x: abs(x['midpoint'] - current_price))
            
            if active_internal:
                nearest_internal = min(active_internal, 
                                      key=lambda x: abs(x['midpoint'] - current_price))
            
            # Calculate statistics
            total_swing = len(swing_obs)
            total_internal = len(internal_obs)
            mitigated_swing = len([ob for ob in swing_obs if ob['mitigated']])
            mitigated_internal = len([ob for ob in internal_obs if ob['mitigated']])
            
            mitigation_rate_swing = (mitigated_swing / total_swing * 100) if total_swing > 0 else 0
            mitigation_rate_internal = (mitigated_internal / total_internal * 100) if total_internal > 0 else 0
            
            return {
                'swing_order_blocks': active_swing,
                'internal_order_blocks': active_internal,
                'statistics': {
                    'total_swing_obs': total_swing,
                    'total_internal_obs': total_internal,
                    'active_swing_obs': len(active_swing),
                    'active_internal_obs': len(active_internal),
                    'mitigated_swing_obs': mitigated_swing,
                    'mitigated_internal_obs': mitigated_internal,
                    'mitigation_rate_swing_percent': mitigation_rate_swing,
                    'mitigation_rate_internal_percent': mitigation_rate_internal
                },
                'nearest_blocks': {
                    'swing': nearest_swing,
                    'internal': nearest_internal
                },
                'current_price': current_price
            }
            
        except Exception as e:
            logger.error(f"Error in Order Block detection: {e}")
            return None
    
    def analyze_multi_timeframe(self, symbol: str, timeframes: List[str] = None) -> Dict:
        """
        Detect Order Blocks across multiple timeframes
        
        Args:
            symbol: Trading symbol
            timeframes: List of timeframes (default: ['4h', '1d'])
            
        Returns:
            Dict with OB analysis for each timeframe
        """
        try:
            if timeframes is None:
                timeframes = ['4h', '1d']
            
            results = {}
            
            for tf in timeframes:
                # Need more data for swing detection
                limit = 200 if self.swing_length > 50 else 150
                df = self.binance.get_klines(symbol, tf, limit=limit)
                
                if df is not None and not df.empty:
                    obs = self.detect_order_blocks(df)
                    if obs:
                        results[tf] = obs
                        
                        swing_count = obs['statistics']['active_swing_obs']
                        internal_count = obs['statistics']['active_internal_obs']
                        logger.info(f"Order Blocks {symbol} {tf}: {swing_count} swing, {internal_count} internal active")
            
            return results
            
        except Exception as e:
            logger.error(f"Error in multi-timeframe OB analysis: {e}")
            return {}
    
    def is_price_near_ob(self, current_price: float, obs: Dict, proximity_percent: float = 1.0) -> Dict:
        """
        Check if current price is near any Order Block
        
        Args:
            current_price: Current market price
            obs: Order Blocks dict from detect_order_blocks()
            proximity_percent: Consider "near" if within this % (default: 1.0%)
            
        Returns:
            Dict with nearby OB information
        """
        try:
            if not obs:
                return {'near_ob': False}
            
            nearby_swing = []
            nearby_internal = []
            
            # Check swing OBs
            for ob in obs.get('swing_order_blocks', []):
                distance = abs((ob['midpoint'] - current_price) / current_price * 100)
                if distance <= proximity_percent:
                    nearby_swing.append({
                        **ob,
                        'distance_percent': distance
                    })
            
            # Check internal OBs
            for ob in obs.get('internal_order_blocks', []):
                distance = abs((ob['midpoint'] - current_price) / current_price * 100)
                if distance <= proximity_percent:
                    nearby_internal.append({
                        **ob,
                        'distance_percent': distance
                    })
            
            has_nearby = len(nearby_swing) > 0 or len(nearby_internal) > 0
            
            # Determine bias
            bullish_count = len([ob for ob in nearby_swing + nearby_internal if ob['bias'] == 'BULLISH'])
            bearish_count = len([ob for ob in nearby_swing + nearby_internal if ob['bias'] == 'BEARISH'])
            
            bias = 'BULLISH_SUPPORT' if bullish_count > bearish_count else 'BEARISH_RESISTANCE' if bearish_count > bullish_count else 'NEUTRAL'
            
            return {
                'near_ob': has_nearby,
                'nearby_swing_obs': nearby_swing,
                'nearby_internal_obs': nearby_internal,
                'count': len(nearby_swing) + len(nearby_internal),
                'bias': bias
            }
            
        except Exception as e:
            logger.error(f"Error checking OB proximity: {e}")
            return {'near_ob': False}
