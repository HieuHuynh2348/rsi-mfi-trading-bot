#!/usr/bin/env python3
"""
Quick test for Gemini AI analysis with unified data collection
"""

import asyncio
import logging
import sys
from binance_client import BinanceClient
from gemini_analyzer import GeminiAnalyzer
from stoch_rsi_analyzer import StochRSIAnalyzer
import config

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

async def test_analysis():
    """Test AI analysis with real symbol"""
    
    try:
        # Initialize components
        logger.info("🔧 Initializing components...")
        binance = BinanceClient(config.BINANCE_API_KEY, config.BINANCE_API_SECRET)
        stoch_rsi = StochRSIAnalyzer(binance)
        
        # Get Gemini API key from environment
        import os
        gemini_key = os.getenv('GEMINI_API_KEY')
        if not gemini_key:
            logger.error("❌ GEMINI_API_KEY not found in environment variables")
            logger.info("💡 Please set GEMINI_API_KEY in .env file")
            return
        
        analyzer = GeminiAnalyzer(gemini_key, binance, stoch_rsi)
        
        # Test symbol
        symbol = 'BTCUSDT'
        logger.info(f"\n{'='*60}")
        logger.info(f"🔍 Testing AI Analysis for {symbol}")
        logger.info(f"{'='*60}\n")
        
        # Collect data
        logger.info("📊 Collecting market data...")
        data = analyzer.collect_data(symbol)  # Not async
        
        # Verify data structure
        logger.info("\n✅ Data Collection Summary:")
        logger.info(f"  Symbol: {data.get('symbol')}")
        logger.info(f"  Timestamp: {data.get('timestamp')}")
        
        # Check klines
        klines = data.get('klines', {})
        logger.info(f"\n📈 Klines Data (used by all indicators):")
        for tf, df in klines.items():
            if df is not None and not df.empty:
                logger.info(f"  {tf.upper()}: {len(df)} candles")
        
        # Check historical context
        historical = data.get('historical_klines', {})
        logger.info(f"\n📜 Historical Context (analyzed for AI):")
        for tf, stats in historical.items():
            if stats:
                logger.info(f"  {tf.upper()}: {stats.get('candles_count')} candles analyzed")
                logger.info(f"    Period: {stats.get('period')}")
                price_range = stats.get('price_range', {})
                logger.info(f"    Price Range: ${price_range.get('low'):.2f} - ${price_range.get('high'):.2f}")
        
        # Verify consistency
        logger.info(f"\n🔍 Data Consistency Check:")
        for tf in ['1h', '4h', '1d']:
            if tf in klines and tf in historical:
                klines_count = len(klines[tf])
                hist_count = historical[tf].get('candles_count', 0)
                match = "✅" if klines_count == hist_count else "❌"
                logger.info(f"  {tf.upper()}: indicators={klines_count}, historical={hist_count} {match}")
        
        # Run AI analysis
        logger.info(f"\n🤖 Running Gemini AI Analysis...")
        analysis = analyzer.analyze(symbol)  # Returns dict
        
        if analysis and isinstance(analysis, dict):
            logger.info(f"\n{'='*60}")
            logger.info("✅ AI ANALYSIS RESULT:")
            logger.info(f"{'='*60}")
            logger.info(f"Recommendation: {analysis.get('recommendation', 'N/A')}")
            logger.info(f"Confidence: {analysis.get('confidence', 0)}%")
            logger.info(f"Timeframe: {analysis.get('timeframe', 'N/A')}")
            logger.info(f"\nFormatted Response:")
            print(analysis.get('formatted_response', 'No formatted response'))
            logger.info(f"{'='*60}")
            logger.info("✅ Test completed successfully!")
        else:
            logger.error(f"\n❌ Analysis failed or returned unexpected format")
            
    except Exception as e:
        logger.error(f"❌ Error during test: {e}", exc_info=True)

if __name__ == '__main__':
    asyncio.run(test_analysis())
