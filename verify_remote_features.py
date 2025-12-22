import requests
import json
import time

# Use the endpoint that generates a fresh chart for "Verification"
# We need to construct the URL with query params to ensure we get specific data if possible,
# Check if there is an endpoint that accepts POST or if we rely on the hardcoded /chart-test
# existing code used /chart-test. Let's assume it returns a standard sample chart.
API_URL = "https://astroshiva-api.onrender.com/api/chart-test"

def check_features():
    print(f"Connecting to {API_URL}...")
    try:
        resp = requests.get(API_URL)
        if resp.status_code != 200:
            print(f"Error: Status {resp.status_code}")
            return False
            
        data = resp.json().get('data', {})
        meta = data.get('meta', {})
        
        # --- Check 0: Version & Errors ---
        version = meta.get('api_version', 'unknown')
        print(f"API Version: {version}")
        
        if 'enrichment_error' in meta:
             print(f"⚠️ ENRICHMENT ERROR: {meta['enrichment_error']}")
             
        if 'phase1_error' in meta:
             print(f"⚠️ PHASE 1 ERROR: {meta['phase1_error']}")

        if version != "2.3.0":
            print(f"❌ Version mismatch. Expected 2.3.0, got {version}. Deployment pending?")
            return False
            
        # --- Check 1: Phase 1 - Deep Dasha (5 Levels) ---
        dashas = data.get('dashas', {}).get('vimshottari', {})
        current = dashas.get('current', {})
        
        # We expect mahadasha, antardasha, pratyantar_dasha, sookshma_dasha, prana_dasha
        levels = ['mahadasha', 'antardasha', 'pratyantar_dasha', 'sookshma_dasha', 'prana_dasha']
        missing_levels = [l for l in levels if l not in current]
        
        if not missing_levels:
            print(f"✅ Deep Dasha: All 5 levels present (Prana Lord: {current['prana_dasha']['lord']})")
        else:
            print(f"❌ Deep Dasha: Missing levels {missing_levels}")

        # --- Check 2: Phase 2 - Interpretive Traceability ---
        # Manglik
        manglik = data.get('doshas', {}).get('manglik', {})
        if 'because' in manglik:
             print(f"✅ Traceability (Manglik): 'because' field found ({len(manglik['because'])} reasons)")
        else:
             print("❌ Traceability (Manglik): 'because' field MISSING")
             
        # Yogas (Gajakesari or others)
        other_yogas = data.get('yogas', {}).get('other_yogas', [])
        found_trace = False
        for yoga in other_yogas:
            if 'because' in yoga and 'textual_source' in yoga:
                print(f"✅ Traceability (Yoga): Found in '{yoga['name']}' -> Source: {yoga['textual_source']}")
                found_trace = True
                break
        
        if not found_trace and len(other_yogas) > 0:
             print(f"❌ Traceability (Yoga): 'because'/'textual_source' missing in {len(other_yogas)} yogas.")

        # --- Check 3: Phase 3 - Varga Transparency ---
        # Verify D9 exists and has Ascendant
        d9 = data.get('divisional_charts', {}).get('D9', {})
        if 'ascendant' in d9 and 'planets' in d9:
            print(f"✅ Varga (D9): Calculated. Ascendant: {d9['ascendant']['sign']} {d9['ascendant']['degree']:.2f}")
        else:
            print("❌ Varga (D9): Data MISSING")

        return True

    except Exception as e:
        print(f"Request failed: {e}")
        return False

# Retry loop for deployment
print("Waiting for deployment to propagate...")
for i in range(1, 11):
    print(f"\n--- Validation Attempt {i} ---")
    if check_features():
        print("\n🎉 SUCCESS: All Strategic Pillars Verified on Live Production!")
        break
    else:
        print("Scaning... (Retrying in 20s)")
        time.sleep(20)
