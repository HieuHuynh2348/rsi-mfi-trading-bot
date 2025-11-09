"""
API Endpoint for Vercel Serverless Function
This endpoint is triggered by Vercel Cron Jobs every 5 minutes
"""

from http.server import BaseHTTPRequestHandler
import json
import sys
import os

# Add parent directory to path to import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from binance_client import BinanceClient
from telegram_bot import TelegramBot
from indicators import analyze_multi_timeframe
import logging

# Disable chart generation for Vercel (matplotlib dependency issues)
SEND_CHARTS = False

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET request - scan market and send signals"""
        try:
            logger.info("Starting market scan via Vercel serverless function...")
            
            # Initialize clients
            binance = BinanceClient(config.BINANCE_API_KEY, config.BINANCE_API_SECRET)
            telegram = TelegramBot(config.TELEGRAM_BOT_TOKEN, config.TELEGRAM_CHAT_ID)
            
            # Get all valid symbols
            symbols = binance.get_all_symbols(
                quote_asset=config.QUOTE_ASSET,
                excluded_keywords=config.EXCLUDED_KEYWORDS,
                min_volume=config.MIN_VOLUME_USDT
            )
            
            if not symbols:
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'status': 'success',
                    'message': 'No symbols found to scan'
                }).encode())
                return
            
            logger.info(f"Scanning {len(symbols)} symbols...")
            signals_found = []
            
            # Limit to first 50 symbols to avoid timeout (Vercel has 10s limit for Hobby plan)
            for i, symbol_info in enumerate(symbols[:50]):
                symbol = symbol_info['symbol']
                
                try:
                    # Get multi-timeframe data
                    klines_dict = binance.get_multi_timeframe_data(
                        symbol, 
                        config.TIMEFRAMES,
                        limit=200
                    )
                    
                    if not klines_dict:
                        continue
                    
                    # Analyze
                    analysis = analyze_multi_timeframe(
                        klines_dict,
                        config.RSI_PERIOD,
                        config.MFI_PERIOD,
                        config.RSI_LOWER,
                        config.RSI_UPPER,
                        config.MFI_LOWER,
                        config.MFI_UPPER
                    )
                    
                    # Check if signal meets minimum consensus strength
                    if analysis['consensus'] != 'NEUTRAL' and \
                       analysis['consensus_strength'] >= config.MIN_CONSENSUS_STRENGTH:
                        
                        price = binance.get_current_price(symbol)
                        market_data = binance.get_24h_data(symbol)
                        # Pre-format prices for downstream Telegram messages
                        formatted_price = binance.format_price(symbol, price) if price is not None else None
                        if market_data:
                            market_data['high'] = binance.format_price(symbol, market_data.get('high'))
                            market_data['low'] = binance.format_price(symbol, market_data.get('low'))
                        
                        signal_data = {
                            'symbol': symbol,
                            'timeframe_data': analysis['timeframes'],
                            'consensus': analysis['consensus'],
                            'consensus_strength': analysis['consensus_strength'],
                            'price': formatted_price,
                            'market_data': market_data,
                            'klines_dict': klines_dict
                        }
                        
                        signals_found.append(signal_data)
                        logger.info(f"Signal found for {symbol}: {analysis['consensus']}")
                
                except Exception as e:
                    logger.error(f"Error analyzing {symbol}: {e}")
                    continue
            
            # Send results
            if signals_found:
                logger.info(f"Found {len(signals_found)} signals, sending to Telegram...")
                
                # Send summary
                telegram.send_summary_table(signals_found)
                
                # Send individual signals if not in summary-only mode
                if not config.SEND_SUMMARY_ONLY:
                    for signal in signals_found[:config.MAX_COINS_PER_MESSAGE]:
                        telegram.send_signal_alert(
                            signal['symbol'],
                            signal['timeframe_data'],
                            signal['consensus'],
                            signal['consensus_strength'],
                            signal['price'],
                            signal.get('market_data'),
                            signal.get('volume_data')
                        )
            
            # Send response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            response = {
                'status': 'success',
                'symbols_scanned': len(symbols[:50]),
                'signals_found': len(signals_found),
                'signals': [
                    {
                        'symbol': s['symbol'],
                        'consensus': s['consensus'],
                        'strength': s['consensus_strength']
                    }
                    for s in signals_found
                ]
            }
            
            self.wfile.write(json.dumps(response).encode())
            logger.info("Market scan completed successfully")
            
        except Exception as e:
            logger.error(f"Error in serverless function: {e}")
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                'status': 'error',
                'message': str(e)
            }).encode())
    
    def do_POST(self):
        """Handle POST request - same as GET"""
        self.do_GET()
