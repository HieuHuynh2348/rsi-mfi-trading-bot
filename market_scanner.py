"""
Market Scanner - Automatic Extreme RSI/MFI Detection
Scans all Binance USDT pairs for extreme overbought/oversold conditions on 1D timeframe
"""

import logging
import time
import threading
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger(__name__)


class MarketScanner:
    def __init__(self, command_handler, scan_interval=900):
        """
        Initialize market scanner
        
        Args:
            command_handler: TelegramCommandHandler instance
            scan_interval: Scan interval in seconds (default: 900 = 15 minutes)
        """
        self.command_handler = command_handler
        self.binance = command_handler.binance
        self.bot = command_handler.bot
        self.scan_interval = scan_interval
        
        # Scanner state
        self.running = False
        self.thread = None
        self.last_alerts = {}  # Track last alerts to avoid duplicates
        
        # Extreme levels for 1D timeframe
        self.rsi_upper = 80
        self.rsi_lower = 20
        self.mfi_upper = 80
        self.mfi_lower = 20
        
        logger.info(f"Market scanner initialized (interval: {scan_interval}s, RSI: {self.rsi_lower}-{self.rsi_upper}, MFI: {self.mfi_lower}-{self.mfi_upper})")
    
    def start(self):
        """Start market scanner"""
        if self.running:
            logger.warning("Market scanner already running")
            return False
        
        self.running = True
        self.thread = threading.Thread(target=self._scan_loop, daemon=True)
        self.thread.start()
        
        logger.info("✅ Market scanner started")
        return True
    
    def stop(self):
        """Stop market scanner"""
        if not self.running:
            logger.warning("Market scanner not running")
            return False
        
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        
        logger.info("⛔ Market scanner stopped")
        return True
    
    def _scan_loop(self):
        """Main scanning loop"""
        logger.info("Market scanner loop started")
        
        while self.running:
            try:
                # Perform scan
                logger.info("🔍 Starting market scan...")
                start_time = time.time()
                
                extreme_coins = self._scan_market()
                
                scan_time = time.time() - start_time
                logger.info(f"✅ Market scan completed in {scan_time:.1f}s - Found {len(extreme_coins)} extreme coins")
                
                # Send alerts for extreme coins
                if extreme_coins:
                    self._send_alerts(extreme_coins)
                
                # Sleep until next scan
                if self.running:
                    logger.info(f"💤 Sleeping for {self.scan_interval}s until next scan...")
                    time.sleep(self.scan_interval)
                    
            except Exception as e:
                logger.error(f"Error in market scanner loop: {e}")
                if self.running:
                    time.sleep(60)  # Sleep 1 minute on error
        
        logger.info("Market scanner loop stopped")
    
    def _scan_market(self):
        """
        Scan all Binance USDT pairs for extreme RSI/MFI on 1D
        
        Returns:
            List of coins with extreme conditions
        """
        try:
            # Get all USDT trading pairs
            all_symbols = self.binance.get_all_usdt_symbols()
            
            if not all_symbols:
                logger.warning("No symbols found")
                return []
            
            logger.info(f"Scanning {len(all_symbols)} USDT pairs...")
            
            extreme_coins = []
            
            # Use thread pool for parallel scanning
            max_workers = 10  # Limit concurrent requests
            
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Submit all analysis tasks
                future_to_symbol = {
                    executor.submit(self._analyze_coin_1d, symbol): symbol 
                    for symbol in all_symbols
                }
                
                # Collect results
                for future in as_completed(future_to_symbol):
                    symbol = future_to_symbol[future]
                    try:
                        result = future.result()
                        if result and result.get('is_extreme'):
                            extreme_coins.append(result)
                            logger.info(f"⚡ EXTREME: {symbol} - RSI: {result.get('rsi_1d', 0):.1f}, MFI: {result.get('mfi_1d', 0):.1f}")
                    except Exception as e:
                        logger.debug(f"Error analyzing {symbol}: {e}")
            
            return extreme_coins
            
        except Exception as e:
            logger.error(f"Error scanning market: {e}")
            return []
    
    def _analyze_coin_1d(self, symbol):
        """
        Analyze single coin for extreme RSI/MFI on 1D timeframe
        
        Args:
            symbol: Trading symbol
        
        Returns:
            dict with analysis or None
        """
        try:
            # Get 1D klines
            df_1d = self.binance.get_klines(symbol, '1d', limit=100)
            
            if df_1d is None or len(df_1d) < 14:
                return None
            
            # Calculate RSI and MFI for 1D
            from indicators import calculate_rsi, calculate_mfi
            
            rsi_1d = calculate_rsi(df_1d, period=14)
            mfi_1d = calculate_mfi(df_1d, period=14)
            
            if rsi_1d is None or mfi_1d is None:
                return None
            
            current_rsi = rsi_1d.iloc[-1]
            current_mfi = mfi_1d.iloc[-1]
            
            # Check if extreme
            is_extreme = (
                current_rsi >= self.rsi_upper or 
                current_rsi <= self.rsi_lower or
                current_mfi >= self.mfi_upper or
                current_mfi <= self.mfi_lower
            )
            
            if not is_extreme:
                return None
            
            # Get current price
            current_price = df_1d['close'].iloc[-1]
            
            # Determine condition type
            conditions = []
            if current_rsi >= self.rsi_upper:
                conditions.append(f"RSI Overbought ({current_rsi:.1f})")
            if current_rsi <= self.rsi_lower:
                conditions.append(f"RSI Oversold ({current_rsi:.1f})")
            if current_mfi >= self.mfi_upper:
                conditions.append(f"MFI Overbought ({current_mfi:.1f})")
            if current_mfi <= self.mfi_lower:
                conditions.append(f"MFI Oversold ({current_mfi:.1f})")
            
            return {
                'symbol': symbol,
                'is_extreme': True,
                'rsi_1d': current_rsi,
                'mfi_1d': current_mfi,
                'price': current_price,
                'conditions': conditions,
                'timestamp': datetime.now()
            }
            
        except Exception as e:
            logger.debug(f"Error analyzing {symbol}: {e}")
            return None
    
    def _send_alerts(self, extreme_coins):
        """
        Send alerts for extreme coins
        
        Args:
            extreme_coins: List of extreme coin data
        """
        try:
            # Filter out recently alerted coins (avoid spam)
            new_alerts = []
            current_time = time.time()
            cooldown = 3600  # 1 hour cooldown per coin
            
            for coin in extreme_coins:
                symbol = coin['symbol']
                last_alert_time = self.last_alerts.get(symbol, 0)
                
                if current_time - last_alert_time > cooldown:
                    new_alerts.append(coin)
                    self.last_alerts[symbol] = current_time
            
            if not new_alerts:
                logger.info("No new alerts (all in cooldown period)")
                return
            
            # Send summary first
            summary = f"<b>🔍 MARKET SCAN ALERT</b>\n\n"
            summary += f"⚡ Found <b>{len(new_alerts)}</b> coins with extreme 1D RSI/MFI:\n\n"
            
            for coin in new_alerts:
                symbol = coin['symbol']
                rsi = coin['rsi_1d']
                mfi = coin['mfi_1d']
                conditions_text = ", ".join(coin['conditions'])
                
                # Emoji based on condition
                if rsi <= self.rsi_lower or mfi <= self.mfi_lower:
                    emoji = "🟢"  # Oversold - potential buy
                else:
                    emoji = "🔴"  # Overbought - potential sell
                
                summary += f"{emoji} <b>{symbol}</b>\n"
                summary += f"   📊 RSI: {rsi:.1f} | MFI: {mfi:.1f}\n"
                summary += f"   ⚡ {conditions_text}\n\n"
            
            summary += f"📤 Sending detailed analysis for each coin...\n"
            
            self.bot.send_message(summary)
            time.sleep(1)
            
            # Send detailed analysis for each coin
            for coin in new_alerts:
                try:
                    self._send_detailed_analysis(coin['symbol'])
                    time.sleep(2)  # Rate limiting
                except Exception as e:
                    logger.error(f"Error sending detailed analysis for {coin['symbol']}: {e}")
            
            logger.info(f"✅ Sent alerts for {len(new_alerts)} extreme coins")
            
        except Exception as e:
            logger.error(f"Error sending alerts: {e}")
    
    def _send_detailed_analysis(self, symbol):
        """
        Send detailed multi-timeframe analysis for symbol
        
        Args:
            symbol: Trading symbol
        """
        try:
            # Use command handler's analysis function
            result = self.command_handler._analyze_symbol_full(symbol)
            
            if result:
                self.bot.send_signal_alert(
                    result['symbol'],
                    result['timeframe_data'],
                    result['consensus'],
                    result['consensus_strength'],
                    result['price'],
                    result.get('market_data'),
                    result.get('volume_data')
                )
                logger.info(f"✅ Sent detailed analysis for {symbol}")
            else:
                logger.warning(f"Failed to analyze {symbol}")
                
        except Exception as e:
            logger.error(f"Error in detailed analysis for {symbol}: {e}")
    
    def get_status(self):
        """
        Get scanner status
        
        Returns:
            dict with status info
        """
        return {
            'running': self.running,
            'scan_interval': self.scan_interval,
            'rsi_levels': f"{self.rsi_lower}-{self.rsi_upper}",
            'mfi_levels': f"{self.mfi_lower}-{self.mfi_upper}",
            'tracked_coins': len(self.last_alerts),
            'cooldown': '1 hour'
        }
