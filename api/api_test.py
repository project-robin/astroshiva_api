"""
Vercel Serverless Function - Test Calculation
Endpoint: /api/api_test
"""

import json
import sys
from pathlib import Path
from http.server import BaseHTTPRequestHandler

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from astro_engine import AstroEngine


class handler(BaseHTTPRequestHandler):
    """Test calculation endpoint using Vercel-compatible handler"""
    
    def do_GET(self):
        """Handle GET requests"""
        try:
            # Initialize engine and run test calculation
            engine = AstroEngine()
            chart = engine.generate_full_chart(
                name="Test Subject",
                dob="1990-01-15",
                tob="12:30:00",
                place="New York",
                latitude=40.7128,
                longitude=-74.0060
            )
            
            # Prepare success response
            response_data = {
                'status': 'success',
                'message': 'Test calculation successful! ✅',
                'details': {
                    'divisional_charts': len(chart.get('divisional_charts', {})),
                    'dasha_periods': len(chart.get('dashas', {}).get('vimshottari', {}).get('mahadasha', [])),
                    'sample_data': {
                        'name': chart.get('user_details', {}).get('name'),
                        'ascendant': chart.get('divisional_charts', {}).get('D1', {}).get('ascendant')
                    }
                }
            }
            
            # Send response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response_data, default=str).encode())
            
        except Exception as e:
            # Send error response
            error_data = {
                'status': 'error',
                'error': str(e),
                'type': type(e).__name__
            }
            
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(error_data).encode())
    
    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
