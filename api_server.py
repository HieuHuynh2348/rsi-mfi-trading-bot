"""
Flask API Routes for Trading Bot
Provides web endpoints for charts and AI analysis
This module is imported by main.py to run alongside the Telegram bot
"""

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import os
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Flask app will be created and configured by main.py
app = None
bot_instance = None

def create_app(trading_bot=None):
    """
    Create and configure Flask app
    Called from main.py with TradingBot instance
    """
    global app, bot_instance
    
    bot_instance = trading_bot
    
    app = Flask(__name__, static_folder='webapp', static_url_path='')
    CORS(app)  # Enable CORS for all routes
    
    logger.info("✅ Flask API app created")
    return app

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
        
        # Check if bot instance available
        if bot_instance is None:
            raise Exception("Bot not initialized")
        
        # Get gemini analyzer from bot
        if not hasattr(bot_instance, 'command_handler') or not hasattr(bot_instance.command_handler, 'gemini'):
            raise Exception("Gemini analyzer not available")
        
        gemini = bot_instance.command_handler.gemini
        
        # Perform analysis
        result = gemini.analyze(
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
        
        # Check if bot instance available
        if bot_instance is None:
            raise Exception("Bot not initialized")
        
        # Get binance client from bot
        binance = bot_instance.binance
        
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

# This file is now imported by main.py, not run standalone
# The Flask app is started by main.py alongside the Telegram bot
