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
        
        # Initialize command handler
        self.command_handler = TelegramCommandHandler(
            self.telegram,
            self.binance,
            self.chart_gen
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
🤖 <b>Trading Bot Started!</b>

✅ All systems operational
📊 Interactive commands enabled

<b>Quick Start:</b>
• Type /<b>BTC</b> for Bitcoin analysis
• Type /<b>ETH</b> for Ethereum analysis
• Type /<b>help</b> for all commands

<i>💡 Auto-scan runs every {}</i> seconds
            """.format(config.SCAN_INTERVAL)
            self.telegram.send_message(welcome_msg)
            return True
        else:
            logger.error("Connection test failed")
            return False
    
    def scan_market(self):
        """Scan the market for trading signals"""
        logger.info("Starting market scan...")
        
        # Get all valid symbols
        symbols = self.binance.get_all_symbols(
            quote_asset=config.QUOTE_ASSET,
            excluded_keywords=config.EXCLUDED_KEYWORDS,
            min_volume=config.MIN_VOLUME_USDT
        )
        
        if not symbols:
            logger.warning("No symbols found to scan")
            return
        
        logger.info(f"Scanning {len(symbols)} symbols...")
        
        signals_found = []
        
        for i, symbol_info in enumerate(symbols):
            symbol = symbol_info['symbol']
            logger.info(f"Analyzing {symbol} ({i+1}/{len(symbols)})...")
            
            try:
                # Get multi-timeframe data
                klines_dict = self.binance.get_multi_timeframe_data(
                    symbol, 
                    config.TIMEFRAMES,
                    limit=200  # Get enough data for indicators
                )
                
                if not klines_dict:
                    logger.warning(f"No data for {symbol}, skipping")
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
                    
                    signals_found.append(signal_data)
                    logger.info(f"Signal found for {symbol}: {analysis['consensus']} "
                              f"(Strength: {analysis['consensus_strength']})")
                
            except Exception as e:
                logger.error(f"Error analyzing {symbol}: {e}")
                continue
            
            # Small delay to avoid rate limits
            time.sleep(0.1)
        
        # Send results
        if signals_found:
            logger.info(f"Found {len(signals_found)} signals")
            self.send_signals(signals_found)
        else:
            logger.info("No signals found")
            if not config.SEND_SUMMARY_ONLY:
                self.telegram.send_message("📊 Market scan complete. No signals detected.")
    
    def send_signals(self, signals_list):
        """Send signals to Telegram"""
        # Send summary first
        self.telegram.send_summary_table(signals_list)
        
        # If summary only mode, stop here
        if config.SEND_SUMMARY_ONLY:
            return
        
        # Send individual signals with charts
        for signal in signals_list[:config.MAX_COINS_PER_MESSAGE]:
            # Send text alert
            self.telegram.send_signal_alert(
                signal['symbol'],
                signal['timeframe_data'],
                signal['consensus'],
                signal['consensus_strength'],
                signal['price'],
                signal.get('market_data')
            )
            
            # Send chart if enabled
            if config.SEND_CHARTS:
                # Create multi-timeframe chart
                chart_buf = self.chart_gen.create_multi_timeframe_chart(
                    signal['symbol'],
                    signal['timeframe_data'],
                    signal['price']
                )
                
                if chart_buf:
                    self.telegram.send_photo(
                        chart_buf,
                        caption=f"{signal['symbol']} - Multi-Timeframe Analysis"
                    )
            
            time.sleep(1)  # Delay between messages
    
    def run(self):
        """Main bot loop"""
        logger.info("Bot is now running...")
        
        # Start command handler in separate thread
        command_thread = threading.Thread(target=self.command_handler.start_polling, daemon=True)
        command_thread.start()
        logger.info("Command handler thread started")
        
        self.telegram.send_message(
            f"🤖 <b>Bot is now running!</b>\n\n"
            f"⚙️ Scan Interval: {config.SCAN_INTERVAL}s\n"
            f"📊 Monitoring: {config.QUOTE_ASSET} pairs\n"
            f"🎯 Min Consensus: {config.MIN_CONSENSUS_STRENGTH}/4\n\n"
            f"💬 <b>Commands ready!</b> Type /help for info"
        )
        
        while True:
            try:
                logger.info(f"\n{'='*50}")
                logger.info(f"Scan started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                logger.info(f"{'='*50}\n")
                
                self.scan_market()
                
                logger.info(f"\nNext scan in {config.SCAN_INTERVAL} seconds...")
                time.sleep(config.SCAN_INTERVAL)
                
            except KeyboardInterrupt:
                logger.info("Bot stopped by user")
                self.telegram.send_message("🛑 <b>Bot stopped by user</b>")
                break
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                time.sleep(60)  # Wait a minute before retrying


def main():
    """Main entry point"""
    print("""
    ╔═══════════════════════════════════════════╗
    ║   RSI + MFI Multi-Timeframe Trading Bot  ║
    ║        Binance + Telegram Integration    ║
    ╚═══════════════════════════════════════════╝
    """)
    
    # Check if config is set
    if "your_" in config.BINANCE_API_KEY or "your_" in config.TELEGRAM_BOT_TOKEN:
        print("\n⚠️  WARNING: Please configure your API keys in config.py first!\n")
        sys.exit(1)
    
    # Start bot
    bot = TradingBot()
    bot.run()


if __name__ == "__main__":
    main()
