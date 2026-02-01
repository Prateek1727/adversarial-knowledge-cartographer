"""Final comprehensive test."""

import requests
import time

BASE_URL = "http://localhost:8000"

print("Waiting for server to start...")
for i in range(10):
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=2)
        if response.status_code == 200:
            print(f"✅ Server is ready!\n")
            break
    except:
        pass
    time.sleep(1)
else:
    print("❌ Server not responding")
    exit(1)

# Start workflow
print("Starting workflow...")
response = requests.post(f"{BASE_URL}/api/research", json={"topic": "Python programming"})
session_id = response.json()["session_id"]
print(f"Session ID: {session_id}\n")

# Monitor for 2 minutes
print("Monitoring progress (will check every 10 seconds for 2 minutes)...")
for i in range(12):  # 12 * 10 = 120 seconds
    try:
        response = requests.get(f"{BASE_URL}/api/research/{session_id}/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"[{i*10:3d}s] {data['status']:10s} | {data['current_phase']:12s} | "
                  f"S:{data['sources_count']:2d} E:{data['entities_count']:2d} "
                  f"R:{data['relationships_count']:2d} C:{data['conflicts_count']:2d}")
            
            if data['status'] == 'completed':
                print("\n✅ WORKFLOW COMPLETED!")
                print(f"\nFinal counts:")
                print(f"  Sources: {data['sources_count']}")
                print(f"  Entities: {data['entities_count']}")
                print(f"  Relationships: {data['relationships_count']}")
                print(f"  Conflicts: {data['conflicts_count']}")
                
                # Try to get graph
                print(f"\nTesting graph endpoint...")
                response = requests.get(f"{BASE_URL}/api/research/{session_id}/graph")
                if response.status_code == 200:
                    graph = response.json()
                    print(f"  ✅ Graph: {len(graph['nodes'])} nodes, {len(graph['edges'])} edges")
                else:
                    print(f"  ❌ Graph error: {response.status_code}")
                
                # Try to get report
                print(f"\nTesting report endpoint...")
                response = requests.get(f"{BASE_URL}/api/research/{session_id}/report")
                if response.status_code == 200:
                    report = response.json()
                    print(f"  ✅ Report: {len(report['report'])} characters")
                else:
                    print(f"  ❌ Report error: {response.status_code}")
                
                break
        else:
            print(f"[{i*10:3d}s] ❌ Error {response.status_code}: {response.text[:100]}")
            break
    except Exception as e:
        print(f"[{i*10:3d}s] ❌ Exception: {e}")
        break
    
    time.sleep(10)

print("\n" + "="*60)
print("Test complete!")
print(f"View in browser: {BASE_URL}/docs")
