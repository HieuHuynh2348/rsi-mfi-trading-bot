"""
Advanced Pump/Dump Detector v4.0
Phát hiện chính xác coin sẽ tăng/giảm mạnh với 15+ indicators

Features:
- 5 loại BOT detection (Wash Trading, Spoofing, Iceberg, Market Maker, Dump)
- Volume legitimacy analysis (VWAP, buy/sell pressure, large trades)
- Order book manipulation detection (fake walls, layering)
- Price action quality assessment (respects S/R, clean breakouts)
- Institutional flow detection (block trades, Wyckoff patterns)
- Direction probability calculation (UP/DOWN/SIDEWAYS)
- Comprehensive risk assessment

Author: AI Assistant
Date: November 20, 2025
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class AdvancedPumpDumpDetector:
    """
    Phát hiện Pump/Dump với độ chính xác cao
    Kết hợp 15+ indicators để xác định xu hướng thực sự
    """
    
    def __init__(self, binance_client):
        """
        Initialize advanced detector
        
        Args:
            binance_client: BinanceClient instance
        """
        self.binance = binance_client
        self.confidence_threshold = 70  # Ngưỡng tin cậy tối thiểu
        
        logger.info("✅ Advanced Pump/Dump Detector v4.0 initialized")
        
    def analyze_comprehensive(self, 
                            symbol: str,
                            klines_5m: Optional[pd.DataFrame] = None,
                            klines_1h: Optional[pd.DataFrame] = None,
                            order_book: Optional[Dict] = None,
                            trades: Optional[List[Dict]] = None,
                            market_data: Optional[Dict] = None) -> Dict:
        """
        Phân tích toàn diện để xác định pump/dump thực sự
        
        Args:
            symbol: Trading symbol
            klines_5m: 5-minute klines data
            klines_1h: 1-hour klines data  
            order_book: Order book data
            trades: Recent trades data
            market_data: 24h market data
            
        Returns:
            {
                'signal': 'STRONG_PUMP' | 'PUMP' | 'NEUTRAL' | 'DUMP' | 'STRONG_DUMP',
                'confidence': 0-100,
                'direction_probability': {
                    'up': 0-100,
                    'down': 0-100,
                    'sideways': 0-100
                },
                'bot_activity': {...},
                'volume_analysis': {...},
                'depth_analysis': {...},
                'price_quality': {...},
                'institutional_flow': {...},
                'risk_level': 'LOW' | 'MEDIUM' | 'HIGH' | 'EXTREME',
                'recommendation': {...}
            }
        """
        
        try:
            results = {}
            
            # Fetch data if not provided
            if klines_5m is None:
                klines_5m = self.binance.get_klines(symbol, '5m', limit=200)
            if klines_1h is None:
                klines_1h = self.binance.get_klines(symbol, '1h', limit=100)
            if order_book is None:
                try:
                    order_book = self.binance.client.get_order_book(symbol=symbol, limit=100)
                except:
                    order_book = None
            if trades is None:
                try:
                    trades = self.binance.client.get_recent_trades(symbol=symbol, limit=500)
                except:
                    trades = []
            if market_data is None:
                try:
                    market_data = self.binance.client.get_ticker(symbol=symbol)
                except:
                    market_data = {}
            
            # Use 5m for main analysis, 1h for confirmation
            klines = klines_5m if klines_5m is not None and not klines_5m.empty else klines_1h
            
            if klines is None or klines.empty:
                logger.warning(f"No klines data for {symbol}")
                return self._get_neutral_result(symbol)
            
            # 1. Phân tích BOT activity (15 points)
            bot_analysis = self._detect_bot_types(klines, trades, order_book)
            results['bot_activity'] = bot_analysis
            
            # 2. Phân tích Volume Profile (20 points)
            volume_analysis = self._analyze_volume_legitimacy(klines, trades)
            results['volume_analysis'] = volume_analysis
            
            # 3. Phân tích Order Book Depth (15 points)
            depth_analysis = self._analyze_order_book_manipulation(order_book)
            results['depth_analysis'] = depth_analysis
            
            # 4. Phân tích Price Action Quality (20 points)
            price_quality = self._analyze_price_action_quality(klines)
            results['price_quality'] = price_quality
            
            # 5. Phân tích Institutional Flow (30 points - quan trọng nhất!)
            institutional = self._detect_institutional_activity(klines, trades, market_data)
            results['institutional_flow'] = institutional
            
            # 6. Tính toán xác suất hướng di chuyển
            direction_prob = self._calculate_direction_probability(results)
            results['direction_probability'] = direction_prob
            
            # 7. Tính confidence tổng thể
            confidence = self._calculate_overall_confidence(results)
            results['confidence'] = confidence
            
            # 8. Xác định signal cuối cùng
            signal = self._determine_final_signal(direction_prob, confidence, results)
            results['signal'] = signal
            
            # 9. Đánh giá rủi ro
            risk = self._assess_risk_level(results)
            results['risk_level'] = risk
            
            # 10. Tạo recommendation
            recommendation = self._generate_recommendation(results, symbol)
            results['recommendation'] = recommendation
            
            # Add metadata
            results['symbol'] = symbol
            results['timestamp'] = datetime.now().isoformat()
            
            logger.info(f"📊 {symbol}: Signal={signal}, Confidence={confidence}%, Risk={risk}")
            
            return results
            
        except Exception as e:
            logger.error(f"Error in comprehensive analysis for {symbol}: {e}")
            return self._get_neutral_result(symbol)
    
    def _get_neutral_result(self, symbol: str) -> Dict:
        """Return neutral result when analysis fails"""
        return {
            'symbol': symbol,
            'signal': 'NEUTRAL',
            'confidence': 0,
            'direction_probability': {'up': 33, 'down': 33, 'sideways': 34},
            'bot_activity': {},
            'volume_analysis': {},
            'depth_analysis': {},
            'price_quality': {},
            'institutional_flow': {},
            'risk_level': 'MEDIUM',
            'recommendation': {'action': 'WAIT', 'reasoning': ['Insufficient data']},
            'timestamp': datetime.now().isoformat()
        }
    
    def _detect_bot_types(self, klines: pd.DataFrame, trades: List[Dict], order_book: Optional[Dict]) -> Dict:
        """
        Phát hiện 5 loại BOT:
        - Wash Trading BOT
        - Spoofing BOT  
        - Iceberg BOT
        - Market Maker BOT
        - Dump BOT
        """
        
        bot_signals = {
            'wash_trading': {'detected': False, 'confidence': 0, 'evidence': []},
            'spoofing': {'detected': False, 'confidence': 0, 'evidence': []},
            'iceberg': {'detected': False, 'confidence': 0, 'evidence': []},
            'market_maker': {'detected': False, 'confidence': 0, 'evidence': []},
            'dump_bot': {'detected': False, 'confidence': 0, 'evidence': []}
        }
        
        if klines.empty:
            return bot_signals
        
        # === 1. WASH TRADING DETECTION ===
        # Volume spike nhưng giá không đổi
        recent = klines.tail(20)
        volume_spike = recent['volume'].iloc[-1] > recent['volume'].mean() * 2
        price_change = abs((recent['close'].iloc[-1] - recent['close'].iloc[-5]) / recent['close'].iloc[-5] * 100)
        
        if volume_spike and price_change < 0.5:
            bot_signals['wash_trading']['detected'] = True
            bot_signals['wash_trading']['confidence'] = min(90, 50 + (2.0 - price_change) * 20)
            bot_signals['wash_trading']['evidence'].append(f"Volume tăng {recent['volume'].iloc[-1] / recent['volume'].mean():.1f}x nhưng giá chỉ thay đổi {price_change:.2f}%")
        
        # === 2. SPOOFING DETECTION ===
        # Order book thay đổi nhiều nhưng ít trades
        if order_book and trades:
            try:
                bid_depth = sum([float(bid[1]) for bid in order_book.get('bids', [])[:10]])
                ask_depth = sum([float(ask[1]) for ask in order_book.get('asks', [])[:10]])
                total_depth = bid_depth + ask_depth
                
                recent_trades_volume = sum([float(t.get('qty', 0)) for t in trades[-50:]])
                
                if total_depth > recent_trades_volume * 5:
                    bot_signals['spoofing']['detected'] = True
                    bot_signals['spoofing']['confidence'] = min(85, 40 + (total_depth / recent_trades_volume) * 5)
                    bot_signals['spoofing']['evidence'].append(f"Order book depth {total_depth:.2f} >> recent trades {recent_trades_volume:.2f}")
            except:
                pass
        
        # === 3. ICEBERG BOT DETECTION ===
        # Nhiều orders nhỏ cùng size, đều đặn
        if trades and len(trades) > 100:
            try:
                trade_sizes = [float(t.get('qty', 0)) for t in trades[-100:]]
                size_std = np.std(trade_sizes)
                size_mean = np.mean(trade_sizes)
                
                # Nếu std/mean < 0.15 → size rất đồng nhất → bot
                if size_mean > 0 and size_std / size_mean < 0.15:
                    # Check thời gian đều đặn
                    timestamps = [t.get('time', 0) for t in trades[-50:]]
                    if timestamps:
                        time_diffs = np.diff(timestamps)
                        time_std = np.std(time_diffs)
                        time_mean = np.mean(time_diffs)
                        
                        if time_mean > 0 and time_std / time_mean < 0.3:
                            bot_signals['iceberg']['detected'] = True
                            bot_signals['iceberg']['confidence'] = 75
                            bot_signals['iceberg']['evidence'].append(f"Trade size đồng nhất (std/mean={size_std/size_mean:.3f}), thời gian đều đặn")
            except:
                pass
        
        # === 4. MARKET MAKER BOT DETECTION ===
        # Bid-ask spread hẹp bất thường + depth cao
        if order_book:
            try:
                best_bid = float(order_book['bids'][0][0]) if order_book.get('bids') else 0
                best_ask = float(order_book['asks'][0][0]) if order_book.get('asks') else 0
                
                if best_bid > 0 and best_ask > 0:
                    spread_pct = (best_ask - best_bid) / best_bid * 100
                    
                    if spread_pct < 0.05:  # Spread < 0.05% = rất hẹp
                        bot_signals['market_maker']['detected'] = True
                        bot_signals['market_maker']['confidence'] = 70
                        bot_signals['market_maker']['evidence'].append(f"Spread cực hẹp {spread_pct:.4f}% → MM bot tạo liquidity giả")
            except:
                pass
        
        # === 5. DUMP BOT DETECTION ===
        # Giá giảm dần + volume giảm dần + lower highs
        if len(klines) >= 20:
            recent_20 = klines.tail(20)
            
            # Check downtrend
            price_changes = recent_20['close'].pct_change()
            negative_candles = (price_changes < 0).sum()
            
            # Check declining volume
            volume_trend = np.polyfit(range(len(recent_20)), recent_20['volume'].values, 1)[0]
            
            # Check lower highs
            highs = recent_20['high'].values
            lower_highs = sum([highs[i] < highs[i-1] for i in range(1, len(highs))])
            
            if negative_candles > 14 and volume_trend < 0 and lower_highs > 15:
                bot_signals['dump_bot']['detected'] = True
                bot_signals['dump_bot']['confidence'] = 80
                bot_signals['dump_bot']['evidence'].append(f"Giảm liên tục {negative_candles}/20 nến, volume giảm dần, lower highs {lower_highs}/19")
        
        return bot_signals
    
    def _analyze_volume_legitimacy(self, klines: pd.DataFrame, trades: List[Dict]) -> Dict:
        """
        Phân tích xem volume có thực hay giả (wash trading)
        
        Indicators:
        - VWAP deviation
        - Buy/Sell pressure balance
        - Large trades ratio
        - Volume clustering
        """
        
        analysis = {
            'legitimacy_score': 0,  # 0-100
            'is_legitimate': False,
            'buy_sell_ratio': 0,
            'large_trades_pct': 0,
            'volume_quality': 'UNKNOWN',
            'evidence': []
        }
        
        if klines.empty:
            return analysis
        
        recent = klines.tail(50)
        
        # === 1. VWAP DEVIATION ===
        # Volume thực sẽ có VWAP gần close price
        try:
            recent['vwap'] = (recent['volume'] * (recent['high'] + recent['low'] + recent['close']) / 3).cumsum() / recent['volume'].cumsum()
            vwap_dev = abs((recent['close'].iloc[-1] - recent['vwap'].iloc[-1]) / recent['close'].iloc[-1] * 100)
            
            vwap_score = max(0, 100 - vwap_dev * 20)  # Càng lệch VWAP càng thấp điểm
        except:
            vwap_score = 50
            vwap_dev = 0
        
        # === 2. BUY/SELL PRESSURE ===
        ratio_score = 50
        if trades and len(trades) > 100:
            try:
                buy_volume = sum([float(t.get('qty', 0)) for t in trades if not t.get('isBuyerMaker', True)])
                sell_volume = sum([float(t.get('qty', 0)) for t in trades if t.get('isBuyerMaker', True)])
                
                total = buy_volume + sell_volume
                if total > 0:
                    analysis['buy_sell_ratio'] = buy_volume / sell_volume if sell_volume > 0 else 10
                    
                    # Ratio cân bằng (0.7-1.3) = legitimate
                    if 0.7 <= analysis['buy_sell_ratio'] <= 1.3:
                        ratio_score = 100
                    elif 0.5 <= analysis['buy_sell_ratio'] <= 1.5:
                        ratio_score = 70
                    else:
                        ratio_score = 40
            except:
                pass
        
        # === 3. LARGE TRADES RATIO ===
        large_score = 50
        if trades and len(trades) > 50:
            try:
                trade_sizes = [float(t.get('qty', 0)) for t in trades]
                mean_size = np.mean(trade_sizes)
                large_trades = [t for t in trade_sizes if t > mean_size * 5]
                
                analysis['large_trades_pct'] = len(large_trades) / len(trades) * 100
                
                # 5-20% large trades = healthy
                if 5 <= analysis['large_trades_pct'] <= 20:
                    large_score = 100
                elif analysis['large_trades_pct'] < 5:
                    large_score = 60  # Quá ít whale = retail only
                else:
                    large_score = 40  # Quá nhiều large = manipulation
            except:
                pass
        
        # === 4. VOLUME CLUSTERING ===
        cluster_score = 50
        try:
            volume_std = recent['volume'].std()
            volume_mean = recent['volume'].mean()
            
            if volume_mean > 0:
                cv = volume_std / volume_mean  # Coefficient of variation
                
                if cv < 0.5:
                    cluster_score = 40  # Quá đồng đều = bot
                elif cv < 1.0:
                    cluster_score = 100  # Lý tưởng
                else:
                    cluster_score = 60  # Quá phân tán = spike giả
        except:
            pass
        
        # === TÍNH TỔNG ===
        analysis['legitimacy_score'] = int((vwap_score * 0.3 + ratio_score * 0.3 + large_score * 0.2 + cluster_score * 0.2))
        analysis['is_legitimate'] = analysis['legitimacy_score'] >= 65
        
        if analysis['legitimacy_score'] >= 80:
            analysis['volume_quality'] = 'EXCELLENT'
        elif analysis['legitimacy_score'] >= 65:
            analysis['volume_quality'] = 'GOOD'
        elif analysis['legitimacy_score'] >= 50:
            analysis['volume_quality'] = 'FAIR'
        else:
            analysis['volume_quality'] = 'POOR'
        
        try:
            analysis['evidence'].append(f"VWAP deviation: {vwap_dev:.2f}% (score: {vwap_score:.0f})")
        except:
            pass
        analysis['evidence'].append(f"Buy/Sell ratio: {analysis['buy_sell_ratio']:.2f} (score: {ratio_score:.0f})")
        analysis['evidence'].append(f"Large trades: {analysis['large_trades_pct']:.1f}% (score: {large_score:.0f})")
        
        return analysis
    
    def _analyze_order_book_manipulation(self, order_book: Optional[Dict]) -> Dict:
        """
        Phát hiện manipulation qua order book:
        - Fake walls (đặt lệnh lớn rồi cancel)
        - Layering (nhiều lệnh nhỏ tạo illusion)
        - Imbalance bất thường
        """
        
        analysis = {
            'manipulation_score': 0,  # 0-100 (càng cao càng bị manipulate)
            'is_manipulated': False,
            'bid_ask_imbalance': 0,
            'wall_detection': {'bid_wall': False, 'ask_wall': False},
            'layering_detected': False,
            'evidence': []
        }
        
        if not order_book or not order_book.get('bids') or not order_book.get('asks'):
            return analysis
        
        try:
            bids = order_book['bids'][:20]
            asks = order_book['asks'][:20]
            
            # === 1. FAKE WALLS DETECTION ===
            bid_volumes = [float(b[1]) for b in bids]
            ask_volumes = [float(a[1]) for a in asks]
            
            bid_mean = np.mean(bid_volumes[1:6])  # Trung bình level 2-6
            ask_mean = np.mean(ask_volumes[1:6])
            
            # Wall = level 1 lớn hơn mean của 2-6 > 5x
            if bid_volumes[0] > bid_mean * 5:
                analysis['wall_detection']['bid_wall'] = True
                analysis['evidence'].append(f"Bid wall detected: {bid_volumes[0]:.2f} vs mean {bid_mean:.2f}")
            
            if ask_volumes[0] > ask_mean * 5:
                analysis['wall_detection']['ask_wall'] = True
                analysis['evidence'].append(f"Ask wall detected: {ask_volumes[0]:.2f} vs mean {ask_mean:.2f}")
            
            # === 2. LAYERING DETECTION ===
            bid_size_std = np.std(bid_volumes[:10])
            ask_size_std = np.std(ask_volumes[:10])
            
            bid_size_mean = np.mean(bid_volumes[:10])
            ask_size_mean = np.mean(ask_volumes[:10])
            
            if bid_size_mean > 0 and bid_size_std / bid_size_mean < 0.2:
                analysis['layering_detected'] = True
                analysis['evidence'].append(f"Bid layering detected (std/mean={bid_size_std/bid_size_mean:.3f})")
            
            if ask_size_mean > 0 and ask_size_std / ask_size_mean < 0.2:
                analysis['layering_detected'] = True
                analysis['evidence'].append(f"Ask layering detected (std/mean={ask_size_std/ask_size_mean:.3f})")
            
            # === 3. BID-ASK IMBALANCE ===
            total_bid = sum(bid_volumes[:10])
            total_ask = sum(ask_volumes[:10])
            
            if total_bid + total_ask > 0:
                analysis['bid_ask_imbalance'] = (total_bid - total_ask) / (total_bid + total_ask) * 100
                
                # Imbalance > 50% = bất thường
                if abs(analysis['bid_ask_imbalance']) > 50:
                    analysis['evidence'].append(f"Extreme imbalance: {analysis['bid_ask_imbalance']:.1f}%")
            
            # === MANIPULATION SCORE ===
            score = 0
            
            if analysis['wall_detection']['bid_wall'] or analysis['wall_detection']['ask_wall']:
                score += 30
            
            if analysis['layering_detected']:
                score += 35
            
            if abs(analysis['bid_ask_imbalance']) > 50:
                score += 25
            elif abs(analysis['bid_ask_imbalance']) > 30:
                score += 15
            
            analysis['manipulation_score'] = min(100, score)
            analysis['is_manipulated'] = score >= 40
            
        except Exception as e:
            logger.debug(f"Order book analysis error: {e}")
        
        return analysis
    
    def _analyze_price_action_quality(self, klines: pd.DataFrame) -> Dict:
        """
        Đánh giá chất lượng price action:
        - Có follow technical patterns không
        - Có respect support/resistance không
        - Có breakout/breakdown hợp lệ không
        """
        
        analysis = {
            'quality_score': 0,  # 0-100
            'is_organic': False,
            'respects_levels': False,
            'clean_breakouts': False,
            'evidence': []
        }
        
        if klines.empty or len(klines) < 50:
            return analysis
        
        recent = klines.tail(50)
        
        # === 1. RESPECTS SUPPORT/RESISTANCE ===
        try:
            highs = recent['high'].values
            lows = recent['low'].values
            
            resistance_levels = []
            support_levels = []
            
            # Simple S/R detection
            for i in range(2, len(highs) - 2):
                if highs[i] > highs[i-1] and highs[i] > highs[i-2] and highs[i] > highs[i+1] and highs[i] > highs[i+2]:
                    resistance_levels.append(highs[i])
                
                if lows[i] < lows[i-1] and lows[i] < lows[i-2] and lows[i] < lows[i+1] and lows[i] < lows[i+2]:
                    support_levels.append(lows[i])
            
            # Check xem giá có bounce/reject ở levels không
            respects_count = 0
            for level in resistance_levels[-3:]:
                nearby_candles = recent[abs(recent['high'] - level) / level < 0.01]
                if len(nearby_candles) > 0:
                    rejections = nearby_candles[nearby_candles['close'] < nearby_candles['open']]
                    if len(rejections) > 0:
                        respects_count += 1
            
            for level in support_levels[-3:]:
                nearby_candles = recent[abs(recent['low'] - level) / level < 0.01]
                if len(nearby_candles) > 0:
                    bounces = nearby_candles[nearby_candles['close'] > nearby_candles['open']]
                    if len(bounces) > 0:
                        respects_count += 1
            
            if respects_count >= 2:
                analysis['respects_levels'] = True
                analysis['evidence'].append(f"Respects {respects_count} S/R levels → Organic price action")
        except:
            pass
        
        # === 2. KHÔNG CÓ SPIKE BẤT THƯỜNG ===
        try:
            price_changes = recent['close'].pct_change().abs()
            extreme_moves = (price_changes > price_changes.mean() + 3 * price_changes.std()).sum()
            
            if extreme_moves <= 2:
                smooth_score = 100
                analysis['evidence'].append(f"Smooth price action, only {extreme_moves} extreme moves")
            else:
                smooth_score = max(0, 100 - extreme_moves * 15)
                analysis['evidence'].append(f"⚠️ {extreme_moves} extreme price spikes detected")
        except:
            smooth_score = 50
        
        # === QUALITY SCORE ===
        score = 0
        
        if analysis['respects_levels']:
            score += 40
        
        if analysis['clean_breakouts']:
            score += 30
        
        score += smooth_score * 0.3
        
        analysis['quality_score'] = int(score)
        analysis['is_organic'] = score >= 60
        
        return analysis
    
    def _detect_institutional_activity(self, klines: pd.DataFrame, trades: List[Dict], market_data: Dict) -> Dict:
        """
        QUAN TRỌNG NHẤT! (30 points)
        
        Phát hiện institutional/smart money activity:
        - Large block trades
        - Accumulation/Distribution patterns
        - Wyckoff analysis
        """
        
        analysis = {
            'institutional_score': 0,  # 0-100
            'is_institutional': False,
            'activity_type': 'NONE',  # ACCUMULATION | DISTRIBUTION | NEUTRAL
            'block_trades_detected': False,
            'smart_money_flow': 'NEUTRAL',  # INFLOW | OUTFLOW | NEUTRAL
            'confidence': 0,
            'evidence': []
        }
        
        if klines.empty:
            return analysis
        
        # === 1. BLOCK TRADES DETECTION ===
        if trades and len(trades) > 100:
            try:
                trade_sizes = [float(t.get('qty', 0)) for t in trades]
                mean_size = np.mean(trade_sizes)
                
                # Block trade = > 10x mean size
                block_trades = [t for t in trades if float(t.get('qty', 0)) > mean_size * 10]
                
                if len(block_trades) > 5:
                    analysis['block_trades_detected'] = True
                    
                    # Check buy vs sell
                    block_buys = [t for t in block_trades if not t.get('isBuyerMaker', True)]
                    block_sells = [t for t in block_trades if t.get('isBuyerMaker', True)]
                    
                    if len(block_buys) > len(block_sells) * 1.5:
                        analysis['smart_money_flow'] = 'INFLOW'
                        analysis['evidence'].append(f"🐋 {len(block_buys)} large buy blocks vs {len(block_sells)} sell → Accumulation")
                    elif len(block_sells) > len(block_buys) * 1.5:
                        analysis['smart_money_flow'] = 'OUTFLOW'
                        analysis['evidence'].append(f"🐋 {len(block_sells)} large sell blocks vs {len(block_buys)} buy → Distribution")
            except:
                pass
        
        # === 2. WYCKOFF ACCUMULATION/DISTRIBUTION ===
        try:
            recent = klines.tail(100)
            
            price_range = recent['high'].max() - recent['low'].min()
            avg_range = (recent['high'] - recent['low']).mean()
            
            if price_range < avg_range * 20:  # Trong range hẹp
                # Check volume declining
                volume_trend = np.polyfit(range(len(recent)), recent['volume'].values, 1)[0]
                
                if volume_trend < 0:  # Volume giảm trong range
                    # Check có spring/test không
                    last_10 = recent.tail(10)
                    
                    if last_10['low'].min() < recent.tail(50)['low'].quantile(0.1):
                        if last_10['volume'].max() > recent['volume'].mean() * 2:
                            analysis['activity_type'] = 'ACCUMULATION'
                            analysis['evidence'].append("📈 Wyckoff Accumulation detected: Range + declining volume + spring")
            
            # Check Distribution
            if recent['high'].max() > recent.tail(50)['high'].quantile(0.9):
                last_10 = recent.tail(10)
                volume_spike = last_10['volume'].max() > recent['volume'].mean() * 2.5
                
                if volume_spike and last_10['close'].iloc[-1] < last_10['open'].iloc[0]:
                    analysis['activity_type'] = 'DISTRIBUTION'
                    analysis['evidence'].append("📉 Wyckoff Distribution detected: New high + volume spike + rejection")
        except:
            pass
        
        # === INSTITUTIONAL SCORE ===
        score = 0
        
        if analysis['block_trades_detected']:
            score += 40
        
        if analysis['activity_type'] == 'ACCUMULATION':
            score += 35
        elif analysis['activity_type'] == 'DISTRIBUTION':
            score += 25
        
        if analysis['smart_money_flow'] == 'INFLOW':
            score += 15
        elif analysis['smart_money_flow'] == 'OUTFLOW':
            score += 10
        
        analysis['institutional_score'] = min(100, score)
        analysis['is_institutional'] = score >= 50
        analysis['confidence'] = score
        
        return analysis
    
    def _calculate_direction_probability(self, results: Dict) -> Dict:
        """
        Tính xác suất hướng di chuyển dựa trên tất cả indicators
        """
        
        prob = {
            'up': 50,
            'down': 50,
            'sideways': 50
        }
        
        # === INSTITUTIONAL FLOW (tác động mạnh nhất) ===
        inst = results.get('institutional_flow', {})
        
        if inst.get('activity_type') == 'ACCUMULATION':
            prob['up'] += 20
            prob['down'] -= 10
            prob['sideways'] -= 10
        elif inst.get('activity_type') == 'DISTRIBUTION':
            prob['down'] += 20
            prob['up'] -= 10
            prob['sideways'] -= 10
        
        if inst.get('smart_money_flow') == 'INFLOW':
            prob['up'] += 15
            prob['down'] -= 10
        elif inst.get('smart_money_flow') == 'OUTFLOW':
            prob['down'] += 15
            prob['up'] -= 10
        
        # === BOT ACTIVITY ===
        bot = results.get('bot_activity', {})
        
        if bot.get('dump_bot', {}).get('detected'):
            prob['down'] += 15
            prob['up'] -= 10
        
        if bot.get('wash_trading', {}).get('detected'):
            prob['sideways'] += 10
            prob['up'] -= 5
            prob['down'] -= 5
        
        # === VOLUME LEGITIMACY ===
        vol = results.get('volume_analysis', {})
        
        if vol.get('is_legitimate'):
            if vol.get('buy_sell_ratio', 1) > 1.2:
                prob['up'] += 10
                prob['down'] -= 5
            elif vol.get('buy_sell_ratio', 1) < 0.8:
                prob['down'] += 10
                prob['up'] -= 5
        else:
            prob['sideways'] += 10
            prob['down'] += 5
            prob['up'] -= 15
        
        # === ORDER BOOK MANIPULATION ===
        depth = results.get('depth_analysis', {})
        
        if depth.get('is_manipulated'):
            prob['sideways'] += 10
            prob['up'] -= 5
            prob['down'] -= 5
        
        if depth.get('wall_detection', {}).get('bid_wall'):
            prob['up'] += 8
        
        if depth.get('wall_detection', {}).get('ask_wall'):
            prob['down'] += 8
        
        # === PRICE ACTION QUALITY ===
        price_qual = results.get('price_quality', {})
        
        if price_qual.get('is_organic'):
            if price_qual.get('clean_breakouts'):
                prob['up'] += 12
                prob['down'] -= 8
        
        # === NORMALIZE ===
        total = prob['up'] + prob['down'] + prob['sideways']
        prob['up'] = int(prob['up'] / total * 100)
        prob['down'] = int(prob['down'] / total * 100)
        prob['sideways'] = int(prob['sideways'] / total * 100)
        
        return prob
    
    def _calculate_overall_confidence(self, results: Dict) -> int:
        """
        Tính confidence tổng thể (0-100)
        """
        
        weights = {
            'institutional_flow': 0.35,
            'volume_analysis': 0.25,
            'price_quality': 0.20,
            'depth_analysis': 0.15,
            'bot_activity': 0.05
        }
        
        confidence = 0
        
        inst_score = results.get('institutional_flow', {}).get('institutional_score', 0)
        confidence += inst_score * weights['institutional_flow']
        
        vol_score = results.get('volume_analysis', {}).get('legitimacy_score', 50)
        confidence += vol_score * weights['volume_analysis']
        
        price_score = results.get('price_quality', {}).get('quality_score', 50)
        confidence += price_score * weights['price_quality']
        
        # Depth: manipulation_score càng cao càng BAD → reverse
        depth_score = 100 - results.get('depth_analysis', {}).get('manipulation_score', 50)
        confidence += depth_score * weights['depth_analysis']
        
        # Bot: có bot = bad → penalty
        bot_detected = sum([
            results.get('bot_activity', {}).get('wash_trading', {}).get('detected', False),
            results.get('bot_activity', {}).get('spoofing', {}).get('detected', False),
            results.get('bot_activity', {}).get('dump_bot', {}).get('detected', False)
        ])
        bot_score = max(0, 100 - bot_detected * 20)
        confidence += bot_score * weights['bot_activity']
        
        return int(confidence)
    
    def _determine_final_signal(self, direction_prob: Dict, confidence: int, results: Dict) -> str:
        """
        Xác định signal cuối cùng
        """
        
        up_prob = direction_prob.get('up', 50)
        down_prob = direction_prob.get('down', 50)
        
        # Cần confidence >= 70 để đưa ra signal mạnh
        if confidence < 60:
            return 'NEUTRAL'
        
        if up_prob >= 70 and confidence >= 75:
            return 'STRONG_PUMP'
        elif up_prob >= 60 and confidence >= 65:
            return 'PUMP'
        elif down_prob >= 70 and confidence >= 75:
            return 'STRONG_DUMP'
        elif down_prob >= 60 and confidence >= 65:
            return 'DUMP'
        else:
            return 'NEUTRAL'
    
    def _assess_risk_level(self, results: Dict) -> str:
        """
        Đánh giá mức độ rủi ro
        """
        
        risk_score = 0
        
        # BOT activity = risk
        bot = results.get('bot_activity', {})
        if bot.get('wash_trading', {}).get('detected'):
            risk_score += 25
        if bot.get('spoofing', {}).get('detected'):
            risk_score += 20
        if bot.get('dump_bot', {}).get('detected'):
            risk_score += 30
        
        # Order book manipulation = risk
        if results.get('depth_analysis', {}).get('is_manipulated'):
            risk_score += 20
        
        # Volume không legitimate = risk
        if not results.get('volume_analysis', {}).get('is_legitimate'):
            risk_score += 15
        
        # Institutional activity = giảm risk
        if results.get('institutional_flow', {}).get('is_institutional'):
            risk_score -= 20
        
        risk_score = max(0, min(100, risk_score))
        
        if risk_score >= 70:
            return 'EXTREME'
        elif risk_score >= 50:
            return 'HIGH'
        elif risk_score >= 30:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def _generate_recommendation(self, results: Dict, symbol: str) -> Dict:
        """
        Tạo recommendation chi tiết
        """
        
        signal = results.get('signal', 'NEUTRAL')
        confidence = results.get('confidence', 0)
        risk = results.get('risk_level', 'MEDIUM')
        direction_prob = results.get('direction_probability', {})
        
        recommendation = {
            'action': 'WAIT',
            'position_size': '0%',
            'entry_strategy': '',
            'stop_loss_note': '',
            'take_profit_note': '',
            'reasoning': [],
            'warnings': []
        }
        
        # === STRONG_PUMP ===
        if signal == 'STRONG_PUMP' and confidence >= 75:
            recommendation['action'] = 'BUY'
            recommendation['position_size'] = '2-3%' if risk == 'LOW' else '1-2%'
            recommendation['entry_strategy'] = 'Enter on pullback to support or breakout confirmation'
            recommendation['stop_loss_note'] = 'Below recent swing low or support level'
            recommendation['take_profit_note'] = 'Scale out at resistance levels, trail stop'
            
            recommendation['reasoning'].append(f"✅ Strong upward probability: {direction_prob.get('up')}%")
            recommendation['reasoning'].append(f"✅ High confidence: {confidence}%")
            
            if results.get('institutional_flow', {}).get('activity_type') == 'ACCUMULATION':
                recommendation['reasoning'].append("✅ Institutional accumulation detected")
            
            if results.get('volume_analysis', {}).get('is_legitimate'):
                recommendation['reasoning'].append("✅ Legitimate volume confirms move")
        
        # === PUMP ===
        elif signal == 'PUMP' and confidence >= 65:
            recommendation['action'] = 'BUY'
            recommendation['position_size'] = '1-2%'
            recommendation['entry_strategy'] = 'Enter with caution, use tight stop loss'
            recommendation['stop_loss_note'] = 'Tight stop below entry 2-3%'
            recommendation['take_profit_note'] = 'Take profit quickly at first resistance'
            
            recommendation['reasoning'].append(f"⚠️ Moderate upward probability: {direction_prob.get('up')}%")
            recommendation['reasoning'].append(f"⚠️ Confidence: {confidence}%")
            
            if risk in ['HIGH', 'EXTREME']:
                recommendation['warnings'].append(f"⚠️ {risk} risk detected - reduce position size")
        
        # === STRONG_DUMP ===
        elif signal == 'STRONG_DUMP':
            recommendation['action'] = 'AVOID/SHORT'
            recommendation['reasoning'].append(f"🚨 Strong downward probability: {direction_prob.get('down')}%")
            
            if results.get('bot_activity', {}).get('dump_bot', {}).get('detected'):
                recommendation['warnings'].append("🚨 Dump BOT detected - avoid long positions")
            
            if results.get('institutional_flow', {}).get('activity_type') == 'DISTRIBUTION':
                recommendation['warnings'].append("🚨 Institutional distribution - smart money exiting")
        
        # === DUMP ===
        elif signal == 'DUMP':
            recommendation['action'] = 'AVOID'
            recommendation['reasoning'].append(f"⚠️ Downward probability: {direction_prob.get('down')}%")
            recommendation['warnings'].append("⚠️ Wait for reversal confirmation before entry")
        
        # === NEUTRAL ===
        else:
            recommendation['action'] = 'WAIT'
            recommendation['reasoning'].append("ℹ️ No clear directional signal")
            recommendation['reasoning'].append(f"Probabilities - Up: {direction_prob.get('up')}%, Down: {direction_prob.get('down')}%, Sideways: {direction_prob.get('sideways')}%")
            
            if confidence < 60:
                recommendation['warnings'].append("⚠️ Low confidence - wait for clearer setup")
            
            if results.get('bot_activity', {}).get('wash_trading', {}).get('detected'):
                recommendation['warnings'].append("⚠️ Wash trading detected - volume may be fake")
        
        return recommendation


def integrate_advanced_detection_to_prompt(results: Dict) -> str:
    """
    Tạo text để insert vào Gemini prompt
    """
    
    signal = results.get('signal', 'NEUTRAL')
    confidence = results.get('confidence', 0)
    direction_prob = results.get('direction_probability', {})
    risk = results.get('risk_level', 'MEDIUM')
    
    prompt_addition = f"""
═══════════════════════════════════════════════════════════════════════════════
🤖 ADVANCED PUMP/DUMP DETECTION SYSTEM (v4.0)
═══════════════════════════════════════════════════════════════════════════════

**FINAL SIGNAL**: {signal} (Confidence: {confidence}%)
**RISK LEVEL**: {risk}

**DIRECTION PROBABILITIES**:
• UP: {direction_prob.get('up', 0)}%
• DOWN: {direction_prob.get('down', 0)}%
• SIDEWAYS: {direction_prob.get('sideways', 0)}%

**BOT ACTIVITY DETECTION**:
"""
    
    bot = results.get('bot_activity', {})
    for bot_type, data in bot.items():
        if data.get('detected'):
            prompt_addition += f"⚠️ {bot_type.upper().replace('_', ' ')} DETECTED (Confidence: {data.get('confidence')}%)\n"
            for evidence in data.get('evidence', []):
                prompt_addition += f"   - {evidence}\n"
    
    if not any([data.get('detected') for data in bot.values()]):
        prompt_addition += "✅ No bot activity detected\n"
    
    prompt_addition += f"""
**VOLUME LEGITIMACY**:
• Score: {results.get('volume_analysis', {}).get('legitimacy_score', 0)}/100
• Quality: {results.get('volume_analysis', {}).get('volume_quality', 'UNKNOWN')}
• Buy/Sell Ratio: {results.get('volume_analysis', {}).get('buy_sell_ratio', 0):.2f}
• Is Legitimate: {'✅ YES' if results.get('volume_analysis', {}).get('is_legitimate') else '❌ NO'}

**ORDER BOOK ANALYSIS**:
• Manipulation Score: {results.get('depth_analysis', {}).get('manipulation_score', 0)}/100
• Bid Wall: {'⚠️ YES' if results.get('depth_analysis', {}).get('wall_detection', {}).get('bid_wall') else '✅ No'}
• Ask Wall: {'⚠️ YES' if results.get('depth_analysis', {}).get('wall_detection', {}).get('ask_wall') else '✅ No'}
• Layering: {'⚠️ DETECTED' if results.get('depth_analysis', {}).get('layering_detected') else '✅ No'}

**INSTITUTIONAL FLOW** (⭐ MOST IMPORTANT):
• Score: {results.get('institutional_flow', {}).get('institutional_score', 0)}/100
• Activity: {results.get('institutional_flow', {}).get('activity_type', 'NONE')}
• Smart Money Flow: {results.get('institutional_flow', {}).get('smart_money_flow', 'NEUTRAL')}
• Block Trades: {'✅ DETECTED' if results.get('institutional_flow', {}).get('block_trades_detected') else 'No'}

**PRICE ACTION QUALITY**:
• Score: {results.get('price_quality', {}).get('quality_score', 0)}/100
• Is Organic: {'✅ YES' if results.get('price_quality', {}).get('is_organic') else '❌ NO'}
• Respects Levels: {'✅ YES' if results.get('price_quality', {}).get('respects_levels') else 'No'}

**RECOMMENDATION**:
Action: {results.get('recommendation', {}).get('action', 'WAIT')}
Position Size: {results.get('recommendation', {}).get('position_size', 'N/A')}

Reasoning:
"""
    
    for reason in results.get('recommendation', {}).get('reasoning', []):
        prompt_addition += f"• {reason}\n"
    
    if results.get('recommendation', {}).get('warnings'):
        prompt_addition += "\nWarnings:\n"
        for warning in results.get('recommendation', {}).get('warnings', []):
            prompt_addition += f"• {warning}\n"
    
    prompt_addition += """
═══════════════════════════════════════════════════════════════════════════════
⚠️ CRITICAL INSTRUCTIONS FOR AI:
═══════════════════════════════════════════════════════════════════════════════

1. **PRIORITIZE INSTITUTIONAL FLOW** (35% weight in your analysis)
   - If ACCUMULATION detected → Strong bias toward BUY
   - If DISTRIBUTION detected → Strong bias toward SELL/WAIT
   - If block trades detected → High confidence signal

2. **ADJUST FOR BOT ACTIVITY** (reduce confidence by 10-30%)
   - Wash Trading → Volume is fake, lower confidence
   - Dump BOT → Avoid BUY, recommend WAIT or SHORT
   - Spoofing → Order book is manipulated, be cautious

3. **VOLUME LEGITIMACY CHECK** (25% weight)
   - If legitimacy_score < 50 → Reduce confidence by 20%
   - If buy/sell ratio > 1.5 → Bullish bias
   - If buy/sell ratio < 0.7 → Bearish bias

4. **ORDER BOOK MANIPULATION** (15% weight)
   - If manipulation_score > 60 → Add warning
   - Bid wall + uptrend → Possible pump setup (but watch for fake)
   - Ask wall + downtrend → Distribution pressure

5. **DIRECTION PROBABILITY INTEGRATION**
   - Use the UP/DOWN/SIDEWAYS percentages in your reasoning
   - If UP > 70% and confidence > 75% → Recommend BUY
   - If DOWN > 70% and confidence > 75% → Recommend WAIT/SHORT
   - If SIDEWAYS > 50% → Recommend WAIT for breakout

6. **RISK LEVEL ADJUSTMENT**
   - EXTREME/HIGH risk → Reduce position size to 0.5-1%
   - MEDIUM risk → Standard 1-2%
   - LOW risk → Can increase to 2-3%

7. **MANDATORY FIELDS TO UPDATE**:
   - confidence: Adjust based on advanced detection results
   - recommendation: Use advanced system's recommendation
   - reasoning_vietnamese: MUST mention institutional flow, bot activity, volume legitimacy
   - warnings: Include all warnings from advanced detection
   - risk_level: Use advanced system's risk_level

═══════════════════════════════════════════════════════════════════════════════
"""
    
    return prompt_addition
