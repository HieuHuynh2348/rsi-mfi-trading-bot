"""
Volume Anomaly Detector
Detects unusual volume spikes that may indicate breakouts or significant price movements
"""

import logging
import pandas as pd
import numpy as np
from datetime import datetime

logger = logging.getLogger(__name__)


class VolumeDetector:
    def __init__(self, binance_client, sensitivity='medium'):
        """
        Initialize volume anomaly detector
        
        Args:
            binance_client: BinanceClient instance
            sensitivity: Detection sensitivity ('low', 'medium', 'high')
        """
        self.binance = binance_client
        
        # Volume spike thresholds based on sensitivity
        self.thresholds = {
            'low': {
                'volume_multiplier': 3.0,      # 3x average volume
                'lookback_periods': 50,         # Compare with last 50 candles
                'min_increase_percent': 200     # Minimum 200% increase
            },
            'medium': {
                'volume_multiplier': 2.5,      # 2.5x average volume
                'lookback_periods': 30,         # Compare with last 30 candles
                'min_increase_percent': 150     # Minimum 150% increase
            },
            'high': {
                'volume_multiplier': 2.0,      # 2x average volume
                'lookback_periods': 20,         # Compare with last 20 candles
                'min_increase_percent': 100     # Minimum 100% increase
            }
        }
        
        self.sensitivity = sensitivity
        self.config = self.thresholds.get(sensitivity, self.thresholds['medium'])
        
        logger.info(f"Volume detector initialized with {sensitivity} sensitivity")
    
    def detect_volume_spike(self, symbol, timeframe='5m'):
        """
        Detect if current volume is abnormally high
        
        Args:
            symbol: Trading symbol
            timeframe: Timeframe to check
        
        Returns:
            dict with detection results or None
        """
        try:
            # Get historical data
            df = self.binance.get_klines(
                symbol, 
                timeframe, 
                limit=self.config['lookback_periods'] + 10
            )
            
            if df is None or len(df) < self.config['lookback_periods']:
                logger.warning(f"Insufficient data for {symbol}")
                return None
            
            # Calculate volume statistics
            current_volume = df['volume'].iloc[-1]
            
            # Average volume (excluding current candle)
            avg_volume = df['volume'].iloc[:-1].tail(self.config['lookback_periods']).mean()
            
            # Standard deviation
            std_volume = df['volume'].iloc[:-1].tail(self.config['lookback_periods']).std()
            
            # Volume ratio (current / average)
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 0
            
            # Percent increase from average
            volume_increase = ((current_volume - avg_volume) / avg_volume * 100) if avg_volume > 0 else 0
            
            # Z-score (how many standard deviations from mean)
            z_score = (current_volume - avg_volume) / std_volume if std_volume > 0 else 0
            
            # Detect spike
            is_spike = (
                volume_ratio >= self.config['volume_multiplier'] and
                volume_increase >= self.config['min_increase_percent'] and
                z_score >= 2.0  # At least 2 standard deviations
            )
            
            # Get price change
            price_change = ((df['close'].iloc[-1] - df['open'].iloc[-1]) / df['open'].iloc[-1] * 100)
            
            # Classify spike type
            spike_type = None
            if is_spike:
                if price_change > 2:
                    spike_type = "BULLISH_BREAKOUT"
                elif price_change < -2:
                    spike_type = "BEARISH_BREAKDOWN"
                else:
                    spike_type = "NEUTRAL_SPIKE"
            
            result = {
                'symbol': symbol,
                'timeframe': timeframe,
                'is_spike': is_spike,
                'spike_type': spike_type,
                'current_volume': current_volume,
                'avg_volume': avg_volume,
                'volume_ratio': volume_ratio,
                'volume_increase_percent': volume_increase,
                'z_score': z_score,
                'price_change_percent': price_change,
                'current_price': df['close'].iloc[-1],
                'timestamp': datetime.now(),
                'sensitivity': self.sensitivity
            }
            
            if is_spike:
                logger.info(f"🔥 VOLUME SPIKE DETECTED: {symbol} - {volume_ratio:.2f}x average volume!")
            
            return result
            
        except Exception as e:
            logger.error(f"Error detecting volume spike for {symbol}: {e}")
            return None
    
    def detect_multi_timeframe_spike(self, symbol, timeframes=['5m', '1h', '4h']):
        """
        Detect volume spikes across multiple timeframes
        
        Args:
            symbol: Trading symbol
            timeframes: List of timeframes to check
        
        Returns:
            dict with results for all timeframes
        """
        results = {}
        spike_count = 0
        
        for tf in timeframes:
            result = self.detect_volume_spike(symbol, tf)
            if result:
                results[tf] = result
                if result['is_spike']:
                    spike_count += 1
        
        # Overall assessment
        assessment = {
            'symbol': symbol,
            'timeframes_checked': len(timeframes),
            'spikes_detected': spike_count,
            'has_spike': spike_count > 0,
            'spike_strength': 'STRONG' if spike_count >= 2 else ('MODERATE' if spike_count == 1 else 'NONE'),
            'timeframe_results': results,
            'timestamp': datetime.now()
        }
        
        return assessment
    
    def scan_watchlist_volumes(self, watchlist_symbols, timeframes=['5m', '1h']):
        """
        Scan entire watchlist for volume anomalies
        
        Args:
            watchlist_symbols: List of symbols to scan
            timeframes: Timeframes to check
        
        Returns:
            List of symbols with volume spikes
        """
        spike_alerts = []
        
        logger.info(f"Scanning {len(watchlist_symbols)} symbols for volume spikes...")
        
        for symbol in watchlist_symbols:
            try:
                # Check multi-timeframe
                assessment = self.detect_multi_timeframe_spike(symbol, timeframes)
                
                if assessment['has_spike']:
                    spike_alerts.append(assessment)
                    logger.info(f"⚡ Volume spike found: {symbol} ({assessment['spike_strength']})")
                
            except Exception as e:
                logger.error(f"Error scanning {symbol}: {e}")
                continue
        
        # Sort by spike strength (most timeframes with spikes first)
        spike_alerts.sort(key=lambda x: x['spikes_detected'], reverse=True)
        
        logger.info(f"Scan complete: {len(spike_alerts)} symbols with volume spikes")
        
        return spike_alerts
    
    def get_volume_analysis_text(self, result):
        """
        Format volume analysis as readable text
        
        Args:
            result: Detection result dict
        
        Returns:
            Formatted text string
        """
        if not result:
            return "No volume data available"
        
        text = f"<b>📊 VOLUME ANALYSIS</b>\n\n"
        text += f"<b>Symbol:</b> {result['symbol']}\n"
        text += f"<b>Timeframe:</b> {result['timeframe']}\n\n"
        
        # Current volume
        if result['current_volume'] >= 1e9:
            vol_str = f"${result['current_volume']/1e9:.2f}B"
        elif result['current_volume'] >= 1e6:
            vol_str = f"${result['current_volume']/1e6:.2f}M"
        elif result['current_volume'] >= 1e3:
            vol_str = f"${result['current_volume']/1e3:.2f}K"
        else:
            vol_str = f"${result['current_volume']:.2f}"
        
        text += f"<b>Current Volume:</b> {vol_str}\n"
        text += f"<b>Volume Ratio:</b> {result['volume_ratio']:.2f}x average\n"
        text += f"<b>Increase:</b> +{result['volume_increase_percent']:.1f}%\n"
        text += f"<b>Z-Score:</b> {result['z_score']:.2f}σ\n\n"
        
        # Spike status
        if result['is_spike']:
            spike_emoji = {
                'BULLISH_BREAKOUT': '🚀',
                'BEARISH_BREAKDOWN': '⚠️',
                'NEUTRAL_SPIKE': '⚡'
            }
            emoji = spike_emoji.get(result['spike_type'], '🔥')
            
            text += f"<b>Status:</b> {emoji} <b>{result['spike_type'].replace('_', ' ')}</b>\n"
            text += f"<b>Price Change:</b> {result['price_change_percent']:+.2f}%\n"
        else:
            text += f"<b>Status:</b> ⚪ Normal Volume\n"
        
        return text
    
    def get_watchlist_spike_summary(self, spike_alerts):
        """
        Create summary of watchlist volume spikes
        
        Args:
            spike_alerts: List of spike assessments
        
        Returns:
            Formatted summary text
        """
        if not spike_alerts:
            return "ℹ️ No volume spikes detected in watchlist"
        
        text = f"<b>🔥 VOLUME SPIKE ALERT!</b>\n\n"
        text += f"<b>📊 Summary:</b>\n"
        text += f"• {len(spike_alerts)} coin(s) with unusual volume\n"
        text += f"• Sensitivity: {self.sensitivity.upper()}\n"
        text += f"• Time: {datetime.now().strftime('%H:%M:%S')}\n\n"
        
        # Group by strength
        strong = [a for a in spike_alerts if a['spike_strength'] == 'STRONG']
        moderate = [a for a in spike_alerts if a['spike_strength'] == 'MODERATE']
        
        if strong:
            text += f"<b>🔴 STRONG SIGNALS ({len(strong)}):</b>\n"
            for alert in strong[:5]:  # Top 5
                symbol = alert['symbol']
                spikes = alert['spikes_detected']
                text += f"  🚨 <b>{symbol}</b> - {spikes} timeframe(s)\n"
            text += "\n"
        
        if moderate:
            text += f"<b>🟡 MODERATE SIGNALS ({len(moderate)}):</b>\n"
            for alert in moderate[:5]:  # Top 5
                symbol = alert['symbol']
                text += f"  ⚡ <b>{symbol}</b>\n"
            text += "\n"
        
        text += f"💡 Detailed analysis will be sent for each coin..."
        
        return text
