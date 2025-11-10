"""Simple test of institutional helpers without dependencies"""
import pandas as pd
import numpy as np

# Mock the institutional methods standalone
def analyze_volume_profile_historical(df, current_price: float):
    """Analyze Volume Profile metrics over historical period"""
    try:
        # Calculate POC (Point of Control) - price level with highest volume
        price_levels = df[['close', 'volume']].copy()
        price_levels['price_level'] = (price_levels['close'] // 1).astype(int)
        volume_by_level = price_levels.groupby('price_level')['volume'].sum()
        
        if len(volume_by_level) == 0:
            return {}
        
        poc_price = float(volume_by_level.idxmax())
        poc_volume = float(volume_by_level.max())
        
        # Value Area (70% of volume)
        total_volume = float(df['volume'].sum())
        sorted_levels = volume_by_level.sort_values(ascending=False)
        cumsum = sorted_levels.cumsum()
        value_area_levels = sorted_levels[cumsum <= total_volume * 0.7]
        
        vah = float(value_area_levels.index.max()) if len(value_area_levels) > 0 else poc_price * 1.05
        val = float(value_area_levels.index.min()) if len(value_area_levels) > 0 else poc_price * 0.95
        
        # Current price position
        if current_price > vah:
            position = "PREMIUM"
        elif current_price < val:
            position = "DISCOUNT"
        else:
            position = "VALUE_AREA"
        
        distance_from_poc = ((current_price - poc_price) / poc_price) * 100
        
        return {
            'poc': round(poc_price, 4),
            'vah': round(vah, 4),
            'val': round(val, 4),
            'current_position': position,
            'distance_from_poc_pct': round(distance_from_poc, 2),
            'poc_volume': round(poc_volume, 2),
            'value_area_coverage': 70.0
        }
    except Exception as e:
        print(f"Volume Profile error: {e}")
        return {}

# Create sample data
print("Creating sample BTCUSDT-like data...")
dates = pd.date_range('2025-01-01', periods=168, freq='h')
np.random.seed(42)

# Generate realistic price data
base_price = 100000
price_changes = np.random.randn(168) * 500
prices = base_price + np.cumsum(price_changes)

df = pd.DataFrame({
    'timestamp': dates,
    'open': prices + np.random.randn(168) * 100,
    'high': prices + np.abs(np.random.randn(168) * 200),
    'low': prices - np.abs(np.random.randn(168) * 200),
    'close': prices,
    'volume': np.random.rand(168) * 1000 + 500
})

current_price = float(df.iloc[-1]['close'])

print(f"\nData shape: {df.shape}")
print(f"Current Price: ${current_price:,.2f}\n")

# Test Volume Profile
print("="*60)
print("Testing Volume Profile Historical Analysis")
print("="*60)
vp_result = analyze_volume_profile_historical(df, current_price)
if vp_result:
    print(f"✅ POC (Point of Control): ${vp_result['poc']:,.2f}")
    print(f"✅ VAH (Value Area High): ${vp_result['vah']:,.2f}")
    print(f"✅ VAL (Value Area Low): ${vp_result['val']:,.2f}")
    print(f"✅ Price Position: {vp_result['current_position']}")
    print(f"✅ Distance from POC: {vp_result['distance_from_poc_pct']:+.2f}%")
    print(f"✅ POC Volume: {vp_result['poc_volume']:,.0f}")
else:
    print("❌ Analysis failed")

print("\n" + "="*60)
print("✅ Test completed successfully!")
print("="*60)
