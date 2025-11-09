"""
Test script to debug ZBTUSDT chart generation
"""

import logging
import os
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment
load_dotenv()

def test_zbtusdt_chart():
    """Test chart generation for ZBTUSDT"""
    try:
        from binance_client import BinanceClient
        from chart_generator import ChartGenerator
        
        # Initialize clients
        api_key = os.getenv('BINANCE_API_KEY')
        api_secret = os.getenv('BINANCE_API_SECRET')
        
        logger.info("Initializing Binance client...")
        binance = BinanceClient(api_key, api_secret)
        
        logger.info("Initializing chart generator...")
        chart_gen = ChartGenerator()
        
        symbol = 'ZBTUSDT'
        
        # Test 1: Check if symbol exists
        logger.info(f"\n[TEST 1] Checking if {symbol} exists...")
        symbols = binance.get_all_usdt_symbols()
        if symbol in symbols:
            logger.info(f"✅ {symbol} exists in Binance")
        else:
            logger.error(f"❌ {symbol} NOT found in Binance")
            logger.info(f"Available symbols starting with Z: {[s for s in symbols if s.startswith('Z')]}")
            return False
        
        # Test 2: Get klines data
        logger.info(f"\n[TEST 2] Fetching klines for {symbol}...")
        klines = binance.get_klines(symbol, '1h', limit=100)
        
        if klines is None or klines.empty:
            logger.error(f"❌ No klines data for {symbol}")
            return False
        
        logger.info(f"✅ Got {len(klines)} candles for {symbol}")
        logger.info(f"Columns: {list(klines.columns)}")
        logger.info(f"First row:\n{klines.iloc[0]}")
        logger.info(f"Last row:\n{klines.iloc[-1]}")
        
        # Test 3: Generate chart
        logger.info(f"\n[TEST 3] Generating chart for {symbol}...")
        chart_path = chart_gen.generate_chart_with_indicators(
            symbol=symbol,
            df=klines,
            rsi_period=14,
            mfi_period=14,
            timeframe='1h'
        )
        
        if not chart_path:
            logger.error(f"❌ Failed to generate chart for {symbol}")
            return False
        
        if not os.path.exists(chart_path):
            logger.error(f"❌ Chart file not found: {chart_path}")
            return False
        
        file_size = os.path.getsize(chart_path)
        logger.info(f"✅ Chart generated successfully!")
        logger.info(f"   Path: {chart_path}")
        logger.info(f"   Size: {file_size:,} bytes")
        
        # Clean up
        os.remove(chart_path)
        logger.info(f"✅ Cleaned up temp file")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}", exc_info=True)
        return False

if __name__ == '__main__':
    logger.info("="*60)
    logger.info("ZBTUSDT CHART GENERATION TEST")
    logger.info("="*60)
    
    success = test_zbtusdt_chart()
    
    logger.info("\n" + "="*60)
    if success:
        logger.info("✅ ALL TESTS PASSED - ZBTUSDT chart works!")
    else:
        logger.info("❌ TEST FAILED - Check logs above")
    logger.info("="*60)
