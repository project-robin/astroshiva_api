"""
Vercel Serverless Function - Test Calculation
Endpoint: /api/api_test
"""

import json
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from astro_engine import AstroEngine


async def handler(request):
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
                    'sample_data': {
                        'name': chart.get('user_details', {}).get('name'),
                        'ascendant': chart.get('divisional_charts', {}).get('D1', {}).get('ascendant')
                    }
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
                'error': str(e),
                'type': type(e).__name__
            }),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            }
        }
