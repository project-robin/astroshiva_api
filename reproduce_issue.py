# Test script to reproduce the ValueError found in the chart generation
import sys
from pathlib import Path

# Add _vendor directory to path for vendored jyotishyamitra
vendor_path = Path(__file__).parent / "_vendor"
sys.path.insert(0, str(vendor_path))

import jyotishyamitra as jm
import traceback
import tempfile
import uuid

def reproduce():
    try:
        print("Step 1: Input birth data")
        jm.input_birthdata(
            name="Test Person",
            place="New York",
            gender="male",
            year="1990",
            month="1",
            day="15",
            hour="12",
            min="30",
            sec="0",
            lattitude="40.7128",
            longitude="-74.0060",
            timezone="-5.0"
        )
        
        print("Step 2: Validate birth data")
        validation_result = jm.validate_birthdata()
        print(f"Validation result: {validation_result}")
        
        print("Step 3: Get birth data")
        birth_data = jm.get_birthdata()
        print("Got birth data")
        
        print("Step 4: Set output")
        output_dir = tempfile.gettempdir()
        output_filename = f"astro_{uuid.uuid4().hex[:8]}"
        jm.set_output(output_dir, output_filename)
        print(f"Output set to {output_dir}/{output_filename}")
        
        print("Step 5: Generate astrological data")
        jm.generate_astrologicalData(birth_data)
        print("Generation successful")
        
    except Exception:
        traceback.print_exc()

if __name__ == "__main__":
    reproduce()
