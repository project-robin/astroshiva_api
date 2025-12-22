import sys
import os
import datetime
from datetime import datetime, timedelta

# Add current directory to path
sys.path.append(os.getcwd())

# Mock necessary classes
class MockPlanet:
    def __init__(self, name, sign, sign_degrees):
        self.celestial_body = name
        self.sign = sign
        self.sign_degrees = sign_degrees

class MockD1:
    def __init__(self):
        # Moon at 22 Aries (Ashwini Nakshatra, Ketu Lord)
        # Ashwini is 0-13.33 deg.
        # Wait, 22 deg Aries is Bharani (13.33 - 26.66). Lord Venus.
        self.planets = [
            MockPlanet("Moon", "Aries", 22.0)
        ]

class MockChart:
    def __init__(self):
        self.d1_chart = MockD1()
        self.dashas = None # Trigger pure calculation

# Import Engine
from astro_engine import AstroEngine

def test_deep_dashas():
    engine = AstroEngine()
    chart = MockChart()
    
    # Birth: 2000-01-01
    birth_date = datetime(2000, 1, 1, 12, 0, 0)
    
    # Run Extraction
    with open("dasha_output.txt", "w") as f:
        f.write("Running Dasha Extraction...\n")
        result = engine._extract_dashas(chart, birth_datetime=birth_date)
        
        vim = result.get("vimshottari", {})
        current = vim.get("current_dasha", {})
        
        if not current:
            f.write("FAIL: No current dasha calculated.\n")
            return
            
        f.write("\n--- Current Dasha Stack ---\n")
        
        # Check Depth
        levels = ["mahadasha", "antardasha", "pratyantar_dasha", "sookshma_dasha", "prana_dasha"]
        
        curr_ptr = current
        depth_count = 0
        
        for lvl in levels:
            if lvl in curr_ptr:
                depth_count += 1
                data = curr_ptr[lvl]
                f.write(f"Level {depth_count} ({lvl}): {data.get('lord')} [{data.get('start')} - {data.get('end')}]\n")
                # Siblings structure implies we can access them all from 'current' root ?
                # NO. recursions return nested? 
                # Let's check my implementation again.
                # response = {MD}
                # response[AD] = ad_obj
                # ad_obj[PD] = ... NO.
                # My implementation structure:
                # response = {mahadasha: {..}, antardasha: {..}, pratyantar: {..}}
                # They are FLAT SIBLINGS in the `current_dasha` dict because I structured it that way?
                # Code check:
                # response["antardasha"] = ad_obj
                # inside ad_obj loop? No.
                # `if ad_obj: response["antardasha"] = ad_obj`
                # `if pd_obj: response["pratyantar"] = pd_obj`
                # YES. They are all attached to the ROOT `response` object.
                # So `curr_ptr = current` is correct, we just look for keys in `current`.
                pass
            else:
                f.write(f"MISSING Level: {lvl}\n")
                
        if depth_count == 5:
            f.write("\nSUCCESS: Full 5-Level Depth Achieved!\n")
        else:
            f.write(f"\nPARTIAL: Only {depth_count}/5 levels found.\n")

        # Check Lifetime list
        f.write("\n--- Lifetime Mahadashas ---\n")
        md_list = vim.get("mahadasha", [])
        f.write(f"Generated {len(md_list)} Mahadashas.\n")
        if len(md_list) > 0:
            f.write(f"First: {md_list[0]}\n")

if __name__ == "__main__":
    test_deep_dashas()
