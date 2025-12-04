"""
Vercel Serverless Function - Astrology Chart Generation
Deploy to: api/chart.py
"""

import json
from astro_engine import AstroEngine


def handler(request):
    """Main handler for chart generation requests"""
    
    # Handle CORS
    if request.method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, GET',
                'Access-Control-Allow-Headers': 'Content-Type'
            }
        }
    
    # Parse request
    try:
        if request.method == 'POST':
            data = json.loads(request.body) if request.body else {}
        else:
            data = request.query_string_params or {}
        
        # Validate required fields
        required = ['name', 'dob', 'tob', 'place']
        missing = [f for f in required if f not in data]
        if missing:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'Missing required fields',
                    'missing': missing,
                    'required': required
                })
            }
        
        # Generate chart
        engine = AstroEngine()
        chart = engine.generate_full_chart(
            name=data['name'],
            dob=data['dob'],
            tob=data['tob'],
            place=data['place'],
            latitude=float(data.get('latitude', 0)) if data.get('latitude') else None,
            longitude=float(data.get('longitude', 0)) if data.get('longitude') else None
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
        
    except json.JSONDecodeError:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Invalid JSON'}),
            'headers': {'Content-Type': 'application/json'}
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)}),
            'headers': {'Content-Type': 'application/json'}
        }
