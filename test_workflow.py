"""Test the workflow to see where it's failing."""

import logging
logging.basicConfig(level=logging.INFO)

from agents.workflow import WorkflowOrchestrator
from config import config

print("=" * 60)
print("Testing Workflow")
print("=" * 60)

try:
    print("\n1. Validating configuration...")
    config.validate_api_keys()
    print("[OK] Configuration valid")
    
    print("\n2. Creating workflow orchestrator...")
    orchestrator = WorkflowOrchestrator(max_iterations=1, enable_checkpoints=False)
    print("[OK] Orchestrator created")
    
    print("\n3. Testing with simple topic...")
    topic = "Is coffee good for health?"
    print(f"   Topic: {topic}")
    
    print("\n4. Executing workflow...")
    result = orchestrator.execute(topic)
    
    print("\n[OK] WORKFLOW COMPLETED!")
    
    # Handle both dict and WorkflowState responses
    if isinstance(result, dict):
        sources = result.get('sources', [])
        kg = result.get('knowledge_graph', {})
        entities = kg.get('entities', []) if isinstance(kg, dict) else getattr(kg, 'entities', [])
        relationships = kg.get('relationships', []) if isinstance(kg, dict) else getattr(kg, 'relationships', [])
        conflicts = kg.get('conflicts', []) if isinstance(kg, dict) else getattr(kg, 'conflicts', [])
        report = result.get('synthesis_report')
    else:
        sources = result.sources
        entities = result.knowledge_graph.entities
        relationships = result.knowledge_graph.relationships
        conflicts = result.knowledge_graph.conflicts
        report = result.synthesis_report
    
    print(f"   Sources collected: {len(sources)}")
    print(f"   Entities found: {len(entities)}")
    print(f"   Relationships: {len(relationships)}")
    print(f"   Conflicts: {len(conflicts)}")
    
    if report:
        print(f"\n   Report preview:")
        print(f"   {report[:200]}...")
    
except Exception as e:
    print(f"\n[ERROR] {e}")
    import traceback
    traceback.print_exc()
    print("\nThis error needs to be fixed before the API will work.")
