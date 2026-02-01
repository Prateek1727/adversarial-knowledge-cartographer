#!/usr/bin/env python3
"""
Debug script to analyze why the cricket topic isn't generating relationships.
"""

import json
import os
from pathlib import Path

def analyze_checkpoint():
    """Analyze the latest cricket checkpoint to understand the issue."""
    
    checkpoint_dir = Path(".checkpoints")
    cricket_files = list(checkpoint_dir.glob("*cricket*mapper*.json"))
    
    if not cricket_files:
        print("❌ No cricket checkpoint files found")
        return
    
    # Get the most recent file
    latest_file = max(cricket_files, key=os.path.getctime)
    print(f"📁 Analyzing: {latest_file}")
    
    with open(latest_file, 'r') as f:
        data = json.load(f)
    
    kg = data.get('knowledge_graph', {})
    entities = kg.get('entities', [])
    relationships = kg.get('relationships', [])
    conflicts = kg.get('conflicts', [])
    
    print(f"\n📊 EXTRACTED DATA:")
    print(f"Entities: {len(entities)}")
    print(f"Relationships: {len(relationships)}")
    print(f"Conflicts: {len(conflicts)}")
    
    print(f"\n🏷️  ENTITIES (first 20):")
    for i, entity in enumerate(entities[:20]):
        print(f"  {i+1:2d}. {entity}")
    
    if len(entities) > 20:
        print(f"  ... and {len(entities) - 20} more")
    
    print(f"\n🔗 RELATIONSHIPS:")
    if relationships:
        for i, rel in enumerate(relationships):
            print(f"  {i+1}. {rel.get('source', 'N/A')} -> {rel.get('relation', 'N/A')} -> {rel.get('target', 'N/A')}")
    else:
        print("  ❌ No relationships found")
    
    print(f"\n⚔️  CONFLICTS:")
    if conflicts:
        for i, conflict in enumerate(conflicts):
            print(f"  {i+1}. {conflict.get('point_of_contention', 'N/A')}")
    else:
        print("  ❌ No conflicts found")
    
    # Analyze why relationships might be missing
    print(f"\n🔍 ANALYSIS:")
    
    # Check if we have player entities
    players = [e for e in entities if any(name in e.lower() for name in ['kohli', 'root', 'williamson', 'sharma', 'jadeja'])]
    print(f"Player entities found: {len(players)}")
    for player in players[:5]:
        print(f"  - {player}")
    
    # Check if we have ranking/system entities
    rankings = [e for e in entities if any(word in e.lower() for word in ['ranking', 'icc', 'test', 'odi', 't20'])]
    print(f"Ranking/system entities found: {len(rankings)}")
    for ranking in rankings[:5]:
        print(f"  - {ranking}")
    
    if players and rankings:
        print("✅ Both players and rankings found - relationships should be possible")
    elif players and not rankings:
        print("⚠️  Players found but no ranking systems - this might be the issue")
    elif not players and rankings:
        print("⚠️  Rankings found but no players - this might be the issue")
    else:
        print("❌ Neither players nor rankings found clearly")

def main():
    print("🏏 Cricket Topic Debug Analysis")
    print("=" * 50)
    analyze_checkpoint()

if __name__ == "__main__":
    main()