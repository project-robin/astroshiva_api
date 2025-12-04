"""
Vercel Serverless Function - Health Check
Endpoint: /api/api_health
"""

import json


async def handler(request):
    """Health check endpoint"""
    return {
        'statusCode': 200,
        'body': json.dumps({
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
        }),
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        }
    }
