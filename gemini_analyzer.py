"""
Gemini AI Trading Analyzer v3.3
Integrates Google Gemini 1.5 Pro for comprehensive trading analysis

Enhanced with:
- Advanced Pump/Dump Detector integration
- Real-time data from 15+ sources
- Sentiment analysis & on-chain data
- Institutional flow detection
- 5 BOT type detection

Author: AI Assistant
Date: November 20, 2025
"""

import google.generativeai as genai
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import time
import os

logger = logging.getLogger(__name__)

# Import database and price tracker
try:
    from database import get_db, AnalysisDatabase
    from price_tracker import get_tracker, PriceTracker
    DATABASE_AVAILABLE = True
    logger.info("✅ Database and Price Tracker modules loaded")
except ImportError as e:
    logger.warning(f"⚠️ Database/Price Tracker not available: {e}")
    DATABASE_AVAILABLE = False

# Import advanced detection
try:
    from advanced_pump_detector import AdvancedPumpDumpDetector, integrate_advanced_detection_to_prompt
    ADVANCED_DETECTOR_AVAILABLE = True
    logger.info("✅ Advanced Pump/Dump Detector loaded")
except ImportError as e:
    logger.warning(f"⚠️ Advanced Detector not available: {e}")
    ADVANCED_DETECTOR_AVAILABLE = False


class GeminiAnalyzer:
    """
    Google Gemini AI integration for advanced trading analysis v3.3
    
    Features:
    - Comprehensive multi-indicator analysis
    - Historical comparison (week-over-week)
    - Scalping and swing trading recommendations
    - Risk assessment and entry/exit points
    - Vietnamese language output
    - Advanced pump/dump detection with institutional flow
    - 5 BOT type detection (Wash Trading, Spoofing, Iceberg, Market Maker, Dump)
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
        
        # Initialize database connection
        self.db = None
        self.tracker = None
        self.db_available = DATABASE_AVAILABLE  # Store as instance variable
        
        if self.db_available:
            try:
                self.db = get_db()
                self.tracker = get_tracker()
                logger.info("✅ Database and Price Tracker initialized")
            except Exception as e:
                logger.warning(f"⚠️ Failed to initialize database/tracker: {e}")
                self.db_available = False
        
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
        
        # Initialize Advanced Detector (NEW)
        self.advanced_detector = None
        if ADVANCED_DETECTOR_AVAILABLE:
            try:
                self.advanced_detector = AdvancedPumpDumpDetector(binance_client)
                logger.info("✅ Advanced Pump/Dump Detector initialized")
            except Exception as e:
                logger.warning(f"⚠️ Failed to initialize Advanced Detector: {e}")
        
        # Configure Gemini
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Cache system (15 minutes)
        self.cache = {}  # {symbol: {'data': result, 'timestamp': time.time()}}
        self.cache_duration = 900  # 15 minutes in seconds
        
        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 1.0  # 1 second between requests
        
        logger.info("✅ Gemini AI Analyzer v3.3 initialized (gemini-2.5-flash + Advanced Detection + Institutional indicators)")
    
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
            
            # === ADVANCED PUMP/DUMP DETECTION (NEW!) ===
            advanced_detection = None
            if self.advanced_detector:
                try:
                    logger.info(f"🤖 Running advanced pump/dump detection for {symbol}...")
                    
                    # Get recent trades for advanced analysis
                    recent_trades = []
                    order_book = None
                    try:
                        recent_trades = self.binance.client.get_recent_trades(symbol=symbol, limit=500)
                        order_book = self.binance.client.get_order_book(symbol=symbol, limit=100)
                    except:
                        logger.debug("Could not fetch trades/orderbook for advanced detection")
                    
                    # Run comprehensive analysis
                    advanced_detection = self.advanced_detector.analyze_comprehensive(
                        symbol=symbol,
                        klines_5m=klines_dict.get('5m'),
                        klines_1h=klines_dict.get('1h'),
                        order_book=order_book,
                        trades=recent_trades,
                        market_data=ticker_24h
                    )
                    
                    if advanced_detection:
                        signal = advanced_detection.get('signal', 'NEUTRAL')
                        confidence = advanced_detection.get('confidence', 0)
                        direction_prob = advanced_detection.get('direction_probability', {})
                        
                        logger.info(f"✅ Advanced Detection: Signal={signal}, Confidence={confidence}%, UP={direction_prob.get('up')}%")
                        
                        # Log warnings
                        if signal in ['STRONG_DUMP', 'DUMP']:
                            logger.warning(f"⚠️ {symbol}: {signal} detected - Confidence {confidence}%")
                        
                        bot_activity = advanced_detection.get('bot_activity', {})
                        for bot_type, data in bot_activity.items():
                            if data.get('detected'):
                                logger.warning(f"🚨 {symbol}: {bot_type.upper()} BOT detected (confidence {data.get('confidence')}%)")
                
                except Exception as e:
                    logger.error(f"Error in advanced detection for {symbol}: {e}")
            
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
                'smart_money_concepts': smc_result,
                # Advanced detection (NEW)
                'advanced_detection': advanced_detection
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
        Analyze a historical period and extract key statistics INCLUDING institutional indicators
        
        Args:
            df: DataFrame with OHLCV data
            period_name: Name of the period for logging
            
        Returns:
            Dict with statistics including institutional analysis
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
            
            # ============================================================
            # INSTITUTIONAL INDICATORS ON HISTORICAL DATA
            # ============================================================
            
            institutional_stats = {}
            
            try:
                # Volume Profile analysis on historical range
                vp_stats = self._analyze_volume_profile_historical(df, current_price)
                institutional_stats['volume_profile'] = vp_stats
            except Exception as e:
                logger.warning(f"Volume Profile historical analysis failed: {e}")
                institutional_stats['volume_profile'] = {}
            
            try:
                # Fair Value Gaps count and nearest gaps
                fvg_stats = self._analyze_fvg_historical(df, current_price)
                institutional_stats['fair_value_gaps'] = fvg_stats
            except Exception as e:
                logger.warning(f"FVG historical analysis failed: {e}")
                institutional_stats['fair_value_gaps'] = {}
            
            try:
                # Order Blocks active count and strength
                ob_stats = self._analyze_order_blocks_historical(df, current_price)
                institutional_stats['order_blocks'] = ob_stats
            except Exception as e:
                logger.warning(f"Order Blocks historical analysis failed: {e}")
                institutional_stats['order_blocks'] = {}
            
            try:
                # Smart Money structure changes over time
                smc_stats = self._analyze_smc_historical(df)
                institutional_stats['smart_money'] = smc_stats
            except Exception as e:
                logger.warning(f"SMC historical analysis failed: {e}")
                institutional_stats['smart_money'] = {}
            
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
                },
                'institutional_indicators': institutional_stats  # NEW: Institutional analysis
            }
            
            logger.info(f"✅ Analyzed {period_name} ({total_candles} candles): "
                       f"trend={trend_direction} ({trend_pct:+.2f}%), "
                       f"volatility={volatility:.2f}%, "
                       f"RSI={current_rsi:.1f} (avg={avg_rsi:.1f}), "
                       f"MFI={current_mfi:.1f} (avg={avg_mfi:.1f}), "
                       f"volume={volume_trend} ({current_volume/avg_volume:.2f}x avg)")
            return stats
            
        except Exception as e:
            logger.error(f"Error analyzing historical period {period_name}: {e}")
            return {}
    
    def _analyze_volume_profile_historical(self, df, current_price: float) -> Dict:
        """Analyze Volume Profile metrics over historical period"""
        try:
            # Calculate POC (Point of Control) - price level with highest volume
            # Group by price levels and sum volume
            price_levels = df[['close', 'volume']].copy()
            price_levels['price_level'] = (price_levels['close'] // 1).astype(int)  # Round to nearest dollar
            volume_by_level = price_levels.groupby('price_level')['volume'].sum()
            
            if len(volume_by_level) == 0:
                return {}
            
            poc_price = float(volume_by_level.idxmax())
            poc_volume = float(volume_by_level.max())
            
            # Value Area (70% of volume) estimation
            total_volume = float(df['volume'].sum())
            sorted_levels = volume_by_level.sort_values(ascending=False)
            cumsum = sorted_levels.cumsum()
            value_area_levels = sorted_levels[cumsum <= total_volume * 0.7]
            
            vah = float(value_area_levels.index.max()) if len(value_area_levels) > 0 else poc_price * 1.05
            val = float(value_area_levels.index.min()) if len(value_area_levels) > 0 else poc_price * 0.95
            
            # Current price position relative to Value Area
            if current_price > vah:
                position = "PREMIUM"
            elif current_price < val:
                position = "DISCOUNT"
            else:
                position = "VALUE_AREA"
            
            # Distance from POC
            if poc_price > 0:
                distance_from_poc = ((current_price - poc_price) / poc_price) * 100
            else:
                distance_from_poc = 0.0
            
            return {
                'poc': round(poc_price, 4),
                'vah': round(vah, 4),
                'val': round(val, 4),
                'current_position': position,
                'distance_from_poc_pct': round(distance_from_poc, 2),
                'poc_volume': round(poc_volume, 2),
                'value_area_coverage': 70.0
            }
        except Exception as e:
            logger.warning(f"Volume Profile historical calc error: {e}")
            return {}
    
    def _analyze_fvg_historical(self, df, current_price: float) -> Dict:
        """Analyze Fair Value Gaps over historical period"""
        try:
            bullish_gaps = 0
            bearish_gaps = 0
            unfilled_bullish = []
            unfilled_bearish = []
            
            # Detect gaps: gap exists when candle i+1 leaves a gap with candle i-1
            for i in range(1, len(df) - 1):
                prev_candle = df.iloc[i-1]
                curr_candle = df.iloc[i]
                next_candle = df.iloc[i+1]
                
                # Bullish FVG: low[i+1] > high[i-1]
                if next_candle['low'] > prev_candle['high']:
                    gap_top = next_candle['low']
                    gap_bottom = prev_candle['high']
                    bullish_gaps += 1
                    
                    # Check if gap is still unfilled (current price hasn't gone back to fill it)
                    if current_price > gap_top:
                        unfilled_bullish.append({
                            'bottom': float(gap_bottom),
                            'top': float(gap_top),
                            'index': i
                        })
                
                # Bearish FVG: high[i+1] < low[i-1]
                if next_candle['high'] < prev_candle['low']:
                    gap_top = prev_candle['low']
                    gap_bottom = next_candle['high']
                    bearish_gaps += 1
                    
                    # Check if gap is still unfilled
                    if current_price < gap_bottom:
                        unfilled_bearish.append({
                            'bottom': float(gap_bottom),
                            'top': float(gap_top),
                            'index': i
                        })
            
            # Find nearest unfilled gaps
            nearest_bullish = None
            nearest_bearish = None
            
            if unfilled_bullish:
                # Nearest bullish gap below current price
                nearest_bullish = min(unfilled_bullish, key=lambda g: current_price - g['top'])
            
            if unfilled_bearish:
                # Nearest bearish gap above current price
                nearest_bearish = min(unfilled_bearish, key=lambda g: g['bottom'] - current_price)
            
            return {
                'total_bullish_gaps': bullish_gaps,
                'total_bearish_gaps': bearish_gaps,
                'unfilled_bullish_count': len(unfilled_bullish),
                'unfilled_bearish_count': len(unfilled_bearish),
                'nearest_bullish_gap': nearest_bullish,
                'nearest_bearish_gap': nearest_bearish,
                'gap_density_pct': round(((bullish_gaps + bearish_gaps) / len(df)) * 100, 2)
            }
        except Exception as e:
            logger.warning(f"FVG historical calc error: {e}")
            return {}
    
    def _analyze_order_blocks_historical(self, df, current_price: float) -> Dict:
        """Analyze Order Blocks over historical period"""
        try:
            bullish_ob_count = 0
            bearish_ob_count = 0
            active_bullish = []
            active_bearish = []
            
            # Detect Order Blocks: significant candles before strong moves
            for i in range(len(df) - 2):
                curr = df.iloc[i]
                next1 = df.iloc[i+1]
                next2 = df.iloc[i+2] if i+2 < len(df) else None
                
                # Bullish OB: Large down candle followed by strong bullish move
                if float(curr['close']) < float(curr['open']):  # Down candle
                    if float(next1['close']) > float(next1['open']) and next2 is not None and float(next2['close']) > float(next2['open']):
                        # Strong 2-candle bullish move after down candle
                        move_pct = ((float(next2['close']) - float(curr['close'])) / float(curr['close'])) * 100
                        if move_pct > 2:  # Significant move
                            ob_high = float(curr['high'])
                            ob_low = float(curr['low'])
                            bullish_ob_count += 1
                            
                            # Check if still active (price hasn't broken below it significantly)
                            if current_price > ob_low * 0.98:
                                active_bullish.append({
                                    'high': ob_high,
                                    'low': ob_low,
                                    'strength': min(move_pct / 2, 10),  # Cap at 10
                                    'index': i
                                })
                
                # Bearish OB: Large up candle followed by strong bearish move
                if float(curr['close']) > float(curr['open']):  # Up candle
                    if float(next1['close']) < float(next1['open']) and next2 is not None and float(next2['close']) < float(next2['open']):
                        move_pct = ((float(curr['close']) - float(next2['close'])) / float(curr['close'])) * 100
                        if move_pct > 2:
                            ob_high = float(curr['high'])
                            ob_low = float(curr['low'])
                            bearish_ob_count += 1
                            
                            if current_price < ob_high * 1.02:
                                active_bearish.append({
                                    'high': ob_high,
                                    'low': ob_low,
                                    'strength': min(move_pct / 2, 10),
                                    'index': i
                                })
            
            # Find strongest active OBs
            strongest_bullish = max(active_bullish, key=lambda x: x['strength']) if active_bullish else None
            strongest_bearish = max(active_bearish, key=lambda x: x['strength']) if active_bearish else None
            
            return {
                'total_bullish_ob': bullish_ob_count,
                'total_bearish_ob': bearish_ob_count,
                'active_bullish_count': len(active_bullish),
                'active_bearish_count': len(active_bearish),
                'strongest_bullish_ob': strongest_bullish,
                'strongest_bearish_ob': strongest_bearish,
                'ob_density_pct': round(((bullish_ob_count + bearish_ob_count) / len(df)) * 100, 2)
            }
        except Exception as e:
            logger.warning(f"Order Blocks historical calc error: {e}")
            return {}
    
    def _analyze_smc_historical(self, df) -> Dict:
        """Analyze Smart Money Concepts over historical period"""
        try:
            # Track structure breaks
            bos_bullish = 0  # Break of Structure (bullish)
            bos_bearish = 0
            choch_bullish = 0  # Change of Character (bullish)
            choch_bearish = 0
            
            # Find swing highs and lows
            swing_highs = []
            swing_lows = []
            
            for i in range(2, len(df) - 2):
                # Swing high: higher than 2 candles before and after
                if (df.iloc[i]['high'] > df.iloc[i-1]['high'] and 
                    df.iloc[i]['high'] > df.iloc[i-2]['high'] and
                    df.iloc[i]['high'] > df.iloc[i+1]['high'] and 
                    df.iloc[i]['high'] > df.iloc[i+2]['high']):
                    swing_highs.append({'index': i, 'price': float(df.iloc[i]['high'])})
                
                # Swing low
                if (df.iloc[i]['low'] < df.iloc[i-1]['low'] and 
                    df.iloc[i]['low'] < df.iloc[i-2]['low'] and
                    df.iloc[i]['low'] < df.iloc[i+1]['low'] and 
                    df.iloc[i]['low'] < df.iloc[i+2]['low']):
                    swing_lows.append({'index': i, 'price': float(df.iloc[i]['low'])})
            
            # Count structure breaks
            for i in range(1, len(swing_highs)):
                if swing_highs[i]['price'] > swing_highs[i-1]['price']:
                    bos_bullish += 1
                else:
                    choch_bearish += 1
            
            for i in range(1, len(swing_lows)):
                if swing_lows[i]['price'] < swing_lows[i-1]['price']:
                    bos_bearish += 1
                else:
                    choch_bullish += 1
            
            # Determine overall structure bias
            net_bullish = bos_bullish + choch_bullish
            net_bearish = bos_bearish + choch_bearish
            total_signals = net_bullish + net_bearish
            
            if total_signals > 0:
                bullish_ratio = (net_bullish / total_signals) * 100
                if bullish_ratio > 60:
                    structure_bias = "BULLISH"
                elif bullish_ratio < 40:
                    structure_bias = "BEARISH"
                else:
                    structure_bias = "NEUTRAL"
            else:
                structure_bias = "NEUTRAL"
                bullish_ratio = 50
            
            return {
                'bos_bullish': bos_bullish,
                'bos_bearish': bos_bearish,
                'choch_bullish': choch_bullish,
                'choch_bearish': choch_bearish,
                'swing_highs_count': len(swing_highs),
                'swing_lows_count': len(swing_lows),
                'structure_bias': structure_bias,
                'bullish_bias_pct': round(bullish_ratio, 2),
                'total_structure_events': total_signals
            }
        except Exception as e:
            logger.warning(f"SMC historical calc error: {e}")
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
    
    def _generate_learning_recommendation(self, rsi_mfi: Dict, vp_data: Dict, 
                                          winning_cond: Dict, losing_cond: Dict,
                                          current_price: float) -> str:
        """
        Generate AI learning recommendation based on historical patterns
        
        Args:
            rsi_mfi: Current RSI/MFI data
            vp_data: Volume Profile data
            winning_cond: Winning pattern conditions
            losing_cond: Losing pattern conditions
            current_price: Current market price
            
        Returns:
            Recommendation text
        """
        try:
            # Get current conditions
            current_rsi = rsi_mfi.get('timeframes', {}).get('1h', {}).get('rsi', 50)
            current_mfi = rsi_mfi.get('timeframes', {}).get('1h', {}).get('mfi', 50)
            
            # Get VP position if available
            vp_1d = vp_data.get('1d', {})
            current_vp_position = "UNKNOWN"
            if vp_1d:
                from volume_profile import VolumeProfileAnalyzer
                position_data = self.volume_profile.get_current_position_in_profile(current_price, vp_1d)
                current_vp_position = position_data.get('position', 'UNKNOWN')
            
            # Check similarity to winning patterns
            similarity_to_wins = 0
            if winning_cond.get('rsi_avg'):
                rsi_distance = abs(current_rsi - winning_cond['rsi_avg'])
                if rsi_distance < 10:  # Within 10 points
                    similarity_to_wins += 40
                elif rsi_distance < 20:
                    similarity_to_wins += 20
            
            if winning_cond.get('best_vp_position') == current_vp_position:
                similarity_to_wins += 30
            
            if winning_cond.get('mfi_avg'):
                mfi_distance = abs(current_mfi - winning_cond['mfi_avg'])
                if mfi_distance < 10:
                    similarity_to_wins += 30
                elif mfi_distance < 20:
                    similarity_to_wins += 15
            
            # Check similarity to losing patterns
            similarity_to_losses = 0
            if losing_cond.get('rsi_avg'):
                rsi_distance = abs(current_rsi - losing_cond['rsi_avg'])
                if rsi_distance < 10:
                    similarity_to_losses += 40
                elif rsi_distance < 20:
                    similarity_to_losses += 20
            
            if losing_cond.get('worst_vp_position') == current_vp_position:
                similarity_to_losses += 30
            
            # Generate recommendation
            if similarity_to_wins > 60:
                return f"✅ STRONG SIGNAL: Current setup matches previous WINS ({similarity_to_wins}% similarity). INCREASE confidence to 85-95%."
            elif similarity_to_losses > 60:
                return f"⚠️ WARNING: Current setup matches previous LOSSES ({similarity_to_losses}% similarity). DECREASE confidence or recommend WAIT."
            elif similarity_to_wins > 40:
                return f"✓ POSITIVE: Setup has {similarity_to_wins}% similarity to wins. Moderate confidence 65-80%."
            elif similarity_to_losses > 40:
                return f"⚠️ CAUTION: Setup has {similarity_to_losses}% similarity to losses. Be conservative, confidence <60%."
            else:
                return "ℹ️ NEUTRAL: New market conditions, no strong historical match. Use standard analysis."
                
        except Exception as e:
            logger.warning(f"Error generating learning recommendation: {e}")
            return "ℹ️ Historical learning data unavailable for this analysis."
    
    def _detect_asset_type(self, symbol: str, market_cap: Optional[float] = None) -> str:
        """
        Detect asset type based on symbol and market cap
        
        Asset Types (v2.2):
        - BTC: Bitcoin, macro-driven, highest priority
        - ETH: Ethereum, smart contracts, institutional
        - LARGE_CAP_ALT: >$10B, lower risk altcoins
        - MID_CAP_ALT: $1B-$10B, moderate risk
        - SMALL_CAP_ALT: $100M-$1B, high risk
        - MEME_COIN: <$100M, extreme risk, community-driven
        
        Args:
            symbol: Trading symbol (e.g., 'BTCUSDT')
            market_cap: Optional market cap in USD
            
        Returns:
            Asset type string
        """
        base = symbol.replace('USDT', '').replace('BUSD', '').replace('USDC', '').upper()
        
        # Check special cases first
        if base == 'BTC':
            return 'BTC'
        elif base == 'ETH':
            return 'ETH'
        
        # Use market cap if available
        if market_cap:
            if market_cap > 10_000_000_000:  # > $10B
                return 'LARGE_CAP_ALT'
            elif market_cap > 1_000_000_000:  # $1B - $10B
                return 'MID_CAP_ALT'
            elif market_cap > 100_000_000:  # $100M - $1B
                return 'SMALL_CAP_ALT'
            else:  # < $100M
                return 'MEME_COIN'
        
        # Fallback: assume altcoin without market cap
        logger.debug(f"Asset type detection: {symbol} (no market cap data available)")
        return 'MID_CAP_ALT'
    
    def _build_prompt(self, data: Dict, trading_style: str = 'swing', user_id: Optional[int] = None) -> str:
        """
        Build Gemini prompt from collected data with historical learning
        
        Args:
            data: Collected analysis data
            trading_style: 'scalping' or 'swing'
            user_id: User ID for historical analysis lookup
            
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
        
        # === NEW: GET HISTORICAL ANALYSIS DATA ===
        historical_context = ""
        if self.db and user_id:
            try:
                # Get past analyses for this symbol
                history = self.db.get_symbol_history(symbol, user_id, days=7)
                stats = self.db.calculate_accuracy_stats(symbol, user_id, days=7)
                
                if stats and stats['total'] > 0:
                    patterns = stats.get('patterns', {})
                    winning_cond = patterns.get('winning_conditions', {})
                    losing_cond = patterns.get('losing_conditions', {})
                    
                    # Get rsi_mfi from data for learning recommendation
                    rsi_mfi = data.get('rsi_mfi', {})
                    
                    historical_context = f"""
═══════════════════════════════════════════
🧠 HISTORICAL PERFORMANCE FOR {symbol} (Last 7 days)
═══════════════════════════════════════════

📊 <b>ACCURACY STATISTICS:</b>
  • Total Analyses: {stats['total']}
  • Wins: {stats['wins']} | Losses: {stats['losses']}
  • Win Rate: {stats['win_rate']:.1f}%
  • Avg Profit: +{stats.get('avg_profit', 0):.2f}% | Avg Loss: {stats.get('avg_loss', 0):.2f}%

✅ <b>WINNING PATTERNS (What worked):</b>
  • RSI Range: {winning_cond.get('rsi_range', 'N/A')} (avg: {winning_cond.get('rsi_avg', 0):.1f})
  • MFI Range: {winning_cond.get('mfi_range', 'N/A')} (avg: {winning_cond.get('mfi_avg', 0):.1f})
  • Best VP Position: {winning_cond.get('best_vp_position', 'N/A')}
  • Win Rate in This Setup: {winning_cond.get('setup_win_rate', 0):.1f}%

❌ <b>LOSING PATTERNS (What didn't work):</b>
  • RSI Range: {losing_cond.get('rsi_range', 'N/A')} (avg: {losing_cond.get('rsi_avg', 0):.1f})
  • MFI Range: {losing_cond.get('mfi_range', 'N/A')} (avg: {losing_cond.get('mfi_avg', 0):.1f})
  • Problem VP Position: {losing_cond.get('worst_vp_position', 'N/A')}

🎯 <b>AI LEARNING RECOMMENDATION:</b>
  {self._generate_learning_recommendation(rsi_mfi, data.get('volume_profile', {}), winning_cond, losing_cond, market['price'])}

⚠️ <b>CRITICAL: Use this historical data to:</b>
  1. Adjust confidence based on similar past setups
  2. Warn if current conditions match previous losses
  3. Increase confidence if conditions match previous wins
  4. Suggest WAIT if win rate for this setup is <40%

═══════════════════════════════════════════
📜 PREVIOUS ANALYSES DETAILS (Read and learn from these)
═══════════════════════════════════════════
"""
                    
                    # Add detailed previous analyses (up to 5 most recent)
                    if history and len(history) > 0:
                        for i, record in enumerate(history[:5], 1):
                            try:
                                ai_response = record.get('ai_full_response', {})
                                tracking = record.get('tracking_result', {})
                                created_at = record.get('created_at', 'Unknown')
                                
                                # Extract key fields from AI response
                                recommendation = ai_response.get('recommendation', 'N/A')
                                confidence = ai_response.get('confidence', 0)
                                entry = ai_response.get('entry_point', 0)
                                stop_loss = ai_response.get('stop_loss', 0)
                                take_profit = ai_response.get('take_profit', [])
                                reasoning = ai_response.get('reasoning_vietnamese', '')
                                
                                # Tracking result
                                outcome = tracking.get('outcome', 'PENDING') if tracking else 'PENDING'
                                profit_pct = tracking.get('profit_percent', 0) if tracking else 0
                                peak_profit = tracking.get('peak_profit_percent', 0) if tracking else 0
                                hit_tp = tracking.get('hit_take_profit', False) if tracking else False
                                hit_sl = tracking.get('hit_stop_loss', False) if tracking else False
                                
                                # Format outcome emoji
                                outcome_emoji = "✅" if outcome == "WIN" else "❌" if outcome == "LOSS" else "⏳"
                                
                                historical_context += f"""
<b>Analysis #{i} - {created_at}</b> {outcome_emoji}
  • Recommendation: {recommendation} (Confidence: {confidence}%)
  • Entry: ${entry:,.2f} | Stop Loss: ${stop_loss:,.2f} | Take Profit: {take_profit}
  • Outcome: {outcome} | Profit: {profit_pct:+.2f}% (Peak: {peak_profit:+.2f}%)
  • Hit TP: {'Yes' if hit_tp else 'No'} | Hit SL: {'Yes' if hit_sl else 'No'}
  • Reasoning Summary: {reasoning[:200]}{'...' if len(reasoning) > 200 else ''}

"""
                            except Exception as detail_error:
                                logger.warning(f"Failed to parse analysis detail #{i}: {detail_error}")
                                continue
                    
                    historical_context += """
<b>🔍 HOW TO USE PREVIOUS ANALYSES:</b>
  1. Check if current market conditions (RSI, MFI, VP position) are similar to past WIN or LOSS
  2. If similar to WIN → Mention it and INCREASE confidence: "Setup tương tự phân tích #X đã thắng +Y%"
  3. If similar to LOSS → Mention it and DECREASE confidence or WAIT: "⚠️ Cảnh báo: Setup giống phân tích #X đã thua -Y%"
  4. Learn from reasoning: If past reasoning was wrong, adjust your logic
  5. If past entry/SL/TP were off, improve current recommendations
"""
                    
                else:
                    historical_context = f"\n🆕 <b>NEW SYMBOL:</b> No historical data for {symbol} yet. First analysis.\n"
                    
            except Exception as e:
                logger.warning(f"Failed to load historical context: {e}")
                historical_context = ""
        
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
                    # Add institutional indicators for 1H
                    inst = h1.get('institutional_indicators', {})
                    if inst:
                        hist_klines_text += "  🏛️ Institutional Indicators (1H - 7 ngày):\n"
                        
                        vp = inst.get('volume_profile', {})
                        if vp:
                            hist_klines_text += f"    • Volume Profile: POC=${vp.get('poc', 0):,.4f}, VAH=${vp.get('vah', 0):,.4f}, VAL=${vp.get('val', 0):,.4f}\n"
                            hist_klines_text += f"      Position: {vp.get('current_position', 'N/A')}, Distance from POC: {vp.get('distance_from_poc_pct', 0):+.2f}%\n"
                        
                        fvg = inst.get('fair_value_gaps', {})
                        if fvg:
                            hist_klines_text += f"    • Fair Value Gaps: {fvg.get('total_bullish_gaps', 0)} bullish, {fvg.get('total_bearish_gaps', 0)} bearish\n"
                            hist_klines_text += f"      Unfilled: {fvg.get('unfilled_bullish_count', 0)} bullish, {fvg.get('unfilled_bearish_count', 0)} bearish\n"
                            hist_klines_text += f"      Gap Density: {fvg.get('gap_density_pct', 0):.2f}%\n"
                        
                        ob = inst.get('order_blocks', {})
                        if ob:
                            hist_klines_text += f"    • Order Blocks: {ob.get('total_bullish_ob', 0)} bullish, {ob.get('total_bearish_ob', 0)} bearish\n"
                            hist_klines_text += f"      Active: {ob.get('active_bullish_count', 0)} bullish, {ob.get('active_bearish_count', 0)} bearish\n"
                            hist_klines_text += f"      OB Density: {ob.get('ob_density_pct', 0):.2f}%\n"
                        
                        smc = inst.get('smart_money', {})
                        if smc:
                            hist_klines_text += f"    • Smart Money Concepts: Structure Bias={smc.get('structure_bias', 'N/A')} ({smc.get('bullish_bias_pct', 0):.1f}% bullish)\n"
                            hist_klines_text += f"      BOS: {smc.get('bos_bullish', 0)} bullish / {smc.get('bos_bearish', 0)} bearish\n"
                            hist_klines_text += f"      CHoCH: {smc.get('choch_bullish', 0)} bullish / {smc.get('choch_bearish', 0)} bearish\n"
                        
                        hist_klines_text += "\n"

            
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
                    # Add institutional indicators for 4H
                    inst = h4.get('institutional_indicators', {})
                    if inst:
                        hist_klines_text += "  🏛️ Institutional Indicators (4H - 30 ngày):\n"
                        
                        vp = inst.get('volume_profile', {})
                        if vp:
                            hist_klines_text += f"    • Volume Profile: POC=${vp.get('poc', 0):,.4f}, VAH=${vp.get('vah', 0):,.4f}, VAL=${vp.get('val', 0):,.4f}\n"
                            hist_klines_text += f"      Position: {vp.get('current_position', 'N/A')}, Distance from POC: {vp.get('distance_from_poc_pct', 0):+.2f}%\n"
                        
                        fvg = inst.get('fair_value_gaps', {})
                        if fvg:
                            hist_klines_text += f"    • Fair Value Gaps: {fvg.get('total_bullish_gaps', 0)} bullish, {fvg.get('total_bearish_gaps', 0)} bearish\n"
                            hist_klines_text += f"      Unfilled: {fvg.get('unfilled_bullish_count', 0)} bullish, {fvg.get('unfilled_bearish_count', 0)} bearish\n"
                            hist_klines_text += f"      Gap Density: {fvg.get('gap_density_pct', 0):.2f}%\n"
                        
                        ob = inst.get('order_blocks', {})
                        if ob:
                            hist_klines_text += f"    • Order Blocks: {ob.get('total_bullish_ob', 0)} bullish, {ob.get('total_bearish_ob', 0)} bearish\n"
                            hist_klines_text += f"      Active: {ob.get('active_bullish_count', 0)} bullish, {ob.get('active_bearish_count', 0)} bearish\n"
                            hist_klines_text += f"      OB Density: {ob.get('ob_density_pct', 0):.2f}%\n"
                        
                        smc = inst.get('smart_money', {})
                        if smc:
                            hist_klines_text += f"    • Smart Money Concepts: Structure Bias={smc.get('structure_bias', 'N/A')} ({smc.get('bullish_bias_pct', 0):.1f}% bullish)\n"
                            hist_klines_text += f"      BOS: {smc.get('bos_bullish', 0)} bullish / {smc.get('bos_bearish', 0)} bearish\n"
                            hist_klines_text += f"      CHoCH: {smc.get('choch_bullish', 0)} bullish / {smc.get('choch_bearish', 0)} bearish\n"
                        
                        hist_klines_text += "\n"

            
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
                    # Add institutional indicators for 1D
                    inst = d1.get('institutional_indicators', {})
                    if inst:
                        hist_klines_text += "  🏛️ Institutional Indicators (1D - 90 ngày):\n"
                        
                        vp = inst.get('volume_profile', {})
                        if vp:
                            hist_klines_text += f"    • Volume Profile: POC=${vp.get('poc', 0):,.4f}, VAH=${vp.get('vah', 0):,.4f}, VAL=${vp.get('val', 0):,.4f}\n"
                            hist_klines_text += f"      Position: {vp.get('current_position', 'N/A')}, Distance from POC: {vp.get('distance_from_poc_pct', 0):+.2f}%\n"
                        
                        fvg = inst.get('fair_value_gaps', {})
                        if fvg:
                            hist_klines_text += f"    • Fair Value Gaps: {fvg.get('total_bullish_gaps', 0)} bullish, {fvg.get('total_bearish_gaps', 0)} bearish\n"
                            hist_klines_text += f"      Unfilled: {fvg.get('unfilled_bullish_count', 0)} bullish, {fvg.get('unfilled_bearish_count', 0)} bearish\n"
                            hist_klines_text += f"      Gap Density: {fvg.get('gap_density_pct', 0):.2f}%\n"
                        
                        ob = inst.get('order_blocks', {})
                        if ob:
                            hist_klines_text += f"    • Order Blocks: {ob.get('total_bullish_ob', 0)} bullish, {ob.get('total_bearish_ob', 0)} bearish\n"
                            hist_klines_text += f"      Active: {ob.get('active_bullish_count', 0)} bullish, {ob.get('active_bearish_count', 0)} bearish\n"
                            hist_klines_text += f"      OB Density: {ob.get('ob_density_pct', 0):.2f}%\n"
                        
                        smc = inst.get('smart_money', {})
                        if smc:
                            hist_klines_text += f"    • Smart Money Concepts: Structure Bias={smc.get('structure_bias', 'N/A')} ({smc.get('bullish_bias_pct', 0):.1f}% bullish)\n"
                            hist_klines_text += f"      BOS: {smc.get('bos_bullish', 0)} bullish / {smc.get('bos_bearish', 0)} bearish\n"
                            hist_klines_text += f"      CHoCH: {smc.get('choch_bullish', 0)} bullish / {smc.get('choch_bearish', 0)} bearish\n"
                            hist_klines_text += f"      Swing Highs/Lows: {smc.get('swing_highs_count', 0)} / {smc.get('swing_lows_count', 0)}\n"
                        
                        hist_klines_text += "\n"

            
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

6. INSTITUTIONAL INDICATORS (HISTORICAL):
   - Volume Profile Position: 
     * PREMIUM (>VAH): Giá cao, có thể điều chỉnh xuống POC
     * VALUE_AREA: Giá fair, cân bằng
     * DISCOUNT (<VAL): Giá rẻ, có thể bật lên POC
   - Fair Value Gaps:
     * Unfilled gaps = magnets (giá có xu hướng fill gaps)
     * High gap density (>10%) = nhiều vùng trống, biến động mạnh
     * Nearest unfilled gap = S/R tiềm năng
   - Order Blocks:
     * Active OB = vùng institutional footprint, S/R mạnh
     * High OB density (>5%) = smart money tích cực
     * Strongest OB (strength >5) = vùng quan trọng
   - Smart Money Concepts:
     * Structure Bias: BULLISH/BEARISH/NEUTRAL
     * BOS (Break of Structure) = continuation signal
     * CHoCH (Change of Character) = reversal signal
     * High swing count = nhiều cấu trúc, trending market

SỬ DỤNG DỮ LIỆU NÀY ĐỂ:
- Xác định vùng giá quan trọng (support/resistance lịch sử)
- Đánh giá độ mạnh của trend hiện tại
- So sánh volume hiện tại với lịch sử
- Nhận biết pattern đảo chiều sớm
- Tính toán risk/reward dựa trên range lịch sử
- Phát hiện institutional accumulation/distribution zones
- Dự đoán price targets dựa trên POC và gaps
- Xác định trend consistency qua SMC structure
"""
        
        # Format institutional indicators as JSON
        institutional_json = self._format_institutional_indicators_json(data, market)
        
        # === NEW v2.2: ASSET TYPE DETECTION ===
        asset_type = self._detect_asset_type(symbol)
        
        # === NEW v2.2: DYNAMIC RISK MULTIPLIERS BY ASSET TYPE ===
        risk_multiplier = {
            'BTC': 1.0,
            'ETH': 1.2,
            'LARGE_CAP_ALT': 1.5,
            'MID_CAP_ALT': 2.0,
            'SMALL_CAP_ALT': 2.5,
            'MEME_COIN': 3.0
        }.get(asset_type, 2.0)
        
        position_sizing_guide = {
            'BTC': '3-5% of portfolio',
            'ETH': '2-3% of portfolio',
            'LARGE_CAP_ALT': '1.5-2% of portfolio',
            'MID_CAP_ALT': '1-1.5% of portfolio',
            'SMALL_CAP_ALT': '0.5-1% of portfolio',
            'MEME_COIN': '0.05-0.1% of portfolio'
        }.get(asset_type, '1% of portfolio')
        
        # Build full prompt with v2.2 enhancements
        prompt = f"""You are an expert cryptocurrency trading analyst with 10+ years of experience in technical analysis and market psychology.

═══════════════════════════════════════════════════════════════════════════════
🎯 SECTION 0: ASSET TYPE DETECTION & ANALYSIS FOCUS (v2.2)
═══════════════════════════════════════════════════════════════════════════════

DETECTED ASSET TYPE: {asset_type}

Asset Classification (v2.2):
- BTC: Bitcoin - Macro-driven, institutional flows, dominance critical
- ETH: Ethereum - Smart contract ecosystem, institutional interest
- LARGE_CAP_ALT (>$10B): Lower risk, stronger fundamentals, institutional access
- MID_CAP_ALT ($1B-$10B): Moderate risk, sector potential, growth opportunity
- SMALL_CAP_ALT ($100M-$1B): High risk, high reward, technical analysis critical
- MEME_COIN (<$100M): Extreme risk, community-driven, sentiment matters most

ANALYSIS APPROACH FOR {asset_type}:
- Risk Multiplier: {risk_multiplier}x (higher = more cautious)
- Recommended Position Size: {position_sizing_guide}
- Stop Loss Width: {"5-10% BTC dominance-aware" if asset_type == "BTC" else "Wider stops due to correlation risk" if asset_type != "BTC" else "Standard"}
- Confidence Adjustment: {"Base on macro factors heavily" if asset_type == "BTC" else "Base on BTC correlation" if asset_type in ["ETH", "LARGE_CAP_ALT"] else "Base on sector momentum"}

CRITICAL FOR {asset_type}:
"""
        
        # Add asset-specific critical factors
        if asset_type == 'BTC':
            prompt += """1. BTC MACRO FACTORS (Weight: 40% of analysis):
   - BTC dominance (trend, support/resistance levels, institutional thesis)
   - ETF flows (>$500M daily = strong institutional signal)
   - Whale accumulation/distribution (large transaction analysis)
   - Miner pressure (difficulty adjustments, outflows from mining pools)
   - Macro correlations (DXY, S&P500, Gold, Treasury yields)
   - Fed policy and macro sentiment shifts
   ONLY BTC can have dominance-driven analysis. Use this heavily for conviction.

2. CONFLUENCE RULES FOR BTC:
   - STRONG BUY: Price at support + Dominance rising + Positive macro + Institutional inflow
   - WEAK BUY: Technical confluence alone without macro support = reduce confidence 30%
   - SELL: Breaking macro support levels (dominance break, whale exit, macro headwind)
   - WAIT: Macro uncertainty or dominance consolidation (sideways 50-60%)

"""
        elif asset_type in ['ETH', 'LARGE_CAP_ALT', 'MID_CAP_ALT']:
            prompt += f"""1. ALTCOIN CORRELATION ANALYSIS (Weight: 35% of analysis):
   - BTC correlation strength: How closely {symbol} follows BTC (0-100%)
   - ETH correlation: Alternative smart contract ecosystem dependency
   - Independent move probability: Can this move against BTC? (low on alts)
   - Sector momentum: {asset_type} sector performance vs overall market
   - Sector rotation risk: Moving from one sector to another?
   - Project health score: Tokenomics, development, adoption
   - Liquidity assessment: Can you enter/exit without slippage?
   ALTCOINS HIGHLY DEPENDENT ON BTC - Use correlation heavily for conviction.

2. CONFLUENCE RULES FOR {asset_type}:
   - STRONG BUY: Technical setup + BTC positive + Sector leadership + Health good
   - WEAK BUY: Technical alone without BTC support = reduce confidence 40%
   - SELL: BTC weakness OR sector rotation OR health degradation
   - WAIT: High BTC correlation + uncertain macro (price will follow BTC down)

"""
        else:
            prompt += f"""1. SMALL CAP/MEME ANALYSIS (Weight: 30% of technical):
   - Community sentiment and social metrics
   - Chart technicals and momentum
   - Volatility and pump-and-dump risk assessment
   - Liquidity and slippage concerns
   - Project fundamentals (if any) or pure sentiment play
   SMALL CAPS ARE HIGHLY RISKY - Only trade with tight stops and small position sizes.

2. CONFLUENCE RULES FOR {asset_type}:
   - STRONG BUY: Perfect technical + Extreme momentum + Good liquidity
   - WEAK BUY: Technical alone = apply 50% confidence penalty
   - SELL: Loss of momentum or liquidity drying up
   - WAIT: Whenever uncertain (risk/reward not favorable)

"""
        
        prompt += f"""
TRADING STYLE: {trading_style.upper()}
- If scalping: Focus on 1m-5m-15m timeframes, quick entries/exits, tight stop losses
- If swing: Focus on 1h-4h-1D timeframes, position holding 2-7 days, wider stop losses

{historical_context}

ANALYZE THIS CRYPTOCURRENCY:

SYMBOL: {symbol}
DETECTED TYPE: {asset_type}
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

═══════════════════════════════════════════════════════════════════════════════
🔄 SECTION 0.5: MULTI-SOURCE ON-CHAIN DATA INTEGRATION (v3.3 - REAL-TIME)
═══════════════════════════════════════════════════════════════════════════════

**IMPORTANT FOR AI:** You have web browsing capability. Fetch real-time on-chain data from these public URLs:

**Glassnode Institutional Flows:** https://studio.glassnode.com/metrics
- Browse for Exchange Flow Multiple, Long-Term Holder Supply, Miner Reserve
- Example: Rising miner reserves = capitulation bottom signal
- Integration: Cross-verify with Arkham whale flows for BTC direction

**CoinGlass Derivatives Data:** https://www.coinglass.com/
- Browse perpetual funding rates, liquidation heatmaps, open interest
- Example: BTC Funding Rate >0.1% = contrarian short opportunity
- Integration: Combine with DeFiLlama TVL for hedging signals

**DeFiLlama TVL & Liquidity:** https://defillama.com/
- Browse TVL across chains, protocol revenue, yield trends
- Example: Ethereum TVL $50B+, Solana yield spikes indicate sector rotation
- Integration: Monitor cross-chain bridges for liquidity shifts

**Arkham Entity Explorer:** https://platform.arkhamintelligence.com/explorer
- Track institutional wallet flows and entity clustering
- Example: Binance Hot Wallet >10k ETH transfers signal exchange inflows
- Integration: High concentration (>30% top 10) increases dump risk

**Token Terminal Protocol Revenue:** https://tokenterminal.com/terminal
- Browse protocol revenue, P/S ratios, valuation multiples
- Example: Uniswap P/S <5x with rising revenue = long opportunity
- Integration: Compare with Messari tokenomics for valuation models

**Nansen Smart Money Analysis:** https://www.nansen.ai/research
- Follow smart money wallets and DEX trader performance
- Example: Smart DEX traders with >90% win rate = follow their entries
- Integration: Highest weight for entry confirmation signals

**Messari Research & Tokenomics:** https://messari.io/research
- Read free research reports on fundamentals and market structure
- Example: DePIN protocol incentive burns indicate utility strength
- Integration: Combine with DeFiLlama TVL for sector rotation alpha

**DATA INTEGRATION PRIORITIES:**
1. Cross-verify signals across MINIMUM 3 independent on-chain sources
2. Weight institutional sources 40% higher (Glassnode, Arkham, Token Terminal)
3. Prioritize real-time DEX data over CEX for altcoins (less manipulation)
4. Use Glassnode flows as PRIMARY BTC direction indicator
5. Apply mean-variance optimization to correlation analysis
6. Factor time decay: older signals weighted 30% lower than current

═══════════════════════════════════════════════════════════════════════════════
🧭 SECTION 1.5: INSTITUTIONAL FUND TRADING TACTICS (v3.3)
═══════════════════════════════════════════════════════════════════════════════

**ASSET ALLOCATION STRATEGY (Risk Parity Model):**
- Macro Regime Detection: Fed policy + BTC dominance + institutional flows + volatility
- Risk Parity Allocation: Position sizing based on volatility-adjusted correlations
- Cross-DEX Liquidity Mining: Capture alpha from concentrated liquidity in high-fee tiers
- Derivatives Hedging: Use CoinGlass funding rates to delta-neutral hedge spot exposure
- Yield Curve Arbitrage: Exploit basis differences between spot/futures/perpetuals

**ENTRY/EXIT METHODOLOGY (Smart Money Framework):**
- Track >$10M institutional orders via Arkham for confirmation
- Follow labeled smart money wallets with >90% win rate history (Nansen)
- Enter when price approaches high-liquidity DEX zones (Volume Profile analysis)
- Use CoinGlass funding extremes (>±$0.1%) for contrarian signals
- Use Glassnode miner capitulation for BTC bottom fishing

**RISK MANAGEMENT (Fund Grade Standards):**
- Max Drawdown: 2% per trade, 8% per portfolio
- Correlation Risk: Reduce position 30% when BTC correlation >85%
- Liquidity Risk: Avoid positions >10% of daily DEX volume
- Black Swan Protection: Maintain 5% stablecoin buffer during high volatility
- Stress Test: Simulate -30% scenarios before entry
- Kelly Criterion: Position Size = (win_prob × win_loss_ratio - loss_prob) / win_loss_ratio

**PORTFOLIO CONSTRUCTION (Institutional Framework):**
- Core Holdings (60%): BTC + ETH with custody and yield
- Satellite (25%): High-conviction alts with fundamentals
- Alpha Generation (10%): Active trading from technical + on-chain signals
- Risk Mitigation (5%): Options protection, stablecoin yield, cash

**PERFORMANCE TARGETS:**
- Sharpe Ratio: >1.5 (risk-adjusted returns)
- Win Rate: ≥65% for systematic strategies
- Profit Factor: >2.0 (gross profits / gross losses)
- Max Drawdown: <25% annually
- Calmar Ratio: >1.0 (annual return / max drawdown)

═══════════════════════════════════════════════════════════════════════════════
😨 SECTION 1.6: MULTI-SOURCE SENTIMENT & MEDIA DATA INTEGRATION (v3.3 - REAL-TIME)
═══════════════════════════════════════════════════════════════════════════════

**IMPORTANT FOR AI:** Fetch real-time sentiment from these public URLs:

**Social Media Sentiment (Browse & Analyze):**
- X/Twitter: https://x.com/ - Search "{symbol} price" or "{symbol} news" for FOMO detection
- Telegram: https://web.telegram.org/ - Monitor {symbol} channels for retail panic
- Reddit: https://www.reddit.com/ - Check r/cryptocurrency and {symbol}-specific subreddits
- TradingView Ideas: https://www.tradingview.com/ - Check if >70% votes bullish

**News Platforms (Latest Headlines):**
- CoinDesk: https://www.coindesk.com/ - Institutional buy-in signals (ETF approvals)
- Cointelegraph: https://cointelegraph.com/ - Regulatory and project news
- Bloomberg Crypto: https://www.bloomberg.com/crypto - Macro and institution interest
- Reuters Markets: https://www.reuters.com/markets/cryptocurrencies/ - Official announcements
- Yahoo Finance Crypto: https://finance.yahoo.com/cryptocurrencies/ - Sentiment shifts

**Search Trends (Retail Interest Indicator):**
- Google Trends: https://trends.google.com/ - Search "{symbol}" for trend spikes
- CryptoCompare: https://www.cryptocompare.com/ - Search volume vs price correlation
- >200% WoW spike = Retail entry phase (caution for dump)

**Economic Calendar & Macro Events:**
- ForexFactory: https://www.forexfactory.com/calendar - Fed decisions (HIGH impact = volatility)
- Investing.com: https://www.investing.com/economic-calendar/ - Macro events impact
- Correlate Fed rate decisions with BTC direction

**Whale & Liquidation Alerts:**
- Whale Alert Twitter: https://x.com/whale_alert - ">10,000 BTC to exchange" signals
- CoinGlass Heatmap: https://www.coinglass.com/ - Liquidation cascades predict volatility
- Large transfers = distribution risk (price likely down next)

**Options & Derivatives Sentiment:**
- Deribit Options: https://www.deribit.com/ - Put/call ratios (>1.5 = bearish)
- OKX Options: https://www.okx.com/ - Volatility skew analysis
- High puts = fear = contrarian buy setup

**Funding Rate Sentiment (Leverage Positions):**
- Binance Perpetuals: https://www.binance.com/ - Browse funding rates
- OKX Perpetuals: https://www.okx.com/ - Negative funding = squeeze potential
- Bybit Perpetuals: https://www.bybit.com/ - Longs overly leveraged = risk

**Fear & Greed Index (Market Sentiment Gauge):**
- Alternative.me: https://alternative.me/crypto/fear-and-greed-index/
- **CONTRARIAN SIGNAL:** Index 0-20 (Extreme Fear) = Buy opportunity
- Index 80-100 (Extreme Greed) = Sell/Take profits
- Current usage: If index is 11 (Extreme Fear), boost buy confidence by 15-20%

**Institutional Filings (Long-term Conviction):**
- SEC EDGAR: https://www.sec.gov/edgar.shtml - Search "Bitcoin ETF" or {symbol} ETF
- Form 13F filings = Quarterly institutional holdings changes
- ETF inflows >$500M = Strong institutional support

**SENTIMENT WEIGHTING FRAMEWORK:**
1. Institutional News (Bloomberg, Reuters): 35% weight - High reliability
2. Social Media (X/Telegram): 25% weight - Retail flow indicator
3. On-Chain Data (Glassnode, Arkham): 25% weight - Actual money movement
4. Fear & Greed Index: 10% weight - Market extremes for contrarian plays
5. Search Trends: 5% weight - Retail FOMO detection

**SENTIMENT INTEGRATION RULES:**
- If Fear & Greed <20 AND technical bullish = STRONG BUY (contrarian + technicals)
- If Fear & Greed >80 AND technical bearish = STRONG SELL (greed + technicals)
- If whale alert ">10k BTC to exchange" + price rallying = DISTRIBUTION RISK (lower confidence)
- If smart money wallet accumulating + price consolidating = STRONG BUY setup
- If news +ve but Fear & Greed extreme fear = EXTREME BULL move coming

═══════════════════════════════════════════
🎯 YOUR TASK (v3.3 ENHANCED)
═══════════════════════════════════════════

═══════════════════════════════════════════════════════════════════════════════
⚖️ SECTION 12: DYNAMIC RISK ADJUSTMENTS (v2.2)
═══════════════════════════════════════════════════════════════════════════════

FOR {asset_type} - Apply these risk multipliers to your analysis:

**Position Sizing Formula:**
Base Position = 2% of portfolio
Risk Multiplier = {risk_multiplier}x (asset type risk)
Liquidity Factor = 1.0 if volume > $10M, else 0.5-0.7x (reduce position if illiquid)
BTC Correlation Factor = 0.8-1.0x for alts (reduce if highly correlated to BTC weakness)

FINAL_POSITION = Base Position × (1/Risk_Multiplier) × Liquidity_Factor × Correlation_Factor
CAPPED AT: {position_sizing_guide}

**Asset Type Risk Profiles:**
- BTC (1.0x): 3-5% position, 5-10% stop, long-term conviction possible
- ETH (1.2x): 2-3% position, 8-12% stop, sector leadership matters
- LARGE_CAP_ALT (1.5x): 1.5-2% position, 10-15% stop, BTC correlation important
- MID_CAP_ALT (2.0x): 1-1.5% position, 12-18% stop, correlation risk high
- SMALL_CAP_ALT (2.5x): 0.5-1% position, 15-25% stop, tight technical stops critical
- MEME_COIN (3.0x): 0.05-0.1% position, 20-30% stop, use only with extreme caution

**Market Regime Adjustments:**
- ALTSEASON (alts outperforming BTC): Increase small cap position 20-30%
- BTC_DOMINANT (alts underperforming): Reduce small cap position 30-50%, increase BTC
- RISK_ON (high market confidence): Normal sizing
- RISK_OFF (uncertainty/fear): Reduce all positions 30-50%, increase stop widths 20-30%

**Critical Risk Rules:**
1. If volume < $10M: Reduce position by 50-70% (liquidity too low for exit)
2. If BTC correlation > 90% for altcoin: Add dependency warning (limited independent move)
3. If volatility is 2x normal: Widen stops by 20-30% (larger average swings)
4. If market regime uncertain: Increase confidence requirement from 65 to 75%
5. Use WAIT instead of HOLD if conditions unclear (preserve capital)

APPLY THESE RULES TO YOUR RECOMMENDATION AND ADJUST ENTRY/TP/SL ACCORDINGLY.

═══════════════════════════════════════════════════════════════════════════════
🎯 ENHANCED JSON FORMAT (v3.3 - REAL-TIME + SENTIMENT)
═══════════════════════════════════════════════════════════════════════════════

Provide a comprehensive trading analysis in JSON format with REAL-TIME timestamp:

{{
  "real_time_timestamp": "ISO 8601 timestamp when this analysis was generated (e.g., '2025-11-20T12:00:00Z')",
  "asset_type": "{asset_type}",
  "recommendation": "BUY" | "SELL" | "HOLD" | "WAIT",
  "confidence": 0-100,
  "trading_style": "{trading_style}",
  "entry_point": price in USD,
  "stop_loss": price in USD,
  "take_profit": [target1, target2, target3],
  "expected_holding_period": "X hours/days",
  "risk_level": "LOW" | "MEDIUM" | "HIGH",
  "reasoning_vietnamese": "Chi tiết phân tích bằng tiếng Việt (300-500 từ)",
  
  "sector_analysis": {{
    "sector": "{asset_type} sector name",
    "sector_momentum": "STRONG_UP" | "UP" | "NEUTRAL" | "DOWN" | "STRONG_DOWN",
    "rotation_risk": "None" | "Minor" | "Moderate" | "High",
    "sector_leadership": "This coin is leading sector" or "Lagging sector"
  }},
  
  "correlation_analysis": {{
    "btc_correlation": 0-100,
    "eth_correlation": 0-100,
    "independent_move_probability": 0-100
  }},
  
  "fundamental_analysis": {{
    "health_score": 0-100,
    "tokenomics": "Good" | "Fair" | "Poor",
    "centralization_risk": "Low" | "Medium" | "High",
    "ecosystem_strength": "Strong" | "Moderate" | "Weak"
  }},
  
  "position_sizing_recommendation": {{
    "position_size_percent": "X% of portfolio",
    "risk_per_trade": "X%",
    "recommended_leverage": "1x (no leverage)" | "2x" | "3x+",
    "liquidity_notes": "Good liquidity" | "Moderate" | "Low - reduce position"
  }},
  
  "macro_context": {{"""
        
        if asset_type == "BTC":
            prompt += """
    "btc_dominance": "RISING" | "FALLING" | "STABLE",
    "dominance_trend": "Bullish" | "Bearish" | "Neutral",
    "institutional_flows": "Inflows $XXM" | "Outflows $XXM" | "Neutral",
    "etf_status": "Strong inflows" | "Neutral" | "Outflows",
    "whale_activity": "Accumulation" | "Distribution" | "Neutral",
    "miner_pressure": "Selling pressure" | "Accumulating" | "Neutral",
    "macro_correlation": "Positive (DXY down, S&P up)" | "Neutral" | "Negative"
  }}"""
        else:
            prompt += """
    "sector_rotation_status": "Sector in favor" | "Rotating out" | "Out of favor",
    "btc_dependency": "High (follow BTC)" | "Moderate" | "Low (independent)",
    "project_catalysts": "Near-term catalyst details" | "None expected",
    "liquidity_assessment": "Good (easy entry/exit)" | "Moderate" | "Poor (wide spreads)",
    "market_cap_impact": "Supported by market cap" | "Fair value" | "Overvalued"
  }}"""
        
        prompt += f"""
  ,
  "key_points": ["Điểm chính 1 (bằng tiếng Việt)", "Điểm chính 2 (bằng tiếng Việt)", ...],
  "conflicting_signals": ["Tín hiệu mâu thuẫn 1 (tiếng Việt)", "Tín hiệu 2", ...] or [],
  "warnings": ["Cảnh báo 1 (tiếng Việt)", "Cảnh báo 2", ...] or [],
  "market_sentiment": "BULLISH" | "BEARISH" | "NEUTRAL",
  "technical_score": 0-100,
  "fundamental_score": 0-100,
  "historical_analysis": {{
    "h1_context": {{
      "rsi_interpretation": "RSI avg vs current, oversold/overbought zones",
      "volume_trend": "Increasing/Decreasing và ý nghĩa",
      "price_position": "Vị trí trong range và trend 7 ngày",
      "institutional_insights": "Phân tích Volume Profile, FVG, OB, SMC trên khung 1H (7 ngày)"
    }},
    "h4_context": {{
      "rsi_interpretation": "RSI context 30 ngày",
      "volume_trend": "Volume pattern analysis",
      "price_position": "Vị trí trong range và xu hướng",
      "institutional_insights": "Phân tích Volume Profile, FVG, OB, SMC trên khung 4H (30 ngày)"
    }},
    "d1_context": {{
      "rsi_mfi_correlation": "RSI & MFI alignment analysis",
      "long_term_trend": "Xu hướng 90 ngày và momentum",
      "volatility_assessment": "Đánh giá độ biến động",
      "institutional_insights": "Phân tích Volume Profile, FVG, OB, SMC trên khung 1D (90 ngày)"
    }}
  }},
  
  "historical_learning": {{
    "total_past_analyses": 0-100,
    "win_rate_percent": 0-100,
    "base_confidence": 0-100,
    "historical_adjustment": -20 to +15,
    "final_confidence_calculation": "Explain: base X + adjustment Y = final Z",
    "similar_past_analysis": {{
      "found": true | false,
      "analysis_number": "#X" or null,
      "analysis_date": "YYYY-MM-DD" or null,
      "similarity_factors": ["RSI range match", "MFI range match", "VP position match", ...] or [],
      "past_outcome": "WIN" | "LOSS" | "PENDING" | null,
      "past_profit_percent": -100 to +100 or null,
      "lessons_learned": "What went right/wrong in that analysis" or null,
      "adjustments_made": "How current recommendation differs based on past outcome" or null
    }},
    "pattern_match": {{
      "matches_winning_pattern": true | false,
      "matches_losing_pattern": true | false,
      "winning_pattern_details": "RSI X-Y, MFI A-B, VP position Z" or null,
      "losing_pattern_details": "RSI X-Y, MFI A-B, VP position Z" or null,
      "pattern_confidence_impact": "Increase/Decrease by X points" or "No impact"
    }},
    "entry_stop_learning": {{
      "past_sl_too_tight": true | false,
      "past_sl_too_wide": true | false,
      "past_tp_not_reached": true | false,
      "past_entry_too_early": true | false,
      "current_adjustments": "Specific changes made to entry/SL/TP based on past" or "No adjustments needed"
    }},
    "recommendation_rationale": "Brief explanation of how historical data influenced final recommendation (2-3 sentences)"
  }},
  
  "sentiment_analysis": {{
    "fear_greed_index": {{
      "current_value": 0-100,
      "current_status": "Extreme Fear" | "Fear" | "Neutral" | "Greed" | "Extreme Greed",
      "contrarian_signal": "Buy opportunity" | "Normal" | "Sell opportunity",
      "confidence_impact": "Increase confidence by X%" or "Decrease confidence by X%"
    }},
    "social_media_sentiment": {{
      "x_twitter_sentiment": "Very Positive" | "Positive" | "Neutral" | "Negative" | "Very Negative",
      "telegram_sentiment": "Very Positive" | "Positive" | "Neutral" | "Negative" | "Very Negative",
      "reddit_sentiment": "Very Positive" | "Positive" | "Neutral" | "Negative" | "Very Negative",
      "overall_social_score": 0-100,
      "retail_fomo_level": "Extreme" | "High" | "Moderate" | "Low" | "None"
    }},
    "news_sentiment": {{
      "latest_news_source": "CoinDesk" | "Cointelegraph" | "Bloomberg" | "Reuters" | "Other",
      "headline": "Latest significant headline",
      "sentiment": "Very Positive" | "Positive" | "Neutral" | "Negative" | "Very Negative",
      "institutional_impact": "Strong positive" | "Positive" | "Neutral" | "Negative" | "Strong negative",
      "news_relevance": "Direct to {symbol}" | "Sector impact" | "Market-wide impact"
    }},
    "whale_activity_sentiment": {{
      "recent_whale_alerts": "Large transfers to exchange" | "Accumulation" | "None significant",
      "distribution_risk": "High" | "Moderate" | "Low",
      "sentiment_impact": "Bearish" | "Neutral" | "Bullish"
    }},
    "economic_calendar_impact": {{
      "upcoming_event": "Fed rate decision" | "CPI release" | "Other macro event" | "None",
      "event_impact_level": "HIGH" | "MEDIUM" | "LOW",
      "expected_direction": "Bullish for crypto" | "Bearish for crypto" | "Neutral"
    }},
    "sentiment_divergence": {{
      "retail_vs_institutional": "Retail bullish, institutions bearish" | "Aligned" | "Retail bearish, institutions bullish",
      "divergence_strength": "Extreme" | "Significant" | "Moderate" | "None",
      "risk_implication": "High risk of reversal" | "Mixed signals" | "Aligned direction"
    }},
    "overall_sentiment_score": 0-100,
    "sentiment_summary": "One sentence summary of market sentiment for {symbol} (tiếng Việt)"
  }},
  
  "on_chain_analysis": {{
    "glassnode_flows": {{
      "exchange_flow_status": "Net inflows >$100M" | "Neutral flows" | "Net outflows >$100M",
      "interpretation": "Accumulation" | "Neutral" | "Distribution"
    }},
    "coinglass_derivatives": {{
      "funding_rate_status": "Positive >0.1%" | "Positive <0.1%" | "Neutral" | "Negative",
      "liquidation_risk": "High" | "Moderate" | "Low",
      "open_interest_trend": "Increasing" | "Stable" | "Decreasing"
    }},
    "defillama_tvl": {{
      "tvl_trend": "Increasing >10% MoM" | "Stable" | "Decreasing >10% MoM",
      "protocol_health": "Strong" | "Stable" | "Concerning",
      "cross_chain_flows": "Inflows" | "Neutral" | "Outflows"
    }}
  }},
  
  "data_sources": {{
    "real_time_data_timestamp": "ISO 8601 timestamp of data fetch",
    "on_chain_sources": [
      {{"url": "https://studio.glassnode.com/metrics", "fetched_at": "ISO timestamp", "data": "Exchange flows, LTH supply"}},
      {{"url": "https://www.coinglass.com/", "fetched_at": "ISO timestamp", "data": "Funding rates, liquidations"}},
      {{"url": "https://defillama.com/", "fetched_at": "ISO timestamp", "data": "TVL, cross-chain flows"}}
    ],
    "sentiment_sources": [
      {{"url": "https://alternative.me/crypto/fear-and-greed-index/", "fetched_at": "ISO timestamp", "value": "Current Fear & Greed value"}},
      {{"url": "https://x.com/whale_alert", "fetched_at": "ISO timestamp", "data": "Latest whale transfers"}},
      {{"url": "https://www.coindesk.com/", "fetched_at": "ISO timestamp", "headline": "Latest news"}}
    ],
    "fetched_metrics": [
      "BTC price from news: ~$91,500",
      "Fear & Greed Index: 11 (Extreme Fear)",
      "Glassnode flows: [specific data]",
      "Whale alerts: [specific transfers]"
    ]
  }}
}}

IMPORTANT GUIDELINES - EXPANDED (v3.3):

1. **REAL-TIME DATA REQUIREMENT:**
   - Must include real_time_timestamp in ISO 8601 format
   - Must include data_sources with fetched_at timestamps for each source
   - Verify data is current (within 24h) or note any delays
   - If unable to fetch current data, indicate "data age >24h" in warnings

2. **SENTIMENT ANALYSIS INTEGRATION (NEW - v3.3):**
   - Fill fear_greed_index with current value from https://alternative.me/crypto/fear-and-greed-index/
   - If Fear & Greed <20 (Extreme Fear): Apply +15 confidence boost for BUY signals
   - If Fear & Greed >80 (Extreme Greed): Apply -15 confidence reduction for SELL signals
   - Cross-verify sentiment divergence: Retail bullish but institutions selling = CAUTION
   - Whale alerts showing >$1B to exchange = distribution risk, reduce confidence

3. **ON-CHAIN DATA INTEGRATION (v3.3):**
   - Browse Glassnode for latest exchange flows (indicator of institutional direction)
   - Check CoinGlass funding rates: >0.1% = longs overly leveraged, contrarian short
   - Monitor DeFiLlama TVL changes: >10% MoM growth = sector strength
   - Weight on-chain data 25% in final confidence calculation

4. **ASSET TYPE ANALYSIS:**
   - {asset_type} requires specific focus areas (see Section 0)
   - Apply risk multiplier {risk_multiplier}x to position sizing

   - Adjust confidence penalties based on asset type (see Dynamic Risk Rules)
   - Include macro_context section in JSON (conditional on asset type)

2. **CRITICAL: ALL TEXT FIELDS MUST BE IN VIETNAMESE**
   - reasoning_vietnamese: MUST be 100% Vietnamese (300-500 words)
   - key_points: MUST be Vietnamese (e.g., "RSI quá bán cho thấy...", "Khối lượng giảm đáng kể...")
   - conflicting_signals: MUST be Vietnamese (e.g., "Tín hiệu RSI tăng nhưng MFI giảm...")
   - warnings: MUST be Vietnamese (e.g., "Cảnh báo: Khối lượng thấp...")
   - historical_analysis fields (rsi_interpretation, volume_trend, etc.): MUST be Vietnamese
   - historical_learning.recommendation_rationale: MUST be Vietnamese
   - DO NOT use English for any text content visible to users

3. **Analyze ALL technical indicators systematically:**
   - RSI+MFI consensus and individual timeframe signals
   - Stochastic+RSI momentum across timeframes
   - Volume patterns and 24h trading activity
   - Pump detection signals (if >=80%, consider high risk/reward)
   - Previous candle patterns on H4 and D1 (wick analysis, body size, bullish/bearish)
   - **HISTORICAL DATA ANALYSIS (CRITICAL):** Xem section "DỮ LIỆU LỊCH SỬ MỞ RỘNG" bên trên

4. **Historical Data Analysis (REQUIRED - Fill historical_analysis in JSON):**
   - **1H Context (7 days):** Compare current RSI vs average, volume trend, price position
   - **4H Context (30 days):** RSI context, volume pattern, price positioning
   - **1D Context (90 days):** RSI & MFI correlation, long-term trend, volatility

5. **Historical Learning Analysis (NEW - REQUIRED - Fill historical_learning in JSON):**
   - **MANDATORY FIELD** - Must be included in every response with all sub-fields filled
   - Based on PREVIOUS ANALYSES DETAILS section above (Analysis #1, #2, #3, etc.):
     * total_past_analyses: Count from statistics
     * win_rate_percent: From statistics section
     * base_confidence: Initial confidence before historical adjustment
     * historical_adjustment: Calculate (-20 to +15) based on win rate + similar analysis + patterns
     * final_confidence_calculation: Show clear math, e.g., "Base 68 + WinRate +12 + Similar +5 = 85"
   - **similar_past_analysis**:
     * Search Analysis #1, #2, #3, etc. for similar RSI/MFI/VP conditions
     * If found: Set found=true, fill analysis_number, date, outcome, profit_percent
     * similarity_factors: ["RSI both 30-35", "MFI both 25-30", "Both DISCOUNT"]
     * lessons_learned: What worked/failed in that past analysis
     * adjustments_made: "Widened SL 2%→3% based on Analysis #3 getting stopped"
   - **pattern_match**:
     * matches_winning_pattern: true if current RSI/MFI/VP matches WINNING PATTERNS stats
     * matches_losing_pattern: true if matches LOSING PATTERNS stats
     * Fill winning_pattern_details or losing_pattern_details
     * pattern_confidence_impact: "Increase by 12 points" or "Decrease by 15 points"
   - **entry_stop_learning**:
     * Review past analyses' SL/TP outcomes
     * Mark true if past had issues (SL too tight, TP not reached, etc.)
     * current_adjustments: "SL 2.5%→3.2% based on Analysis #2 stopped out too early"
   - **recommendation_rationale**: 
     * 2-3 sentences: HOW historical data influenced final recommendation
     * MUST reference specific Analysis numbers if similar found
     * Example: "Win rate 75% for this setup. Similar to Analysis #2 (WIN +5.3%), boosted confidence 68→85"

6. **Candle Pattern Analysis (CRITICAL):**
   - D1/H4 previous candles show institutional behavior
   - Large wicks indicate rejection or absorption zones
   - Bullish candles with small upper wicks = continuation potential

7. **Dynamic Risk Application (CRITICAL - v2.2):**
   - Calculate position size using formula above
   - Apply liquidity penalties if volume < $10M
   - Apply correlation penalties for altcoins dependent on BTC
   - Adjust confidence if market regime is uncertain
   - Use WAIT if risk/reward not favorable

7. **CONJUNCTION RULES (Based on Asset Type):**
   - For BTC: Confluence requires macro + technical (both critical)
   - For ETH/LARGE_CAPS: Confluence requires BTC alignment + technical (both important)
   - For SMALL_CAPS/MEMES: Confluence requires strong technicals + liquidity + low BTC risk

8. **Institutional Indicators (CRITICAL - Weight 40% - JSON FORMAT ABOVE):**
   
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

═══════════════════════════════════════════════════════════════════════════════
🧠 SECTION 13: HISTORICAL LEARNING & ADAPTIVE ANALYSIS (v2.2) - CRITICAL!
═══════════════════════════════════════════════════════════════════════════════

{historical_context}

**🔥 MANDATORY INSTRUCTIONS - YOU MUST USE HISTORICAL DATA TO IMPROVE ANALYSIS:**

1. **Read Previous Analyses (NEW - CRITICAL):**
   - Section "PREVIOUS ANALYSES DETAILS" above shows actual past recommendations
   - Each analysis shows: Recommendation, Entry/SL/TP, Reasoning, and Outcome (WIN/LOSS/PENDING)
   - Compare CURRENT market conditions with each past analysis:
     * If current setup is similar to a WIN → Reference it: "Setup tương tự Analysis #2 đã thắng +5.3%"
     * If current setup is similar to a LOSS → Warn: "⚠️ Cảnh báo: Điều kiện giống Analysis #4 đã thua -3.2%"
   - Learn from reasoning: If past reasoning was wrong, explain what was missed
   - Improve entry/SL/TP: If past levels were hit too early/late, adjust current recommendations

2. **Win Rate-Based Confidence Adjustment:**
   - If historical win rate > 60% for THIS specific setup → Increase confidence by +10 to +15 points
   - If historical win rate < 40% for THIS specific setup → DECREASE confidence by -15 to -20 points OR use WAIT
   - Example: Current RSI=35, historical data shows RSI 30-40 has 70% win rate → BOOST confidence significantly

3. **Pattern Matching (CRITICAL):**
   - Compare CURRENT indicators with WINNING PATTERNS above:
     * Current RSI/MFI ranges vs historical winning RSI/MFI ranges
     * Current Volume Profile position (DISCOUNT/PREMIUM/VALUE_AREA) vs past wins
     * Current SMC bias vs historical successful biases
   - If setup MATCHES winning pattern:
     * MUST mention in reasoning: "✅ Setup khớp với pattern thắng lịch sử (Win Rate: X%)"
     * Use as STRONG confirmation → Increase confidence
   - If setup MATCHES losing pattern:
     * MUST mention: "⚠️ CẢNH BÁO: Setup khớp với pattern thua lịch sử (Loss Rate: X%)"
     * STRONGLY favor WAIT unless overriding factors exist

4. **RSI/MFI Learning Rules:**
   - Historical winning RSI ranges = Zones where AI made CORRECT predictions
   - If current RSI in losing range (e.g., past losses at RSI 60-70) → AVOID that signal
   - If current RSI in winning range (e.g., past wins at RSI 30-40) → FAVOR that signal
   - Same logic for MFI ranges

5. **Volume Profile Position Learning:**
   - Check if past WINS occurred at DISCOUNT, PREMIUM, or VALUE_AREA
   - If 70%+ of past wins were at DISCOUNT and current is DISCOUNT → Strong BUY confluence
   - If past losses concentrated at specific position → Avoid similar setups

6. **Entry/SL/TP Learning (NEW):**
   - Review previous analyses' entry/stop/target levels vs actual outcomes
   - If past SL was hit too early → Widen current SL by 0.5-1%
   - If past TP was not reached (price reversed before TP) → Lower current TP targets
   - If past entry was too early (price went lower first) → Wait for better entry
   - Example: "Analysis #3 had SL too tight at 2%, got stopped out before reversal. Using 3% SL now."

7. **AI Learning Recommendation Compliance:**
   - The "AI LEARNING RECOMMENDATION" text above provides SPECIFIC guidance
   - MUST follow these rules in your analysis
   - Example: If recommendation says "avoid RSI 60-70" and current RSI=65 → Lower confidence or WAIT

8. **Reasoning Integration (MANDATORY IN JSON):**
   - In "reasoning_vietnamese" field, you MUST explicitly reference historical data:
     * "Dựa trên phân tích 7 ngày qua, setup tương tự có tỷ lệ thắng X%..."
     * "RSI hiện tại [value] nằm trong vùng [range] đã thắng X lần/thua Y lần trong quá khứ..."
     * "Volume Profile ở [position] - vị trí này có lịch sử thắng/thua như thế nào..."
     * "Setup hiện tại giống Analysis #X (đã thắng/thua Y%), điều chỉnh SL/TP dựa trên bài học đó..."
   - **MUST also summarize historical_learning JSON findings in Vietnamese**
   - This proves you ACTUALLY analyzed historical context (not just ignored it)

9. **Historical Learning JSON Integration (CRITICAL):**
   - The "historical_learning" section in JSON MUST align with "reasoning_vietnamese" text
   - If you mention "Analysis #2" in reasoning → historical_learning.similar_past_analysis must show analysis_number="#2"
   - If you say confidence boosted → historical_learning.historical_adjustment must be positive
   - If you mention pattern match → historical_learning.pattern_match must show matches_winning_pattern=true
   - **CONSISTENCY CHECK**: Reasoning text + historical_learning JSON must tell same story
   - Example alignment:
     * Reasoning says: "Setup giống Analysis #2 thắng +5.3%, tăng confidence từ 68 lên 85"
     * JSON shows: similar_past_analysis.found=true, analysis_number="#2", past_profit_percent=5.3
     * JSON shows: base_confidence=68, final_confidence_calculation="68 + 12 + 5 = 85"

10. **Confidence Calculation Formula:**
   ```
   BASE_CONFIDENCE = Technical Analysis (0-100) + Fundamental Analysis (0-100) / 2
   
   HISTORICAL_ADJUSTMENT:
   - Win rate > 60%: +10 to +15
   - Win rate 40-60%: 0 (neutral)
   - Win rate < 40%: -15 to -20 (or force WAIT)
   - Similar to past WIN: +5 to +10
   - Similar to past LOSS: -10 to -15
   
   FINAL_CONFIDENCE = min(100, max(0, BASE_CONFIDENCE + HISTORICAL_ADJUSTMENT))
   ```
   - Example: BASE=70, Win rate=72%, Similar to Analysis #2 (WIN) → FINAL=70+12+8=90
   - Example: BASE=65, Win rate=30% → Force WAIT (too risky)

10. **WAIT Triggers Based on History:**
   - If win rate < 35% for similar setup → FORCE WAIT (preserve capital)
   - If losing pattern matches AND no strong overriding technicals → WAIT
   - If current setup very similar to recent LOSS → WAIT unless conditions clearly different
   - If only 1-2 historical analyses (insufficient data) → Note "limited historical context, be cautious"

═══════════════════════════════════════════════════════════════════════════════
🌍 SECTION 14: REAL-TIME DATA INTEGRATION (v3.3 - NEW)
═══════════════════════════════════════════════════════════════════════════════

**AI INSTRUCTION - MANDATORY DATA FETCHING:**

You MUST fetch real-time data from public URLs before finalizing your analysis:

1. **On-Chain Data (30% weight in final recommendation):**
   - Visit https://studio.glassnode.com/metrics for Glassnode exchange flows
   - Browse https://www.coinglass.com/ for funding rates and liquidations
   - Check https://defillama.com/ for TVL and cross-chain flows
   - Include fetched data in data_sources section with timestamps

2. **Sentiment Data (25% weight in final recommendation):**
   - Visit https://alternative.me/crypto/fear-and-greed-index/ for current Fear & Greed
   - Browse https://x.com/ for latest {symbol} sentiment (search "{symbol} news", "{symbol} bullish")
   - Check https://www.coindesk.com/ for latest institutional news
   - Visit https://x.com/whale_alert for recent large transfers

3. **Data Quality Requirements:**
   - All fetched data MUST have timestamps in ISO 8601 format (2025-11-20T12:00:00Z)
   - If data is >24h old, note this as "⚠️ Data age >24h" in warnings section
   - If unable to fetch current data, explicitly state this in analysis
   - Cross-verify multiple sources - require agreement from 2/3 sources for high confidence

4. **Timestamp Integration:**
   - real_time_timestamp field MUST be current (when you generate the analysis)
   - Each data_source entry MUST have fetched_at timestamp
   - Use exact timestamp when data was retrieved, not approximate time

5. **Data Sources Documentation:**
   - data_sources.on_chain_sources: List URLs and data fetched for each
   - data_sources.sentiment_sources: List URLs and data fetched for each
   - data_sources.fetched_metrics: Specific values like "BTC price ~$91,500", "Fear & Greed: 11"
   - This ensures full transparency and reproducibility

═══════════════════════════════════════════════════════════════════════════════
🔍 SECTION 15: SENTIMENT-ADJUSTED CONFIDENCE FORMULA (v3.3 - NEW)
═══════════════════════════════════════════════════════════════════════════════

**FINAL CONFIDENCE CALCULATION WITH REAL-TIME DATA:**

```
TECHNICAL_SCORE = (RSI analysis + MFI analysis + Volume profile + SMC bias + Pump signals) / 5

HISTORICAL_SCORE = Historical Adjustment (from past analyses and patterns)

SENTIMENT_SCORE = (Fear & Greed impact + News sentiment + Whale activity + On-chain flows) / 4

INSTITUTIONAL_WEIGHT = On-chain data quality and confirmation strength (0-100)

FINAL_CONFIDENCE = (
  TECHNICAL_SCORE × 0.40 +
  HISTORICAL_SCORE × 0.25 +
  SENTIMENT_SCORE × 0.20 +
  INSTITUTIONAL_WEIGHT × 0.15
)

APPLIED_ADJUSTMENTS:
1. If Fear & Greed < 20: +15 confidence for BUY (contrarian)
2. If Fear & Greed > 80: -15 confidence for SELL (greed risk)
3. If whale alerts show >$1B to exchange: -10 confidence (distribution risk)
4. If Glassnode flows positive >$500M: +8 confidence (institutional inflows)
5. If news extremely negative but technical bullish: -5 confidence (caution)
6. If sentiment divergence (retail bullish, institutions bearish): -10 confidence
```

**EXAMPLE CALCULATION:**
- Technical Score: 72 (good confluence)
- Historical Score: +10 (similar to past WIN, 68% win rate)
- Sentiment Score: 65 (Fear & Greed 15 = contrarian +15, news +5, flows positive)
- Institutional Weight: 75 (Glassnode confirmed inflow)

Final = (72 × 0.40) + (10 × 0.25) + (65 × 0.20) + (75 × 0.15)
     = 28.8 + 2.5 + 13.0 + 11.25
     = 55.55 → Round to 56 (medium-high confidence)

With adjustments: 56 + 15 (Fear & Greed extreme) = 71 final confidence

═══════════════════════════════════════════════════════════════════════════════
✅ FINAL CHECKLIST (v3.3 - BEFORE SUBMITTING)
═══════════════════════════════════════════════════════════════════════════════

**REQUIRED FOR EVERY RESPONSE:**

1. ✅ real_time_timestamp included (ISO 8601 format)
2. ✅ data_sources section with URLs and fetched_at timestamps
3. ✅ sentiment_analysis section filled with Fear & Greed, social, news, whale alerts
4. ✅ on_chain_analysis section with Glassnode, CoinGlass, DeFiLlama data
5. ✅ historical_learning section with all sub-fields filled
6. ✅ reasoning_vietnamese 100% in Vietnamese (300-500 words)
7. ✅ key_points, conflicting_signals, warnings all in Vietnamese
8. ✅ Entry/SL/TP specific and justified
9. ✅ Confidence calculation explained (technical + historical + sentiment)
10. ✅ Risk level appropriate for asset type
11. ✅ Position sizing within recommended ranges
12. ✅ No major internal contradictions (if reasoning says "bullish" but confidence <50, explain)
13. ✅ All numeric fields properly typed (not strings where integers expected)
14. ✅ JSON properly formatted and parseable

**IF ANY REQUIREMENT NOT MET:** 
- Do not submit incomplete analysis
- Re-check and complete all required sections
- Ensure data is current (fetch fresh if needed)
**📊 EXAMPLES OF CORRECT HISTORICAL INTEGRATION:**

✅ **EXCELLENT ANALYSIS WITH PREVIOUS ANALYSES REFERENCE:**
```json
{{
  "confidence": 85,
  "reasoning_vietnamese": "Phân tích kỹ thuật cơ bản cho confidence 68 điểm. 
Dựa trên dữ liệu lịch sử 7 ngày, setup tương tự (RSI 30-40, MFI 25-35, Volume Profile ở DISCOUNT) 
có tỷ lệ thắng 75% (9/12). RSI hiện tại 32 khớp với vùng này → +12 điểm.

Đặc biệt, điều kiện hiện tại rất giống Analysis #2 (ngày 10/11) với:
- RSI 31 vs 32 hiện tại
- MFI 28 vs 27 hiện tại  
- Volume Profile ở DISCOUNT (cùng vị trí)
- Entry $103,200 đã thắng +5.3%, hit TP2

Tuy nhiên, Analysis #2 có SL hơi rộng (3.5%), giá không test SL. 
Do đó sử dụng SL chặt hơn 2.8% để tối ưu risk/reward.

Final confidence: 68 + 12 (win rate) + 5 (similar to past win) = 85",
  
  "historical_learning": {{
    "total_past_analyses": 12,
    "win_rate_percent": 75,
    "base_confidence": 68,
    "historical_adjustment": 17,
    "final_confidence_calculation": "Base 68 + Win Rate 75% (+12) + Similar to Analysis #2 WIN (+5) = 85",
    "similar_past_analysis": {{
      "found": true,
      "analysis_number": "#2",
      "analysis_date": "2025-11-10",
      "similarity_factors": ["RSI 31 vs 32 current", "MFI 28 vs 27 current", "Both at DISCOUNT position", "Both BUY signals"],
      "past_outcome": "WIN",
      "past_profit_percent": 5.3,
      "lessons_learned": "Analysis #2 entry worked well, hit TP2. SL was 3.5% but never tested, could have been tighter.",
      "adjustments_made": "Tightened SL from 3.5% to 2.8% to improve risk/reward ratio while maintaining safety margin."
    }},
    "pattern_match": {{
      "matches_winning_pattern": true,
      "matches_losing_pattern": false,
      "winning_pattern_details": "RSI 30-40, MFI 25-35, DISCOUNT position - 75% win rate (9/12 trades)",
      "losing_pattern_details": null,
      "pattern_confidence_impact": "Increase by 12 points due to strong historical win rate"
    }},
    "entry_stop_learning": {{
      "past_sl_too_tight": false,
      "past_sl_too_wide": true,
      "past_tp_not_reached": false,
      "past_entry_too_early": false,
      "current_adjustments": "Tightened SL from historical 3.5% to 2.8% based on Analysis #2 not testing SL. TP targets kept similar as Analysis #2 hit TP2 successfully."
    }},
    "recommendation_rationale": "Historical win rate of 75% for this setup type combined with strong similarity to past winning Analysis #2 justifies high confidence. SL adjustment learned from past success improves risk/reward."
  }}
}}
```

✅ **EXCELLENT ANALYSIS WITH LOSS AVOIDANCE:**
```json
{{
  "recommendation": "WAIT",
  "confidence": 0,
  "reasoning_vietnamese": "Phân tích kỹ thuật cho BUY signal với base confidence 62.
Tuy nhiên, ⚠️ CẢNH BÁO: Setup hiện tại giống Analysis #4 (ngày 09/11) đã thua -3.8%:
- RSI 67 (Analysis #4: RSI 65) - Cùng vùng overbought
- MFI 72 (Analysis #4: MFI 70) - Quá cao
- Volume Profile ở PREMIUM (Analysis #4: PREMIUM) - Đã quá đắt
- Entry $105,000 đã bị rejected, hit SL

Dữ liệu lịch sử cho thấy RSI 60-70 + PREMIUM position có win rate chỉ 30% (3/10).
Khuyến nghị WAIT cho đến khi giá về DISCOUNT hoặc RSI xuống dưới 50.",
  
  "historical_learning": {{
    "total_past_analyses": 10,
    "win_rate_percent": 30,
    "base_confidence": 62,
    "historical_adjustment": -20,
    "final_confidence_calculation": "Base 62 - Win Rate 30% (-18) - Similar to Analysis #4 LOSS (-2) = 42 → FORCED WAIT",
    "similar_past_analysis": {{
      "found": true,
      "analysis_number": "#4",
      "analysis_date": "2025-11-09",
      "similarity_factors": ["RSI 65 vs 67 current (both overbought)", "MFI 70 vs 72 current (both high)", "Both at PREMIUM position", "Both BUY attempts at resistance"],
      "past_outcome": "LOSS",
      "past_profit_percent": -3.8,
      "lessons_learned": "Analysis #4 tried to buy at PREMIUM with overbought indicators. Price rejected and hit SL. Buying at PREMIUM with RSI>60 has proven risky.",
      "adjustments_made": "Changed recommendation from BUY to WAIT. Will only consider BUY when price returns to DISCOUNT or RSI drops below 50."
    }},
    "pattern_match": {{
      "matches_winning_pattern": false,
      "matches_losing_pattern": true,
      "winning_pattern_details": null,
      "losing_pattern_details": "RSI 60-70, MFI 65-75, PREMIUM position - 30% win rate (3/10 trades, 7 losses)",
      "pattern_confidence_impact": "Decrease by 18 points due to poor historical performance in this setup"
    }},
    "entry_stop_learning": {{
      "past_sl_too_tight": false,
      "past_sl_too_wide": false,
      "past_tp_not_reached": true,
      "past_entry_too_early": true,
      "current_adjustments": "Recommendation changed to WAIT instead of attempting early entry. Will wait for better conditions (DISCOUNT or lower RSI) before considering entry."
    }},
    "recommendation_rationale": "Strong similarity to past losing Analysis #4 combined with 30% win rate for this pattern type makes this trade too risky. Preserving capital by waiting for better setup."
  }}
}}
```

❌ **BAD ANALYSIS (DO NOT DO THIS):**
```json
{{
  "confidence": 65,
  "reasoning_vietnamese": "RSI quá bán, MFI thấp, có thể sẽ tăng.",
  "historical_learning": {{}}
}}
```
→ Không mention historical data, historical_learning empty = AI không học được gì!

**⚠️ CRITICAL REMINDERS:**
- PREVIOUS ANALYSES DETAILS section shows ACTUAL past recommendations - READ AND USE THEM
- Historical data is NOT optional - it MUST influence your final recommendation
- If you see losing patterns, AVOID them (don't repeat mistakes)
- If you see winning patterns, FAVOR them (capitalize on what works)
- Always explain WHY historical data changed your confidence score
- Learning from past = Better future predictions = Higher user trust

11. **Scoring methodology (UPDATED):**
    - Technical score = RSI+MFI (15%) + Stoch+RSI (15%) + Volume (10%) + Candles (10%) + Volume Profile (15%) + FVG (10%) + OB (10%) + S/R (10%) + SMC (15%)
    - Fundamental score = volume strength (40%), liquidity (30%), market sentiment (30%)
12. **Entry/Exit Recommendations:**
    - Entry: Near VAL, bullish FVG, bullish OB, support zones
    - Stop Loss: Below nearest support (OB/S/R zone) with 1-2 ATR buffer
    - Take Profit: At VAH, bearish FVG, resistance zones, EQH levels
"""

        # === NEW: ADD PATTERN RECOGNITION CONTEXT ===
        pattern_context = data.get('pattern_context')
        if pattern_context:
            regime = pattern_context.get('market_regime', {})
            patterns = pattern_context.get('universal_patterns', [])
            recommendations = pattern_context.get('recommendations', [])
            
            prompt += f"""

═══════════════════════════════════════════
🌍 CROSS-SYMBOL PATTERN RECOGNITION
═══════════════════════════════════════════

🔮 <b>MARKET REGIME: {regime.get('regime', 'UNKNOWN')}</b>
  • Confidence: {regime.get('confidence', 0) * 100:.0f}%
  • EMA Trend: {regime.get('metrics', {}).get('ema_trend', 'N/A')}
  • Volatility: {regime.get('metrics', {}).get('volatility', 'N/A')}
  • Volume: {regime.get('metrics', {}).get('volume', 'N/A')}

🎯 <b>REGIME-BASED RECOMMENDATIONS:</b>
"""
            for rec in recommendations:
                prompt += f"  {rec}\n"
            
            if patterns:
                prompt += "\n📊 <b>UNIVERSAL PATTERNS (Work across multiple symbols):</b>\n"
                for i, pattern in enumerate(patterns[:5], 1):  # Top 5
                    prompt += f"""  {i}. {pattern['condition']}
     • Win Rate: {pattern['win_rate']}% ({pattern['sample_size']} trades)
     • Symbols: {', '.join(pattern['symbols'])}
"""
            else:
                prompt += "\n⚠️ No universal patterns detected yet (insufficient data)\n"
            
            prompt += """
⚠️ <b>CRITICAL: Adjust your analysis based on market regime:</b>
  - BULL market → Favor BUY signals, tighter stops, look for dips to buy
  - BEAR market → Favor SELL signals, avoid longs unless strong reversal
  - SIDEWAYS → Range trading, buy support / sell resistance
  - If universal patterns match current setup → Increase confidence
"""
        
        prompt += "\nReturn ONLY valid JSON, no markdown formatting.\n"
        
        # === INJECT ADVANCED DETECTION RESULTS (NEW!) ===
        if data.get('advanced_detection') and ADVANCED_DETECTOR_AVAILABLE:
            try:
                advanced_section = integrate_advanced_detection_to_prompt(data['advanced_detection'])
                prompt += "\n" + advanced_section
                logger.info("✅ Injected advanced detection results into prompt")
            except Exception as e:
                logger.error(f"Error injecting advanced detection: {e}")
        
        return prompt
    
    def analyze(self, symbol: str, pump_data: Optional[Dict] = None, 
                trading_style: str = 'swing', use_cache: bool = True,
                user_id: Optional[int] = None) -> Optional[Dict]:
        """
        Perform AI analysis using Gemini with historical learning
        
        Args:
            symbol: Trading symbol
            pump_data: Optional pump detector data
            trading_style: 'scalping' or 'swing'
            use_cache: Whether to use cached results
            user_id: User ID for saving analysis and historical lookup
            
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
            
            # === NEW: GET PATTERN RECOGNITION CONTEXT ===
            if self.db and user_id:
                try:
                    from pattern_recognition import get_pattern_context
                    pattern_context = get_pattern_context(self.db, self.binance, user_id, symbol)
                    data['pattern_context'] = pattern_context
                    logger.info(f"✅ Pattern context: {pattern_context['market_regime']['regime']} market")
                except Exception as e:
                    logger.warning(f"⚠️ Pattern recognition failed: {e}")
                    data['pattern_context'] = None
            
            # Build prompt with historical context and patterns
            prompt = self._build_prompt(data, trading_style, user_id)
            
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
                # STEP 1: Remove dangerous control characters (0x00-0x1F except tab, newline, carriage return)
                # Keep Unicode characters for Vietnamese text
                import re
                # Remove control chars except \t (09), \n (0A), \r (0D)
                response_text = re.sub(r'[\x00-\x08\x0B-\x0C\x0E-\x1F]', '', response_text)
                
                # STEP 2: Additional JSON cleaning (MORE AGGRESSIVE)
                # Fix trailing commas in arrays/objects
                response_text = re.sub(r',\s*}', '}', response_text)
                response_text = re.sub(r',\s*]', ']', response_text)
                
                # Fix missing commas between object properties (common Gemini error)
                # Pattern: "value"\n  "key" -> "value",\n  "key"
                response_text = re.sub(r'"\s*\n\s*"', '",\n  "', response_text)
                
                # Fix missing commas after numbers in arrays
                response_text = re.sub(r'(\d)\s*\n\s*(\d)', r'\1,\2', response_text)
                
                # Fix missing commas in arrays: 100.00 200.00 -> 100.00, 200.00
                response_text = re.sub(r'(\d+\.?\d*)\s+(\d+\.?\d*)', r'\1, \2', response_text)
                
                # STEP 3: Handle long reasoning_vietnamese WITHOUT truncating
                # Instead of truncating, escape special characters properly
                def escape_json_string(text):
                    """Properly escape string for JSON"""
                    # Escape backslashes first
                    text = text.replace('\\', '\\\\')
                    # Escape quotes
                    text = text.replace('"', '\\"')
                    # Escape newlines (keep them as \n)
                    text = text.replace('\n', '\\n')
                    text = text.replace('\r', '\\r')
                    text = text.replace('\t', '\\t')
                    return text
                
                # Find and properly escape reasoning_vietnamese
                reasoning_match = re.search(r'"reasoning_vietnamese"\s*:\s*"(.*?)(?:"\s*[,}])', response_text, re.DOTALL)
                if reasoning_match:
                    reasoning_text = reasoning_match.group(1)
                    # Check if already escaped (contains \\n)
                    if '\\n' not in reasoning_text and '\n' in reasoning_text:
                        # Not escaped - needs escaping
                        escaped_reasoning = escape_json_string(reasoning_text)
                        # Replace in response_text
                        response_text = response_text.replace(
                            reasoning_match.group(0),
                            f'"reasoning_vietnamese": "{escaped_reasoning}",'
                        )
                        logger.info(f"✅ Escaped reasoning_vietnamese ({len(reasoning_text)} chars)")
                
                # Try to parse
                analysis = json.loads(response_text)
            except json.JSONDecodeError as json_err:
                logger.error(f"JSON parsing failed for {symbol}: {json_err}")
                logger.error(f"Response preview: {response_text[:500]}...")
                
                # Try to fix common JSON issues
                try:
                    # Strategy 1: Find matching braces and truncate after last complete object
                    brace_count = 0
                    last_valid_pos = -1
                    
                    for i, char in enumerate(response_text):
                        if char == '{':
                            brace_count += 1
                        elif char == '}':
                            brace_count -= 1
                            if brace_count == 0:
                                last_valid_pos = i + 1
                                break
                    
                    if last_valid_pos > 0:
                        fixed_json = response_text[:last_valid_pos]
                        analysis = json.loads(fixed_json)
                        logger.info(f"✅ Fixed JSON by truncating at position {last_valid_pos}")
                    else:
                        raise ValueError("Could not find complete JSON object")
                        
                except Exception as fix_err:
                    logger.warning(f"JSON auto-fix failed: {fix_err}")
                    
                    # Strategy 2: Extract minimal required fields manually
                    try:
                        import re
                        
                        # Extract required fields with regex
                        rec_match = re.search(r'"recommendation"\s*:\s*"([^"]+)"', response_text)
                        conf_match = re.search(r'"confidence"\s*:\s*(\d+)', response_text)
                        entry_match = re.search(r'"entry_point"\s*:\s*([\d.]+)', response_text)
                        sl_match = re.search(r'"stop_loss"\s*:\s*([\d.]+)', response_text)
                        tp_match = re.search(r'"take_profit"\s*:\s*\[([\d.,\s]+)\]', response_text)
                        period_match = re.search(r'"expected_holding_period"\s*:\s*"([^"]+)"', response_text)
                        risk_match = re.search(r'"risk_level"\s*:\s*"([^"]+)"', response_text)
                        # Extract full reasoning without truncating
                        reason_match = re.search(r'"reasoning_vietnamese"\s*:\s*"(.*?)(?:"\s*[,}])', response_text, re.DOTALL)
                        
                        if rec_match and conf_match:
                            # Get full reasoning text (don't truncate)
                            full_reasoning = reason_match.group(1) if reason_match else 'Không có phân tích chi tiết.'
                            # Clean but don't truncate
                            full_reasoning = full_reasoning.replace('\\n', '\n').replace('\\r', '\r').replace('\\"', '"')
                            
                            # Build minimal valid JSON
                            analysis = {
                                'recommendation': rec_match.group(1),
                                'confidence': int(conf_match.group(1)),
                                'trading_style': 'swing',
                                'entry_point': float(entry_match.group(1)) if entry_match else 0,
                                'stop_loss': float(sl_match.group(1)) if sl_match else 0,
                                'take_profit': [float(x.strip()) for x in tp_match.group(1).split(',')] if tp_match else [],
                                'expected_holding_period': period_match.group(1) if period_match else '3-7 days',
                                'risk_level': risk_match.group(1) if risk_match else 'MEDIUM',
                                'reasoning_vietnamese': full_reasoning  # Keep full text
                            }
                            logger.info(f"✅ Extracted partial JSON with regex for {symbol} (reasoning: {len(full_reasoning)} chars)")
                        else:
                            logger.error(f"❌ Cannot extract minimal required fields (recommendation, confidence)")
                            return None
                    except Exception as extract_err:
                        logger.error(f"❌ Regex extraction also failed: {extract_err}")
                        return None
            
            # Add metadata
            analysis['symbol'] = symbol
            analysis['analyzed_at'] = datetime.now().isoformat()
            
            # === NEW v2.2: Add default values for new fields if missing ===
            # Asset Type (auto-detected if not in response)
            if 'asset_type' not in analysis:
                analysis['asset_type'] = self._detect_asset_type(symbol)
            
            # Sector Analysis (8 new fields - v2.2)
            if 'sector_analysis' not in analysis:
                analysis['sector_analysis'] = {
                    'sector': 'Unknown',
                    'sector_momentum': 'NEUTRAL',
                    'rotation_risk': 'None',
                    'sector_leadership': 'Not available'
                }
            
            # Correlation Analysis (3 new fields - v2.2)
            if 'correlation_analysis' not in analysis:
                analysis['correlation_analysis'] = {
                    'btc_correlation': 0,
                    'eth_correlation': 0,
                    'independent_move_probability': 50
                }
            
            # Fundamental Analysis (4 new fields - v2.2)
            if 'fundamental_analysis' not in analysis:
                analysis['fundamental_analysis'] = {
                    'health_score': 50,
                    'tokenomics': 'Unknown',
                    'centralization_risk': 'Medium',
                    'ecosystem_strength': 'Moderate'
                }
            
            # Position Sizing Recommendation (4 new fields - v2.2)
            if 'position_sizing_recommendation' not in analysis:
                analysis['position_sizing_recommendation'] = {
                    'position_size_percent': '1-2% of portfolio',
                    'risk_per_trade': '1-2%',
                    'recommended_leverage': '1x (no leverage)',
                    'liquidity_notes': 'Check liquidity before trading'
                }
            
            # Macro Context (conditional - v2.2)
            if 'macro_context' not in analysis:
                analysis['macro_context'] = {}
            
            # Legacy fields for backward compatibility
            analysis['data_used'] = {
                'rsi_mfi_consensus': data['rsi_mfi'].get('consensus', 'N/A') if isinstance(data.get('rsi_mfi'), dict) else 'N/A',
                'stoch_rsi_consensus': data['stoch_rsi'].get('consensus', 'N/A') if isinstance(data.get('stoch_rsi'), dict) else 'N/A',
                'pump_score': pump_data.get('final_score', 0) if pump_data and isinstance(pump_data, dict) else 0,
                'current_price': data['market_data']['price']
            }
            
            # === NEW: SAVE TO DATABASE AND START TRACKING ===
            if self.db and user_id:
                try:
                    # Prepare market snapshot (current indicators)
                    # Convert all data to JSON-serializable format (no pandas Series/Timestamp)
                    def make_serializable(obj):
                        """Convert pandas Series/Timestamp and other non-serializable objects to JSON-safe format"""
                        # Handle pandas Timestamp
                        if hasattr(obj, 'isoformat'):
                            return obj.isoformat()
                        # Handle pandas Series/DataFrame - convert first, then serialize recursively
                        elif hasattr(obj, 'to_dict'):
                            result = obj.to_dict()
                            # Recursively serialize the result (may have Timestamp keys)
                            return make_serializable(result)
                        elif hasattr(obj, 'tolist'):
                            result = obj.tolist()
                            return make_serializable(result)
                        # Handle dict with potential Timestamp keys
                        elif isinstance(obj, dict):
                            return {
                                (k.isoformat() if hasattr(k, 'isoformat') else str(k) if not isinstance(k, (str, int, float, bool, type(None))) else k): 
                                make_serializable(v) 
                                for k, v in obj.items()
                            }
                        # Handle list/tuple
                        elif isinstance(obj, (list, tuple)):
                            return [make_serializable(item) for item in obj]
                        # Handle primitives
                        elif isinstance(obj, (int, float, str, bool, type(None))):
                            return obj
                        # Fallback: convert to string
                        else:
                            return str(obj)
                    
                    market_snapshot = {
                        'price': float(data['market_data']['price']),
                        'rsi_mfi': data.get('rsi_mfi', {}),
                        'stoch_rsi': data.get('stoch_rsi', {}),
                        'volume_profile': data.get('volume_profile', {}),
                        'order_blocks': data.get('order_blocks', {}),
                        'smart_money': data.get('smart_money', {}),
                        'timestamp': datetime.now().isoformat()
                    }
                    
                    # Convert entire market_snapshot (handles nested Timestamp keys)
                    market_snapshot = make_serializable(market_snapshot)
                    
                    # Get timeframe from trading style
                    timeframe = '5m' if trading_style == 'scalping' else '1h'
                    
                    # Save analysis to database (including WAIT recommendations)
                    analysis_id = self.db.save_analysis(
                        user_id=user_id,
                        symbol=symbol,
                        timeframe=timeframe,
                        ai_response=analysis,
                        market_snapshot=market_snapshot
                    )
                    
                    if analysis_id:
                        logger.info(f"✅ Saved analysis to database: {analysis_id}")
                        
                        # Check if analysis is dict before modifying
                        if isinstance(analysis, dict):
                            analysis['analysis_id'] = analysis_id
                            
                            # Start price tracking ONLY for BUY/SELL (not WAIT/HOLD)
                            recommendation = analysis.get('recommendation', '').upper()
                            if (self.tracker and 
                                recommendation in ['BUY', 'SELL'] and
                                analysis.get('entry_point') and 
                                analysis.get('stop_loss') and 
                                analysis.get('take_profit')):
                                
                                self.tracker.start_tracking(
                                    analysis_id=analysis_id,
                                    symbol=symbol,
                                    ai_response=analysis,
                                    entry_price=data['market_data']['price']
                                )
                                logger.info(f"✅ Started price tracking for {analysis_id}")
                            else:
                                logger.info(f"ℹ️ Analysis saved but not tracked (recommendation: {recommendation})")
                        else:
                            logger.warning(f"⚠️ Analysis is not dict (type: {type(analysis)}), cannot add analysis_id or start tracking")
                        
                        
                except Exception as db_error:
                    logger.error(f"❌ Failed to save analysis or start tracking: {db_error}", exc_info=True)
                    # Don't fail the whole analysis if DB save fails
            
            # Cache result
            self._update_cache(symbol, analysis)
            
            # Safe logging (check if analysis is dict)
            if isinstance(analysis, dict):
                logger.info(f"✅ Gemini analysis complete for {symbol}: {analysis.get('recommendation', 'N/A')} (confidence: {analysis.get('confidence', 0)}%)")
            else:
                logger.info(f"✅ Gemini analysis complete for {symbol} (type: {type(analysis)})")
            
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
        
        MESSAGE ORDER (v2.2):
        1. ENTRY/TP/SL SUMMARY - What to do (recommendation + prices) - FIRST for quick decision
        2. TECHNICAL DETAILS - Why to do it (analysis + indicators) - Context for decision
        3. AI REASONING - Deep analysis - Extended reading
        """
        def split_long_message(msg: str, max_length: int = 4000) -> list:
            """
            Split message into multiple parts if too long, keeping formatting intact
            
            Args:
                msg: Message to split
                max_length: Maximum length per message part
                
            Returns:
                List of message parts
            """
            if len(msg) <= max_length:
                return [msg]
            
            parts = []
            current_part = ""
            lines = msg.split('\n')
            
            for line in lines:
                # If adding this line would exceed limit, save current part and start new one
                if len(current_part) + len(line) + 1 > max_length:
                    if current_part:
                        parts.append(current_part.rstrip())
                        current_part = ""
                
                current_part += line + '\n'
            
            # Add last part
            if current_part:
                parts.append(current_part.rstrip())
            
            return parts
        
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
            
            # Message 1: ENTRY/TP/SL Summary (MOVED TO TOP)
            # This is the ACTION PLAN - Users see what Gemini recommends FIRST
            rec_emoji = "🟢" if rec == "BUY" else "🔴" if rec == "SELL" else "🟡" if rec == "HOLD" else "⚪"
            
            summary = "🤖 <b>GEMINI AI ANALYSIS v2.2</b>\n\n"
            summary += f"💎 <b>{symbol}</b> | 📊 {style.upper()}\n\n"
            summary += f"{rec_emoji} <b>KHUYẾN NGHỊ:</b> {rec}\n"
            summary += f"🎯 <b>Độ Tin Cậy:</b> {conf}%\n"
            summary += f"⚠️ <b>Mức Rủi Ro:</b> {risk}\n\n"
            
            # Only show trading plan if recommendation is actionable (BUY/SELL/HOLD)
            if rec in ["BUY", "SELL", "HOLD"] and entry > 0:
                summary += "💰 <b>KẾ HOẠCH GIAO DỊCH</b>\n"
                summary += f"📍 <b>Điểm Vào:</b> ${self.binance.format_price(symbol, entry)}\n"
                summary += f"🛑 <b>Cắt Lỗ:</b> ${self.binance.format_price(symbol, stop)}\n"
                summary += f"🎯 <b>Chốt Lời:</b>\n"
                for i, target in enumerate(targets, 1):
                    summary += f"   • TP{i}: ${self.binance.format_price(symbol, target)}\n"
                summary += f"⏱ <b>Thời Gian:</b> {period}\n\n"
            elif rec == "WAIT":
                summary += "⏸ <b>KHÔNG NÊN GIAO DỊCH</b>\n"
                summary += "📋 Tín hiệu chưa rõ ràng, cần chờ xác nhận\n"
                summary += "💡 Theo dõi thêm và đợi setup tốt hơn\n\n"
            
            summary += "<i>💡 Dữ liệu từ Gemini AI 2.0 Flash</i>"
            
            # Message 2: Technical Details
            tech = "📊 <b>PH&#194;N T&#205;CH K&#7926; THU&#7852;T CHI TI&#7870;T</b>\n\n"
            tech += f"💎 <b>{symbol}</b>\n\n"
            
            # Data used
            data_used = analysis.get('data_used', {})
            tech += "🔍 <b>Ch&#7881; B&#225;o S&#7917; D&#7909;ng:</b>\n"
            tech += f"• RSI+MFI: {data_used.get('rsi_mfi_consensus', 'N/A')}\n"
            tech += f"• Stoch+RSI: {data_used.get('stoch_rsi_consensus', 'N/A')}\n"
            
            pump_score = data_used.get('pump_score', 0)
            if pump_score >= 80:
                tech += f"• 🚀 Pump: {pump_score:.0f}% (Cao)\n"
            elif pump_score > 0:
                tech += f"• Pump: {pump_score:.0f}%\n"
            
            tech += f"• Gi&#225;: ${self.binance.format_price(symbol, data_used.get('current_price', 0))}\n\n"
            
            # === NEW v2.2: Add Asset Type Context ===
            asset_type = analysis.get('asset_type', 'UNKNOWN')
            tech += f"🎯 <b>Asset Type:</b> {asset_type}\n"
            
            # Helper function to encode Vietnamese characters to HTML entities
            def encode_vietnamese(text):
                """Encode Vietnamese characters to HTML entities to prevent Telegram parsing errors"""
                if not isinstance(text, str):
                    text = str(text)
                
                # Vietnamese character mapping to HTML entities
                vietnamese_map = {
                    # Lowercase
                    'à': '&#224;', 'á': '&#225;', 'ả': '&#7843;', 'ã': '&#227;', 'ạ': '&#7841;',
                    'ă': '&#259;', 'ằ': '&#7857;', 'ắ': '&#7855;', 'ẳ': '&#7859;', 'ẵ': '&#7861;', 'ặ': '&#7863;',
                    'â': '&#226;', 'ầ': '&#7847;', 'ấ': '&#7845;', 'ẩ': '&#7849;', 'ẫ': '&#7851;', 'ậ': '&#7853;',
                    'đ': '&#273;',
                    'è': '&#232;', 'é': '&#233;', 'ẻ': '&#7867;', 'ẽ': '&#7869;', 'ẹ': '&#7865;',
                    'ê': '&#234;', 'ề': '&#7873;', 'ế': '&#7871;', 'ể': '&#7875;', 'ễ': '&#7877;', 'ệ': '&#7879;',
                    'ì': '&#236;', 'í': '&#237;', 'ỉ': '&#7881;', 'ĩ': '&#297;', 'ị': '&#7883;',
                    'ò': '&#242;', 'ó': '&#243;', 'ỏ': '&#7887;', 'õ': '&#245;', 'ọ': '&#7885;',
                    'ô': '&#244;', 'ồ': '&#7891;', 'ố': '&#7889;', 'ổ': '&#7893;', 'ỗ': '&#7895;', 'ộ': '&#7897;',
                    'ơ': '&#417;', 'ờ': '&#7901;', 'ớ': '&#7899;', 'ở': '&#7903;', 'ỡ': '&#7905;', 'ợ': '&#7907;',
                    'ù': '&#249;', 'ú': '&#250;', 'ủ': '&#7911;', 'ũ': '&#361;', 'ụ': '&#7909;',
                    'ư': '&#432;', 'ừ': '&#7915;', 'ứ': '&#7913;', 'ử': '&#7917;', 'ữ': '&#7919;', 'ự': '&#7921;',
                    'ỳ': '&#7923;', 'ý': '&#253;', 'ỷ': '&#7927;', 'ỹ': '&#7929;', 'ỵ': '&#7925;',
                    # Uppercase
                    'À': '&#192;', 'Á': '&#193;', 'Ả': '&#7842;', 'Ã': '&#195;', 'Ạ': '&#7840;',
                    'Ă': '&#258;', 'Ằ': '&#7856;', 'Ắ': '&#7854;', 'Ẳ': '&#7858;', 'Ẵ': '&#7860;', 'Ặ': '&#7862;',
                    'Â': '&#194;', 'Ầ': '&#7846;', 'Ấ': '&#7844;', 'Ẩ': '&#7848;', 'Ẫ': '&#7850;', 'Ậ': '&#7852;',
                    'Đ': '&#272;',
                    'È': '&#200;', 'É': '&#201;', 'Ẻ': '&#7866;', 'Ẽ': '&#7868;', 'Ẹ': '&#7864;',
                    'Ê': '&#202;', 'Ề': '&#7872;', 'Ế': '&#7870;', 'Ể': '&#7874;', 'Ễ': '&#7876;', 'Ệ': '&#7878;',
                    'Ì': '&#204;', 'Í': '&#205;', 'Ỉ': '&#7880;', 'Ĩ': '&#296;', 'Ị': '&#7882;',
                    'Ò': '&#210;', 'Ó': '&#211;', 'Ỏ': '&#7886;', 'Õ': '&#213;', 'Ọ': '&#7884;',
                    'Ô': '&#212;', 'Ồ': '&#7890;', 'Ố': '&#7888;', 'Ổ': '&#7892;', 'Ỗ': '&#7894;', 'Ộ': '&#7896;',
                    'Ơ': '&#416;', 'Ờ': '&#7900;', 'Ớ': '&#7898;', 'Ở': '&#7902;', 'Ỡ': '&#7904;', 'Ợ': '&#7906;',
                    'Ù': '&#217;', 'Ú': '&#218;', 'Ủ': '&#7910;', 'Ũ': '&#360;', 'Ụ': '&#7908;',
                    'Ư': '&#431;', 'Ừ': '&#7914;', 'Ứ': '&#7912;', 'Ử': '&#7916;', 'Ữ': '&#7918;', 'Ự': '&#7920;',
                    'Ỳ': '&#7922;', 'Ý': '&#221;', 'Ỷ': '&#7926;', 'Ỹ': '&#7928;', 'Ỵ': '&#7924;',
                }
                
                # First escape HTML special characters
                text = (text.replace('&', '&amp;')
                           .replace('<', '&lt;')
                           .replace('>', '&gt;')
                           .replace('"', '&quot;'))
                
                # Then encode Vietnamese characters
                for viet_char, html_entity in vietnamese_map.items():
                    text = text.replace(viet_char, html_entity)
                
                return text
            
            # Legacy escape_html for backward compatibility (redirects to encode_vietnamese)
            def escape_html(text):
                """Deprecated: Use encode_vietnamese instead"""
                return encode_vietnamese(text)
            
            # Add asset-specific context
            sector = analysis.get('sector_analysis', {})
            if sector and sector.get('sector') != 'Unknown':
                tech += f"• Sector: {escape_html(sector.get('sector', ''))}\n"
                tech += f"• Momentum: {escape_html(sector.get('sector_momentum', ''))}\n"
                tech += f"• Rotation Risk: {escape_html(sector.get('rotation_risk', ''))}\n\n"
            
            corr = analysis.get('correlation_analysis', {})
            if corr:
                # Safely convert to int, handle both string and int
                try:
                    btc_corr = int(corr.get('btc_correlation', 0)) if corr.get('btc_correlation') else 0
                    eth_corr = int(corr.get('eth_correlation', 0)) if corr.get('eth_correlation') else 0
                    indep_prob = int(corr.get('independent_move_probability', 50)) if corr.get('independent_move_probability') else 50
                    
                    if btc_corr > 0:
                        tech += f"🔗 <b>Correlation:</b>\n"
                        tech += f"• BTC: {btc_corr}%\n"
                        tech += f"• ETH: {eth_corr}%\n"
                        tech += f"• Independent: {indep_prob}%\n\n"
                except (ValueError, TypeError):
                    # Skip correlation section if values can't be converted
                    pass
            
            fund = analysis.get('fundamental_analysis', {})
            if fund:
                # Safely convert health_score to int
                try:
                    health_score = int(fund.get('health_score', 0)) if fund.get('health_score') is not None else 0
                    if health_score >= 0:
                        tech += f"💪 <b>Fundamental:</b>\n"
                        tech += f"• Health: {health_score}/100\n"
                        tech += f"• Tokenomics: {escape_html(fund.get('tokenomics', 'Unknown'))}\n"
                        tech += f"• Risk: {escape_html(fund.get('centralization_risk', 'Medium'))}\n"
                        tech += f"• Ecosystem: {escape_html(fund.get('ecosystem_strength', 'Moderate'))}\n\n"
                except (ValueError, TypeError):
                    # Skip if health_score can't be converted
                    pass
            
            sizing = analysis.get('position_sizing_recommendation', {})
            if sizing and sizing.get('position_size_percent'):
                tech += f"📊 <b>Position Sizing:</b>\n"
                tech += f"• Size: {escape_html(sizing.get('position_size_percent', ''))}\n"
                tech += f"• Risk: {escape_html(sizing.get('risk_per_trade', ''))}\n"
                tech += f"• Leverage: {escape_html(sizing.get('recommended_leverage', ''))}\n"
                if sizing.get('liquidity_notes'):
                    tech += f"• Liquidity: {escape_html(sizing.get('liquidity_notes', ''))}\n"
                tech += "\n"
            
            # Macro context for BTC or altcoins
            macro = analysis.get('macro_context', {})
            if macro:
                if asset_type == 'BTC':
                    tech += f"🏛️ <b>BTC Macro:</b>\n"
                    tech += f"• Dominance: {escape_html(macro.get('btc_dominance', 'N/A'))}\n"
                    tech += f"• Flows: {escape_html(macro.get('institutional_flows', 'N/A'))}\n"
                    tech += f"• ETF: {escape_html(macro.get('etf_status', 'N/A'))}\n"
                    tech += f"• Whale: {escape_html(macro.get('whale_activity', 'N/A'))}\n\n"
                elif asset_type in ['ETH', 'LARGE_CAP_ALT', 'MID_CAP_ALT']:
                    tech += f"🔗 <b>Altcoin Context:</b>\n"
                    tech += f"• Sector: {escape_html(macro.get('sector_rotation_status', 'N/A'))}\n"
                    tech += f"• BTC Depend: {escape_html(macro.get('btc_dependency', 'N/A'))}\n"
                    if macro.get('project_catalysts'):
                        tech += f"• Catalysts: {escape_html(macro.get('project_catalysts', ''))}\n"
                    tech += f"• Liquidity: {escape_html(macro.get('liquidity_assessment', 'N/A'))}\n\n"
            
            # Scores
            # Safely convert scores to numbers
            try:
                tech_score = float(analysis.get('technical_score', 0)) if analysis.get('technical_score') is not None else 0
                fund_score = float(analysis.get('fundamental_score', 0)) if analysis.get('fundamental_score') is not None else 0
            except (ValueError, TypeError):
                tech_score = 0
                fund_score = 0
            
            tech += "📈 <b>&#272;i&#7875;m &#272;&#225;nh Gi&#225;:</b>\n"
            tech += f"• K&#7929; Thu&#7853;t: {tech_score:.0f}/100\n"
            tech += f"• C&#417; B&#7843;n: {fund_score:.0f}/100\n"
            tech += f"• T&#7893;ng: {(tech_score + fund_score)/2:.0f}/100\n\n"
            
            # Market sentiment
            sentiment = analysis.get('market_sentiment', 'NEUTRAL')
            sentiment_emoji = "🟢" if sentiment == "BULLISH" else "🔴" if sentiment == "BEARISH" else "🟡"
            sentiment_vn = "T&#259;ng" if sentiment == "BULLISH" else "Gi&#7843;m" if sentiment == "BEARISH" else "Trung L&#7853;p"
            tech += f"💭 <b>T&#226;m L&#253;:</b> {sentiment_emoji} {sentiment_vn}\n\n"
            
            # Key points
            tech += "🎯 <b>&#272;i&#7875;m Ch&#237;nh:</b>\n"
            for point in analysis.get('key_points', []):
                # Encode Vietnamese and escape HTML characters in key points
                safe_point = encode_vietnamese(str(point))
                tech += f"✓ {safe_point}\n"
            
            # Conflicting signals
            conflicts = analysis.get('conflicting_signals', [])
            if conflicts:
                tech += "\n⚠️ <b>T&#237;n Hi&#7879;u M&#226;u Thu&#7849;n:</b>\n"
                for conflict in conflicts:
                    safe_conflict = encode_vietnamese(str(conflict))
                    tech += f"• {safe_conflict}\n"
            
            # Warnings
            warnings = analysis.get('warnings', [])
            if warnings:
                tech += "\n🚨 <b>C&#7843;nh B&#225;o:</b>\n"
                for warning in warnings:
                    safe_warning = encode_vietnamese(str(warning))
                    tech += f"⚠️ {safe_warning}\n"
            
            # Historical Analysis
            hist_analysis = analysis.get('historical_analysis', {})
            if hist_analysis:
                tech += "\n📊 <b>D&#7919; Li&#7879;u L&#7883;ch S&#7917;:</b>\n\n"
                
                # 1H Context
                h1 = hist_analysis.get('h1_context', {})
                if h1:
                    tech += "⏰ <b>1H (7 ng&#224;y):</b>\n"
                    if h1.get('rsi_interpretation'):
                        tech += f"• RSI: {encode_vietnamese(h1['rsi_interpretation'])}\n"
                    if h1.get('volume_trend'):
                        tech += f"• Volume: {encode_vietnamese(h1['volume_trend'])}\n"
                    if h1.get('price_position'):
                        tech += f"• V&#7883; tr&#237;: {encode_vietnamese(h1['price_position'])}\n"
                    if h1.get('institutional_insights'):
                        tech += f"• Institutional: {encode_vietnamese(h1['institutional_insights'])}\n"
                    tech += "\n"
                
                # 4H Context
                h4 = hist_analysis.get('h4_context', {})
                if h4:
                    tech += "⏰ <b>4H (30 ng&#224;y):</b>\n"
                    if h4.get('rsi_interpretation'):
                        tech += f"• RSI: {encode_vietnamese(h4['rsi_interpretation'])}\n"
                    if h4.get('volume_trend'):
                        tech += f"• Volume: {encode_vietnamese(h4['volume_trend'])}\n"
                    if h4.get('price_position'):
                        tech += f"• V&#7883; tr&#237;: {encode_vietnamese(h4['price_position'])}\n"
                    if h4.get('institutional_insights'):
                        tech += f"• Institutional: {encode_vietnamese(h4['institutional_insights'])}\n"
                    tech += "\n"
                
                # 1D Context
                d1 = hist_analysis.get('d1_context', {})
                if d1:
                    tech += "⏰ <b>1D (90 ng&#224;y):</b>\n"
                    if d1.get('rsi_mfi_correlation'):
                        tech += f"• RSI/MFI: {encode_vietnamese(d1['rsi_mfi_correlation'])}\n"
                    if d1.get('long_term_trend'):
                        tech += f"• Xu h&#432;&#7899;ng: {encode_vietnamese(d1['long_term_trend'])}\n"
                    if d1.get('volatility_assessment'):
                        tech += f"• Bi&#7871;n &#273;&#7897;ng: {encode_vietnamese(d1['volatility_assessment'])}\n"
                    if d1.get('institutional_insights'):
                        tech += f"• Institutional: {encode_vietnamese(d1['institutional_insights'])}\n"
            
            tech += "\n<i>💡 Ph&#226;n t&#237;ch &#273;a khung th&#7901;i gian</i>"
            
            # Message 3: AI Reasoning
            reasoning = "🧠 <b>PH&#194;N T&#205;CH CHI TI&#7870;T T&#7914; AI</b>\n\n"
            reasoning += f"💎 <b>{symbol}</b>\n\n"
            reasoning += encode_vietnamese(analysis.get('reasoning_vietnamese', 'Không có phân tích chi tiết.'))
            reasoning += f"\n\n⏰ <b>Th&#7901;i gian:</b> {analysis.get('analyzed_at', 'N/A')}\n"
            reasoning += f"🤖 <b>Model:</b> Gemini 2.0 Flash\n\n"
            reasoning += "<i>⚠️ &#272;&#226;y l&#224; ph&#226;n t&#237;ch AI, kh&#244;ng ph&#7843;i t&#432; v&#7845;n t&#224;i ch&#237;nh.\n"
            reasoning += "Lu&#244;n DYOR (Do Your Own Research) tr&#432;&#7899;c khi &#273;&#7847;u t&#432;.</i>"
            
            # Return in proper order: technical details first, then summary, then reasoning
            # This allows users to understand the analysis BEFORE seeing entry/TP/SL recommendations
            # Store split_long_message function for external use
            self._split_message = split_long_message
            
            return summary, tech, reasoning
            
        except Exception as e:
            logger.error(f"Error formatting response: {e}")
            error_msg = f"❌ Lỗi khi format kết quả AI analysis: {str(e)}"
            return error_msg, "", ""
