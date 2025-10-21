"""
Main Bot Script
RSI + MFI Multi-Timeframe Analysis Bot
Scans Binance markets and sends alerts to Telegram
"""

import time
import logging
from datetime import datetime
import sys
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

# Import modules
import config
from binance_client import BinanceClient
from telegram_bot import TelegramBot
from chart_generator import ChartGenerator
from indicators import analyze_multi_timeframe
from telegram_commands import TelegramCommandHandler

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class TradingBot:
    def __init__(self):
        """Initialize the trading bot"""
        logger.info("Initializing Trading Bot...")
        
        # Initialize clients
        self.binance = BinanceClient(config.BINANCE_API_KEY, config.BINANCE_API_SECRET)
        self.telegram = TelegramBot(config.TELEGRAM_BOT_TOKEN, config.TELEGRAM_CHAT_ID)
        self.chart_gen = ChartGenerator(
            style=config.CHART_STYLE,
            dpi=config.CHART_DPI,
            width=config.CHART_WIDTH,
            height=config.CHART_HEIGHT
        )
        
        # Initialize command handler (pass self for /scan command)
        self.command_handler = TelegramCommandHandler(
            self.telegram,
            self.binance,
            self.chart_gen,
            trading_bot_instance=self  # Pass bot instance for /scan
        )
        
        # Test connections
        if not self.test_connections():
            logger.error("Failed to initialize connections. Exiting.")
            sys.exit(1)
        
        logger.info("Trading Bot initialized successfully")
    
    def test_connections(self):
        """Test all API connections"""
        logger.info("Testing API connections...")
        
        binance_ok = self.binance.test_connection()
        telegram_ok = self.telegram.test_connection()
        
        if binance_ok and telegram_ok:
            logger.info("All connections successful")
            welcome_msg = """
<b>ðŸ¤– TRADING BOT ONLINE!</b>

<b>âœ… ALL SYSTEMS OPERATIONAL</b>

<b>ðŸŽ® MODE:</b> Command-Only
<b>ðŸ“Š Interactive:</b> Enabled
<b>âš¡ Fast Scan:</b> Active

<b>ðŸš€ QUICK START:</b>
â€¢ /<b>BTC</b> - Bitcoin analysis
â€¢ /<b>ETH</b> - Ethereum analysis  
â€¢ /<b>scan</b> - Scan entire market
â€¢ /<b>help</b> - All commands

<i>ðŸ’¡ No auto-scan. Use /scan when needed!</i>
            """
            self.telegram.send_message(welcome_msg)
            return True
        else:
            logger.error("Connection test failed")
            return False
    
    def analyze_symbol(self, symbol):
        """
        Analyze a single symbol (thread-safe method for concurrent execution)
        
        Args:
            symbol: Trading symbol to analyze
        
        Returns:
            Signal data dict or None if no signal
        """
        try:
            # Get multi-timeframe data
            klines_dict = self.binance.get_multi_timeframe_data(
                symbol, 
                config.TIMEFRAMES,
                limit=200
            )
            
            if not klines_dict:
                logger.warning(f"No data for {symbol}")
                return None
            
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
                
                # Get current price and 24h data
                price = self.binance.get_current_price(symbol)
                market_data = self.binance.get_24h_data(symbol)
                
                signal_data = {
                    'symbol': symbol,
                    'timeframe_data': analysis['timeframes'],
                    'consensus': analysis['consensus'],
                    'consensus_strength': analysis['consensus_strength'],
                    'price': price,
                    'market_data': market_data,
                    'klines_dict': klines_dict
                }
                
                logger.info(f"âœ“ Signal found for {symbol}: {analysis['consensus']} "
                          f"(Strength: {analysis['consensus_strength']})")
                return signal_data
            
            return None
            
        except Exception as e:
            logger.error(f"Error analyzing {symbol}: {e}")
            return None
    
    def scan_market(self, use_fast_scan=True, max_workers=0):
        """
        Scan the market for trading signals
        
        Args:
            use_fast_scan: Use parallel processing (default: True)
            max_workers: Number of concurrent threads (0 = auto-scale, default: 0)
        """
        logger.info(f"Starting market scan... (Fast: {use_fast_scan})")
        
        # Get all valid symbols
        symbol_infos = self.binance.get_all_symbols(
            quote_asset=config.QUOTE_ASSET,
            excluded_keywords=config.EXCLUDED_KEYWORDS,
            min_volume=config.MIN_VOLUME_USDT
        )
        
        if not symbol_infos:
            logger.warning("No symbols found to scan")
            return
        
        # Extract symbol names
        symbols = [s['symbol'] for s in symbol_infos]
        
        logger.info(f"Scanning {len(symbols)} symbols...")
        
        start_time = time.time()
        signals_found = []
        
        if use_fast_scan:
            # AUTO-SCALE workers based on number of symbols
            if max_workers == 0:
                # Smart scaling: 
                # 1-10 symbols: 5 workers
                # 11-50 symbols: 10 workers
                # 51-100 symbols: 15 workers
                # 100+ symbols: 20 workers (max)
                if len(symbols) <= 10:
                    max_workers = 5
                elif len(symbols) <= 50:
                    max_workers = 10
                elif len(symbols) <= 100:
                    max_workers = 15
                else:
                    max_workers = 20
                
                logger.info(f"Auto-scaled workers: {max_workers} (for {len(symbols)} symbols)")
            else:
                # Use provided max_workers but cap at 20
                max_workers = min(max_workers, 20)
            
            # FAST SCAN - Parallel processing
            self.telegram.send_message(
                f"ðŸ” <b>Fast Market Scan Started</b>\n\n"
                f"âš¡ Analyzing {len(symbols)} symbols\n"
                f"ðŸš€ Using {max_workers} parallel threads (auto-scaled)\n"
                f"â³ Please wait..."
            )
            
            completed_count = 0
            
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Submit all analysis tasks
                future_to_symbol = {
                    executor.submit(self.analyze_symbol, symbol): symbol 
                    for symbol in symbols
                }
                
                # Process results as they complete
                for future in as_completed(future_to_symbol):
                    symbol = future_to_symbol[future]
                    completed_count += 1
                    
                    try:
                        signal_data = future.result()
                        
                        if signal_data:
                            signals_found.append(signal_data)
                        
                        # Send progress update every 20%
                        progress_pct = (completed_count / len(symbols)) * 100
                        if completed_count % max(1, len(symbols) // 5) == 0:
                            elapsed = time.time() - start_time
                            avg_time = elapsed / completed_count
                            remaining = (len(symbols) - completed_count) * avg_time
                            
                            self.telegram.send_message(
                                f"â³ Progress: {completed_count}/{len(symbols)} ({progress_pct:.0f}%)\n"
                                f"ðŸ“Š Signals: {len(signals_found)}\n"
                                f"â±ï¸ Est. remaining: {remaining:.0f}s"
                            )
                    
                    except Exception as e:
                        logger.error(f"Error processing result for {symbol}: {e}")
        
        else:
            # NORMAL SCAN - Sequential processing
            for i, symbol in enumerate(symbols):
                logger.info(f"Analyzing {symbol} ({i+1}/{len(symbols)})...")
                
                signal_data = self.analyze_symbol(symbol)
                if signal_data:
                    signals_found.append(signal_data)
                
                # Small delay to avoid rate limits
                time.sleep(0.1)
        
        # Calculate performance
        total_time = time.time() - start_time
        avg_per_symbol = total_time / len(symbols) if len(symbols) > 0 else 0
        
        # Send results summary
        scan_mode = "âš¡ Fast" if use_fast_scan else "ðŸŒ Normal"
        summary_msg = (
            f"âœ… <b>{scan_mode} Market Scan Complete!</b>\n\n"
            f"â±ï¸ Time: {total_time:.1f}s ({avg_per_symbol:.2f}s per symbol)\n"
            f"ðŸ” Scanned: {len(symbols)} symbols\n"
            f"ðŸ“Š Signals found: {len(signals_found)}"
        )
        
        if use_fast_scan:
            summary_msg += f"\nâš¡ Threads used: {max_workers}"
        
        self.telegram.send_message(summary_msg)
        
        # Send results
        if signals_found:
            logger.info(f"Found {len(signals_found)} signals")
            self.send_signals(signals_found)
        else:
            logger.info("No signals found")
            if not config.SEND_SUMMARY_ONLY:
                self.telegram.send_message("ðŸ“Š Market scan complete. No signals detected.")
    
    def send_signals(self, signals_list):
        """Send signals to Telegram"""
        # Send summary first
        self.telegram.send_summary_table(signals_list)
        
        # If summary only mode, stop here
        if config.SEND_SUMMARY_ONLY:
            return
        
        # Add delay
        time.sleep(2)  # Give user time to see summary
        
        # Send RSI/MFI overview charts (for /scan command)
        if config.SEND_CHARTS and len(signals_list) > 0:
            self.telegram.send_message(f"📊 <b>Generating RSI/MFI overview charts by timeframe...</b>")
            
            try:
                chart_buffers = self.chart_gen.create_rsi_mfi_overview_charts(signals_list)
                
                if chart_buffers:
                    # chart_buffers is list of tuples: (indicator, timeframe, buffer)
                    for indicator, timeframe, chart_buf in chart_buffers:
                        emoji = "📊" if indicator == "RSI" else "💰"
                        self.telegram.send_photo(
                            chart_buf,
                            caption=f"{emoji} <b>{indicator} Overview - {timeframe}</b>\n"
                                   f"All coins with {indicator} signals on {timeframe} timeframe"
                        )
                        time.sleep(0.8)
                    
                    logger.info(f"✅ Sent {len(chart_buffers)} overview charts successfully")
                else:
                    logger.warning("No overview charts generated")
            except Exception as e:
                logger.error(f"Error sending overview charts: {e}")
        
        # Send notification before detailed analysis
        self.telegram.send_message(f"ðŸ“¤ <b>Sending detailed analysis for {len(signals_list[:config.MAX_COINS_PER_MESSAGE])} signals...</b>")
        time.sleep(1)
        
        # Send individual signals WITHOUT charts (already have overview)
        for signal in signals_list[:config.MAX_COINS_PER_MESSAGE]:
            # Send text alert only
            self.telegram.send_signal_alert(
                signal['symbol'],
                signal['timeframe_data'],
                signal['consensus'],
                signal['consensus_strength'],
                signal['price'],
                signal.get('market_data'),
                signal.get('volume_data')
            )
            
            time.sleep(1)  # Delay between messages
    
    def run(self):
        """Main bot loop - Commands only mode (no auto-scan)"""
        logger.info("Bot is now running in COMMAND-ONLY mode...")
        
        self.telegram.send_message(
            f"<b>ðŸ¤– BOT NOW RUNNING!</b>\n\n"
            f"<b>âš™ï¸ MODE:</b> Command-Only (Auto-scan OFF)\n"
            f"<b>ðŸ“Š Monitoring:</b> {config.QUOTE_ASSET} pairs\n"
            f"<b>ðŸŽ¯ Min Consensus:</b> {config.MIN_CONSENSUS_STRENGTH}/4\n"
            f"<b>âš¡ Fast Scan:</b> {'âœ… Enabled' if config.USE_FAST_SCAN else 'â❌Œ Disabled'}\n\n"
            f"<b>ðŸ’¬ AVAILABLE COMMANDS:</b>\n"
            f"â€¢ /<b>scan</b> - Run market scan\n"
            f"â€¢ /<b>BTC</b>, /<b>ETH</b> - Analyze coins\n"
            f"â€¢ /<b>help</b> - Show all commands\n\n"
            f"<i>ðŸ’¡ Use /scan to scan market anytime!</i>"
        )
        
        # Start command handler (blocking - this will run forever)
        try:
            logger.info("Starting command handler (blocking mode)...")
            self.command_handler.start_polling()
        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
            self.telegram.send_message("ðŸ›‘ <b>Bot stopped by user</b>")
        except Exception as e:
            logger.error(f"Error in command handler: {e}")
            self.telegram.send_message(f"â❌Œ <b>Bot error:</b> {str(e)}")


def main():
    """Main entry point"""
    print("""
    RSI + MFI Multi-Timeframe Trading Bot
        Binance + Telegram Integration
    """)
    
    # Check if config is set
    if "your_" in config.BINANCE_API_KEY or "your_" in config.TELEGRAM_BOT_TOKEN:
        print("\nâš ï¸  WARNING: Please configure your API keys in config.py first!\n")
        sys.exit(1)
    
    # Start bot
    bot = TradingBot()
    bot.run()


if __name__ == "__main__":
    main()

