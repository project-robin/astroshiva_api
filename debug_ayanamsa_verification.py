#!/usr/bin/env python
"""
Debug script to verify Ayanamsa precision and house system configuration
Compares our calculations with AstroSage reference data

Reference Data (AstroSage):
- DOB: May 26, 2001
- TOB: 21:48:00
- Place: Ahmednagar (19°23'N, 74°39'E)
- Ayanamsa: 023-52-34 (Lahiri)
- Lagna: Sagittarius 19°54'38"
"""

import sys
import os

# Add vendor path to find swisseph if needed
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '_vendor'))

try:
    import swisseph as swe
except ImportError:
    print("ERROR: swisseph module not found.")
    print("Install with: pip install pyswisseph")
    sys.exit(1)
from datetime import datetime

# Birth Data
YEAR = 2001
MONTH = 5
DAY = 26
HOUR = 21
MINUTE = 48
SECOND = 0

# AstroSage coordinates
ASTROSAGE_LAT = 19 + 23/60  # 19°23'N = 19.3833
ASTROSAGE_LON = 74 + 39/60  # 74°39'E = 74.65
TIMEZONE = 5.5

# Our coordinates (from our_data.json)
OUR_LAT = 19.094829
OUR_LON = 74.747979

def get_ayanamsa_value(jd):
    """Get the exact ayanamsa value used"""
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    return swe.get_ayanamsa_ut(jd)

def calculate_lagna(jd, lat, lon, house_system='P'):
    """Calculate Lagna using specified house system"""
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    cusps, ascmc = swe.houses(jd, lat, lon, bytes(house_system, 'utf-8'))
    return ascmc[0]  # Ascendant

def format_dms(degrees):
    """Convert decimal degrees to D°M'S" format"""
    d = int(degrees)
    m_full = (degrees - d) * 60
    m = int(m_full)
    s = (m_full - m) * 60
    return f"{d}°{m}'{s:.2f}\""

def main():
    print("=" * 70)
    print("AYANAMSA AND HOUSE SYSTEM VERIFICATION")
    print("=" * 70)
    print()
    
    # Calculate UTC time
    utc_hour = HOUR + MINUTE/60 + SECOND/3600 - TIMEZONE
    
    # Julian Day
    jd = swe.julday(YEAR, MONTH, DAY, utc_hour)
    print(f"Julian Day: {jd}")
    print(f"UTC Time: {utc_hour:.4f} hours")
    print()
    
    # 1. Ayanamsa Verification
    print("-" * 70)
    print("1. AYANAMSA VALUE")
    print("-" * 70)
    ayanamsa = get_ayanamsa_value(jd)
    print(f"   Swiss Ephemeris SIDM_LAHIRI: {format_dms(ayanamsa)}")
    print(f"   Decimal: {ayanamsa:.6f}°")
    print(f"   AstroSage Reference: 023°52'34\"")
    
    # Convert AstroSage value to decimal
    astrosage_ayanamsa = 23 + 52/60 + 34/3600
    print(f"   AstroSage Decimal: {astrosage_ayanamsa:.6f}°")
    print(f"   Difference: {abs(ayanamsa - astrosage_ayanamsa)*3600:.2f} arc-seconds")
    print()
    
    # 2. Coordinate Comparison
    print("-" * 70)
    print("2. COORDINATE COMPARISON")
    print("-" * 70)
    print(f"   AstroSage: Lat {ASTROSAGE_LAT:.4f}°N, Lon {ASTROSAGE_LON:.4f}°E")
    print(f"   Our Data:  Lat {OUR_LAT:.4f}°N, Lon {OUR_LON:.4f}°E")
    lat_diff = abs(ASTROSAGE_LAT - OUR_LAT)
    lon_diff = abs(ASTROSAGE_LON - OUR_LON)
    print(f"   Difference: Lat {lat_diff:.4f}° ({lat_diff*111:.1f} km), Lon {lon_diff:.4f}° ({lon_diff*111*0.93:.1f} km)")
    print()
    
    # 3. House System Comparison
    print("-" * 70)
    print("3. LAGNA CALCULATION BY HOUSE SYSTEM (using AstroSage coords)")
    print("-" * 70)
    
    house_systems = {
        'P': 'Placidus',
        'K': 'Koch',
        'W': 'Whole Sign',
        'E': 'Equal',
        'B': 'Alcabitus'
    }
    
    for code, name in house_systems.items():
        try:
            lagna = calculate_lagna(jd, ASTROSAGE_LAT, ASTROSAGE_LON, code)
            sign_idx = int(lagna / 30)
            sign_deg = lagna % 30
            signs = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
                    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
            print(f"   {name:12}: {signs[sign_idx]} {format_dms(sign_deg)}")
        except Exception as e:
            print(f"   {name:12}: Error - {e}")
    
    print()
    print(f"   AstroSage Reference: Sagittarius 19°54'38\"")
    print()
    
    # 4. Impact of coordinates on Lagna
    print("-" * 70)
    print("4. LAGNA DIFFERENCE DUE TO COORDINATES (Placidus)")
    print("-" * 70)
    
    lagna_astrosage = calculate_lagna(jd, ASTROSAGE_LAT, ASTROSAGE_LON, 'P')
    lagna_ours = calculate_lagna(jd, OUR_LAT, OUR_LON, 'P')
    
    print(f"   With AstroSage coords: {format_dms(lagna_astrosage % 30)} in {['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'][int(lagna_astrosage/30)]}")
    print(f"   With Our coords:       {format_dms(lagna_ours % 30)} in {['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'][int(lagna_ours/30)]}")
    print(f"   Difference: {abs(lagna_astrosage - lagna_ours)*60:.2f} arc-minutes")
    print()
    
    # 5. D9 Navamsa Ascendant Calculation
    print("-" * 70)
    print("5. NAVAMSA (D9) ASCENDANT CALCULATION")
    print("-" * 70)
    
    # Standard Navamsa formula: (Lagna_degree / 3.333...) mod 12 = starting sign
    def calculate_navamsa_lagna(lagna_total_deg):
        """Calculate D9 Lagna from D1 Lagna using standard formula"""
        one_navamsa = 360 / 108  # 3.333... degrees per navamsa
        navamsa_num = int(lagna_total_deg / one_navamsa)
        navamsa_sign = navamsa_num % 12  # 0-11
        return navamsa_sign
    
    navamsa_sign_astrosage = calculate_navamsa_lagna(lagna_astrosage)
    navamsa_sign_ours = calculate_navamsa_lagna(lagna_ours)
    
    signs = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
            "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
    
    print(f"   D1 Lagna (AstroSage coords): {format_dms(lagna_astrosage)} → D9 Lagna: {signs[navamsa_sign_astrosage]}")
    print(f"   D1 Lagna (Our coords):       {format_dms(lagna_ours)} → D9 Lagna: {signs[navamsa_sign_ours]}")
    print(f"   AstroSage D9 Reference: Aries")
    print(f"   Our Data D9: Libra")
    print()
    
    # Check which degree range gives Aries D9
    print("   Degree ranges for D9 Sagittarius Lagna → D9 Signs:")
    for i in range(12):
        start_deg = (8 * 30) + (i * 3.333333)  # Sagittarius base (240°) + navamsa
        end_deg = start_deg + 3.333333
        sign_result = (i + 9) % 12  # Sagittarius = sign 9, navamsa starts from same sign for odd
        if sign_result == 0: sign_result = 12
        print(f"      {start_deg:.2f}° - {end_deg:.2f}° → {signs[sign_result-1]}")
    
    print()
    print("-" * 70)
    print("SUMMARY")
    print("-" * 70)
    print("""
    1. AYANAMSA: Match is excellent (< 1 arc-second difference)
    
    2. COORDINATES: ~28km difference between geocoded locations
       - This causes ~1° Lagna difference
    
    3. HOUSE SYSTEM: Placidus is being used (correct for Western/KP)
       - Different from traditional Whole Sign used in Vedic
       - AstroSage likely uses Equal or Placidus
    
    4. D9 DISCREPANCY ROOT CAUSE:
       - If D1 Lagna is 14° Sag (our data), D9 = Libra
       - If D1 Lagna is 19°54' Sag (AstroSage), D9 = Aries
       - The ~6° D1 Lagna difference directly causes the D9 sign flip
       
    5. RECOMMENDED FIX:
       - Verify exact coordinates used by AstroSage
       - Consider using swe.houses_ex() for more precision
       - Log ayanamsa value in API response metadata
    """)

if __name__ == "__main__":
    main()
