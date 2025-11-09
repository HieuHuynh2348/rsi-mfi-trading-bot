"""
Quick test script to debug Gemini analyzer
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

def test_gemini_basic():
    """Test basic Gemini API connection"""
    try:
        import google.generativeai as genai
        
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            logger.error("❌ GEMINI_API_KEY not found in .env")
            return False
        
        logger.info(f"✓ API Key loaded: {api_key[:20]}...")
        
        # Configure Gemini
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        logger.info("✓ Gemini model initialized")
        
        # Test simple prompt
        logger.info("Testing simple prompt...")
        response = model.generate_content("Say 'Hello from Gemini!'")
        
        if response and response.text:
            logger.info(f"✅ Gemini response: {response.text}")
            return True
        else:
            logger.error("❌ Empty response from Gemini")
            return False
            
    except Exception as e:
        logger.error(f"❌ Test failed: {e}", exc_info=True)
        return False

def test_gemini_with_binance():
    """Test full pipeline with Binance data"""
    try:
        from binance_client import BinanceClient
        from stoch_rsi_analyzer import StochRSIAnalyzer
        from gemini_analyzer import GeminiAnalyzer
        
        logger.info("Initializing Binance client...")
        binance = BinanceClient()
        
        logger.info("Initializing StochRSI analyzer...")
        stoch_rsi = StochRSIAnalyzer(binance)
        
        logger.info("Initializing Gemini analyzer...")
        api_key = os.getenv('GEMINI_API_KEY')
        gemini = GeminiAnalyzer(api_key, binance, stoch_rsi)
        
        logger.info("✓ All components initialized")
        
        # Test data collection
        symbol = 'ETHUSDT'
        logger.info(f"\nTesting data collection for {symbol}...")
        data = gemini.collect_data(symbol)
        
        if not data:
            logger.error(f"❌ Failed to collect data for {symbol}")
            return False
        
        logger.info(f"✅ Data collected successfully for {symbol}")
        logger.info(f"   - Market price: ${data['market_data']['price']:,.2f}")
        logger.info(f"   - RSI/MFI available: {data['rsi_mfi'] is not None}")
        logger.info(f"   - Stoch+RSI available: {data['stoch_rsi'] is not None}")
        logger.info(f"   - Volume Profile: {data['volume_profile'] is not None}")
        logger.info(f"   - Fair Value Gaps: {data['fair_value_gaps'] is not None}")
        logger.info(f"   - Order Blocks: {data['order_blocks'] is not None}")
        logger.info(f"   - S/R Zones: {data['support_resistance'] is not None}")
        logger.info(f"   - Smart Money: {data['smart_money_concepts'] is not None}")
        
        # Test full analysis
        logger.info(f"\nTesting full Gemini analysis for {symbol}...")
        analysis = gemini.analyze(symbol, use_cache=False)
        
        if not analysis:
            logger.error(f"❌ Failed to analyze {symbol}")
            return False
        
        logger.info(f"✅ Analysis complete for {symbol}")
        logger.info(f"   - Recommendation: {analysis['recommendation']}")
        logger.info(f"   - Confidence: {analysis['confidence']}%")
        logger.info(f"   - Entry: ${analysis['entry_point']:,.2f}")
        logger.info(f"   - Stop Loss: ${analysis['stop_loss']:,.2f}")
        logger.info(f"   - Take Profit: {analysis['take_profit']}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}", exc_info=True)
        return False

if __name__ == '__main__':
    logger.info("="*60)
    logger.info("GEMINI ANALYZER TEST")
    logger.info("="*60)
    
    logger.info("\n[1/2] Testing basic Gemini API connection...")
    basic_ok = test_gemini_basic()
    
    if basic_ok:
        logger.info("\n[2/2] Testing full pipeline with Binance data...")
        full_ok = test_gemini_with_binance()
        
        if full_ok:
            logger.info("\n" + "="*60)
            logger.info("✅ ALL TESTS PASSED")
            logger.info("="*60)
        else:
            logger.info("\n" + "="*60)
            logger.info("❌ FULL PIPELINE TEST FAILED")
            logger.info("="*60)
    else:
        logger.info("\n" + "="*60)
        logger.info("❌ BASIC API TEST FAILED - Check API key")
        logger.info("="*60)
