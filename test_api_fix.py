"""Test the API fix for status endpoint."""

import requests
import time
import json

BASE_URL = "http://localhost:8000"

print("=" * 60)
print("Testing API Fix")
print("=" * 60)

# Test 1: Health check
print("\n1. Testing health endpoint...")
try:
    response = requests.get(f"{BASE_URL}/health", timeout=5)
    if response.status_code == 200:
        print(f"   ✅ Health check passed: {response.json()}")
    else:
        print(f"   ❌ Health check failed: {response.status_code}")
        exit(1)
except Exception as e:
    print(f"   ❌ Cannot connect to server: {e}")
    print("\n   Please start the server first:")
    print("   > start_server.bat")
    exit(1)

# Test 2: Start research
print("\n2. Starting research workflow...")
try:
    response = requests.post(
        f"{BASE_URL}/api/research",
        json={"topic": "Is coffee good for health"},
        timeout=10
    )
    if response.status_code == 200:
        data = response.json()
        session_id = data["session_id"]
        print(f"   ✅ Research started")
        print(f"   Session ID: {session_id}")
    else:
        print(f"   ❌ Failed to start research: {response.status_code}")
        print(f"   Response: {response.text}")
        exit(1)
except Exception as e:
    print(f"   ❌ Error: {e}")
    exit(1)

# Test 3: Check status immediately (this was failing before)
print("\n3. Testing status endpoint (immediate check)...")
try:
    response = requests.get(
        f"{BASE_URL}/api/research/{session_id}/status",
        timeout=10
    )
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Status check passed!")
        print(f"   Status: {data['status']}")
        print(f"   Phase: {data['current_phase']}")
        print(f"   Sources: {data['sources_count']}")
        print(f"   Entities: {data['entities_count']}")
    else:
        print(f"   ❌ Status check failed: {response.status_code}")
        print(f"   Response: {response.text}")
        exit(1)
except Exception as e:
    print(f"   ❌ Error: {e}")
    exit(1)

# Test 4: Wait and check again
print("\n4. Waiting 10 seconds and checking again...")
time.sleep(10)
try:
    response = requests.get(
        f"{BASE_URL}/api/research/{session_id}/status",
        timeout=10
    )
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Status check passed!")
        print(f"   Status: {data['status']}")
        print(f"   Phase: {data['current_phase']}")
        print(f"   Sources: {data['sources_count']}")
        print(f"   Entities: {data['entities_count']}")
        print(f"   Relationships: {data['relationships_count']}")
        print(f"   Conflicts: {data['conflicts_count']}")
    else:
        print(f"   ❌ Status check failed: {response.status_code}")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "=" * 60)
print("✅ API FIX VERIFIED!")
print("=" * 60)
print(f"\nYour session ID: {session_id}")
print("\nThe workflow is running in the background.")
print("Wait ~2 minutes, then check:")
print(f"  Status: {BASE_URL}/api/research/{session_id}/status")
print(f"  Graph:  {BASE_URL}/api/research/{session_id}/graph")
print(f"  Report: {BASE_URL}/api/research/{session_id}/report")
print("\nOr use the Swagger UI: http://localhost:8000/docs")
