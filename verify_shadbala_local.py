
from astro_engine import AstroEngine
import json

def verify():
    engine = AstroEngine()
    data = engine.generate_full_chart(
        name="Verify",
        dob="2000-01-01",
        tob="12:00:00",
        place="Delhi",
        latitude=28.6,
        longitude=77.2,
        timezone="+5.5"
    )
    
    # Check Meta
    print("--- Meta Check ---")
    if "meta" in data and "content_map" in data["meta"]:
        print("✅ Meta tags present")
        print(f"Engine Version: {data['meta']['calculation_engine']['version']}")
    else:
        print("❌ Meta tags missing")

    # Check Shadbala
    print("\n--- Shadbala Check ---")
    balas = data.get("balas", {}).get("shadbala", {})
    if not balas:
        print("❌ Shadbala empty")
        return

    sun_bala = balas.get("Sun", {})
    if isinstance(sun_bala, dict) and "Sthanabala" in sun_bala:
        print("✅ Shadbala Detailed Breakdown Found")
        print(f"Sun Sthanabala: {sun_bala.get('Sthanabala')}") 
        # Check for numpy types existence (should be gone)
        import numpy as np
        try:
             json.dumps(sun_bala)
             print("✅ JSON Serialization Safe (No numpy types)")
        except TypeError:
             print("❌ JSON Serialization Failed (Numpy types persist)")
    else:
         print(f"❌ Shadbala missing details. Type: {type(sun_bala)}")
         print(sun_bala)

if __name__ == "__main__":
    verify()
