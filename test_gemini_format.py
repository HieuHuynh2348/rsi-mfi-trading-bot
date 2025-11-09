"""
Test Gemini format output
"""

import sys
import io

# Set UTF-8 encoding for console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Test data
test_analysis = {
    'symbol': 'ZBTUSDT',
    'recommendation': 'WAIT',
    'confidence': 60,
    'entry_point': 0.1550,
    'stop_loss': 0.1500,
    'take_profit': [0.1700, 0.1850, 0.2000],
    'expected_holding_period': '3-5 ngày',
    'risk_level': 'MEDIUM',
    'trading_style': 'swing',
    'technical_score': 65,
    'fundamental_score': 55,
    'market_sentiment': 'NEUTRAL',
    'key_points': [
        'RSI ở vùng trung lập, chưa có tín hiệu rõ ràng',
        'Volume thấp, thị trường sideway',
        'Cần chờ breakout để xác nhận trend'
    ],
    'conflicting_signals': [
        'RSI tăng nhưng MFI giảm',
        'Stochastic cho tín hiệu mua nhưng giá đang giảm'
    ],
    'warnings': [
        'Volume thấp, khả năng dump cao',
        'Nên đợi xác nhận từ timeframe 4h'
    ],
    'reasoning_vietnamese': '''
🔍 <b>Phân Tích Chi Tiết:</b>

<b>1. Phân Tích Kỹ Thuật:</b>
ZBTUSDT hiện đang ở vùng giá $0.1550, trong trạng thái sideway. Các chỉ báo RSI và MFI đang ở vùng trung lập (50-60), cho thấy thị trường chưa có xu hướng rõ ràng.

<b>2. Volume Analysis:</b>
Volume giao dịch đang ở mức thấp, cho thấy sự quan tâm của nhà đầu tư chưa cao. Điều này làm tăng rủi ro volatility đột ngột khi có tin tức hoặc whale action.

<b>3. Khuyến Nghị:</b>
Với các tín hiệu hiện tại, tốt nhất là CHỜ ĐỢI (WAIT) cho đến khi có tín hiệu rõ ràng hơn. Nếu giá breakout lên trên $0.1600 với volume tốt, có thể xem xét vào lệnh mua.

<b>4. Risk Management:</b>
Nếu quyết định vào lệnh, nhớ đặt stop loss chặt chẽ tại $0.1500 để bảo vệ vốn. Take profit chia làm 3 đợt để tối ưu lợi nhuận.
    ''',
    'analyzed_at': '2025-11-09 17:00:00',
    'data_used': {
        'rsi_mfi_consensus': 'NEUTRAL',
        'stoch_rsi_consensus': 'NEUTRAL',
        'pump_score': 45,
        'current_price': 0.1550
    }
}

# Mock format_price
class MockBinance:
    def format_price(self, symbol, price):
        return f"{price:.4f}"

# Test format
def test_format():
    from gemini_analyzer import GeminiAnalyzer
    
    # Create mock instance
    analyzer = GeminiAnalyzer.__new__(GeminiAnalyzer)
    analyzer.binance = MockBinance()
    
    # Format response
    msg1, msg2, msg3 = analyzer.format_response(test_analysis)
    
    print("\n" + "="*60)
    print("MESSAGE 1 - SUMMARY:")
    print("="*60)
    print(msg1)
    
    print("\n" + "="*60)
    print("MESSAGE 2 - TECHNICAL DETAILS:")
    print("="*60)
    print(msg2)
    
    print("\n" + "="*60)
    print("MESSAGE 3 - AI REASONING:")
    print("="*60)
    print(msg3)
    
    print("\n" + "="*60)
    print("✅ Format test completed!")
    print("="*60)

if __name__ == '__main__':
    test_format()
