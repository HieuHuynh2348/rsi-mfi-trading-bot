"""
Fair Value Gaps (FVG) Detector
Converted from Pine Script: Order Blocks & Fair Value Gaps by LuxAlgo

Detects imbalance zones (Fair Value Gaps) where price moved too fast,
leaving unfilled areas that often act as support/resistance.

Author: AI Assistant
Date: November 9, 2025
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class FairValueGapDetector:
    """
    Fair Value Gap detection for cryptocurrency trading
    
    Fair Value Gaps occur when:
    - Bullish FVG: candle[2].high < candle[0].low (gap between old high and new low)
    - Bearish FVG: candle[2].low > candle[0].high (gap between old low and new high)
    
    These gaps represent imbalance zones where price moved rapidly,
    often returning to fill the gap later.
    """
    
    def __init__(self, binance_client, auto_threshold: bool = False, threshold_multiplier: float = 1.0):
        """
        Initialize Fair Value Gap detector
        
        Args:
            binance_client: BinanceClient instance
            auto_threshold: Use automatic gap size filtering based on ATR
            threshold_multiplier: Multiplier for ATR-based threshold (default: 1.0)
        """
        self.binance = binance_client
        self.auto_threshold = auto_threshold
        self.threshold_multiplier = threshold_multiplier
        
        logger.info(f"FVG detector initialized (auto_threshold={auto_threshold}, multiplier={threshold_multiplier})")
    
    def _calculate_atr(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate Average True Range"""
        try:
            high = df['high']
            low = df['low']
            close = df['close']
            
            tr1 = high - low
            tr2 = abs(high - close.shift(1))
            tr3 = abs(low - close.shift(1))
            
            tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            atr = tr.rolling(window=period).mean()
            
            return atr
        except Exception as e:
            logger.error(f"Error calculating ATR: {e}")
            return pd.Series(dtype=float)
    
    def detect_fvgs(self, df: pd.DataFrame, max_gaps: int = 10) -> Optional[Dict]:
        """
        Detect Fair Value Gaps in given OHLCV dataframe
        
        Args:
            df: DataFrame with OHLCV data
            max_gaps: Maximum number of unfilled gaps to track per direction
            
        Returns:
            Dict with bullish and bearish FVGs
        """
        try:
            if df is None or df.empty or len(df) < 4:
                logger.warning("Insufficient data for FVG detection")
                return None
            
            # Ensure numeric types
            df = df.copy()
            df['high'] = pd.to_numeric(df['high'], errors='coerce')
            df['low'] = pd.to_numeric(df['low'], errors='coerce')
            df['close'] = pd.to_numeric(df['close'], errors='coerce')
            
            # Calculate ATR for threshold filtering
            atr = None
            if self.auto_threshold:
                atr = self._calculate_atr(df)
            
            bullish_fvgs = []
            bearish_fvgs = []
            current_price = float(df['close'].iloc[-1])
            
            # Iterate through bars looking for gaps (need at least 3 bars)
            for i in range(2, len(df)):
                # Get three consecutive bars
                bar_0 = df.iloc[i]      # Current bar
                bar_1 = df.iloc[i-1]    # Middle bar
                bar_2 = df.iloc[i-2]    # Old bar
                
                high_0 = float(bar_0['high'])
                low_0 = float(bar_0['low'])
                high_1 = float(bar_1['high'])
                low_1 = float(bar_1['low'])
                high_2 = float(bar_2['high'])
                low_2 = float(bar_2['low'])
                
                # Detect Bullish FVG: bar_2.high < bar_0.low
                # (Price gapped up, leaving imbalance zone)
                if high_2 < low_0:
                    gap_size = low_0 - high_2
                    gap_midpoint = (low_0 + high_2) / 2.0
                    
                    # Apply ATR threshold if enabled
                    if self.auto_threshold and atr is not None:
                        threshold = float(atr.iloc[i]) * self.threshold_multiplier
                        if gap_size < threshold:
                            continue  # Skip small gaps
                    
                    # Check if gap has been filled
                    filled = False
                    filled_at_index = None
                    
                    for j in range(i+1, len(df)):
                        future_low = float(df.iloc[j]['low'])
                        if future_low <= high_2:  # Price came back and filled the gap
                            filled = True
                            filled_at_index = j
                            break
                    
                    # Calculate gap percentage
                    gap_percentage = (gap_size / high_2 * 100) if high_2 > 0 else 0
                    
                    # Distance from current price
                    distance_to_top = ((low_0 - current_price) / current_price * 100)
                    distance_to_bottom = ((high_2 - current_price) / current_price * 100)
                    
                    bullish_fvgs.append({
                        'top': low_0,
                        'bottom': high_2,
                        'midpoint': gap_midpoint,
                        'size': gap_size,
                        'size_percentage': gap_percentage,
                        'bar_index': i,
                        'filled': filled,
                        'filled_at_index': filled_at_index,
                        'distance_to_top_percent': distance_to_top,
                        'distance_to_bottom_percent': distance_to_bottom,
                        'status': 'FILLED' if filled else 'ACTIVE'
                    })
                
                # Detect Bearish FVG: bar_2.low > bar_0.high
                # (Price gapped down, leaving imbalance zone)
                if low_2 > high_0:
                    gap_size = low_2 - high_0
                    gap_midpoint = (low_2 + high_0) / 2.0
                    
                    # Apply ATR threshold if enabled
                    if self.auto_threshold and atr is not None:
                        threshold = float(atr.iloc[i]) * self.threshold_multiplier
                        if gap_size < threshold:
                            continue  # Skip small gaps
                    
                    # Check if gap has been filled
                    filled = False
                    filled_at_index = None
                    
                    for j in range(i+1, len(df)):
                        future_high = float(df.iloc[j]['high'])
                        if future_high >= low_2:  # Price came back and filled the gap
                            filled = True
                            filled_at_index = j
                            break
                    
                    # Calculate gap percentage
                    gap_percentage = (gap_size / low_2 * 100) if low_2 > 0 else 0
                    
                    # Distance from current price
                    distance_to_top = ((low_2 - current_price) / current_price * 100)
                    distance_to_bottom = ((high_0 - current_price) / current_price * 100)
                    
                    bearish_fvgs.append({
                        'top': low_2,
                        'bottom': high_0,
                        'midpoint': gap_midpoint,
                        'size': gap_size,
                        'size_percentage': gap_percentage,
                        'bar_index': i,
                        'filled': filled,
                        'filled_at_index': filled_at_index,
                        'distance_to_top_percent': distance_to_top,
                        'distance_to_bottom_percent': distance_to_bottom,
                        'status': 'FILLED' if filled else 'ACTIVE'
                    })
            
            # Filter only unfilled gaps and sort by proximity to current price
            unfilled_bullish = [fvg for fvg in bullish_fvgs if not fvg['filled']]
            unfilled_bearish = [fvg for fvg in bearish_fvgs if not fvg['filled']]
            
            # Sort by distance to current price (nearest first)
            unfilled_bullish = sorted(unfilled_bullish, 
                                     key=lambda x: abs(x['midpoint'] - current_price))[:max_gaps]
            unfilled_bearish = sorted(unfilled_bearish, 
                                     key=lambda x: abs(x['midpoint'] - current_price))[:max_gaps]
            
            # Calculate statistics
            total_bullish = len(bullish_fvgs)
            total_bearish = len(bearish_fvgs)
            filled_bullish = len([fvg for fvg in bullish_fvgs if fvg['filled']])
            filled_bearish = len([fvg for fvg in bearish_fvgs if fvg['filled']])
            
            fill_rate_bullish = (filled_bullish / total_bullish * 100) if total_bullish > 0 else 0
            fill_rate_bearish = (filled_bearish / total_bearish * 100) if total_bearish > 0 else 0
            
            # Find nearest gaps to current price
            nearest_bullish = None
            nearest_bearish = None
            
            if unfilled_bullish:
                nearest_bullish = min(unfilled_bullish, 
                                     key=lambda x: abs(x['midpoint'] - current_price))
            
            if unfilled_bearish:
                nearest_bearish = min(unfilled_bearish, 
                                     key=lambda x: abs(x['midpoint'] - current_price))
            
            return {
                'bullish_fvgs': unfilled_bullish,
                'bearish_fvgs': unfilled_bearish,
                'statistics': {
                    'total_bullish_gaps': total_bullish,
                    'total_bearish_gaps': total_bearish,
                    'unfilled_bullish_gaps': len(unfilled_bullish),
                    'unfilled_bearish_gaps': len(unfilled_bearish),
                    'filled_bullish_gaps': filled_bullish,
                    'filled_bearish_gaps': filled_bearish,
                    'fill_rate_bullish_percent': fill_rate_bullish,
                    'fill_rate_bearish_percent': fill_rate_bearish
                },
                'nearest_gaps': {
                    'bullish': nearest_bullish,
                    'bearish': nearest_bearish
                },
                'current_price': current_price
            }
            
        except Exception as e:
            logger.error(f"Error detecting FVGs: {e}")
            return None
    
    def analyze_multi_timeframe(self, symbol: str, timeframes: List[str] = None) -> Dict:
        """
        Detect Fair Value Gaps across multiple timeframes
        
        Args:
            symbol: Trading symbol
            timeframes: List of timeframes (default: ['1h', '4h', '1d'])
            
        Returns:
            Dict with FVG analysis for each timeframe
        """
        try:
            if timeframes is None:
                timeframes = ['1h', '4h', '1d']
            
            results = {}
            
            for tf in timeframes:
                # Get klines data (100 bars sufficient for FVG)
                df = self.binance.get_klines(symbol, tf, limit=100)
                
                if df is not None and not df.empty:
                    fvgs = self.detect_fvgs(df)
                    if fvgs:
                        results[tf] = fvgs
                        
                        bullish_count = fvgs['statistics']['unfilled_bullish_gaps']
                        bearish_count = fvgs['statistics']['unfilled_bearish_gaps']
                        logger.info(f"FVG {symbol} {tf}: {bullish_count} bullish, {bearish_count} bearish unfilled gaps")
            
            return results
            
        except Exception as e:
            logger.error(f"Error in multi-timeframe FVG analysis: {e}")
            return {}
    
    def is_price_near_fvg(self, current_price: float, fvgs: Dict, proximity_percent: float = 1.0) -> Dict:
        """
        Check if current price is near any FVG
        
        Args:
            current_price: Current market price
            fvgs: FVG dict from detect_fvgs()
            proximity_percent: Consider "near" if within this % (default: 1.0%)
            
        Returns:
            Dict with nearby FVG information
        """
        try:
            if not fvgs:
                return {'near_fvg': False}
            
            nearby_bullish = []
            nearby_bearish = []
            
            # Check bullish FVGs
            for fvg in fvgs.get('bullish_fvgs', []):
                distance = abs((fvg['midpoint'] - current_price) / current_price * 100)
                if distance <= proximity_percent:
                    nearby_bullish.append({
                        **fvg,
                        'distance_percent': distance
                    })
            
            # Check bearish FVGs
            for fvg in fvgs.get('bearish_fvgs', []):
                distance = abs((fvg['midpoint'] - current_price) / current_price * 100)
                if distance <= proximity_percent:
                    nearby_bearish.append({
                        **fvg,
                        'distance_percent': distance
                    })
            
            has_nearby = len(nearby_bullish) > 0 or len(nearby_bearish) > 0
            
            return {
                'near_fvg': has_nearby,
                'nearby_bullish_fvgs': nearby_bullish,
                'nearby_bearish_fvgs': nearby_bearish,
                'count': len(nearby_bullish) + len(nearby_bearish),
                'bias': 'BULLISH_SUPPORT' if nearby_bullish else 'BEARISH_RESISTANCE' if nearby_bearish else 'NEUTRAL'
            }
            
        except Exception as e:
            logger.error(f"Error checking FVG proximity: {e}")
            return {'near_fvg': False}
