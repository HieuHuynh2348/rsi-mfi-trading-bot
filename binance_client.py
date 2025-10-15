"""
Binance API Client Module
Handles all interactions with Binance API
"""

from binance.client import Client
from binance.exceptions import BinanceAPIException
import pandas as pd
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class BinanceClient:
    def __init__(self, api_key, api_secret):
        """Initialize Binance client"""
        self.client = Client(api_key, api_secret)
        logger.info("Binance client initialized")
    
    def get_all_symbols(self, quote_asset='USDT', excluded_keywords=None, min_volume=0):
        """
        Get all trading symbols, filtered by criteria
        
        Args:
            quote_asset: Quote currency (default USDT)
            excluded_keywords: List of keywords to exclude (e.g., ['BEAR', 'BULL'])
            min_volume: Minimum 24h volume in quote asset
        
        Returns:
            List of symbol dictionaries
        """
        if excluded_keywords is None:
            excluded_keywords = []
        
        try:
            # Get exchange info
            exchange_info = self.client.get_exchange_info()
            
            # Get 24h ticker for volume data
            tickers = self.client.get_ticker()
            ticker_dict = {t['symbol']: float(t['quoteVolume']) for t in tickers}
            
            valid_symbols = []
            
            for symbol_info in exchange_info['symbols']:
                symbol = symbol_info['symbol']
                
                # Check if it ends with quote asset
                if not symbol.endswith(quote_asset):
                    continue
                
                # Check if trading is enabled
                if symbol_info['status'] != 'TRADING':
                    continue
                
                # Check for excluded keywords
                if any(keyword in symbol for keyword in excluded_keywords):
                    logger.debug(f"Excluding {symbol} - contains excluded keyword")
                    continue
                
                # Check minimum volume
                volume = ticker_dict.get(symbol, 0)
                if volume < min_volume:
                    logger.debug(f"Excluding {symbol} - volume {volume} < {min_volume}")
                    continue
                
                valid_symbols.append({
                    'symbol': symbol,
                    'base_asset': symbol_info['baseAsset'],
                    'quote_asset': symbol_info['quoteAsset'],
                    'volume_24h': volume
                })
            
            logger.info(f"Found {len(valid_symbols)} valid symbols")
            return valid_symbols
            
        except BinanceAPIException as e:
            logger.error(f"Binance API error: {e}")
            return []
        except Exception as e:
            logger.error(f"Error getting symbols: {e}")
            return []
    
    def get_klines(self, symbol, interval, limit=500):
        """
        Get candlestick data for a symbol
        
        Args:
            symbol: Trading pair symbol
            interval: Kline interval (e.g., '5m', '1h', '4h', '1d')
            limit: Number of candles to fetch (max 1000)
        
        Returns:
            pandas DataFrame with OHLCV data
        """
        try:
            klines = self.client.get_klines(
                symbol=symbol,
                interval=interval,
                limit=limit
            )
            
            # Convert to DataFrame
            df = pd.DataFrame(klines, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_volume', 'trades', 'taker_buy_base',
                'taker_buy_quote', 'ignore'
            ])
            
            # Convert types
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = df[col].astype(float)
            
            df.set_index('timestamp', inplace=True)
            
            return df
            
        except BinanceAPIException as e:
            logger.error(f"Binance API error for {symbol}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error getting klines for {symbol}: {e}")
            return None
    
    def get_multi_timeframe_data(self, symbol, intervals, limit=500):
        """
        Get kline data for multiple timeframes
        
        Args:
            symbol: Trading pair symbol
            intervals: List of intervals (e.g., ['5m', '1h', '4h', '1d'])
            limit: Number of candles per timeframe
        
        Returns:
            Dictionary of {interval: DataFrame}
        """
        data = {}
        
        for interval in intervals:
            df = self.get_klines(symbol, interval, limit)
            if df is not None and len(df) > 0:
                data[interval] = df
            else:
                logger.warning(f"No data for {symbol} on {interval}")
        
        return data
    
    def get_current_price(self, symbol):
        """Get current price for a symbol"""
        try:
            ticker = self.client.get_symbol_ticker(symbol=symbol)
            return float(ticker['price'])
        except Exception as e:
            logger.error(f"Error getting price for {symbol}: {e}")
            return None
    
    def get_24h_data(self, symbol):
        """
        Get 24h market data for a symbol
        
        Returns:
            Dictionary with high, low, volume, price_change_percent
        """
        try:
            ticker = self.client.get_ticker(symbol=symbol)
            return {
                'high': float(ticker['highPrice']),
                'low': float(ticker['lowPrice']),
                'volume': float(ticker['quoteVolume']),
                'price_change_percent': float(ticker['priceChangePercent']),
                'price_change': float(ticker['priceChange'])
            }
        except Exception as e:
            logger.error(f"Error getting 24h data for {symbol}: {e}")
            return None
    
    def test_connection(self):
        """Test Binance API connection"""
        try:
            self.client.ping()
            logger.info("Binance API connection successful")
            return True
        except Exception as e:
            logger.error(f"Binance API connection failed: {e}")
            return False
