"""
Unified Server for Railway
Serves both Telegram bot and static webapp files
"""

from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
import os
import sys
import threading
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__, static_folder='webapp')
CORS(app)

# Bot thread reference
bot_thread = None

@app.route('/')
def index():
    """Health check"""
    return jsonify({
        'status': 'online',
        'service': 'RSI + MFI Trading Bot',
        'bot': 'running' if bot_thread and bot_thread.is_alive() else 'starting',
        'webapp': 'available at /webapp/chart.html'
    })

@app.route('/webapp/<path:filename>')
def serve_webapp(filename):
    """Serve webapp files"""
    try:
        file_path = os.path.join('webapp', filename)
        logger.info(f"📂 Serving file: {filename} from {file_path}")
        
        if not os.path.exists(file_path):
            logger.error(f"❌ File not found: {file_path}")
            return jsonify({'error': f'File not found: {filename}'}), 404
            
        return send_from_directory('webapp', filename)
    except Exception as e:
        logger.error(f"❌ Error serving {filename}: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/chart.html')
def serve_chart_direct():
    """Direct access to chart - redirects to /webapp/chart.html"""
    logger.info("📊 Direct chart access - serving from webapp/")
    try:
        return send_from_directory('webapp', 'chart.html')
    except Exception as e:
        logger.error(f"❌ Error serving chart.html: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/ai-analysis', methods=['POST'])
def trigger_ai_analysis():
    """
    API endpoint to trigger AI analysis from WebApp
    Receives: {user_id, symbol, timeframe}
    """
    from flask import request
    
    try:
        data = request.json
        user_id = data.get('user_id')
        symbol = data.get('symbol')
        timeframe = data.get('timeframe', '1h')
        
        logger.info(f"🤖 AI Analysis API called: user={user_id}, symbol={symbol}, tf={timeframe}")
        
        if not user_id or not symbol:
            return jsonify({'success': False, 'error': 'Missing user_id or symbol'}), 400
        
        # Get TradingBot instance
        from main import TradingBot
        if hasattr(TradingBot, '_instance') and TradingBot._instance:
            bot = TradingBot._instance
            
            # Send processing message first
            try:
                bot.telegram.bot.send_message(
                    chat_id=user_id,
                    text=f"🤖 <b>GEMINI AI ĐANG PHÂN TÍCH</b>\n\n"
                         f"💎 <b>Symbol:</b> {symbol}\n"
                         f"📊 Đang thu thập dữ liệu từ tất cả indicators...\n"
                         f"🧠 Đang gọi Gemini 2.0 Flash API...\n"
                         f"🔮 Đang phân tích và dự đoán...\n\n"
                         f"⏳ <b>Vui lòng chờ 10-20 giây...</b>",
                    parse_mode='HTML'
                )
            except Exception as e:
                logger.warning(f"⚠️ Could not send processing message: {e}")
            
            # Perform AI analysis
            try:
                result = bot.command_handler.gemini_analyzer.analyze(
                    symbol=symbol,
                    pump_data=None,
                    trading_style='swing',
                    use_cache=True
                )
                
                if result:
                    # Format response using gemini_analyzer's format_response method
                    msg1, msg2, msg3 = bot.command_handler.gemini_analyzer.format_response(result)
                    
                    # Send all 3 messages
                    for msg in [msg1, msg2, msg3]:
                        if msg:  # Only send non-empty messages
                            bot.telegram.bot.send_message(
                                chat_id=user_id,
                                text=msg,
                                parse_mode='HTML'
                            )
                    
                    logger.info(f"✅ AI Analysis sent to user {user_id} for {symbol}")
                    return jsonify({'success': True, 'message': 'Analysis sent to Telegram'})
                else:
                    # Analysis failed - send user-friendly error
                    error_msg = (
                        f"❌ <b>Không thể phân tích {symbol}</b>\n\n"
                        f"⚠️ <b>Lỗi:</b> Gemini AI không trả về kết quả hợp lệ.\n"
                        f"Có thể do:\n"
                        f"• Response quá dài\n"
                        f"• JSON format không đúng\n"
                        f"• API tạm thời quá tải\n\n"
                        f"💡 <b>Giải pháp:</b> Vui lòng thử lại sau vài giây hoặc dùng nút <b>🤖 AI Phân Tích</b> trong tin nhắn phân tích chính."
                    )
                    try:
                        bot.telegram.bot.send_message(
                            chat_id=user_id,
                            text=error_msg,
                            parse_mode='HTML'
                        )
                    except:
                        pass
                    return jsonify({'success': False, 'error': 'Analysis parsing failed'}), 500
                    
            except Exception as e:
                logger.error(f"❌ Error performing AI analysis: {e}", exc_info=True)
                # Send error message to user
                try:
                    bot.telegram.bot.send_message(
                        chat_id=user_id,
                        text=f"❌ <b>Lỗi khi phân tích {symbol}</b>\n\n{str(e)}",
                        parse_mode='HTML'
                    )
                except:
                    pass
                return jsonify({'success': False, 'error': str(e)}), 500
        else:
            logger.error("❌ TradingBot instance not found")
            return jsonify({'success': False, 'error': 'Bot not ready'}), 503
            
    except Exception as e:
        logger.error(f"❌ API error: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

def start_telegram_bot():
    """Run Telegram bot in background thread"""
    try:
        logger.info("🤖 Starting Telegram bot...")
        import main
        main.main()
    except Exception as e:
        logger.error(f"❌ Bot error: {e}", exc_info=True)

if __name__ == '__main__':
    # Start bot in background thread
    bot_thread = threading.Thread(target=start_telegram_bot, daemon=True, name='TelegramBot')
    bot_thread.start()
    logger.info("✅ Bot thread started")
    
    # Start Flask server
    port = int(os.getenv('PORT', 8080))
    logger.info(f"🌐 Starting Flask server on port {port}...")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False,
        threaded=True
    )
