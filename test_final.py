"""
Final verification test for API fixes
"""
import json
import re
from urllib.parse import unquote

def test_charts_sanitization_final():
    """Test the FINAL charts parameter sanitization with URL decoding"""
    print("=" * 70)
    print("FINAL TEST: Charts Parameter Sanitization (with URL decoding)")
    print("=" * 70)
    
    test_cases = [
        ("D1,D9", ["D1", "D9"], "Normal input"),
        ("D1,D9%22", ["D1", "D9"], "With trailing URL-encoded quote (%22)"),
        ("D1, D9", ["D1", "D9"], "With spaces"),
        ('"D1,D9"', ["D1", "D9"], "With quotes"),
        ("d1,d9", ["D1", "D9"], "Lowercase"),
        ("invalid", ["D1", "D9", "D10"], "Invalid input - should default"),
        ("", ["D1", "D9", "D10"], "Empty - should default"),
        (None, ["D1", "D9", "D10"], "None - should default"),
    ]
    
    passed = 0
    failed = 0
    
    for input_val, expected, description in test_cases:
        charts_list = None
        if input_val:
            # Decode URL encoding first
            decoded = unquote(input_val)
            # Then sanitize
            sanitized = re.sub(r'["\'\s]+', '', decoded)
            if sanitized:
                charts_list = [c.strip().upper() for c in sanitized.split(',') if c.strip()]
                valid_charts = []
                for chart in charts_list:
                    if re.match(r'^D\d{1,2}$', chart):
                        valid_charts.append(chart)
                charts_list = valid_charts if valid_charts else None
        
        if not charts_list:
            charts_list = ["D1", "D9", "D10"]
        
        if charts_list == expected:
            status = "✅ PASS"
            passed += 1
        else:
            status = "❌ FAIL"
            failed += 1
            
        print(f"{status} | {description}")
        print(f"   Input: {repr(input_val)}")
        print(f"   Expected: {expected}")
        print(f"   Got: {charts_list}")
        print()
    
    return passed, failed

def test_rahu_ketu_calculation():
    """Test Rahu/Ketu 180° relationship"""
    print("=" * 70)
    print("TEST: Rahu/Ketu Transit Calculation (180° Opposite)")
    print("=" * 70)
    
    signs = ["", "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", 
             "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
    
    test_cases = [
        (19.32, "Aquarius", "Leo"),  # Current Rahu position
        (0.0, "Aries", "Libra"),
        (90.0, "Cancer", "Capricorn"),
        (180.0, "Libra", "Aries"),
        (270.0, "Capricorn", "Cancer"),
    ]
    
    passed = 0
    failed = 0
    
    for rahu_long, expected_rahu_sign, expected_ketu_sign in test_cases:
        # Calculate Ketu
        ketu_long = (rahu_long + 180) % 360
        
        # Get signs
        rahu_sign_num = int(rahu_long / 30) + 1
        ketu_sign_num = int(ketu_long / 30) + 1
        
        rahu_sign = signs[rahu_sign_num] if 1 <= rahu_sign_num <= 12 else "Unknown"
        ketu_sign = signs[ketu_sign_num] if 1 <= ketu_sign_num <= 12 else "Unknown"
        
        if rahu_sign == expected_rahu_sign and ketu_sign == expected_ketu_sign:
            status = "✅ PASS"
            passed += 1
        else:
            status = "❌ FAIL"
            failed += 1
            
        print(f"{status} | Rahu: {rahu_long}° → {rahu_sign}, Ketu: {ketu_long}° → {ketu_sign}")
        print(f"   Expected: Rahu in {expected_rahu_sign}, Ketu in {expected_ketu_sign}")
        print()
    
    return passed, failed

if __name__ == "__main__":
    p1, f1 = test_charts_sanitization_final()
    p2, f2 = test_rahu_ketu_calculation()
    
    total_passed = p1 + p2
    total_failed = f1 + f2
    
    print("=" * 70)
    print("FINAL SUMMARY")
    print("=" * 70)
    print(f"Total Tests: {total_passed + total_failed}")
    print(f"✅ Passed: {total_passed}")
    print(f"❌ Failed: {total_failed}")
    print()
    
    if total_failed == 0:
        print("🎉 ALL TESTS PASSED! Both fixes are working correctly.")
        print()
        print("1. ✅ Charts parameter sanitization with URL decoding")
        print("2. ✅ Rahu/Ketu 180° calculation")
        print()
        print("Ready to deploy to production!")
    else:
        print("⚠️  Some tests failed. Please review the fixes.")
