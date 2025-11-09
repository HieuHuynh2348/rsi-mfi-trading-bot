"""
AI Analysis API Endpoint
Returns Gemini AI analysis for a symbol
"""

from http.server import BaseHTTPRequestHandler
import json
import os
import sys
from urllib.parse import parse_qs, urlparse

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from gemini_analyzer import GeminiAnalyzer
    from binance_client import BinanceClient
    from indicators import StochRSIAnalyzer
except ImportError as e:
    print(f"Import error: {e}")
    GeminiAnalyzer = None


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle AI analysis request"""
        try:
            # Parse query parameters
            parsed_url = urlparse(self.path)
            params = parse_qs(parsed_url.query)
            
            symbol = params.get('symbol', ['BTCUSDT'])[0]
            timeframe = params.get('timeframe', ['1h'])[0]
            
            print(f"AI Analysis request: {symbol} @ {timeframe}")
            
            # Check if modules imported successfully
            if GeminiAnalyzer is None:
                raise Exception("Failed to import required modules")
            
            # Get API key
            gemini_api_key = os.getenv('GEMINI_API_KEY')
            if not gemini_api_key:
                raise Exception("GEMINI_API_KEY not configured")
            
            # Initialize clients
            binance = BinanceClient()
            stoch_rsi = StochRSIAnalyzer(binance)
            gemini = GeminiAnalyzer(gemini_api_key, binance, stoch_rsi)
            
            # Perform analysis
            print(f"Starting AI analysis for {symbol}...")
            result = gemini.analyze(
                symbol=symbol,
                pump_data=None,
                trading_style='swing',
                use_cache=True
            )
            
            if not result:
                raise Exception("AI analysis returned no result")
            
            # Return success response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                'success': True,
                'symbol': symbol,
                'timeframe': timeframe,
                'analysis': result
            }
            
            self.wfile.write(json.dumps(response, default=str).encode())
            print(f"✅ AI analysis completed for {symbol}")
            
        except Exception as e:
            print(f"❌ AI analysis error: {e}")
            import traceback
            traceback.print_exc()
            
            # Return error response
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            error_response = {
                'success': False,
                'error': str(e),
                'symbol': params.get('symbol', ['UNKNOWN'])[0] if 'params' in locals() else 'UNKNOWN'
            }
            
            self.wfile.write(json.dumps(error_response).encode())
    
    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
