"""
Stochastic + RSI Multi-Timeframe Analyzer
Converted from Pine Script to Python

Analyzes multiple timeframes (1m, 5m, 4h, 1D) using:
- Custom RSI on OHLC/4
- Stochastic oscillator on OHLC/4
- Consensus signal from all timeframes

Author: AI Assistant
Date: November 9, 2025
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)


class StochRSIAnalyzer:
    """
    Multi-timeframe Stochastic + RSI analyzer
    
    Features:
    - OHLC/4 calculation for smoother signals
    - Custom RSI with RMA smoothing
    - Stochastic oscillator
    - Multi-timeframe consensus (4 timeframes)
    - BUY/SELL signal generation
    """
    
    def __init__(self, binance_client):
        """
        Initialize Stoch+RSI analyzer
        
        Args:
            binance_client: BinanceClient instance
        """
        self.binance = binance_client
        
        # Default settings from Pine Script
        self.stoch_k_period = 6
        self.stoch_d_period = 6
        self.stoch_smooth = 6
        
        self.rsi_length = 6
        self.rsi_lower = 20
        self.rsi_upper = 80
        
        self.stoch_lower = 20
        self.stoch_upper = 80
        
        # Default timeframes
        self.timeframes = ['1m', '5m', '4h', '1d']
        
        logger.info("Stoch+RSI Multi-timeframe analyzer initialized")
    
    def calculate_ohlc4(self, df: pd.DataFrame) -> pd.Series:
        """
        Calculate OHLC/4 (smoother than close)
        
        Args:
            df: DataFrame with OHLC data
            
        Returns:
            Series with OHLC/4 values
        """
        return (df['open'] + df['high'] + df['low'] + df['close']) / 4
    
    def calculate_custom_rsi(self, src: pd.Series, length: int = 6) -> pd.Series:
        """
        Calculate RSI using RMA (same as Pine Script)
        
        Args:
            src: Source data (OHLC/4)
            length: RSI period
            
        Returns:
            RSI values
        """
        # Calculate price changes
        delta = src.diff()
        
        # Separate gains and losses
        gain = delta.where(delta > 0, 0.0)
        loss = -delta.where(delta < 0, 0.0)
        
        # Calculate RMA (exponential moving average with alpha=1/length)
        alpha = 1.0 / length
        avg_gain = gain.ewm(alpha=alpha, adjust=False).mean()
        avg_loss = loss.ewm(alpha=alpha, adjust=False).mean()
        
        # Calculate RS and RSI
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        # Handle division by zero
        rsi = rsi.fillna(100)
        
        return rsi
    
    def calculate_stochastic(self, src: pd.Series, k_period: int = 6, smooth: int = 6) -> pd.Series:
        """
        Calculate Stochastic oscillator on OHLC/4
        
        Args:
            src: Source data (OHLC/4)
            k_period: Lookback period
            smooth: Smoothing period
            
        Returns:
            Smoothed Stochastic %K values
        """
        # Calculate raw stochastic
        lowest_low = src.rolling(window=k_period).min()
        highest_high = src.rolling(window=k_period).max()
        
        stoch = 100 * (src - lowest_low) / (highest_high - lowest_low)
        stoch = stoch.fillna(50)  # Handle division by zero
        
        # Smooth the stochastic
        smooth_stoch = stoch.rolling(window=smooth).mean()
        
        return smooth_stoch
    
    def calculate_stochastic_d(self, stoch_k: pd.Series, d_period: int = 6) -> pd.Series:
        """
        Calculate Stochastic %D (moving average of %K)
        
        Args:
            stoch_k: Stochastic %K values
            d_period: Smoothing period
            
        Returns:
            Stochastic %D values
        """
        return stoch_k.rolling(window=d_period).mean()
    
    def get_signal(self, rsi_val: float, stoch_val: float) -> int:
        """
        Generate BUY/SELL/NEUTRAL signal based on RSI and Stochastic
        
        Args:
            rsi_val: Current RSI value
            stoch_val: Current Stochastic value
            
        Returns:
            1 = BUY, -1 = SELL, 0 = NEUTRAL
        """
        # Determine RSI signal
        if rsi_val < self.rsi_lower:
            rsi_signal = 1  # Oversold
        elif rsi_val > self.rsi_upper:
            rsi_signal = -1  # Overbought
        else:
            rsi_signal = 0
        
        # Determine Stochastic signal
        if stoch_val < self.stoch_lower:
            stoch_signal = 1  # Oversold
        elif stoch_val > self.stoch_upper:
            stoch_signal = -1  # Overbought
        else:
            stoch_signal = 0
        
        # Consensus: both must agree
        if rsi_signal == 1 and stoch_signal == 1:
            return 1  # BUY
        elif rsi_signal == -1 and stoch_signal == -1:
            return -1  # SELL
        else:
            return 0  # NEUTRAL
    
    def analyze_timeframe(self, symbol: str, interval: str) -> Optional[Dict]:
        """
        Analyze single timeframe for symbol
        
        Args:
            symbol: Trading symbol (e.g., BTCUSDT)
            interval: Timeframe (e.g., '5m', '1h', '1d')
            
        Returns:
            Dict with RSI, Stochastic, and signal
        """
        try:
            # Get kline data
            df = self.binance.get_klines(symbol, interval, limit=100)
            
            if df is None or len(df) < 20:
                logger.warning(f"Insufficient data for {symbol} on {interval}")
                return None
            
            # Calculate OHLC/4
            ohlc4 = self.calculate_ohlc4(df)
            
            # Calculate indicators
            rsi = self.calculate_custom_rsi(ohlc4, self.rsi_length)
            stoch_k = self.calculate_stochastic(ohlc4, self.stoch_k_period, self.stoch_smooth)
            stoch_d = self.calculate_stochastic_d(stoch_k, self.stoch_d_period)
            
            # Get latest values
            current_rsi = float(rsi.iloc[-1])
            current_stoch_k = float(stoch_k.iloc[-1])
            current_stoch_d = float(stoch_d.iloc[-1])
            
            # Generate signal
            signal = self.get_signal(current_rsi, current_stoch_k)
            
            return {
                'timeframe': interval,
                'rsi': current_rsi,
                'stoch_k': current_stoch_k,
                'stoch_d': current_stoch_d,
                'signal': signal,
                'signal_text': 'BUY' if signal == 1 else 'SELL' if signal == -1 else 'NEUTRAL'
            }
            
        except Exception as e:
            logger.error(f"Error analyzing {symbol} on {interval}: {e}")
            return None
    
    def analyze_multi_timeframe(self, symbol: str, timeframes: List[str] = None) -> Dict:
        """
        Analyze multiple timeframes and generate consensus
        
        Args:
            symbol: Trading symbol
            timeframes: List of timeframes (default: ['1m', '5m', '4h', '1d'])
            
        Returns:
            Dict with multi-timeframe analysis and consensus
        """
        if timeframes is None:
            timeframes = self.timeframes
        
        try:
            results = []
            total_signal = 0
            
            # Analyze each timeframe
            for tf in timeframes:
                result = self.analyze_timeframe(symbol, tf)
                if result:
                    results.append(result)
                    total_signal += result['signal']
            
            if not results:
                return {
                    'symbol': symbol,
                    'timeframes': [],
                    'consensus': 'NEUTRAL',
                    'consensus_strength': 0,
                    'total_signal': 0
                }
            
            # Determine consensus
            if total_signal > 0:
                consensus = 'BUY'
            elif total_signal < 0:
                consensus = 'SELL'
            else:
                consensus = 'NEUTRAL'
            
            consensus_strength = abs(total_signal)
            
            return {
                'symbol': symbol,
                'timeframes': results,
                'consensus': consensus,
                'consensus_strength': consensus_strength,
                'total_signal': total_signal,
                'analyzed_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in multi-timeframe analysis for {symbol}: {e}")
            return {
                'symbol': symbol,
                'error': str(e),
                'consensus': 'ERROR',
                'consensus_strength': 0
            }
    
    def get_consensus_emoji(self, consensus: str, strength: int) -> str:
        """
        Get emoji representation of consensus
        
        Args:
            consensus: BUY/SELL/NEUTRAL
            strength: Consensus strength (0-4)
            
        Returns:
            Emoji string
        """
        if consensus == 'BUY':
            if strength >= 4:
                return '🟢🟢🟢🟢'  # Strong BUY
            elif strength == 3:
                return '🟢🟢🟢'
            elif strength == 2:
                return '🟢🟢'
            else:
                return '🟢'
        elif consensus == 'SELL':
            if strength >= 4:
                return '🔴🔴🔴🔴'  # Strong SELL
            elif strength == 3:
                return '🔴🔴🔴'
            elif strength == 2:
                return '🔴🔴'
            else:
                return '🔴'
        else:
            return '⚪'  # NEUTRAL
    
    def format_analysis_message(self, analysis: Dict, include_details: bool = True) -> str:
        """
        Format analysis result as Vietnamese message
        
        Args:
            analysis: Analysis result dict
            include_details: Include detailed timeframe breakdown
            
        Returns:
            Formatted message string
        """
        symbol = analysis['symbol']
        consensus = analysis['consensus']
        strength = analysis['consensus_strength']
        total = analysis['total_signal']
        
        emoji = self.get_consensus_emoji(consensus, strength)
        
        msg = f"<b>📊 PHÂN TÍCH STOCH+RSI MULTI-TIMEFRAME</b>\n\n"
        msg += f"<b>💎 {symbol}</b>\n\n"
        
        # Consensus
        if consensus == 'BUY':
            msg += f"<b>✅ TÍN HIỆU: {emoji} MUA</b>\n"
            msg += f"<b>💪 Độ mạnh: {strength}/4 khung thời gian</b>\n\n"
        elif consensus == 'SELL':
            msg += f"<b>❌ TÍN HIỆU: {emoji} BÁN</b>\n"
            msg += f"<b>💪 Độ mạnh: {strength}/4 khung thời gian</b>\n\n"
        else:
            msg += f"<b>⚪ TÍN HIỆU: TRUNG LẬP</b>\n"
            msg += f"<b>Signal: {total:+d}</b>\n\n"
        
        if include_details and 'timeframes' in analysis:
            msg += f"<b>📈 Chi Tiết Theo Khung Thời Gian:</b>\n\n"
            
            for tf_data in analysis['timeframes']:
                tf = tf_data['timeframe']
                rsi = tf_data['rsi']
                stoch = tf_data['stoch_k']
                signal_text = tf_data['signal_text']
                
                # Signal emoji
                if signal_text == 'BUY':
                    signal_emoji = '🟢'
                elif signal_text == 'SELL':
                    signal_emoji = '🔴'
                else:
                    signal_emoji = '⚪'
                
                msg += f"<b>{tf.upper()}:</b> {signal_emoji} {signal_text}\n"
                msg += f"   • RSI: {rsi:.2f}\n"
                msg += f"   • Stoch: {stoch:.2f}\n\n"
        
        # Recommendations
        msg += f"<b>💡 KHUYẾN NGHỊ:</b>\n"
        
        if consensus == 'BUY' and strength >= 3:
            msg += f"   ✅ Tín hiệu MUA mạnh\n"
            msg += f"   ✅ {strength}/4 timeframes đồng thuận\n"
            msg += f"   🎯 Cơ hội vào lệnh tốt\n"
            msg += f"   🛡️ Stop loss: -3%\n"
        elif consensus == 'SELL' and strength >= 3:
            msg += f"   ❌ Tín hiệu BÁN mạnh\n"
            msg += f"   ❌ {strength}/4 timeframes đồng thuận\n"
            msg += f"   ⚠️ Nên chốt lời hoặc tránh\n"
            msg += f"   🛡️ Bảo vệ vốn ưu tiên\n"
        elif strength >= 2:
            msg += f"   ⚠️ Tín hiệu trung bình ({strength}/4)\n"
            msg += f"   💡 Chờ xác nhận thêm\n"
            msg += f"   📊 Theo dõi sát\n"
        else:
            msg += f"   ⚪ Không có tín hiệu rõ ràng\n"
            msg += f"   💡 Chờ tín hiệu mạnh hơn\n"
            msg += f"   📊 Thị trường sideway\n"
        
        msg += f"\n⚠️ <i>Đây là phân tích kỹ thuật, không phải tư vấn tài chính</i>"
        
        return msg
    
    def combine_with_rsi_mfi(self, symbol: str, stoch_rsi_result: Dict, 
                            rsi_mfi_result: Dict) -> Dict:
        """
        Combine Stoch+RSI analysis with existing RSI+MFI analysis
        
        Args:
            symbol: Trading symbol
            stoch_rsi_result: Result from analyze_multi_timeframe()
            rsi_mfi_result: Result from existing RSI+MFI analyzer
            
        Returns:
            Combined analysis with enhanced signals
        """
        try:
            # Extract signals
            stoch_consensus = stoch_rsi_result.get('consensus', 'NEUTRAL')
            stoch_strength = stoch_rsi_result.get('consensus_strength', 0)
            
            # Assuming rsi_mfi_result has 'signal' field
            rsi_mfi_signal = rsi_mfi_result.get('signal', 'NEUTRAL')
            
            # Combined scoring
            combined_score = 0
            
            # Stoch+RSI contribution (0-40 points)
            if stoch_consensus == 'BUY':
                combined_score += stoch_strength * 10
            elif stoch_consensus == 'SELL':
                combined_score -= stoch_strength * 10
            
            # RSI+MFI contribution (0-60 points)
            if rsi_mfi_signal == 'BUY':
                combined_score += 30
            elif rsi_mfi_signal == 'SELL':
                combined_score -= 30
            
            # Determine final consensus
            if combined_score >= 30:
                final_consensus = 'STRONG BUY'
            elif combined_score >= 10:
                final_consensus = 'BUY'
            elif combined_score <= -30:
                final_consensus = 'STRONG SELL'
            elif combined_score <= -10:
                final_consensus = 'SELL'
            else:
                final_consensus = 'NEUTRAL'
            
            return {
                'symbol': symbol,
                'stoch_rsi': stoch_rsi_result,
                'rsi_mfi': rsi_mfi_result,
                'combined_score': combined_score,
                'final_consensus': final_consensus,
                'analyzed_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error combining analyses for {symbol}: {e}")
            return {
                'symbol': symbol,
                'error': str(e),
                'final_consensus': 'ERROR'
            }
    
    def enhance_pump_detection(self, symbol: str, pump_data: Dict, 
                               stoch_rsi_result: Dict) -> Dict:
        """
        Enhance pump detection with Stoch+RSI confirmation
        
        Args:
            symbol: Trading symbol
            pump_data: Pump detector result
            stoch_rsi_result: Stoch+RSI multi-timeframe result
            
        Returns:
            Enhanced pump analysis
        """
        try:
            pump_score = pump_data.get('final_score', 0)
            stoch_consensus = stoch_rsi_result.get('consensus', 'NEUTRAL')
            stoch_strength = stoch_rsi_result.get('consensus_strength', 0)
            
            # Enhance pump score with Stoch+RSI confirmation
            enhanced_score = pump_score
            
            # Bonus for BUY consensus
            if stoch_consensus == 'BUY':
                bonus = stoch_strength * 5  # 5-20 points bonus
                enhanced_score = min(100, enhanced_score + bonus)
                confirmation = True
            # Penalty for SELL consensus (false pump warning)
            elif stoch_consensus == 'SELL':
                penalty = stoch_strength * 5
                enhanced_score = max(0, enhanced_score - penalty)
                confirmation = False
            else:
                confirmation = None
            
            return {
                'symbol': symbol,
                'original_pump_score': pump_score,
                'enhanced_pump_score': enhanced_score,
                'stoch_rsi_confirmation': confirmation,
                'stoch_consensus': stoch_consensus,
                'stoch_strength': stoch_strength,
                'recommendation': 'CONFIRMED' if confirmation and enhanced_score >= 80 else 'UNCONFIRMED'
            }
            
        except Exception as e:
            logger.error(f"Error enhancing pump detection for {symbol}: {e}")
            return {
                'symbol': symbol,
                'error': str(e)
            }
