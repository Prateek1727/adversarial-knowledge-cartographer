#!/usr/bin/env python3
"""
Quick test to verify the Mapper Agent improvements work for any topic.
"""

import requests
import json
import time

def test_research_topic(topic: str):
    """Test ANY research topic and check if relationships are generated."""
    print(f"\n🔬 Testing: '{topic}'")
    
    # Start research
    try:
        response = requests.post(
            "http://localhost:8000/api/research",
            json={"topic": topic},
            timeout=10
        )
        
        if response.status_code != 200:
            print(f"❌ Failed to start: {response.text}")
            return False
        
        session_id = response.json()["session_id"]
        print(f"📋 Session: {session_id[:8]}...")
        
        # Wait for completion (max 2 minutes for faster testing)
        for i in range(24):  # 24 * 5 seconds = 2 minutes
            time.sleep(5)
            
            try:
                status_response = requests.get(
                    f"http://localhost:8000/api/research/{session_id}/status",
                    timeout=5
                )
                
                if status_response.status_code == 200:
                    status = status_response.json()
                    entities = status['entities_count']
                    relationships = status['relationships_count']
                    
                    if status["status"] == "completed":
                        if relationships > 0:
                            print(f"✅ SUCCESS: {relationships} relationships, {entities} entities")
                            return True
                        else:
                            print(f"❌ FAILED: 0 relationships ({entities} entities)")
                            return False
                    
                    if i % 4 == 0:  # Every 20 seconds
                        print(f"⏳ {status['status']}: {entities}E, {relationships}R ({i*5}s)")
                        
            except requests.RequestException:
                print(f"⚠️  Connection issue at {i*5}s")
                continue
    
    except requests.RequestException as e:
        print(f"❌ Network error: {e}")
        return False
    
    print("❌ TIMEOUT: Took too long")
    return False

def main():
    """Test multiple topics to verify the fix works universally."""
    
    test_topics = [
        "health effects of coffee",                   # Health topic
        "benefits and risks of artificial intelligence",  # Technology topic  
        "climate change causes and solutions",        # Environmental topic
        "electric cars vs gasoline vehicles",         # Comparison topic
        "best programming languages for beginners",   # Education topic
        "social media impact on mental health"        # Psychology topic
    ]
    
    print("🧪 Testing Mapper Agent improvements across different topics...")
    
    results = {}
    for topic in test_topics:
        results[topic] = test_research_topic(topic)
    
    print("\n📊 RESULTS SUMMARY:")
    print("=" * 60)
    
    success_count = 0
    for topic, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {topic}")
        if success:
            success_count += 1
    
    print("=" * 60)
    print(f"Overall: {success_count}/{len(test_topics)} topics generated relationships")
    
    if success_count == len(test_topics):
        print("🎉 ALL TESTS PASSED! The Mapper Agent now works on all topics!")
    elif success_count > len(test_topics) // 2:
        print("⚠️  Most tests passed, but some topics still need work")
    else:
        print("❌ Most tests failed, more improvements needed")

if __name__ == "__main__":
    main()