"""
Test script for /api/candles endpoint
Run this to verify the indicators tab will work
"""

import requests
import json

# Test local server
BASE_URL = "http://localhost:5000"  # Change to Railway URL if testing production

def test_candles_endpoint():
    """Test /api/candles endpoint"""
    
    print("🧪 Testing /api/candles endpoint...\n")
    
    # Test parameters
    test_cases = [
        {'symbol': 'BTCUSDT', 'interval': '1h', 'limit': 100},
        {'symbol': 'ETHUSDT', 'interval': '5m', 'limit': 50},
        {'symbol': 'BTCUSDT', 'interval': '1d', 'limit': 30},
    ]
    
    for i, params in enumerate(test_cases, 1):
        print(f"Test {i}: {params}")
        print("-" * 50)
        
        try:
            response = requests.get(f"{BASE_URL}/api/candles", params=params, timeout=10)
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Success: {data.get('success')}")
                print(f"📊 Symbol: {data.get('symbol')}")
                print(f"⏱️  Interval: {data.get('interval')}")
                print(f"📈 Candles Count: {data.get('count')}")
                
                if data.get('candles'):
                    candle = data['candles'][0]
                    print(f"\nSample Candle:")
                    print(f"  Time: {candle.get('time')}")
                    print(f"  Open: {candle.get('open')}")
                    print(f"  High: {candle.get('high')}")
                    print(f"  Low: {candle.get('low')}")
                    print(f"  Close: {candle.get('close')}")
                    print(f"  Volume: {candle.get('volume')}")
            else:
                print(f"❌ Error: {response.text}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")
        
        print("\n")

def test_missing_params():
    """Test error handling"""
    
    print("🧪 Testing error handling...\n")
    
    # Missing symbol
    print("Test: Missing symbol parameter")
    try:
        response = requests.get(f"{BASE_URL}/api/candles", params={'interval': '1h'})
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    print("\n")
    
    # Missing interval
    print("Test: Missing interval parameter")
    try:
        response = requests.get(f"{BASE_URL}/api/candles", params={'symbol': 'BTCUSDT'})
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == '__main__':
    print("=" * 50)
    print("🚀 Indicators API Test Suite")
    print("=" * 50)
    print()
    
    test_candles_endpoint()
    test_missing_params()
    
    print("=" * 50)
    print("✅ Tests completed!")
    print("=" * 50)
