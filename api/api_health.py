"""
Vercel Serverless Function - Health Check
Endpoint: /api/api_health
"""

import json
from http.server import BaseHTTPRequestHandler


class handler(BaseHTTPRequestHandler):
    """Health check endpoint using Vercel-compatible handler"""
    
    def do_GET(self):
        """Handle GET requests"""
        # Set response status
        self.send_response(200)
        
        # Set headers
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        # Prepare response data
        response_data = {
            'status': 'healthy',
            'service': 'Vedic Astrology Engine',
            'version': '1.0.0',
            'features': [
                'All 16 Divisional Charts (D1-D60)',
                'Vimshottari Dasha Calculations',
                'Ashtakavarga & Shadbala',
                'Nakshatras & Panchang Data',
                'JSON Output for AI Agents'
            ]
        }
        
        # Send response
        self.wfile.write(json.dumps(response_data).encode())
    
    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
