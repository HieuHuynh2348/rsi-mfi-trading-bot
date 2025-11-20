"""
Bot Trading Activity Detector v2.0
Detects algorithmic/bot trading patterns on Binance

Enhanced with 5 BOT types:
- Wash Trading BOT
- Spoofing BOT
- Iceberg BOT
- Market Maker BOT
- Dump BOT
"""

import logging
from datetime import datetime
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class BotDetector:
    def __init__(self, binance_client):
        """
        Initialize Bot Detector
        
        Args:
            binance_client: BinanceClient instance
        """
        self.binance = binance_client
        logger.info("✅ Bot detector v2.0 initialized with 5 BOT detection types")
    
    def detect_bot_activity(self, symbol):
        """
        Analyze a symbol for bot trading patterns
        
        Args:
            symbol: Trading symbol (e.g., BTCUSDT)
        
        Returns:
            dict with bot activity analysis or None
        """
        try:
            # 1. Get Order Book Depth
            depth = self.binance.client.get_order_book(symbol=symbol, limit=100)
            
            # 2. Get Recent Trades
            trades = self.binance.client.get_recent_trades(symbol=symbol, limit=500)
            
            # 3. Get Aggregate Trades (for timing analysis)
            agg_trades = self.binance.client.get_aggregate_trades(symbol=symbol, limit=1000)
            
            # 4. Get 24h data for pump detection
            ticker_24h = self.binance.client.get_ticker(symbol=symbol)
            
            # 5. Get recent klines for price action analysis
            klines = self.binance.get_klines(symbol, '5m', limit=100)
            
            # Analyze components
            orderbook_analysis = self._analyze_orderbook(depth)
            trade_analysis = self._analyze_trades(trades)
            timing_analysis = self._analyze_timing(agg_trades)
            pump_analysis = self._analyze_pump_pattern(ticker_24h, klines, trades)
            
            # NEW: Enhanced BOT detection (5 types)
            enhanced_bot_detection = self._detect_enhanced_bot_types(klines, trades, depth, ticker_24h)
            
            # Combine analyses
            bot_score = self._calculate_bot_score(
                orderbook_analysis,
                trade_analysis,
                timing_analysis,
                enhanced_bot_detection  # Include enhanced detection in scoring
            )
            
            # Calculate pump score separately
            pump_score = pump_analysis.get('pump_score', 0)
            
            result = {
                'symbol': symbol,
                'bot_score': bot_score,
                'pump_score': pump_score,
                'likely_bot_activity': bot_score >= 40,  # 40%+ = likely bot (more sensitive)
                'likely_pump_bot': pump_score >= 45,  # 45%+ = likely pump bot (more sensitive)
                'confidence': self._get_confidence_level(bot_score),
                'pump_confidence': self._get_confidence_level(pump_score),
                'orderbook': orderbook_analysis,
                'trades': trade_analysis,
                'timing': timing_analysis,
                'pump': pump_analysis,
                'enhanced_bot_types': enhanced_bot_detection,  # NEW
                'timestamp': datetime.now()
            }
            
            logger.info(f"Bot detection for {symbol}: Bot Score={bot_score:.1f}%, Pump Score={pump_score:.1f}%")
            
            # Log detected BOT types
            detected_types = [k for k, v in enhanced_bot_detection.items() 
                            if isinstance(v, dict) and v.get('detected')]
            if detected_types:
                logger.warning(f"⚠️ {symbol}: Detected BOT types: {', '.join(detected_types)}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error detecting bot activity for {symbol}: {e}")
            return None
    
    def _analyze_orderbook(self, depth):
        """
        Analyze order book for bot patterns
        
        Returns:
            dict with orderbook analysis
        """
        try:
            bids = [(float(p), float(q)) for p, q in depth['bids'][:50]]
            asks = [(float(p), float(q)) for p, q in depth['asks'][:50]]
            
            if not bids or not asks:
                return {'bot_indicators': 0, 'spread_percent': 0}
            
            best_bid = bids[0][0]
            best_ask = asks[0][0]
            spread = best_ask - best_bid
            spread_percent = (spread / best_bid) * 100
            
            # Bot indicators
            bot_indicators = 0
            
            # 1. Very tight spread (< 0.05%)
            if spread_percent < 0.05:
                bot_indicators += 1
            
            # 2. Check for "walls" - large orders at specific levels
            bid_quantities = [q for p, q in bids]
            ask_quantities = [q for p, q in asks]
            
            avg_bid_qty = np.mean(bid_quantities) if bid_quantities else 0
            avg_ask_qty = np.mean(ask_quantities) if ask_quantities else 0
            
            # Large orders (>5x average) = potential bot walls
            large_bids = sum(1 for q in bid_quantities if q > avg_bid_qty * 5)
            large_asks = sum(1 for q in ask_quantities if q > avg_ask_qty * 5)
            
            if large_bids >= 3 or large_asks >= 3:
                bot_indicators += 1
            
            # 3. Check for evenly spaced orders (bot signature)
            bid_prices = [p for p, q in bids[:20]]
            ask_prices = [p for p, q in asks[:20]]
            
            if len(bid_prices) >= 5:
                bid_gaps = [bid_prices[i] - bid_prices[i+1] for i in range(len(bid_prices)-1)]
                bid_gap_std = np.std(bid_gaps) if bid_gaps else 0
                bid_gap_mean = np.mean(bid_gaps) if bid_gaps else 0
                
                # Low variance in gaps = evenly spaced = bot
                if bid_gap_mean > 0 and bid_gap_std / bid_gap_mean < 0.1:
                    bot_indicators += 1
            
            if len(ask_prices) >= 5:
                ask_gaps = [ask_prices[i+1] - ask_prices[i] for i in range(len(ask_prices)-1)]
                ask_gap_std = np.std(ask_gaps) if ask_gaps else 0
                ask_gap_mean = np.mean(ask_gaps) if ask_gaps else 0
                
                if ask_gap_mean > 0 and ask_gap_std / ask_gap_mean < 0.1:
                    bot_indicators += 1
            
            return {
                'spread_percent': round(spread_percent, 4),
                'bot_indicators': bot_indicators,
                'large_orders': large_bids + large_asks,
                'avg_bid_size': round(avg_bid_qty, 2),
                'avg_ask_size': round(avg_ask_qty, 2)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing orderbook: {e}")
            return {'bot_indicators': 0, 'spread_percent': 0}
    
    def _analyze_trades(self, trades):
        """
        Analyze recent trades for bot patterns
        
        Returns:
            dict with trade analysis
        """
        try:
            if not trades or len(trades) < 10:
                return {'bot_indicators': 0}
            
            # Extract trade quantities
            quantities = [float(t['qty']) for t in trades]
            
            # Bot indicators
            bot_indicators = 0
            
            # 1. Check for repeated trade sizes
            unique_qty = len(set(quantities))
            total_qty = len(quantities)
            unique_ratio = unique_qty / total_qty if total_qty > 0 else 1
            
            # Low unique ratio (< 0.3) = many repeated sizes = bot
            if unique_ratio < 0.3:
                bot_indicators += 1
            
            # 2. Check for "round" numbers (100, 1000, 0.1, 0.01, etc.)
            round_numbers = sum(1 for q in quantities if self._is_round_number(q))
            round_ratio = round_numbers / total_qty if total_qty > 0 else 0
            
            # High round ratio (> 0.5) = bot
            if round_ratio > 0.5:
                bot_indicators += 1
            
            # 3. Check for identical consecutive trades
            consecutive_same = 0
            for i in range(1, len(quantities)):
                if quantities[i] == quantities[i-1]:
                    consecutive_same += 1
            
            consecutive_ratio = consecutive_same / (total_qty - 1) if total_qty > 1 else 0
            
            # High consecutive ratio (> 0.4) = bot
            if consecutive_ratio > 0.4:
                bot_indicators += 1
            
            return {
                'bot_indicators': bot_indicators,
                'unique_size_ratio': round(unique_ratio, 3),
                'round_number_ratio': round(round_ratio, 3),
                'consecutive_same_ratio': round(consecutive_ratio, 3),
                'total_trades': total_qty
            }
            
        except Exception as e:
            logger.error(f"Error analyzing trades: {e}")
            return {'bot_indicators': 0}
    
    def _analyze_timing(self, agg_trades):
        """
        Analyze trade timing for bot patterns
        
        Returns:
            dict with timing analysis
        """
        try:
            if not agg_trades or len(agg_trades) < 20:
                return {'bot_indicators': 0}
            
            # Extract timestamps
            timestamps = [t['T'] for t in agg_trades]
            
            # Calculate time differences (in milliseconds)
            time_diffs = [timestamps[i] - timestamps[i-1] for i in range(1, len(timestamps))]
            
            if not time_diffs:
                return {'bot_indicators': 0}
            
            avg_time_diff = np.mean(time_diffs)
            std_time_diff = np.std(time_diffs)
            
            bot_indicators = 0
            
            # 1. Very fast trades (< 100ms average)
            if avg_time_diff < 100:
                bot_indicators += 1
            
            # 2. Consistent timing (low variance)
            if avg_time_diff > 0:
                cv = std_time_diff / avg_time_diff  # Coefficient of variation
                
                # Low variance (cv < 0.5) = consistent timing = bot
                if cv < 0.5:
                    bot_indicators += 1
            
            # 3. Check for periodic patterns (trades at regular intervals)
            # Round time diffs to nearest 10ms and check for repetition
            rounded_diffs = [round(td / 10) * 10 for td in time_diffs]
            unique_intervals = len(set(rounded_diffs))
            total_intervals = len(rounded_diffs)
            
            interval_diversity = unique_intervals / total_intervals if total_intervals > 0 else 1
            
            # Low diversity (< 0.2) = regular intervals = bot
            if interval_diversity < 0.2:
                bot_indicators += 1
            
            return {
                'bot_indicators': bot_indicators,
                'avg_interval_ms': round(avg_time_diff, 2),
                'std_interval_ms': round(std_time_diff, 2),
                'interval_diversity': round(interval_diversity, 3),
                'total_trades': len(agg_trades)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing timing: {e}")
            return {'bot_indicators': 0}
    
    def _analyze_pump_pattern(self, ticker_24h, klines, recent_trades):
        """
        Analyze for PUMP BOT patterns - coordinated buying to artificially inflate price
        
        Args:
            ticker_24h: 24h ticker data
            klines: Recent 5m klines DataFrame
            recent_trades: Recent trades data
        
        Returns:
            dict with pump analysis
        """
        try:
            pump_indicators = 0
            details = {}
            
            # 1. PRICE SPIKE - Sharp price increase in short time
            price_change = float(ticker_24h.get('priceChangePercent', 0))
            details['price_change_24h'] = price_change
            
            # Extreme price spike (>10% in 24h)
            if price_change > 10:
                pump_indicators += 1
            if price_change > 20:
                pump_indicators += 2  # Extra point for extreme spike
            
            # 2. VOLUME SPIKE - Abnormal volume surge
            volume_24h = float(ticker_24h.get('volume', 0))
            quote_volume = float(ticker_24h.get('quoteVolume', 0))
            
            # Check volume concentration in recent candles
            if klines is not None and len(klines) >= 20:
                recent_volumes = klines['volume'].tail(5).sum()  # Last 5 candles
                older_volumes = klines['volume'].iloc[-20:-5].sum()  # Previous 15 candles
                
                if older_volumes > 0:
                    volume_concentration = recent_volumes / (older_volumes / 3)  # Compare to average
                    details['volume_concentration'] = round(volume_concentration, 2)
                    
                    # High concentration (>3x) = pump
                    if volume_concentration > 3:
                        pump_indicators += 1
                    if volume_concentration > 5:
                        pump_indicators += 1
            
            # 3. BUY PRESSURE - Majority of trades are buys (taker buys)
            if recent_trades and len(recent_trades) >= 50:
                buy_count = sum(1 for t in recent_trades if t.get('isBuyerMaker') == False)  # Taker buys
                total_trades = len(recent_trades)
                buy_ratio = buy_count / total_trades if total_trades > 0 else 0
                details['buy_ratio'] = round(buy_ratio, 3)
                
                # High buy ratio (>70%) = coordinated buying
                if buy_ratio > 0.7:
                    pump_indicators += 1
                if buy_ratio > 0.85:
                    pump_indicators += 1
            
            # 4. PRICE VELOCITY - Rapid consecutive green candles
            if klines is not None and len(klines) >= 10:
                last_10_candles = klines.tail(10)
                green_candles = sum(1 for _, row in last_10_candles.iterrows() 
                                  if row['close'] > row['open'])
                green_ratio = green_candles / 10
                details['green_candle_ratio'] = round(green_ratio, 2)
                
                # Mostly green (>80%) = pump momentum
                if green_ratio > 0.8:
                    pump_indicators += 1
            
            # 5. SUDDEN VOLUME APPEARANCE - Low volume then sudden spike
            num_trades_24h = int(ticker_24h.get('count', 0))
            if klines is not None and len(klines) >= 20:
                avg_old_volume = klines['volume'].iloc[-20:-5].mean()
                current_volume = klines['volume'].iloc[-1]
                
                if avg_old_volume > 0:
                    volume_ratio = current_volume / avg_old_volume
                    details['current_vs_avg_volume'] = round(volume_ratio, 2)
                    
                    # Extreme spike (>10x average)
                    if volume_ratio > 10:
                        pump_indicators += 2
                    elif volume_ratio > 5:
                        pump_indicators += 1
            
            # 6. ORDERBOOK IMBALANCE - Heavy buy side
            # This would require orderbook analysis (already in _analyze_orderbook)
            
            # Calculate pump score (max 10 indicators)
            max_pump_indicators = 10
            pump_score = min(100, (pump_indicators / max_pump_indicators) * 100)
            
            # Bonus for extreme combinations
            if price_change > 15 and details.get('buy_ratio', 0) > 0.75:
                pump_score = min(100, pump_score + 15)
            
            details['pump_indicators'] = pump_indicators
            details['pump_score'] = round(pump_score, 1)
            
            return details
            
        except Exception as e:
            logger.error(f"Error analyzing pump pattern: {e}")
            return {'pump_score': 0, 'pump_indicators': 0}
    
    def _detect_enhanced_bot_types(self, klines, trades, depth, ticker_24h):
        """
        Enhanced BOT detection - 5 types
        
        Returns:
            dict with detection results for each BOT type
        """
        bot_types = {
            'wash_trading': {'detected': False, 'confidence': 0, 'evidence': []},
            'spoofing': {'detected': False, 'confidence': 0, 'evidence': []},
            'iceberg': {'detected': False, 'confidence': 0, 'evidence': []},
            'market_maker': {'detected': False, 'confidence': 0, 'evidence': []},
            'dump_bot': {'detected': False, 'confidence': 0, 'evidence': []}
        }
        
        try:
            # === 1. WASH TRADING BOT ===
            if klines is not None and not klines.empty and len(klines) >= 20:
                recent = klines.tail(20)
                volume_spike = recent['volume'].iloc[-1] > recent['volume'].mean() * 2
                price_change = abs((recent['close'].iloc[-1] - recent['close'].iloc[-5]) / recent['close'].iloc[-5] * 100)
                
                if volume_spike and price_change < 0.5:
                    bot_types['wash_trading']['detected'] = True
                    bot_types['wash_trading']['confidence'] = min(90, 50 + (2.0 - price_change) * 20)
                    bot_types['wash_trading']['evidence'].append(f"Volume {recent['volume'].iloc[-1] / recent['volume'].mean():.1f}x but price only {price_change:.2f}%")
            
            # === 2. SPOOFING BOT ===
            if depth and trades and len(trades) > 50:
                try:
                    bid_depth = sum([float(bid[1]) for bid in depth.get('bids', [])[:10]])
                    ask_depth = sum([float(ask[1]) for ask in depth.get('asks', [])[:10]])
                    total_depth = bid_depth + ask_depth
                    
                    recent_trades_vol = sum([float(t.get('qty', 0)) for t in trades[-50:]])
                    
                    if total_depth > recent_trades_vol * 5:
                        bot_types['spoofing']['detected'] = True
                        bot_types['spoofing']['confidence'] = min(85, 40 + (total_depth / recent_trades_vol) * 5)
                        bot_types['spoofing']['evidence'].append(f"Orderbook depth {total_depth:.2f} >> trades {recent_trades_vol:.2f}")
                except:
                    pass
            
            # === 3. ICEBERG BOT ===
            if trades and len(trades) > 100:
                try:
                    trade_sizes = [float(t.get('qty', 0)) for t in trades[-100:]]
                    size_std = np.std(trade_sizes)
                    size_mean = np.mean(trade_sizes)
                    
                    if size_mean > 0 and size_std / size_mean < 0.15:
                        timestamps = [t.get('time', 0) for t in trades[-50:]]
                        if timestamps:
                            time_diffs = np.diff(timestamps)
                            if len(time_diffs) > 0:
                                time_std = np.std(time_diffs)
                                time_mean = np.mean(time_diffs)
                                
                                if time_mean > 0 and time_std / time_mean < 0.3:
                                    bot_types['iceberg']['detected'] = True
                                    bot_types['iceberg']['confidence'] = 75
                                    bot_types['iceberg']['evidence'].append(f"Uniform trade size (CV={size_std/size_mean:.3f}), regular timing")
                except:
                    pass
            
            # === 4. MARKET MAKER BOT ===
            if depth:
                try:
                    best_bid = float(depth['bids'][0][0]) if depth.get('bids') else 0
                    best_ask = float(depth['asks'][0][0]) if depth.get('asks') else 0
                    
                    if best_bid > 0 and best_ask > 0:
                        spread_pct = (best_ask - best_bid) / best_bid * 100
                        
                        if spread_pct < 0.05:
                            bot_types['market_maker']['detected'] = True
                            bot_types['market_maker']['confidence'] = 70
                            bot_types['market_maker']['evidence'].append(f"Extremely tight spread {spread_pct:.4f}%")
                except:
                    pass
            
            # === 5. DUMP BOT ===
            if klines is not None and not klines.empty and len(klines) >= 20:
                recent_20 = klines.tail(20)
                
                price_changes = recent_20['close'].pct_change()
                negative_candles = (price_changes < 0).sum()
                
                volume_trend = np.polyfit(range(len(recent_20)), recent_20['volume'].values, 1)[0]
                
                highs = recent_20['high'].values
                lower_highs = sum([highs[i] < highs[i-1] for i in range(1, len(highs))])
                
                if negative_candles > 14 and volume_trend < 0 and lower_highs > 15:
                    bot_types['dump_bot']['detected'] = True
                    bot_types['dump_bot']['confidence'] = 80
                    bot_types['dump_bot']['evidence'].append(f"{negative_candles}/20 red candles, declining volume, {lower_highs}/19 lower highs")
            
        except Exception as e:
            logger.error(f"Error in enhanced BOT detection: {e}")
        
        return bot_types
    
    def _is_round_number(self, num):
        """
        Check if a number is "round" (ends in 0s)
        
        Examples: 1000, 100, 10, 1, 0.1, 0.01, 0.001
        """
        # Convert to string and check for patterns
        num_str = f"{num:.8f}".rstrip('0').rstrip('.')
        
        # Check if it's a simple number (1, 10, 100, 0.1, 0.01, etc.)
        try:
            # Powers of 10
            if num in [10**i for i in range(-8, 8)]:
                return True
            
            # Multiples of powers of 10
            for power in range(-4, 4):
                base = 10 ** power
                if num % base == 0 and num / base in [1, 2, 5, 10, 25, 50, 100]:
                    return True
            
            return False
        except:
            return False
    
    def _calculate_bot_score(self, orderbook, trades, timing, enhanced=None):
        """
        Calculate overall bot activity score (0-100)
        
        Each indicator contributes to the score
        """
        max_indicators = 10  # Total possible indicators across all analyses
        total_indicators = (
            orderbook.get('bot_indicators', 0) +
            trades.get('bot_indicators', 0) +
            timing.get('bot_indicators', 0)
        )
        
        # Base score from indicators
        base_score = (total_indicators / max_indicators) * 100
        
        # Bonus adjustments
        bonus = 0
        
        # Very tight spread is strong indicator
        if orderbook.get('spread_percent', 1) < 0.03:
            bonus += 10
        
        # Very fast trades is strong indicator
        if timing.get('avg_interval_ms', 1000) < 50:
            bonus += 10
        
        # NEW: Enhanced BOT detection bonus
        if enhanced:
            detected_count = sum([1 for k, v in enhanced.items() 
                                if isinstance(v, dict) and v.get('detected')])
            
            # Each detected BOT type adds 10-15 points
            if enhanced.get('wash_trading', {}).get('detected'):
                bonus += 12
            if enhanced.get('spoofing', {}).get('detected'):
                bonus += 15
            if enhanced.get('iceberg', {}).get('detected'):
                bonus += 10
            if enhanced.get('market_maker', {}).get('detected'):
                bonus += 8
            if enhanced.get('dump_bot', {}).get('detected'):
                bonus += 15
        
        # Cap at 100
        final_score = min(100, base_score + bonus)
        
        return round(final_score, 1)
    
    def _get_confidence_level(self, bot_score):
        """
        Get confidence level based on bot score
        
        Returns:
            str: 'LOW', 'MEDIUM', 'HIGH', 'VERY HIGH'
        """
        if bot_score >= 75:
            return 'VERY HIGH'
        elif bot_score >= 60:
            return 'HIGH'
        elif bot_score >= 40:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def get_formatted_analysis(self, detection_result):
        """
        Format bot detection result for display
        
        Args:
            detection_result: Result from detect_bot_activity()
        
        Returns:
            str: Formatted text message
        """
        from vietnamese_messages import get_bot_detection_message
        return get_bot_detection_message(detection_result)
