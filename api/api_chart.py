"""
Vercel Serverless Function - Astrology Chart Generation
Endpoint: /api/api_chart
"""

import json
import sys
from pathlib import Path
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from astro_engine import AstroEngine


class handler(BaseHTTPRequestHandler):
    """Chart generation endpoint using Vercel-compatible handler"""
    
    def do_POST(self):
        """Handle POST requests"""
        try:
            # Read and parse request body
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            
            # Parse JSON data
            try:
                data = json.loads(body) if body else {}
            except json.JSONDecodeError as e:
                self._send_error(400, f'Invalid JSON: {str(e)}')
                return
            
            # Validate required fields
            required = ['name', 'dob', 'tob', 'place']
            missing = [f for f in required if f not in data]
            
            if missing:
                self._send_error(400, {
                    'error': 'Missing required fields',
                    'missing': missing,
                    'required': required,
                    'example': {
                        'name': 'John Doe',
                        'dob': '1990-01-15',
                        'tob': '12:30:00',
                        'place': 'New York',
                        'latitude': 40.7128,
                        'longitude': -74.0060
                    }
                })
                return
            
            # Generate chart
            engine = AstroEngine()
            chart = engine.generate_full_chart(
                name=data['name'],
                dob=data['dob'],
                tob=data['tob'],
                place=data['place'],
                latitude=float(data.get('latitude')) if data.get('latitude') else None,
                longitude=float(data.get('longitude')) if data.get('longitude') else None
            )
            
            # Send success response
            response_data = {
                'status': 'success',
                'data': chart
            }
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response_data, default=str).encode())
            
        except Exception as e:
            self._send_error(500, {
                'error': str(e),
                'type': type(e).__name__
            })
    
    def do_GET(self):
        """Handle GET requests with query parameters"""
        try:
            # Parse query string
            from urllib.parse import urlparse
            query = urlparse(self.path).query
            data = {}
            if query:
                params = parse_qs(query)
                # Convert query params (which are lists) to single values
                data = {k: v[0] if len(v) == 1 else v for k, v in params.items()}
            
            # Validate required fields
            required = ['name', 'dob', 'tob', 'place']
            missing = [f for f in required if f not in data]
            
            if missing:
                self._send_error(400, {
                    'error': 'Missing required fields',
                    'missing': missing,
                    'required': required,
                    'note': 'Use POST method for complex requests or provide all required query parameters'
                })
                return
            
            # Generate chart
            engine = AstroEngine()
            chart = engine.generate_full_chart(
                name=data['name'],
                dob=data['dob'],
                tob=data['tob'],
                place=data['place'],
                latitude=float(data.get('latitude')) if data.get('latitude') else None,
                longitude=float(data.get('longitude')) if data.get('longitude') else None
            )
            
            # Send success response
            response_data = {
                'status': 'success',
                'data': chart
            }
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response_data, default=str).encode())
            
        except Exception as e:
            self._send_error(500, {
                'error': str(e),
                'type': type(e).__name__
            })
    
    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def _send_error(self, status_code, error_data):
        """Helper method to send error responses"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        if isinstance(error_data, str):
            error_data = {'error': error_data}
        
        self.wfile.write(json.dumps(error_data).encode())
