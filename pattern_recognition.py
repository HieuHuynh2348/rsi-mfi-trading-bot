"""
Pattern Recognition Module - Cross-Symbol and Market Regime Detection
Enhances AI analysis with universal patterns and market condition awareness
"""

import logging
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
from collections import defaultdict

logger = logging.getLogger(__name__)


class PatternRecognizer:
    """
    Detects recurring patterns across symbols and market regimes
    """
    
    def __init__(self, database):
        """
        Initialize pattern recognizer
        
        Args:
            database: AnalysisDatabase instance
        """
        self.db = database
        logger.info("✅ Pattern Recognizer initialized")
    
    def detect_cross_symbol_patterns(self, user_id: int, days: int = 30) -> Dict:
        """
        Find patterns that work across multiple symbols
        
        Returns:
            {
                'universal_patterns': [
                    {
                        'condition': 'RSI 25-35 + VP DISCOUNT + BULLISH OB',
                        'symbols': ['BTCUSDT', 'ETHUSDT', 'BNBUSDT'],
                        'win_rate': 78.5,
                        'sample_size': 34
                    }
                ]
            }
        """
        try:
            if not self.db:
                return {'universal_patterns': []}
            
            # Get all history for user (limit is removed, function doesn't support it)
            history = self.db.get_all_history(user_id, days=days)
            
            if len(history) < 10:
                logger.info(f"Insufficient data for pattern detection: {len(history)} analyses")
                return {'universal_patterns': []}
            
            # Group by conditions
            patterns = defaultdict(lambda: {
                'symbols': set(),
                'wins': 0,
                'total': 0,
                'win_rate': 0
            })
            
            for analysis in history:
                result = analysis.get('tracking_result', {})
                if result.get('result') not in ['WIN', 'LOSS']:
                    continue
                
                snapshot = analysis.get('market_snapshot', {})
                symbol = analysis.get('symbol')
                
                # Extract key conditions
                condition = self._extract_conditions(snapshot)
                if not condition:
                    continue
                
                patterns[condition]['symbols'].add(symbol)
                patterns[condition]['total'] += 1
                if result.get('result') == 'WIN':
                    patterns[condition]['wins'] += 1
            
            # Calculate win rates and filter for universal patterns
            universal_patterns = []
            
            for condition, data in patterns.items():
                if data['total'] >= 5:  # Minimum sample size
                    win_rate = (data['wins'] / data['total']) * 100
                    data['win_rate'] = win_rate
                    
                    # Universal = works on 3+ symbols with 60%+ win rate
                    if len(data['symbols']) >= 3 and win_rate >= 60:
                        universal_patterns.append({
                            'condition': condition,
                            'symbols': list(data['symbols']),
                            'win_rate': round(win_rate, 1),
                            'sample_size': data['total']
                        })
            
            # Sort by win rate
            universal_patterns.sort(key=lambda x: x['win_rate'], reverse=True)
            
            logger.info(f"Found {len(universal_patterns)} universal patterns for user {user_id}")
            return {'universal_patterns': universal_patterns[:10]}  # Top 10
            
        except Exception as e:
            logger.error(f"Error detecting cross-symbol patterns: {e}")
            return {'universal_patterns': []}
    
    def _extract_conditions(self, snapshot: Dict) -> Optional[str]:
        """
        Extract key conditions from market snapshot
        
        Returns:
            Condition string like "RSI 25-35 + VP DISCOUNT + BULLISH OB"
        """
        try:
            conditions = []
            
            # RSI zones
            rsi = snapshot.get('rsi')
            if rsi:
                if rsi <= 20:
                    conditions.append('RSI OVERSOLD')
                elif 20 < rsi <= 35:
                    conditions.append('RSI LOW (20-35)')
                elif 65 <= rsi < 80:
                    conditions.append('RSI HIGH (65-80)')
                elif rsi >= 80:
                    conditions.append('RSI OVERBOUGHT')
            
            # MFI zones
            mfi = snapshot.get('mfi')
            if mfi:
                if mfi <= 20:
                    conditions.append('MFI OVERSOLD')
                elif mfi >= 80:
                    conditions.append('MFI OVERBOUGHT')
            
            # Volume Profile
            vp = snapshot.get('volume_profile', {})
            if vp.get('current_price_zone'):
                conditions.append(f"VP {vp['current_price_zone']}")
            
            # Order Blocks
            ob = snapshot.get('order_blocks', {})
            if ob.get('nearest_bullish') or ob.get('nearest_bearish'):
                if ob.get('nearest_bullish'):
                    conditions.append('BULLISH OB')
                if ob.get('nearest_bearish'):
                    conditions.append('BEARISH OB')
            
            # Smart Money Concepts
            smc = snapshot.get('smart_money', {})
            if smc.get('bos_detected'):
                conditions.append(f"BOS {smc.get('bos_type', 'N/A')}")
            if smc.get('choch_detected'):
                conditions.append('CHOCH')
            
            return ' + '.join(conditions) if conditions else None
            
        except Exception as e:
            logger.error(f"Error extracting conditions: {e}")
            return None


class MarketRegimeDetector:
    """
    Classifies market into BULL, BEAR, or SIDEWAYS regime
    """
    
    def __init__(self, binance_client):
        """
        Initialize market regime detector
        
        Args:
            binance_client: BinanceClient instance
        """
        self.binance = binance_client
        logger.info("✅ Market Regime Detector initialized")
    
    def detect_regime(self, symbol: str, timeframe: str = '1h') -> Dict:
        """
        Detect current market regime
        
        Returns:
            {
                'regime': 'BULL' | 'BEAR' | 'SIDEWAYS',
                'confidence': 0.0 - 1.0,
                'metrics': {
                    'ema_trend': 'UP' | 'DOWN' | 'FLAT',
                    'volatility': 'HIGH' | 'NORMAL' | 'LOW',
                    'volume': 'INCREASING' | 'DECREASING' | 'STABLE'
                }
            }
        """
        try:
            # Get klines (last 100 candles)
            klines = self.binance.get_klines(symbol, timeframe, limit=100)
            if klines is None or (hasattr(klines, '__len__') and len(klines) == 0):
                return self._default_regime()
            
            closes = [float(k[4]) for k in klines]
            volumes = [float(k[5]) for k in klines]
            
            # 1. EMA Trend (20, 50, 200)
            ema_20 = self._calculate_ema(closes, 20)
            ema_50 = self._calculate_ema(closes, 50)
            ema_200 = self._calculate_ema(closes, 200) if len(closes) >= 200 else None
            
            current_price = closes[-1]
            
            # Determine EMA trend
            if ema_200:
                if current_price > ema_20 > ema_50 > ema_200:
                    ema_trend = 'UP'
                    trend_score = 1.0
                elif current_price < ema_20 < ema_50 < ema_200:
                    ema_trend = 'DOWN'
                    trend_score = 0.0
                else:
                    ema_trend = 'FLAT'
                    trend_score = 0.5
            else:
                if current_price > ema_20 > ema_50:
                    ema_trend = 'UP'
                    trend_score = 0.8
                elif current_price < ema_20 < ema_50:
                    ema_trend = 'DOWN'
                    trend_score = 0.2
                else:
                    ema_trend = 'FLAT'
                    trend_score = 0.5
            
            # 2. Volatility (ATR-based)
            atr = self._calculate_atr(klines, 14)
            avg_price = sum(closes[-20:]) / 20
            volatility_pct = (atr / avg_price) * 100
            
            if volatility_pct > 3:
                volatility = 'HIGH'
            elif volatility_pct > 1.5:
                volatility = 'NORMAL'
            else:
                volatility = 'LOW'
            
            # 3. Volume Trend
            recent_vol = sum(volumes[-10:]) / 10
            older_vol = sum(volumes[-30:-10]) / 20
            
            vol_change = ((recent_vol - older_vol) / older_vol) * 100
            
            if vol_change > 20:
                volume_trend = 'INCREASING'
            elif vol_change < -20:
                volume_trend = 'DECREASING'
            else:
                volume_trend = 'STABLE'
            
            # Determine regime
            if trend_score >= 0.7:
                regime = 'BULL'
                confidence = min(trend_score + (0.1 if volume_trend == 'INCREASING' else 0), 1.0)
            elif trend_score <= 0.3:
                regime = 'BEAR'
                confidence = min((1 - trend_score) + (0.1 if volume_trend == 'INCREASING' else 0), 1.0)
            else:
                regime = 'SIDEWAYS'
                confidence = 1 - abs(trend_score - 0.5) * 2
            
            return {
                'regime': regime,
                'confidence': round(confidence, 2),
                'metrics': {
                    'ema_trend': ema_trend,
                    'volatility': volatility,
                    'volume': volume_trend
                }
            }
            
        except Exception as e:
            logger.error(f"Error detecting market regime: {e}")
            return self._default_regime()
    
    def _calculate_ema(self, prices: List[float], period: int) -> float:
        """Calculate Exponential Moving Average"""
        if len(prices) < period:
            return sum(prices) / len(prices)
        
        multiplier = 2 / (period + 1)
        ema = sum(prices[:period]) / period
        
        for price in prices[period:]:
            ema = (price - ema) * multiplier + ema
        
        return ema
    
    def _calculate_atr(self, klines: List, period: int = 14) -> float:
        """Calculate Average True Range"""
        if len(klines) < period + 1:
            return 0
        
        true_ranges = []
        
        for i in range(1, len(klines)):
            high = float(klines[i][2])
            low = float(klines[i][3])
            prev_close = float(klines[i-1][4])
            
            tr = max(
                high - low,
                abs(high - prev_close),
                abs(low - prev_close)
            )
            true_ranges.append(tr)
        
        return sum(true_ranges[-period:]) / period
    
    def _default_regime(self) -> Dict:
        """Return default regime when detection fails"""
        return {
            'regime': 'SIDEWAYS',
            'confidence': 0.5,
            'metrics': {
                'ema_trend': 'FLAT',
                'volatility': 'NORMAL',
                'volume': 'STABLE'
            }
        }


def get_pattern_context(db, binance_client, user_id: int, symbol: str) -> Dict:
    """
    Get comprehensive pattern recognition and regime context
    
    Returns:
        {
            'universal_patterns': [...],
            'market_regime': {...},
            'recommendations': [...]
        }
    """
    try:
        # Initialize recognizers
        pattern_recognizer = PatternRecognizer(db)
        regime_detector = MarketRegimeDetector(binance_client)
        
        # Detect patterns and regime
        patterns = pattern_recognizer.detect_cross_symbol_patterns(user_id, days=30)
        regime = regime_detector.detect_regime(symbol, timeframe='1h')
        
        # Generate recommendations based on regime
        recommendations = []
        
        if regime['regime'] == 'BULL' and regime['confidence'] >= 0.7:
            recommendations.append("🟢 BULL market: Favor BUY signals, use tighter stops")
            recommendations.append("Focus on breakout entries above resistance")
        elif regime['regime'] == 'BEAR' and regime['confidence'] >= 0.7:
            recommendations.append("🔴 BEAR market: Favor SELL signals or WAIT for reversal")
            recommendations.append("Look for breakdown entries below support")
        else:
            recommendations.append("🟡 SIDEWAYS market: Range trading strategy recommended")
            recommendations.append("Buy support, sell resistance, tight stops")
        
        return {
            'universal_patterns': patterns.get('universal_patterns', []),
            'market_regime': regime,
            'recommendations': recommendations
        }
        
    except Exception as e:
        logger.error(f"Error getting pattern context: {e}")
        return {
            'universal_patterns': [],
            'market_regime': {'regime': 'UNKNOWN', 'confidence': 0},
            'recommendations': []
        }
