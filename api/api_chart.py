"""
Vercel Serverless Function - Astrology Chart Generation
Endpoint: /api/api_chart
"""

import json
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from astro_engine import AstroEngine


async def handler(request):
    """Main handler for chart generation requests"""
    
    if request.method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, GET',
                'Access-Control-Allow-Headers': 'Content-Type'
            }
        }
    
    try:
        # Parse request body
        if isinstance(request.body, bytes):
            body = request.body.decode()
        else:
            body = request.body or '{}'
        
        data = json.loads(body) if body else {}
        
        # Get query params if POST data not provided
        if not data and hasattr(request, 'query'):
            data = request.query
        
        # Validate required fields
        required = ['name', 'dob', 'tob', 'place']
        missing = [f for f in required if f not in data]
        
        if missing:
            return {
                'statusCode': 400,
                'body': json.dumps({
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
                }),
                'headers': {'Content-Type': 'application/json'}
            }
        
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
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'status': 'success',
                'data': chart
            }, default=str),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            }
        }
        
    except json.JSONDecodeError as e:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': f'Invalid JSON: {str(e)}'}),
            'headers': {'Content-Type': 'application/json'}
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e),
                'type': type(e).__name__
            }),
            'headers': {'Content-Type': 'application/json'}
        }

