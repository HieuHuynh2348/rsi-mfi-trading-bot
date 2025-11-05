"""
Bot Trading Activity Detector
Detects algorithmic/bot trading patterns on Binance
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
        logger.info("Bot detector initialized")
    
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
            
            # Analyze components
            orderbook_analysis = self._analyze_orderbook(depth)
            trade_analysis = self._analyze_trades(trades)
            timing_analysis = self._analyze_timing(agg_trades)
            
            # Combine analyses
            bot_score = self._calculate_bot_score(
                orderbook_analysis,
                trade_analysis,
                timing_analysis
            )
            
            result = {
                'symbol': symbol,
                'bot_score': bot_score,
                'likely_bot_activity': bot_score >= 50,  # 50%+ = likely bot
                'confidence': self._get_confidence_level(bot_score),
                'orderbook': orderbook_analysis,
                'trades': trade_analysis,
                'timing': timing_analysis,
                'timestamp': datetime.now()
            }
            
            logger.info(f"Bot detection for {symbol}: Score={bot_score:.1f}%, Likely={result['likely_bot_activity']}")
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
    
    def _calculate_bot_score(self, orderbook, trades, timing):
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
        if not detection_result:
            return "❌ Bot detection failed"
        
        symbol = detection_result['symbol']
        score = detection_result['bot_score']
        likely = detection_result['likely_bot_activity']
        confidence = detection_result['confidence']
        
        # Emoji based on likelihood
        if likely:
            emoji = "🤖"
            verdict = "LIKELY BOT TRADING"
        else:
            emoji = "👤"
            verdict = "LIKELY HUMAN TRADING"
        
        msg = f"{emoji} <b>BOT ACTIVITY ANALYSIS</b>\n"
        msg += f"<b>Symbol:</b> {symbol}\n\n"
        
        # Score bar
        msg += f"<b>Bot Score:</b> {score}% "
        msg += "█" * int(score / 10) + "░" * (10 - int(score / 10)) + "\n"
        msg += f"<b>Verdict:</b> {verdict}\n"
        msg += f"<b>Confidence:</b> {confidence}\n\n"
        
        # Orderbook analysis
        ob = detection_result['orderbook']
        msg += f"<b>📊 Order Book:</b>\n"
        msg += f"   Spread: {ob.get('spread_percent', 0):.4f}%\n"
        msg += f"   Large orders: {ob.get('large_orders', 0)}\n"
        msg += f"   Bot signals: {ob.get('bot_indicators', 0)}/4\n\n"
        
        # Trade analysis
        tr = detection_result['trades']
        msg += f"<b>💱 Trade Patterns:</b>\n"
        msg += f"   Unique sizes: {tr.get('unique_size_ratio', 0)*100:.1f}%\n"
        msg += f"   Round numbers: {tr.get('round_number_ratio', 0)*100:.1f}%\n"
        msg += f"   Bot signals: {tr.get('bot_indicators', 0)}/3\n\n"
        
        # Timing analysis
        tm = detection_result['timing']
        msg += f"<b>⏱️ Timing:</b>\n"
        msg += f"   Avg interval: {tm.get('avg_interval_ms', 0):.1f}ms\n"
        msg += f"   Interval diversity: {tm.get('interval_diversity', 0)*100:.1f}%\n"
        msg += f"   Bot signals: {tm.get('bot_indicators', 0)}/3\n\n"
        
        # Interpretation
        msg += f"<b>💡 Interpretation:</b>\n"
        if likely:
            msg += "   High probability of algorithmic/bot trading.\n"
            msg += "   Market makers or trading bots are active.\n"
            if score >= 75:
                msg += "   ⚠️ Very strong bot activity detected!"
        else:
            msg += "   Market appears to have natural/human trading.\n"
            msg += "   Low bot activity detected.\n"
        
        return msg
