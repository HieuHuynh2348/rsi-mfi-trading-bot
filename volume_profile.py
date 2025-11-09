"""
Volume Profile Analyzer
Converted from Pine Script: Volume Profile, Pivot Anchored by DGT

Calculates:
- POC (Point of Control): Price level with highest traded volume
- VAH (Value Area High): Highest price in value area
- VAL (Value Area Low): Lowest price in value area
- Volume distribution by price levels

Author: AI Assistant
Date: November 9, 2025
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class VolumeProfileAnalyzer:
    """
    Volume Profile analysis for cryptocurrency trading
    
    Features:
    - Point of Control (POC) calculation
    - Value Area High/Low (VAH/VAL)
    - Volume distribution across price levels
    - Support/Resistance identification based on volume
    """
    
    def __init__(self, binance_client, profile_levels: int = 25, value_area_percent: float = 0.68):
        """
        Initialize Volume Profile analyzer
        
        Args:
            binance_client: BinanceClient instance
            profile_levels: Number of price levels to analyze (default: 25)
            value_area_percent: Value area percentage (default: 0.68 = 68%)
        """
        self.binance = binance_client
        self.profile_levels = profile_levels
        self.value_area_percent = value_area_percent
        
        logger.info(f"Volume Profile analyzer initialized (levels={profile_levels}, VA={value_area_percent*100}%)")
    
    def calculate_volume_profile(self, df: pd.DataFrame) -> Optional[Dict]:
        """
        Calculate volume profile for given OHLCV dataframe
        
        Args:
            df: DataFrame with OHLCV data
            
        Returns:
            Dict with POC, VAH, VAL, volume distribution, and statistics
        """
        try:
            if df is None or df.empty or len(df) < 10:
                logger.warning("Insufficient data for volume profile")
                return None
            
            # Ensure numeric types
            df = df.copy()
            df['high'] = pd.to_numeric(df['high'], errors='coerce')
            df['low'] = pd.to_numeric(df['low'], errors='coerce')
            df['close'] = pd.to_numeric(df['close'], errors='coerce')
            df['volume'] = pd.to_numeric(df['volume'], errors='coerce')
            
            # Get price range
            price_high = float(df['high'].max())
            price_low = float(df['low'].min())
            price_range = price_high - price_low
            
            if price_range <= 0:
                logger.warning("Invalid price range for volume profile")
                return None
            
            # Calculate price step for each level
            price_step = price_range / self.profile_levels
            
            # Initialize volume storage for each level
            volume_at_levels = np.zeros(self.profile_levels)
            
            # Distribute volume across price levels
            for idx, row in df.iterrows():
                bar_high = float(row['high'])
                bar_low = float(row['low'])
                bar_volume = float(row['volume'])
                
                if pd.isna(bar_volume) or bar_volume <= 0:
                    continue
                
                # Find which levels this bar touches
                start_level = int((bar_low - price_low) / price_step)
                end_level = int((bar_high - price_low) / price_step)
                
                # Clamp to valid range
                start_level = max(0, min(start_level, self.profile_levels - 1))
                end_level = max(0, min(end_level, self.profile_levels - 1))
                
                # Distribute volume proportionally across touched levels
                levels_touched = end_level - start_level + 1
                volume_per_level = bar_volume / levels_touched if levels_touched > 0 else bar_volume
                
                for level in range(start_level, end_level + 1):
                    if 0 <= level < self.profile_levels:
                        volume_at_levels[level] += volume_per_level
            
            # Find POC (Point of Control) - level with highest volume
            poc_level = int(np.argmax(volume_at_levels))
            poc_price = price_low + (poc_level + 0.5) * price_step
            poc_volume = volume_at_levels[poc_level]
            
            # Calculate Value Area (VA)
            total_volume = np.sum(volume_at_levels)
            value_area_volume_target = total_volume * self.value_area_percent
            
            # Start from POC and expand until we reach VA target
            value_area_volume = volume_at_levels[poc_level]
            level_above_poc = poc_level
            level_below_poc = poc_level
            
            while value_area_volume < value_area_volume_target:
                # Determine which direction to expand (higher volume side)
                volume_above = volume_at_levels[level_above_poc + 1] if level_above_poc + 1 < self.profile_levels else 0
                volume_below = volume_at_levels[level_below_poc - 1] if level_below_poc - 1 >= 0 else 0
                
                if volume_above >= volume_below and level_above_poc + 1 < self.profile_levels:
                    level_above_poc += 1
                    value_area_volume += volume_at_levels[level_above_poc]
                elif level_below_poc - 1 >= 0:
                    level_below_poc -= 1
                    value_area_volume += volume_at_levels[level_below_poc]
                else:
                    break
            
            # Calculate VAH and VAL
            vah = price_low + (level_above_poc + 1.0) * price_step
            val = price_low + (level_below_poc + 0.0) * price_step
            
            # Calculate statistics
            total_traded_volume = float(df['volume'].sum())
            num_bars = len(df)
            avg_volume_per_bar = total_traded_volume / num_bars if num_bars > 0 else 0
            
            # Find high volume nodes (HVN) - levels with volume > 1.5x average
            avg_volume_per_level = total_volume / self.profile_levels
            high_volume_nodes = []
            low_volume_nodes = []
            
            for level in range(self.profile_levels):
                level_volume = volume_at_levels[level]
                level_price = price_low + (level + 0.5) * price_step
                
                if level_volume > avg_volume_per_level * 1.5:
                    high_volume_nodes.append({
                        'price': level_price,
                        'volume': level_volume,
                        'volume_percentage': (level_volume / total_volume * 100) if total_volume > 0 else 0
                    })
                elif level_volume < avg_volume_per_level * 0.5:
                    low_volume_nodes.append({
                        'price': level_price,
                        'volume': level_volume,
                        'volume_percentage': (level_volume / total_volume * 100) if total_volume > 0 else 0
                    })
            
            # Sort by volume (descending for HVN, ascending for LVN)
            high_volume_nodes = sorted(high_volume_nodes, key=lambda x: x['volume'], reverse=True)[:5]
            low_volume_nodes = sorted(low_volume_nodes, key=lambda x: x['volume'])[:5]
            
            return {
                'poc': {
                    'price': poc_price,
                    'volume': poc_volume,
                    'level': poc_level
                },
                'vah': vah,
                'val': val,
                'value_area': {
                    'high': vah,
                    'low': val,
                    'width': vah - val,
                    'width_percentage': ((vah - val) / price_range * 100) if price_range > 0 else 0,
                    'volume': value_area_volume,
                    'volume_percentage': (value_area_volume / total_volume * 100) if total_volume > 0 else 0
                },
                'profile': {
                    'high': price_high,
                    'low': price_low,
                    'range': price_range,
                    'range_percentage': (price_range / price_low * 100) if price_low > 0 else 0
                },
                'volume_stats': {
                    'total_volume': total_traded_volume,
                    'num_bars': num_bars,
                    'avg_volume_per_bar': avg_volume_per_bar
                },
                'high_volume_nodes': high_volume_nodes,
                'low_volume_nodes': low_volume_nodes,
                'volume_distribution': volume_at_levels.tolist()
            }
            
        except Exception as e:
            logger.error(f"Error calculating volume profile: {e}")
            return None
    
    def analyze_multi_timeframe(self, symbol: str, timeframes: List[str] = None) -> Dict:
        """
        Analyze volume profile across multiple timeframes
        
        Args:
            symbol: Trading symbol
            timeframes: List of timeframes (default: ['4h', '1d'])
            
        Returns:
            Dict with volume profile for each timeframe
        """
        try:
            if timeframes is None:
                timeframes = ['4h', '1d']
            
            results = {}
            
            for tf in timeframes:
                # Get klines data (200 bars for better profile)
                df = self.binance.get_klines(symbol, tf, limit=200)
                
                if df is not None and not df.empty:
                    profile = self.calculate_volume_profile(df)
                    if profile:
                        results[tf] = profile
                        logger.info(f"Volume Profile {symbol} {tf}: POC=${profile['poc']['price']:.4f}, VAH=${profile['vah']:.4f}, VAL=${profile['val']:.4f}")
            
            return results
            
        except Exception as e:
            logger.error(f"Error in multi-timeframe volume profile analysis: {e}")
            return {}
    
    def get_current_position_in_profile(self, current_price: float, profile: Dict) -> Dict:
        """
        Determine where current price sits relative to volume profile
        
        Args:
            current_price: Current market price
            profile: Volume profile dict from calculate_volume_profile()
            
        Returns:
            Dict with position analysis
        """
        try:
            if not profile:
                return {}
            
            poc = profile['poc']['price']
            vah = profile['vah']
            val = profile['val']
            
            # Determine position
            if current_price > vah:
                position = "PREMIUM"
                zone = "Above Value Area"
                bias = "Expect rejection or continuation higher"
            elif current_price < val:
                position = "DISCOUNT"
                zone = "Below Value Area"
                bias = "Expect bounce or continuation lower"
            elif abs(current_price - poc) / poc < 0.005:  # Within 0.5% of POC
                position = "AT_POC"
                zone = "At Point of Control"
                bias = "High volume area - expect reaction"
            elif current_price >= val and current_price <= vah:
                position = "VALUE_AREA"
                zone = "Inside Value Area"
                bias = "Balanced - watch for breakout"
            else:
                position = "UNKNOWN"
                zone = "Unknown"
                bias = "N/A"
            
            # Calculate distances
            distance_to_poc = ((current_price - poc) / poc * 100)
            distance_to_vah = ((current_price - vah) / vah * 100)
            distance_to_val = ((current_price - val) / val * 100)
            
            # Find nearest high volume node
            hvn_nearby = None
            if profile.get('high_volume_nodes'):
                for hvn in profile['high_volume_nodes']:
                    hvn_price = hvn['price']
                    distance = abs((current_price - hvn_price) / hvn_price * 100)
                    if distance < 2.0:  # Within 2%
                        hvn_nearby = {
                            'price': hvn_price,
                            'distance_percent': distance,
                            'volume_percentage': hvn['volume_percentage']
                        }
                        break
            
            return {
                'position': position,
                'zone': zone,
                'bias': bias,
                'current_price': current_price,
                'poc': poc,
                'vah': vah,
                'val': val,
                'distance_to_poc_percent': distance_to_poc,
                'distance_to_vah_percent': distance_to_vah,
                'distance_to_val_percent': distance_to_val,
                'hvn_nearby': hvn_nearby
            }
            
        except Exception as e:
            logger.error(f"Error analyzing position in profile: {e}")
            return {}
