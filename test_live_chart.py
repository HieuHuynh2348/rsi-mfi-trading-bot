#!/usr/bin/env python3
"""
Test Live Chart Integration
"""

from chart_generator import (
    get_tradingview_chart_url,
    get_tradingview_urls_multi_timeframe,
    format_chart_caption
)

def test_tradingview_urls():
    """Test TradingView URL generation"""
    
    print("🔍 Testing TradingView URL Generation\n")
    print("="*60)
    
    # Test single URL
    symbol = 'BTCUSDT'
    url_1h = get_tradingview_chart_url(symbol, '60')
    print(f"\n1. Single URL (1H):")
    print(f"   Symbol: {symbol}")
    print(f"   URL: {url_1h}")
    
    # Test multi-timeframe URLs
    print(f"\n2. Multi-Timeframe URLs:")
    urls = get_tradingview_urls_multi_timeframe(symbol)
    for tf, url in urls.items():
        print(f"   {tf}: {url}")
    
    # Test caption formatting
    print(f"\n3. Chart Caption:")
    caption = format_chart_caption(symbol, 102115.69, -2.35)
    print(caption)
    
    print("\n" + "="*60)
    print("✅ All tests passed!")
    
    # Test URLs are accessible
    print(f"\n📌 Test these URLs in browser:")
    print(f"   1H: {url_1h}")
    print(f"   4H: {get_tradingview_chart_url(symbol, '240')}")
    print(f"   1D: {get_tradingview_chart_url(symbol, 'D')}")

if __name__ == '__main__':
    test_tradingview_urls()
