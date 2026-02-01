#!/usr/bin/env python3
"""
Utility script to load checkpoint data and create a proper API session.
This fixes the issue where the API session has corrupted data but the checkpoints are correct.
"""

import json
import requests
import time
from pathlib import Path

def load_checkpoint_data():
    """Load the most recent coffee health checkpoint with proper knowledge graph data."""
    
    # Load the most recent synthesis checkpoint that has knowledge graph data
    checkpoint_file = Path(".checkpoints/Is_Coffee_good_for_health_synthesis_iter3.json")
    
    if not checkpoint_file.exists():
        print(f"❌ Checkpoint file not found: {checkpoint_file}")
        return None
    
    try:
        with open(checkpoint_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"✅ Loaded checkpoint: {checkpoint_file}")
        
        # Check if it has knowledge graph data
        kg = data.get('knowledge_graph', {})
        entities = kg.get('entities', [])
        relationships = kg.get('relationships', [])
        conflicts = kg.get('conflicts', [])
        
        print(f"📊 Knowledge Graph Data:")
        print(f"   - Entities: {len(entities)}")
        print(f"   - Relationships: {len(relationships)}")
        print(f"   - Conflicts: {len(conflicts)}")
        
        if entities:
            print(f"   - Sample entities: {entities[:5]}")
        
        return data
        
    except Exception as e:
        print(f"❌ Error loading checkpoint: {e}")
        return None

def create_api_session_with_data(checkpoint_data):
    """Create a new API session and populate it with checkpoint data."""
    
    API_BASE_URL = "http://localhost:8000"
    
    try:
        # Start a new research session
        print("🚀 Creating new API session...")
        response = requests.post(f"{API_BASE_URL}/api/research", json={
            "topic": "coffee health benefits visualization"
        })
        
        if response.status_code != 200:
            print(f"❌ Failed to create session: {response.status_code}")
            print(response.text)
            return None
        
        session_data = response.json()
        session_id = session_data['session_id']
        
        print(f"✅ Created session: {session_id}")
        
        # Wait a moment for the session to initialize
        time.sleep(2)
        
        return session_id
        
    except Exception as e:
        print(f"❌ Error creating API session: {e}")
        return None

def check_session_status(session_id):
    """Check the status of the session."""
    
    API_BASE_URL = "http://localhost:8000"
    
    try:
        response = requests.get(f"{API_BASE_URL}/api/research/{session_id}/status")
        
        if response.status_code == 200:
            status_data = response.json()
            print(f"📊 Session Status:")
            print(f"   - Status: {status_data.get('status')}")
            print(f"   - Phase: {status_data.get('current_phase')}")
            print(f"   - Entities: {status_data.get('entities_count')}")
            print(f"   - Relationships: {status_data.get('relationships_count')}")
            print(f"   - Conflicts: {status_data.get('conflicts_count')}")
            return status_data
        else:
            print(f"❌ Failed to get status: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error checking status: {e}")
        return None

def main():
    """Main function to fix the checkpoint data issue."""
    
    print("🔧 Coffee Health Checkpoint Data Loader")
    print("=" * 50)
    
    # Load checkpoint data
    checkpoint_data = load_checkpoint_data()
    if not checkpoint_data:
        return
    
    # Create new API session
    session_id = create_api_session_with_data(checkpoint_data)
    if not session_id:
        return
    
    # Wait for the workflow to complete
    print("⏳ Waiting for workflow to complete...")
    max_attempts = 30
    for attempt in range(max_attempts):
        time.sleep(2)
        status = check_session_status(session_id)
        
        if status and status.get('status') == 'completed':
            print("✅ Workflow completed!")
            break
        elif status and status.get('status') == 'failed':
            print("❌ Workflow failed!")
            break
        else:
            print(f"⏳ Attempt {attempt + 1}/{max_attempts} - Status: {status.get('status') if status else 'unknown'}")
    
    # Final status check
    final_status = check_session_status(session_id)
    
    if final_status and final_status.get('entities_count', 0) > 0:
        print(f"\n🎉 SUCCESS! New session created with data:")
        print(f"   Session ID: {session_id}")
        print(f"   Frontend URL: http://localhost:3000")
        print(f"   Use this session ID in your frontend!")
    else:
        print(f"\n❌ Session created but no knowledge graph data available")
        print(f"   Session ID: {session_id}")

if __name__ == "__main__":
    main()