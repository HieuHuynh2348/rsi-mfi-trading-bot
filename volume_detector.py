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
            last_volume = df['volume'].iloc[-2]  # Volume of previous candle
            
            # Average volume (excluding current candle)
            avg_volume = df['volume'].iloc[:-1].tail(self.config['lookback_periods']).mean()
            
            # Standard deviation
            std_volume = df['volume'].iloc[:-1].tail(self.config['lookback_periods']).std()
            
            # Volume ratio (current / average)
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 0
            
            # Last candle ratio (current / last)
            last_candle_ratio = current_volume / last_volume if last_volume > 0 else 0
            
            # Percent increase from average
            volume_increase = ((current_volume - avg_volume) / avg_volume * 100) if avg_volume > 0 else 0
            
            # Percent increase from last candle
            last_candle_increase = ((current_volume - last_volume) / last_volume * 100) if last_volume > 0 else 0
            
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
                'last_volume': last_volume,
                'avg_volume': avg_volume,
                'volume_ratio': volume_ratio,
                'last_candle_ratio': last_candle_ratio,
                'volume_increase_percent': volume_increase,
                'last_candle_increase_percent': last_candle_increase,
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
    
    def detect(self, df, symbol='UNKNOWN'):
        """
        Detect volume anomaly from existing DataFrame (optimized for reusing klines data)
        
        Args:
            df: DataFrame with OHLCV data (must have 'volume', 'open', 'close' columns)
            symbol: Symbol name (for logging)
        
        Returns:
            dict with detection results or None
        """
        try:
            if df is None or len(df) < self.config['lookback_periods']:
                logger.warning(f"Insufficient data for {symbol} (need {self.config['lookback_periods']}, got {len(df) if df is not None else 0})")
                return None
            
            # Calculate volume statistics
            current_volume = df['volume'].iloc[-1]
            last_volume = df['volume'].iloc[-2]  # Volume of previous candle
            
            # Average volume (excluding current candle)
            avg_volume = df['volume'].iloc[:-1].tail(self.config['lookback_periods']).mean()
            
            # Standard deviation
            std_volume = df['volume'].iloc[:-1].tail(self.config['lookback_periods']).std()
            
            # Volume ratio (current / average)
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 0
            
            # Last candle ratio (current / last)
            last_candle_ratio = current_volume / last_volume if last_volume > 0 else 0
            
            # Percent increase from average
            volume_increase = ((current_volume - avg_volume) / avg_volume * 100) if avg_volume > 0 else 0
            
            # Percent increase from last candle
            last_candle_increase = ((current_volume - last_volume) / last_volume * 100) if last_volume > 0 else 0
            
            # Z-score (how many standard deviations from mean)
            z_score = (current_volume - avg_volume) / std_volume if std_volume > 0 else 0
            
            # Detect anomaly (using 'is_anomaly' instead of 'is_spike')
            is_anomaly = (
                volume_ratio >= self.config['volume_multiplier'] and
                volume_increase >= self.config['min_increase_percent'] and
                z_score >= 2.0  # At least 2 standard deviations
            )
            
            # Get price change
            price_change = ((df['close'].iloc[-1] - df['open'].iloc[-1]) / df['open'].iloc[-1] * 100)
            
            # Classify spike type
            spike_type = None
            if is_anomaly:
                if price_change > 2:
                    spike_type = "BULLISH_BREAKOUT"
                elif price_change < -2:
                    spike_type = "BEARISH_BREAKDOWN"
                else:
                    spike_type = "NEUTRAL_SPIKE"
            
            result = {
                'symbol': symbol,
                'is_anomaly': is_anomaly,
                'spike_type': spike_type,
                'current_volume': current_volume,
                'last_volume': last_volume,
                'avg_volume': avg_volume,
                'avg_ratio': volume_ratio,
                'last_candle_ratio': last_candle_ratio,
                'avg_increase_percent': volume_increase,
                'last_candle_increase_percent': last_candle_increase,
                'z_score': z_score,
                'price_change_percent': price_change,
                'current_price': df['close'].iloc[-1],
                'timestamp': datetime.now(),
                'sensitivity': self.sensitivity
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error detecting volume anomaly for {symbol}: {e}")
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
            return "Không có dữ liệu volume"
        
        text = f"<b>📊 PHÂN TÍCH VOLUME</b>\n\n"
        text += f"<b>Symbol:</b> {result['symbol']}\n"
        text += f"<b>Khung thời gian:</b> {result['timeframe']}\n\n"
        
        # Current volume
        if result['current_volume'] >= 1e9:
            curr_vol_str = f"${result['current_volume']/1e9:.2f}B"
        elif result['current_volume'] >= 1e6:
            curr_vol_str = f"${result['current_volume']/1e6:.2f}M"
        elif result['current_volume'] >= 1e3:
            curr_vol_str = f"${result['current_volume']/1e3:.2f}K"
        else:
            curr_vol_str = f"${result['current_volume']:.2f}"
        
        # Last volume
        if result['last_volume'] >= 1e9:
            last_vol_str = f"${result['last_volume']/1e9:.2f}B"
        elif result['last_volume'] >= 1e6:
            last_vol_str = f"${result['last_volume']/1e6:.2f}M"
        elif result['last_volume'] >= 1e3:
            last_vol_str = f"${result['last_volume']/1e3:.2f}K"
        else:
            last_vol_str = f"${result['last_volume']:.2f}"
        
        text += f"<b>💹 Volume Hiện Tại:</b> {curr_vol_str}\n"
        text += f"<b>⏮️ Volume Trước:</b> {last_vol_str}\n"
        text += f"<b>📊 Volume TB:</b> {result.get('avg_volume', 0)/1e6:.2f}M\n\n"
        
        text += f"<b>📈 so với TB:</b> {result['volume_ratio']:.2f}x (+{result['volume_increase_percent']:.1f}%)\n"
        text += f"<b>📊 so với Nến Trước:</b> {result['last_candle_ratio']:.2f}x ({result['last_candle_increase_percent']:+.1f}%)\n"
        text += f"<b>📉 Z-Score:</b> {result['z_score']:.2f}σ\n\n"
        
        # Spike status
        if result['is_spike']:
            spike_emoji = {
                'BULLISH_BREAKOUT': '🚀',
                'BEARISH_BREAKDOWN': '⚠️',
                'NEUTRAL_SPIKE': '⚡'
            }
            emoji = spike_emoji.get(result['spike_type'], '🔥')
            
            spike_type_vn = {
                'BULLISH_BREAKOUT': 'TĂNG ĐỘT PHÁ',
                'BEARISH_BREAKDOWN': 'GIẢM ĐỘT PHÁ',
                'NEUTRAL_SPIKE': 'TĂNG TRUNG LẬP'
            }
            type_text = spike_type_vn.get(result['spike_type'], result['spike_type'])
            
            text += f"<b>Trạng thái:</b> {emoji} <b>{type_text}</b>\n"
            text += f"<b>Thay Đổi Giá:</b> {result['price_change_percent']:+.2f}%\n"
        else:
            text += f"<b>Trạng thái:</b> ⚪ Volume Bình Thường\n"
        
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
            return "ℹ️ Không phát hiện tăng đột biến volume trong watchlist"
        
        text = f"<b>🔥 CẢNH BÁO TĂNG ĐỘT BIẾN VOLUME!</b>\n\n"
        text += f"<b>📊 Tóm tắt:</b>\n"
        text += f"• {len(spike_alerts)} coin có volume bất thường\n"
        text += f"• Độ nhạy: {self.sensitivity.upper()}\n"
        text += f"• Thời gian: {datetime.now().strftime('%H:%M:%S')}\n\n"
        
        # Group by strength
        strong = [a for a in spike_alerts if a['spike_strength'] == 'STRONG']
        moderate = [a for a in spike_alerts if a['spike_strength'] == 'MODERATE']
        
        if strong:
            text += f"<b>🔴 TÍN HIỆU MẠNH ({len(strong)}):</b>\n"
            for alert in strong[:5]:  # Top 5
                symbol = alert['symbol']
                spikes = alert['spikes_detected']
                text += f"  🚨 <b>{symbol}</b> - {spikes} khung thời gian\n"
            text += "\n"
        
        if moderate:
            text += f"<b>🟡 TÍN HIỆU TRUNG BÌNH ({len(moderate)}):</b>\n"
            for alert in moderate[:5]:  # Top 5
                symbol = alert['symbol']
                text += f"  ⚡ <b>{symbol}</b>\n"
            text += "\n"
        
        text += f"💡 Phân tích chi tiết sẽ được gửi cho từng coin..."
        
        return text
