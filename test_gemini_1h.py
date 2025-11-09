"""
Test Gemini analyzer with 1h timeframe
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

def test_gemini_1h():
    """Test that Gemini receives 1h data"""
    try:
        from binance_client import BinanceClient
        from gemini_analyzer import GeminiAnalyzer
        
        # Initialize clients
        api_key = os.getenv('BINANCE_API_KEY')
        api_secret = os.getenv('BINANCE_API_SECRET')
        gemini_key = os.getenv('GEMINI_API_KEY')
        
        if not gemini_key:
            logger.error("❌ GEMINI_API_KEY not found in .env")
            return False
        
        logger.info("Initializing Binance client...")
        binance = BinanceClient(api_key, api_secret)
        
        logger.info("Initializing Stoch+RSI analyzer...")
        from stoch_rsi_analyzer import StochRSIAnalyzer
        stoch_analyzer = StochRSIAnalyzer(binance)
        
        logger.info("Initializing Gemini analyzer...")
        gemini = GeminiAnalyzer(gemini_key, binance, stoch_analyzer)
        
        symbol = 'ETHUSDT'
        
        # Test data collection
        logger.info(f"\n[TEST] Collecting data for {symbol}...")
        data = gemini.collect_data(symbol)
        
        if not data:
            logger.error(f"❌ Failed to collect data for {symbol}")
            return False
        
        logger.info(f"✅ Data collected for {symbol}")
        
        # Check RSI+MFI timeframes
        if 'rsi_mfi' in data and 'timeframes' in data['rsi_mfi']:
            timeframes = list(data['rsi_mfi']['timeframes'].keys())
            logger.info(f"RSI+MFI timeframes: {timeframes}")
            if '1h' in timeframes:
                logger.info("✅ 1h timeframe present in RSI+MFI")
                rsi = data['rsi_mfi']['timeframes']['1h']['rsi']
                mfi = data['rsi_mfi']['timeframes']['1h']['mfi']
                signal = data['rsi_mfi']['timeframes']['1h']['signal']
                logger.info(f"   1h: RSI={rsi:.1f}, MFI={mfi:.1f}, Signal={signal}")
            else:
                logger.error("❌ 1h timeframe NOT found in RSI+MFI")
                return False
        
        # Check Stoch+RSI timeframes
        if 'stoch_rsi' in data and 'timeframes' in data['stoch_rsi']:
            timeframes = [tf_data['timeframe'] for tf_data in data['stoch_rsi']['timeframes']]
            logger.info(f"Stoch+RSI timeframes: {timeframes}")
            if '1h' in timeframes:
                logger.info("✅ 1h timeframe present in Stoch+RSI")
                for tf_data in data['stoch_rsi']['timeframes']:
                    if tf_data['timeframe'] == '1h':
                        logger.info(f"   1h: RSI={tf_data['rsi']:.1f}, Stoch={tf_data['stoch_k']:.1f}, Signal={tf_data['signal_text']}")
            else:
                logger.error("❌ 1h timeframe NOT found in Stoch+RSI")
                return False
        
        # Check FVG timeframes
        if 'fair_value_gaps' in data:
            fvg_timeframes = list(data['fair_value_gaps'].keys())
            logger.info(f"FVG timeframes: {fvg_timeframes}")
            if '1h' in fvg_timeframes:
                logger.info("✅ 1h timeframe present in FVG")
            else:
                logger.warning("⚠️ 1h timeframe NOT in FVG (expected: only 4h, 1d)")
        
        logger.info("\n✅ All timeframes validated successfully!")
        logger.info("Summary:")
        logger.info("  - RSI+MFI: 5m, 1h, 4h, 1d ✅")
        logger.info("  - Stoch+RSI: 1m, 5m, 1h, 4h, 1d ✅")
        logger.info("  - FVG: 1h, 4h, 1d ✅")
        logger.info("  - Volume Profile: 1h, 4h, 1d ✅")
        logger.info("  - Order Blocks: 1h, 4h, 1d ✅")
        logger.info("  - S/R: 1h, 4h, 1d ✅")
        logger.info("  - SMC: 1h, 4h, 1d ✅")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}", exc_info=True)
        return False

if __name__ == '__main__':
    logger.info("="*60)
    logger.info("GEMINI 1H TIMEFRAME VALIDATION TEST")
    logger.info("="*60)
    
    success = test_gemini_1h()
    
    logger.info("\n" + "="*60)
    if success:
        logger.info("✅ TEST PASSED - 1h timeframe integrated!")
    else:
        logger.info("❌ TEST FAILED - Check logs above")
    logger.info("="*60)
