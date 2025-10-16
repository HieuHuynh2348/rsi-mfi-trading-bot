"""
Telegram Command Handler
Handles user commands from Telegram
"""

import logging
from datetime import datetime
import time
from watchlist import WatchlistManager
from watchlist_monitor import WatchlistMonitor
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger(__name__)


class TelegramCommandHandler:
    def __init__(self, bot, binance_client, chart_generator, trading_bot_instance=None):
        """
        Initialize command handler
        
        Args:
            bot: TelegramBot instance
            binance_client: BinanceClient instance
            chart_generator: ChartGenerator instance
            trading_bot_instance: TradingBot instance (for /scan command)
        """
        self.bot = bot
        self.binance = binance_client
        self.chart_gen = chart_generator
        self.telegram_bot = bot.bot  # telebot instance
        self.chat_id = bot.chat_id
        self.trading_bot = trading_bot_instance  # Reference to main bot
        
        # Initialize watchlist manager
        self.watchlist = WatchlistManager()
        
        # Initialize watchlist monitor (auto-notification)
        self.monitor = WatchlistMonitor(self, check_interval=300)  # 5 minutes
        
        # Import config and indicators early for use in analyze_symbol
        import config
        from indicators import analyze_multi_timeframe
        self._config = config
        self._analyze_multi_timeframe = analyze_multi_timeframe
        
        # Setup command handlers
        self.setup_handlers()
        logger.info("Telegram command handler initialized")
    
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
                self._config.TIMEFRAMES,
                limit=200
            )
            
            if not klines_dict:
                logger.warning(f"No data for {symbol}")
                return None
            
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
            
            # Check if signal meets minimum consensus strength
            if analysis['consensus'] != 'NEUTRAL' and \
               analysis['consensus_strength'] >= self._config.MIN_CONSENSUS_STRENGTH:
                
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
                
                logger.info(f"✓ Signal found for {symbol}: {analysis['consensus']} "
                          f"(Strength: {analysis['consensus_strength']})")
                return signal_data
            
            return None
            
        except Exception as e:
            logger.error(f"Error analyzing {symbol}: {e}")
            return None
    
    def _analyze_symbol_full(self, symbol):
        """
        Analyze a symbol and return FULL analysis (regardless of signal)
        
        Args:
            symbol: Trading symbol
        
        Returns:
            Full analysis dict or None if error
        """
        try:
            # Get multi-timeframe data
            klines_dict = self.binance.get_multi_timeframe_data(
                symbol, 
                self._config.TIMEFRAMES,
                limit=200
            )
            
            if not klines_dict:
                logger.warning(f"No data for {symbol}")
                return None
            
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
            
            # Get current price and 24h data
            price = self.binance.get_current_price(symbol)
            market_data = self.binance.get_24h_data(symbol)
            
            # Check if has signal
            has_signal = (analysis['consensus'] != 'NEUTRAL' and 
                         analysis['consensus_strength'] >= self._config.MIN_CONSENSUS_STRENGTH)
            
            result_data = {
                'symbol': symbol,
                'timeframe_data': analysis['timeframes'],
                'consensus': analysis['consensus'],
                'consensus_strength': analysis['consensus_strength'],
                'price': price,
                'market_data': market_data,
                'klines_dict': klines_dict,
                'has_signal': has_signal
            }
            
            status = "✓ SIGNAL" if has_signal else "○ Neutral"
            logger.info(f"{status} - {symbol}: {analysis['consensus']} (Strength: {analysis['consensus_strength']})")
            
            return result_data
            
        except Exception as e:
            logger.error(f"Error analyzing {symbol}: {e}")
            return None
    
    def setup_handlers(self):
        """Setup all command handlers"""
        from indicators import analyze_multi_timeframe
        import config
        
        # Store references for use in handlers
        self._analyze_multi_timeframe = analyze_multi_timeframe
        self._config = config
        
        # List of registered commands (to exclude from symbol handler)
        self.registered_commands = [
            'start', 'help', 'about', 'status', 'price', '24h', 'top',
            'rsi', 'mfi', 'chart', 'scan', 'settings',
            'watch', 'unwatch', 'watchlist', 'scanwatch', 'clearwatch',
            'performance', 'startmonitor', 'stopmonitor', 'monitorstatus'
        ]
        
        # Allow commands from specific chat/group only (for security)
        def check_authorized(message):
            """Check if message is from authorized chat"""
            # Allow both private chat and group chat
            # Convert both to int for comparison (Telegram uses integers for chat IDs)
            try:
                msg_chat_id = int(message.chat.id)
                bot_chat_id = int(self.chat_id)
                
                logger.info(f"Received message from chat_id: {msg_chat_id}, authorized: {bot_chat_id}, type: {message.chat.type}")
                
                # Allow if match or if it's a private message to the bot
                is_authorized = (msg_chat_id == bot_chat_id) or (message.chat.type == 'private')
                logger.info(f"Authorization result: {is_authorized}")
                return is_authorized
            except (ValueError, TypeError) as e:
                logger.error(f"Error checking authorization: {e}")
                return False
        
        @self.telegram_bot.message_handler(commands=['start', 'help'])
        def handle_help(message):
            """Show help message"""
            if not check_authorized(message):
                logger.warning(f"Unauthorized access attempt from {message.chat.id}")
                return
            
            help_text = """
╔══════════════════════════╗
<b>  🤖 RSI+MFI TRADING BOT  </b>
╚══════════════════════════╝

<b>� SYMBOL ANALYSIS:</b>
/<b>SYMBOL</b> - Analyze any coin
Example: /BTC /ETH /LINK

<b>🔍 MARKET INFO:</b>
/price <b>SYMBOL</b> - Current price
/24h <b>SYMBOL</b> - 24h market data
/top - Top 10 volume coins

<b>📈 TECHNICAL ANALYSIS:</b>
/rsi <b>SYMBOL</b> - RSI only
/mfi <b>SYMBOL</b> - MFI only
/chart <b>SYMBOL</b> - View chart

<b>⚙️ BOT CONTROL:</b>
/status - Bot status & settings
/scan - Force market scan
/settings - View settings
/performance - Scan performance

<b>⭐ WATCHLIST:</b>
/watch <b>SYMBOL</b> - Add to watchlist
/unwatch <b>SYMBOL</b> - Remove coin
/watchlist - View watchlist
/scanwatch - Scan watchlist
/clearwatch - Clear all

<b>🔔 AUTO-MONITOR:</b>
/startmonitor - Start auto-notify
/stopmonitor - Stop auto-notify
/monitorstatus - Monitor status

<b>ℹ️ INFO:</b>
/help - Show this message
/about - About bot

<i>💡 Tip: Type /BTC for instant analysis!</i>
            """
            self.bot.send_message(help_text)
        
        @self.telegram_bot.message_handler(commands=['about'])
        def handle_about(message):
            """Show about message"""
            if not check_authorized(message):
                return
            
            about_text = """
╔══════════════════════════╗
<b>  🚀 RSI+MFI TRADING BOT  </b>
╚══════════════════════════╝

<b>📌 Version:</b> 2.0 ULTRA FAST
<b>☁️ Platform:</b> Railway.app
<b>🏦 Exchange:</b> Binance

<b>✨ FEATURES:</b>
✅ Multi-timeframe analysis
✅ RSI + MFI indicators
✅ Real-time monitoring
✅ Auto signal detection
✅ Interactive commands
✅ Custom watchlist
✅ ⚡ Parallel processing
✅ 24/7 cloud operation

<b>📊 INDICATORS:</b>
• RSI (Relative Strength Index)
• MFI (Money Flow Index)
• Multi-timeframe consensus

<b>⏱️ TIMEFRAMES:</b>
• 5m, 1h, 3h, 1d

<b>⚡ PERFORMANCE:</b>
• Auto-scaling: 5-20 workers
• 3-5x faster scanning
• Parallel analysis

<i>⚠️ Disclaimer: Not financial advice!</i>
<i>📚 Always do your own research (DYOR)</i>
            """
            self.bot.send_message(about_text)
        
        @self.telegram_bot.message_handler(commands=['status'])
        def handle_status(message):
            """Show bot status"""
            if not check_authorized(message):
                return
            
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
        
        @self.telegram_bot.message_handler(commands=['price'])
        def handle_price(message):
            """Get current price"""
            if not check_authorized(message):
                return
            
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
            if not check_authorized(message):
                return
            
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
                    
                    # Format volume intelligently
                    volume = data.get('volume', 0)
                    if volume >= 1e9:
                        vol_str = f"${volume/1e9:.2f}B"
                    elif volume >= 1e6:
                        vol_str = f"${volume/1e6:.2f}M"
                    elif volume >= 1e3:
                        vol_str = f"${volume/1e3:.2f}K"
                    else:
                        vol_str = f"${volume:.2f}"
                    
                    msg = f"""
<b>📊 {symbol} - 24h Data</b>

💰 <b>Price:</b> ${data.get('last_price', 0):,.4f}
{emoji} <b>Change:</b> {change:+.2f}%

⬆️ <b>High:</b> ${data.get('high', 0):,.4f}
⬇️ <b>Low:</b> ${data.get('low', 0):,.4f}

💵 <b>Volume:</b> {vol_str}
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
            if not check_authorized(message):
                return
            
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
                    volume = s.get('volume', 0)
                    
                    # Format volume intelligently
                    if volume >= 1e9:
                        vol_str = f"${volume/1e9:.2f}B"
                    elif volume >= 1e6:
                        vol_str = f"${volume/1e6:.1f}M"
                    elif volume >= 1e3:
                        vol_str = f"${volume/1e3:.1f}K"
                    else:
                        vol_str = f"${volume:.0f}"
                    
                    change = s.get('price_change_percent', 0)
                    emoji = "📈" if change >= 0 else "📉"
                    msg += f"{i}. <b>{symbol}</b>\n"
                    msg += f"   {vol_str} | {emoji} {change:+.2f}%\n\n"
                
                self.bot.send_message(msg)
                
            except Exception as e:
                logger.error(f"Error in /top: {e}")
                self.bot.send_message(f"❌ Error: {str(e)}")
        
        @self.telegram_bot.message_handler(commands=['scan'])
        def handle_scan(message):
            """Force immediate market scan (FAST MODE)"""
            if not check_authorized(message):
                return
            
            try:
                # Call scan_market from TradingBot instance with fast scan enabled
                if self.trading_bot:
                    logger.info("Manual FAST scan triggered by user")
                    self.trading_bot.scan_market(
                        use_fast_scan=self._config.USE_FAST_SCAN,
                        max_workers=self._config.MAX_SCAN_WORKERS
                    )
                    logger.info("Manual scan completed")
                else:
                    logger.error("TradingBot instance not available for /scan")
                    self.bot.send_message("❌ Scan functionality not available. "
                                        "Please restart the bot.")
                    
            except Exception as e:
                logger.error(f"Error in /scan: {e}")
                self.bot.send_message(f"❌ Error during scan: {str(e)}")
        
        @self.telegram_bot.message_handler(commands=['rsi'])
        def handle_rsi(message):
            """Get RSI analysis only"""
            if not check_authorized(message):
                return
            
            try:
                parts = message.text.split()
                if len(parts) < 2:
                    self.bot.send_message("❌ Usage: /rsi SYMBOL\nExample: /rsi BTC")
                    return
                
                symbol_raw = parts[1].upper()
                if not symbol_raw.endswith('USDT'):
                    symbol = symbol_raw + 'USDT'
                else:
                    symbol = symbol_raw
                
                logger.info(f"Getting RSI for {symbol}...")
                
                # Get multi-timeframe data
                klines_dict = self.binance.get_multi_timeframe_data(
                    symbol,
                    self._config.TIMEFRAMES,
                    limit=200
                )
                
                if not klines_dict:
                    self.bot.send_message(f"❌ No data found for {symbol}")
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
                
                # Build RSI-only message
                msg = f"<b>📊 RSI Analysis - {symbol}</b>\n\n"
                
                timeframes = sorted(analysis['timeframes'].keys(), 
                                  key=lambda x: {'5m': 1, '1h': 2, '4h': 3, '1d': 4}.get(x, 5))
                
                for tf in timeframes:
                    rsi_val = analysis['timeframes'][tf]['rsi']
                    emoji = "🔴" if rsi_val >= 80 else ("🟢" if rsi_val <= 20 else "⚪")
                    msg += f"RSI {tf.upper()}: {rsi_val:.2f} {emoji}\n"
                
                msg += f"\n⏰ {datetime.now().strftime('%H:%M:%S')}"
                self.bot.send_message(msg)
                
            except Exception as e:
                logger.error(f"Error in /rsi: {e}")
                self.bot.send_message(f"❌ Error: {str(e)}")
        
        @self.telegram_bot.message_handler(commands=['mfi'])
        def handle_mfi(message):
            """Get MFI analysis only"""
            if not check_authorized(message):
                return
            
            try:
                parts = message.text.split()
                if len(parts) < 2:
                    self.bot.send_message("❌ Usage: /mfi SYMBOL\nExample: /mfi BTC")
                    return
                
                symbol_raw = parts[1].upper()
                if not symbol_raw.endswith('USDT'):
                    symbol = symbol_raw + 'USDT'
                else:
                    symbol = symbol_raw
                
                logger.info(f"Getting MFI for {symbol}...")
                
                # Get multi-timeframe data
                klines_dict = self.binance.get_multi_timeframe_data(
                    symbol,
                    self._config.TIMEFRAMES,
                    limit=200
                )
                
                if not klines_dict:
                    self.bot.send_message(f"❌ No data found for {symbol}")
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
                
                # Build MFI-only message
                msg = f"<b>💰 MFI Analysis - {symbol}</b>\n\n"
                
                timeframes = sorted(analysis['timeframes'].keys(), 
                                  key=lambda x: {'5m': 1, '1h': 2, '4h': 3, '1d': 4}.get(x, 5))
                
                for tf in timeframes:
                    mfi_val = analysis['timeframes'][tf]['mfi']
                    emoji = "🔴" if mfi_val >= 80 else ("🟢" if mfi_val <= 20 else "⚪")
                    msg += f"MFI {tf.upper()}: {mfi_val:.2f} {emoji}\n"
                
                msg += f"\n⏰ {datetime.now().strftime('%H:%M:%S')}"
                self.bot.send_message(msg)
                
            except Exception as e:
                logger.error(f"Error in /mfi: {e}")
                self.bot.send_message(f"❌ Error: {str(e)}")
        
        @self.telegram_bot.message_handler(commands=['chart'])
        def handle_chart(message):
            """View chart for a symbol"""
            if not check_authorized(message):
                return
            
            try:
                parts = message.text.split()
                if len(parts) < 2:
                    self.bot.send_message("❌ Usage: /chart SYMBOL\nExample: /chart BTC")
                    return
                
                symbol_raw = parts[1].upper()
                if not symbol_raw.endswith('USDT'):
                    symbol = symbol_raw + 'USDT'
                else:
                    symbol = symbol_raw
                
                logger.info(f"Generating chart for {symbol}...")
                
                # Get multi-timeframe data
                klines_dict = self.binance.get_multi_timeframe_data(
                    symbol,
                    self._config.TIMEFRAMES,
                    limit=200
                )
                
                if not klines_dict:
                    self.bot.send_message(f"❌ No data found for {symbol}")
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
                
                price = self.binance.get_current_price(symbol)
                
                # Generate chart
                chart_buf = self.chart_gen.create_multi_timeframe_chart(
                    symbol,
                    analysis['timeframes'],
                    price,
                    klines_dict
                )
                
                if chart_buf:
                    self.bot.send_photo(
                        chart_buf,
                        caption=f"📊 {symbol} - Multi-Timeframe Chart"
                    )
                else:
                    self.bot.send_message(f"❌ Failed to generate chart for {symbol}")
                
            except Exception as e:
                logger.error(f"Error in /chart: {e}")
                self.bot.send_message(f"❌ Error: {str(e)}")
        
        @self.telegram_bot.message_handler(commands=['settings'])
        def handle_settings(message):
            """View current settings"""
            if not check_authorized(message):
                return
            
            try:
                settings_text = f"""
<b>⚙️ Bot Settings</b>

<b>📊 Indicators:</b>
• RSI Period: {self._config.RSI_PERIOD}
• RSI Levels: {self._config.RSI_LOWER} / {self._config.RSI_UPPER}
• MFI Period: {self._config.MFI_PERIOD}
• MFI Levels: {self._config.MFI_LOWER} / {self._config.MFI_UPPER}

<b>⏱️ Timeframes:</b>
• {', '.join(self._config.TIMEFRAMES)}

<b>🎯 Signal Criteria:</b>
• Min Consensus: {self._config.MIN_CONSENSUS_STRENGTH}/4
• Scan Interval: {self._config.SCAN_INTERVAL}s

<b>💹 Market Filters:</b>
• Quote Asset: {self._config.QUOTE_ASSET}
• Min Volume: ${self._config.MIN_VOLUME_USDT:,.0f}
• Excluded: {', '.join(self._config.EXCLUDED_KEYWORDS) if self._config.EXCLUDED_KEYWORDS else 'None'}

<b>📈 Display:</b>
• Send Charts: {'✅ Yes' if self._config.SEND_CHARTS else '❌ No'}
• Summary Only: {'✅ Yes' if self._config.SEND_SUMMARY_ONLY else '❌ No'}
• Max Coins/Message: {self._config.MAX_COINS_PER_MESSAGE}

<b>⚡ Performance:</b>
• Fast Scan: {'✅ Enabled' if self._config.USE_FAST_SCAN else '❌ Disabled'}
• Workers: {'Auto-scale' if self._config.MAX_SCAN_WORKERS == 0 else self._config.MAX_SCAN_WORKERS}

💡 Use /performance for detailed scan info
                """
                self.bot.send_message(settings_text)
            except Exception as e:
                logger.error(f"Error in /settings: {e}")
                self.bot.send_message(f"❌ Error: {str(e)}")
        
        @self.telegram_bot.message_handler(commands=['performance'])
        def handle_performance(message):
            """Show scan performance info"""
            if not check_authorized(message):
                return
            
            try:
                perf_text = f"""
<b>⚡ Scan Performance Info</b>

<b>🚀 Auto-Scaling Strategy:</b>

<b>Market Scan (/scan):</b>
• 1-10 symbols → 5 workers
• 11-50 symbols → 10 workers
• 51-100 symbols → 15 workers
• 100+ symbols → 20 workers (max)

<b>Watchlist Scan (/scanwatch):</b>
• 1-5 symbols → 3 workers
• 6-10 symbols → 5 workers
• 11-20 symbols → 10 workers
• 20+ symbols → 15 workers (max)

<b>📊 Expected Performance:</b>
• 5 symbols: ~3-4s (3 workers)
• 10 symbols: ~4-6s (5 workers)
• 50 symbols: ~15-20s (10 workers)
• 100 symbols: ~30-40s (15 workers)
• 200 symbols: ~60-80s (20 workers)

<b>⚙️ Current Settings:</b>
• Fast Scan: {'✅ Enabled' if self._config.USE_FAST_SCAN else '❌ Disabled'}
• Auto-scale: {'✅ Yes' if self._config.MAX_SCAN_WORKERS == 0 else f'❌ Fixed at {self._config.MAX_SCAN_WORKERS}'}

💡 <i>Workers scale automatically based on workload</i>
🔧 <i>No manual configuration needed!</i>
                """
                self.bot.send_message(perf_text)
            except Exception as e:
                logger.error(f"Error in /performance: {e}")
                self.bot.send_message(f"❌ Error: {str(e)}")
        
        @self.telegram_bot.message_handler(commands=['watch'])
        def handle_watch(message):
            """Add symbol to watchlist"""
            if not check_authorized(message):
                return
            
            try:
                parts = message.text.split()
                if len(parts) < 2:
                    self.bot.send_message("❌ Usage: /watch SYMBOL\nExample: /watch BTC")
                    return
                
                symbol_raw = parts[1].upper()
                
                # Add to watchlist
                success, msg = self.watchlist.add(symbol_raw)
                
                if success:
                    # Also show current count
                    count = self.watchlist.count()
                    msg += f"\n\n📊 Total watched: {count} symbols"
                    msg += f"\n💡 Use /watchlist to view all"
                
                self.bot.send_message(msg)
                
            except Exception as e:
                logger.error(f"Error in /watch: {e}")
                self.bot.send_message(f"❌ Error: {str(e)}")
        
        @self.telegram_bot.message_handler(commands=['unwatch'])
        def handle_unwatch(message):
            """Remove symbol from watchlist"""
            if not check_authorized(message):
                return
            
            try:
                parts = message.text.split()
                if len(parts) < 2:
                    self.bot.send_message("❌ Usage: /unwatch SYMBOL\nExample: /unwatch BTC")
                    return
                
                symbol_raw = parts[1].upper()
                
                # Remove from watchlist
                success, msg = self.watchlist.remove(symbol_raw)
                
                if success:
                    # Also show current count
                    count = self.watchlist.count()
                    msg += f"\n\n📊 Remaining: {count} symbols"
                    if count > 0:
                        msg += f"\n💡 Use /watchlist to view all"
                
                self.bot.send_message(msg)
                
            except Exception as e:
                logger.error(f"Error in /unwatch: {e}")
                self.bot.send_message(f"❌ Error: {str(e)}")
        
        @self.telegram_bot.message_handler(commands=['watchlist'])
        def handle_watchlist(message):
            """View watchlist"""
            if not check_authorized(message):
                return
            
            try:
                # Get formatted watchlist
                msg = self.watchlist.get_formatted_list()
                self.bot.send_message(msg)
                
            except Exception as e:
                logger.error(f"Error in /watchlist: {e}")
                self.bot.send_message(f"❌ Error: {str(e)}")
        
        @self.telegram_bot.message_handler(commands=['scanwatch'])
        def handle_scanwatch(message):
            """Scan watchlist only (FAST - using concurrent execution)"""
            if not check_authorized(message):
                return
            
            try:
                symbols = self.watchlist.get_all()
                
                if not symbols:
                    self.bot.send_message("❌ Your watchlist is empty!\n\n"
                                        "Use /watch SYMBOL to add coins.")
                    return
                
                # AUTO-SCALE workers based on watchlist size
                if len(symbols) <= 5:
                    max_workers = 3
                elif len(symbols) <= 10:
                    max_workers = 5
                elif len(symbols) <= 20:
                    max_workers = 10
                else:
                    max_workers = 15  # Max for watchlist
                
                self.bot.send_message(f"🔍 <b>Scanning ALL {len(symbols)} watchlist symbols...</b>\n\n"
                                    f"⚡ Using {max_workers} parallel threads (auto-scaled)\n"
                                    "� Will analyze and send ALL coins (not just signals).")
                
                analysis_results = []  # Store ALL analysis results
                errors_count = 0
                completed_count = 0
                
                # Send progress updates every N symbols
                progress_interval = 5 if len(symbols) > 10 else len(symbols)
                
                start_time = time.time()
                
                with ThreadPoolExecutor(max_workers=max_workers) as executor:
                    # Submit all analysis tasks
                    future_to_symbol = {
                        executor.submit(self._analyze_symbol_full, symbol): symbol 
                        for symbol in symbols
                    }
                    
                    # Process results as they complete
                    for future in as_completed(future_to_symbol):
                        symbol = future_to_symbol[future]
                        completed_count += 1
                        
                        try:
                            result = future.result()
                            
                            if result:
                                analysis_results.append(result)
                            else:
                                errors_count += 1
                            
                            # Send progress update
                            if completed_count % progress_interval == 0 and completed_count < len(symbols):
                                elapsed = time.time() - start_time
                                avg_time = elapsed / completed_count
                                remaining = (len(symbols) - completed_count) * avg_time
                                
                                self.bot.send_message(
                                    f"⏳ Progress: {completed_count}/{len(symbols)} analyzed\n"
                                    f"⏱️ Est. time remaining: {remaining:.1f}s"
                                )
                        
                        except Exception as e:
                            logger.error(f"Error processing result for {symbol}: {e}")
                            errors_count += 1
                
                # Calculate total time
                total_time = time.time() - start_time
                avg_per_symbol = total_time / len(symbols) if len(symbols) > 0 else 0
                
                # Send results for ALL analyzed coins
                if analysis_results:
                    logger.info(f"Analyzed {len(analysis_results)} symbols in watchlist")
                    
                    # Count signals
                    signals_count = sum(1 for r in analysis_results if r['has_signal'])
                    
                    # Send summary first
                    self.bot.send_message(
                        f"✅ <b>Watchlist Scan Complete!</b>\n\n"
                        f"⏱️ Time: {total_time:.1f}s ({avg_per_symbol:.2f}s per symbol)\n"
                        f"📊 Analyzed: {len(analysis_results)}/{len(symbols)} symbols\n"
                        f"🎯 Signals found: {signals_count}\n"
                        f"⚡ {max_workers} parallel threads used (auto-scaled)\n\n"
                        f"📤 Sending analysis for ALL {len(analysis_results)} coins..."
                    )
                    
                    # Send ALL analysis results (not just signals)
                    for i, result in enumerate(analysis_results, 1):
                        try:
                            # Send text alert for ALL coins
                            self.bot.send_signal_alert(
                                result['symbol'],
                                result['timeframe_data'],
                                result['consensus'],
                                result['consensus_strength'],
                                result['price'],
                                result.get('market_data')
                            )
                            
                            # Send chart if enabled
                            if self._config.SEND_CHARTS:
                                chart_buf = self.chart_gen.create_multi_timeframe_chart(
                                    result['symbol'],
                                    result['timeframe_data'],
                                    result['price'],
                                    result.get('klines_dict')
                                )
                                
                                if chart_buf:
                                    signal_tag = "🎯 SIGNAL" if result['has_signal'] else "📊 Analysis"
                                    self.bot.send_photo(
                                        chart_buf,
                                        caption=f"{signal_tag} - {result['symbol']} ({i}/{len(analysis_results)})"
                                    )
                            
                            # Small delay between messages
                            time.sleep(0.5)
                            
                        except Exception as e:
                            logger.error(f"Error sending analysis for {result['symbol']}: {e}")
                            continue
                    
                    self.bot.send_message(
                        f"🎯 <b>All {len(analysis_results)} watchlist analyses sent!</b>\n\n"
                        f"✅ Signals: {signals_count}\n"
                        f"📊 Neutral: {len(analysis_results) - signals_count}"
                    )
                    
                else:
                    logger.info("No analysis results from watchlist")
                    msg = f"❌ <b>Scan Failed</b>\n\n"
                    msg += f"⏱️ Time: {total_time:.1f}s\n"
                    msg += f"🔍 Attempted to scan {len(symbols)} symbols.\n"
                    msg += f"⚠️ {errors_count} error(s) occurred.\n\n"
                    msg += f"Please check if symbols are valid."
                    
                    self.bot.send_message(msg)
                
            except Exception as e:
                logger.error(f"Error in /scanwatch: {e}")
                self.bot.send_message(f"❌ Error during watchlist scan: {str(e)}")
        
        @self.telegram_bot.message_handler(commands=['clearwatch'])
        def handle_clearwatch(message):
            """Clear entire watchlist"""
            if not check_authorized(message):
                return
            
            try:
                count = self.watchlist.count()
                
                if count == 0:
                    self.bot.send_message("ℹ️ Your watchlist is already empty.")
                    return
                
                # Clear watchlist
                cleared = self.watchlist.clear()
                
                self.bot.send_message(f"🗑️ <b>Watchlist Cleared</b>\n\n"
                                    f"Removed {cleared} symbols.\n\n"
                                    f"💡 Use /watch SYMBOL to add coins again.")
                
            except Exception as e:
                logger.error(f"Error in /clearwatch: {e}")
                self.bot.send_message(f"❌ Error: {str(e)}")
        
        @self.telegram_bot.message_handler(commands=['startmonitor'])
        def handle_startmonitor(message):
            """Start auto-monitoring watchlist"""
            if not check_authorized(message):
                return
            
            try:
                if self.monitor.running:
                    self.bot.send_message("ℹ️ <b>Monitor already running!</b>\n\n"
                                        f"⏱️ Check interval: {self.monitor.check_interval//60} min\n"
                                        f"📊 Watchlist: {self.watchlist.count()} coins")
                    return
                
                count = self.watchlist.count()
                if count == 0:
                    self.bot.send_message("⚠️ <b>Watchlist is empty!</b>\n\n"
                                        "Add coins first with /watch SYMBOL")
                    return
                
                self.monitor.start()
                
                self.bot.send_message(f"✅ <b>Watchlist Monitor Started!</b>\n\n"
                                    f"⏱️ Check interval: {self.monitor.check_interval//60} min\n"
                                    f"📊 Monitoring: {count} coins\n"
                                    f"🔔 Will auto-notify when signals appear\n\n"
                                    f"💡 Use /stopmonitor to stop")
                
            except Exception as e:
                logger.error(f"Error in /startmonitor: {e}")
                self.bot.send_message(f"❌ Error: {str(e)}")
        
        @self.telegram_bot.message_handler(commands=['stopmonitor'])
        def handle_stopmonitor(message):
            """Stop auto-monitoring watchlist"""
            if not check_authorized(message):
                return
            
            try:
                if not self.monitor.running:
                    self.bot.send_message("ℹ️ Monitor is not running.")
                    return
                
                self.monitor.stop()
                
                self.bot.send_message(f"⏸️ <b>Watchlist Monitor Stopped</b>\n\n"
                                    f"🔕 Auto-notifications disabled\n\n"
                                    f"💡 Use /startmonitor to resume")
                
            except Exception as e:
                logger.error(f"Error in /stopmonitor: {e}")
                self.bot.send_message(f"❌ Error: {str(e)}")
        
        @self.telegram_bot.message_handler(commands=['monitorstatus'])
        def handle_monitorstatus(message):
            """Show monitor status"""
            if not check_authorized(message):
                return
            
            try:
                status_icon = "🟢" if self.monitor.running else "🔴"
                status_text = "RUNNING" if self.monitor.running else "STOPPED"
                
                msg = f"{status_icon} <b>Monitor Status: {status_text}</b>\n\n"
                msg += f"⏱️ Check interval: {self.monitor.check_interval//60} min ({self.monitor.check_interval}s)\n"
                msg += f"📊 Watchlist: {self.watchlist.count()} coins\n"
                msg += f"💾 Signal history: {len(self.monitor.last_signals)} records\n\n"
                
                if self.monitor.running:
                    msg += "🔔 Auto-notifications: ON\n"
                    msg += "💡 Use /stopmonitor to pause"
                else:
                    msg += "🔕 Auto-notifications: OFF\n"
                    msg += "💡 Use /startmonitor to resume"
                
                self.bot.send_message(msg)
                
            except Exception as e:
                logger.error(f"Error in /monitorstatus: {e}")
                self.bot.send_message(f"❌ Error: {str(e)}")
        
        # ===== SYMBOL ANALYSIS HANDLER (MUST BE LAST) =====
        @self.telegram_bot.message_handler(func=lambda m: m.text and m.text.startswith('/') and 
                                          len(m.text) > 1 and m.text[1:].split()[0].upper() not in 
                                          [cmd.upper() for cmd in self.registered_commands] and
                                          m.text[1:].replace('USDT', '').replace('usdt', '').isalnum())
        def handle_symbol_analysis(message):
            """Handle symbol analysis commands like /BTC, /ETH, /LINK"""
            if not check_authorized(message):
                return
            
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
                
                # Send charts (2 separate charts)
                if self._config.SEND_CHARTS:
                    # Chart 1: Candlestick + Volume + RSI + MFI (single timeframe - 3h default)
                    main_tf = '3h' if '3h' in self._config.TIMEFRAMES else self._config.TIMEFRAMES[0]
                    
                    if main_tf in klines_dict and main_tf in analysis['timeframes']:
                        from indicators import calculate_rsi, calculate_mfi
                        
                        df = klines_dict[main_tf]
                        tf_analysis = analysis['timeframes'][main_tf]
                        
                        # Calculate RSI and MFI series for the chart
                        rsi_series = calculate_rsi(df, self._config.RSI_PERIOD)
                        mfi_series = calculate_mfi(df, self._config.MFI_PERIOD)
                        
                        chart1_buf = self.chart_gen.create_rsi_mfi_chart(
                            symbol,
                            df,
                            rsi_series,
                            mfi_series,
                            self._config.RSI_LOWER,
                            self._config.RSI_UPPER,
                            self._config.MFI_LOWER,
                            self._config.MFI_UPPER,
                            main_tf
                        )
                        
                        if chart1_buf:
                            self.bot.send_photo(
                                chart1_buf,
                                caption=f"📈 {symbol} - Candlestick Chart ({main_tf.upper()})\nWith RSI & MFI Indicators"
                            )
                    
                    # Chart 2: Multi-timeframe candlestick charts (TradingView style)
                    # Pass both analysis and klines_dict for candlestick plotting
                    chart2_buf = self.chart_gen.create_multi_timeframe_chart(
                        symbol,
                        analysis['timeframes'],
                        price,
                        klines_dict  # Pass the DataFrame dict for candlestick plotting
                    )
                    
                    if chart2_buf:
                        self.bot.send_photo(
                            chart2_buf,
                            caption=f"📊 {symbol} - Multi-Timeframe Candlestick Charts\nAll Timeframes Overview"
                        )
                
                logger.info(f"Analysis sent for {symbol}")
                
            except Exception as e:
                logger.error(f"Error analyzing symbol: {e}")
                self.bot.send_message(f"❌ Error analyzing {symbol}: {str(e)}")
        
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
