"""
Gemini AI Trading Analyzer
Integrates Google Gemini 1.5 Pro for comprehensive trading analysis

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
        self.fvg_detector = FairValueGapDetector(binance_client)
        self.ob_detector = OrderBlockDetector(binance_client)
        self.sr_detector = SupportResistanceDetector(binance_client)
        self.smc_analyzer = SmartMoneyAnalyzer(binance_client)
        
        # Configure Gemini
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Cache system (15 minutes)
        self.cache = {}  # {symbol: {'data': result, 'timestamp': time.time()}}
        self.cache_duration = 900  # 15 minutes in seconds
        
        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 1.0  # 1 second between requests
        
        logger.info("Gemini AI Analyzer initialized (Model: gemini-1.5-pro, Institutional indicators loaded)")
    
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
            logger.info(f"Collecting data for {symbol}...")
            
            # Get current price and 24h data
            ticker_24h = self.binance.get_24h_data(symbol)
            if not ticker_24h:
                logger.error(f"Failed to get 24h data for {symbol}")
                return None
            
            current_price = ticker_24h['last_price']
            logger.info(f"Current price for {symbol}: ${current_price:,.2f}")
            
            # Get multi-timeframe klines with historical depth
            # Use different limits per timeframe for optimal historical context
            logger.info(f"Fetching historical klines for {symbol}...")
            klines_dict = {}
            
            # 5m: 100 candles (8.3 hours) - for short-term patterns
            df_5m = self.binance.get_klines(symbol, '5m', limit=100)
            if df_5m is not None and not df_5m.empty:
                klines_dict['5m'] = df_5m
            
            # 1h: 168 candles (7 days) - for intraday analysis
            df_1h = self.binance.get_klines(symbol, '1h', limit=168)
            if df_1h is not None and not df_1h.empty:
                klines_dict['1h'] = df_1h
            
            # 4h: 180 candles (30 days) - for swing trading
            df_4h = self.binance.get_klines(symbol, '4h', limit=180)
            if df_4h is not None and not df_4h.empty:
                klines_dict['4h'] = df_4h
            
            # 1d: 90 candles (3 months) - for trend analysis
            df_1d = self.binance.get_klines(symbol, '1d', limit=90)
            if df_1d is not None and not df_1d.empty:
                klines_dict['1d'] = df_1d
            
            if not klines_dict or len(klines_dict) == 0:
                logger.error(f"Failed to get klines data for {symbol}")
                return None
            
            logger.info(f"Got klines for {symbol}: {list(klines_dict.keys())}")
            
            # RSI+MFI analysis
            from indicators import analyze_multi_timeframe
            import config
            logger.info(f"Calculating RSI+MFI for {symbol}...")
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
            logger.info(f"Calculating Stoch+RSI for {symbol}...")
            stoch_rsi_result = self.stoch_rsi_analyzer.analyze_multi_timeframe(
                symbol,
                timeframes=['1m', '5m', '1h', '4h', '1d']
            )
            
            # Volume data
            volume_data = {
                'current': ticker_24h['volume'] if ticker_24h else 0,
                'base_volume': ticker_24h['base_volume'] if ticker_24h else 0,
                'trades': ticker_24h['trades'] if ticker_24h else 0
            }
            
            # INSTITUTIONAL INDICATORS
            
            # Volume Profile (1h, 4h, 1d)
            logger.info(f"Analyzing Volume Profile for {symbol}...")
            vp_result = self.volume_profile.analyze_multi_timeframe(symbol, ['1h', '4h', '1d'])
            
            # Fair Value Gaps (1h, 4h, 1d)
            logger.info(f"Detecting Fair Value Gaps for {symbol}...")
            fvg_result = self.fvg_detector.analyze_multi_timeframe(symbol, ['1h', '4h', '1d'])
            
            # Order Blocks (1h, 4h, 1d)
            logger.info(f"Detecting Order Blocks for {symbol}...")
            ob_result = self.ob_detector.analyze_multi_timeframe(symbol, ['1h', '4h', '1d'])
            
            # Support/Resistance zones (1h, 4h, 1d)
            logger.info(f"Analyzing Support/Resistance for {symbol}...")
            sr_result = self.sr_detector.analyze_multi_timeframe(symbol, ['1h', '4h', '1d'])
            
            # Smart Money Concepts (1h, 4h, 1d)
            logger.info(f"Analyzing Smart Money Concepts for {symbol}...")
            smc_result = self.smc_analyzer.analyze_multi_timeframe(symbol, ['1h', '4h', '1d'])
            
            # Historical comparison (week-over-week)
            logger.info(f"Calculating historical comparison for {symbol}...")
            historical = self._get_historical_comparison(symbol, klines_dict)
            
            # Extended historical klines context (reuse klines_dict data)
            logger.info(f"Analyzing extended historical context for {symbol}...")
            historical_klines = {}
            if '1h' in klines_dict and klines_dict['1h'] is not None:
                historical_klines['1h'] = self._analyze_historical_period(klines_dict['1h'], '1H (7 ngày)')
            if '4h' in klines_dict and klines_dict['4h'] is not None:
                historical_klines['4h'] = self._analyze_historical_period(klines_dict['4h'], '4H (30 ngày)')
            if '1d' in klines_dict and klines_dict['1d'] is not None:
                historical_klines['1d'] = self._analyze_historical_period(klines_dict['1d'], '1D (90 ngày)')
            
            logger.info(f"✅ Analyzed historical context for {len(historical_klines)} timeframes")
            
            # Market data
            market_data = {
                'price': current_price,
                'price_change_24h': ticker_24h['price_change_percent'],
                'high_24h': ticker_24h['high'],
                'low_24h': ticker_24h['low'],
                'volume_24h': ticker_24h['volume']
            }
            
            logger.info(f"✅ Data collection complete for {symbol}")
            
            return {
                'symbol': symbol,
                'timestamp': datetime.now().isoformat(),
                'market_data': market_data,
                'rsi_mfi': rsi_mfi_result,
                'stoch_rsi': stoch_rsi_result,
                'pump_data': pump_data,
                'volume_data': volume_data,
                'historical': historical,
                'historical_klines': historical_klines,  # Extended historical context
                # Institutional indicators
                'volume_profile': vp_result,
                'fair_value_gaps': fvg_result,
                'order_blocks': ob_result,
                'support_resistance': sr_result,
                'smart_money_concepts': smc_result
            }
            
        except Exception as e:
            logger.error(f"❌ Error collecting data for {symbol}: {e}", exc_info=True)
            return None
    
    def _get_historical_klines_context(self, symbol: str) -> Dict:
        """
        Get extended historical klines for better AI context
        - 1H: Last 7 days (168 candles)
        - 4H: Last 30 days (180 candles)
        - 1D: Last 90 days (90 candles)
        
        Args:
            symbol: Trading symbol
            
        Returns:
            Dict with historical klines statistics
        """
        try:
            result = {}
            
            # 1H Historical (7 days = 168 hours)
            logger.info(f"Getting 1H historical data for {symbol}...")
            df_1h = self.binance.get_klines(symbol, '1h', limit=168)
            if df_1h is not None and len(df_1h) > 0:
                result['1h'] = self._analyze_historical_period(df_1h, '1H (7 ngày)')
            
            # 4H Historical (30 days = 180 candles)
            logger.info(f"Getting 4H historical data for {symbol}...")
            df_4h = self.binance.get_klines(symbol, '4h', limit=180)
            if df_4h is not None and len(df_4h) > 0:
                result['4h'] = self._analyze_historical_period(df_4h, '4H (30 ngày)')
            
            # 1D Historical (90 days)
            logger.info(f"Getting 1D historical data for {symbol}...")
            df_1d = self.binance.get_klines(symbol, '1d', limit=90)
            if df_1d is not None and len(df_1d) > 0:
                result['1d'] = self._analyze_historical_period(df_1d, '1D (90 ngày)')
            
            logger.info(f"✅ Got historical context for {len(result)} timeframes")
            return result
            
        except Exception as e:
            logger.error(f"Error getting historical klines context: {e}")
            return {}
    
    def _analyze_historical_period(self, df, period_name: str) -> Dict:
        """
        Analyze a historical period and extract key statistics
        
        Args:
            df: DataFrame with OHLCV data
            period_name: Name of the period for logging
            
        Returns:
            Dict with statistics
        """
        try:
            from indicators import calculate_rsi, calculate_mfi, calculate_hlcc4
            
            # Price statistics
            high_price = float(df['high'].max())
            low_price = float(df['low'].min())
            current_price = float(df['close'].iloc[-1])
            avg_price = float(df['close'].mean())
            price_range_pct = ((high_price - low_price) / low_price) * 100
            
            # Position in range
            position_in_range = ((current_price - low_price) / (high_price - low_price)) * 100 if high_price > low_price else 50
            
            # Volume statistics
            avg_volume = float(df['volume'].mean())
            current_volume = float(df['volume'].iloc[-1])
            max_volume = float(df['volume'].max())
            volume_trend = "tăng" if current_volume > avg_volume else "giảm"
            
            # RSI statistics
            hlcc4 = calculate_hlcc4(df)
            rsi_series = calculate_rsi(hlcc4, 14)
            avg_rsi = float(rsi_series.mean())
            current_rsi = float(rsi_series.iloc[-1])
            max_rsi = float(rsi_series.max())
            min_rsi = float(rsi_series.min())
            
            # MFI statistics
            mfi_series = calculate_mfi(df, 14)
            avg_mfi = float(mfi_series.mean())
            current_mfi = float(mfi_series.iloc[-1])
            
            # Trend analysis
            first_close = float(df['close'].iloc[0])
            last_close = float(df['close'].iloc[-1])
            trend_pct = ((last_close - first_close) / first_close) * 100
            trend_direction = "tăng" if trend_pct > 2 else ("giảm" if trend_pct < -2 else "sideway")
            
            # Volatility (price changes)
            price_changes = df['close'].pct_change().dropna()
            volatility = float(price_changes.std() * 100)  # as percentage
            
            # Bullish/Bearish candles count
            bullish_candles = (df['close'] > df['open']).sum()
            bearish_candles = (df['close'] < df['open']).sum()
            total_candles = len(df)
            bullish_ratio = (bullish_candles / total_candles) * 100
            
            stats = {
                'period': period_name,
                'candles_count': total_candles,
                'price_range': {
                    'high': high_price,
                    'low': low_price,
                    'current': current_price,
                    'average': avg_price,
                    'range_pct': round(price_range_pct, 2),
                    'position_in_range_pct': round(position_in_range, 2)
                },
                'volume': {
                    'average': avg_volume,
                    'current': current_volume,
                    'max': max_volume,
                    'trend': volume_trend,
                    'current_vs_avg_ratio': round(current_volume / avg_volume, 2) if avg_volume > 0 else 0
                },
                'rsi_stats': {
                    'average': round(avg_rsi, 2),
                    'current': round(current_rsi, 2),
                    'max': round(max_rsi, 2),
                    'min': round(min_rsi, 2)
                },
                'mfi_stats': {
                    'average': round(avg_mfi, 2),
                    'current': round(current_mfi, 2)
                },
                'trend': {
                    'direction': trend_direction,
                    'change_pct': round(trend_pct, 2),
                    'volatility_pct': round(volatility, 2)
                },
                'candle_pattern': {
                    'bullish_candles': int(bullish_candles),
                    'bearish_candles': int(bearish_candles),
                    'bullish_ratio_pct': round(bullish_ratio, 2)
                }
            }
            
            logger.info(f"✅ Analyzed {period_name}: {total_candles} candles, trend={trend_direction}, volatility={volatility:.2f}%")
            return stats
            
        except Exception as e:
            logger.error(f"Error analyzing historical period {period_name}: {e}")
            return {}
    
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
    
    def _format_institutional_indicators_json(self, data: Dict, market: Dict) -> Dict:
        """
        Format institutional indicators into structured JSON for AI analysis
        
        Args:
            data: Collected analysis data
            market: Market data with current price
            
        Returns:
            Structured dict with all institutional indicators
        """
        try:
            result = {
                'volume_profile': {},
                'fair_value_gaps': {},
                'order_blocks': {},
                'support_resistance': {},
                'smart_money_concepts': {}
            }
            
            current_price = market['price']
            
            # Volume Profile
            if data.get('volume_profile'):
                vp_1d = data['volume_profile'].get('1d')
                vp_4h = data['volume_profile'].get('4h')
                vp_1h = data['volume_profile'].get('1h')
                
                if vp_1d:
                    position_1d = self.volume_profile.get_current_position_in_profile(current_price, vp_1d)
                    result['volume_profile']['1d'] = {
                        'poc': vp_1d['poc']['price'],
                        'vah': vp_1d['vah'],
                        'val': vp_1d['val'],
                        'current_position': position_1d.get('position'),
                        'zone': position_1d.get('zone'),
                        'bias': position_1d.get('bias'),
                        'distance_to_poc_percent': position_1d.get('distance_to_poc_percent', 0),
                        'distance_to_vah_percent': position_1d.get('distance_to_vah_percent', 0),
                        'distance_to_val_percent': position_1d.get('distance_to_val_percent', 0),
                        'value_area_width_percent': vp_1d['value_area']['width_percentage']
                    }
                
                if vp_4h:
                    position_4h = self.volume_profile.get_current_position_in_profile(current_price, vp_4h)
                    result['volume_profile']['4h'] = {
                        'poc': vp_4h['poc']['price'],
                        'vah': vp_4h['vah'],
                        'val': vp_4h['val'],
                        'current_position': position_4h.get('position'),
                        'distance_to_poc_percent': position_4h.get('distance_to_poc_percent', 0)
                    }
                
                if vp_1h:
                    position_1h = self.volume_profile.get_current_position_in_profile(current_price, vp_1h)
                    result['volume_profile']['1h'] = {
                        'poc': vp_1h['poc']['price'],
                        'vah': vp_1h['vah'],
                        'val': vp_1h['val'],
                        'current_position': position_1h.get('position'),
                        'distance_to_poc_percent': position_1h.get('distance_to_poc_percent', 0)
                    }
            
            # Fair Value Gaps
            if data.get('fair_value_gaps'):
                for tf in ['1d', '4h', '1h']:
                    fvg_data = data['fair_value_gaps'].get(tf)
                    if fvg_data:
                        stats = fvg_data['statistics']
                        nearest = fvg_data.get('nearest_gaps', {})
                        
                        result['fair_value_gaps'][tf] = {
                            'unfilled_bullish_gaps': stats['unfilled_bullish_gaps'],
                            'unfilled_bearish_gaps': stats['unfilled_bearish_gaps'],
                            'fill_rate_bullish_percent': stats['fill_rate_bullish_percent'],
                            'fill_rate_bearish_percent': stats['fill_rate_bearish_percent'],
                            'nearest_bullish_fvg': {
                                'top': nearest.get('bullish', {}).get('top'),
                                'bottom': nearest.get('bullish', {}).get('bottom'),
                                'size_percent': nearest.get('bullish', {}).get('size_percentage'),
                                'distance_to_bottom_percent': nearest.get('bullish', {}).get('distance_to_bottom_percent')
                            } if nearest.get('bullish') else None,
                            'nearest_bearish_fvg': {
                                'top': nearest.get('bearish', {}).get('top'),
                                'bottom': nearest.get('bearish', {}).get('bottom'),
                                'size_percent': nearest.get('bearish', {}).get('size_percentage'),
                                'distance_to_top_percent': nearest.get('bearish', {}).get('distance_to_top_percent')
                            } if nearest.get('bearish') else None
                        }
            
            # Order Blocks
            if data.get('order_blocks'):
                for tf in ['1d', '4h', '1h']:
                    ob_data = data['order_blocks'].get(tf)
                    if ob_data:
                        stats = ob_data['statistics']
                        nearest = ob_data.get('nearest_blocks', {})
                        
                        result['order_blocks'][tf] = {
                            'active_swing_obs': stats['active_swing_obs'],
                            'active_internal_obs': stats['active_internal_obs'],
                            'mitigation_rate_swing_percent': stats['mitigation_rate_swing_percent'],
                            'mitigation_rate_internal_percent': stats['mitigation_rate_internal_percent'],
                            'nearest_swing_ob': {
                                'bias': nearest.get('swing', {}).get('bias'),
                                'top': nearest.get('swing', {}).get('top'),
                                'bottom': nearest.get('swing', {}).get('bottom'),
                                'distance_to_bottom_percent': nearest.get('swing', {}).get('distance_to_bottom_percent'),
                                'distance_to_top_percent': nearest.get('swing', {}).get('distance_to_top_percent')
                            } if nearest.get('swing') else None,
                            'nearest_internal_ob': {
                                'bias': nearest.get('internal', {}).get('bias'),
                                'top': nearest.get('internal', {}).get('top'),
                                'bottom': nearest.get('internal', {}).get('bottom')
                            } if nearest.get('internal') else None
                        }
            
            # Support/Resistance
            if data.get('support_resistance'):
                for tf in ['1d', '4h', '1h']:
                    sr_data = data['support_resistance'].get(tf)
                    if sr_data:
                        stats = sr_data['statistics']
                        nearest = sr_data.get('nearest_zones', {})
                        
                        result['support_resistance'][tf] = {
                            'active_support_zones': stats['active_support_zones'],
                            'active_resistance_zones': stats['active_resistance_zones'],
                            'break_rate_support_percent': stats['break_rate_support_percent'],
                            'break_rate_resistance_percent': stats['break_rate_resistance_percent'],
                            'nearest_support': {
                                'price': nearest.get('support', {}).get('price'),
                                'volume_ratio': nearest.get('support', {}).get('volume_ratio'),
                                'delta_volume': nearest.get('support', {}).get('delta_volume'),
                                'distance_percent': nearest.get('support', {}).get('distance_percent')
                            } if nearest.get('support') else None,
                            'nearest_resistance': {
                                'price': nearest.get('resistance', {}).get('price'),
                                'volume_ratio': nearest.get('resistance', {}).get('volume_ratio'),
                                'delta_volume': nearest.get('resistance', {}).get('delta_volume'),
                                'distance_percent': nearest.get('resistance', {}).get('distance_percent')
                            } if nearest.get('resistance') else None
                        }
            
            # Smart Money Concepts
            if data.get('smart_money_concepts'):
                for tf in ['1d', '4h', '1h']:
                    smc_data = data['smart_money_concepts'].get(tf)
                    if smc_data:
                        swing_structure = smc_data['swing_structure']
                        internal_structure = smc_data['internal_structure']
                        stats = smc_data['statistics']
                        bias_info = self.smc_analyzer.get_trading_bias(smc_data)
                        
                        result['smart_money_concepts'][tf] = {
                            'swing_trend': swing_structure['trend'],
                            'internal_trend': internal_structure['trend'],
                            'structure_bias': smc_data['structure_bias'],
                            'recent_bullish_bos': stats['recent_bullish_bos'],
                            'recent_bearish_bos': stats['recent_bearish_bos'],
                            'recent_bullish_choch': stats['recent_bullish_choch'],
                            'recent_bearish_choch': stats['recent_bearish_choch'],
                            'eqh_count': stats['eqh_count'],
                            'eql_count': stats['eql_count'],
                            'trading_bias': bias_info['bias'],
                            'bias_confidence': bias_info['confidence'],
                            'bias_reason': bias_info['reason'],
                            'last_swing_high': swing_structure.get('last_swing_high'),
                            'last_swing_low': swing_structure.get('last_swing_low')
                        }
            
            return result
            
        except Exception as e:
            logger.error(f"Error formatting institutional indicators JSON: {e}")
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
        
        # Format extended historical klines context
        historical_klines = data.get('historical_klines', {})
        hist_klines_text = ""
        if historical_klines:
            hist_klines_text = "\n═══════════════════════════════════════════\n📊 DỮ LIỆU LỊCH SỬ MỞ RỘNG (HISTORICAL KLINES CONTEXT)\n═══════════════════════════════════════════\n\n"
            
            # 1H context (7 days)
            if '1h' in historical_klines:
                h1 = historical_klines['1h']
                if h1:
                    pr = h1['price_range']
                    vol = h1['volume']
                    rsi = h1['rsi_stats']
                    trend = h1['trend']
                    pattern = h1['candle_pattern']
                    
                    hist_klines_text += f"""⏰ KHUNG 1H (7 NGÀY QUA - {h1['candles_count']} nến):
  
  📈 Giá:
    - Vùng: ${pr['low']:,.4f} - ${pr['high']:,.4f} (Range: {pr['range_pct']:.2f}%)
    - Hiện tại: ${pr['current']:,.4f} (Vị trí: {pr['position_in_range_pct']:.1f}% của range)
    - Trung bình: ${pr['average']:,.4f}
  
  📊 Volume:
    - Trung bình: {vol['average']:,.0f}
    - Hiện tại: {vol['current']:,.0f} (Tỷ lệ: {vol['current_vs_avg_ratio']:.2f}x)
    - Xu hướng: {vol['trend']}
  
  🎯 RSI:
    - Trung bình: {rsi['average']:.1f}
    - Hiện tại: {rsi['current']:.1f}
    - Dao động: {rsi['min']:.1f} - {rsi['max']:.1f}
  
  📉 Xu hướng 7 ngày:
    - Hướng: {trend['direction']} ({trend['change_pct']:+.2f}%)
    - Độ biến động: {trend['volatility_pct']:.2f}%
    - Tỷ lệ nến tăng: {pattern['bullish_ratio_pct']:.1f}% ({pattern['bullish_candles']}/{h1['candles_count']} nến)

"""
            
            # 4H context (30 days)
            if '4h' in historical_klines:
                h4 = historical_klines['4h']
                if h4:
                    pr = h4['price_range']
                    vol = h4['volume']
                    rsi = h4['rsi_stats']
                    trend = h4['trend']
                    pattern = h4['candle_pattern']
                    
                    hist_klines_text += f"""⏰ KHUNG 4H (30 NGÀY QUA - {h4['candles_count']} nến):
  
  📈 Giá:
    - Vùng: ${pr['low']:,.4f} - ${pr['high']:,.4f} (Range: {pr['range_pct']:.2f}%)
    - Hiện tại: ${pr['current']:,.4f} (Vị trí: {pr['position_in_range_pct']:.1f}% của range)
    - Trung bình: ${pr['average']:,.4f}
  
  📊 Volume:
    - Trung bình: {vol['average']:,.0f}
    - Hiện tại: {vol['current']:,.0f} (Tỷ lệ: {vol['current_vs_avg_ratio']:.2f}x)
    - Xu hướng: {vol['trend']}
  
  🎯 RSI:
    - Trung bình: {rsi['average']:.1f}
    - Hiện tại: {rsi['current']:.1f}
    - Dao động: {rsi['min']:.1f} - {rsi['max']:.1f}
  
  📉 Xu hướng 30 ngày:
    - Hướng: {trend['direction']} ({trend['change_pct']:+.2f}%)
    - Độ biến động: {trend['volatility_pct']:.2f}%
    - Tỷ lệ nến tăng: {pattern['bullish_ratio_pct']:.1f}% ({pattern['bullish_candles']}/{h4['candles_count']} nến)

"""
            
            # 1D context (90 days)
            if '1d' in historical_klines:
                d1 = historical_klines['1d']
                if d1:
                    pr = d1['price_range']
                    vol = d1['volume']
                    rsi = d1['rsi_stats']
                    mfi = d1['mfi_stats']
                    trend = d1['trend']
                    pattern = d1['candle_pattern']
                    
                    hist_klines_text += f"""⏰ KHUNG 1D (90 NGÀY QUA - {d1['candles_count']} nến):
  
  📈 Giá:
    - Vùng: ${pr['low']:,.4f} - ${pr['high']:,.4f} (Range: {pr['range_pct']:.2f}%)
    - Hiện tại: ${pr['current']:,.4f} (Vị trí: {pr['position_in_range_pct']:.1f}% của range)
    - Trung bình: ${pr['average']:,.4f}
  
  📊 Volume:
    - Trung bình: {vol['average']:,.0f}
    - Hiện tại: {vol['current']:,.0f} (Tỷ lệ: {vol['current_vs_avg_ratio']:.2f}x)
    - Xu hướng: {vol['trend']}
  
  🎯 RSI & MFI:
    - RSI trung bình: {rsi['average']:.1f} | Hiện tại: {rsi['current']:.1f}
    - RSI dao động: {rsi['min']:.1f} - {rsi['max']:.1f}
    - MFI trung bình: {mfi['average']:.1f} | Hiện tại: {mfi['current']:.1f}
  
  📉 Xu hướng 90 ngày:
    - Hướng: {trend['direction']} ({trend['change_pct']:+.2f}%)
    - Độ biến động: {trend['volatility_pct']:.2f}%
    - Tỷ lệ nến tăng: {pattern['bullish_ratio_pct']:.1f}% ({pattern['bullish_candles']}/{d1['candles_count']} nến)

"""
            
            hist_klines_text += """HƯỚNG DẪN PHÂN TÍCH DỮ LIỆU LỊCH SỬ:
1. VỊ TRÍ TRONG RANGE: 
   - <30%: Gần đáy range → Cơ hội mua nếu trend tăng
   - 30-70%: Giữa range → Chờ xác nhận
   - >70%: Gần đỉnh range → Cẩn trọng nếu đang long

2. VOLUME RATIO:
   - >1.5x: Volume tăng mạnh → Quan tâm đột biến
   - 0.8-1.2x: Volume bình thường
   - <0.8x: Volume yếu → Thiếu conviction

3. RSI CONTEXT:
   - RSI hiện tại vs trung bình: Đánh giá momentum
   - RSI dao động: Range hẹp (<20) = sideway, Range rộng (>40) = trending
   - So sánh RSI các timeframe: Xác định trend đa khung

4. TREND CONSISTENCY:
   - Tỷ lệ nến tăng >60%: Uptrend rõ ràng
   - Tỷ lệ nến tăng 40-60%: Sideway/Consolidation
   - Tỷ lệ nến tăng <40%: Downtrend

5. VOLATILITY:
   - >3%: Biến động cao → Rủi ro cao, cơ hội cao
   - 1-3%: Biến động trung bình
   - <1%: Biến động thấp → Sideway

SỬ DỤNG DỮ LIỆU NÀY ĐỂ:
- Xác định vùng giá quan trọng (support/resistance lịch sử)
- Đánh giá độ mạnh của trend hiện tại
- So sánh volume hiện tại với lịch sử
- Nhận biết pattern đảo chiều sớm
- Tính toán risk/reward dựa trên range lịch sử
"""
        
        # Format institutional indicators as JSON
        institutional_json = self._format_institutional_indicators_json(data, market)
        
        # Build full prompt
        prompt = f"""You are an expert cryptocurrency trading analyst with 10+ years of experience in technical analysis and market psychology.

TRADING STYLE: {trading_style.upper()}
- If scalping: Focus on 1m-5m-15m timeframes, quick entries/exits, tight stop losses
- If swing: Focus on 1h-4h-1D timeframes, position holding 2-7 days, wider stop losses

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
🏛️ INSTITUTIONAL INDICATORS (JSON STRUCTURED)
═══════════════════════════════════════════

CRITICAL: Analyze this institutional data systematically. This represents smart money footprints.

```json
{json.dumps(institutional_json, indent=2, default=str)}
```

KEY INTERPRETATIONS:
- volume_profile: POC=highest volume price, VAH/VAL=value area boundaries, position=current price location
- fair_value_gaps: Unfilled gaps act as magnets (price tends to fill them), high fill_rate=reliable zones
- order_blocks: Institutional accumulation/distribution zones, ACTIVE blocks=strong S/R
- support_resistance: High volume_ratio (>2x)=very strong zones, delta_volume=buy/sell pressure
- smart_money_concepts: BOS=continuation, CHoCH=reversal, EQH/EQL=accumulation zones

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
{hist_klines_text}
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
4. **Institutional Indicators (CRITICAL - Weight 40% - JSON FORMAT ABOVE):**
   
   **READ THE JSON DATA CAREFULLY - Each field has specific meaning:**
   
   - **Volume Profile (volume_profile):**
     * poc = Point of Control (highest volume price level)
     * vah = Value Area High (top of 68% volume range)
     * val = Value Area Low (bottom of 68% volume range)
     * current_position values:
       - "PREMIUM" (above VAH): Price is expensive, expect rejection or strong continuation
       - "DISCOUNT" (below VAL): Price is cheap, expect bounce or deeper correction
       - "AT_POC": At highest volume level, strong S/R, expect high volatility
       - "VALUE_AREA": Inside fair value zone, balanced price, watch for breakout
     * distance_to_poc_percent: Negative=below POC, Positive=above POC
     * bias: Expected price direction based on position
   
   - **Fair Value Gaps (fair_value_gaps):**
     * Gaps are imbalance zones where price moved too fast (no trading occurred)
     * unfilled_bullish_gaps: Gaps below price = support magnets (price tends to fill them)
     * unfilled_bearish_gaps: Gaps above price = resistance magnets
     * fill_rate_percent: >70% = highly reliable zones that price will revisit
     * nearest_bullish_fvg: If exists, strong support zone below current price
     * nearest_bearish_fvg: If exists, strong resistance zone above current price
     * distance_percent: Negative=below price, Positive=above price
   
   - **Order Blocks (order_blocks):**
     * OBs = Last opposite candle before structure break (institutional footprints)
     * active_swing_obs: Major institutional levels (50-period structure)
     * active_internal_obs: Minor levels (5-period structure)
     * mitigation_rate_percent: How often OBs get broken (lower=stronger zones)
     * nearest_swing_ob.bias: "BULLISH"=support, "BEARISH"=resistance
     * If bias=BULLISH and price near bottom: Strong support entry zone
     * If bias=BEARISH and price near top: Strong resistance exit zone
   
   - **Support/Resistance (support_resistance):**
     * High volume zones at pivot points (smart money accumulation)
     * volume_ratio: >2x = very strong zone, >3x = extremely strong
     * delta_volume: Positive=buying pressure, Negative=selling pressure
     * nearest_support: If price approaching, watch for bounce
     * nearest_resistance: If price approaching, watch for rejection
     * distance_percent: How far from current price
   
   - **Smart Money Concepts (smart_money_concepts):**
     * swing_trend: "BULLISH" or "BEARISH" or "NEUTRAL" (main trend)
     * internal_trend: Short-term trend (can diverge from swing)
     * structure_bias: Alignment between swing and internal
       - "BULLISH_ALIGNED" or "BEARISH_ALIGNED" = Strong trend (high confidence)
       - Mixed trends = Divergence (caution, possible reversal)
     * BOS (Break of Structure): Trend continuation signals
       - recent_bullish_bos > recent_bearish_bos = Strong uptrend
       - recent_bearish_bos > recent_bullish_bos = Strong downtrend
     * CHoCH (Change of Character): Trend reversal signals
       - recent_bullish_choch: Potential bottom/reversal up
       - recent_bearish_choch: Potential top/reversal down
     * eqh_count, eql_count: Multiple touches at same level = accumulation zones
     * trading_bias: AI-calculated bias with confidence level
     * bias_reason: Why this bias was determined
   
   **INTEGRATION RULES:**
   - If Volume Profile shows DISCOUNT + Bullish FVG nearby + Bullish OB active + SMC shows bullish CHoCH → STRONG BUY
   - If Volume Profile shows PREMIUM + Bearish FVG nearby + Bearish OB active + SMC shows bearish CHoCH → STRONG SELL
   - If current_price near POC + multiple active OBs → Expect high volatility breakout
   - If price in VALUE_AREA but no clear FVGs/OBs → NEUTRAL/WAIT
   - Weight SMC trading_bias heavily (it's pre-calculated with confluence)
   - High volume_ratio S/R zones (>2x) are NON-NEGOTIABLE levels
   
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
            try:
                response = self.model.generate_content(prompt)
            except Exception as api_error:
                logger.error(f"Gemini API call failed for {symbol}: {api_error}")
                # Check for specific errors
                error_msg = str(api_error).lower()
                if 'quota' in error_msg or 'rate' in error_msg:
                    logger.error("⚠️ Rate limit exceeded or quota exhausted")
                elif 'key' in error_msg or 'auth' in error_msg:
                    logger.error("⚠️ API key authentication failed")
                elif 'timeout' in error_msg:
                    logger.error("⚠️ API request timeout")
                return None
            
            if not response or not response.text:
                logger.error(f"Empty response from Gemini for {symbol}")
                return None
            
            logger.info(f"Got response from Gemini for {symbol} (length: {len(response.text)} chars)")
            
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
            
            # Validate JSON before parsing
            if not response_text:
                logger.error(f"Empty response text after cleaning for {symbol}")
                return None
            
            # Parse JSON
            try:
                analysis = json.loads(response_text)
            except json.JSONDecodeError as json_err:
                logger.error(f"JSON parsing failed for {symbol}: {json_err}")
                logger.error(f"Response preview: {response_text[:500]}...")
                return None
            
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
            
            logger.info(f"✅ Gemini analysis complete for {symbol}: {analysis['recommendation']} (confidence: {analysis['confidence']}%)")
            
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Error in Gemini analysis for {symbol}: {e}", exc_info=True)
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
            
            summary = "═══════════════════════════════════\n"
            summary += "🤖 <b>GEMINI AI ANALYSIS</b>\n"
            summary += "═══════════════════════════════════\n\n"
            summary += f"💎 <b>{symbol}</b>\n"
            summary += f"📊 <b>Trading Style:</b> {style.upper()}\n\n"
            summary += "───────────────────────────────────\n"
            summary += f"{rec_emoji} <b>KHUYẾN NGHỊ:</b> {rec}\n"
            summary += f"🎯 <b>Độ Tin Cậy:</b> {conf}%\n"
            summary += f"⚠️ <b>Mức Rủi Ro:</b> {risk}\n"
            summary += "───────────────────────────────────\n\n"
            
            summary += "💰 <b>KẾ HOẠCH GIAO DỊCH:</b>\n\n"
            summary += f"   📍 <b>Điểm Vào:</b> ${self.binance.format_price(symbol, entry)}\n"
            summary += f"   🛑 <b>Cắt Lỗ:</b> ${self.binance.format_price(symbol, stop)}\n"
            summary += f"   🎯 <b>Chốt Lời:</b>\n"
            for i, target in enumerate(targets, 1):
                summary += f"      • TP{i}: ${self.binance.format_price(symbol, target)}\n"
            summary += f"   ⏱ <b>Thời Gian Nắm Giữ:</b> {period}\n\n"
            summary += "═══════════════════════════════════"
            
            # Message 2: Technical Details
            tech = "═══════════════════════════════════\n"
            tech += "📊 <b>PHÂN TÍCH KỸ THUẬT CHI TIẾT</b>\n"
            tech += "═══════════════════════════════════\n\n"
            tech += f"💎 <b>{symbol}</b>\n\n"
            
            # Data used
            data_used = analysis.get('data_used', {})
            tech += "<b>🔍 Các Chỉ Báo Được Sử Dụng:</b>\n"
            tech += f"   • RSI+MFI: {data_used.get('rsi_mfi_consensus', 'N/A')}\n"
            tech += f"   • Stoch+RSI: {data_used.get('stoch_rsi_consensus', 'N/A')}\n"
            
            pump_score = data_used.get('pump_score', 0)
            if pump_score >= 80:
                tech += f"   • 🚀 Tín Hiệu Pump: {pump_score:.0f}% (Độ Tin Cậy Cao)\n"
            elif pump_score > 0:
                tech += f"   • Tín Hiệu Pump: {pump_score:.0f}%\n"
            
            tech += f"   • Giá Hiện Tại: ${self.binance.format_price(symbol, data_used.get('current_price', 0))}\n\n"
            
            # Scores
            tech_score = analysis.get('technical_score', 0)
            fund_score = analysis.get('fundamental_score', 0)
            
            tech += "<b>📈 Điểm Đánh Giá:</b>\n"
            tech += f"   • Kỹ Thuật: {tech_score}/100\n"
            tech += f"   • Cơ Bản: {fund_score}/100\n"
            tech += f"   • Tổng Hợp: {(tech_score + fund_score)/2:.0f}/100\n\n"
            
            # Market sentiment
            sentiment = analysis.get('market_sentiment', 'NEUTRAL')
            sentiment_emoji = "🟢" if sentiment == "BULLISH" else "🔴" if sentiment == "BEARISH" else "🟡"
            sentiment_vn = "TĂNG GIÁ" if sentiment == "BULLISH" else "GIẢM GIÁ" if sentiment == "BEARISH" else "TRUNG LẬP"
            tech += f"<b>💭 Tâm Lý Thị Trường:</b> {sentiment_emoji} {sentiment_vn}\n\n"
            
            # Key points
            tech += "<b>🎯 Điểm Chính:</b>\n"
            for point in analysis.get('key_points', []):
                tech += f"   ✓ {point}\n"
            
            # Conflicting signals
            conflicts = analysis.get('conflicting_signals', [])
            if conflicts:
                tech += "\n<b>⚠️ Tín Hiệu Mâu Thuẫn:</b>\n"
                for conflict in conflicts:
                    tech += f"   • {conflict}\n"
            
            # Warnings
            warnings = analysis.get('warnings', [])
            if warnings:
                tech += "\n<b>🚨 Cảnh Báo:</b>\n"
                for warning in warnings:
                    tech += f"   ⚠️ {warning}\n"
            
            tech += "\n═══════════════════════════════════"
            
            # Message 3: AI Reasoning
            reasoning = "═══════════════════════════════════\n"
            reasoning += "🧠 <b>PHÂN TÍCH CHI TIẾT TỪ AI</b>\n"
            reasoning += "═══════════════════════════════════\n\n"
            reasoning += f"💎 <b>{symbol}</b>\n\n"
            reasoning += analysis.get('reasoning_vietnamese', 'Không có phân tích chi tiết.')
            reasoning += f"\n\n───────────────────────────────────\n"
            reasoning += f"⏰ <b>Thời Gian Phân Tích:</b> {analysis.get('analyzed_at', 'N/A')}\n"
            reasoning += f"🤖 <b>Mô Hình AI:</b> Gemini 2.0 Flash\n"
            reasoning += "───────────────────────────────────\n\n"
            reasoning += "<i>⚠️ Đây là phân tích AI, không phải tư vấn tài chính.\n"
            reasoning += "Luôn DYOR (Do Your Own Research) trước khi đầu tư.</i>\n"
            reasoning += "═══════════════════════════════════"
            
            return summary, tech, reasoning
            
        except Exception as e:
            logger.error(f"Error formatting response: {e}")
            error_msg = f"❌ Lỗi khi format kết quả AI analysis: {str(e)}"
            return error_msg, "", ""
