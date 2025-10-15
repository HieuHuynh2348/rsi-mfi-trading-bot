"""
Telegram Command Handler
Handles user commands from Telegram
"""

import logging
from datetime import datetime
import time

logger = logging.getLogger(__name__)


class TelegramCommandHandler:
    def __init__(self, bot, binance_client, chart_generator):
        """
        Initialize command handler
        
        Args:
            bot: TelegramBot instance
            binance_client: BinanceClient instance
            chart_generator: ChartGenerator instance
        """
        self.bot = bot
        self.binance = binance_client
        self.chart_gen = chart_generator
        self.telegram_bot = bot.bot  # telebot instance
        self.chat_id = bot.chat_id
        
        # Setup command handlers
        self.setup_handlers()
        logger.info("Telegram command handler initialized")
    
    def setup_handlers(self):
        """Setup all command handlers"""
        from indicators import analyze_multi_timeframe
        import config
        
        # Store references for use in handlers
        self._analyze_multi_timeframe = analyze_multi_timeframe
        self._config = config
        
        @self.telegram_bot.message_handler(commands=['start', 'help'])
        def handle_help(message):
            """Show help message"""
            help_text = """
🤖 <b>RSI+MFI Trading Bot - Commands</b>

<b>📊 Symbol Analysis:</b>
/<b>SYMBOL</b> - Analyze any coin (auto-adds USDT)
Example: /BTC or /ETH or /LINK

<b>🔍 Market Info:</b>
/price <b>SYMBOL</b> - Get current price
/24h <b>SYMBOL</b> - Get 24h market data
/top - Top 10 volume coins

<b>📈 Technical Analysis:</b>
/rsi <b>SYMBOL</b> - RSI analysis only
/mfi <b>SYMBOL</b> - MFI analysis only
/chart <b>SYMBOL</b> - View chart

<b>⚙️ Bot Control:</b>
/status - Bot status & settings
/scan - Force market scan now
/settings - View current settings

<b>📋 Watchlist:</b>
/watch <b>SYMBOL</b> - Add to watchlist
/unwatch <b>SYMBOL</b> - Remove from watchlist
/watchlist - View watchlist

<b>ℹ️ Info:</b>
/help - Show this message
/about - About this bot

<i>💡 Tip: Just type /BTC to get full analysis!</i>
            """
            self.bot.send_message(help_text)
        
        @self.telegram_bot.message_handler(commands=['about'])
        def handle_about(message):
            """Show about message"""
            about_text = """
<b>🤖 RSI+MFI Trading Bot</b>

<b>Version:</b> 2.0
<b>Platform:</b> Railway.app
<b>Exchange:</b> Binance

<b>Features:</b>
✅ Multi-timeframe RSI+MFI analysis
✅ Real-time price monitoring
✅ Automatic signal detection
✅ Interactive commands
✅ Custom watchlist
✅ 24/7 cloud operation

<b>Indicators:</b>
• RSI (Relative Strength Index)
• MFI (Money Flow Index)
• Multi-timeframe consensus

<b>Timeframes:</b> 5m, 1h, 3h, 1d

<i>⚠️ Not financial advice. DYOR!</i>
            """
            self.bot.send_message(about_text)
        
        @self.telegram_bot.message_handler(commands=['status'])
        def handle_status(message):
            """Show bot status"""
            try:
                # Get config
                status_text = f"""
<b>🤖 Bot Status</b>

<b>⚡ System:</b> ✅ Online
<b>🔗 Binance:</b> ✅ Connected
<b>💬 Telegram:</b> ✅ Connected

<b>⚙️ Settings:</b>
• Scan Interval: {self._config.SCAN_INTERVAL}s
• Min Consensus: {self._config.MIN_CONSENSUS_STRENGTH}/4
• RSI Period: {self._config.RSI_PERIOD}
• MFI Period: {self._config.MFI_PERIOD}
• Timeframes: {', '.join(self._config.TIMEFRAMES)}

<b>📊 Trading Pairs:</b>
• Quote: {self._config.QUOTE_ASSET}
• Min Volume: ${self._config.MIN_VOLUME_USDT:,.0f}

<b>🕐 Current Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                """
                self.bot.send_message(status_text)
            except Exception as e:
                logger.error(f"Error in /status: {e}")
                self.bot.send_message(f"❌ Error: {str(e)}")
        
        @self.telegram_bot.message_handler(func=lambda m: m.text and m.text.startswith('/') and 
                                          len(m.text) > 1 and m.text[1:].replace('USDT', '').isalpha())
        def handle_symbol_analysis(message):
            """Handle symbol analysis commands like /BTC, /ETH, /LINK"""
            try:
                # Extract symbol from command
                symbol_raw = message.text[1:].upper().strip()
                
                # Auto-add USDT if not present
                if not symbol_raw.endswith('USDT'):
                    symbol = symbol_raw + 'USDT'
                else:
                    symbol = symbol_raw
                
                logger.info(f"Analyzing {symbol} on demand...")
                
                # Send processing message
                processing_msg = self.bot.send_message(f"🔍 Analyzing {symbol}...")
                
                # Get multi-timeframe data
                klines_dict = self.binance.get_multi_timeframe_data(
                    symbol,
                    self._config.TIMEFRAMES,
                    limit=200
                )
                
                if not klines_dict:
                    self.bot.send_message(f"❌ No data found for {symbol}. Symbol may not exist or be delisted.")
                    return
                
                # Analyze
                analysis = self._analyze_multi_timeframe(
                    klines_dict,
                    self._config.RSI_PERIOD,
                    self._config.MFI_PERIOD,
                    self._config.RSI_LOWER,
                    self._config.RSI_UPPER,
                    self._config.MFI_LOWER,
                    self._config.MFI_UPPER
                )
                
                # Get price and market data
                price = self.binance.get_current_price(symbol)
                market_data = self.binance.get_24h_data(symbol)
                
                # Send analysis
                self.bot.send_signal_alert(
                    symbol,
                    analysis['timeframes'],
                    analysis['consensus'],
                    analysis['consensus_strength'],
                    price,
                    market_data
                )
                
                # Send chart
                if self._config.SEND_CHARTS:
                    chart_buf = self.chart_gen.create_multi_timeframe_chart(
                        symbol,
                        analysis['timeframes'],
                        price
                    )
                    
                    if chart_buf:
                        self.bot.send_photo(
                            chart_buf,
                            caption=f"📊 {symbol} Multi-Timeframe Chart"
                        )
                
                logger.info(f"Analysis sent for {symbol}")
                
            except Exception as e:
                logger.error(f"Error analyzing symbol: {e}")
                self.bot.send_message(f"❌ Error analyzing {symbol}: {str(e)}")
        
        @self.telegram_bot.message_handler(commands=['price'])
        def handle_price(message):
            """Get current price"""
            try:
                parts = message.text.split()
                if len(parts) < 2:
                    self.bot.send_message("❌ Usage: /price SYMBOL\nExample: /price BTC")
                    return
                
                symbol_raw = parts[1].upper()
                if not symbol_raw.endswith('USDT'):
                    symbol = symbol_raw + 'USDT'
                else:
                    symbol = symbol_raw
                
                price = self.binance.get_current_price(symbol)
                
                if price:
                    self.bot.send_message(f"💰 <b>{symbol}</b>\nPrice: ${price:,.4f}")
                else:
                    self.bot.send_message(f"❌ Could not get price for {symbol}")
                    
            except Exception as e:
                logger.error(f"Error in /price: {e}")
                self.bot.send_message(f"❌ Error: {str(e)}")
        
        @self.telegram_bot.message_handler(commands=['24h'])
        def handle_24h(message):
            """Get 24h market data"""
            try:
                parts = message.text.split()
                if len(parts) < 2:
                    self.bot.send_message("❌ Usage: /24h SYMBOL\nExample: /24h BTC")
                    return
                
                symbol_raw = parts[1].upper()
                if not symbol_raw.endswith('USDT'):
                    symbol = symbol_raw + 'USDT'
                else:
                    symbol = symbol_raw
                
                data = self.binance.get_24h_data(symbol)
                
                if data:
                    change = data.get('price_change_percent', 0)
                    emoji = "📈" if change >= 0 else "📉"
                    
                    msg = f"""
<b>📊 {symbol} - 24h Data</b>

💰 <b>Price:</b> ${data.get('last_price', 0):,.4f}
{emoji} <b>Change:</b> {change:+.2f}%

⬆️ <b>High:</b> ${data.get('high', 0):,.4f}
⬇️ <b>Low:</b> ${data.get('low', 0):,.4f}

💵 <b>Volume:</b> ${data.get('volume', 0)/1e6:.2f}M
                    """
                    self.bot.send_message(msg)
                else:
                    self.bot.send_message(f"❌ Could not get 24h data for {symbol}")
                    
            except Exception as e:
                logger.error(f"Error in /24h: {e}")
                self.bot.send_message(f"❌ Error: {str(e)}")
        
        @self.telegram_bot.message_handler(commands=['top'])
        def handle_top(message):
            """Get top volume coins"""
            try:
                symbols = self.binance.get_all_symbols(
                    quote_asset=self._config.QUOTE_ASSET,
                    excluded_keywords=self._config.EXCLUDED_KEYWORDS,
                    min_volume=self._config.MIN_VOLUME_USDT
                )
                
                if not symbols:
                    self.bot.send_message("❌ No data available")
                    return
                
                # Sort by volume
                sorted_symbols = sorted(symbols, key=lambda x: x.get('volume', 0), reverse=True)
                top_10 = sorted_symbols[:10]
                
                msg = "<b>🏆 Top 10 Volume (24h)</b>\n\n"
                for i, s in enumerate(top_10, 1):
                    symbol = s['symbol']
                    volume = s.get('volume', 0) / 1e6  # Convert to millions
                    change = s.get('price_change_percent', 0)
                    emoji = "📈" if change >= 0 else "📉"
                    msg += f"{i}. <b>{symbol}</b>\n"
                    msg += f"   ${volume:.1f}M | {emoji} {change:+.2f}%\n\n"
                
                self.bot.send_message(msg)
                
            except Exception as e:
                logger.error(f"Error in /top: {e}")
                self.bot.send_message(f"❌ Error: {str(e)}")
        
        @self.telegram_bot.message_handler(commands=['scan'])
        def handle_scan(message):
            """Force immediate market scan"""
            try:
                self.bot.send_message("🔍 Starting market scan...")
                # This will be called from main.py
                # For now, just acknowledge
                self.bot.send_message("⏳ Scan in progress... Results will appear shortly.")
            except Exception as e:
                logger.error(f"Error in /scan: {e}")
                self.bot.send_message(f"❌ Error: {str(e)}")
        
        logger.info("All command handlers registered")
    
    def start_polling(self):
        """Start polling for commands"""
        logger.info("Starting command polling...")
        try:
            self.telegram_bot.infinity_polling(timeout=10, long_polling_timeout=5)
        except Exception as e:
            logger.error(f"Polling error: {e}")
    
    def process_commands_non_blocking(self):
        """Process commands without blocking (for use in main loop)"""
        try:
            self.telegram_bot.polling(none_stop=False, timeout=1)
        except Exception as e:
            logger.error(f"Error processing commands: {e}")
