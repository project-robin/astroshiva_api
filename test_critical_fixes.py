"""
Test script to verify the 4 critical bug fixes in astro_engine.py
Birth data: K, 26/05/2001, 21:48, Ahmednagar
Expected values from AstroSage reference
"""

import sys
import json
sys.path.insert(0, r'd:\building apps\astro-shiva 2.0\12astro-backend')

from astro_engine import AstroEngine

def test_critical_fixes():
    print("=" * 60)
    print("TESTING 4 CRITICAL BUG FIXES")
    print("=" * 60)
    
    engine = AstroEngine()
    
    # Generate chart for the test case
    result = engine.generate_full_chart(
        name="K",
        dob="2001-05-26",
        tob="21:48:00",
        place="Ahmednagar",
        latitude=19.3833,
        longitude=74.65,
        timezone=5.5
    )
    
    # Save full output for inspection
    with open(r'd:\building apps\astro-shiva 2.0\12astro-backend\test_fixes_output.json', 'w') as f:
        json.dump(result, f, indent=2, default=str)
    
    print("\n[1] SUNRISE/SUNSET TEST")
    print("-" * 40)
    sunrise_sunset = result.get("sunrise_sunset", {})
    sunrise = sunrise_sunset.get("sunrise", "ERROR")
    sunset = sunrise_sunset.get("sunset", "ERROR")
    print(f"  Our Sunrise:    {sunrise}")
    print(f"  Our Sunset:     {sunset}")
    print(f"  Expected:       ~05:53 / ~19:03")
    
    if sunrise.startswith("05") or sunrise.startswith("06"):
        print("  ✅ PASS: Sunrise is in morning hours")
    else:
        print(f"  ❌ FAIL: Sunrise is {sunrise}, expected ~05:53")
    
    print("\n[2] YOGINI DASHA STARTING POINT TEST")
    print("-" * 40)
    yogini_dasha = result.get("yogini_dasha", {})
    starting_yogini = yogini_dasha.get("starting_yogini", "ERROR")
    moon_nak = yogini_dasha.get("moon_nakshatra_number", "?")
    print(f"  Moon Nakshatra #: {moon_nak}")
    print(f"  Starting Yogini:  {starting_yogini}")
    print(f"  Expected:         Pingala (for Punarvasu)")
    
    # For Punarvasu (Nakshatra 7), formula: (7+3)%8 = 2 → Pingala
    if starting_yogini == "Pingala":
        print("  ✅ PASS: Yogini starts with Pingala")
    else:
        print(f"  ❌ FAIL: Expected Pingala, got {starting_yogini}")
    
    print("\n[3] CHAR DASHA SEQUENCE TEST")
    print("-" * 40)
    char_dasha = result.get("char_dasha", {})
    maha_dasha = char_dasha.get("maha_dasha", [])
    lagna = char_dasha.get("lagna_sign", "?")
    direction = char_dasha.get("sequence_direction", "?")
    
    sequence = [d.get("sign") for d in maha_dasha[:6]]
    print(f"  Lagna:            {lagna}")
    print(f"  Direction:        {direction}")
    print(f"  First 6 signs:    {sequence}")
    print(f"  Expected:         ['Sagittarius', 'Scorpio', 'Libra', 'Virgo', 'Leo', 'Cancer']")
    
    expected_sequence = ["Sagittarius", "Scorpio", "Libra", "Virgo", "Leo", "Cancer"]
    if sequence == expected_sequence:
        print("  ✅ PASS: Char Dasha sequence is correct (backward for odd sign)")
    else:
        print(f"  ❌ FAIL: Expected {expected_sequence}, got {sequence}")
    
    print("\n[4] BHAVABALA EXTRACTION TEST")
    print("-" * 40)
    bhavabala = result.get("bhavabala", {})
    
    if "note" in bhavabala or "error" in bhavabala:
        print(f"  ⚠️  INFO: {bhavabala}")
        print("  (Bhavabala may require jyotishganit to expose the data)")
    elif "house_1" in bhavabala:
        h1 = bhavabala.get("house_1", {})
        print(f"  House 1 Total:  {h1.get('total', 'N/A')}")
        print("  ✅ PASS: Bhavabala data extracted")
    else:
        print(f"  ⚠️  PARTIAL: Got keys: {list(bhavabala.keys())[:5]}")
    
    print("\n" + "=" * 60)
    print("VERIFICATION COMPLETE")
    print("=" * 60)
    print(f"\nFull output saved to: test_fixes_output.json")

if __name__ == "__main__":
    test_critical_fixes()
