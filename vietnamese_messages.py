"""
Vietnamese Messages for Trading Bot
All user-facing messages in Vietnamese
"""

from datetime import datetime

# Help and Info Messages
HELP_MESSAGE = """
<b>🤖 BOT GIAO DỊCH CRYPTO - PHIÊN BẢN 3.0</b>

<b>🎛️ MENU TƯƠNG TÁC:</b>
/menu - Mở menu nút bấm (khuyên dùng!)

<b>📊 PHÂN TÍCH TOÀN DIỆN:</b>
/<b>SYMBOL</b> - Phân tích TẤT CẢ indicators
Ví dụ: /BTC /ETH /LINK

<b>🏛️ Bao gồm 10+ Indicators:</b>
   ✅ PUMP/DUMP Detection (3 layers)
   ✅ RSI/MFI Multi-timeframe (4 TF)
   ✅ Stoch+RSI Multi-timeframe (4 TF)
   ✅ Volume Profile (POC/VAH/VAL)
   ✅ Fair Value Gaps (FVG)
   ✅ Order Blocks (OB)
   ✅ Support/Resistance Zones
   ✅ Smart Money Concepts (BOS/CHoCH)
   ✅ Trading Recommendation
   🤖 AI Analysis với Gemini 2.0

<b>🚀 PUMP & DUMP:</b>
/pumpscan <b>SYMBOL</b> - Quét pump 3 layers
/startpumpwatch - Tự động phát hiện pump
/stoppumpwatch - Dừng pump watch
/pumpstatus - Trạng thái & settings
/top - Top 10 coin khối lượng cao

<b>⚙️ ĐIỀU KHIỂN BOT:</b>
/status - Trạng thái bot & cài đặt
/scan - Quét thị trường ngay
/settings - Xem cài đặt
/performance - Hiệu suất quét

<b>⭐ DANH SÁCH THEO DÕI:</b>
/watch <b>SYMBOL</b> - Thêm vào watchlist
/unwatch <b>SYMBOL</b> - Xóa coin
/watchlist - Xem danh sách
/scanwatch - Quét watchlist
/clearwatch - Xóa tất cả

<b>🔔 TỰ ĐỘNG THEO DÕI:</b>
/startmonitor - Bật thông báo tự động
/stopmonitor - Tắt thông báo
/monitorstatus - Trạng thái monitor

<b>🔥 CẢNH BÁO KHỐI LƯỢNG:</b>
/volumescan - Quét tăng đột biến volume
/volumesensitivity - Đặt độ nhạy

<b>🌍 QUÉT THỊ TRƯỜNG:</b>
/startmarketscan - Tự động quét TẤT CẢ Binance
/stopmarketscan - Dừng quét thị trường
/marketstatus - Trạng thái scanner

<b>🤖 GIÁM SÁT BOT:</b>
/startbotmonitor - Tự động phát hiện bot
/stopbotmonitor - Dừng giám sát bot
/botmonitorstatus - Trạng thái monitor
/botscan - Quét bot thủ công
/botthreshold - Đặt ngưỡng cảnh báo

<b>ℹ️ THÔNG TIN:</b>
/help - Hiện tin nhắn này
/about - Về bot

<i>💡 Mẹo: Dùng /BTC để xem 10+ indicators + AI analysis!</i>
<i>🏛️ Institutional indicators giúp phát hiện smart money</i>
"""

ABOUT_MESSAGE = """
<b>🚀 BOT GIAO DỊCH CRYPTO - PHIÊN BẢN 3.0</b>

<b>📌 Phiên bản:</b> 3.0 INSTITUTIONAL
<b>☁️ Nền tảng:</b> Railway.app
<b>🏦 Sàn:</b> Binance
<b>🤖 AI Engine:</b> Google Gemini 1.5 Pro

<b>✨ TÍNH NĂNG CHÍNH:</b>
✅ Phân tích đa khung thời gian (1m-1d)
✅ 10+ Indicators tích hợp
✅ Institutional indicators (Smart Money)
✅ AI Analysis với Gemini 2.0
✅ Pump/Dump Detection (3 layers)
✅ Bot Activity Monitor
✅ Giám sát thời gian thực 24/7
✅ Xử lý song song (5-20 workers)
✅ Watchlist tự động theo dõi
✅ Lệnh tương tác với inline keyboards

<b>📊 CHỈ BÁO KỸ THUẬT:</b>
• RSI + MFI (Retail indicators)
• Stochastic + RSI (Momentum)
• Volume Analysis (24h data)

<b>🏛️ CHỈ BÁO INSTITUTIONAL:</b>
• Volume Profile (POC/VAH/VAL)
• Fair Value Gaps (Imbalance zones)
• Order Blocks (Institutional footprints)
• Support/Resistance (Delta volume)
• Smart Money Concepts (BOS/CHoCH/EQH/EQL)

<b>⏱️ KHUNG THỜI GIAN:</b>
• Scalping: 1m, 5m, 15m
• Intraday: 1h, 4h
• Swing: 1d
• Multi-TF consensus: 4 timeframes

<b>🤖 AI ANALYSIS:</b>
• Gemini 1.5 Pro model
• JSON structured data input
• 60% weight on institutional indicators
• Confluence analysis across all indicators
• Vietnamese language output
• Entry/Exit points với risk management

<b>⚡ HIỆU SUẤT:</b>
• Auto-scaling: 5-20 workers động
• Fast scan mode
• Parallel processing
• 15-min cache system
• Rate limiting protection

<i>⚠️ Lưu ý: Không phải lời khuyên tài chính!</i>
<i>📚 Luôn tự nghiên cứu (DYOR)</i>
<i>🏛️ Institutional indicators = Smart Money footprints</i>
"""

# Error Messages
ERROR_OCCURRED = "❌ Lỗi: {error}"
BOT_DETECTION_FAILED = "❌ Phát hiện bot thất bại"

# Usage Messages
PRICE_USAGE = "❌ Cách dùng: /price SYMBOL\nVí dụ: /price BTC"
DAILY_USAGE = "❌ Cách dùng: /24h SYMBOL\nVí dụ: /24h BTC"
WATCH_USAGE = "❌ Cách dùng: /watch SYMBOL\nVí dụ: /watch BTC"
UNWATCH_USAGE = "❌ Cách dùng: /unwatch SYMBOL\nVí dụ: /unwatch BTC"

# Watchlist Messages
WATCHLIST_COUNT = "📊 Tổng số đang theo dõi: {count} symbols"

# Status Messages
def get_status_message(config):
    return f"""
<b>🤖 Trạng Thái Bot - Phiên bản 3.0</b>

<b>⚡ Hệ thống:</b> ✅ Trực tuyến
<b>🔗 Binance:</b> ✅ Đã kết nối
<b>💬 Telegram:</b> ✅ Đã kết nối
<b>🤖 AI Engine:</b> ✅ Gemini 1.5 Pro

<b>⚙️ Cài đặt Technical:</b>
• Khoảng quét: {config.SCAN_INTERVAL}s
• Đồng thuận tối thiểu: {config.MIN_CONSENSUS_STRENGTH}/4
• RSI Period: {config.RSI_PERIOD} | MFI Period: {config.MFI_PERIOD}
• Timeframes: {', '.join(config.TIMEFRAMES)}

<b>🏛️ Institutional Indicators:</b>
✅ Volume Profile (POC/VAH/VAL)
✅ Fair Value Gaps (Imbalance detection)
✅ Order Blocks (Smart money zones)
✅ Support/Resistance (Delta volume)
✅ Smart Money Concepts (BOS/CHoCH)

<b>📊 Cặp Giao Dịch:</b>
• Quote: {config.QUOTE_ASSET}
• Volume tối thiểu: ${config.MIN_VOLUME_USDT:,.0f}

<b>🕐 Thời gian:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

def get_settings_message(config):
    return f"""
<b>⚙️ Cài Đặt Bot - Phiên bản 3.0</b>

<b>📊 Technical Indicators:</b>
• RSI Period: {config.RSI_PERIOD} | Threshold: {config.RSI_LOWER}-{config.RSI_UPPER}
• MFI Period: {config.MFI_PERIOD} | Threshold: {config.MFI_LOWER}-{config.MFI_UPPER}
• Stochastic+RSI: HLCC/4 smoothing
• Volume Analysis: 24h tracking

<b>🏛️ Institutional Indicators:</b>
• Volume Profile: 25 price levels
• Fair Value Gaps: ATR filtering
• Order Blocks: Swing (50) + Internal (5)
• S/R Zones: Delta volume analysis
• SMC: BOS/CHoCH/EQH/EQL detection

<b>⏱️ Khung thời gian:</b>
• Technical: {', '.join(config.TIMEFRAMES)}
• Institutional: 1h, 4h, 1d
• AI Analysis: Multi-TF consensus

<b>🎯 Tiêu chí tín hiệu:</b>
• Consensus tối thiểu: {config.MIN_CONSENSUS_STRENGTH}/4
• Scan interval: {config.SCAN_INTERVAL}s
• Cache duration: 15 phút

<b>💹 Bộ lọc thị trường:</b>
• Quote asset: {config.QUOTE_ASSET}
• Min volume: ${config.MIN_VOLUME_USDT:,.0f}
• Excluded: {', '.join(config.EXCLUDED_KEYWORDS) if config.EXCLUDED_KEYWORDS else 'None'}

<b>📈 Display settings:</b>
• Charts: {'✅ Enabled' if config.SEND_CHARTS else '❌ Disabled'}
• Summary only: {'✅ Yes' if config.SEND_SUMMARY_ONLY else '❌ No'}
• Max coins/message: {config.MAX_COINS_PER_MESSAGE}

<b>⚡ Performance:</b>
• Fast scan: {'✅ Enabled' if config.USE_FAST_SCAN else '❌ Disabled'}
• Workers: {'Auto-scaling (5-20)' if config.MAX_SCAN_WORKERS == 0 else config.MAX_SCAN_WORKERS}
• Parallel processing: ✅ Active

<b>🤖 AI Configuration:</b>
• Model: Gemini 1.5 Pro
• Input format: JSON structured
• Weight: 60% institutional + 40% technical
• Output: Vietnamese + Entry/Exit points

💡 Dùng /performance để xem chi tiết quét
"""

# Signal Messages
def get_signal_alert(symbol, timeframe_data, consensus, strength, price, market_data, volume_data):
    """Generate signal alert message in Vietnamese"""
    
    # Consensus emoji and text
    if consensus == "BUY":
        consensus_emoji = "🟢"
        consensus_text = "MUA"
        action_text = "Cơ hội MUA tiềm năng"
    elif consensus == "SELL":
        consensus_emoji = "🔴"
        consensus_text = "BÁN"
        action_text = "Cơ hội BÁN tiềm năng"
    else:
        consensus_emoji = "⚪"
        consensus_text = "TRUNG LẬP"
        action_text = "Không có tín hiệu rõ ràng"
    
    # Build message
    msg = f"<b>💎 #{symbol}</b>\n"
    msg += f"🕐 {datetime.now().strftime('%H:%M:%S')}\n\n"
    msg += f"{consensus_emoji} <b>TÍN HIỆU {consensus_text}</b>\n\n"
    
    # Consensus strength
    strength_bar = "█" * strength + "░" * (4 - strength)
    msg += f"<b>Độ mạnh:</b> {strength_bar} {strength}/4\n"
    msg += f"<b>Hành động:</b> {action_text}\n\n"
    
    # Timeframe analysis
    if timeframe_data:
        timeframes = sorted(timeframe_data.keys(), 
                          key=lambda x: {'5m': 1, '1h': 2, '4h': 3, '1d': 4}.get(x, 5))
        
        msg += f"<b>📊 PHÂN TÍCH RSI:</b>\n"
        for tf in timeframes:
            rsi_val = timeframe_data[tf]['rsi']
            change = timeframe_data[tf].get('rsi_change', 0)
            
            if rsi_val >= 80:
                emoji = "🔴"
                status = "Quá mua"
            elif rsi_val <= 20:
                emoji = "🟢"
                status = "Quá bán"
            else:
                emoji = "🔵"
                status = "Bình thường"
            
            trend = "↗" if change > 0 else ("↘" if change < 0 else "→")
            msg += f"  {tf.upper()}: {rsi_val:.2f} {emoji} {status} {trend}\n"
        
        msg += f"\n<b>💰 PHÂN TÍCH MFI:</b>\n"
        for tf in timeframes:
            mfi_val = timeframe_data[tf]['mfi']
            change = timeframe_data[tf].get('mfi_change', 0)
            
            if mfi_val >= 80:
                emoji = "🔴"
                status = "Quá mua"
            elif mfi_val <= 20:
                emoji = "🟢"
                status = "Quá bán"
            else:
                emoji = "🔵"
                status = "Bình thường"
            
            trend = "↗" if change > 0 else ("↘" if change < 0 else "→")
            msg += f"  {tf.upper()}: {mfi_val:.2f} {emoji} {status} {trend}\n"
        
        msg += "\n"
    
    # Price info
    if price:
        # If caller pre-formatted price as string use it directly, otherwise format with default 4 decimals
        if isinstance(price, str):
            msg += f"💰 <b>Giá:</b> ${price}\n"
        else:
            msg += f"💰 <b>Giá:</b> ${price:,.4f}\n"
    
    # 24h data
    if market_data:
        change = market_data.get('price_change_percent', 0)
        emoji = "📈" if change >= 0 else "📉"
        msg += f"{emoji} <b>Thay đổi 24h:</b> {change:+.2f}%\n"
        high_v = market_data.get('high', 0)
        low_v = market_data.get('low', 0)
        if isinstance(high_v, str):
            msg += f"⬆️ <b>Cao 24h:</b> ${high_v}\n"
        else:
            msg += f"⬆️ <b>Cao 24h:</b> ${high_v:,.4f}\n"
        if isinstance(low_v, str):
            msg += f"⬇️ <b>Thấp 24h:</b> ${low_v}\n"
        else:
            msg += f"⬇️ <b>Thấp 24h:</b> ${low_v:,.4f}\n"
        
        # Volume
        volume = market_data.get('volume', 0)
        if volume >= 1e9:
            vol_str = f"${volume/1e9:.2f}B"
        elif volume >= 1e6:
            vol_str = f"${volume/1e6:.2f}M"
        elif volume >= 1e3:
            vol_str = f"${volume/1e3:.2f}K"
        else:
            vol_str = f"${volume:.2f}"
        msg += f"💵 <b>Khối lượng 24h:</b> {vol_str}\n"
    
    # Volume analysis
    if volume_data:
        msg += f"\n<b>📊 PHÂN TÍCH KHỐI LƯỢNG:</b>\n"
        
        if volume_data.get('is_anomaly'):
            msg += f"⚡ <b>TĂNG ĐỘT BIẾN KHỐI LƯỢNG!</b>\n"
        
        current_vol = volume_data.get('current_volume', 0)
        last_vol = volume_data.get('last_volume', 0)
        
        if current_vol >= 1e9:
            curr_str = f"${current_vol/1e9:.2f}B"
        elif current_vol >= 1e6:
            curr_str = f"${current_vol/1e6:.2f}M"
        else:
            curr_str = f"${current_vol/1e3:.2f}K"
            
        if last_vol >= 1e9:
            last_str = f"${last_vol/1e9:.2f}B"
        elif last_vol >= 1e6:
            last_str = f"${last_vol/1e6:.2f}M"
        else:
            last_str = f"${last_vol/1e3:.2f}K"
        
        msg += f"   Hiện tại: {curr_str}\n"
        msg += f"   Trước đó: {last_str}\n"
        
        if 'volume_ratio' in volume_data:
            ratio = volume_data['volume_ratio']
            msg += f"   Tỷ lệ: {ratio:.2f}x\n"
    
    msg += f"\n⏰ {datetime.now().strftime('%H:%M:%S')}"
    
    return msg

# Watchlist Messages
WATCHLIST_EMPTY = "⭐ <b>Danh sách theo dõi trống</b>\n\nDùng /watch SYMBOL để thêm coin"

def get_watchlist_message(symbols):
    msg = f"⭐ <b>Danh sách Theo dõi</b>\n\n"
    msg += f"📊 Tổng: <b>{len(symbols)}</b> coin\n\n"
    
    for i, symbol in enumerate(symbols, 1):
        msg += f"{i}. {symbol}\n"
    
    msg += f"\n💡 Dùng /scanwatch để quét tất cả"
    msg += f"\n💡 Dùng /unwatch SYMBOL để xóa"
    
    return msg

def add_to_watchlist_success(symbol, count):
    return f"✅ Đã thêm <b>{symbol}</b> vào watchlist\n\n📊 Tổng theo dõi: {count} coin\n💡 Dùng /watchlist để xem tất cả"

def remove_from_watchlist_success(symbol, count):
    return f"✅ Đã xóa <b>{symbol}</b> khỏi watchlist\n\n📊 Còn lại: {count} coin"

# Error Messages  
ERROR_NO_DATA = "❌ Không tìm thấy dữ liệu cho {}. Coin có thể không tồn tại hoặc đã bị hủy niêm yết."
ERROR_INVALID_DATA = "❌ Dữ liệu không hợp lệ cho {}. Không thể phân tích."
ERROR_SYMBOL_NOT_FOUND = "❌ Không tìm thấy {} trên Binance"
ERROR_ANALYSIS_FAILED = "❌ Lỗi phân tích {}: {}"

# Success Messages
SCAN_START = "🔍 <b>Đang quét {} coin...</b>\n\n⚡ Sử dụng {} luồng song song (tự động)\n📊 Sẽ phân tích và gửi TẤT CẢ coin (không chỉ tín hiệu)."
SCAN_COMPLETE = "✅ <b>Quét Watchlist Hoàn tất!</b>"
ANALYSIS_PROCESSING = "🔍 Đang phân tích {}..."

# Monitor Messages
MONITOR_STARTED = "✅ <b>Đã Bật Giám Sát Watchlist!</b>"
MONITOR_STOPPED = "⏸️ <b>Đã Dừng Giám Sát Watchlist</b>"
MONITOR_ALREADY_RUNNING = "ℹ️ <b>Giám sát đang chạy!</b>"
MONITOR_NOT_RUNNING = "ℹ️ Giám sát không chạy."

# Bot Detection Messages
BOT_DETECTION_TITLE = "🤖 PHÂN TÍCH HOẠT ĐỘNG BOT"

def get_bot_detection_message(detection_result):
    """Generate bot detection message in Vietnamese"""
    if not detection_result:
        return BOT_DETECTION_FAILED
    
    symbol = detection_result['symbol']
    bot_score = detection_result['bot_score']
    pump_score = detection_result['pump_score']
    likely_bot = detection_result['likely_bot_activity']
    likely_pump = detection_result['likely_pump_bot']
    confidence = detection_result['confidence']
    pump_confidence = detection_result['pump_confidence']
    
    # Confidence level translation
    confidence_vn = {
        'VERY HIGH': 'RẤT CAO',
        'HIGH': 'CAO',
        'MEDIUM': 'TRUNG BÌNH',
        'LOW': 'THẤP'
    }
    
    # Determine primary pattern
    if likely_pump and pump_score > bot_score:
        emoji = "🚀"
        primary_verdict = "PHÁT HIỆN BOT PUMP"
        alert_level = "⚠️ RỦI RO CAO"
    elif likely_bot:
        emoji = "🤖"
        primary_verdict = "PHÁT HIỆN BOT GIAO DỊCH"
        alert_level = "ℹ️ TRUNG BÌNH"
    else:
        emoji = "👤"
        primary_verdict = "GIAO DỊCH TỰ NHIÊN"
        alert_level = "✅ BÌNH THƯỜNG"
    
    msg = f"{emoji} <b>{BOT_DETECTION_TITLE}</b>\n"
    msg += f"<b>Coin:</b> {symbol}\n"
    msg += f"<b>Mức cảnh báo:</b> {alert_level}\n\n"
    
    # Bot Score
    msg += f"<b>🤖 Điểm Bot Giao dịch:</b> {bot_score}% "
    msg += "█" * int(bot_score / 10) + "░" * (10 - int(bot_score / 10)) + "\n"
    msg += f"   Kết luận: {'CÓ' if likely_bot else 'KHÔNG'} (Độ tin cậy: {confidence_vn.get(confidence, confidence)})\n\n"
    
    # Pump Score
    msg += f"<b>🚀 Điểm Bot Pump:</b> {pump_score}% "
    msg += "█" * int(pump_score / 10) + "░" * (10 - int(pump_score / 10)) + "\n"
    msg += f"   Kết luận: {'CÓ' if likely_pump else 'KHÔNG'} (Độ tin cậy: {confidence_vn.get(pump_confidence, pump_confidence)})\n\n"
    
    msg += f"<b>━━━━━━━━━━━━━━━━━━━━</b>\n\n"
    
    # Orderbook analysis
    ob = detection_result['orderbook']
    msg += f"<b>📊 Sổ Lệnh:</b>\n"
    msg += f"   Spread: {ob.get('spread_percent', 0):.4f}%\n"
    msg += f"   Lệnh lớn: {ob.get('large_orders', 0)}\n"
    msg += f"   Tín hiệu bot: {ob.get('bot_indicators', 0)}/4\n\n"
    
    # Trade analysis
    tr = detection_result['trades']
    msg += f"<b>💱 Mẫu Giao dịch:</b>\n"
    msg += f"   Kích cỡ độc nhất: {tr.get('unique_size_ratio', 0)*100:.1f}%\n"
    msg += f"   Số tròn: {tr.get('round_number_ratio', 0)*100:.1f}%\n"
    msg += f"   Tín hiệu bot: {tr.get('bot_indicators', 0)}/3\n\n"
    
    # Timing analysis
    tm = detection_result['timing']
    msg += f"<b>⏱️ Thời gian:</b>\n"
    msg += f"   Khoảng TB: {tm.get('avg_interval_ms', 0):.1f}ms\n"
    msg += f"   Đa dạng khoảng: {tm.get('interval_diversity', 0)*100:.1f}%\n"
    msg += f"   Tín hiệu bot: {tm.get('bot_indicators', 0)}/3\n\n"
    
    # Pump analysis
    pump = detection_result.get('pump', {})
    msg += f"<b>🚀 Chỉ báo Pump:</b>\n"
    msg += f"   Thay đổi giá 24h: {pump.get('price_change_24h', 0):+.2f}%\n"
    msg += f"   Áp lực mua: {pump.get('buy_ratio', 0)*100:.1f}%\n"
    
    if 'volume_concentration' in pump:
        msg += f"   Tăng khối lượng: {pump.get('volume_concentration', 0):.1f}x\n"
    if 'green_candle_ratio' in pump:
        msg += f"   Nến xanh: {pump.get('green_candle_ratio', 0)*100:.0f}%\n"
    
    msg += f"   Tín hiệu pump: {pump.get('pump_indicators', 0)}/10\n\n"
    
    msg += f"<b>━━━━━━━━━━━━━━━━━━━━</b>\n\n"
    
    # Interpretation
    msg += f"<b>💡 Giải thích:</b>\n"
    
    if likely_pump:
        msg += "   🚀 <b>PHÁT HIỆN BOT PUMP!</b>\n"
        msg += "   ⚠️ Phát hiện mẫu mua có tổ chức\n"
        msg += "   ⚠️ Có thể thổi giá giả tạo\n"
        msg += "   ⚠️ RỦI RO CAO - Có thể là pump & dump\n"
        if pump_score >= 80:
            msg += "   🔴 <b>HOẠT ĐỘNG PUMP CỰC MẠNH!</b>\n"
        msg += "\n   📉 <b>Cảnh báo:</b> Giá có thể sụp đổ đột ngột\n"
        msg += "   💡 <b>Khuyến nghị:</b> Tránh mua, cân nhắc bán\n"
    elif likely_bot:
        msg += "   🤖 Bot/thuật toán giao dịch đang hoạt động\n"
        msg += "   Market maker hoặc hệ thống tự động\n"
        if bot_score >= 75:
            msg += "   ⚠️ Hoạt động bot rất mạnh\n"
        msg += "   💡 Kỳ vọng spread chặt và khớp lệnh nhanh\n"
    else:
        msg += "   👤 Mẫu giao dịch tự nhiên/con người\n"
        msg += "   Hoạt động tự động thấp\n"
        msg += "   ✅ Điều kiện thị trường bình thường\n"
    
    return msg
