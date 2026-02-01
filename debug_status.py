"""Debug the status endpoint error."""

import requests
import time

BASE_URL = "http://localhost:8000"

# Start workflow
print("Starting workflow...")
response = requests.post(f"{BASE_URL}/api/research", json={"topic": "Test topic"})
session_id = response.json()["session_id"]
print(f"Session ID: {session_id}\n")

# Check status multiple times
for i in range(10):
    print(f"Check #{i+1} (after {i*3}s):")
    try:
        response = requests.get(f"{BASE_URL}/api/research/{session_id}/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"  ✅ Phase: {data['current_phase']}, Sources: {data['sources_count']}, Entities: {data['entities_count']}")
        else:
            print(f"  ❌ Error {response.status_code}")
            print(f"  Response: {response.text[:200]}")
            # Try to get more details
            try:
                error_data = response.json()
                print(f"  Detail: {error_data}")
            except:
                pass
            break
    except Exception as e:
        print(f"  ❌ Exception: {e}")
        break
    
    time.sleep(3)
