# Project Structure

## Directory Layout

```
adversarial-knowledge-cartographer/
│
├── .kiro/                          # Kiro spec files
│   └── specs/
│       └── adversarial-knowledge-cartographer/
│           ├── requirements.md     # EARS-compliant requirements
│           ├── design.md          # Design document with correctness properties
│           └── tasks.md           # Implementation task list
│
├── agents/                        # Agent implementations
│   └── __init__.py
│   # Future: scout.py, mapper.py, adversary.py, judge.py, synthesis.py
│
├── models/                        # Pydantic data models
│   └── __init__.py
│   # Future: state.py, graph.py, source.py, credibility.py
│
├── utils/                         # Utility functions
│   └── __init__.py
│   # Future: search.py, extraction.py, logging.py
│
├── tests/                         # Test suite
│   ├── __init__.py
│   └── test_config.py            # Configuration tests
│   # Future: test_agents/, test_models/, test_properties/
│
├── config.py                      # Configuration management
├── main.py                        # Application entry point
├── requirements.txt               # Python dependencies
├── setup.py                       # Package setup script
├── pytest.ini                     # Pytest configuration
│
├── .env.example                   # Example environment variables
├── .gitignore                     # Git ignore rules
│
├── README.md                      # Main documentation
├── QUICKSTART.md                  # Quick start guide
└── PROJECT_STRUCTURE.md           # This file
```

## Key Files

### Configuration Files

- **config.py**: Central configuration management using Pydantic models
  - Loads from environment variables
  - Validates API keys and settings
  - Provides type-safe configuration access

- **.env.example**: Template for environment variables
  - Documents all configuration options
  - Copy to `.env` and fill in your API keys

- **pytest.ini**: Pytest configuration
  - Test discovery patterns
  - Markers for different test types
  - Output formatting

### Setup Files

- **requirements.txt**: Python package dependencies
  - Core: LangGraph, LangChain, Pydantic, FastAPI
  - Search: httpx, beautifulsoup4, trafilatura
  - Testing: pytest, hypothesis, pytest-mock

- **setup.py**: Package installation script
  - Enables `pip install -e .` for development
  - Defines package metadata

- **setup.bat / setup.sh**: Automated setup scripts
  - Creates virtual environment
  - Installs dependencies
  - Platform-specific (Windows/Unix)

### Documentation Files

- **README.md**: Main project documentation
  - Overview and features
  - Installation instructions
  - Usage examples

- **QUICKSTART.md**: Quick start guide
  - Step-by-step setup
  - Configuration examples
  - Troubleshooting tips

## Module Organization

### agents/
Will contain specialized agent implementations:
- `scout.py`: Web search and source collection
- `mapper.py`: Entity and relationship extraction
- `adversary.py`: Counter-evidence generation
- `judge.py`: Credibility evaluation
- `synthesis.py`: Report generation

### models/
Will contain Pydantic data models:
- `state.py`: WorkflowState and related models
- `graph.py`: KnowledgeGraph, Relationship, Conflict
- `source.py`: Source and content models
- `credibility.py`: CredibilityScore models

### utils/
Will contain utility functions:
- `search.py`: Search API integrations (Tavily, Serper)
- `extraction.py`: Content extraction (Trafilatura, BeautifulSoup)
- `logging.py`: Structured logging utilities

### tests/
Will contain test suites:
- `test_config.py`: Configuration tests (✓ implemented)
- `test_agents/`: Agent-specific tests
- `test_models/`: Data model tests
- `test_properties/`: Property-based tests
- `test_integration/`: End-to-end tests

## Development Workflow

1. **Setup**: Run `setup.bat` (Windows) or `setup.sh` (Unix)
2. **Configure**: Copy `.env.example` to `.env` and add API keys
3. **Develop**: Implement tasks from `.kiro/specs/adversarial-knowledge-cartographer/tasks.md`
4. **Test**: Run `pytest` to verify implementation
5. **Iterate**: Follow the task list sequentially

## Testing Strategy

### Unit Tests
- Test individual functions and classes
- Mock external dependencies
- Fast execution

### Property-Based Tests
- Test universal properties using Hypothesis
- Generate random inputs
- Verify correctness properties from design doc
- Minimum 100 iterations per property

### Integration Tests
- Test complete workflows
- Use real or realistic data
- Verify agent interactions

## Next Steps

Follow the implementation plan in `.kiro/specs/adversarial-knowledge-cartographer/tasks.md`:

1. ✓ Set up project structure and dependencies (COMPLETE)
2. Implement core data models
3. Implement workflow orchestration with LangGraph
4. Implement Scout Agent
5. Implement Mapper Agent
6. Implement Adversary Agent
7. Implement Judge Agent
8. Implement Synthesis Agent
9. Implement visualization frontend
10. Create documentation and examples
