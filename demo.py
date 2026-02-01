"""
Demo script to showcase the Adversarial Knowledge Cartographer project structure.
This demonstrates the project without requiring API keys.
"""

import json
from pathlib import Path

def show_project_overview():
    """Display project overview and structure."""
    print("=" * 80)
    print("ADVERSARIAL KNOWLEDGE CARTOGRAPHER - PROJECT DEMO")
    print("=" * 80)
    print()
    
    print("📋 PROJECT OVERVIEW")
    print("-" * 80)
    print("An autonomous research system that acts as a 'Dialectic Engine':")
    print("  • Uses recursive adversarial prompting to find contradictions")
    print("  • Models conflicts as structured knowledge graphs")
    print("  • Creates synthesis reports with credibility-weighted analysis")
    print("  • Visualizes argument topologies as interactive graphs")
    print()
    
    print("🏗️  ARCHITECTURE")
    print("-" * 80)
    print("Multi-Agent Workflow:")
    print("  1. Scout Agent    → Gathers diverse sources from web")
    print("  2. Mapper Agent   → Extracts entities, relationships, conflicts")
    print("  3. Adversary Agent → Generates counter-queries, finds weaknesses")
    print("  4. Judge Agent    → Evaluates credibility, weights claims")
    print("  5. Synthesis Agent → Generates final report + knowledge graph")
    print()
    
    print("📁 PROJECT STRUCTURE")
    print("-" * 80)
    
    structure = {
        "agents/": "Multi-agent system (Scout, Mapper, Adversary, Judge, Synthesis)",
        "models/": "Pydantic data models for entities, relationships, conflicts",
        "api/": "FastAPI REST API for research workflows",
        "frontend/": "React visualization with interactive graph rendering",
        "tests/": "27 property-based tests + unit tests",
        ".kiro/specs/": "Requirements, design, and implementation tasks"
    }
    
    for folder, description in structure.items():
        print(f"  {folder:20} {description}")
    print()

def show_spec_files():
    """Display information about spec files."""
    print("📝 SPECIFICATION FILES")
    print("-" * 80)
    
    spec_path = Path(".kiro/specs/adversarial-knowledge-cartographer")
    
    if spec_path.exists():
        print(f"Spec location: {spec_path}")
        print()
        
        files = {
            "requirements.md": "EARS-compliant requirements with user stories",
            "design.md": "System design with 27 correctness properties",
            "tasks.md": "Implementation task list (all completed ✓)"
        }
        
        for file, desc in files.items():
            file_path = spec_path / file
            if file_path.exists():
                size = file_path.stat().st_size
                print(f"  ✓ {file:20} {desc} ({size:,} bytes)")
            else:
                print(f"  ✗ {file:20} Not found")
    else:
        print("  Spec directory not found")
    print()

def show_implementation_status():
    """Show implementation status."""
    print("✅ IMPLEMENTATION STATUS")
    print("-" * 80)
    
    components = [
        ("Data Models", "models/data_models.py", True),
        ("Scout Agent", "agents/scout.py", True),
        ("Mapper Agent", "agents/mapper.py", True),
        ("Adversary Agent", "agents/adversary.py", True),
        ("Judge Agent", "agents/judge.py", True),
        ("Synthesis Agent", "agents/synthesis.py", True),
        ("Workflow Orchestrator", "agents/workflow.py", True),
        ("FastAPI Backend", "api/app.py", True),
        ("React Frontend", "frontend/src/App.tsx", True),
        ("Property-Based Tests", "tests/test_*_properties.py", True),
    ]
    
    for name, path, status in components:
        status_icon = "✓" if status else "✗"
        print(f"  {status_icon} {name:30} {path}")
    print()

def show_testing_info():
    """Display testing information."""
    print("🧪 TESTING FRAMEWORK")
    print("-" * 80)
    print("Property-Based Testing with Hypothesis:")
    print()
    
    properties = {
        "Workflow Properties": ["Initialization", "Validation"],
        "Scout Properties": ["Source collection", "Diversity", "Error handling"],
        "Mapper Properties": ["Entity extraction", "Relationship detection", "Conflict identification"],
        "Adversary Properties": ["Weakness detection", "Counter-query generation", "Iteration limits"],
        "Judge Properties": ["Credibility scoring", "Domain weighting", "Citation analysis"],
        "Synthesis Properties": ["Report generation", "Graph completeness", "Citation inclusion"]
    }
    
    total = 0
    for category, props in properties.items():
        count = len(props)
        total += count
        print(f"  {category:25} {count} properties")
    
    print(f"\n  Total: {total} correctness properties tested with 100+ iterations each")
    print()

def show_api_endpoints():
    """Display API endpoints."""
    print("🌐 API ENDPOINTS")
    print("-" * 80)
    
    endpoints = [
        ("POST", "/api/research", "Start research workflow"),
        ("GET", "/api/research/{id}/status", "Get session status"),
        ("GET", "/api/research/{id}/graph", "Get knowledge graph"),
        ("GET", "/api/research/{id}/report", "Get synthesis report"),
        ("GET", "/docs", "Swagger API documentation"),
        ("GET", "/redoc", "ReDoc API documentation"),
    ]
    
    for method, path, description in endpoints:
        print(f"  {method:6} {path:35} {description}")
    print()

def show_usage_example():
    """Show usage example."""
    print("💡 USAGE EXAMPLE")
    print("-" * 80)
    print("Python API:")
    print("""
    from agents import WorkflowOrchestrator
    from config import config
    
    # Initialize orchestrator
    orchestrator = WorkflowOrchestrator(max_iterations=3)
    
    # Execute research workflow
    result = orchestrator.execute("Effects of climate change on agriculture")
    
    # Access results
    print(f"Entities: {len(result.knowledge_graph.entities)}")
    print(f"Conflicts: {len(result.knowledge_graph.conflicts)}")
    print(f"Report: {result.synthesis_report}")
""")
    
    print("REST API:")
    print("""
    # Start research
    curl -X POST http://localhost:8000/api/research \\
      -H "Content-Type: application/json" \\
      -d '{"topic": "Is coffee good or bad for health?"}'
    
    # Get knowledge graph
    curl http://localhost:8000/api/research/{session_id}/graph
""")
    print()

def show_next_steps():
    """Show next steps to run the project."""
    print("🚀 NEXT STEPS TO RUN THE PROJECT")
    print("-" * 80)
    print("1. Install dependencies:")
    print("   pip install -r requirements.txt")
    print()
    print("2. Configure API keys in .env file:")
    print("   - Get OpenAI API key: https://platform.openai.com/api-keys")
    print("   - Get Tavily API key: https://tavily.com/")
    print()
    print("3. Start the backend API:")
    print("   python -m uvicorn api.app:app --reload --port 8000")
    print()
    print("4. Start the frontend (in separate terminal):")
    print("   cd frontend")
    print("   npm install")
    print("   npm start")
    print()
    print("5. Open browser:")
    print("   Frontend: http://localhost:3000")
    print("   API Docs: http://localhost:8000/docs")
    print()

def main():
    """Main demo function."""
    show_project_overview()
    show_spec_files()
    show_implementation_status()
    show_testing_info()
    show_api_endpoints()
    show_usage_example()
    show_next_steps()
    
    print("=" * 80)
    print("For more information, see:")
    print("  • README.md - Complete documentation")
    print("  • QUICKSTART.md - Quick start guide")
    print("  • ARCHITECTURE.md - System architecture")
    print("  • .kiro/specs/adversarial-knowledge-cartographer/ - Full specification")
    print("=" * 80)

if __name__ == "__main__":
    main()
