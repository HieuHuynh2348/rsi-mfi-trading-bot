"""
WebApp API Handler
Provides simple HTTP endpoints for WebApp to communicate with bot
Uses in-memory storage for request/response handling
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import threading
import time
import uuid
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

# In-memory storage for analysis requests and results
# {request_id: {'symbol': str, 'timeframe': str, 'status': 'pending'|'completed', 'result': dict, 'timestamp': datetime}}
analysis_requests = {}
analysis_results = {}

# Cleanup old requests every 5 minutes
CLEANUP_INTERVAL = 300  # 5 minutes
MAX_AGE = 600  # 10 minutes

def cleanup_old_requests():
    """Remove old requests to prevent memory leak"""
    while True:
        time.sleep(CLEANUP_INTERVAL)
        current_time = datetime.now()
        
        # Remove requests older than MAX_AGE
        expired_ids = [
            req_id for req_id, data in analysis_requests.items()
            if (current_time - data['timestamp']).total_seconds() > MAX_AGE
        ]
        
        for req_id in expired_ids:
            del analysis_requests[req_id]
            if req_id in analysis_results:
                del analysis_results[req_id]
        
        if expired_ids:
            print(f"🧹 Cleaned up {len(expired_ids)} old requests")

# Start cleanup thread
cleanup_thread = threading.Thread(target=cleanup_old_requests, daemon=True)
cleanup_thread.start()


@app.route('/')
def index():
    """Health check"""
    return jsonify({
        'status': 'online',
        'service': 'WebApp API',
        'active_requests': len(analysis_requests),
        'active_results': len(analysis_results)
    })


@app.route('/api/request-analysis', methods=['POST'])
def request_analysis():
    """
    Create new analysis request
    WebApp calls this to request AI analysis
    Returns request_id to poll for results
    """
    try:
        data = request.get_json()
        symbol = data.get('symbol', 'BTCUSDT')
        timeframe = data.get('timeframe', '1h')
        user_id = data.get('user_id')
        
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        
        # Store request
        analysis_requests[request_id] = {
            'symbol': symbol,
            'timeframe': timeframe,
            'user_id': user_id,
            'status': 'pending',
            'timestamp': datetime.now()
        }
        
        print(f"📝 New analysis request: {request_id} - {symbol} @ {timeframe}")
        
        return jsonify({
            'success': True,
            'request_id': request_id,
            'symbol': symbol,
            'timeframe': timeframe,
            'message': 'Analysis request created. Bot will process shortly.'
        })
        
    except Exception as e:
        print(f"❌ Error creating request: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/get-result/<request_id>', methods=['GET'])
def get_result(request_id):
    """
    Poll for analysis result
    WebApp calls this repeatedly until result is ready
    """
    try:
        # Check if request exists
        if request_id not in analysis_requests:
            return jsonify({
                'success': False,
                'status': 'not_found',
                'error': 'Request ID not found or expired'
            }), 404
        
        # Check if result is ready
        if request_id in analysis_results:
            result = analysis_results[request_id]
            
            # Mark request as completed
            analysis_requests[request_id]['status'] = 'completed'
            
            return jsonify({
                'success': True,
                'status': 'completed',
                'analysis': result['analysis'],
                'symbol': result['symbol'],
                'timeframe': result['timeframe']
            })
        else:
            # Still pending
            request_data = analysis_requests[request_id]
            return jsonify({
                'success': True,
                'status': 'pending',
                'symbol': request_data['symbol'],
                'timeframe': request_data['timeframe'],
                'message': 'Analysis in progress...'
            })
            
    except Exception as e:
        print(f"❌ Error getting result: {e}")
        return jsonify({
            'success': False,
            'status': 'error',
            'error': str(e)
        }), 500


@app.route('/api/submit-result', methods=['POST'])
def submit_result():
    """
    Bot calls this to submit analysis result
    Internal endpoint - called by telegram_commands.py
    """
    try:
        data = request.get_json()
        request_id = data.get('request_id')
        analysis = data.get('analysis')
        symbol = data.get('symbol')
        timeframe = data.get('timeframe')
        
        if not request_id or not analysis:
            return jsonify({
                'success': False,
                'error': 'Missing request_id or analysis'
            }), 400
        
        # Store result
        analysis_results[request_id] = {
            'analysis': analysis,
            'symbol': symbol,
            'timeframe': timeframe,
            'timestamp': datetime.now()
        }
        
        print(f"✅ Analysis result submitted: {request_id} - {symbol}")
        
        return jsonify({
            'success': True,
            'message': 'Result stored successfully'
        })
        
    except Exception as e:
        print(f"❌ Error submitting result: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/get-pending-requests', methods=['GET'])
def get_pending_requests():
    """
    Get list of pending analysis requests
    Bot calls this to check for new work
    """
    try:
        pending = [
            {
                'request_id': req_id,
                'symbol': data['symbol'],
                'timeframe': data['timeframe'],
                'user_id': data.get('user_id'),
                'timestamp': data['timestamp'].isoformat()
            }
            for req_id, data in analysis_requests.items()
            if data['status'] == 'pending' and req_id not in analysis_results
        ]
        
        return jsonify({
            'success': True,
            'pending_requests': pending,
            'count': len(pending)
        })
        
    except Exception as e:
        print(f"❌ Error getting pending requests: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


if __name__ == '__main__':
    import os
    port = int(os.getenv('PORT', 8080))
    print(f"🚀 Starting WebApp API on port {port}...")
    app.run(host='0.0.0.0', port=port, debug=False)
