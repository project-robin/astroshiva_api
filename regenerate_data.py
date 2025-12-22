from astro_engine import AstroEngine
import json
import os

def regenerate():
    print("Regenerating our_data.json with standard test case...")
    engine = AstroEngine()
    
    # Test Case: "K"
    # DOB: 26 May 2001
    # TOB: 21:48:00
    # Place: Ahmednagar (19.3833 N, 74.65 E) (Matches previous context)
    # Timezone: 5.5
    
    try:
        chart = engine.generate_full_chart(
            name="K",
            dob="2001-05-26",
            tob="21:48:00",
            place="Ahmednagar",
            latitude=19.3833,
            longitude=74.65,
            timezone="+5.5"
        )
        
        # Determine output path
        output_path = r"d:\building apps\astro-shiva 2.0\12astro-backend\reference\astro_data\our_data.json"
        
        # Use the dictionary returned by generate_full_chart directly
        # Wrap it to mimic API response structure used in verification script
        final_output = {
            "status": "success",
            "data": chart
        }
        
        json_str = json.dumps(final_output, indent=2, default=str)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(json_str)
            
        print(f"✅ Successfully updated: {output_path}")
        print(f"File size: {len(json_str)} bytes")
        
    except Exception as e:
        print(f"❌ Error regenerating data: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    regenerate()
