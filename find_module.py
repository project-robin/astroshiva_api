import sys
from pathlib import Path

# Simulate the environment in reproduce_issue.py
vendor_path = Path(__file__).parent / "_vendor"
sys.path.insert(0, str(vendor_path))

try:
    import support.mod_general
    print(f"support.mod_general: {support.mod_general.__file__}")
except ImportError as e:
    print(f"Error importing support.mod_general: {e}")

try:
    import support.panchanga
    print(f"support.panchanga: {support.panchanga.__file__}")
except ImportError as e:
    print(f"Error importing support.panchanga: {e}")

try:
    import jyotishyamitra
    print(f"jyotishyamitra: {jyotishyamitra.__file__}")
except ImportError as e:
    print(f"Error importing jyotishyamitra: {e}")
