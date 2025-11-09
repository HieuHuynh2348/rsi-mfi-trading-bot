"""
Test script for historical klines context enhancement
Tests the new _get_historical_klines_context() function
"""
import sys
import asyncio
from gemini_analyzer import GeminiAnalyzer
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_historical_klines():
    """Test historical klines context for a symbol"""
    
    symbol = 'BTCUSDT'
    logger.info(f"Testing historical klines context for {symbol}...")
    
    try:
        # Initialize analyzer
        analyzer = GeminiAnalyzer()
        
        # Test _get_historical_klines_context
        logger.info("=" * 60)
        logger.info("Testing _get_historical_klines_context()...")
        logger.info("=" * 60)
        
        historical_klines = analyzer._get_historical_klines_context(symbol)
        
        if not historical_klines:
            logger.error("❌ No historical klines data returned")
            return False
        
        # Print results
        logger.info(f"\n✅ Historical klines context retrieved for {len(historical_klines)} timeframes")
        
        for tf, data in historical_klines.items():
            logger.info(f"\n{'='*60}")
            logger.info(f"Timeframe: {tf.upper()}")
            logger.info(f"{'='*60}")
            
            if not data:
                logger.warning(f"⚠️ No data for {tf}")
                continue
            
            logger.info(f"Period: {data.get('period', 'N/A')}")
            logger.info(f"Candles: {data.get('candles_count', 0)}")
            
            # Price info
            if 'price_range' in data:
                pr = data['price_range']
                logger.info(f"\n📈 Price Range:")
                logger.info(f"  High: ${pr['high']:,.4f}")
                logger.info(f"  Low: ${pr['low']:,.4f}")
                logger.info(f"  Current: ${pr['current']:,.4f}")
                logger.info(f"  Range: {pr['range_pct']:.2f}%")
                logger.info(f"  Position: {pr['position_in_range_pct']:.1f}% of range")
            
            # Volume info
            if 'volume' in data:
                vol = data['volume']
                logger.info(f"\n📊 Volume:")
                logger.info(f"  Average: {vol['average']:,.0f}")
                logger.info(f"  Current: {vol['current']:,.0f}")
                logger.info(f"  Ratio: {vol['current_vs_avg_ratio']:.2f}x")
                logger.info(f"  Trend: {vol['trend']}")
            
            # RSI info
            if 'rsi_stats' in data:
                rsi = data['rsi_stats']
                logger.info(f"\n🎯 RSI:")
                logger.info(f"  Average: {rsi['average']:.1f}")
                logger.info(f"  Current: {rsi['current']:.1f}")
                logger.info(f"  Range: {rsi['min']:.1f} - {rsi['max']:.1f}")
            
            # Trend info
            if 'trend' in data:
                trend = data['trend']
                logger.info(f"\n📉 Trend:")
                logger.info(f"  Direction: {trend['direction']}")
                logger.info(f"  Change: {trend['change_pct']:+.2f}%")
                logger.info(f"  Volatility: {trend['volatility_pct']:.2f}%")
            
            # Candle pattern
            if 'candle_pattern' in data:
                pattern = data['candle_pattern']
                logger.info(f"\n🕯️ Candle Pattern:")
                logger.info(f"  Bullish: {pattern['bullish_candles']}")
                logger.info(f"  Bearish: {pattern['bearish_candles']}")
                logger.info(f"  Bullish Ratio: {pattern['bullish_ratio_pct']:.1f}%")
        
        # Test full analysis with historical context
        logger.info(f"\n{'='*60}")
        logger.info("Testing full analysis with historical context...")
        logger.info(f"{'='*60}")
        
        result = await analyzer.analyze_symbol(symbol, trading_style='swing')
        
        if result and 'result' in result:
            analysis = result['result']
            logger.info(f"\n✅ Full analysis completed:")
            logger.info(f"  Recommendation: {analysis.get('recommendation', 'N/A')}")
            logger.info(f"  Confidence: {analysis.get('confidence', 0)}%")
            logger.info(f"  Risk Level: {analysis.get('risk_level', 'N/A')}")
            logger.info(f"  Market Sentiment: {analysis.get('market_sentiment', 'N/A')}")
            
            # Check if historical_klines is in the data
            if 'data' in result and 'historical_klines' in result['data']:
                logger.info(f"\n✅ Historical klines context included in analysis data")
            else:
                logger.warning(f"\n⚠️ Historical klines context NOT found in analysis data")
        else:
            logger.error("❌ Full analysis failed")
            return False
        
        logger.info(f"\n{'='*60}")
        logger.info("✅ All tests passed!")
        logger.info(f"{'='*60}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}", exc_info=True)
        return False

if __name__ == "__main__":
    success = asyncio.run(test_historical_klines())
    sys.exit(0 if success else 1)
