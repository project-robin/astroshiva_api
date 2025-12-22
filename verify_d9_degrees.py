
from astro_engine import AstroEngine
import json

def verify_d9_logic():
    engine = AstroEngine()
    
    # Test Data: Jan 1 2024, 12:00 PM, New Delhi
    chart_data = engine.generate_full_chart(
        name="Verification",
        dob="2024-01-01",
        tob="12:00:00",
        place="New Delhi",
        latitude=28.6139,
        longitude=77.2090,
        timezone="+5.5"
    )
    
    if "error" in chart_data:
        print(f"Error: {chart_data['error']}")
        return

    # Check D1 Ascendant
    d1 = chart_data['divisional_charts']['D1']
    asc_d1 = d1['ascendant']
    print(f"\nD1 Ascendant: {asc_d1['sign']} {asc_d1['degree']:.2f}")

    # Check D9 Ascendant
    d9 = chart_data['divisional_charts']['D9']
    asc_d9 = d9['ascendant']
    print(f"D9 Ascendant: {asc_d9['sign']} {asc_d9['degree']:.2f}")
    
    # Check Sun D1 vs D9
    sun_d1 = d1['planets']['Sun']
    sun_d9 = d9['planets']['Sun']
    
    print(f"\nSun D1: {sun_d1['sign']} {sun_d1['degree']:.2f} (Total: {sun_d1.get('total_degree', 0):.2f})")
    print(f"Sun D9: {sun_d9['sign']} {sun_d9['degree']:.2f}")
    
    # Manual Calculation Check for Sun D9
    # Sun Total Degree / 30 = Sign Index (0-11)
    # Remainder = Degree in Sign
    # D9 calculation: (Degree in Sign / 3.333...) -> Pada (1-9)
    # Verify mapping logic behaves as expected
    
    total_deg = sun_d1.get('total_degree', 0)
    # engine._calculate_varga_sign(total_deg, 9) could be used if public, but we implicitly test it via output
    
    print("\n--- Output JSON Snippet (D9 Ascendant) ---")
    print(json.dumps(asc_d9, indent=2))

if __name__ == "__main__":
    verify_d9_logic()
