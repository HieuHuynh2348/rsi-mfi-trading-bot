"""
Web Chart API
Serves chart data and webapp for Telegram Mini App
"""

from flask import Flask, jsonify, send_file, request
from flask_cors import CORS
import os
import sys
import logging
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from binance_client import BinanceClient
from indicators import calculate_rsi, calculate_mfi, calculate_hlcc4
import config

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Binance client
try:
    binance = BinanceClient(config.BINANCE_API_KEY, config.BINANCE_API_SECRET)
    logger.info("✅ Binance client initialized")
except Exception as e:
    logger.error(f"❌ Failed to initialize Binance client: {e}")
    binance = None


@app.route('/')
def index():
    """Serve main webapp page"""
    return send_file('webapp/chart.html')


@app.route('/api/chart')
def get_chart_data():
    """
    Get chart data for symbol and timeframe
    
    Query params:
        symbol: Trading pair (e.g., BTCUSDT)
        timeframe: Timeframe (5m, 1h, 4h, 1d)
    
    Returns:
        JSON with candles, indicators, and current price
    """
    try:
        symbol = request.args.get('symbol', 'BTCUSDT')
        timeframe = request.args.get('timeframe', '1h')
        
        logger.info(f"📊 Getting chart data for {symbol} {timeframe}")
        
        if not binance:
            return jsonify({'error': 'Binance client not initialized'}), 500
        
        # Convert timeframe to limit
        limit_map = {
            '5m': 100,
            '1h': 168,
            '4h': 180,
            '1d': 90
        }
        limit = limit_map.get(timeframe, 100)
        
        # Get klines
        df = binance.get_klines(symbol, timeframe, limit=limit)
        
        if df is None or df.empty:
            return jsonify({'error': 'No data available'}), 404
        
        # Calculate indicators
        hlcc4 = calculate_hlcc4(df)
        df['rsi'] = calculate_rsi(hlcc4, 14)
        df['mfi'] = calculate_mfi(df, 14)
        
        # Get current price and 24h change
        try:
            ticker_data = binance.client.get_ticker(symbol=symbol)
            current_price = float(ticker_data['lastPrice'])
            price_change = float(ticker_data['priceChangePercent'])
        except:
            # Fallback to last close price
            current_price = float(df['close'].iloc[-1])
            price_change = 0.0
        
        # Format candles for chart
        candles = []
        for idx, row in df.iterrows():
            # Use index as timestamp (it's already datetime)
            if isinstance(idx, int):
                time = idx
            elif hasattr(idx, 'timestamp'):
                time = int(idx.timestamp())
            else:
                # Fallback to close_time if available
                time = int(row.get('close_time', idx) / 1000) if 'close_time' in row else idx
            
            candles.append({
                'time': time,
                'open': float(row['open']),
                'high': float(row['high']),
                'low': float(row['low']),
                'close': float(row['close']),
                'volume': float(row['volume'])
            })
        
        # Get latest indicator values
        latest_rsi = float(df['rsi'].iloc[-1])
        latest_mfi = float(df['mfi'].iloc[-1])
        
        response = {
            'symbol': symbol,
            'timeframe': timeframe,
            'currentPrice': current_price,
            'priceChange': price_change,
            'rsi': latest_rsi,
            'mfi': latest_mfi,
            'candles': candles,
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"✅ Sent {len(candles)} candles for {symbol} {timeframe}")
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"❌ Error getting chart data: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'binance_connected': binance is not None,
        'timestamp': datetime.now().isoformat()
    })


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    logger.info(f"🚀 Starting Flask server on port {port}")
    
    # Production mode: use Waitress WSGI server
    try:
        from waitress import serve
        logger.info("✅ Using Waitress production WSGI server")
        serve(app, host='0.0.0.0', port=port, threads=4)
    except ImportError:
        logger.warning("⚠️ Waitress not found, falling back to development server")
        app.run(host='0.0.0.0', port=port, debug=False)
