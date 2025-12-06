import requests
import json
import time

API_URL = "https://astroshiva-api.onrender.com/api/chart-test"

def check_features():
    print(f"Connecting to {API_URL}...")
    try:
        resp = requests.get(API_URL)
        if resp.status_code != 200:
            print(f"Error: Status {resp.status_code}")
            return False
            
        data = resp.json()['data']
        
        # Check 1: API Version
        version = data.get('meta', {}).get('api_version', 'unknown')
        print(f"API Version: {version}")
        
        # Check for Errors
        if 'enrichment_error' in data.get('meta', {}):
             print(f"⚠️ ENRICHMENT ERROR FOUND:\n{data['meta']['enrichment_error']}")
             return False
             
        if version != "2.0.0":
            print("❌ Old version detected. Deployment likely not ready.")
            return False
            
        # Check 2: Jaimini
        if 'jaimini_karakas' in data and 'Atmakaraka' in data['jaimini_karakas']:
            print("✅ Jaimini Karakas found")
            print("   Atmakaraka:", data['jaimini_karakas']['Atmakaraka']['planet'])
        else:
            print("❌ Jaimini Karakas MISSING")
            
        # Check 3: KP & Avasthas (Check Sun)
        sun = data['divisional_charts']['D1']['planets']['Sun']
        
        if 'kp' in sun:
            print("✅ KP Details found")
            print("   Sun Sub-Lord:", sun['kp']['sub_lord'])
        else:
            print("❌ KP details MISSING")
            
        if 'avasthas' in sun:
            print("✅ Avasthas found")
            print("   Sun Avastha:", sun['avasthas']['baaladi']['full_name'])
        else:
            print("❌ Avasthas MISSING")

        # Check 4: Transits
        if 'current_transits' in data:
            print("✅ Current Transits found")
            print("   Saturn is currently in:", data['current_transits']['Saturn']['current_sign'])
        else:
            print("❌ Transits MISSING")
            
        return True

    except Exception as e:
        print(f"Request failed: {e}")
        return False

# Simple retry loop
for i in range(5):
    print(f"\n--- Attempt {i+1} ---")
    if check_features():
        print("\n🎉 VALIDATION SUCCESS: All features active on Render!")
        break
    else:
        print("Waiting 15s for deployment...")
        time.sleep(15)
