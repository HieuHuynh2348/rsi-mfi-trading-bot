"""
Telegram Bot Module
Handles sending messages and charts to Telegram
"""

import telebot
from telebot import types
import logging
import io
from datetime import datetime

logger = logging.getLogger(__name__)


class TelegramBot:
    def __init__(self, token, chat_id):
        """Initialize Telegram bot"""
        self.bot = telebot.TeleBot(token)
        self.chat_id = chat_id
        logger.info("Telegram bot initialized")
    
    def send_message(self, message, parse_mode='HTML', reply_markup=None):
        """
        Send a text message
        
        Args:
            message: Message text
            parse_mode: 'HTML' or 'Markdown'
            reply_markup: Optional keyboard markup
        """
        try:
            self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode=parse_mode,
                reply_markup=reply_markup
            )
            logger.info("Message sent successfully")
            return True
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return False
    
    def create_main_menu_keyboard(self):
        """Create main menu inline keyboard"""
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        
        # Row 1: Analysis
        keyboard.row(
            types.InlineKeyboardButton("📊 Scan Market", callback_data="cmd_scan"),
            types.InlineKeyboardButton("⭐ Scan Watchlist", callback_data="cmd_scanwatch")
        )
        
        # Row 2: Watchlist
        keyboard.row(
            types.InlineKeyboardButton("📝 View Watchlist", callback_data="cmd_watchlist"),
            types.InlineKeyboardButton("🗑️ Clear Watchlist", callback_data="cmd_clearwatch")
        )
        
        # Row 3: Volume
        keyboard.row(
            types.InlineKeyboardButton("🔥 Volume Scan", callback_data="cmd_volumescan"),
            types.InlineKeyboardButton("🎯 Volume Settings", callback_data="cmd_volumesensitivity")
        )
        
        # Row 4: Monitor
        keyboard.row(
            types.InlineKeyboardButton("🔔 Start Monitor", callback_data="cmd_startmonitor"),
            types.InlineKeyboardButton("⏸️ Stop Monitor", callback_data="cmd_stopmonitor")
        )
        
        # Row 5: Info & Analysis
        keyboard.row(
            types.InlineKeyboardButton("📈 Top Coins", callback_data="cmd_top"),
            types.InlineKeyboardButton("🔍 Quick Analysis", callback_data="cmd_quickanalysis")
        )
        
        # Row 6: Status & Settings
        keyboard.row(
            types.InlineKeyboardButton("📊 Bot Status", callback_data="cmd_status"),
            types.InlineKeyboardButton("⚙️ Settings", callback_data="cmd_settings")
        )
        
        # Row 7: Monitor Status & Performance
        keyboard.row(
            types.InlineKeyboardButton("� Monitor Status", callback_data="cmd_monitorstatus"),
            types.InlineKeyboardButton("⚡ Performance", callback_data="cmd_performance")
        )
        
        # Row 8: Help
        keyboard.row(
            types.InlineKeyboardButton("ℹ️ Help", callback_data="cmd_help"),
            types.InlineKeyboardButton("ℹ️ About", callback_data="cmd_about")
        )
        
        return keyboard
    
    def create_watchlist_keyboard(self):
        """Create watchlist management keyboard"""
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        
        keyboard.row(
            types.InlineKeyboardButton("📝 View List", callback_data="cmd_watchlist"),
            types.InlineKeyboardButton("⭐ Scan All", callback_data="cmd_scanwatch")
        )
        keyboard.row(
            types.InlineKeyboardButton("🔥 Volume Scan", callback_data="cmd_volumescan"),
            types.InlineKeyboardButton("🗑️ Clear All", callback_data="cmd_clearwatch")
        )
        keyboard.row(
            types.InlineKeyboardButton("🔙 Main Menu", callback_data="cmd_menu")
        )
        
        return keyboard
    
    def create_monitor_keyboard(self):
        """Create monitor control keyboard"""
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        
        keyboard.row(
            types.InlineKeyboardButton("🔔 Start", callback_data="cmd_startmonitor"),
            types.InlineKeyboardButton("⏸️ Stop", callback_data="cmd_stopmonitor")
        )
        keyboard.row(
            types.InlineKeyboardButton("📊 Status", callback_data="cmd_monitorstatus")
        )
        keyboard.row(
            types.InlineKeyboardButton("🔙 Main Menu", callback_data="cmd_menu")
        )
        
        return keyboard
    
    def create_volume_keyboard(self):
        """Create volume settings keyboard"""
        keyboard = types.InlineKeyboardMarkup(row_width=3)
        
        keyboard.row(
            types.InlineKeyboardButton("🔥 Scan Now", callback_data="cmd_volumescan")
        )
        keyboard.row(
            types.InlineKeyboardButton("🔴 Low", callback_data="vol_low"),
            types.InlineKeyboardButton("🟡 Medium", callback_data="vol_medium"),
            types.InlineKeyboardButton("🟢 High", callback_data="vol_high")
        )
        keyboard.row(
            types.InlineKeyboardButton("🔙 Main Menu", callback_data="cmd_menu")
        )
        
        return keyboard
    
    def create_quick_analysis_keyboard(self):
        """Create quick analysis keyboard for popular coins"""
        keyboard = types.InlineKeyboardMarkup(row_width=3)
        
        keyboard.row(
            types.InlineKeyboardButton("₿ BTC", callback_data="analyze_BTCUSDT"),
            types.InlineKeyboardButton("Ξ ETH", callback_data="analyze_ETHUSDT"),
            types.InlineKeyboardButton("₿ BNB", callback_data="analyze_BNBUSDT")
        )
        keyboard.row(
            types.InlineKeyboardButton("🔗 LINK", callback_data="analyze_LINKUSDT"),
            types.InlineKeyboardButton("⚪ DOT", callback_data="analyze_DOTUSDT"),
            types.InlineKeyboardButton("🔵 ADA", callback_data="analyze_ADAUSDT")
        )
        keyboard.row(
            types.InlineKeyboardButton("🟣 SOL", callback_data="analyze_SOLUSDT"),
            types.InlineKeyboardButton("⚫ AVAX", callback_data="analyze_AVAXUSDT"),
            types.InlineKeyboardButton("🔴 MATIC", callback_data="analyze_MATICUSDT")
        )
        keyboard.row(
            types.InlineKeyboardButton("🔙 Main Menu", callback_data="cmd_menu")
        )
        
        return keyboard
    
    def create_action_keyboard(self):
        """Create action keyboard for commands that completed an action"""
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        
        keyboard.row(
            types.InlineKeyboardButton("📊 Scan Market", callback_data="cmd_scan"),
            types.InlineKeyboardButton("⭐ Scan Watchlist", callback_data="cmd_scanwatch")
        )
        keyboard.row(
            types.InlineKeyboardButton("📝 View Watchlist", callback_data="cmd_watchlist"),
            types.InlineKeyboardButton("🔥 Volume Scan", callback_data="cmd_volumescan")
        )
        keyboard.row(
            types.InlineKeyboardButton("🔙 Main Menu", callback_data="cmd_menu")
        )
        
        return keyboard
    
    def send_photo(self, photo_bytes, caption=''):
        """
        Send a photo
        
        Args:
            photo_bytes: Bytes of image data
            caption: Optional caption
        """
        try:
            self.bot.send_photo(
                chat_id=self.chat_id,
                photo=photo_bytes,
                caption=caption,
                parse_mode='HTML'
            )
            logger.info("Photo sent successfully")
            return True
        except Exception as e:
            logger.error(f"Error sending photo: {e}")
            return False
    
    def send_signal_alert(self, symbol, timeframe_data, consensus, consensus_strength, price=None, market_data=None, volume_data=None):
        """
        Send a formatted signal alert with detailed information
        
        Args:
            symbol: Trading symbol
            timeframe_data: Dictionary of timeframe analysis
            consensus: Overall consensus (BUY/SELL/NEUTRAL)
            consensus_strength: Strength of consensus (0-4)
            price: Current price (optional)
            market_data: Dictionary with 24h data (high, low, change, volume)
            volume_data: Dictionary with volume analysis (current, last, avg, ratios)
        """
        # Get current time
        current_time = datetime.now().strftime('%H:%M:%S')
        
        # Header with symbol
        message = f"<b>💎 #{symbol}</b>\n"
        message += f"🕐 {current_time}\n\n"
        
        # Get timeframe list (sorted)
        timeframes = sorted(timeframe_data.keys(), 
                          key=lambda x: {'5m': 1, '1h': 2, '4h': 3, '1d': 4}.get(x, 5))
        
        # RSI Analysis
        message += "\n<b>📊 RSI ANALYSIS</b>\n"
        
        # Find main timeframe (usually first or most important)
        main_tf = timeframes[0] if timeframes else '5m'
        main_rsi = timeframe_data[main_tf]['rsi']
        last_rsi = timeframe_data[main_tf].get('last_rsi', main_rsi)
        rsi_change = timeframe_data[main_tf].get('rsi_change', 0)
        
        # RSI status emoji
        if main_rsi >= 80:
            rsi_status = "🔥"
            rsi_alert = f"⚠️ Overbought Alert: {main_rsi:.0f}+ 🔴🔴"
        elif main_rsi <= 20:
            rsi_status = "❄️"
            rsi_alert = f"💎 Oversold Alert: {main_rsi:.0f}- 🟢🟢"
        else:
            rsi_status = "⚖️"
            rsi_alert = None
        
        # RSI trend indicator
        rsi_trend = "📈" if rsi_change > 0 else ("📉" if rsi_change < 0 else "➡️")
        
        message += f"📍 <b>Main RSI:</b> {main_rsi:.2f} {rsi_status}\n"
        message += f"⏮️ <b>Last RSI:</b> {last_rsi:.2f} {rsi_trend} <i>({rsi_change:+.2f})</i>\n"
        if rsi_alert:
            message += f"{rsi_alert}\n\n"
        else:
            message += "\n"
        
        # All timeframe RSI values
        for tf in timeframes:
            rsi_val = timeframe_data[tf]['rsi']
            last_val = timeframe_data[tf].get('last_rsi', rsi_val)
            change = timeframe_data[tf].get('rsi_change', 0)
            
            if rsi_val >= 80:
                emoji = "🔴"
                status = "Overbought"
            elif rsi_val <= 20:
                emoji = "🟢"
                status = "Oversold"
            else:
                emoji = "🔵"
                status = "Normal"
            
            trend = "↗" if change > 0 else ("↘" if change < 0 else "→")
            message += f"  ├─ {tf.upper()}: {rsi_val:.2f} {emoji} <i>{status}</i> {trend}\n"
        
        # MFI Analysis
        message += "\n<b>💰 MFI ANALYSIS</b>\n"
        main_mfi = timeframe_data[main_tf]['mfi']
        last_mfi = timeframe_data[main_tf].get('last_mfi', main_mfi)
        mfi_change = timeframe_data[main_tf].get('mfi_change', 0)
        
        # MFI status emoji
        if main_mfi >= 80:
            mfi_status = "🔥"
            mfi_alert = f"⚠️ Overbought Alert: {main_mfi:.0f}+ 🔴🔴"
        elif main_mfi <= 20:
            mfi_status = "❄️"
            mfi_alert = f"💎 Oversold Alert: {main_mfi:.0f}- 🟢🟢"
        else:
            mfi_status = "⚖️"
            mfi_alert = None
        
        # MFI trend indicator
        mfi_trend = "📈" if mfi_change > 0 else ("📉" if mfi_change < 0 else "➡️")
        
        message += f"📍 <b>Main MFI:</b> {main_mfi:.2f} {mfi_status}\n"
        message += f"⏮️ <b>Last MFI:</b> {last_mfi:.2f} {mfi_trend} <i>({mfi_change:+.2f})</i>\n"
        if mfi_alert:
            message += f"{mfi_alert}\n\n"
        else:
            message += "\n"
        
        # All timeframe MFI values
        for tf in timeframes:
            mfi_val = timeframe_data[tf]['mfi']
            last_val = timeframe_data[tf].get('last_mfi', mfi_val)
            change = timeframe_data[tf].get('mfi_change', 0)
            
            if mfi_val >= 80:
                emoji = "🔴"
                status = "Overbought"
            elif mfi_val <= 20:
                emoji = "🟢"
                status = "Oversold"
            else:
                emoji = "🔵"
                status = "Normal"
            
            trend = "↗" if change > 0 else ("↘" if change < 0 else "→")
            message += f"  ├─ {tf.upper()}: {mfi_val:.2f} {emoji} <i>{status}</i> {trend}\n"
        
        # Consensus Analysis
        message += "\n<b>🎯 CONSENSUS SIGNALS</b>\n"
        for tf in timeframes:
            data = timeframe_data[tf]
            avg = (data['rsi'] + data['mfi']) / 2
            
            if data['signal'] == 1:
                signal_text = "🟢 BUY"
                arrow = "📈"
            elif data['signal'] == -1:
                signal_text = "🔴 SELL"
                arrow = "📉"
            else:
                signal_text = "⚪ NEUTRAL"
                arrow = "➡️"
            
            message += f"  {arrow} {tf.upper()}: {avg:.1f} → {signal_text}\n"
        
        # Overall consensus
        if consensus == "BUY":
            consensus_icon = "�"
            consensus_bar = "🟩" * consensus_strength + "⬜" * (4 - consensus_strength)
        elif consensus == "SELL":
            consensus_icon = "⚠️"
            consensus_bar = "🟥" * consensus_strength + "⬜" * (4 - consensus_strength)
        else:
            consensus_icon = "💤"
            consensus_bar = "⬜" * 4
        
        message += f"\n<b>{consensus_icon} OVERALL: {consensus}</b>\n"
        message += f"<b>Strength: {consensus_bar} ({consensus_strength}/4)</b>\n"
        
        # Price Information
        message += "\n<b>💵 PRICE INFO</b>\n"
        if price:
            message += f"💲 Current: <b>${price:,.4f}</b>\n"
        
        # 24h Market Data
        if market_data:
            change_24h = market_data.get('price_change_percent', 0)
            volume_24h = market_data.get('volume', 0)
            high_24h = market_data.get('high', 0)
            low_24h = market_data.get('low', 0)
            
            # Format volume intelligently
            if volume_24h >= 1e9:  # Billions
                vol_str = f"${volume_24h/1e9:.2f}B"
            elif volume_24h >= 1e6:  # Millions
                vol_str = f"${volume_24h/1e6:.2f}M"
            elif volume_24h >= 1e3:  # Thousands
                vol_str = f"${volume_24h/1e3:.2f}K"
            else:
                vol_str = f"${volume_24h:.2f}"
            
            change_emoji = "📈" if change_24h >= 0 else "📉"
            change_color = "🟩" if change_24h >= 0 else "🟥"
            message += f"\n📊 <b>24h Change:</b> {change_emoji} {change_color} <b>{change_24h:+.2f}%</b>\n"
            message += f"💎 <b>Volume:</b> {vol_str}\n"
            
            if price and high_24h > 0:
                high_diff = ((high_24h - price) / price) * 100
                message += f"🔺 <b>High:</b> ${high_24h:,.4f} <i>(+{high_diff:.2f}%)</i>\n"
            
            if price and low_24h > 0:
                low_diff = ((price - low_24h) / price) * 100
                message += f"🔻 <b>Low:</b> ${low_24h:,.4f} <i>(+{low_diff:.2f}%)</i>\n"
        
        # Volume Analysis (if available)
        if volume_data:
            current_vol = volume_data.get('current_volume', 0)
            last_vol = volume_data.get('last_volume', 0)
            avg_vol = volume_data.get('avg_volume', 0)
            is_anomaly = volume_data.get('is_anomaly', False)
            
            # Format volumes intelligently
            def format_volume(vol):
                if vol >= 1e9:
                    return f"{vol/1e9:.2f}B"
                elif vol >= 1e6:
                    return f"{vol/1e6:.2f}M"
                elif vol >= 1e3:
                    return f"{vol/1e3:.2f}K"
                else:
                    return f"{vol:.2f}"
            
            message += f"\n<b>📊 VOLUME ANALYSIS</b>\n"
            
            # Show anomaly warning if detected
            if is_anomaly:
                message += f"⚡ <b>VOLUME SPIKE DETECTED!</b> ⚡\n"
            
            message += f"💹 <b>Current:</b> {format_volume(current_vol)}\n"
            message += f"⏮️ <b>Last:</b> {format_volume(last_vol)}\n"
            message += f"📊 <b>Average:</b> {format_volume(avg_vol)}\n"
            
            # Show ratios
            if last_vol > 0:
                last_ratio = volume_data.get('last_candle_ratio', 0)
                last_increase = volume_data.get('last_candle_increase_percent', 0)
                ratio_emoji = "📈" if last_ratio > 1 else ("📉" if last_ratio < 1 else "➡️")
                message += f"🔄 <b>vs Last:</b> {last_ratio:.2f}x {ratio_emoji} <i>({last_increase:+.1f}%)</i>\n"
            
            if avg_vol > 0:
                avg_ratio = volume_data.get('avg_ratio', 0)
                avg_increase = volume_data.get('avg_increase_percent', 0)
                avg_emoji = "📈" if avg_ratio > 1 else ("📉" if avg_ratio < 1 else "➡️")
                message += f"🔄 <b>vs Avg:</b> {avg_ratio:.2f}x {avg_emoji} <i>({avg_increase:+.1f}%)</i>\n"
        
        return self.send_message(message)
    
    def send_summary_table(self, signals_list):
        """
        Send a summary table of multiple signals
        
        Args:
            signals_list: List of signal dictionaries
        """
        if not signals_list:
            return self.send_message("💤 No signals detected at this time.")
        
        # Sort by consensus strength
        signals_list = sorted(signals_list, key=lambda x: x['consensus_strength'], reverse=True)
        
        message = "<b>📊 MARKET SCAN SUMMARY</b>\n\n"
        
        buy_signals = [s for s in signals_list if s['consensus'] == 'BUY']
        sell_signals = [s for s in signals_list if s['consensus'] == 'SELL']
        
        if buy_signals:
            message += "<b>🚀 BUY SIGNALS:</b>\n"
            for signal in buy_signals:
                strength_bar = "🟩" * signal['consensus_strength'] + "⬜" * (4 - signal['consensus_strength'])
                message += f"  ✅ <b>{signal['symbol']}</b>\n"
                message += f"     {strength_bar} {signal['consensus_strength']}/4\n"
            message += "\n"
        
        if sell_signals:
            message += "<b>⚠️ SELL SIGNALS:</b>\n"
            for signal in sell_signals:
                strength_bar = "🟥" * signal['consensus_strength'] + "⬜" * (4 - signal['consensus_strength'])
                message += f"  ⛔ <b>{signal['symbol']}</b>\n"
                message += f"     {strength_bar} {signal['consensus_strength']}/4\n"
            message += "\n"
        
        message += f"<b>📈 Total Signals:</b> {len(signals_list)}\n"
        message += f"   🟢 Buy: {len(buy_signals)} | 🔴 Sell: {len(sell_signals)}\n"
        message += f"\n🕐 <i>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>"
        
        return self.send_message(message)
    
    def test_connection(self):
        """Test Telegram bot connection"""
        try:
            me = self.bot.get_me()
            logger.info(f"Telegram bot connected: @{me.username}")
            return True
        except Exception as e:
            logger.error(f"Telegram bot connection failed: {e}")
            return False
