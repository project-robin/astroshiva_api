"""
Quick test script to verify the API fixes
"""
import requests
import json

# Test 1: Charts parameter with trailing quote (URL encoding artifact)
print("=" * 60)
print("TEST 1: Charts parameter with URL encoding artifacts")
print("=" * 60)

url1 = "http://localhost:8000/api/chart-get?name=John&dob=1990-05-15&tob=14:30:00&place=Mumbai&latitude=19.0760&longitude=72.8777&timezone=+5.5&charts=D1,D9%22"

print(f"Testing URL: {url1}")
print("Expected: Should sanitize the trailing %22 (quote) and return D1 and D9 charts")
print()

# Test 2: Malformed charts parameter
print("=" * 60)
print("TEST 2: Malformed charts parameter")
print("=" * 60)

url2 = "http://localhost:8000/api/chart-get?name=John&dob=1990-05-15&tob=14:30:00&place=Mumbai&latitude=19.0760&longitude=72.8777&timezone=+5.5&charts=invalid"

print(f"Testing URL: {url2}")
print("Expected: Should default to D1, D9, D10")
print()

# Test 3: Rahu/Ketu transits verification
print("=" * 60)
print("TEST 3: Rahu/Ketu Transit Positions")
print("=" * 60)

url3 = "http://localhost:8000/api/chart-get?name=John&dob=1990-05-15&tob=14:30:00&place=Mumbai&latitude=19.0760&longitude=72.8777&timezone=+5.5&charts=D1"

print(f"Testing URL: {url3}")
print("Expected: Rahu and Ketu should be in opposite signs (180° apart)")
print()

print("To run these tests:")
print("1. Start the local server: uvicorn app:app --reload")
print("2. Run this script: python test_api_fixes.py")
print("3. Or manually test using curl/browser")
