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
                    use_cache=True,
                    user_id=user_id  # Pass user_id for history
                )
                
                if result:
                    # Format response using gemini_analyzer's format_response method
                    msg1, msg2, msg3 = bot.command_handler.gemini_analyzer.format_response(result)
                    
                    # Helper function to split long messages
                    def split_message(msg, max_len=4000):
                        """Split message if longer than Telegram's limit"""
                        if len(msg) <= max_len:
                            return [msg]
                        
                        parts = []
                        lines = msg.split('\n')
                        current = ""
                        
                        for line in lines:
                            if len(current) + len(line) + 1 > max_len:
                                if current:
                                    parts.append(current.rstrip())
                                    current = ""
                            current += line + '\n'
                        
                        if current:
                            parts.append(current.rstrip())
                        
                        return parts
                    
                    # Send to Telegram with splitting
                    for msg in [msg1, msg2, msg3]:
                        if msg:
                            # Split if too long
                            msg_parts = split_message(msg, max_len=4000)
                            
                            for part in msg_parts:
                                try:
                                    bot.telegram.bot.send_message(
                                        chat_id=user_id,
                                        text=part,
                                        parse_mode='HTML'
                                    )
                                except Exception as send_err:
                                    logger.warning(f"⚠️ Could not send message part: {send_err}")
                    
                    logger.info(f"✅ AI Analysis sent to user {user_id} for {symbol}")
                    
                    # Return formatted result to WebApp
                    return jsonify({
                        'success': True, 
                        'message': 'Analysis sent to Telegram',
                        'analysis': {
                            'symbol': result.get('symbol', symbol),
                            'recommendation': result.get('recommendation', 'N/A'),
                            'confidence': result.get('confidence', 0),
                            'entry_point': result.get('entry_point', 0),
                            'stop_loss': result.get('stop_loss', 0),
                            'take_profit': result.get('take_profit', []),
                            'risk_level': result.get('risk_level', 'N/A'),
                            'reasoning': result.get('reasoning_vietnamese', 'N/A'),
                            'messages': {
                                'summary': msg1,
                                'technical': msg2,
                                'reasoning': msg3
                            }
                        }
                    })
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

@app.route('/api/analysis-history', methods=['GET'])
def get_analysis_history():
    """
    API endpoint to get analysis history
    Query params: user_id (required), symbol (optional), days (optional, default=7)
    """
    from flask import request
    
    try:
        user_id = request.args.get('user_id', type=int)
        symbol = request.args.get('symbol', default=None)
        days = request.args.get('days', default=7, type=int)
        
        logger.info(f"📊 History API called: user={user_id}, symbol={symbol}, days={days}")
        
        if not user_id:
            return jsonify({'success': False, 'error': 'Missing user_id parameter'}), 400
        
        # Get database instance
        from database import get_db
        db = get_db()
        
        if not db:
            return jsonify({'success': False, 'error': 'Database not available'}), 503
        
        # Get history
        if symbol:
            # Get history for specific symbol
            history = db.get_symbol_history(symbol, user_id, days=days)
            stats = db.calculate_accuracy_stats(symbol, user_id, days=days)
        else:
            # Get all history for user
            history = db.get_all_history(user_id, days=days)
            stats = None
        
        logger.info(f"✅ Found {len(history) if history else 0} analyses for user {user_id}")
        
        return jsonify({
            'success': True,
            'user_id': user_id,
            'symbol': symbol,
            'days': days,
            'count': len(history) if history else 0,
            'history': history,
            'stats': stats
        })
            
    except Exception as e:
        logger.error(f"❌ History API error: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/review-analysis', methods=['POST'])
def review_analysis():
    """
    API endpoint for manual review (👍/👎)
    Body: { user_id, analysis_id, review ('good'|'bad'), comment }
    """
    from flask import request
    
    try:
        data = request.json
        user_id = data.get('user_id')
        analysis_id = data.get('analysis_id')
        review = data.get('review')  # 'good' or 'bad'
        comment = data.get('comment', '')
        
        if not all([user_id, analysis_id, review]):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        if review not in ['good', 'bad']:
            return jsonify({'success': False, 'error': 'Invalid review value'}), 400
        
        # Get database
        from database import get_db
        db = get_db()
        
        if not db:
            return jsonify({'success': False, 'error': 'Database not available'}), 503
        
        # Add review
        success = db.add_manual_review(analysis_id, user_id, review, comment)
        
        if success:
            return jsonify({'success': True, 'message': 'Review added successfully'})
        else:
            return jsonify({'success': False, 'error': 'Failed to add review'}), 500
            
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
