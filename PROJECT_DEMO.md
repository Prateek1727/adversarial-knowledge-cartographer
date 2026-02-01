# Adversarial Knowledge Cartographer - Project Demo

## 🎯 What This Project Does

This is a **fully implemented autonomous research system** that acts as a "Dialectic Engine" - it doesn't just summarize information, it actively seeks out disagreements and builds knowledge graphs of conflicting viewpoints.

## 🏗️ Complete Architecture

```
User Query: "Is coffee good or bad for health?"
           ↓
    [Scout Agent]
    Searches web, finds 10+ diverse sources
    ✓ Implemented with Tavily/Serper API integration
           ↓
    [Mapper Agent]
    Extracts entities, relationships, conflicts
    ✓ Implemented with LangChain + LLM parsing
           ↓
    [Adversary Agent]
    Challenges findings, generates counter-queries
    ✓ Implemented with adversarial prompting
           ↓
    [Decision: Weak claims found?]
           ↓ Yes (loop up to 3x)
    [Back to Scout with new queries]
           ↓ No
    [Judge Agent]
    Scores credibility (domain, citations, recency)
    ✓ Implemented with weighted scoring algorithm
           ↓
    [Synthesis Agent]
    Generates final report + knowledge graph
    ✓ Implemented with structured output
           ↓
    [Visualization]
    Interactive React graph with React Flow
    ✓ Implemented with custom node components
```

## 📁 Fully Implemented Components

### Backend (Python)
- ✅ **5 Specialized Agents** (`agents/`)
  - `scout.py` - Web search with rate limiting & fallback
  - `mapper.py` - Entity/relationship extraction
  - `adversary.py` - Bias detection & counter-queries
  - `judge.py` - Credibility scoring algorithm
  - `synthesis.py` - Report generation
  - `workflow.py` - LangGraph orchestration

- ✅ **Data Models** (`models/data_models.py`)
  - Pydantic models for type safety
  - Entity, Relationship, Conflict, Source classes
  - WorkflowState for state management

- ✅ **REST API** (`api/app.py`)
  - FastAPI with async support
  - Session management
  - CORS configured
  - Swagger/ReDoc documentation

- ✅ **Utilities** (`utils/`)
  - Structured logging with context
  - Error handling with retry logic
  - Configuration management

### Frontend (React + TypeScript)
- ✅ **Interactive Graph Visualization** (`frontend/src/`)
  - React Flow integration
  - Custom EntityNode and ConflictNode components
  - Color-coded relationships (green=support, red=refute)
  - Conflict highlighting with pulsing animation
  - Detail panel with citations
  - Zoom, pan, navigation controls

### Testing (Hypothesis + Pytest)
- ✅ **27 Correctness Properties**
  - Property-based tests with 100+ iterations each
  - Tests for all agents
  - Graph structure validation
  - Credibility scoring verification
  - Round-trip serialization tests

## 📊 Example Output

### Knowledge Graph Structure
```json
{
  "entities": [
    {
      "id": "e1",
      "name": "Coffee consumption",
      "type": "concept",
      "description": "Regular intake of coffee beverages"
    },
    {
      "id": "e2",
      "name": "Cardiovascular health",
      "type": "health_outcome",
      "description": "Heart and blood vessel health"
    }
  ],
  "relationships": [
    {
      "source": "e1",
      "target": "e2",
      "type": "supports",
      "description": "Moderate coffee consumption associated with reduced heart disease risk",
      "credibility_score": 0.85,
      "citations": ["https://pubmed.ncbi.nlm.nih.gov/..."]
    }
  ],
  "conflicts": [
    {
      "id": "c1",
      "entity_ids": ["e1", "e2"],
      "description": "Conflicting evidence on coffee's cardiovascular effects",
      "conflicting_claims": [
        "Coffee reduces heart disease risk (credibility: 0.85)",
        "Coffee increases blood pressure (credibility: 0.72)"
      ]
    }
  ]
}
```

### Synthesis Report
```
# Research Report: Is coffee good or bad for health?

## Executive Summary
Analysis of 15 sources reveals nuanced evidence with significant conflicts...

## Key Findings
1. Cardiovascular Effects (Conflict Detected)
   - Supporting evidence (credibility: 0.85): Moderate consumption protective
   - Contradicting evidence (credibility: 0.72): Acute blood pressure increase
   
2. Cognitive Benefits (Strong Consensus)
   - Evidence (credibility: 0.90): Improved alertness and focus
   
## Credibility Analysis
- High-credibility sources (.edu, .gov): 8/15
- Recent publications (< 2 years): 12/15
- Citation indicators present: 10/15

## Conclusion
The evidence suggests moderate coffee consumption (2-3 cups/day) has net positive 
effects, though individual responses vary...
```

## 🎨 Visual Interface

The React frontend provides:
- **Interactive graph** with draggable nodes
- **Color-coded edges**: Green (supports), Red (refutes), Gray (neutral)
- **Conflict nodes**: Yellow pulsing circles highlighting contradictions
- **Detail panel**: Click any node to see full information
- **Credibility indicators**: Node opacity reflects source credibility
- **Navigation**: Zoom, pan, fit view controls

## 🧪 Testing Coverage

### Property-Based Tests (27 properties)
```
✓ Workflow initialization and validation
✓ Scout source collection and diversity
✓ Mapper entity extraction completeness
✓ Adversary bias detection and iteration limits
✓ Judge credibility scoring consistency
✓ Synthesis report completeness
✓ Graph structure invariants
✓ Round-trip serialization
```

### Unit Tests
```
✓ API endpoint integration
✓ Error handling and recovery
✓ Configuration validation
✓ Component rendering
```

## 🚀 How to Run

### 1. Install Dependencies
```bash
pip install -r requirements.txt
cd frontend && npm install
```

### 2. Configure API Keys
Edit `.env`:
```bash
OPENAI_API_KEY=your_key_here
TAVILY_API_KEY=your_key_here
```

### 3. Start Backend
```bash
python -m uvicorn api.app:app --reload --port 8000
```

### 4. Start Frontend
```bash
cd frontend
npm start
```

### 5. Open Browser
- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs

## 📈 Performance Metrics

Typical workflow execution:
- Scout phase: ~30 seconds (10 sources)
- Mapper phase: ~15 seconds
- Adversary phase: ~10 seconds
- Judge phase: ~5 seconds
- Synthesis phase: ~20 seconds
- **Total: ~2 minutes per iteration**

## 🎓 Specification-Driven Development

This project was built using **spec-driven development**:

1. **Requirements** (`.kiro/specs/.../requirements.md`)
   - 8 user stories
   - 40+ EARS-compliant acceptance criteria
   - Glossary of terms

2. **Design** (`.kiro/specs/.../design.md`)
   - System architecture
   - Component interfaces
   - **27 correctness properties**
   - Testing strategy

3. **Tasks** (`.kiro/specs/.../tasks.md`)
   - 50+ implementation tasks
   - All tasks completed ✓
   - Property tests linked to requirements

## 🔍 Key Features Demonstrated

### 1. Multi-Agent Collaboration
Five specialized agents work together through LangGraph orchestration

### 2. Adversarial Reasoning
System actively challenges its own findings through iterative refinement

### 3. Credibility Weighting
Sophisticated scoring based on domain authority, citations, and recency

### 4. Conflict Detection
Automatically identifies and highlights contradictory claims

### 5. Interactive Visualization
React-based graph rendering with rich interactions

### 6. Property-Based Testing
27 universal properties tested with 100+ random inputs each

### 7. Production-Ready API
FastAPI with async support, session management, and documentation

## 📚 Documentation

- **README.md** - Complete project documentation
- **QUICKSTART.md** - Quick start guide
- **ARCHITECTURE.md** - System architecture details
- **EXAMPLES.md** - Usage examples
- **api/README.md** - API documentation
- **frontend/README.md** - Frontend documentation

## 🎯 Example Research Topics

Try these to see the system in action:

**Controversial Topics** (great for conflict detection):
- "Is coffee good or bad for health?"
- "Nuclear energy safety and environmental impact"
- "Cryptocurrency as investment vs speculation"

**Technical Topics** (great for credibility scoring):
- "Time complexity of quicksort algorithm"
- "Quantum computing practical applications"

**Current Events** (great for recency scoring):
- "Latest developments in renewable energy"
- "Recent advances in cancer treatment"

## 💡 What Makes This Special

1. **Not just summarization** - Actively seeks contradictions
2. **Credibility-aware** - Weights claims by source quality
3. **Iterative refinement** - Up to 3 adversarial cycles
4. **Visual argument maps** - See the topology of debates
5. **Property-tested** - 27 correctness guarantees
6. **Production-ready** - Full API, frontend, and tests

## 🎉 Project Status

**✅ FULLY IMPLEMENTED AND TESTED**

All 50+ tasks from the specification have been completed:
- ✅ All agents implemented
- ✅ API fully functional
- ✅ Frontend visualization complete
- ✅ 27 property-based tests passing
- ✅ Unit tests passing
- ✅ Integration tests passing
- ✅ Documentation complete

---

**Ready to explore conflicting viewpoints and build argument topology maps!** 🚀
