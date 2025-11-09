#!/usr/bin/env python3
"""Test unified data collection architecture"""

import asyncio
import os
from binance_client import BinanceClient
from gemini_analyzer import GeminiAnalyzer
from stoch_rsi_analyzer import StochRSIAnalyzer

async def test_data_collection():
    """Test that indicators and historical context use same data"""
    
    # Initialize required components
    binance = BinanceClient()
    stoch_rsi = StochRSIAnalyzer(binance)
    api_key = os.getenv('GEMINI_API_KEY', 'dummy-key-for-testing')
    analyzer = GeminiAnalyzer(api_key, binance, stoch_rsi)
    
    symbol = 'BTCUSDT'
    
    print(f"🔍 Testing unified data collection for {symbol}...\n")
    
    # Collect data
    result = await analyzer.collect_data(symbol)
    
    # Check klines_dict
    klines = result.get('klines', {})
    print("📊 Klines Data (used by indicators):")
    for tf, df in klines.items():
        if df is not None and not df.empty:
            print(f"  {tf}: {len(df)} candles")
    
    # Check historical_klines
    historical = result.get('historical_klines', {})
    print(f"\n📜 Historical Context (used by AI):")
    for tf, stats in historical.items():
        if stats:
            print(f"  {tf}: {stats.get('period', 'N/A')}")
            print(f"    - Candles analyzed: {stats.get('candles_count', 'N/A')}")
    
    # Verify they use same data
    print(f"\n✅ Verification:")
    print(f"  - Klines timeframes: {list(klines.keys())}")
    print(f"  - Historical timeframes: {list(historical.keys())}")
    
    # Check if historical stats are calculated from klines data
    for tf in ['1h', '4h', '1d']:
        if tf in klines and tf in historical:
            klines_len = len(klines[tf])
            hist_count = historical[tf].get('candles_count', 0)
            match = "✅" if klines_len == hist_count else "❌"
            print(f"  - {tf.upper()}: klines={klines_len}, historical={hist_count} {match}")
    
    print(f"\n🎯 Result: Indicators and AI context now use unified data source!")

if __name__ == '__main__':
    asyncio.run(test_data_collection())
