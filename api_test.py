"""
Vercel Serverless Function - Test Calculation
Deploy to: api/test.py
"""

import json
from astro_engine import AstroEngine


def handler(request):
    """Test calculation endpoint"""
    try:
        engine = AstroEngine()
        chart = engine.generate_full_chart(
            name="Test Subject",
            dob="1990-01-15",
            tob="12:30:00",
            place="New York",
            latitude=40.7128,
            longitude=-74.0060
        )
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'status': 'success',
                'message': 'Test calculation successful! ✅',
                'details': {
                    'divisional_charts': len(chart.get('divisional_charts', {})),
                    'dasha_periods': len(chart.get('dashas', {}).get('vimshottari', {}).get('mahadasha', [])),
                    'test_data': chart
                }
            }, default=str),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            }
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'status': 'error',
                'error': str(e)
            }),
            'headers': {'Content-Type': 'application/json'}
        }
