"""Monitor workflow progress in real-time."""

import requests
import time
import sys

BASE_URL = "http://localhost:8000"
SESSION_ID = "aacd7073-d0d7-4ba8-bc64-3d7aa8628721"

print("=" * 60)
print("Monitoring Workflow Progress")
print("=" * 60)
print(f"Session ID: {SESSION_ID}")
print("\nWatching for updates every 5 seconds...")
print("Press Ctrl+C to stop monitoring")
print("=" * 60)

last_status = None
start_time = time.time()

try:
    while True:
        try:
            response = requests.get(
                f"{BASE_URL}/api/research/{SESSION_ID}/status",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                elapsed = int(time.time() - start_time)
                
                # Create status line
                status_line = (
                    f"[{elapsed:3d}s] "
                    f"Status: {data['status']:10s} | "
                    f"Phase: {data['current_phase']:12s} | "
                    f"Sources: {data['sources_count']:2d} | "
                    f"Entities: {data['entities_count']:2d} | "
                    f"Relationships: {data['relationships_count']:2d} | "
                    f"Conflicts: {data['conflicts_count']:2d}"
                )
                
                # Only print if status changed
                if status_line != last_status:
                    print(status_line)
                    last_status = status_line
                
                # Check if completed
                if data['status'] == 'completed':
                    print("\n" + "=" * 60)
                    print("✅ WORKFLOW COMPLETED!")
                    print("=" * 60)
                    print(f"\nFinal Results:")
                    print(f"  Sources: {data['sources_count']}")
                    print(f"  Entities: {data['entities_count']}")
                    print(f"  Relationships: {data['relationships_count']}")
                    print(f"  Conflicts: {data['conflicts_count']}")
                    print(f"  Report available: {data['synthesis_available']}")
                    print(f"\nTotal time: {elapsed} seconds")
                    print(f"\nView results:")
                    print(f"  Graph:  {BASE_URL}/api/research/{SESSION_ID}/graph")
                    print(f"  Report: {BASE_URL}/api/research/{SESSION_ID}/report")
                    print(f"  Docs:   {BASE_URL}/docs")
                    break
                
                # Check if failed
                if data['status'] == 'failed':
                    print("\n" + "=" * 60)
                    print("❌ WORKFLOW FAILED")
                    print("=" * 60)
                    print("Check server logs for details")
                    break
                    
            else:
                print(f"Error: {response.status_code}")
                break
                
        except requests.exceptions.RequestException as e:
            print(f"Connection error: {e}")
            break
        
        # Wait 5 seconds before next check
        time.sleep(5)
        
except KeyboardInterrupt:
    print("\n\nMonitoring stopped by user")
    elapsed = int(time.time() - start_time)
    print(f"Elapsed time: {elapsed} seconds")
    print(f"\nCheck status manually:")
    print(f"  {BASE_URL}/api/research/{SESSION_ID}/status")
