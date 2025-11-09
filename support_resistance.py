"""
Support and Resistance Zones (High Volume Boxes)
Converted from Pine Script: Support and Resistance (High Volume Boxes) by zjcxhuang

Detects support/resistance zones based on delta volume (buy vs sell pressure)
at pivot points, with break and retest tracking.

Author: AI Assistant
Date: November 9, 2025
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class SupportResistanceDetector:
    """
    Support and Resistance zone detection based on volume analysis
    
    Identifies high volume zones at pivot points where institutional
    accumulation/distribution occurred, creating strong S/R levels.
    
    Features:
    - Delta volume calculation (buy vs sell volume)
    - High volume boxes at pivot points
    - Break and retest detection
    - Adaptive box width using ATR
    """
    
    def __init__(self, binance_client,
                 pivot_length: int = 10,
                 volume_threshold_multiplier: float = 1.5,
                 atr_period: int = 14,
                 atr_box_width_multiplier: float = 0.5,
                 max_zones: int = 5):
        """
        Initialize Support/Resistance detector
        
        Args:
            binance_client: BinanceClient instance
            pivot_length: Period for pivot detection (default: 10)
            volume_threshold_multiplier: Multiplier for high volume detection (default: 1.5)
            atr_period: ATR calculation period (default: 14)
            atr_box_width_multiplier: ATR multiplier for box width (default: 0.5)
            max_zones: Maximum zones to track (default: 5)
        """
        self.binance = binance_client
        self.pivot_length = pivot_length
        self.volume_threshold = volume_threshold_multiplier
        self.atr_period = atr_period
        self.atr_box_width = atr_box_width_multiplier
        self.max_zones = max_zones
        
        logger.info(f"S/R detector initialized (pivot={pivot_length}, volume_threshold={volume_threshold_multiplier}x)")
    
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
    
    def _calculate_delta_volume(self, df: pd.DataFrame) -> pd.Series:
        """
        Calculate delta volume (buy volume - sell volume)
        
        Estimation method:
        - If close > open: bullish candle, more buy volume
        - If close < open: bearish candle, more sell volume
        
        Delta = (close - open) / (high - low) * volume
        """
        try:
            open_price = df['open']
            high = df['high']
            low = df['low']
            close = df['close']
            volume = df['volume']
            
            # Calculate price range
            price_range = high - low
            price_range = price_range.replace(0, np.nan)  # Avoid division by zero
            
            # Calculate price change
            price_change = close - open_price
            
            # Calculate delta volume
            delta_volume = (price_change / price_range) * volume
            delta_volume = delta_volume.fillna(0)
            
            return delta_volume
            
        except Exception as e:
            logger.error(f"Error calculating delta volume: {e}")
            return pd.Series(dtype=float)
    
    def _find_pivot_highs_lows(self, df: pd.DataFrame) -> Tuple[pd.Series, pd.Series]:
        """
        Find pivot highs and lows
        
        Returns:
            Tuple of (pivot_highs, pivot_lows)
        """
        try:
            high = df['high']
            low = df['low']
            
            pivot_highs = pd.Series(index=df.index, dtype=float)
            pivot_lows = pd.Series(index=df.index, dtype=float)
            
            # Find pivot highs
            for i in range(self.pivot_length, len(df) - self.pivot_length):
                window = high[i-self.pivot_length:i+self.pivot_length+1]
                if high.iloc[i] == window.max():
                    pivot_highs.iloc[i] = high.iloc[i]
            
            # Find pivot lows
            for i in range(self.pivot_length, len(df) - self.pivot_length):
                window = low[i-self.pivot_length:i+self.pivot_length+1]
                if low.iloc[i] == window.min():
                    pivot_lows.iloc[i] = low.iloc[i]
            
            return pivot_highs, pivot_lows
            
        except Exception as e:
            logger.error(f"Error finding pivots: {e}")
            return pd.Series(dtype=float), pd.Series(dtype=float)
    
    def detect_support_resistance_zones(self, df: pd.DataFrame) -> Optional[Dict]:
        """
        Detect support and resistance zones based on volume
        
        Args:
            df: DataFrame with OHLCV data
            
        Returns:
            Dict with support and resistance zones
        """
        try:
            if df is None or df.empty or len(df) < self.pivot_length * 2 + 10:
                logger.warning("Insufficient data for S/R detection")
                return None
            
            # Ensure numeric types
            df = df.copy()
            df['high'] = pd.to_numeric(df['high'], errors='coerce')
            df['low'] = pd.to_numeric(df['low'], errors='coerce')
            df['close'] = pd.to_numeric(df['close'], errors='coerce')
            df['open'] = pd.to_numeric(df['open'], errors='coerce')
            df['volume'] = pd.to_numeric(df['volume'], errors='coerce')
            
            # Calculate indicators
            atr = self._calculate_atr(df)
            delta_volume = self._calculate_delta_volume(df)
            pivot_highs, pivot_lows = self._find_pivot_highs_lows(df)
            
            # Calculate volume statistics
            avg_volume = df['volume'].mean()
            high_volume_threshold = avg_volume * self.volume_threshold
            
            support_zones = []
            resistance_zones = []
            current_price = float(df['close'].iloc[-1])
            
            # Detect resistance zones at pivot highs with high volume
            for i in range(len(df)):
                if pd.isna(pivot_highs.iloc[i]):
                    continue
                
                pivot_price = float(pivot_highs.iloc[i])
                bar_volume = float(df['volume'].iloc[i])
                bar_delta = float(delta_volume.iloc[i])
                
                # Check if volume is high
                if bar_volume < high_volume_threshold:
                    continue
                
                # Calculate box dimensions
                box_width = float(atr.iloc[i]) * self.atr_box_width if not pd.isna(atr.iloc[i]) else pivot_price * 0.01
                box_top = pivot_price + box_width / 2.0
                box_bottom = pivot_price - box_width / 2.0
                
                # Check if zone was broken (price went above it)
                broken = False
                retest_occurred = False
                
                for j in range(i+1, len(df)):
                    future_close = float(df['close'].iloc[j])
                    future_high = float(df['high'].iloc[j])
                    
                    # Check for break
                    if future_close > box_top:
                        broken = True
                        
                        # After break, check for retest (price came back to zone)
                        for k in range(j+1, len(df)):
                            retest_low = float(df['low'].iloc[k])
                            if retest_low <= box_top and retest_low >= box_bottom:
                                retest_occurred = True
                                break
                        break
                
                # Calculate distance from current price
                distance = ((box_bottom - current_price) / current_price * 100)
                
                # Determine status
                if broken:
                    status = 'BROKEN_RETESTED' if retest_occurred else 'BROKEN'
                else:
                    status = 'ACTIVE'
                
                resistance_zones.append({
                    'type': 'RESISTANCE',
                    'price': pivot_price,
                    'top': box_top,
                    'bottom': box_bottom,
                    'width': box_width,
                    'width_percentage': (box_width / pivot_price * 100) if pivot_price > 0 else 0,
                    'volume': bar_volume,
                    'volume_ratio': bar_volume / avg_volume if avg_volume > 0 else 0,
                    'delta_volume': bar_delta,
                    'bar_index': i,
                    'broken': broken,
                    'retest_occurred': retest_occurred,
                    'status': status,
                    'distance_percent': distance
                })
            
            # Detect support zones at pivot lows with high volume
            for i in range(len(df)):
                if pd.isna(pivot_lows.iloc[i]):
                    continue
                
                pivot_price = float(pivot_lows.iloc[i])
                bar_volume = float(df['volume'].iloc[i])
                bar_delta = float(delta_volume.iloc[i])
                
                # Check if volume is high
                if bar_volume < high_volume_threshold:
                    continue
                
                # Calculate box dimensions
                box_width = float(atr.iloc[i]) * self.atr_box_width if not pd.isna(atr.iloc[i]) else pivot_price * 0.01
                box_top = pivot_price + box_width / 2.0
                box_bottom = pivot_price - box_width / 2.0
                
                # Check if zone was broken (price went below it)
                broken = False
                retest_occurred = False
                
                for j in range(i+1, len(df)):
                    future_close = float(df['close'].iloc[j])
                    future_low = float(df['low'].iloc[j])
                    
                    # Check for break
                    if future_close < box_bottom:
                        broken = True
                        
                        # After break, check for retest (price came back to zone)
                        for k in range(j+1, len(df)):
                            retest_high = float(df['high'].iloc[k])
                            if retest_high >= box_bottom and retest_high <= box_top:
                                retest_occurred = True
                                break
                        break
                
                # Calculate distance from current price
                distance = ((box_top - current_price) / current_price * 100)
                
                # Determine status
                if broken:
                    status = 'BROKEN_RETESTED' if retest_occurred else 'BROKEN'
                else:
                    status = 'ACTIVE'
                
                support_zones.append({
                    'type': 'SUPPORT',
                    'price': pivot_price,
                    'top': box_top,
                    'bottom': box_bottom,
                    'width': box_width,
                    'width_percentage': (box_width / pivot_price * 100) if pivot_price > 0 else 0,
                    'volume': bar_volume,
                    'volume_ratio': bar_volume / avg_volume if avg_volume > 0 else 0,
                    'delta_volume': bar_delta,
                    'bar_index': i,
                    'broken': broken,
                    'retest_occurred': retest_occurred,
                    'status': status,
                    'distance_percent': distance
                })
            
            # Filter only active zones
            active_support = [z for z in support_zones if z['status'] == 'ACTIVE']
            active_resistance = [z for z in resistance_zones if z['status'] == 'ACTIVE']
            
            # Sort by proximity to current price
            active_support = sorted(active_support, 
                                   key=lambda x: abs(x['price'] - current_price))[:self.max_zones]
            active_resistance = sorted(active_resistance, 
                                      key=lambda x: abs(x['price'] - current_price))[:self.max_zones]
            
            # Find nearest zones
            nearest_support = None
            nearest_resistance = None
            
            if active_support:
                nearest_support = min(active_support, 
                                     key=lambda x: abs(x['price'] - current_price))
            
            if active_resistance:
                nearest_resistance = min(active_resistance, 
                                        key=lambda x: abs(x['price'] - current_price))
            
            # Calculate statistics
            total_support = len(support_zones)
            total_resistance = len(resistance_zones)
            broken_support = len([z for z in support_zones if z['broken']])
            broken_resistance = len([z for z in resistance_zones if z['broken']])
            
            break_rate_support = (broken_support / total_support * 100) if total_support > 0 else 0
            break_rate_resistance = (broken_resistance / total_resistance * 100) if total_resistance > 0 else 0
            
            return {
                'support_zones': active_support,
                'resistance_zones': active_resistance,
                'statistics': {
                    'total_support_zones': total_support,
                    'total_resistance_zones': total_resistance,
                    'active_support_zones': len(active_support),
                    'active_resistance_zones': len(active_resistance),
                    'broken_support_zones': broken_support,
                    'broken_resistance_zones': broken_resistance,
                    'break_rate_support_percent': break_rate_support,
                    'break_rate_resistance_percent': break_rate_resistance,
                    'avg_volume': avg_volume,
                    'high_volume_threshold': high_volume_threshold
                },
                'nearest_zones': {
                    'support': nearest_support,
                    'resistance': nearest_resistance
                },
                'current_price': current_price
            }
            
        except Exception as e:
            logger.error(f"Error detecting S/R zones: {e}")
            return None
    
    def analyze_multi_timeframe(self, symbol: str, timeframes: List[str] = None) -> Dict:
        """
        Detect S/R zones across multiple timeframes
        
        Args:
            symbol: Trading symbol
            timeframes: List of timeframes (default: ['4h', '1d'])
            
        Returns:
            Dict with S/R analysis for each timeframe
        """
        try:
            if timeframes is None:
                timeframes = ['4h', '1d']
            
            results = {}
            
            for tf in timeframes:
                # Get klines data
                df = self.binance.get_klines(symbol, tf, limit=150)
                
                if df is not None and not df.empty:
                    zones = self.detect_support_resistance_zones(df)
                    if zones:
                        results[tf] = zones
                        
                        support_count = zones['statistics']['active_support_zones']
                        resistance_count = zones['statistics']['active_resistance_zones']
                        logger.info(f"S/R {symbol} {tf}: {support_count} support, {resistance_count} resistance zones")
            
            return results
            
        except Exception as e:
            logger.error(f"Error in multi-timeframe S/R analysis: {e}")
            return {}
    
    def is_price_near_zone(self, current_price: float, zones: Dict, proximity_percent: float = 1.0) -> Dict:
        """
        Check if current price is near any S/R zone
        
        Args:
            current_price: Current market price
            zones: S/R dict from detect_support_resistance_zones()
            proximity_percent: Consider "near" if within this % (default: 1.0%)
            
        Returns:
            Dict with nearby zone information
        """
        try:
            if not zones:
                return {'near_zone': False}
            
            nearby_support = []
            nearby_resistance = []
            
            # Check support zones
            for zone in zones.get('support_zones', []):
                distance = abs((zone['price'] - current_price) / current_price * 100)
                if distance <= proximity_percent:
                    nearby_support.append({
                        **zone,
                        'distance_percent': distance
                    })
            
            # Check resistance zones
            for zone in zones.get('resistance_zones', []):
                distance = abs((zone['price'] - current_price) / current_price * 100)
                if distance <= proximity_percent:
                    nearby_resistance.append({
                        **zone,
                        'distance_percent': distance
                    })
            
            has_nearby = len(nearby_support) > 0 or len(nearby_resistance) > 0
            
            return {
                'near_zone': has_nearby,
                'nearby_support_zones': nearby_support,
                'nearby_resistance_zones': nearby_resistance,
                'count': len(nearby_support) + len(nearby_resistance),
                'bias': 'NEAR_SUPPORT' if nearby_support else 'NEAR_RESISTANCE' if nearby_resistance else 'NEUTRAL'
            }
            
        except Exception as e:
            logger.error(f"Error checking zone proximity: {e}")
            return {'near_zone': False}
