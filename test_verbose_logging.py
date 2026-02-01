#!/usr/bin/env python3
"""
Test script to verify verbose logging is working.
Run this after starting the server with verbose logging.
"""

import requests
import time
import json

def test_verbose_logging():
    """Test that verbose logging shows activity in terminal."""
    
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Verbose Logging...")
    print("=" * 50)
    
    try:
        # Test 1: Health check
        print("1️⃣ Testing health endpoint...")
        response = requests.get(f"{base_url}/health")
        print(f"   Health check: {response.status_code}")
        time.sleep(1)
        
        # Test 2: API docs
        print("2️⃣ Testing docs endpoint...")
        response = requests.get(f"{base_url}/docs")
        print(f"   Docs: {response.status_code}")
        time.sleep(1)
        
        # Test 3: OpenAPI schema
        print("3️⃣ Testing OpenAPI endpoint...")
        response = requests.get(f"{base_url}/openapi.json")
        print(f"   OpenAPI: {response.status_code}")
        time.sleep(1)
        
        # Test 4: Start research (this should show lots of activity)
        print("4️⃣ Testing research endpoint...")
        research_data = {
            "topic": "verbose logging test"
        }
        response = requests.post(f"{base_url}/api/research", json=research_data)
        if response.status_code == 200:
            session_data = response.json()
            session_id = session_data["session_id"]
            print(f"   Research started: {session_id}")
            
            # Test 5: Check status (should show more activity)
            print("5️⃣ Testing status endpoint...")
            time.sleep(2)  # Give it a moment to start
            status_response = requests.get(f"{base_url}/api/research/{session_id}/status")
            print(f"   Status check: {status_response.status_code}")
            
        else:
            print(f"   Research failed: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Server not running! Please start the server first with:")
        print("   start_server_verbose.bat")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    print("=" * 50)
    print("✅ Test completed!")
    print("📺 Check your server terminal - you should see:")
    print("   🌐 HTTP request logs with emojis")
    print("   ✅ Response status and timing")
    print("   🚀 Background workflow activity")
    print("   📊 Research progress updates")
    
    return True

if __name__ == "__main__":
    test_verbose_logging()