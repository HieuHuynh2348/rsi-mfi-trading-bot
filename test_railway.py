"""
Test Railway deployment
Verify all endpoints are working correctly
"""

import requests
import json
import sys

RAILWAY_URL = "https://rsi-mfi-trading-bot-production.up.railway.app"

def test_endpoint(url, expected_status=200, check_html=False):
    """Generic endpoint tester"""
    try:
        print(f"\n🔗 Testing: {url}")
        response = requests.get(url, timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('Content-Type')}")
        
        if check_html:
            print(f"   Content length: {len(response.content)} bytes")
            if b'<!DOCTYPE html>' in response.content:
                print("   ✅ Valid HTML document")
            else:
                print("   ⚠️  Not a valid HTML document")
        else:
            try:
                data = response.json()
                print(f"   JSON: {json.dumps(data, indent=6)}")
            except:
                print(f"   Text: {response.text[:200]}...")
        
        if response.status_code == expected_status:
            print("   ✅ PASSED")
            return True
        else:
            print(f"   ❌ FAILED (expected {expected_status}, got {response.status_code})")
            return False
            
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        return False

def main():
    print("="*70)
    print("🚀 RAILWAY DEPLOYMENT TEST")
    print("="*70)
    print(f"\nTesting: {RAILWAY_URL}\n")
    
    tests = [
        {
            'name': 'Health Check',
            'url': f"{RAILWAY_URL}/",
            'check_html': False
        },
        {
            'name': 'WebApp Chart (Full Path)',
            'url': f"{RAILWAY_URL}/webapp/chart.html",
            'check_html': True
        },
        {
            'name': 'Chart with Symbol Parameter',
            'url': f"{RAILWAY_URL}/webapp/chart.html?symbol=BTCUSDT&timeframe=1h",
            'check_html': True
        },
        {
            'name': 'Direct Chart Route',
            'url': f"{RAILWAY_URL}/chart.html",
            'check_html': True
        }
    ]
    
    results = []
    for test in tests:
        print(f"\n{'='*70}")
        print(f"TEST: {test['name']}")
        print('='*70)
        passed = test_endpoint(test['url'], check_html=test.get('check_html', False))
        results.append({'name': test['name'], 'passed': passed})
    
    # Summary
    print("\n" + "="*70)
    print("📊 TEST SUMMARY")
    print("="*70)
    
    for result in results:
        status = "✅ PASSED" if result['passed'] else "❌ FAILED"
        print(f"{status} - {result['name']}")
    
    passed_count = sum(1 for r in results if r['passed'])
    total_count = len(results)
    
    print(f"\n{passed_count}/{total_count} tests passed")
    
    if passed_count == total_count:
        print("\n🎉 All tests passed! Deployment is working correctly.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Check Railway logs for errors.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
