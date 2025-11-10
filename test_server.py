"""
Test script to verify server.py routes
Run this locally before deploying to Railway
"""

import requests
import json

BASE_URL = "http://localhost:8080"

def test_health_check():
    """Test health check endpoint"""
    print("\n🧪 Testing health check endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'online'
        print("✅ Health check passed!")
    except Exception as e:
        print(f"❌ Health check failed: {e}")

def test_webapp_chart():
    """Test webapp chart.html serving"""
    print("\n🧪 Testing chart.html serving...")
    try:
        response = requests.get(f"{BASE_URL}/webapp/chart.html")
        print(f"Status: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type')}")
        print(f"Content length: {len(response.content)} bytes")
        assert response.status_code == 200
        assert 'text/html' in response.headers.get('Content-Type', '')
        assert b'<!DOCTYPE html>' in response.content
        assert b'Live Chart' in response.content
        print("✅ Chart serving passed!")
    except Exception as e:
        print(f"❌ Chart serving failed: {e}")

def test_webapp_chart_direct():
    """Test direct /chart.html route"""
    print("\n🧪 Testing direct /chart.html route...")
    try:
        response = requests.get(f"{BASE_URL}/chart.html")
        print(f"Status: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type')}")
        assert response.status_code == 200
        assert 'text/html' in response.headers.get('Content-Type', '')
        print("✅ Direct chart route passed!")
    except Exception as e:
        print(f"❌ Direct chart route failed: {e}")

def test_webapp_with_params():
    """Test chart with URL parameters"""
    print("\n🧪 Testing chart with parameters...")
    try:
        response = requests.get(f"{BASE_URL}/webapp/chart.html?symbol=BTCUSDT&timeframe=1h")
        print(f"Status: {response.status_code}")
        assert response.status_code == 200
        print("✅ Chart with params passed!")
    except Exception as e:
        print(f"❌ Chart with params failed: {e}")

if __name__ == '__main__':
    print("="*60)
    print("🚀 Testing Server Routes")
    print("="*60)
    print("\n⚠️  Make sure server is running: python server.py")
    print(f"Testing against: {BASE_URL}")
    
    test_health_check()
    test_webapp_chart()
    test_webapp_chart_direct()
    test_webapp_with_params()
    
    print("\n" + "="*60)
    print("✅ All tests completed!")
    print("="*60)
