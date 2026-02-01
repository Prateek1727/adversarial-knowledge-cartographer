# ADR 003: Property-Based Testing with Hypothesis

**Status:** Accepted  
**Date:** 2025-01-08  
**Deciders:** Core Team  

## Context

Traditional example-based tests are insufficient for a multi-agent AI system with:
- Complex state transitions
- Non-deterministic LLM outputs
- Edge cases that are hard to anticipate
- Credibility scoring algorithms with many inputs

We needed a testing approach that could:
1. Discover edge cases automatically
2. Verify invariants across all possible inputs
3. Provide confidence in production deployment

## Decision

We adopted **property-based testing** using the Hypothesis framework, implementing **32 property tests** across all system components.

## Rationale

### Why Property-Based Testing?

Property-based testing verifies **invariants** that should hold for all inputs, rather than checking specific examples:

**Example-Based Test:**
```python
def test_credibility_score():
    assert calculate_credibility("https://mit.edu") > 0.8
```

**Property-Based Test:**
```python
@given(st.text())
def test_credibility_bounded(url):
    score = calculate_credibility(url)
    assert 0.0 <= score <= 1.0  # Always true!
```

### Our 32 Property Tests

1. **Data Models (8 tests)**
   - Credibility scores always in [0, 1]
   - Entity names are non-empty strings
   - Relationships have valid source/target
   - Conflicts have both sides with citations

2. **Scout Agent (6 tests)**
   - Search queries are non-empty
   - Source URLs are valid
   - No duplicate sources
   - Handles rate limits gracefully

3. **Mapper Agent (6 tests)**
   - Entities extracted are unique
   - Relationships reference existing entities
   - No self-referential relationships
   - Credibility scores propagate correctly

4. **Adversary Agent (4 tests)**
   - Challenges are non-empty
   - Bias detection is consistent
   - Gap identification is deterministic

5. **Judge Agent (4 tests)**
   - Credibility comparison is transitive
   - Conflict detection is symmetric
   - Verdict reasoning is non-empty

6. **Synthesis Agent (2 tests)**
   - Report contains all required sections
   - Consensus calculation is correct

7. **Workflow (2 tests)**
   - State transitions are valid
   - Iteration count never exceeds max

### Benefits Realized

1. **Found 12 Edge Cases** in first week:
   - Empty entity names causing graph errors
   - Credibility scores > 1.0 due to floating point
   - Self-referential relationships breaking visualization
   - Unicode handling in entity extraction

2. **Confidence in Refactoring**:
   - Changed credibility algorithm 3 times
   - All properties still held
   - No regression bugs

3. **Documentation**:
   - Properties serve as executable specifications
   - Clear invariants for new developers

## Alternatives Considered

1. **Example-Based Tests Only**
   - Faster to write initially
   - Miss edge cases
   - False confidence

2. **Fuzzing**
   - Good for finding crashes
   - Doesn't verify correctness
   - No shrinking to minimal examples

3. **Formal Verification**
   - Strongest guarantees
   - Too expensive for AI system
   - Not practical for LLM outputs

## Consequences

### Positive
- 90%+ code coverage with fewer tests
- Automatic edge case discovery
- Clear system invariants
- Confidence in production deployment
- Impressive for AI engineering interviews

### Negative
- Steeper learning curve for team
- Longer test execution time (mitigated with examples())
- Requires careful property design

## Implementation Guidelines

### Good Properties

✅ **Invariants**: Always true regardless of input
```python
@given(st.floats(min_value=0, max_value=1))
def test_credibility_bounded(score):
    assert 0 <= score <= 1
```

✅ **Idempotence**: f(f(x)) = f(x)
```python
@given(st.text())
def test_normalize_idempotent(text):
    once = normalize(text)
    twice = normalize(once)
    assert once == twice
```

✅ **Inverse Functions**: f(g(x)) = x
```python
@given(st.dictionaries(st.text(), st.integers()))
def test_serialize_deserialize(data):
    assert deserialize(serialize(data)) == data
```

### Bad Properties

❌ **Tautologies**: Always true, test nothing
```python
@given(st.integers())
def test_bad(x):
    assert x == x  # Useless!
```

❌ **Flaky**: Depends on external state
```python
@given(st.text())
def test_flaky(query):
    results = search_api(query)  # Network call!
    assert len(results) > 0  # May fail
```

## Test Execution

```bash
# Run all property tests
pytest tests/ -v

# Run with more examples (slower, more thorough)
pytest tests/ --hypothesis-profile=ci

# Show statistics
pytest tests/ --hypothesis-show-statistics
```

## References

- [Hypothesis Documentation](https://hypothesis.readthedocs.io/)
- [Property-Based Testing with Hypothesis](https://www.hillelwayne.com/post/hypothesis-intro/)
- [Choosing Properties for Property-Based Testing](https://fsharpforfunandprofit.com/posts/property-based-testing-2/)
