"""Test the workflow directly without the API."""

import logging
logging.basicConfig(level=logging.INFO)

from agents.workflow import WorkflowOrchestrator
from config import config

print("=" * 60)
print("Testing Workflow Directly")
print("=" * 60)

try:
    print("\n1. Validating configuration...")
    config.validate_api_keys()
    print("[OK] Configuration valid")
    
    print("\n2. Creating workflow orchestrator...")
    orchestrator = WorkflowOrchestrator(max_iterations=1, enable_checkpoints=False)
    print("[OK] Orchestrator created")
    
    print("\n3. Testing with simple topic...")
    topic = "Python programming"
    print(f"   Topic: {topic}")
    
    print("\n4. Executing workflow...")
    result = orchestrator.execute(topic)
    
    print("\n[OK] WORKFLOW COMPLETED!")
    print(f"   Sources: {len(result.sources)}")
    print(f"   Entities: {len(result.knowledge_graph.entities)}")
    print(f"   Relationships: {len(result.knowledge_graph.relationships)}")
    print(f"   Conflicts: {len(result.knowledge_graph.conflicts)}")
    
    if result.synthesis_report:
        print(f"   Report: {len(result.synthesis_report)} characters")
    
except Exception as e:
    print(f"\n[ERROR] {e}")
    import traceback
    traceback.print_exc()
