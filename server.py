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
