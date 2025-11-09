#!/usr/bin/env python3
"""
Test WebApp Integration
Tests Flask API endpoints and chart functionality
"""

import sys
import os
import time
import requests
import json
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all required modules can be imported"""
    print("🔍 Testing imports...")
    try:
        from binance_client import BinanceClient
        from indicators import calculate_rsi, calculate_mfi, calculate_hlcc4
        import config
        print("  ✅ All imports successful")
        return True
    except Exception as e:
        print(f"  ❌ Import error: {e}")
        return False

def test_binance_connection():
    """Test Binance client connection"""
    print("\n🔍 Testing Binance connection...")
    try:
        from binance_client import BinanceClient
        import config
        
        binance = BinanceClient(config.BINANCE_API_KEY, config.BINANCE_API_SECRET)
        
        # Test getting ticker using actual client method
        ticker = binance.client.get_ticker(symbol='BTCUSDT')
        if ticker and 'lastPrice' in ticker:
            print(f"  ✅ Connected! BTC price: ${float(ticker['lastPrice']):,.2f}")
            return True
        else:
            print("  ❌ Could not get ticker data")
            return False
    except Exception as e:
        print(f"  ❌ Connection error: {e}")
        return False

def test_chart_data_generation():
    """Test generating chart data"""
    print("\n🔍 Testing chart data generation...")
    try:
        from binance_client import BinanceClient
        from indicators import calculate_rsi, calculate_mfi, calculate_hlcc4
        import config
        
        binance = BinanceClient(config.BINANCE_API_KEY, config.BINANCE_API_SECRET)
        
        # Get klines
        symbol = 'BTCUSDT'
        timeframe = '1h'
        df = binance.get_klines(symbol, timeframe, limit=100)
        
        if df is None or df.empty:
            print(f"  ❌ No klines data for {symbol}")
            return False
        
        print(f"  ✅ Got {len(df)} candles for {symbol}")
        
        # Calculate indicators
        hlcc4 = calculate_hlcc4(df)
        df['rsi'] = calculate_rsi(hlcc4, 14)
        df['mfi'] = calculate_mfi(df, 14)
        
        latest_rsi = float(df['rsi'].iloc[-1])
        latest_mfi = float(df['mfi'].iloc[-1])
        
        print(f"  ✅ RSI: {latest_rsi:.2f}")
        print(f"  ✅ MFI: {latest_mfi:.2f}")
        
        # Format for chart
        candles = []
        for idx, row in df.iterrows():
            # Use index as timestamp (DataFrame index is datetime)
            if hasattr(idx, 'timestamp'):
                time_val = int(idx.timestamp())
            else:
                # Fallback
                time_val = int(time.time())
            
            candles.append({
                'time': time_val,
                'open': float(row['open']),
                'high': float(row['high']),
                'low': float(row['low']),
                'close': float(row['close']),
                'volume': float(row['volume'])
            })
        
        print(f"  ✅ Formatted {len(candles)} candles for chart")
        
        return True
    except Exception as e:
        print(f"  ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_flask_app_startup():
    """Test Flask app can start"""
    print("\n🔍 Testing Flask app startup...")
    try:
        # Import the app
        sys.path.insert(0, 'webapp')
        from app import app, binance
        
        if binance is None:
            print("  ⚠️ Warning: Binance client not initialized in app")
        else:
            print("  ✅ Binance client initialized in Flask app")
        
        print("  ✅ Flask app can be imported")
        return True
    except Exception as e:
        print(f"  ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_webapp_files_exist():
    """Test that WebApp files exist"""
    print("\n🔍 Testing WebApp files...")
    
    files = {
        'webapp/app.py': 'Flask API backend',
        'webapp/chart.html': 'Chart frontend',
    }
    
    all_exist = True
    for filepath, description in files.items():
        if os.path.exists(filepath):
            size = os.path.getsize(filepath)
            print(f"  ✅ {filepath} ({size:,} bytes) - {description}")
        else:
            print(f"  ❌ {filepath} NOT FOUND - {description}")
            all_exist = False
    
    return all_exist

def test_config():
    """Test configuration"""
    print("\n🔍 Testing configuration...")
    try:
        import config
        
        checks = {
            'BINANCE_API_KEY': config.BINANCE_API_KEY,
            'BINANCE_API_SECRET': config.BINANCE_API_SECRET,
            'TELEGRAM_BOT_TOKEN': config.TELEGRAM_BOT_TOKEN,
            'WEBAPP_URL': config.WEBAPP_URL,
        }
        
        all_ok = True
        for key, value in checks.items():
            if value:
                masked = value[:10] + '...' if len(value) > 10 else value
                print(f"  ✅ {key}: {masked}")
            else:
                print(f"  ⚠️ {key}: NOT SET")
                if key == 'WEBAPP_URL':
                    print(f"     Note: Set this in Railway after deployment")
                else:
                    all_ok = False
        
        return all_ok
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def test_html_structure():
    """Test HTML file has required elements"""
    print("\n🔍 Testing HTML structure...")
    try:
        with open('webapp/chart.html', 'r', encoding='utf-8') as f:
            html = f.read()
        
        required_elements = [
            ('Telegram WebApp SDK', 'telegram-web-app.js'),
            ('LightWeight Charts', 'lightweight-charts'),
            ('Chart Container', 'chartContainer'),
            ('Timeframe Buttons', 'tf-btn'),
            ('API Endpoint', '/api/chart'),
            ('Symbol Parameter', 'symbol'),
            ('Indicators Display', 'rsi-value'),
        ]
        
        all_found = True
        for name, pattern in required_elements:
            if pattern in html:
                print(f"  ✅ {name} found")
            else:
                print(f"  ❌ {name} NOT FOUND")
                all_found = False
        
        return all_found
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def run_all_tests():
    """Run all tests"""
    print("="*60)
    print("🧪 WEBAPP INTEGRATION TEST SUITE")
    print("="*60)
    
    tests = [
        ("Imports", test_imports),
        ("WebApp Files", test_webapp_files_exist),
        ("Configuration", test_config),
        ("HTML Structure", test_html_structure),
        ("Binance Connection", test_binance_connection),
        ("Chart Data Generation", test_chart_data_generation),
        ("Flask App Startup", test_flask_app_startup),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ Test '{name}' crashed: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    print("\n" + "="*60)
    print(f"Results: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    print("="*60)
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! WebApp is ready to deploy!")
        print("\n📋 Next Steps:")
        print("   1. Push to GitHub (already done)")
        print("   2. Wait for Railway to deploy (~2-3 min)")
        print("   3. Set WEBAPP_URL in Railway environment:")
        print("      WEBAPP_URL=https://YOUR-APP.up.railway.app/webapp/chart.html")
        print("   4. Test in Telegram:")
        print("      /analyze BTCUSDT → Click Chart → Click Live Chart")
    else:
        print(f"\n⚠️ {total - passed} test(s) failed. Fix issues before deploying.")
    
    return passed == total

if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
