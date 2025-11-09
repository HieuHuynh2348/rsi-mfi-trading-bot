"""
Telegram Command Handler
Handles user commands from Telegram
"""

import logging
from datetime import datetime
import time
from watchlist import WatchlistManager
from watchlist_monitor import WatchlistMonitor
from volume_detector import VolumeDetector
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
        
        # Use monitor's volume detector for signal alerts (shared instance)
        self.volume_detector = self.monitor.volume_detector
        
        # Import config and indicators early for use in analyze_symbol
        import config
        from indicators import analyze_multi_timeframe
        from bot_detector import BotDetector
        self._config = config
        self._analyze_multi_timeframe = analyze_multi_timeframe
        
        # Initialize bot detector BEFORE bot monitor and market scanner
        self.bot_detector = BotDetector(binance_client)
        
        # Initialize market scanner (extreme RSI/MFI detection) - AFTER bot_detector
        from market_scanner import MarketScanner
        self.market_scanner = MarketScanner(self, scan_interval=900)  # 15 minutes
        
        # Initialize bot activity monitor (requires bot_detector)
        # Default mode: 'all' - scan top 50 coins by volume independently
        from bot_monitor import BotMonitor
        self.bot_monitor = BotMonitor(self, check_interval=1800, scan_mode='all')  # 30 minutes, all mode
        
        # Initialize real-time pump detector (3-layer detection system)
        from pump_detector_realtime import RealtimePumpDetector
        self.pump_detector = RealtimePumpDetector(binance_client, bot, self.bot_detector, self.watchlist)
        
        # Initialize Stoch+RSI multi-timeframe analyzer
        from stoch_rsi_analyzer import StochRSIAnalyzer
        self.stoch_rsi_analyzer = StochRSIAnalyzer(binance_client)
        
        # Initialize Gemini AI Analyzer
        from gemini_analyzer import GeminiAnalyzer
        gemini_api_key = "AIzaSyAjyq7CwNWJfK-JaRoXSTXVmKt2t_C0fd0"
        self.gemini_analyzer = GeminiAnalyzer(gemini_api_key, binance_client, self.stoch_rsi_analyzer)
        
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
            
            # Get volume analysis
            volume_data = None
            if self.volume_detector:
                try:
                    # Use main timeframe (5m) for volume analysis
                    main_tf = self._config.TIMEFRAMES[0] if self._config.TIMEFRAMES else '5m'
                    if main_tf in klines_dict:
                        volume_result = self.volume_detector.detect(klines_dict[main_tf], symbol)
                        if volume_result:  # ✅ Always get volume data, not just anomalies
                            volume_data = volume_result
                            logger.info(f"Volume analysis for {symbol}: Current={volume_result.get('current_volume', 0):.0f}, Last={volume_result.get('last_volume', 0):.0f}, Anomaly={volume_result.get('is_anomaly', False)}")
                except Exception as e:
                    logger.error(f"Volume analysis failed for {symbol}: {e}")
            
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
                'volume_data': volume_data,
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
            'rsi', 'mfi', 'chart', 'scan', 'settings', 'menu',
            'watch', 'unwatch', 'watchlist', 'scanwatch', 'clearwatch',
            'performance', 'startmonitor', 'stopmonitor', 'monitorstatus',
            'volumescan', 'volumesensitivity',
            'startmarketscan', 'stopmarketscan', 'marketstatus',
            'startbotmonitor', 'stopbotmonitor', 'botmonitorstatus', 'botscan', 'botthreshold',
            'startpumpwatch', 'stoppumpwatch', 'pumpstatus', 'pumpscan',
            'stochrsi'
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
        
        # ===== CALLBACK QUERY HANDLER =====
        @self.telegram_bot.callback_query_handler(func=lambda call: True)
        def handle_callback(call):
            """Handle inline keyboard button presses"""
            if not check_authorized(call.message):
                return
            
            try:
                # Answer callback to remove loading state
                self.telegram_bot.answer_callback_query(call.id)
                
                data = call.data
                
                # Main menu
                if data == "cmd_menu":
                    keyboard = self.bot.create_main_menu_keyboard()
                    self.telegram_bot.edit_message_text(
                        chat_id=call.message.chat.id,
                        message_id=call.message.message_id,
                        text="<b>🤖 MAIN MENU</b>\n\nChoose an option:",
                        parse_mode='HTML',
                        reply_markup=keyboard
                    )
                
                # Quick analysis
                elif data.startswith("analyze_"):
                    symbol = data.replace("analyze_", "")
                    self.telegram_bot.send_message(
                        chat_id=call.message.chat.id,
                        text=f"🔍 Analyzing {symbol}..."
                    )
                    result = self._analyze_symbol_full(symbol)
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

                # View chart request
                elif data.startswith("viewchart_"):
                    symbol = data.replace("viewchart_", "").upper().strip()
                    symbol = symbol.replace('&AMP;', '&').replace('&amp;', '&')
                    try:
                        self.telegram_bot.send_message(chat_id=call.message.chat.id, text=f"📈 Generating chart for {symbol}...")
                        # Generate a chart image for the symbol using chart generator
                        # Use last analysis data if available via trading bot, otherwise perform quick analysis
                        if self.trading_bot:
                            try:
                                # Attempt to get full analysis for the symbol
                                result = self._analyze_symbol_full(symbol)
                                if result and 'klines_dict' in result:
                                    buf = self.chart_gen.create_price_chart(symbol, result['klines_dict'])
                                    if buf:
                                        self.bot.send_photo(buf, caption=f"📈 <b>{symbol}</b> - Price Chart")
                                        return
                            except Exception:
                                pass

                        # Fallback: request quick chart from Binance client
                        klines = self.binance.get_klines(symbol, '1h', limit=200)
                        buf = self.chart_gen.create_price_chart(symbol, {'1h': klines} if klines is not None else None)
                        if buf:
                            self.bot.send_photo(buf, caption=f"📈 <b>{symbol}</b> - Price Chart")
                        else:
                            self.telegram_bot.send_message(chat_id=call.message.chat.id, text=f"❌ Could not generate chart for {symbol}")
                    except Exception as e:
                        logger.error(f"Error generating chart for {symbol}: {e}")
                        self.telegram_bot.send_message(chat_id=call.message.chat.id, text=f"❌ Error generating chart: {e}")

                # Add to watchlist request
                elif data.startswith("addwatch_"):
                    symbol = data.replace("addwatch_", "").upper().strip()
                    symbol = symbol.replace('&AMP;', '&').replace('&amp;', '&')
                    try:
                        success, message = self.watchlist.add(symbol)
                        # Update user immediately
                        self.telegram_bot.send_message(chat_id=call.message.chat.id, text=message)
                    except Exception as e:
                        logger.error(f"Error adding {symbol} to watchlist: {e}")
                        self.telegram_bot.send_message(chat_id=call.message.chat.id, text=f"❌ Error adding to watchlist: {e}")
                
                # Volume sensitivity
                elif data.startswith("vol_"):
                    sensitivity = data.replace("vol_", "")
                    old = self.monitor.volume_detector.sensitivity
                    self.monitor.volume_detector.sensitivity = sensitivity
                    self.monitor.volume_detector.config = self.monitor.volume_detector.thresholds[sensitivity]
                    
                    keyboard = self.bot.create_volume_keyboard()
                    self.telegram_bot.edit_message_text(
                        chat_id=call.message.chat.id,
                        message_id=call.message.message_id,
                        text=f"✅ Sensitivity updated: {old.upper()} → {sensitivity.upper()}",
                        parse_mode='HTML',
                        reply_markup=keyboard
                    )
                
                # Command callbacks - use simplified approach
                elif data.startswith("cmd_"):
                    cmd = data.replace("cmd_", "")
                    # Create a fake message object to reuse handlers
                    fake_msg = call.message
                    fake_msg.text = f"/{cmd}"
                    
                    # Route to appropriate handler
                    if cmd == "scan":
                        handle_scan(fake_msg)
                    elif cmd == "scanwatch":
                        handle_scanwatch(fake_msg)
                    elif cmd == "watchlist":
                        handle_watchlist(fake_msg)
                    elif cmd == "clearwatch":
                        handle_clearwatch(fake_msg)
                    elif cmd == "volumescan":
                        handle_volumescan(fake_msg)
                    elif cmd == "volumesensitivity":
                        current = self.monitor.volume_detector.sensitivity
                        keyboard = self.bot.create_volume_keyboard()
                        self.telegram_bot.send_message(
                            chat_id=call.message.chat.id,
                            text=f"<b>🎯 Volume Sensitivity</b>\n\nCurrent: <b>{current.upper()}</b>\n\nSelect level:",
                            parse_mode='HTML',
                            reply_markup=keyboard
                        )
                    elif cmd == "quickanalysis":
                        keyboard = self.bot.create_quick_analysis_keyboard()
                        self.telegram_bot.send_message(
                            chat_id=call.message.chat.id,
                            text="<b>🔍 Quick Analysis</b>\n\nSelect a coin to analyze:",
                            parse_mode='HTML',
                            reply_markup=keyboard
                        )
                    elif cmd == "startmonitor":
                        handle_startmonitor(fake_msg)
                    elif cmd == "stopmonitor":
                        handle_stopmonitor(fake_msg)
                    elif cmd == "monitorstatus":
                        handle_monitorstatus(fake_msg)
                    elif cmd == "top":
                        handle_top(fake_msg)
                    elif cmd == "status":
                        handle_status(fake_msg)
                    elif cmd == "settings":
                        handle_settings(fake_msg)
                    elif cmd == "performance":
                        handle_performance(fake_msg)
                    elif cmd == "help":
                        handle_help(fake_msg)
                    elif cmd == "about":
                        handle_about(fake_msg)
                    elif cmd == "startmarketscan":
                        handle_startmarketscan(fake_msg)
                    elif cmd == "stopmarketscan":
                        handle_stopmarketscan(fake_msg)
                    elif cmd == "marketstatus":
                        handle_marketstatus(fake_msg)
                    elif cmd == "startbotmonitor":
                        handle_startbotmonitor(fake_msg)
                    elif cmd == "stopbotmonitor":
                        handle_stopbotmonitor(fake_msg)
                    elif cmd == "botmonitorstatus":
                        handle_botmonitorstatus(fake_msg)
                    elif cmd == "botscan":
                        handle_botscan(fake_msg)
                    elif cmd == "botthreshold":
                        # Show bot threshold help
                        status = self.bot_monitor.get_status()
                        keyboard = self.bot.create_bot_monitor_keyboard()
                        self.telegram_bot.send_message(
                            chat_id=call.message.chat.id,
                            text=f"<b>🎯 Ngưỡng Phát Hiện Bot</b>\n\n"
                                 f"<b>Hiện tại:</b>\n"
                                 f"🤖 Bot: {status['bot_threshold']}%\n"
                                 f"🚀 Pump: {status['pump_threshold']}%\n\n"
                                 f"<b>Dùng lệnh:</b>\n"
                                 f"/botthreshold bot 75\n"
                                 f"/botthreshold pump 80",
                            parse_mode='HTML',
                            reply_markup=keyboard
                        )
                    elif cmd == "startpumpwatch":
                        handle_startpumpwatch(fake_msg)
                    elif cmd == "stoppumpwatch":
                        handle_stoppumpwatch(fake_msg)
                    elif cmd == "pumpstatus":
                        handle_pumpstatus(fake_msg)
                
                # Pump scan callbacks
                elif data.startswith("pumpscan_"):
                    if data == "pumpscan_all":
                        # Scan all coins for pump signals
                        self.telegram_bot.send_message(
                            chat_id=call.message.chat.id,
                            text=f"🌐 <b>QUÉT TẤT CẢ THỊ TRƯỜNG</b>\n\n"
                                 f"🔍 Đang quét tất cả USDT coins qua Layer 1...\n"
                                 f"⏳ Quá trình có thể mất 2-5 phút\n\n"
                                 f"💡 Chỉ hiển thị coins có Layer 1 >= 60%",
                            parse_mode='HTML'
                        )
                        
                        # Get all USDT symbols
                        symbols = self.binance.get_all_usdt_symbols()
                        if not symbols:
                            self.telegram_bot.send_message(
                                chat_id=call.message.chat.id,
                                text="❌ Không thể lấy danh sách coins",
                                parse_mode='HTML'
                            )
                            return
                        
                        logger.info(f"Pump scan all: scanning {len(symbols)} coins...")
                        
                        # Scan Layer 1 for all coins (parallel)
                        from concurrent.futures import ThreadPoolExecutor, as_completed
                        detections = []
                        
                        with ThreadPoolExecutor(max_workers=10) as executor:
                            futures = {
                                executor.submit(self.pump_detector._analyze_layer1, symbol): symbol 
                                for symbol in symbols[:200]  # Limit to top 200 by volume
                            }
                            
                            for future in as_completed(futures):
                                try:
                                    result = future.result()
                                    if result and result.get('pump_score', 0) >= 60:
                                        detections.append(result)
                                except Exception as e:
                                    logger.debug(f"Error in Layer 1 scan: {e}")
                        
                        # Sort by score
                        detections.sort(key=lambda x: x.get('pump_score', 0), reverse=True)
                        
                        if not detections:
                            self.telegram_bot.send_message(
                                chat_id=call.message.chat.id,
                                text=f"✅ <b>QUÉT HOÀN TẤT</b>\n\n"
                                     f"🔍 Đã quét {len(symbols[:200])} coins\n"
                                     f"❌ Không tìm thấy pump signals >= 60%\n\n"
                                     f"💡 Thử lại sau 15-30 phút",
                                parse_mode='HTML'
                            )
                            return
                        
                        # Send summary
                        summary = f"<b>🚀 PHÁT HIỆN PUMP SIGNALS</b>\n\n"
                        summary += f"🔍 Quét: {len(symbols[:200])} coins\n"
                        summary += f"⚡ Tìm thấy: <b>{len(detections)}</b> signals >= 60%\n\n"
                        summary += f"<b>TOP {min(10, len(detections))} PUMP CANDIDATES:</b>\n\n"
                        
                        # Show top 10
                        for i, detection in enumerate(detections[:10], 1):
                            symbol = detection['symbol']
                            score = detection['pump_score']
                            indicators = detection.get('indicators', {})
                            
                            volume_spike = indicators.get('volume_spike', 0)
                            price_change = indicators.get('price_change_5m', 0)
                            rsi = indicators.get('current_rsi', 0)
                            
                            if score >= 80:
                                emoji = "🔴"
                            elif score >= 70:
                                emoji = "🟡"
                            else:
                                emoji = "🟢"
                            
                            summary += f"{emoji} <b>{i}. {symbol}</b> - {score:.0f}%\n"
                            summary += f"   💧 Vol: {volume_spike:.1f}x | 📈 +{price_change:.1f}% | RSI: {rsi:.0f}\n\n"
                        
                        if len(detections) > 10:
                            summary += f"ℹ️ +{len(detections) - 10} coins khác\n\n"
                        
                        summary += f"💡 <i>Dùng /pumpscan SYMBOL để phân tích chi tiết</i>"
                        
                        keyboard = self.bot.create_pump_detector_keyboard()
                        self.telegram_bot.send_message(
                            chat_id=call.message.chat.id,
                            text=summary,
                            parse_mode='HTML',
                            reply_markup=keyboard
                        )
                        return
                    
                    # Single symbol scan
                    symbol = data.replace("pumpscan_", "")
                    self.telegram_bot.send_message(
                        chat_id=call.message.chat.id,
                        text=f"🔍 <b>Đang phân tích {symbol} qua 3 layers...</b>\n\n⏳ Vui lòng chờ 10-15 giây...",
                        parse_mode='HTML'
                    )
                    
                    # Perform pump scan
                    result = self.pump_detector.manual_scan(symbol)
                    
                    if not result:
                        self.telegram_bot.send_message(
                            chat_id=call.message.chat.id,
                            text=f"❌ <b>Không thể phân tích {symbol}</b>\n\n"
                                 "Symbol có thể không tồn tại hoặc thiếu dữ liệu.",
                            parse_mode='HTML'
                        )
                        return
                    
                    # Build result message
                    msg = f"<b>📊 PUMP ANALYSIS - {symbol}</b>\n\n"
                    msg += f"<b>Kết Quả:</b> {result['result']}\n\n"
                    
                    if 'final_score' in result:
                        score = result['final_score']
                        msg += f"<b>🎯 Điểm Tổng Hợp: {score:.0f}%</b>\n\n"
                        
                        if score >= 90:
                            msg += "✅ <b>PUMP RẤT CAO - 90%+ chính xác</b>\n"
                        elif score >= 80:
                            msg += "✅ <b>PUMP CAO - 80%+ chính xác</b>\n"
                        else:
                            msg += "⚠️ <b>Dưới ngưỡng - Không khuyến nghị</b>\n"
                    
                    # Layer details (abbreviated for callback)
                    if 'layer1' in result and result['layer1']:
                        layer1 = result['layer1']
                        msg += f"\n⚡ Layer 1 (5m): {layer1['pump_score']:.0f}%"
                    
                    if 'layer2' in result and result['layer2']:
                        layer2 = result['layer2']
                        msg += f" | ✅ Layer 2: {layer2['pump_score']:.0f}%"
                    
                    if 'layer3' in result and result['layer3']:
                        layer3 = result['layer3']
                        msg += f" | 📈 Layer 3: {layer3['pump_score']:.0f}%"
                    
                    msg += f"\n\n⚠️ <i>Phân tích kỹ thuật - không phải tư vấn tài chính</i>"
                    
                    keyboard = self.bot.create_pump_detector_keyboard()
                    self.telegram_bot.send_message(
                        chat_id=call.message.chat.id,
                        text=msg,
                        parse_mode='HTML',
                        reply_markup=keyboard
                    )
                
                # Stoch+RSI callbacks
                elif data.startswith("stochrsi_"):
                    symbol = data.replace("stochrsi_", "")
                    
                    self.telegram_bot.send_message(
                        chat_id=call.message.chat.id,
                        text=f"🔍 <b>STOCH+RSI MULTI-TF ANALYSIS</b>\n\n"
                             f"📊 Đang phân tích {symbol} trên 4 timeframes...\n"
                             f"⏳ Vui lòng chờ...",
                        parse_mode='HTML'
                    )
                    
                    # Perform multi-timeframe analysis
                    result = self.stoch_rsi_analyzer.analyze_multi_timeframe(
                        symbol, 
                        timeframes=['1m', '5m', '4h', '1d']
                    )
                    
                    if not result or 'error' in result:
                        self.telegram_bot.send_message(
                            chat_id=call.message.chat.id,
                            text=f"❌ <b>Không thể phân tích {symbol}</b>\n\n"
                                 "Symbol có thể không tồn tại hoặc thiếu dữ liệu.",
                            parse_mode='HTML'
                        )
                        return
                    
                    # Format message
                    msg = self.stoch_rsi_analyzer.format_analysis_message(result, include_details=True)
                    
                    keyboard = self.bot.create_stoch_rsi_keyboard()
                    self.telegram_bot.send_message(
                        chat_id=call.message.chat.id,
                        text=msg,
                        parse_mode='HTML',
                        reply_markup=keyboard
                    )
                
                elif data == "cmd_stochrsi_menu":
                    # Show Stoch+RSI menu
                    msg = f"<b>📊 STOCH+RSI MULTI-TIMEFRAME ANALYZER</b>\n\n"
                    msg += f"<b>Phân tích kết hợp Stochastic + RSI trên 4 khung thời gian:</b>\n"
                    msg += f"   • 1 phút (1m)\n"
                    msg += f"   • 5 phút (5m)\n"
                    msg += f"   • 4 giờ (4h)\n"
                    msg += f"   • 1 ngày (1D)\n\n"
                    msg += f"<b>✨ Tính Năng:</b>\n"
                    msg += f"   ✅ OHLC/4 smoother signals\n"
                    msg += f"   ✅ Custom RSI với RMA\n"
                    msg += f"   ✅ Stochastic oscillator\n"
                    msg += f"   ✅ Consensus từ 4 timeframes\n\n"
                    msg += f"<b>🎯 Signals:</b>\n"
                    msg += f"   🟢 BUY - Khi cả RSI và Stoch oversold\n"
                    msg += f"   🔴 SELL - Khi cả RSI và Stoch overbought\n"
                    msg += f"   ⚪ NEUTRAL - Không có consensus\n\n"
                    msg += f"💡 <i>Chọn coin bên dưới để phân tích hoặc dùng /stochrsi SYMBOL</i>"
                    
                    keyboard = self.bot.create_stoch_rsi_keyboard()
                    self.telegram_bot.send_message(
                        chat_id=call.message.chat.id,
                        text=msg,
                        parse_mode='HTML',
                        reply_markup=keyboard
                    )
                
                elif data == "cmd_stochrsi_info":
                    # Show info about Stoch+RSI
                    msg = f"<b>ℹ️ STOCH+RSI MULTI-TF - THÔNG TIN</b>\n\n"
                    msg += f"<b>📊 Cách Hoạt Động:</b>\n\n"
                    msg += f"<b>1. OHLC/4:</b>\n"
                    msg += f"   Tính trung bình (O+H+L+C)/4\n"
                    msg += f"   Giảm nhiễu, tín hiệu mượt hơn close price\n\n"
                    msg += f"<b>2. RSI (RMA):</b>\n"
                    msg += f"   Length: 6\n"
                    msg += f"   Oversold: < 20\n"
                    msg += f"   Overbought: > 80\n\n"
                    msg += f"<b>3. Stochastic:</b>\n"
                    msg += f"   %K Period: 6\n"
                    msg += f"   Smooth: 6\n"
                    msg += f"   %D Period: 6\n"
                    msg += f"   Oversold: < 20, Overbought: > 80\n\n"
                    msg += f"<b>4. Consensus Signal:</b>\n"
                    msg += f"   ✅ Cả RSI và Stoch phải đồng ý\n"
                    msg += f"   ✅ Tính signal cho 4 timeframes\n"
                    msg += f"   ✅ Tổng hợp consensus cuối cùng\n\n"
                    msg += f"<b>💡 Cách Sử Dụng:</b>\n"
                    msg += f"   • Tín hiệu BUY mạnh: 3-4/4 TF đồng thuận\n"
                    msg += f"   • Tín hiệu SELL mạnh: 3-4/4 TF đồng thuận\n"
                    msg += f"   • Kết hợp với Pump Detector để xác nhận\n"
                    msg += f"   • Kiểm tra Volume trước khi vào lệnh\n\n"
                    msg += f"<b>⚙️ Command:</b>\n"
                    msg += f"   /stochrsi BTCUSDT\n"
                    msg += f"   /stochrsi ETH"
                    
                    keyboard = self.bot.create_stoch_rsi_keyboard()
                    self.telegram_bot.send_message(
                        chat_id=call.message.chat.id,
                        text=msg,
                        parse_mode='HTML',
                        reply_markup=keyboard
                    )
                
                # AI Analysis callbacks
                elif data.startswith("ai_analyze_"):
                    symbol = data.replace("ai_analyze_", "")
                    
                    # Send processing message
                    self.telegram_bot.send_message(
                        chat_id=call.message.chat.id,
                        text=f"🤖 <b>GEMINI AI ANALYSIS</b>\n\n"
                             f"💎 Đang phân tích {symbol}...\n"
                             f"📊 Thu thập dữ liệu từ tất cả indicators\n"
                             f"🧠 Gọi Gemini 2.5 Pro API\n\n"
                             f"⏳ Vui lòng chờ 10-20 giây...",
                        parse_mode='HTML'
                    )
                    
                    # Check if we have pump data for this symbol
                    pump_data = None
                    if symbol in self.pump_detector.detected_pumps:
                        pump_data = self.pump_detector.detected_pumps[symbol]
                    
                    # Perform AI analysis
                    try:
                        result = self.gemini_analyzer.analyze(
                            symbol, 
                            pump_data=pump_data, 
                            trading_style='swing',
                            use_cache=True
                        )
                        
                        if not result:
                            self.telegram_bot.send_message(
                                chat_id=call.message.chat.id,
                                text=f"❌ <b>Không thể phân tích {symbol}</b>\n\n"
                                     "Có thể do:\n"
                                     "• Lỗi Gemini API\n"
                                     "• Thiếu dữ liệu market\n"
                                     "• Rate limit\n\n"
                                     "💡 Vui lòng thử lại sau vài phút.",
                                parse_mode='HTML'
                            )
                            return
                        
                        # Format into 3 messages
                        msg1, msg2, msg3 = self.gemini_analyzer.format_response(result)
                        
                        # Send 3 messages sequentially
                        self.telegram_bot.send_message(
                            chat_id=call.message.chat.id,
                            text=msg1,
                            parse_mode='HTML'
                        )
                        
                        time.sleep(1)  # Small delay between messages
                        
                        self.telegram_bot.send_message(
                            chat_id=call.message.chat.id,
                            text=msg2,
                            parse_mode='HTML'
                        )
                        
                        time.sleep(1)
                        
                        self.telegram_bot.send_message(
                            chat_id=call.message.chat.id,
                            text=msg3,
                            parse_mode='HTML'
                        )
                        
                        logger.info(f"✅ Sent AI analysis for {symbol} to user")
                        
                    except Exception as e:
                        logger.error(f"Error in AI analysis for {symbol}: {e}", exc_info=True)
                        self.telegram_bot.send_message(
                            chat_id=call.message.chat.id,
                            text=f"❌ <b>Lỗi trong quá trình phân tích AI</b>\n\n"
                                 f"Error: {str(e)}\n\n"
                                 f"💡 Vui lòng báo admin hoặc thử lại sau.",
                            parse_mode='HTML'
                        )
                
            except Exception as e:
                logger.error(f"Error handling callback: {e}")
                self.telegram_bot.answer_callback_query(call.id, text=f"Error: {str(e)}")
        
        @self.telegram_bot.message_handler(commands=['start', 'help'])
        def handle_help(message):
            """Show help message"""
            if not check_authorized(message):
                logger.warning(f"Unauthorized access attempt from {message.chat.id}")
                return
            
            # Use Vietnamese help message
            from vietnamese_messages import HELP_MESSAGE
            keyboard = self.bot.create_main_menu_keyboard()
            self.bot.send_message(HELP_MESSAGE, reply_markup=keyboard)
        
        @self.telegram_bot.message_handler(commands=['menu'])
        def handle_menu(message):
            """Show interactive menu with buttons"""
            if not check_authorized(message):
                return
            
            try:
                keyboard = self.bot.create_main_menu_keyboard()
                self.bot.send_message(
                    "<b>🤖 MENU CHÍNH</b>\n\n"
                    "Chọn một tùy chọn bên dưới hoặc dùng /help để xem lệnh văn bản:",
                    reply_markup=keyboard
                )
            except Exception as e:
                logger.error(f"Error in /menu: {e}")
                self.bot.send_message(f"❌ Lỗi: {str(e)}")
        
        @self.telegram_bot.message_handler(commands=['about'])
        def handle_about(message):
            """Show about message"""
            if not check_authorized(message):
                return
            
            from vietnamese_messages import ABOUT_MESSAGE
            keyboard = self.bot.create_main_menu_keyboard()
            self.bot.send_message(ABOUT_MESSAGE, reply_markup=keyboard)
        
        @self.telegram_bot.message_handler(commands=['status'])
        def handle_status(message):
            """Show bot status"""
            if not check_authorized(message):
                return
            
            try:
                from vietnamese_messages import get_status_message
                status_text = get_status_message(self._config)
                keyboard = self.bot.create_main_menu_keyboard()
                self.bot.send_message(status_text, reply_markup=keyboard)
            except Exception as e:
                logger.error(f"Error in /status: {e}")
                keyboard = self.bot.create_main_menu_keyboard()
                self.bot.send_message(f"❌ Error: {str(e)}", reply_markup=keyboard)
        
        @self.telegram_bot.message_handler(commands=['price'])
        def handle_price(message):
            """Get current price"""
            if not check_authorized(message):
                return
            
            try:
                parts = message.text.split()
                if len(parts) < 2:
                    from vietnamese_messages import PRICE_USAGE
                    self.bot.send_message(PRICE_USAGE)
                    return
                
                symbol_raw = parts[1].upper()
                if not symbol_raw.endswith('USDT'):
                    symbol = symbol_raw + 'USDT'
                else:
                    symbol = symbol_raw
                
                price = self.binance.get_current_price(symbol)
                
                if price:
                    keyboard = self.bot.create_quick_analysis_keyboard()
                    self.bot.send_message(f"💰 <b>{symbol}</b>\nGiá: ${price:,.4f}", reply_markup=keyboard)
                else:
                    keyboard = self.bot.create_main_menu_keyboard()
                    self.bot.send_message(f"❌ Không thể lấy giá cho {symbol}", reply_markup=keyboard)
                    
            except Exception as e:
                logger.error(f"Error in /price: {e}")
                keyboard = self.bot.create_main_menu_keyboard()
                from vietnamese_messages import ERROR_OCCURRED
                self.bot.send_message(ERROR_OCCURRED.format(error=str(e)), reply_markup=keyboard)
        
        @self.telegram_bot.message_handler(commands=['24h'])
        def handle_24h(message):
            """Get 24h market data"""
            if not check_authorized(message):
                return
            
            try:
                parts = message.text.split()
                if len(parts) < 2:
                    from vietnamese_messages import DAILY_USAGE
                    self.bot.send_message(DAILY_USAGE)
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
<b>📊 {symbol} - Dữ liệu 24h</b>

💰 <b>Giá:</b> ${data.get('last_price', 0):,.4f}
{emoji} <b>Thay đổi:</b> {change:+.2f}%

⬆️ <b>Cao nhất:</b> ${data.get('high', 0):,.4f}
⬇️ <b>Thấp nhất:</b> ${data.get('low', 0):,.4f}

💵 <b>Khối lượng:</b> {vol_str}
                    """
                    keyboard = self.bot.create_quick_analysis_keyboard()
                    self.bot.send_message(msg, reply_markup=keyboard)
                else:
                    keyboard = self.bot.create_main_menu_keyboard()
                    self.bot.send_message(f"❌ Không thể lấy dữ liệu 24h cho {symbol}", reply_markup=keyboard)
                    
            except Exception as e:
                logger.error(f"Error in /24h: {e}")
                keyboard = self.bot.create_main_menu_keyboard()
                from vietnamese_messages import ERROR_OCCURRED
                self.bot.send_message(ERROR_OCCURRED.format(error=str(e)), reply_markup=keyboard)
        
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
                    self.bot.send_message("❌ Không có dữ liệu")
                    return
                
                # Sort by volume
                sorted_symbols = sorted(symbols, key=lambda x: x.get('volume', 0), reverse=True)
                top_10 = sorted_symbols[:10]
                
                msg = "<b>🏆 Top 10 Khối Lượng (24h)</b>\n\n"
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
                
                # Send with action keyboard
                keyboard = self.bot.create_action_keyboard()
                self.bot.send_message(msg, reply_markup=keyboard)
                
            except Exception as e:
                logger.error(f"Error in /top: {e}")
                keyboard = self.bot.create_main_menu_keyboard()
                from vietnamese_messages import ERROR_OCCURRED
                self.bot.send_message(ERROR_OCCURRED.format(error=str(e)), reply_markup=keyboard)
        
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
                    self.bot.send_message("❌ Cách dùng: /rsi SYMBOL\nVí dụ: /rsi BTC")
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
                    self.bot.send_message(f"❌ Không tìm thấy dữ liệu cho {symbol}")
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
                msg = f"<b>📊 Phân Tích RSI - {symbol}</b>\n\n"
                
                timeframes = sorted(analysis['timeframes'].keys(), 
                                  key=lambda x: {'5m': 1, '1h': 2, '4h': 3, '1d': 4}.get(x, 5))
                
                for tf in timeframes:
                    rsi_val = analysis['timeframes'][tf]['rsi']
                    emoji = "🔴" if rsi_val >= 80 else ("🟢" if rsi_val <= 20 else "⚪")
                    msg += f"RSI {tf.upper()}: {rsi_val:.2f} {emoji}\n"
                
                msg += f"\n⏰ {datetime.now().strftime('%H:%M:%S')}"
                keyboard = self.bot.create_quick_analysis_keyboard()
                self.bot.send_message(msg, reply_markup=keyboard)
                
            except Exception as e:
                logger.error(f"Error in /rsi: {e}")
                keyboard = self.bot.create_main_menu_keyboard()
                from vietnamese_messages import ERROR_OCCURRED
                self.bot.send_message(ERROR_OCCURRED.format(error=str(e)), reply_markup=keyboard)
        
        @self.telegram_bot.message_handler(commands=['mfi'])
        def handle_mfi(message):
            """Get MFI analysis only"""
            if not check_authorized(message):
                return
            
            try:
                parts = message.text.split()
                if len(parts) < 2:
                    self.bot.send_message("❌ Cách dùng: /mfi SYMBOL\nVí dụ: /mfi BTC")
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
                    self.bot.send_message(f"❌ Không tìm thấy dữ liệu cho {symbol}")
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
                msg = f"<b>💰 Phân Tích MFI - {symbol}</b>\n\n"
                
                timeframes = sorted(analysis['timeframes'].keys(), 
                                  key=lambda x: {'5m': 1, '1h': 2, '4h': 3, '1d': 4}.get(x, 5))
                
                for tf in timeframes:
                    mfi_val = analysis['timeframes'][tf]['mfi']
                    emoji = "🔴" if mfi_val >= 80 else ("🟢" if mfi_val <= 20 else "⚪")
                    msg += f"MFI {tf.upper()}: {mfi_val:.2f} {emoji}\n"
                
                msg += f"\n⏰ {datetime.now().strftime('%H:%M:%S')}"
                keyboard = self.bot.create_quick_analysis_keyboard()
                self.bot.send_message(msg, reply_markup=keyboard)
                
            except Exception as e:
                logger.error(f"Error in /mfi: {e}")
                keyboard = self.bot.create_main_menu_keyboard()
                from vietnamese_messages import ERROR_OCCURRED
                self.bot.send_message(ERROR_OCCURRED.format(error=str(e)), reply_markup=keyboard)
        
        @self.telegram_bot.message_handler(commands=['chart'])
        def handle_chart(message):
            """View chart for a symbol"""
            if not check_authorized(message):
                return
            
            try:
                parts = message.text.split()
                if len(parts) < 2:
                    self.bot.send_message("❌ Cách dùng: /chart SYMBOL\nVí dụ: /chart BTC")
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
                    self.bot.send_message(f"❌ Không tìm thấy dữ liệu cho {symbol}")
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
                from vietnamese_messages import get_settings_message
                settings_text = get_settings_message(self._config)
                keyboard = self.bot.create_main_menu_keyboard()
                self.bot.send_message(settings_text, reply_markup=keyboard)
            except Exception as e:
                logger.error(f"Error in /settings: {e}")
                keyboard = self.bot.create_main_menu_keyboard()
                from vietnamese_messages import ERROR_OCCURRED
                self.bot.send_message(ERROR_OCCURRED.format(error=str(e)), reply_markup=keyboard)
        
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
                keyboard = self.bot.create_main_menu_keyboard()
                self.bot.send_message(perf_text, reply_markup=keyboard)
            except Exception as e:
                logger.error(f"Error in /performance: {e}")
                keyboard = self.bot.create_main_menu_keyboard()
                self.bot.send_message(f"❌ Error: {str(e)}", reply_markup=keyboard)
        
        @self.telegram_bot.message_handler(commands=['watch'])
        def handle_watch(message):
            """Add symbol to watchlist"""
            if not check_authorized(message):
                return
            
            try:
                parts = message.text.split()
                if len(parts) < 2:
                    from vietnamese_messages import WATCH_USAGE
                    self.bot.send_message(WATCH_USAGE)
                    return
                
                symbol_raw = parts[1].upper()
                
                # Add to watchlist
                success, msg = self.watchlist.add(symbol_raw)
                
                if success:
                    # Also show current count
                    count = self.watchlist.count()
                    from vietnamese_messages import WATCHLIST_COUNT
                    msg += f"\n\n{WATCHLIST_COUNT.format(count=count)}"
                    msg += f"\n💡 Dùng /watchlist để xem tất cả"
                
                # Send with watchlist keyboard
                keyboard = self.bot.create_watchlist_keyboard()
                self.bot.send_message(msg, reply_markup=keyboard)
                
            except Exception as e:
                logger.error(f"Error in /watch: {e}")
                keyboard = self.bot.create_main_menu_keyboard()
                from vietnamese_messages import ERROR_OCCURRED
                self.bot.send_message(ERROR_OCCURRED.format(error=str(e)), reply_markup=keyboard)
        
        @self.telegram_bot.message_handler(commands=['unwatch'])
        def handle_unwatch(message):
            """Remove symbol from watchlist"""
            if not check_authorized(message):
                return
            
            try:
                parts = message.text.split()
                if len(parts) < 2:
                    from vietnamese_messages import UNWATCH_USAGE
                    self.bot.send_message(UNWATCH_USAGE)
                    return
                
                symbol_raw = parts[1].upper()
                
                # Remove from watchlist
                success, msg = self.watchlist.remove(symbol_raw)
                
                if success:
                    # Also show current count
                    count = self.watchlist.count()
                    msg += f"\n\n📊 Còn lại: {count} symbols"
                    if count > 0:
                        msg += f"\n💡 Dùng /watchlist để xem tất cả"
                
                # Send with watchlist keyboard
                keyboard = self.bot.create_watchlist_keyboard()
                self.bot.send_message(msg, reply_markup=keyboard)
                
            except Exception as e:
                logger.error(f"Error in /unwatch: {e}")
                keyboard = self.bot.create_main_menu_keyboard()
                self.bot.send_message(f"❌ Error: {str(e)}", reply_markup=keyboard)
        
        @self.telegram_bot.message_handler(commands=['watchlist'])
        def handle_watchlist(message):
            """View watchlist"""
            if not check_authorized(message):
                return
            
            try:
                # Get formatted watchlist
                msg = self.watchlist.get_formatted_list()
                keyboard = self.bot.create_watchlist_keyboard()
                self.bot.send_message(msg, reply_markup=keyboard)
                
            except Exception as e:
                logger.error(f"Error in /watchlist: {e}")
                keyboard = self.bot.create_main_menu_keyboard()
                self.bot.send_message(f"❌ Error: {str(e)}", reply_markup=keyboard)
        
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
                                result.get('market_data'),
                                result.get('volume_data')
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
                    
                    keyboard = self.bot.create_action_keyboard()
                    self.bot.send_message(
                        f"🎯 <b>All {len(analysis_results)} watchlist analyses sent!</b>\n\n"
                        f"✅ Signals: {signals_count}\n"
                        f"📊 Neutral: {len(analysis_results) - signals_count}",
                        reply_markup=keyboard
                    )
                    
                else:
                    logger.info("No analysis results from watchlist")
                    msg = f"❌ <b>Scan Failed</b>\n\n"
                    msg += f"⏱️ Time: {total_time:.1f}s\n"
                    msg += f"🔍 Attempted to scan {len(symbols)} symbols.\n"
                    msg += f"⚠️ {errors_count} error(s) occurred.\n\n"
                    msg += f"Please check if symbols are valid."
                    
                    keyboard = self.bot.create_main_menu_keyboard()
                    self.bot.send_message(msg, reply_markup=keyboard)
                
            except Exception as e:
                logger.error(f"Error in /scanwatch: {e}")
                keyboard = self.bot.create_main_menu_keyboard()
                self.bot.send_message(f"❌ Error during watchlist scan: {str(e)}", reply_markup=keyboard)
        
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
                
                keyboard = self.bot.create_watchlist_keyboard()
                self.bot.send_message(f"🗑️ <b>Watchlist Cleared</b>\n\n"
                                    f"Removed {cleared} symbols.\n\n"
                                    f"💡 Use /watch SYMBOL to add coins again.",
                                    reply_markup=keyboard)
                
            except Exception as e:
                logger.error(f"Error in /clearwatch: {e}")
                keyboard = self.bot.create_main_menu_keyboard()
                self.bot.send_message(f"❌ Error: {str(e)}", reply_markup=keyboard)
        
        @self.telegram_bot.message_handler(commands=['startmonitor'])
        def handle_startmonitor(message):
            """Start auto-monitoring watchlist"""
            if not check_authorized(message):
                return
            
            try:
                if self.monitor.running:
                    self.bot.send_message("ℹ️ <b>Giám sát đã đang chạy!</b>\n\n"
                                        f"⏱️ Khoảng thời gian kiểm tra: {self.monitor.check_interval//60} phút\n"
                                        f"📊 Watchlist: {self.watchlist.count()} đồng")
                    return
                
                count = self.watchlist.count()
                if count == 0:
                    self.bot.send_message("⚠️ <b>Watchlist trống!</b>\n\n"
                                        "Thêm coin trước với /watch SYMBOL")
                    return
                
                self.monitor.start()
                
                keyboard = self.bot.create_monitor_keyboard()
                self.bot.send_message(f"✅ <b>Giám Sát Watchlist Đã Bắt Đầu!</b>\n\n"
                                    f"⏱️ Khoảng thời gian kiểm tra: {self.monitor.check_interval//60} phút\n"
                                    f"📊 Đang giám sát: {count} đồng\n"
                                    f"🔔 Sẽ tự động thông báo khi có tín hiệu\n\n"
                                    f"💡 Dùng /stopmonitor để dừng",
                                    reply_markup=keyboard)
                
            except Exception as e:
                logger.error(f"Error in /startmonitor: {e}")
                keyboard = self.bot.create_main_menu_keyboard()
                from vietnamese_messages import ERROR_OCCURRED
                self.bot.send_message(ERROR_OCCURRED.format(error=str(e)), reply_markup=keyboard)
        
        @self.telegram_bot.message_handler(commands=['stopmonitor'])
        def handle_stopmonitor(message):
            """Stop auto-monitoring watchlist"""
            if not check_authorized(message):
                return
            
            try:
                if not self.monitor.running:
                    self.bot.send_message("ℹ️ Giám sát không chạy.")
                    return
                
                self.monitor.stop()
                
                keyboard = self.bot.create_monitor_keyboard()
                self.bot.send_message(f"⏸️ <b>Giám Sát Watchlist Đã Dừng</b>\n\n"
                                    f"🔕 Thông báo tự động đã tắt\n\n"
                                    f"💡 Dùng /startmonitor để tiếp tục",
                                    reply_markup=keyboard)
                
            except Exception as e:
                logger.error(f"Error in /stopmonitor: {e}")
                keyboard = self.bot.create_main_menu_keyboard()
                from vietnamese_messages import ERROR_OCCURRED
                self.bot.send_message(ERROR_OCCURRED.format(error=str(e)), reply_markup=keyboard)
        
        @self.telegram_bot.message_handler(commands=['monitorstatus'])
        def handle_monitorstatus(message):
            """Show monitor status"""
            if not check_authorized(message):
                return
            
            try:
                status_icon = "🟢" if self.monitor.running else "🔴"
                status_text = "ĐANG CHẠY" if self.monitor.running else "ĐÃ DỪNG"
                
                msg = f"{status_icon} <b>Trạng Thái Giám Sát: {status_text}</b>\n\n"
                msg += f"⏱️ Khoảng thời gian kiểm tra: {self.monitor.check_interval//60} phút ({self.monitor.check_interval}s)\n"
                msg += f"📊 Watchlist: {self.watchlist.count()} đồng\n"
                msg += f"💾 Lịch sử tín hiệu: {len(self.monitor.last_signals)} bản ghi\n\n"
                
                if self.monitor.running:
                    msg += "🔔 Thông báo tự động: BẬT\n"
                    msg += f"📊 Giám sát khối lượng: {self.monitor.volume_check_interval//60} phút\n"
                    msg += f"🎯 Độ nhạy khối lượng: {self.monitor.volume_detector.sensitivity.upper()}\n\n"
                    msg += "💡 Dùng /stopmonitor để tạm dừng"
                else:
                    msg += "🔕 Thông báo tự động: TẮT\n"
                    msg += "💡 Dùng /startmonitor để tiếp tục"
                
                keyboard = self.bot.create_monitor_keyboard()
                self.bot.send_message(msg, reply_markup=keyboard)
                
            except Exception as e:
                logger.error(f"Error in /monitorstatus: {e}")
                keyboard = self.bot.create_main_menu_keyboard()
                self.bot.send_message(f"❌ Error: {str(e)}", reply_markup=keyboard)
        
        @self.telegram_bot.message_handler(commands=['startmarketscan'])
        def handle_startmarketscan(message):
            """Start automatic market scanner"""
            logger.info(f"Received /startmarketscan command from chat {message.chat.id}")
            
            if not check_authorized(message):
                logger.warning(f"/startmarketscan: Unauthorized access attempt from {message.chat.id}")
                return
            
            try:
                logger.info("/startmarketscan: Checking scanner status...")
                if self.market_scanner.running:
                    logger.info("/startmarketscan: Scanner already running")
                    msg = "⚠️ Market scanner is already running!\n\n"
                    msg += "💡 Use /marketstatus to check status"
                else:
                    logger.info("/startmarketscan: Starting scanner...")
                    success = self.market_scanner.start()
                    logger.info(f"/startmarketscan: Scanner start result: {success}")
                    
                    if success:
                        msg = "✅ <b>Market Scanner Started!</b>\n\n"
                        msg += "🔍 <b>What it does:</b>\n"
                        msg += "   • Scans ALL Binance USDT pairs\n"
                        msg += "   • Calculates 1D RSI & MFI\n"
                        msg += "   • Alerts based on RSI only (&gt;80 or &lt;20)\n"
                        msg += "   • 🤖 Detects bot activity automatically\n"
                        msg += "   • 🚀 Identifies pump patterns\n"
                        msg += "   • ⚠️ Warns about dump risks\n\n"
                        msg += f"⏱️ <b>Scan interval:</b> {self.market_scanner.scan_interval//60} minutes\n"
                        msg += f"📊 <b>RSI alert levels:</b> &lt;{self.market_scanner.rsi_lower} or &gt;{self.market_scanner.rsi_upper}\n"
                        msg += f"💰 <b>MFI (display only):</b> {self.market_scanner.mfi_lower}-{self.market_scanner.mfi_upper}\n"
                        msg += f"🔔 <b>Cooldown:</b> 1 hour per coin\n\n"
                        msg += "⚡ <b>Early Entry Signals:</b>\n"
                        msg += "   🚀 Pump + Oversold RSI = STRONG BUY\n"
                        msg += "   ⚠️ Pump + Overbought RSI = DUMP WARNING\n\n"
                        msg += "🚀 Scanner running in background...\n"
                        msg += "💡 Use /stopmarketscan to stop"
                    else:
                        msg = "❌ Failed to start market scanner"
                
                logger.info("/startmarketscan: Sending response message...")
                keyboard = self.bot.create_main_menu_keyboard()
                self.bot.send_message(msg, reply_markup=keyboard)
                logger.info("/startmarketscan: Response sent successfully")
                
            except Exception as e:
                logger.error(f"Error in /startmarketscan: {e}", exc_info=True)
                keyboard = self.bot.create_main_menu_keyboard()
                self.bot.send_message(f"❌ Error: {str(e)}", reply_markup=keyboard)
        
        @self.telegram_bot.message_handler(commands=['stopmarketscan'])
        def handle_stopmarketscan(message):
            """Stop automatic market scanner"""
            if not check_authorized(message):
                return
            
            try:
                if not self.market_scanner.running:
                    msg = "⚠️ Market scanner is not running"
                else:
                    success = self.market_scanner.stop()
                    if success:
                        msg = "⛔ <b>Market Scanner Stopped</b>\n\n"
                        msg += "🔕 Auto-scanning disabled\n"
                        msg += "💡 Use /startmarketscan to resume"
                    else:
                        msg = "❌ Failed to stop market scanner"
                
                keyboard = self.bot.create_main_menu_keyboard()
                self.bot.send_message(msg, reply_markup=keyboard)
                
            except Exception as e:
                logger.error(f"Error in /stopmarketscan: {e}")
                keyboard = self.bot.create_main_menu_keyboard()
                self.bot.send_message(f"❌ Error: {str(e)}", reply_markup=keyboard)
        
        @self.telegram_bot.message_handler(commands=['marketstatus'])
        def handle_marketstatus(message):
            """Show market scanner status"""
            logger.info(f"Received /marketstatus command from chat {message.chat.id}")
            
            if not check_authorized(message):
                logger.warning(f"/marketstatus: Unauthorized access attempt from {message.chat.id}")
                return
            
            try:
                # Check if market_scanner exists
                if not hasattr(self, 'market_scanner'):
                    logger.warning("/marketstatus: market_scanner not initialized")
                    keyboard = self.bot.create_main_menu_keyboard()
                    self.bot.send_message(
                        "❌ <b>Market Scanner not initialized</b>\n\n"
                        "This bot is running in command-only mode.\n"
                        "Use /scan for manual market scanning.",
                        reply_markup=keyboard
                    )
                    return
                
                logger.info("/marketstatus: Getting scanner status...")
                status = self.market_scanner.get_status()
                logger.info(f"/marketstatus: Status retrieved - running: {status['running']}")
                
                status_icon = "🟢" if status['running'] else "🔴"
                status_text = "RUNNING" if status['running'] else "STOPPED"
                
                msg = f"{status_icon} <b>Market Scanner Status: {status_text}</b>\n\n"
                msg += f"⏱️ <b>Scan interval:</b> {status['scan_interval']//60} min ({status['scan_interval']}s)\n"
                msg += f"📊 <b>RSI alert levels:</b> {status['rsi_levels']}\n"
                msg += f"💰 <b>MFI (display only):</b> {status['mfi_levels']}\n"
                msg += f"🔔 <b>Alert cooldown:</b> {status['cooldown']}\n"
                msg += f"💾 <b>Tracked coins:</b> {status['tracked_coins']}\n\n"
                
                if status['running']:
                    msg += "🔍 <b>Điều kiện cảnh báo (chỉ RSI):</b>\n"
                    msg += "   🟢 Quá bán: RSI &lt; 20\n"
                    msg += "   🔴 Quá mua: RSI &gt; 80\n"
                    msg += "   ℹ️ MFI được tính nhưng không dùng cho cảnh báo\n\n"
                    msg += "🤖 <b>Phân Tích Bot:</b>\n"
                    msg += "   • Phát hiện hoạt động giao dịch bot\n"
                    msg += "   • Nhận diện mẫu pump\n"
                    msg += "   • Cảnh báo rủi ro dump\n"
                    msg += "   • Cung cấp tín hiệu vào lệnh sớm\n\n"
                    msg += "🚀 Scanner đang hoạt động nền\n"
                    msg += "💡 Dùng /stopmarketscan để dừng"
                else:
                    msg += "🔕 Quét tự động: TẮT\n"
                    msg += "💡 Dùng /startmarketscan để bắt đầu"
                
                keyboard = self.bot.create_main_menu_keyboard()
                logger.info("/marketstatus: Sending status message...")
                self.bot.send_message(msg, reply_markup=keyboard)
                logger.info("/marketstatus: Status message sent successfully")
                
            except Exception as e:
                logger.error(f"Error in /marketstatus: {e}", exc_info=True)
                keyboard = self.bot.create_main_menu_keyboard()
                self.bot.send_message(
                    f"❌ <b>Lỗi lấy trạng thái thị trường</b>\n\n"
                    f"Chi tiết: {str(e)}\n\n"
                    f"Vui lòng thử lại hoặc liên hệ hỗ trợ.",
                    reply_markup=keyboard
                )
        
        @self.telegram_bot.message_handler(commands=['volumescan'])
        def handle_volumescan(message):
            """Scan watchlist for volume spikes (manual)"""
            if not check_authorized(message):
                return
            
            try:
                symbols = self.watchlist.get_all()
                
                if not symbols:
                    self.bot.send_message("⚠️ <b>Watchlist is empty!</b>\n\n"
                                        "Add coins first with /watch SYMBOL")
                    return
                
                self.bot.send_message(f"🔍 <b>Scanning {len(symbols)} coins for volume spikes...</b>\n\n"
                                    f"⏳ This may take a moment...")
                
                # Scan for volume spikes
                spike_alerts = self.monitor.volume_detector.scan_watchlist_volumes(
                    symbols,
                    timeframes=['5m', '1h', '4h']
                )
                
                if not spike_alerts:
                    self.bot.send_message("ℹ️ <b>No volume spikes detected</b>\n\n"
                                        f"All {len(symbols)} coins have normal volume.\n\n"
                                        f"Current sensitivity: {self.monitor.volume_detector.sensitivity.upper()}")
                    return
                
                # Send summary
                summary = self.monitor.volume_detector.get_watchlist_spike_summary(spike_alerts)
                self.bot.send_message(summary)
                
                # Send detailed analysis for each spike
                for i, alert in enumerate(spike_alerts, 1):
                    # Get volume details
                    strongest_tf = None
                    max_ratio = 0
                    for tf, tf_result in alert['timeframe_results'].items():
                        if tf_result['is_spike'] and tf_result['volume_ratio'] > max_ratio:
                            max_ratio = tf_result['volume_ratio']
                            strongest_tf = tf
                    
                    if strongest_tf:
                        tf_data = alert['timeframe_results'][strongest_tf]
                        vol_text = self.monitor.volume_detector.get_volume_analysis_text(tf_data)
                        self.bot.send_message(f"<b>📊 {alert['symbol']}</b> ({i}/{len(spike_alerts)})\n\n{vol_text}")
                    
                    time.sleep(0.5)
                
                keyboard = self.bot.create_volume_keyboard()
                self.bot.send_message(f"✅ <b>Volume scan complete!</b>\n\n"
                                    f"Found {len(spike_alerts)} spike(s)",
                                    reply_markup=keyboard)
                
            except Exception as e:
                logger.error(f"Error in /volumescan: {e}")
                keyboard = self.bot.create_main_menu_keyboard()
                self.bot.send_message(f"❌ Error: {str(e)}", reply_markup=keyboard)
        
        @self.telegram_bot.message_handler(commands=['volumesensitivity'])
        def handle_volumesensitivity(message):
            """Change volume detection sensitivity"""
            if not check_authorized(message):
                return
            
            try:
                # Parse sensitivity from command
                parts = message.text.split()
                
                if len(parts) < 2:
                    # Show current sensitivity
                    current = self.monitor.volume_detector.sensitivity
                    config = self.monitor.volume_detector.config
                    
                    msg = f"<b>🎯 Volume Detection Sensitivity</b>\n\n"
                    msg += f"<b>Current:</b> {current.upper()}\n\n"
                    msg += f"<b>Settings:</b>\n"
                    msg += f"• Volume multiplier: {config['volume_multiplier']}x\n"
                    msg += f"• Min increase: {config['min_increase_percent']}%\n"
                    msg += f"• Lookback period: {config['lookback_periods']} candles\n\n"
                    msg += f"<b>Available levels:</b>\n"
                    msg += f"• <b>low</b> - Only extreme spikes (3x volume)\n"
                    msg += f"• <b>medium</b> - Moderate spikes (2.5x volume)\n"
                    msg += f"• <b>high</b> - Sensitive (2x volume)\n\n"
                    msg += f"💡 Usage: /volumesensitivity <level>"
                    
                    keyboard = self.bot.create_volume_keyboard()
                    self.bot.send_message(msg, reply_markup=keyboard)
                    return
                
                new_sensitivity = parts[1].lower()
                
                if new_sensitivity not in ['low', 'medium', 'high']:
                    self.bot.send_message("❌ <b>Invalid sensitivity!</b>\n\n"
                                        "Choose: <b>low</b>, <b>medium</b>, or <b>high</b>")
                    return
                
                # Update sensitivity
                old_sensitivity = self.monitor.volume_detector.sensitivity
                self.monitor.volume_detector.sensitivity = new_sensitivity
                self.monitor.volume_detector.config = self.monitor.volume_detector.thresholds[new_sensitivity]
                
                new_config = self.monitor.volume_detector.config
                
                keyboard = self.bot.create_volume_keyboard()
                self.bot.send_message(
                    f"✅ <b>Sensitivity updated!</b>\n\n"
                    f"<b>Changed from:</b> {old_sensitivity.upper()}\n"
                    f"<b>Changed to:</b> {new_sensitivity.upper()}\n\n"
                    f"<b>New settings:</b>\n"
                    f"• Volume multiplier: {new_config['volume_multiplier']}x\n"
                    f"• Min increase: {new_config['min_increase_percent']}%\n"
                    f"• Lookback: {new_config['lookback_periods']} candles\n\n"
                    f"💡 Test with /volumescan",
                    reply_markup=keyboard
                )
                
            except Exception as e:
                logger.error(f"Error in /volumesensitivity: {e}")
                keyboard = self.bot.create_main_menu_keyboard()
                self.bot.send_message(f"❌ Error: {str(e)}", reply_markup=keyboard)
        
        @self.telegram_bot.message_handler(commands=['startbotmonitor'])
        def handle_startbotmonitor(message):
            """Start automatic bot activity monitor"""
            if not check_authorized(message):
                return
            
            try:
                if self.bot_monitor.running:
                    msg = "⚠️ Giám sát bot đã đang chạy!\n\n"
                    msg += "💡 Dùng /botmonitorstatus để kiểm tra trạng thái"
                else:
                    success = self.bot_monitor.start()
                    
                    if success:
                        status = self.bot_monitor.get_status()
                        msg = "✅ <b>Đã Bật Giám Sát Bot!</b>\n\n"
                        msg += "🔍 <b>Giám sát:</b>\n"
                        msg += "   • Mẫu bot giao dịch\n"
                        msg += "   • Lừa đảo pump & dump\n"
                        msg += "   • Hoạt động giao dịch tự động\n\n"
                        msg += f"⏱️ <b>Khoảng kiểm tra:</b> {status['check_interval']//60} phút\n"
                        msg += f"📊 <b>Đang giám sát:</b> {status['watchlist_count']} symbols\n"
                        msg += f"🤖 <b>Cảnh báo bot:</b> Điểm ≥{status['bot_threshold']}%\n"
                        msg += f"🚀 <b>Cảnh báo pump:</b> Điểm ≥{status['pump_threshold']}%\n"
                        msg += f"🔔 <b>Thời gian chờ:</b> {status['alert_cooldown']//60} phút/symbol\n\n"
                        msg += "🚀 Monitor đang chạy nền...\n"
                        msg += "💡 Dùng /stopbotmonitor để dừng"
                    else:
                        msg = "❌ Không thể khởi động giám sát bot\n\n"
                        msg += "⚠️ Hãy chắc watchlist không trống\n"
                        msg += "Dùng /watch SYMBOL để thêm coin"
                
                keyboard = self.bot.create_bot_monitor_keyboard()
                self.bot.send_message(msg, reply_markup=keyboard)
                
            except Exception as e:
                logger.error(f"Error in /startbotmonitor: {e}")
                keyboard = self.bot.create_bot_monitor_keyboard()
                from vietnamese_messages import ERROR_OCCURRED
                self.bot.send_message(ERROR_OCCURRED.format(error=str(e)), reply_markup=keyboard)
        
        @self.telegram_bot.message_handler(commands=['stopbotmonitor'])
        def handle_stopbotmonitor(message):
            """Stop automatic bot activity monitor"""
            if not check_authorized(message):
                return
            
            try:
                if not self.bot_monitor.running:
                    msg = "⚠️ Giám sát bot không chạy"
                else:
                    success = self.bot_monitor.stop()
                    if success:
                        msg = "⛔ <b>Đã Dừng Giám Sát Bot</b>\n\n"
                        msg += "🔕 Giám sát tự động đã tắt\n"
                        msg += "💡 Dùng /startbotmonitor để tiếp tục"
                    else:
                        msg = "❌ Không thể dừng giám sát bot"
                
                keyboard = self.bot.create_bot_monitor_keyboard()
                self.bot.send_message(msg, reply_markup=keyboard)
                
            except Exception as e:
                logger.error(f"Error in /stopbotmonitor: {e}")
                keyboard = self.bot.create_bot_monitor_keyboard()
                from vietnamese_messages import ERROR_OCCURRED
                self.bot.send_message(ERROR_OCCURRED.format(error=str(e)), reply_markup=keyboard)
        
        @self.telegram_bot.message_handler(commands=['botmonitorstatus'])
        def handle_botmonitorstatus(message):
            """Show bot monitor status"""
            if not check_authorized(message):
                return
            
            try:
                status = self.bot_monitor.get_status()
                
                status_icon = "🟢" if status['running'] else "🔴"
                status_text = "ĐANG CHẠY" if status['running'] else "ĐÃ DỪNG"
                mode_text = "📋 Watchlist" if status['scan_mode'] == 'watchlist' else "🌐 ALL Market (Tất Cả USDT Coins)"
                
                msg = f"{status_icon} <b>Trạng Thái Giám Sát Bot: {status_text}</b>\n\n"
                msg += f"📍 <b>Chế độ quét:</b> {mode_text}\n"
                msg += f"⏱️ <b>Khoảng kiểm tra:</b> {status['check_interval']//60} phút ({status['check_interval']}s)\n"
                msg += f"📊 <b>Watchlist:</b> {status['watchlist_count']} symbols\n"
                msg += f"🤖 <b>Ngưỡng bot:</b> {status['bot_threshold']}% (Chỉ tín hiệu cao)\n"
                msg += f"🚀 <b>Ngưỡng pump:</b> {status['pump_threshold']}% (Độ chính xác cao)\n"
                msg += f"� <b>Max alerts:</b> {status['max_alerts_per_scan']} tín hiệu mạnh nhất\n"
                msg += f"�🔔 <b>Thời gian chờ:</b> {status['alert_cooldown']//60} phút\n"
                msg += f"💾 <b>Symbols theo dõi:</b> {status['tracked_symbols']}\n\n"
                
                if status['running']:
                    msg += "🔍 <b>Đang giám sát (Tín hiệu cao only):</b>\n"
                    msg += "   🤖 Bot giao dịch >= 70% (thao túng mạnh)\n"
                    msg += "   🚀 Pump pattern >= 70% (nguy cơ cao)\n"
                    msg += "   📊 Chỉ hiển thị top 10 tín hiệu mạnh nhất\n"
                    msg += "   ⚡ Lọc bỏ tín hiệu yếu (< 70%)\n\n"
                    msg += "✅ Cảnh báo tự động đã bật\n"
                    msg += "💡 Dùng /stopbotmonitor để dừng"
                else:
                    msg += "🔕 Giám sát tự động: TẮT\n"
                    msg += "💡 Dùng /startbotmonitor để bắt đầu\n"
                    msg += "💡 Dùng /botscan để quét thủ công"
                
                keyboard = self.bot.create_bot_monitor_keyboard()
                self.bot.send_message(msg, reply_markup=keyboard)
                
            except Exception as e:
                logger.error(f"Error in /botmonitorstatus: {e}")
                keyboard = self.bot.create_bot_monitor_keyboard()
                from vietnamese_messages import ERROR_OCCURRED
                self.bot.send_message(ERROR_OCCURRED.format(error=str(e)), reply_markup=keyboard)
        
        @self.telegram_bot.message_handler(commands=['botscan'])
        def handle_botscan(message):
            """Manual bot activity scan"""
            if not check_authorized(message):
                return
            
            try:
                # Get scan mode
                scan_mode = self.bot_monitor.scan_mode
                
                if scan_mode == 'watchlist':
                    symbols = self.watchlist.get_all()
                    if not symbols:
                        self.bot.send_message("⚠️ <b>Watchlist trống!</b>\n\n"
                                            "Thêm coin trước với /watch SYMBOL")
                        return
                    scan_text = f"watchlist ({len(symbols)} symbols)"
                else:
                    scan_text = "ALL market (tất cả USDT coins)"
                
                self.bot.send_message(f"🔍 <b>Đang quét {scan_text} tìm bot...</b>\n\n"
                                    f"⏳ Vui lòng chờ...")
                
                # Perform manual scan
                detections = self.bot_monitor.manual_scan()
                
                if not detections:
                    self.bot.send_message(f"✅ <b>Quét Hoàn Tất</b>\n\n"
                                        f"Không phát hiện hoạt động bot đáng kể trong {scan_text}.\n\n"
                                        f"Tất cả symbols đều có mẫu giao dịch bình thường.")
                    return
                
                # Count alerts
                pump_alerts = [d for d in detections if d.get('pump_score', 0) >= 45]
                bot_alerts = [d for d in detections if d.get('bot_score', 0) >= 40]
                
                # Send summary
                summary = f"<b>🤖 KẾT QUẢ QUÉT BOT</b>\n\n"
                summary += f"� Chế độ: {scan_text}\n"
                summary += f"⚠️ Cảnh báo: {len(pump_alerts) + len(bot_alerts)}\n\n"
                
                if pump_alerts:
                    summary += f"🚀 <b>BOT PUMP:</b> {len(pump_alerts)}\n"
                if bot_alerts:
                    summary += f"🤖 <b>BOT Giao Dịch:</b> {len(bot_alerts)}\n"
                
                summary += f"\n📤 Đang gửi phân tích chi tiết..."
                
                self.bot.send_message(summary)
                time.sleep(1)
                
                # Send all detections (sorted by score)
                sorted_detections = sorted(detections, 
                                         key=lambda x: max(x.get('bot_score', 0), x.get('pump_score', 0)), 
                                         reverse=True)
                
                for i, detection in enumerate(sorted_detections[:10], 1):  # Limit to top 10
                    try:
                        analysis_msg = self.bot_detector.get_formatted_analysis(detection)
                        self.bot.send_message(f"<b>Kết quả {i}/{min(10, len(sorted_detections))}</b>\n\n{analysis_msg}")
                        time.sleep(1.5)
                    except Exception as e:
                        logger.error(f"Error sending detection {i}: {e}")
                
                if len(sorted_detections) > 10:
                    self.bot.send_message(f"ℹ️ Hiển thị top 10 trong tổng {len(sorted_detections)} phát hiện")
                
                keyboard = self.bot.create_bot_monitor_keyboard()
                self.bot.send_message(f"✅ <b>Quét bot hoàn tất!</b>", reply_markup=keyboard)
                
            except Exception as e:
                logger.error(f"Error in /botscan: {e}")
                keyboard = self.bot.create_bot_monitor_keyboard()
                from vietnamese_messages import ERROR_OCCURRED
                self.bot.send_message(ERROR_OCCURRED.format(error=str(e)), reply_markup=keyboard)
        
        @self.telegram_bot.message_handler(commands=['botthreshold'])
        def handle_botthreshold(message):
            """Set bot detection thresholds"""
            if not check_authorized(message):
                return
            
            try:
                parts = message.text.split()
                
                if len(parts) < 2:
                    # Show current thresholds
                    status = self.bot_monitor.get_status()
                    msg = f"<b>🎯 Ngưỡng Phát Hiện Bot</b>\n\n"
                    msg += f"<b>Cài đặt hiện tại:</b>\n"
                    msg += f"🤖 Bot Giao Dịch: {status['bot_threshold']}%\n"
                    msg += f"🚀 Bot Pump: {status['pump_threshold']}%\n\n"
                    msg += f"<b>Cách dùng:</b>\n"
                    msg += f"/botthreshold bot 80\n"
                    msg += f"/botthreshold pump 70\n\n"
                    msg += f"Khoảng: 0-100%"
                    
                    keyboard = self.bot.create_main_menu_keyboard()
                    self.bot.send_message(msg, reply_markup=keyboard)
                    return
                
                threshold_type = parts[1].lower()
                threshold_value = int(parts[2]) if len(parts) > 2 else None
                
                if threshold_value is None:
                    self.bot.send_message("❌ Vui lòng chỉ định giá trị ngưỡng\n\n"
                                        "Ví dụ: /botthreshold bot 80")
                    return
                
                if threshold_type == 'bot':
                    self.bot_monitor.set_thresholds(bot_threshold=threshold_value)
                    msg = f"✅ Ngưỡng Bot Giao Dịch đã cập nhật thành {threshold_value}%"
                elif threshold_type == 'pump':
                    self.bot_monitor.set_thresholds(pump_threshold=threshold_value)
                    msg = f"✅ Ngưỡng Bot Pump đã cập nhật thành {threshold_value}%"
                else:
                    msg = "❌ Loại không hợp lệ. Dùng 'bot' hoặc 'pump'"
                
                keyboard = self.bot.create_bot_monitor_keyboard()
                self.bot.send_message(msg, reply_markup=keyboard)
                
            except Exception as e:
                logger.error(f"Error in /botthreshold: {e}")
                keyboard = self.bot.create_bot_monitor_keyboard()
                from vietnamese_messages import ERROR_OCCURRED
                self.bot.send_message(ERROR_OCCURRED.format(error=str(e)), reply_markup=keyboard)
        
        # ===== REAL-TIME PUMP DETECTOR HANDLERS =====
        @self.telegram_bot.message_handler(commands=['startpumpwatch'])
        def handle_startpumpwatch(message):
            """Start real-time pump monitoring"""
            if not check_authorized(message):
                return
            
            try:
                if self.pump_detector.running:
                    self.bot.send_message("⚠️ <b>Pump Detector đã chạy rồi!</b>\n\n"
                                        "Dùng /pumpstatus để xem trạng thái\n"
                                        "Dùng /stoppumpwatch để dừng")
                    return
                
                success = self.pump_detector.start()
                
                if success:
                    msg = "✅ <b>Pump Detector ĐÃ BẬT</b>\n\n"
                    msg += "🎯 <b>Hệ Thống 3-Layer Detection:</b>\n"
                    msg += "   🔹 Layer 1 (5m): Phát hiện sớm mỗi 3 phút\n"
                    msg += "   🔹 Layer 2 (1h/4h): Xác nhận mỗi 10 phút\n"
                    msg += "   🔹 Layer 3 (1D): Xu hướng mỗi 15 phút\n\n"
                    msg += "📊 <b>Độ Chính Xác: 90%+</b>\n"
                    msg += "⚡ <b>Phát hiện trước: 10-20 phút</b>\n\n"
                    msg += "🚀 Detector đang hoạt động nền\n"
                    msg += "🔔 Bạn sẽ nhận cảnh báo tự động khi phát hiện pump\n\n"
                    msg += "💡 Dùng /pumpstatus để xem trạng thái\n"
                    msg += "💡 Dùng /stoppumpwatch để dừng"
                    
                    keyboard = self.bot.create_main_menu_keyboard()
                    self.bot.send_message(msg, reply_markup=keyboard)
                else:
                    self.bot.send_message("❌ Không thể khởi động Pump Detector")
                    
            except Exception as e:
                logger.error(f"Error in /startpumpwatch: {e}")
                from vietnamese_messages import ERROR_OCCURRED
                self.bot.send_message(ERROR_OCCURRED.format(error=str(e)))
        
        @self.telegram_bot.message_handler(commands=['stoppumpwatch'])
        def handle_stoppumpwatch(message):
            """Stop real-time pump monitoring"""
            if not check_authorized(message):
                return
            
            try:
                if not self.pump_detector.running:
                    self.bot.send_message("⚠️ <b>Pump Detector chưa chạy!</b>\n\n"
                                        "Dùng /startpumpwatch để bắt đầu")
                    return
                
                success = self.pump_detector.stop()
                
                if success:
                    msg = "⛔ <b>Pump Detector ĐÃ DỪNG</b>\n\n"
                    msg += "🔕 Cảnh báo pump tự động đã tắt\n\n"
                    msg += "💡 Dùng /startpumpwatch để bắt đầu lại\n"
                    msg += "💡 Dùng /pumpscan để quét thủ công"
                    
                    keyboard = self.bot.create_main_menu_keyboard()
                    self.bot.send_message(msg, reply_markup=keyboard)
                else:
                    self.bot.send_message("❌ Không thể dừng Pump Detector")
                    
            except Exception as e:
                logger.error(f"Error in /stoppumpwatch: {e}")
                from vietnamese_messages import ERROR_OCCURRED
                self.bot.send_message(ERROR_OCCURRED.format(error=str(e)))
        
        @self.telegram_bot.message_handler(commands=['pumpstatus'])
        def handle_pumpstatus(message):
            """Show pump detector status"""
            if not check_authorized(message):
                return
            
            try:
                status = self.pump_detector.get_status()
                
                status_icon = "🟢" if status['running'] else "🔴"
                status_text = "ĐANG CHẠY" if status['running'] else "ĐÃ DỪNG"
                
                msg = f"{status_icon} <b>Trạng Thái Pump Detector: {status_text}</b>\n\n"
                msg += f"<b>⚙️ Cấu Hình:</b>\n"
                msg += f"   🔹 Layer 1 (5m): Quét mỗi {status['layer1_interval']//60} phút\n"
                msg += f"   🔹 Layer 2 (1h/4h): Quét mỗi {status['layer2_interval']//60} phút\n"
                msg += f"   🔹 Layer 3 (1D): Quét mỗi {status['layer3_interval']//60} phút\n\n"
                msg += f"<b>📊 Thống Kê:</b>\n"
                msg += f"   💾 Pumps đang theo dõi: {status['tracked_pumps']}\n"
                msg += f"   🎯 Ngưỡng cảnh báo: {status['final_threshold']}%\n"
                msg += f"   🔔 Thời gian chờ: {status['alert_cooldown']//60} phút\n"
                msg += f"   📤 Đã gửi cảnh báo: {status['last_alerts']}\n\n"
                
                # Auto-save watchlist info
                msg += f"<b>💾 Auto-Save Watchlist:</b>\n"
                msg += f"   ✅ Tự động lưu: {'BẬT' if self.pump_detector.watchlist else 'TẮT'}\n"
                if self.pump_detector.watchlist:
                    msg += f"   🎯 Ngưỡng lưu: >= {self.pump_detector.auto_save_threshold}%\n"
                    msg += f"   📋 Watchlist: {self.pump_detector.watchlist.count()}/{self.pump_detector.max_watchlist_size} coins\n\n"
                else:
                    msg += "\n"
                
                if status['running']:
                    msg += "<b>🎯 Hệ Thống 3-Layer:</b>\n"
                    msg += "   ⚡ Layer 1: Phát hiện volume spike, price momentum\n"
                    msg += "   ✅ Layer 2: Xác nhận RSI/MFI, bot detection\n"
                    msg += "   📈 Layer 3: Kiểm tra xu hướng dài hạn\n\n"
                    msg += "🚀 Detector hoạt động nền\n"
                    msg += "💡 Dùng /stoppumpwatch để dừng"
                else:
                    msg += "🔕 Giám sát pump: TẮT\n"
                    msg += "💡 Dùng /startpumpwatch để bắt đầu\n"
                    msg += "💡 Dùng /pumpscan SYMBOL để quét thủ công"
                
                keyboard = self.bot.create_main_menu_keyboard()
                self.bot.send_message(msg, reply_markup=keyboard)
                
            except Exception as e:
                logger.error(f"Error in /pumpstatus: {e}")
                from vietnamese_messages import ERROR_OCCURRED
                self.bot.send_message(ERROR_OCCURRED.format(error=str(e)))
        
        @self.telegram_bot.message_handler(commands=['pumpscan'])
        def handle_pumpscan(message):
            """Manual pump scan for specific symbol"""
            if not check_authorized(message):
                return
            
            try:
                # Parse symbol from command
                parts = message.text.split()
                
                if len(parts) < 2:
                    self.bot.send_message("❌ <b>Vui lòng chỉ định symbol</b>\n\n"
                                        "Cú pháp: /pumpscan BTCUSDT\n"
                                        "Hoặc: /pumpscan BTC")
                    return
                
                symbol_raw = parts[1].upper()
                
                # Auto-add USDT if not present
                if not symbol_raw.endswith('USDT'):
                    symbol = symbol_raw + 'USDT'
                else:
                    symbol = symbol_raw
                
                self.bot.send_message(f"🔍 <b>Đang phân tích {symbol} qua 3 layers...</b>\n\n"
                                    f"⏳ Vui lòng chờ 10-15 giây...")
                
                # Perform manual scan
                result = self.pump_detector.manual_scan(symbol)
                
                if not result:
                    self.bot.send_message(f"❌ <b>Không thể phân tích {symbol}</b>\n\n"
                                        "Symbol có thể không tồn tại hoặc thiếu dữ liệu.")
                    return
                
                # Build result message
                msg = f"<b>📊 PUMP ANALYSIS - {symbol}</b>\n\n"
                msg += f"<b>Kết Quả:</b> {result['result']}\n\n"
                
                if 'final_score' in result:
                    score = result['final_score']
                    msg += f"<b>🎯 Điểm Tổng Hợp: {score:.0f}%</b>\n\n"
                    
                    if score >= 90:
                        msg += "✅ <b>PUMP RẤT CAO - 90%+ chính xác</b>\n"
                        msg += "   • Tín hiệu pump mạnh\n"
                        msg += "   • An toàn vào lệnh\n"
                        msg += "   • Mục tiêu: +10-30%\n"
                    elif score >= 80:
                        msg += "✅ <b>PUMP CAO - 80%+ chính xác</b>\n"
                        msg += "   • Tín hiệu pump tốt\n"
                        msg += "   • Theo dõi sát\n"
                        msg += "   • Mục tiêu: +5-20%\n"
                    else:
                        msg += "⚠️ <b>Dưới ngưỡng - Không khuyến nghị</b>\n"
                
                # Layer details
                if 'layer1' in result and result['layer1']:
                    layer1 = result['layer1']
                    msg += f"\n<b>⚡ Layer 1 (5m):</b> {layer1['pump_score']:.0f}%\n"
                    if 'indicators' in layer1:
                        ind = layer1['indicators']
                        msg += f"   • Volume spike: {ind.get('volume_spike', 0)}x\n"
                        msg += f"   • Giá +5m: {ind.get('price_change_5m', 0):+.2f}%\n"
                        msg += f"   • RSI: {ind.get('current_rsi', 0):.1f}\n"
                
                if 'layer2' in result and result['layer2']:
                    layer2 = result['layer2']
                    msg += f"\n<b>✅ Layer 2 (1h/4h):</b> {layer2['pump_score']:.0f}%\n"
                    if 'indicators' in layer2:
                        ind = layer2['indicators']
                        msg += f"   • RSI 1h: {ind.get('rsi_1h', 0):.1f}\n"
                        msg += f"   • RSI 4h: {ind.get('rsi_4h', 0):.1f}\n"
                
                if 'layer3' in result and result['layer3']:
                    layer3 = result['layer3']
                    msg += f"\n<b>📈 Layer 3 (1D):</b> {layer3['pump_score']:.0f}%\n"
                    if 'indicators' in layer3:
                        ind = layer3['indicators']
                        msg += f"   • RSI 1D: {ind.get('rsi_1d', 0):.1f}\n"
                        msg += f"   • Xu hướng 7D: {ind.get('trend_7d', 0):+.1f}%\n"
                
                msg += f"\n⚠️ <i>Đây là phân tích kỹ thuật, không phải tư vấn tài chính</i>"
                
                keyboard = self.bot.create_main_menu_keyboard()
                self.bot.send_message(msg, reply_markup=keyboard)
                
            except Exception as e:
                logger.error(f"Error in /pumpscan: {e}")
                from vietnamese_messages import ERROR_OCCURRED
                self.bot.send_message(ERROR_OCCURRED.format(error=str(e)))
        
        @self.telegram_bot.message_handler(commands=['stochrsi'])
        def handle_stochrsi(message):
            """Stochastic + RSI multi-timeframe analysis"""
            if not check_authorized(message):
                return
            
            try:
                # Parse symbol from command
                parts = message.text.split()
                
                if len(parts) < 2:
                    self.bot.send_message("❌ <b>Vui lòng chỉ định symbol</b>\n\n"
                                        "Cú pháp: /stochrsi BTCUSDT\n"
                                        "Hoặc: /stochrsi BTC\n\n"
                                        "💡 Phân tích Stochastic + RSI trên 4 timeframes")
                    return
                
                symbol_raw = parts[1].upper()
                
                # Auto-add USDT if not present
                if not symbol_raw.endswith('USDT'):
                    symbol = symbol_raw + 'USDT'
                else:
                    symbol = symbol_raw
                
                self.bot.send_message(f"🔍 <b>STOCH+RSI MULTI-TIMEFRAME ANALYSIS</b>\n\n"
                                    f"📊 Đang phân tích {symbol} trên 4 timeframes...\n"
                                    f"⏳ Vui lòng chờ...")
                
                # Perform multi-timeframe analysis
                result = self.stoch_rsi_analyzer.analyze_multi_timeframe(
                    symbol, 
                    timeframes=['1m', '5m', '4h', '1d']
                )
                
                if not result or 'error' in result:
                    self.bot.send_message(f"❌ <b>Không thể phân tích {symbol}</b>\n\n"
                                        "Symbol có thể không tồn tại hoặc thiếu dữ liệu.\n"
                                        f"Error: {result.get('error', 'Unknown')}")
                    return
                
                # Format message using analyzer's format function
                msg = self.stoch_rsi_analyzer.format_analysis_message(result, include_details=True)
                
                # Add integration hints if pump detector is running
                if self.pump_detector.running:
                    consensus = result['consensus']
                    if consensus == 'BUY':
                        msg += f"\n\n💡 <b>TIP:</b> Kết hợp với /pumpscan {symbol_raw} để xác nhận pump"
                    elif consensus == 'SELL':
                        msg += f"\n\n⚠️ <b>WARNING:</b> Stoch+RSI cho tín hiệu SELL, tránh vào lệnh"
                
                keyboard = self.bot.create_main_menu_keyboard()
                self.bot.send_message(msg, reply_markup=keyboard)
                
            except Exception as e:
                logger.error(f"Error in /stochrsi: {e}")
                from vietnamese_messages import ERROR_OCCURRED
                self.bot.send_message(ERROR_OCCURRED.format(error=str(e)))
        
        @self.telegram_bot.message_handler(commands=['analyzer'])
        def handle_comprehensive_analyzer(message):
            """Comprehensive analysis: PUMP/DUMP + RSI/MFI + Stoch+RSI + AI Button"""
            if not check_authorized(message):
                return
            
            try:
                # Parse symbol from command
                parts = message.text.split()
                
                if len(parts) < 2:
                    self.bot.send_message(
                        "❌ <b>Vui lòng chỉ định symbol</b>\n\n"
                        "<b>Cú pháp:</b>\n"
                        "   /analyzer BTCUSDT\n"
                        "   /analyzer BTC\n\n"
                        "<b>Phân tích toàn diện:</b>\n"
                        "   ✅ PUMP/DUMP Detection (3 layers)\n"
                        "   ✅ RSI/MFI Multi-timeframe\n"
                        "   ✅ Stoch+RSI Multi-timeframe\n"
                        "   ✅ Volume Analysis\n"
                        "   🤖 AI Analysis Button"
                    )
                    return
                
                symbol_raw = parts[1].upper()
                
                # Auto-add USDT if not present
                if not symbol_raw.endswith('USDT'):
                    symbol = symbol_raw + 'USDT'
                else:
                    symbol = symbol_raw
                
                self.bot.send_message(
                    f"🔍 <b>COMPREHENSIVE ANALYSIS - {symbol}</b>\n\n"
                    f"📊 Đang thu thập dữ liệu từ tất cả indicators...\n"
                    f"⏳ Vui lòng chờ 15-20 giây..."
                )
                
                # === 1. PUMP/DUMP ANALYSIS ===
                pump_result = self.pump_detector.manual_scan(symbol)
                
                # === 2. RSI/MFI ANALYSIS ===
                timeframes = ['5m', '1h', '4h', '1d']
                klines_dict = self.binance.get_multi_timeframe_data(symbol, timeframes, limit=200)
                
                if not klines_dict:
                    self.bot.send_message(
                        f"❌ <b>Không thể lấy dữ liệu cho {symbol}</b>\n\n"
                        "Symbol có thể không tồn tại hoặc không có đủ lịch sử giao dịch."
                    )
                    return
                
                rsi_mfi_result = self._analyze_multi_timeframe(
                    klines_dict,
                    self._config.RSI_PERIOD,
                    self._config.MFI_PERIOD,
                    self._config.RSI_LOWER,
                    self._config.RSI_UPPER,
                    self._config.MFI_LOWER,
                    self._config.MFI_UPPER
                )
                
                # === 3. STOCH+RSI ANALYSIS ===
                stoch_rsi_result = self.stoch_rsi_analyzer.analyze_multi_timeframe(
                    symbol, 
                    timeframes=['1m', '5m', '4h', '1d']
                )
                
                # === 4. BUILD COMPREHENSIVE MESSAGE ===
                msg = f"<b>📊 COMPREHENSIVE ANALYSIS</b>\n\n"
                msg += f"<b>💎 {symbol}</b>\n"
                msg += f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                
                # Current Price
                ticker_24h = self.binance.get_24h_data(symbol)
                if ticker_24h:
                    current_price = ticker_24h['last_price']
                    price_change_24h = ticker_24h['price_change_percent']
                    volume_24h = ticker_24h['volume']
                    
                    msg += f"<b>💰 Giá Hiện Tại:</b> ${current_price:,.8f}\n"
                    msg += f"<b>📈 24h Change:</b> {price_change_24h:+.2f}%\n"
                    msg += f"<b>💧 24h Volume:</b> ${volume_24h:,.0f}\n\n"
                
                msg += "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                
                # === PUMP/DUMP SECTION ===
                msg += "<b>🚀 PUMP/DUMP DETECTION (3-Layer)</b>\n\n"
                
                if pump_result and 'final_score' in pump_result:
                    score = pump_result['final_score']
                    
                    if score >= 80:
                        status_emoji = "🔴"
                        status_text = "PUMP CAO"
                    elif score >= 60:
                        status_emoji = "🟡"
                        status_text = "PUMP VỪA"
                    elif score >= 40:
                        status_emoji = "🟢"
                        status_text = "PUMP YẾU"
                    else:
                        status_emoji = "⚪"
                        status_text = "KHÔNG PUMP"
                    
                    msg += f"{status_emoji} <b>Status:</b> {status_text}\n"
                    msg += f"<b>🎯 Final Score:</b> {score:.0f}%\n\n"
                    
                    # Layer breakdown
                    if 'layer1' in pump_result and pump_result['layer1']:
                        layer1 = pump_result['layer1']
                        msg += f"   ⚡ Layer 1 (5m): {layer1['pump_score']:.0f}%\n"
                    
                    if 'layer2' in pump_result and pump_result['layer2']:
                        layer2 = pump_result['layer2']
                        msg += f"   ✅ Layer 2 (1h/4h): {layer2['pump_score']:.0f}%\n"
                    
                    if 'layer3' in pump_result and pump_result['layer3']:
                        layer3 = pump_result['layer3']
                        msg += f"   📈 Layer 3 (1D): {layer3['pump_score']:.0f}%\n"
                else:
                    msg += "⚪ <b>Status:</b> Không có tín hiệu pump rõ ràng\n"
                
                msg += "\n━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                
                # === RSI/MFI SECTION ===
                msg += "<b>📊 RSI/MFI MULTI-TIMEFRAME</b>\n\n"
                
                if rsi_mfi_result and 'timeframes' in rsi_mfi_result:
                    consensus = rsi_mfi_result['consensus']
                    strength = rsi_mfi_result['consensus_strength']
                    
                    if consensus == 'BUY':
                        consensus_emoji = "🟢"
                    elif consensus == 'SELL':
                        consensus_emoji = "🔴"
                    else:
                        consensus_emoji = "🟡"
                    
                    msg += f"{consensus_emoji} <b>Consensus:</b> {consensus} (Strength: {strength}/4)\n\n"
                    
                    # Timeframe breakdown
                    for tf, data in rsi_mfi_result['timeframes'].items():
                        signal = data['signal']
                        rsi = data['rsi']
                        mfi = data['mfi']
                        
                        signal_emoji = "🟢" if signal == 'BUY' else "🔴" if signal == 'SELL' else "🟡"
                        
                        msg += f"   {signal_emoji} <b>{tf}:</b> {signal}\n"
                        msg += f"      RSI: {rsi:.1f} | MFI: {mfi:.1f}\n"
                else:
                    msg += "⚪ Không có dữ liệu RSI/MFI\n"
                
                msg += "\n━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                
                # === STOCH+RSI SECTION ===
                msg += "<b>📈 STOCH+RSI MULTI-TIMEFRAME</b>\n\n"
                
                if stoch_rsi_result and 'timeframes' in stoch_rsi_result:
                    consensus = stoch_rsi_result['consensus']
                    strength = stoch_rsi_result['consensus_strength']
                    
                    if consensus == 'BUY':
                        consensus_emoji = "🟢"
                    elif consensus == 'SELL':
                        consensus_emoji = "🔴"
                    else:
                        consensus_emoji = "🟡"
                    
                    msg += f"{consensus_emoji} <b>Consensus:</b> {consensus} (Strength: {strength}/4)\n\n"
                    
                    # Timeframe breakdown
                    for tf_data in stoch_rsi_result['timeframes']:
                        tf = tf_data['timeframe']
                        signal = tf_data['signal_text']
                        rsi = tf_data['rsi']
                        stoch_k = tf_data['stoch_k']
                        
                        signal_emoji = "🟢" if 'BUY' in signal else "🔴" if 'SELL' in signal else "🟡"
                        
                        msg += f"   {signal_emoji} <b>{tf}:</b> {signal}\n"
                        msg += f"      RSI: {rsi:.1f} | Stoch: {stoch_k:.1f}\n"
                else:
                    msg += "⚪ Không có dữ liệu Stoch+RSI\n"
                
                msg += "\n━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                
                # === TRADING RECOMMENDATION ===
                msg += "<b>🎯 TỔNG KẾT & KHUYẾN NGHỊ</b>\n\n"
                
                # Calculate overall signal
                buy_signals = 0
                sell_signals = 0
                total_signals = 0
                
                # Count RSI/MFI signals
                if rsi_mfi_result and 'consensus' in rsi_mfi_result:
                    total_signals += 1
                    if rsi_mfi_result['consensus'] == 'BUY':
                        buy_signals += 1
                    elif rsi_mfi_result['consensus'] == 'SELL':
                        sell_signals += 1
                
                # Count Stoch+RSI signals
                if stoch_rsi_result and 'consensus' in stoch_rsi_result:
                    total_signals += 1
                    if stoch_rsi_result['consensus'] == 'BUY':
                        buy_signals += 1
                    elif stoch_rsi_result['consensus'] == 'SELL':
                        sell_signals += 1
                
                # Count Pump signal
                if pump_result and 'final_score' in pump_result:
                    total_signals += 1
                    if pump_result['final_score'] >= 60:
                        buy_signals += 1
                
                # Overall recommendation
                if buy_signals >= 2 and sell_signals == 0:
                    msg += "✅ <b>KHUYẾN NGHỊ: MUA/LONG</b>\n"
                    msg += f"   • Tín hiệu BUY: {buy_signals}/{total_signals}\n"
                    msg += "   • Đa số indicators đồng thuận BUY\n"
                elif sell_signals >= 2 and buy_signals == 0:
                    msg += "❌ <b>KHUYẾN NGHỊ: BÁN/SHORT</b>\n"
                    msg += f"   • Tín hiệu SELL: {sell_signals}/{total_signals}\n"
                    msg += "   • Đa số indicators đồng thuận SELL\n"
                elif buy_signals > sell_signals:
                    msg += "🟢 <b>KHUYẾN NGHỊ: CHỜ XÁC NHẬN MUA</b>\n"
                    msg += f"   • Tín hiệu BUY: {buy_signals}/{total_signals}\n"
                    msg += "   • Tín hiệu SELL: {sell_signals}/{total_signals}\n"
                    msg += "   • Theo dõi thêm trước khi vào lệnh\n"
                elif sell_signals > buy_signals:
                    msg += "🔴 <b>KHUYẾN NGHỊ: CHỜ XÁC NHẬN BÁN</b>\n"
                    msg += f"   • Tín hiệu SELL: {sell_signals}/{total_signals}\n"
                    msg += "   • Tín hiệu BUY: {buy_signals}/{total_signals}\n"
                    msg += "   • Có xu hướng giảm, cẩn trọng\n"
                else:
                    msg += "🟡 <b>KHUYẾN NGHỊ: CHỜ ĐỢI</b>\n"
                    msg += f"   • Tín hiệu BUY: {buy_signals}/{total_signals}\n"
                    msg += f"   • Tín hiệu SELL: {sell_signals}/{total_signals}\n"
                    msg += "   • Indicators mâu thuẫn nhau\n"
                    msg += "   • Tránh vào lệnh trong lúc này\n"
                
                msg += "\n⚠️ <i>Đây là phân tích kỹ thuật tự động, không phải tư vấn tài chính</i>"
                
                # Create AI Analysis button
                ai_keyboard = self.bot.create_ai_analysis_keyboard(symbol)
                
                # Send comprehensive analysis
                self.bot.send_message(msg, reply_markup=ai_keyboard)
                
                logger.info(f"✅ Sent comprehensive analysis for {symbol}")
                
            except Exception as e:
                logger.error(f"Error in /analyzer: {e}", exc_info=True)
                from vietnamese_messages import ERROR_OCCURRED
                self.bot.send_message(ERROR_OCCURRED.format(error=str(e)))
        
        # ===== SYMBOL ANALYSIS HANDLER (MUST BE LAST) =====
        @self.telegram_bot.message_handler(func=lambda m: m.text and m.text.startswith('/') and 
                                          len(m.text) > 1 and m.text[1:].split()[0].upper() not in 
                                          [cmd.upper() for cmd in self.registered_commands] and
                                          m.text[1:].replace('USDT', '').replace('usdt', '').isalnum())
        def handle_symbol_analysis(message):
            """Comprehensive analysis for symbol commands like /BTC, /ETH - includes PUMP + RSI/MFI + Stoch+RSI + AI Button"""
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
                
                logger.info(f"Comprehensive analysis for {symbol}...")
                
                # Send processing message
                self.bot.send_message(
                    f"🔍 <b>COMPREHENSIVE ANALYSIS - {symbol}</b>\n\n"
                    f"📊 Đang thu thập dữ liệu từ tất cả indicators...\n"
                    f"⏳ Vui lòng chờ 15-20 giây..."
                )
                
                # === 1. PUMP/DUMP ANALYSIS ===
                pump_result = self.pump_detector.manual_scan(symbol)
                
                # === 2. RSI/MFI ANALYSIS ===
                timeframes = ['5m', '1h', '4h', '1d']
                klines_dict = self.binance.get_multi_timeframe_data(symbol, timeframes, limit=200)
                
                if not klines_dict:
                    self.bot.send_message(
                        f"❌ <b>Không thể lấy dữ liệu cho {symbol}</b>\n\n"
                        "Symbol có thể không tồn tại hoặc không có đủ lịch sử giao dịch."
                    )
                    return
                
                # Validate data
                for tf, df in klines_dict.items():
                    if df is None or len(df) < 14:
                        continue
                    if df[['high', 'low', 'close', 'volume']].isnull().any().any():
                        logger.warning(f"Skipping {symbol} {tf} - contains invalid data")
                        klines_dict[tf] = None
                
                klines_dict = {k: v for k, v in klines_dict.items() if v is not None}
                
                if not klines_dict:
                    self.bot.send_message(f"❌ Invalid data for {symbol}. Cannot analyze.")
                    return
                
                rsi_mfi_result = self._analyze_multi_timeframe(
                    klines_dict,
                    self._config.RSI_PERIOD,
                    self._config.MFI_PERIOD,
                    self._config.RSI_LOWER,
                    self._config.RSI_UPPER,
                    self._config.MFI_LOWER,
                    self._config.MFI_UPPER
                )
                
                # === 3. STOCH+RSI ANALYSIS ===
                stoch_rsi_result = self.stoch_rsi_analyzer.analyze_multi_timeframe(
                    symbol, 
                    timeframes=['1m', '5m', '4h', '1d']
                )
                
                # Get price and market data
                price = self.binance.get_current_price(symbol)
                ticker_24h = self.binance.get_24h_data(symbol)
                
                # === 4. BUILD COMPREHENSIVE MESSAGE ===
                msg = f"<b>📊 COMPREHENSIVE ANALYSIS</b>\n\n"
                msg += f"<b>💎 {symbol}</b>\n"
                msg += f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                
                # Current Price
                if ticker_24h:
                    current_price = ticker_24h['last_price']
                    price_change_24h = ticker_24h['price_change_percent']
                    volume_24h = ticker_24h['volume']
                    
                    msg += f"<b>💰 Giá Hiện Tại:</b> ${current_price:,.8f}\n"
                    msg += f"<b>📈 24h Change:</b> {price_change_24h:+.2f}%\n"
                    msg += f"<b>💧 24h Volume:</b> ${volume_24h:,.0f}\n\n"
                
                msg += "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                
                # === PUMP/DUMP SECTION ===
                msg += "<b>🚀 PUMP/DUMP DETECTION (3-Layer)</b>\n\n"
                
                if pump_result and 'final_score' in pump_result:
                    score = pump_result['final_score']
                    
                    if score >= 80:
                        status_emoji = "🔴"
                        status_text = "PUMP CAO"
                    elif score >= 60:
                        status_emoji = "🟡"
                        status_text = "PUMP VỪA"
                    elif score >= 40:
                        status_emoji = "🟢"
                        status_text = "PUMP YẾU"
                    else:
                        status_emoji = "⚪"
                        status_text = "KHÔNG PUMP"
                    
                    msg += f"{status_emoji} <b>Status:</b> {status_text}\n"
                    msg += f"<b>🎯 Final Score:</b> {score:.0f}%\n\n"
                    
                    # Layer breakdown
                    if 'layer1' in pump_result and pump_result['layer1']:
                        layer1 = pump_result['layer1']
                        msg += f"   ⚡ Layer 1 (5m): {layer1['pump_score']:.0f}%\n"
                    
                    if 'layer2' in pump_result and pump_result['layer2']:
                        layer2 = pump_result['layer2']
                        msg += f"   ✅ Layer 2 (1h/4h): {layer2['pump_score']:.0f}%\n"
                    
                    if 'layer3' in pump_result and pump_result['layer3']:
                        layer3 = pump_result['layer3']
                        msg += f"   📈 Layer 3 (1D): {layer3['pump_score']:.0f}%\n"
                else:
                    msg += "⚪ <b>Status:</b> Không có tín hiệu pump rõ ràng\n"
                
                msg += "\n━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                
                # === RSI/MFI SECTION ===
                msg += "<b>📊 RSI/MFI MULTI-TIMEFRAME</b>\n\n"
                
                if rsi_mfi_result and 'timeframes' in rsi_mfi_result:
                    consensus = rsi_mfi_result['consensus']
                    strength = rsi_mfi_result['consensus_strength']
                    
                    if consensus == 'BUY':
                        consensus_emoji = "🟢"
                    elif consensus == 'SELL':
                        consensus_emoji = "🔴"
                    else:
                        consensus_emoji = "🟡"
                    
                    msg += f"{consensus_emoji} <b>Consensus:</b> {consensus} (Strength: {strength}/4)\n\n"
                    
                    # Timeframe breakdown
                    for tf, data in rsi_mfi_result['timeframes'].items():
                        signal = data['signal']
                        rsi = data['rsi']
                        mfi = data['mfi']
                        
                        signal_emoji = "🟢" if signal == 'BUY' else "🔴" if signal == 'SELL' else "🟡"
                        
                        msg += f"   {signal_emoji} <b>{tf}:</b> {signal}\n"
                        msg += f"      RSI: {rsi:.1f} | MFI: {mfi:.1f}\n"
                else:
                    msg += "⚪ Không có dữ liệu RSI/MFI\n"
                
                msg += "\n━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                
                # === STOCH+RSI SECTION ===
                msg += "<b>📈 STOCH+RSI MULTI-TIMEFRAME</b>\n\n"
                
                if stoch_rsi_result and 'timeframes' in stoch_rsi_result:
                    consensus = stoch_rsi_result['consensus']
                    strength = stoch_rsi_result['consensus_strength']
                    
                    if consensus == 'BUY':
                        consensus_emoji = "🟢"
                    elif consensus == 'SELL':
                        consensus_emoji = "🔴"
                    else:
                        consensus_emoji = "🟡"
                    
                    msg += f"{consensus_emoji} <b>Consensus:</b> {consensus} (Strength: {strength}/4)\n\n"
                    
                    # Timeframe breakdown
                    for tf_data in stoch_rsi_result['timeframes']:
                        tf = tf_data['timeframe']
                        signal = tf_data['signal_text']
                        rsi = tf_data['rsi']
                        stoch_k = tf_data['stoch_k']
                        
                        signal_emoji = "🟢" if 'BUY' in signal else "🔴" if 'SELL' in signal else "🟡"
                        
                        msg += f"   {signal_emoji} <b>{tf}:</b> {signal}\n"
                        msg += f"      RSI: {rsi:.1f} | Stoch: {stoch_k:.1f}\n"
                else:
                    msg += "⚪ Không có dữ liệu Stoch+RSI\n"
                
                msg += "\n━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                
                # === TRADING RECOMMENDATION ===
                msg += "<b>🎯 TỔNG KẾT & KHUYẾN NGHỊ</b>\n\n"
                
                # Calculate overall signal
                buy_signals = 0
                sell_signals = 0
                total_signals = 0
                
                # Count RSI/MFI signals
                if rsi_mfi_result and 'consensus' in rsi_mfi_result:
                    total_signals += 1
                    if rsi_mfi_result['consensus'] == 'BUY':
                        buy_signals += 1
                    elif rsi_mfi_result['consensus'] == 'SELL':
                        sell_signals += 1
                
                # Count Stoch+RSI signals
                if stoch_rsi_result and 'consensus' in stoch_rsi_result:
                    total_signals += 1
                    if stoch_rsi_result['consensus'] == 'BUY':
                        buy_signals += 1
                    elif stoch_rsi_result['consensus'] == 'SELL':
                        sell_signals += 1
                
                # Count Pump signal
                if pump_result and 'final_score' in pump_result:
                    total_signals += 1
                    if pump_result['final_score'] >= 60:
                        buy_signals += 1
                
                # Overall recommendation
                if buy_signals >= 2 and sell_signals == 0:
                    msg += "✅ <b>KHUYẾN NGHỊ: MUA/LONG</b>\n"
                    msg += f"   • Tín hiệu BUY: {buy_signals}/{total_signals}\n"
                    msg += "   • Đa số indicators đồng thuận BUY\n"
                elif sell_signals >= 2 and buy_signals == 0:
                    msg += "❌ <b>KHUYẾN NGHỊ: BÁN/SHORT</b>\n"
                    msg += f"   • Tín hiệu SELL: {sell_signals}/{total_signals}\n"
                    msg += "   • Đa số indicators đồng thuận SELL\n"
                elif buy_signals > sell_signals:
                    msg += "🟢 <b>KHUYẾN NGHỊ: CHỜ XÁC NHẬN MUA</b>\n"
                    msg += f"   • Tín hiệu BUY: {buy_signals}/{total_signals}\n"
                    msg += f"   • Tín hiệu SELL: {sell_signals}/{total_signals}\n"
                    msg += "   • Theo dõi thêm trước khi vào lệnh\n"
                elif sell_signals > buy_signals:
                    msg += "🔴 <b>KHUYẾN NGHỊ: CHỜ XÁC NHẬN BÁN</b>\n"
                    msg += f"   • Tín hiệu SELL: {sell_signals}/{total_signals}\n"
                    msg += f"   • Tín hiệu BUY: {buy_signals}/{total_signals}\n"
                    msg += "   • Có xu hướng giảm, cẩn trọng\n"
                else:
                    msg += "🟡 <b>KHUYẾN NGHỊ: CHỜ ĐỢI</b>\n"
                    msg += f"   • Tín hiệu BUY: {buy_signals}/{total_signals}\n"
                    msg += f"   • Tín hiệu SELL: {sell_signals}/{total_signals}\n"
                    msg += "   • Indicators mâu thuẫn nhau\n"
                    msg += "   • Tránh vào lệnh trong lúc này\n"
                
                msg += "\n⚠️ <i>Đây là phân tích kỹ thuật tự động, không phải tư vấn tài chính</i>"
                
                # Create AI Analysis button
                ai_keyboard = self.bot.create_ai_analysis_keyboard(symbol)
                
                # Send comprehensive analysis
                self.bot.send_message(msg, reply_markup=ai_keyboard)
                
                logger.info(f"✅ Sent comprehensive analysis for {symbol}")
                
            except Exception as e:
                logger.error(f"Error analyzing symbol: {e}", exc_info=True)
                self.bot.send_message(f"❌ Error analyzing {symbol}: {str(e)}")
        
        logger.info("All command handlers registered")
    
    def start_polling(self):
        """Start polling for commands"""
        logger.info("Starting command polling...")
        
        # Wait a bit to ensure any previous instance has released the connection
        import time
        time.sleep(2)
        
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                logger.info(f"Attempting to start polling (attempt {retry_count + 1}/{max_retries})...")
                
                # Use infinity_polling with better error handling
                self.telegram_bot.infinity_polling(
                    timeout=30,  # Increased timeout
                    long_polling_timeout=20,  # Increased long polling
                    skip_pending=True,  # Skip old messages on restart
                    allowed_updates=['message', 'callback_query']  # Only handle relevant updates
                )
                break  # If successful, exit loop
                
            except KeyboardInterrupt:
                logger.info("Polling stopped by user")
                break
                
            except Exception as e:
                error_msg = str(e)
                
                # Check if it's a conflict error (409)
                if "409" in error_msg or "Conflict" in error_msg:
                    retry_count += 1
                    logger.warning(f"Bot instance conflict detected (attempt {retry_count}/{max_retries})")
                    
                    if retry_count < max_retries:
                        wait_time = 5 * retry_count  # Exponential backoff
                        logger.info(f"Waiting {wait_time} seconds before retry...")
                        time.sleep(wait_time)
                        
                        # Try to clear the webhook (in case it's set)
                        try:
                            logger.info("Attempting to delete webhook...")
                            self.telegram_bot.delete_webhook(drop_pending_updates=True)
                            time.sleep(2)
                        except Exception as webhook_error:
                            logger.error(f"Failed to delete webhook: {webhook_error}")
                    else:
                        logger.error("Max retries reached. Another bot instance may be running.")
                        logger.error("Please kill all Python processes and try again.")
                        raise
                else:
                    logger.error(f"Polling error: {e}", exc_info=True)
                    raise
    
    def process_commands_non_blocking(self):
        """Process commands without blocking (for use in main loop)"""
        try:
            self.telegram_bot.polling(none_stop=False, timeout=1)
        except Exception as e:
            logger.error(f"Error processing commands: {e}")
