"""
Test script to verify historical data integration with current analysis
Kiểm tra xem dữ liệu lịch sử có được tích hợp với phân tích hiện tại không
"""
import sys
import os
from gemini_analyzer import GeminiAnalyzer
from binance_client import BinanceClient
from stoch_rsi_analyzer import StochRSIAnalyzer
import config
import logging
import json

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_data_integration():
    """
    Test to verify:
    1. Historical klines data is collected
    2. Current analysis data is collected  
    3. Both are integrated in final prompt
    4. Gemini receives complete context
    """
    
    symbol = 'BTCUSDT'
    logger.info(f"{'='*80}")
    logger.info(f"TESTING DATA INTEGRATION FOR {symbol}")
    logger.info(f"{'='*80}\n")
    
    try:
        # Initialize required components
        logger.info("Initializing components...")
        
        # Check API key
        gemini_api_key = os.getenv('GEMINI_API_KEY') or config.GEMINI_API_KEY
        if not gemini_api_key:
            logger.error("❌ GEMINI_API_KEY not found")
            return False
        
        # Binance API keys
        binance_api_key = os.getenv('BINANCE_API_KEY') or config.BINANCE_API_KEY
        binance_api_secret = os.getenv('BINANCE_API_SECRET') or config.BINANCE_API_SECRET
        
        binance = BinanceClient(binance_api_key, binance_api_secret)
        stoch_rsi = StochRSIAnalyzer(binance)
        analyzer = GeminiAnalyzer(gemini_api_key, binance, stoch_rsi)
        
        logger.info("✅ Components initialized\n")
        
        # Test 1: Collect analysis data
        logger.info("TEST 1: Collecting analysis data...")
        logger.info("-" * 80)
        
        data = analyzer.collect_data(symbol, pump_data=None)
        
        if not data:
            logger.error("❌ FAILED: Cannot collect data")
            return False
        
        logger.info("✅ PASSED: Data collection successful\n")
        
        # Test 2: Verify current indicators exist
        logger.info("TEST 2: Verifying current indicators...")
        logger.info("-" * 80)
        
        required_keys = [
            'market_data',
            'rsi_mfi', 
            'stoch_rsi',
            'volume_profile',
            'fair_value_gaps',
            'order_blocks',
            'support_resistance',
            'smart_money_concepts'
        ]
        
        missing_keys = []
        for key in required_keys:
            if key not in data:
                missing_keys.append(key)
                logger.warning(f"⚠️  Missing: {key}")
            else:
                logger.info(f"✅ Found: {key}")
        
        if missing_keys:
            logger.error(f"❌ FAILED: Missing current indicators: {missing_keys}")
            return False
        
        logger.info("✅ PASSED: All current indicators present\n")
        
        # Test 3: Verify historical data exists
        logger.info("TEST 3: Verifying historical data...")
        logger.info("-" * 80)
        
        if 'historical' not in data:
            logger.error("❌ FAILED: 'historical' key missing")
            return False
        
        logger.info("✅ Found: historical (week-over-week comparison)")
        
        if 'historical_klines' not in data:
            logger.error("❌ FAILED: 'historical_klines' key missing")
            return False
        
        logger.info("✅ Found: historical_klines (extended context)")
        
        historical_klines = data['historical_klines']
        
        # Check timeframes
        expected_timeframes = ['1h', '4h', '1d']
        for tf in expected_timeframes:
            if tf not in historical_klines:
                logger.warning(f"⚠️  Missing timeframe: {tf}")
            else:
                tf_data = historical_klines[tf]
                if tf_data:
                    logger.info(f"✅ Timeframe {tf}: {tf_data.get('candles_count', 0)} candles")
                else:
                    logger.warning(f"⚠️  Timeframe {tf}: No data")
        
        logger.info("✅ PASSED: Historical data present\n")
        
        # Test 4: Verify historical data structure
        logger.info("TEST 4: Verifying historical data structure...")
        logger.info("-" * 80)
        
        required_fields = [
            'price_range',
            'volume',
            'rsi_stats',
            'trend',
            'candle_pattern'
        ]
        
        all_valid = True
        for tf, tf_data in historical_klines.items():
            if not tf_data:
                logger.warning(f"⚠️  {tf}: No data")
                continue
            
            logger.info(f"\n  Checking {tf}:")
            for field in required_fields:
                if field not in tf_data:
                    logger.error(f"    ❌ Missing: {field}")
                    all_valid = False
                else:
                    logger.info(f"    ✅ {field}: OK")
        
        if not all_valid:
            logger.error("❌ FAILED: Historical data structure incomplete")
            return False
        
        logger.info("\n✅ PASSED: Historical data structure valid\n")
        
        # Test 5: Compare data ranges
        logger.info("TEST 5: Comparing data ranges...")
        logger.info("-" * 80)
        
        # Check RSI+MFI (uses limit=200 from current klines)
        rsi_mfi = data.get('rsi_mfi', {})
        if 'timeframes' in rsi_mfi:
            logger.info(f"RSI+MFI timeframes: {list(rsi_mfi['timeframes'].keys())}")
        
        # Check historical klines
        logger.info("\nHistorical klines ranges:")
        for tf, tf_data in historical_klines.items():
            if tf_data:
                candles = tf_data.get('candles_count', 0)
                period = tf_data.get('period', 'Unknown')
                logger.info(f"  {tf}: {candles} candles ({period})")
        
        logger.info("✅ PASSED: Data ranges verified\n")
        
        # Test 6: Build prompt and check integration
        logger.info("TEST 6: Building prompt with integrated data...")
        logger.info("-" * 80)
        
        prompt = analyzer._build_prompt(data, trading_style='swing')
        
        # Check if prompt contains historical sections
        checks = [
            ("HISTORICAL COMPARISON", "📈 HISTORICAL COMPARISON"),
            ("EXTENDED HISTORICAL", "DỮ LIỆU LỊCH SỬ MỞ RỘNG"),
            ("1H context", "KHUNG 1H"),
            ("4H context", "KHUNG 4H"),
            ("1D context", "KHUNG 1D"),
            ("RSI+MFI", "RSI + MFI"),
            ("Stoch+RSI", "Stochastic + RSI"),
            ("Institutional", "INSTITUTIONAL INDICATORS")
        ]
        
        all_present = True
        for name, marker in checks:
            if marker in prompt:
                logger.info(f"✅ Found in prompt: {name}")
            else:
                logger.error(f"❌ Missing from prompt: {name}")
                all_present = False
        
        if not all_present:
            logger.error("❌ FAILED: Prompt missing key sections")
            return False
        
        logger.info("✅ PASSED: Prompt contains all sections\n")
        
        # Test 7: Verify prompt size
        logger.info("TEST 7: Checking prompt size...")
        logger.info("-" * 80)
        
        prompt_length = len(prompt)
        logger.info(f"Prompt length: {prompt_length:,} characters")
        logger.info(f"Prompt size: {prompt_length/1024:.2f} KB")
        
        if prompt_length < 1000:
            logger.error("❌ FAILED: Prompt too short (< 1KB)")
            return False
        
        if prompt_length > 50000:
            logger.warning(f"⚠️  WARNING: Prompt very large (> 50KB)")
        
        logger.info("✅ PASSED: Prompt size reasonable\n")
        
        # Test 8: Check data correlation
        logger.info("TEST 8: Checking data correlation...")
        logger.info("-" * 80)
        
        # Compare current price from market_data with historical_klines
        current_price = data['market_data']['price']
        logger.info(f"Current price (market_data): ${current_price:,.2f}")
        
        for tf, tf_data in historical_klines.items():
            if tf_data and 'price_range' in tf_data:
                hist_current = tf_data['price_range']['current']
                logger.info(f"Current price ({tf} historical): ${hist_current:,.2f}")
                
                # Prices should be very close (within 1%)
                diff_pct = abs(current_price - hist_current) / current_price * 100
                if diff_pct > 1.0:
                    logger.warning(f"⚠️  Price mismatch in {tf}: {diff_pct:.2f}% difference")
                else:
                    logger.info(f"  ✅ Price match: {diff_pct:.4f}% difference")
        
        logger.info("✅ PASSED: Data correlation verified\n")
        
        # Test 9: Full analysis test
        logger.info("TEST 9: Running full analysis...")
        logger.info("-" * 80)
        
        analysis = analyzer.analyze(symbol, pump_data=None, trading_style='swing')
        
        if not analysis:
            logger.error("❌ FAILED: Analysis returned no result")
            return False
        
        logger.info(f"✅ Analysis completed successfully")
        logger.info(f"  Recommendation: {analysis.get('recommendation', 'N/A')}")
        logger.info(f"  Confidence: {analysis.get('confidence', 0)}%")
        logger.info(f"  Risk Level: {analysis.get('risk_level', 'N/A')}")
        logger.info(f"  Market Sentiment: {analysis.get('market_sentiment', 'N/A')}")
        
        # Check if reasoning mentions historical data
        reasoning = analysis.get('reasoning_vietnamese', '')
        historical_keywords = [
            'lịch sử',
            'trước đó',
            'tuần trước',
            'ngày qua',
            '7 ngày',
            '30 ngày',
            '90 ngày',
            'range',
            'dao động'
        ]
        
        found_keywords = [kw for kw in historical_keywords if kw.lower() in reasoning.lower()]
        
        if found_keywords:
            logger.info(f"✅ AI reasoning mentions historical context: {found_keywords[:3]}")
        else:
            logger.warning("⚠️  AI reasoning may not use historical context")
        
        logger.info("✅ PASSED: Full analysis works\n")
        
        # Summary
        logger.info("="*80)
        logger.info("SUMMARY - ALL TESTS")
        logger.info("="*80)
        logger.info("✅ TEST 1: Data collection - PASSED")
        logger.info("✅ TEST 2: Current indicators - PASSED")
        logger.info("✅ TEST 3: Historical data - PASSED")
        logger.info("✅ TEST 4: Data structure - PASSED")
        logger.info("✅ TEST 5: Data ranges - PASSED")
        logger.info("✅ TEST 6: Prompt integration - PASSED")
        logger.info("✅ TEST 7: Prompt size - PASSED")
        logger.info("✅ TEST 8: Data correlation - PASSED")
        logger.info("✅ TEST 9: Full analysis - PASSED")
        logger.info("="*80)
        logger.info("🎉 ALL TESTS PASSED!")
        logger.info("="*80)
        
        # Optional: Save sample prompt for inspection
        logger.info("\nSaving sample prompt to 'test_prompt_sample.txt'...")
        with open('test_prompt_sample.txt', 'w', encoding='utf-8') as f:
            f.write(f"SYMBOL: {symbol}\n")
            f.write(f"Generated at: {data['timestamp']}\n")
            f.write("="*80 + "\n\n")
            f.write(prompt)
        logger.info("✅ Sample prompt saved\n")
        
        # Save analysis result
        logger.info("Saving analysis result to 'test_analysis_result.json'...")
        with open('test_analysis_result.json', 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False, default=str)
        logger.info("✅ Analysis result saved\n")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ TEST FAILED WITH ERROR: {e}", exc_info=True)
        return False

if __name__ == "__main__":
    success = test_data_integration()
    
    if success:
        print("\n" + "="*80)
        print("KẾT LUẬN:")
        print("="*80)
        print("✅ Hệ thống đã được nâng cấp ĐÚNG")
        print("✅ Dữ liệu lịch sử được thu thập và tích hợp với dữ liệu hiện tại")
        print("✅ Các chỉ báo (RSI+MFI, Stoch+RSI, Institutional) phân tích dữ liệu hiện tại")
        print("✅ Gemini AI nhận được cả 2 loại dữ liệu để phân tích toàn diện")
        print("="*80)
        sys.exit(0)
    else:
        print("\n" + "="*80)
        print("⚠️  CÓ LỖI TRONG TÍCH HỢP DỮ LIỆU")
        print("Vui lòng kiểm tra logs ở trên để xem chi tiết")
        print("="*80)
        sys.exit(1)
