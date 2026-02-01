"""Quick test to see the actual error."""

import requests
import traceback

BASE_URL = "http://localhost:8000"

print("Starting new workflow...")
response = requests.post(
    f"{BASE_URL}/api/research",
    json={"topic": "Python programming"}
)
data = response.json()
session_id = data["session_id"]
print(f"Session ID: {session_id}")

print("\nChecking status immediately...")
try:
    response = requests.get(f"{BASE_URL}/api/research/{session_id}/status")
    print(f"Status code: {response.status_code}")
    if response.status_code == 200:
        print(f"Response: {response.json()}")
    else:
        print(f"Error response: {response.text}")
except Exception as e:
    print(f"Exception: {e}")
    traceback.print_exc()
