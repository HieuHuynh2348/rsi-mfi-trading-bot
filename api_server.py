"""
API Server for Trading Bot
Handles web requests for charts and AI analysis
"""

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import os
import logging
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

from binance_client import BinanceClient
from stoch_rsi_analyzer import StochRSIAnalyzer
from gemini_analyzer import GeminiAnalyzer
import config

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__, static_folder='webapp', static_url_path='')
CORS(app)  # Enable CORS for all routes

# Initialize clients
binance = None
gemini_analyzer = None

def init_clients():
    """Initialize API clients"""
    global binance, gemini_analyzer
    
    try:
        logger.info("Initializing API clients...")
        binance = BinanceClient()
        
        # Get Gemini API key
        gemini_api_key = os.getenv('GEMINI_API_KEY')
        if not gemini_api_key:
            logger.error("GEMINI_API_KEY not found in environment")
            return False
        
        stoch_rsi = StochRSIAnalyzer(binance)
        gemini_analyzer = GeminiAnalyzer(gemini_api_key, binance, stoch_rsi)
        
        logger.info("✅ API clients initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize clients: {e}")
        return False

@app.route('/')
def index():
    """Health check endpoint"""
    return jsonify({
        'status': 'online',
        'service': 'RSI + MFI Trading Bot API',
        'version': '1.0.0',
        'endpoints': {
            'ai_analyze': '/api/ai-analyze?symbol=BTCUSDT&timeframe=1h',
            'chart': '/chart.html?symbol=BTCUSDT&timeframe=1h',
            'health': '/'
        }
    })

@app.route('/chart.html')
def serve_chart():
    """Serve chart HTML"""
    return send_from_directory('webapp', 'chart.html')

@app.route('/api/ai-analyze')
def ai_analyze():
    """
    AI Analysis endpoint
    GET /api/ai-analyze?symbol=BTCUSDT&timeframe=1h
    """
    try:
        # Get parameters
        symbol = request.args.get('symbol', 'BTCUSDT')
        timeframe = request.args.get('timeframe', '1h')
        
        logger.info(f"AI Analysis request: {symbol} @ {timeframe}")
        
        # Check if clients initialized
        if gemini_analyzer is None:
            raise Exception("Gemini analyzer not initialized")
        
        # Perform analysis
        result = gemini_analyzer.analyze(
            symbol=symbol,
            pump_data=None,
            trading_style='swing',
            use_cache=True
        )
        
        if not result:
            raise Exception("AI analysis returned no result")
        
        logger.info(f"✅ AI analysis completed for {symbol}")
        
        return jsonify({
            'success': True,
            'symbol': symbol,
            'timeframe': timeframe,
            'analysis': result
        })
        
    except Exception as e:
        logger.error(f"❌ AI analysis error: {e}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'success': False,
            'error': str(e),
            'symbol': request.args.get('symbol', 'UNKNOWN')
        }), 500

@app.route('/api/chart-data')
def chart_data():
    """
    Chart data endpoint
    GET /api/chart-data?symbol=BTCUSDT&timeframe=1h
    """
    try:
        symbol = request.args.get('symbol', 'BTCUSDT')
        timeframe = request.args.get('timeframe', '1h')
        
        logger.info(f"Chart data request: {symbol} @ {timeframe}")
        
        if binance is None:
            raise Exception("Binance client not initialized")
        
        # Get candle data
        candles = binance.get_historical_klines(symbol, timeframe, limit=500)
        
        if not candles:
            raise Exception("No candle data available")
        
        return jsonify({
            'success': True,
            'symbol': symbol,
            'timeframe': timeframe,
            'candles': candles
        })
        
    except Exception as e:
        logger.error(f"❌ Chart data error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    # Initialize clients
    if not init_clients():
        logger.error("Failed to initialize clients. Exiting.")
        sys.exit(1)
    
    # Get port from environment or use 8080
    port = int(os.getenv('PORT', 8080))
    
    logger.info(f"🚀 Starting API server on port {port}...")
    
    # Run Flask app
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False
    )
