import json
import sys
import os

def check_feature(data, path_list, feature_name):
    """Check if a feature exists at the given path."""
    current = data
    for key in path_list:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            print(f"❌ {feature_name}: Missing (key '{key}' not found)")
            return False
            
    # Check if empty (except 0, False, which are valid)
    if not current and not isinstance(current, (int, float, bool)):
        print(f"⚠️ {feature_name}: Present but Empty")
        return False
        
    print(f"✅ {feature_name}: Present")
    return True

def verify_completeness():
    file_path = r"d:\building apps\astro-shiva 2.0\12astro-backend\reference\astro_data\our_data.json"
    
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"JSON Load Error: {e}")
        return

    # Unwrap if wrapped
    if "data" in data and isinstance(data["data"], dict):
        data = data["data"]

    print("=== Astrological Data Completeness Audit ===\n")
    print(f"Top-level keys found: {list(data.keys())}")

    # 1. Shadbala
    check_feature(data, ["balas", "shadbala"], "Shadbala")
    
    # 2. Ashtakavarga
    check_feature(data, ["balas", "ashtakavarga"], "Ashtakavarga")
    
    # 3. Vimshottari Dasha
    check_feature(data, ["dashas", "vimshottari"], "Vimshottari Dasha")
    
    # 4. Divisional Charts (D1-D60)
    print("\n--- Divisional Charts ---")
    d_charts = data.get("divisional_charts", {})
    required_charts = ["D1", "D9", "D10", "D60"]
    for c in required_charts:
        if c in d_charts:
            print(f"✅ {c}: Present")
        else:
            print(f"❌ {c}: Missing")
            
    # 5. Yogas
    check_feature(data, ["yogas"], "Yogas")
    
    # 6. Karakas
    check_feature(data, ["jaimini_karakas"], "Jaimini Karakas")
    
    # 7. Doshas
    check_feature(data, ["doshas"], "Doshas")
    
    # 8. Transits
    check_feature(data, ["current_transits"], "Transits")
    
    # 9. Bhavabala
    check_feature(data, ["bhavabala"], "Bhavabala")
    
    # 10. Astronomical Values
    check_feature(data, ["astronomical_details"], "Astronomical Details")
    
    # 11. Time Calculations
    print("\n--- Time Calculations ---")
    bd = data.get("birth_details", {})
    ad = data.get("astronomical_details", {})
    
    if "lmt_at_birth" in bd or "lmt_at_birth" in ad: 
        print("✅ LMT: Present") 
    else: 
        print("❌ LMT: Missing")
    
    # 12. Sunrise/Sunset
    check_feature(data, ["sunrise_sunset"], "Sunrise/Sunset")
    
    # 13. Yogini Dasha
    check_feature(data, ["yogini_dasha"], "Yogini Dasha")
    
    # 14. Char Dasha
    check_feature(data, ["char_dasha"], "Char Dasha")
    
    # 15. KP Cusps
    check_feature(data, ["kp_cusps"], "KP Cusps")
    
    # 16. Prastharashtakavarga
    check_feature(data, ["balas", "ashtakavarga", "bhav"], "Prastharashtakavarga (Bhav)") 
    
    # 17. Muhurta Elements (Panchanga)
    check_feature(data, ["panchang"], "Muhurta/Panchanga")
    
    # 18. Favorable Points
    check_feature(data, ["favorable_points"], "Favorable Points")

if __name__ == "__main__":
    verify_completeness()
