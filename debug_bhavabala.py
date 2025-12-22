import sys
import os
import inspect

# Add the backend directory to sys.path
sys.path.append(os.getcwd())

from astro_engine import AstroEngine
from jyotishganit import calculate_birth_chart

def inspect_object(obj, path="chart", max_depth=3, current_depth=0):
    """Recursively inspect object structure to find keys related to 'bala'."""
    if current_depth > max_depth:
        return

    indent = "  " * current_depth
    
    # Try to get attributes and keys
    attributes = dir(obj)
    
    # Check for direct dictionary
    if isinstance(obj, dict):
        for k, v in obj.items():
            if "bala" in str(k).lower():
                print(f"{indent}FOUND MATCH: {path}['{k}'] (Type: {type(v).__name__})")
            
            if isinstance(v, (dict, list, object)) and not isinstance(v, (str, int, float, bool)):
                 inspect_object(v, f"{path}['{k}']", max_depth, current_depth + 1)
        return

    # Check for object attributes
    for attr in attributes:
        if attr.startswith("__"): continue
        
        try:
            val = getattr(obj, attr)
            if "bala" in attr.lower():
                print(f"{indent}FOUND MATCH: {path}.{attr} (Type: {type(val).__name__})")
                
            if not inspect.ismethod(val) and not isinstance(val, (str, int, float, bool)):
                 inspect_object(val, f"{path}.{attr}", max_depth, current_depth + 1)
        except:
            pass

def run_introspection():
    print("Initializing AstroEngine...")
    engine = AstroEngine()
    
    print("\nGenerating Chart...")
    # Use the test case data
    result = engine.generate_full_chart(
        name="Test",
        dob="2001-05-26",
        tob="21:48:00",
        place="Ahmednagar",
        latitude=19.3833,
        longitude=74.65,
        timezone=5.5
    )
    
    print("\nIntrospecting current_chart object...")
    if engine.current_chart:
        inspect_object(engine.current_chart)
    else:
        print("❌ engine.current_chart is None")

if __name__ == "__main__":
    run_introspection()
