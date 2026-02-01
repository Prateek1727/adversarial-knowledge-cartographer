# Contributing to Adversarial Knowledge Cartographer

Thank you for your interest in contributing! This document provides guidelines for contributing to this project.

## Code of Conduct

Be respectful, constructive, and professional in all interactions.

## Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+
- Git
- Docker (optional, for containerized development)

### Development Setup

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/adversarial-knowledge-cartographer.git
cd adversarial-knowledge-cartographer
```

2. **Set up Python environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Development dependencies
```

3. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your API keys
```

4. **Run tests**
```bash
pytest tests/ -v
```

5. **Start development server**
```bash
# Backend
python -m uvicorn api.app:app --reload

# Frontend (separate terminal)
cd frontend
npm install
npm start
```

## Development Workflow

### 1. Create a Branch
```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

### 2. Make Changes
- Write clean, documented code
- Follow existing code style
- Add tests for new functionality
- Update documentation as needed

### 3. Run Tests
```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_scout_properties.py -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html
```

### 4. Commit Changes
```bash
git add .
git commit -m "feat: add new feature"
# or
git commit -m "fix: resolve bug in mapper"
```

**Commit Message Format:**
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `test:` Test additions/changes
- `refactor:` Code refactoring
- `perf:` Performance improvements
- `chore:` Maintenance tasks

### 5. Push and Create Pull Request
```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub.

## Code Standards

### Python Code Style
- Follow PEP 8
- Use type hints for all function signatures
- Maximum line length: 100 characters
- Use docstrings for all public functions/classes

**Example:**
```python
def calculate_credibility(
    domain_authority: float,
    citation_score: float,
    recency: float
) -> float:
    """
    Calculate overall credibility score.
    
    Args:
        domain_authority: Domain authority score (0-1)
        citation_score: Citation indicators score (0-1)
        recency: Recency score (0-1)
        
    Returns:
        Overall credibility score (0-1)
    """
    return (domain_authority * 0.4 + 
            citation_score * 0.3 + 
            recency * 0.3)
```

### TypeScript/React Code Style
- Use functional components with hooks
- Use TypeScript for all new code
- Follow Airbnb style guide
- Use meaningful variable names

### Testing Requirements
- All new features must include tests
- Maintain 90%+ code coverage
- Use property-based tests for invariants
- Use unit tests for specific behaviors

**Property Test Example:**
```python
from hypothesis import given, strategies as st

@given(st.lists(st.text(), min_size=1))
def test_entity_deduplication_preserves_count(entities):
    """Property: Deduplication never increases entity count."""
    deduplicated = deduplicate_entities(entities)
    assert len(deduplicated) <= len(entities)
```

## Project Structure

```
adversarial-knowledge-cartographer/
├── agents/              # Agent implementations
│   ├── scout.py        # Source collection
│   ├── mapper.py       # Knowledge extraction
│   ├── adversary.py    # Conflict detection
│   ├── judge.py        # Credibility scoring
│   └── synthesis.py    # Report generation
├── models/             # Data models
├── utils/              # Utility functions
├── tests/              # Test suite
│   ├── test_*_properties.py  # Property-based tests
│   └── test_*.py            # Unit tests
├── api/                # FastAPI backend
├── frontend/           # React frontend
└── docs/               # Documentation
    └── adr/           # Architecture decisions
```

## Adding New Features

### 1. Agent Enhancements
When adding new agent capabilities:
1. Update agent class in `agents/`
2. Add property-based tests in `tests/`
3. Update workflow in `agents/workflow.py`
4. Document in agent docstring
5. Add ADR if architectural change

### 2. API Endpoints
When adding new endpoints:
1. Add route in `api/app.py`
2. Add request/response models
3. Add endpoint tests
4. Update Swagger documentation
5. Update API_REFERENCE_GUIDE.md

### 3. Frontend Components
When adding UI components:
1. Create component in `frontend/src/components/`
2. Add TypeScript types
3. Add component tests
4. Update parent components
5. Add to Storybook (if applicable)

## Testing Guidelines

### Property-Based Tests
Use for testing invariants and general behaviors:
- Entity deduplication properties
- Credibility score bounds (0-1)
- Knowledge graph referential integrity
- Conflict detection completeness

### Unit Tests
Use for testing specific scenarios:
- API endpoint responses
- Error handling
- Edge cases
- Integration points

### Running Tests
```bash
# All tests
pytest tests/ -v

# Specific category
pytest tests/test_scout_properties.py -v
pytest tests/test_mapper_properties.py -v

# With coverage
pytest tests/ --cov=. --cov-report=html

# Fast tests only (skip slow property tests)
pytest tests/ -m "not slow"
```

## Documentation

### Code Documentation
- All public functions need docstrings
- Use Google-style docstrings
- Include type hints
- Provide examples for complex functions

### Architecture Decisions
When making significant architectural changes:
1. Create ADR in `docs/adr/`
2. Use template: `docs/adr/000-template.md`
3. Number sequentially
4. Include: Context, Decision, Rationale, Consequences

### README Updates
Update README.md when:
- Adding new features
- Changing setup process
- Updating dependencies
- Modifying architecture

## Pull Request Process

### Before Submitting
- [ ] All tests pass locally
- [ ] Code follows style guidelines
- [ ] New tests added for new features
- [ ] Documentation updated
- [ ] Commit messages follow format
- [ ] Branch is up to date with main

### PR Description Template
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Property tests added/updated
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests pass locally
```

### Review Process
1. Automated CI checks must pass
2. At least one maintainer approval required
3. Address all review comments
4. Squash commits before merge (if requested)

## Performance Guidelines

### Agent Optimization
- Minimize LLM calls (expensive)
- Cache repeated queries
- Use smaller models when possible
- Implement rate limiting

### API Performance
- Use async/await for I/O operations
- Implement request caching
- Add pagination for large responses
- Monitor response times

## Security Guidelines

### API Keys
- Never commit API keys
- Use environment variables
- Add `.env` to `.gitignore`
- Rotate keys if exposed

### Input Validation
- Validate all user inputs
- Sanitize before LLM calls
- Implement rate limiting
- Add CORS restrictions

### Dependencies
- Keep dependencies updated
- Run security audits: `pip-audit`
- Review dependency licenses
- Pin versions in requirements.txt

## Getting Help

### Resources
- **Documentation:** `/docs` folder
- **API Reference:** `API_REFERENCE_GUIDE.md`
- **Architecture:** `ARCHITECTURE.md`
- **Examples:** `EXAMPLES.md`

### Communication
- **Issues:** GitHub Issues for bugs/features
- **Discussions:** GitHub Discussions for questions
- **Email:** [your-email] for security issues

## Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Credited in documentation

Thank you for contributing to making AI research more reliable and transparent!
