"""
Vercel Index Endpoint - Health Check
"""

from http.server import BaseHTTPRequestHandler
import json
from datetime import datetime


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Health check endpoint"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        response = {
            'status': 'online',
            'service': 'RSI + MFI Trading Bot',
            'version': '1.0.0',
            'timestamp': datetime.now().isoformat(),
            'endpoints': {
                'scan': '/api/scan - Trigger market scan',
                'health': '/ - Health check'
            }
        }
        
        self.wfile.write(json.dumps(response, indent=2).encode())
