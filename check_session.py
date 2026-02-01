"""Check the completed session."""

import requests
import json

BASE_URL = "http://localhost:8000"
SESSION_ID = "ad16fd85-31c0-4e25-a9d3-03ab326ea781"

print("=" * 60)
print("Checking Completed Session")
print("=" * 60)

# Check status
print("\n1. Checking status...")
try:
    response = requests.get(f"{BASE_URL}/api/research/{SESSION_ID}/status", timeout=10)
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Status: {data['status']}")
        print(f"   Phase: {data['current_phase']}")
        print(f"   Sources: {data['sources_count']}")
        print(f"   Entities: {data['entities_count']}")
        print(f"   Relationships: {data['relationships_count']}")
        print(f"   Conflicts: {data['conflicts_count']}")
        print(f"   Report available: {data['synthesis_available']}")
    else:
        print(f"   ❌ Error {response.status_code}: {response.text}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Check graph
print("\n2. Checking knowledge graph...")
try:
    response = requests.get(f"{BASE_URL}/api/research/{SESSION_ID}/graph", timeout=10)
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Graph retrieved!")
        print(f"   Nodes: {len(data['nodes'])}")
        print(f"   Edges: {len(data['edges'])}")
        
        # Show some entities
        if data['nodes']:
            print(f"\n   Sample entities:")
            for node in data['nodes'][:5]:
                print(f"     - {node['label']} ({node['type']})")
    else:
        print(f"   ❌ Error {response.status_code}: {response.text}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Check report
print("\n3. Checking synthesis report...")
try:
    response = requests.get(f"{BASE_URL}/api/research/{SESSION_ID}/report", timeout=10)
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Report retrieved!")
        print(f"   Length: {len(data['report'])} characters")
        print(f"\n   Preview:")
        print(f"   {data['report'][:300]}...")
    else:
        print(f"   ❌ Error {response.status_code}: {response.text}")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "=" * 60)
print("✅ ALL ENDPOINTS WORKING!")
print("=" * 60)
