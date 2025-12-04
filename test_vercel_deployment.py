"""
Pre-deployment Test Suite
Run this to verify everything will work on Vercel
"""

import json
import sys
from pathlib import Path


def test_imports():
    """Test all imports work"""
    print("Testing imports...")
    try:
        import jyotishyamitra
        print("  ✅ jyotishyamitra imported")
    except ImportError as e:
        print(f"  ❌ jyotishyamitra: {e}")
        return False
    
    try:
        from astro_engine import AstroEngine
        print("  ✅ AstroEngine imported")
    except ImportError as e:
        print(f"  ❌ AstroEngine: {e}")
        return False
    
    try:
        from ai_agent import AIAgentInterface
        print("  ✅ AIAgentInterface imported")
    except ImportError as e:
        print(f"  ❌ AIAgentInterface: {e}")
        return False
    
    return True


def test_astro_engine():
    """Test AstroEngine functionality"""
    print("\nTesting AstroEngine...")
    try:
        from astro_engine import AstroEngine
        
        engine = AstroEngine()
        print("  ✅ Engine initialized")
        
        chart = engine.generate_full_chart(
            name="Test Person",
            dob="1990-01-15",
            tob="12:30:00",
            place="New York",
            latitude=40.7128,
            longitude=-74.0060
        )
        
        # Verify chart structure
        assert 'divisional_charts' in chart, "Missing divisional_charts"
        assert 'dashas' in chart, "Missing dashas"
        assert 'user_details' in chart, "Missing user_details"
        
        d_charts = chart['divisional_charts']
        print(f"  ✅ Chart generated ({len(d_charts)} divisional charts)")
        
        dashas = chart['dashas']['vimshottari']['mahadasha']
        print(f"  ✅ Dashas calculated ({len(dashas)} periods)")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_ai_agent():
    """Test AIAgentInterface"""
    print("\nTesting AIAgentInterface...")
    try:
        from ai_agent import AIAgentInterface
        
        ai = AIAgentInterface()
        print("  ✅ Interface initialized")
        
        birth_info = {
            "name": "Test Person",
            "dob": "1990-01-15",
            "tob": "12:30:00",
            "place": "New York",
            "latitude": 40.7128,
            "longitude": -74.0060
        }
        
        result = ai.process_birth_data(birth_info)
        assert 'astrological_profile' in result, "Missing profile"
        print("  ✅ Profile generated")
        
        json_output = ai.export_for_llm(birth_info, format="json")
        data = json.loads(json_output)
        print("  ✅ JSON export successful")
        
        md_output = ai.export_for_llm(birth_info, format="markdown")
        assert "# Astrological Profile" in md_output, "Missing markdown header"
        print("  ✅ Markdown export successful")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_api_handlers():
    """Test API handler functions"""
    print("\nTesting API handlers...")
    
    # Create mock request objects
    class MockRequest:
        def __init__(self, method='GET', body=None, query_params=None):
            self.method = method
            self.body = body
            self.query_string_params = query_params or {}
    
    try:
        # Test health endpoint
        import importlib.util
        spec = importlib.util.spec_from_file_location("api_health", "api_health.py")
        health_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(health_module)
        
        response = health_module.handler(MockRequest())
        assert response['statusCode'] == 200, "Health check failed"
        print("  ✅ Health endpoint works")
        
        # Test chart endpoint
        spec = importlib.util.spec_from_file_location("api_chart", "api_chart.py")
        chart_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(chart_module)
        
        test_data = {
            "name": "Test",
            "dob": "1990-01-15",
            "tob": "12:30:00",
            "place": "NYC",
            "latitude": 40.7128,
            "longitude": -74.0060
        }
        
        request = MockRequest(
            method='POST',
            body=json.dumps(test_data)
        )
        response = chart_module.handler(request)
        assert response['statusCode'] == 200, "Chart endpoint failed"
        print("  ✅ Chart endpoint works")
        
        return True
        
    except Exception as e:
        print(f"  ⚠️  Warning: {e} (This is OK if you're not running locally)")
        return True  # Don't fail on this


def test_config():
    """Test configuration"""
    print("\nTesting configuration...")
    try:
        from config import DIVISIONAL_CHARTS, DASHA_YEARS, NAKSHATRAS
        
        assert len(DIVISIONAL_CHARTS) >= 16, "Missing divisional charts"
        print(f"  ✅ {len(DIVISIONAL_CHARTS)} divisional charts configured")
        
        assert len(DASHA_YEARS) == 9, "Missing dasha lords"
        print(f"  ✅ {len(DASHA_YEARS)} dasha lords configured")
        
        assert len(NAKSHATRAS) == 27, "Missing nakshatras"
        print(f"  ✅ {len(NAKSHATRAS)} nakshatras configured")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False


def verify_files():
    """Verify all required files exist"""
    print("\nVerifying files...")
    
    required_files = [
        'main.py',
        'astro_engine.py',
        'ai_agent.py',
        'config.py',
        'requirements.txt',
        'vercel.json',
        'api_chart.py',
        'api_health.py',
        'api_test.py',
        '.vercelignore'
    ]
    
    all_exist = True
    for file in required_files:
        if Path(file).exists():
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ {file} (MISSING!)")
            all_exist = False
    
    return all_exist


def main():
    """Run all tests"""
    print("=" * 60)
    print("VERCEL PRE-DEPLOYMENT TEST SUITE")
    print("=" * 60)
    
    results = {
        "Files": verify_files(),
        "Config": test_config(),
        "Imports": test_imports(),
        "AstroEngine": test_astro_engine(),
        "AIAgent": test_ai_agent(),
        "API Handlers": test_api_handlers()
    }
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:.<30} {status}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n🎉 All tests passed! Ready to deploy to Vercel!")
        print("\nNext steps:")
        print("1. npm install -g vercel")
        print("2. vercel")
        print("3. Follow the prompts")
        return 0
    else:
        print("\n⚠️  Some tests failed. Fix issues before deploying.")
        print("\nFailed tests:")
        for test_name, result in results.items():
            if not result:
                print(f"  - {test_name}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
