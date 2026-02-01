"""Check if background tasks are working."""

import requests
import time

BASE_URL = "http://localhost:8000"

print("Testing background task execution...")

# Start a workflow
response = requests.post(f"{BASE_URL}/api/research", json={"topic": "Test"})
session_id = response.json()["session_id"]
print(f"Started session: {session_id}")

# Check if it's actually running
print("\nChecking session status in memory...")
try:
    # This will tell us if the background task is even starting
    response = requests.get(f"{BASE_URL}/api/research/{session_id}/status")
    if response.status_code == 200:
        data = response.json()
        print(f"Status: {data['status']}")
        print(f"Phase: {data['current_phase']}")
        
        # Wait a bit and check again
        print("\nWaiting 30 seconds...")
        time.sleep(30)
        
        response = requests.get(f"{BASE_URL}/api/research/{session_id}/status")
        if response.status_code == 200:
            data = response.json()
            print(f"After 30s - Status: {data['status']}")
            print(f"After 30s - Phase: {data['current_phase']}")
            print(f"After 30s - Sources: {data['sources_count']}")
            
            if data['current_phase'] == 'initialized' and data['sources_count'] == 0:
                print("\n❌ Background task is NOT running!")
                print("The workflow is stuck in initialized phase.")
                print("This could be:")
                print("1. Rate limiting preventing any progress")
                print("2. Background task not starting")
                print("3. Error in workflow execution")
            else:
                print("\n✅ Background task is working!")
        else:
            print(f"Error checking status: {response.status_code}")
    else:
        print(f"Error: {response.status_code}")
        
except Exception as e:
    print(f"Error: {e}")