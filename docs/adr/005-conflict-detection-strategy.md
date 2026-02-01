# ADR 005: Conflict Detection Strategy

**Status:** Accepted  
**Date:** 2025-01-08  
**Deciders:** Core Team  

## Context

The Adversarial Knowledge Cartographer's core value proposition is identifying **conflicting claims** in research. We needed a strategy to:

1. Detect contradictions between sources
2. Represent conflicts in the knowledge graph
3. Evaluate which side is more credible
4. Present conflicts clearly to users

## Decision

We implemented a **multi-stage conflict detection pipeline**:

1. **Adversary Agent**: Identifies potential conflicts using LLM analysis
2. **Judge Agent**: Evaluates credibility of conflicting claims
3. **Conflict Nodes**: Represent conflicts as first-class entities in the graph
4. **Synthesis**: Presents conflicts as "battleground topics" in the report

## Rationale

### Stage 1: Adversary Detection

The Adversary agent analyzes the knowledge graph and identifies:

- **Direct Contradictions**: "X causes Y" vs "X prevents Y"
- **Quantitative Disagreements**: "10% increase" vs "5% decrease"
- **Methodological Conflicts**: Different study designs, conflicting results
- **Temporal Conflicts**: Claims that contradict over time

**Prompt Strategy:**
```python
prompt = f"""
Analyze this knowledge graph for conflicts:

Entities: {entities}
Relationships: {relationships}

Identify:
1. Direct contradictions between claims
2. Quantitative disagreements
3. Methodological conflicts
4. Missing perspectives

For each conflict, provide:
- Point of contention
- Side A claim + citation
- Side B claim + citation
"""
```

### Stage 2: Judge Evaluation

The Judge agent evaluates conflicts using:

1. **Source Credibility**: Compare credibility scores
2. **Evidence Quality**: Assess citation strength
3. **Consensus**: Check if one side has more sources
4. **Recency**: Consider if newer research supersedes older

**Credibility Comparison:**
```python
def evaluate_conflict(conflict):
    if conflict.side_a_credibility > conflict.side_b_credibility + 0.2:
        return "Side A more credible"
    elif conflict.side_b_credibility > conflict.side_a_credibility + 0.2:
        return "Side B more credible"
    else:
        return "Insufficient evidence to determine"
```

### Stage 3: Graph Representation

Conflicts are represented as **special nodes** in the knowledge graph:

```python
class Conflict(BaseModel):
    point_of_contention: str
    side_a: str
    side_a_citation: str
    side_a_credibility: float
    side_b: str
    side_b_citation: str
    side_b_credibility: float
```

**Visualization:**
- Conflict nodes are red/orange
- Connected to related entities
- Show credibility scores on hover

### Stage 4: Synthesis Presentation

The Synthesis agent presents conflicts as:

1. **Consensus Points**: Claims with >90% agreement
2. **Battleground Topics**: Major conflicts with analysis
3. **The Verdict**: Judge's assessment with reasoning

**Example Output:**
```markdown
## The Battleground

### Topic: Silver ETF vs Physical Silver

**Side A** (Credibility: 0.75)
"Silver ETFs offer superior liquidity and lower storage costs"
Source: Investopedia

**Side B** (Credibility: 0.68)
"Physical silver provides tangible ownership and no counterparty risk"
Source: APMEX

**The Verdict**: Side A slightly more credible due to higher source authority,
but both perspectives have merit depending on investor priorities.
```

## Alternatives Considered

### 1. Semantic Similarity Approach

**Idea**: Use embeddings to find contradictory statements

**Pros:**
- Automatic, no manual rules
- Scales to large graphs

**Cons:**
- Misses nuanced conflicts
- High false positive rate
- Requires embedding API ($$$)

**Verdict**: Too simplistic for research quality

### 2. Rule-Based NLP

**Idea**: Use spaCy/NLTK to detect negations and contradictions

**Pros:**
- Fast, deterministic
- No LLM calls

**Cons:**
- Brittle, misses context
- Requires extensive rule engineering
- Poor handling of implicit conflicts

**Verdict**: Not robust enough

### 3. Human-in-the-Loop

**Idea**: Flag potential conflicts, let users decide

**Pros:**
- Highest accuracy
- No false positives

**Cons:**
- Not scalable
- Defeats automation purpose
- Slow

**Verdict**: Good for validation, not primary strategy

## Consequences

### Positive
- Identifies conflicts GPT-4 alone misses
- Clear presentation of disagreements
- Credibility-weighted evaluation
- Unique value proposition

### Negative
- Requires 2 extra LLM calls (Adversary + Judge)
- May miss subtle conflicts
- Credibility scoring can be subjective

## Conflict Detection Metrics

We track:

```python
class ConflictMetrics:
    total_conflicts: int
    conflicts_per_iteration: List[int]
    avg_credibility_gap: float
    resolution_rate: float  # % with clear verdict
```

**Good Research Session:**
- 3-10 conflicts identified
- Avg credibility gap > 0.15
- Resolution rate > 60%

**Poor Research Session:**
- 0-1 conflicts (too shallow)
- Avg credibility gap < 0.05 (no clear winner)
- Resolution rate < 30% (inconclusive)

## Future Improvements

1. **Conflict Clustering**: Group related conflicts
2. **Temporal Analysis**: Track how conflicts evolve over time
3. **Expert Weighting**: Give more weight to domain experts
4. **Conflict Visualization**: Interactive conflict explorer
5. **Meta-Analysis**: Synthesize across multiple conflicts

## Example: Silver ETF Analysis

**Original Problem**: Only 1 conflict detected, both sides 0.54 credibility

**Root Cause**: 
- Too few sources (10)
- No domain-specific credibility weighting
- Shallow entity extraction

**Solution**:
- Increase `MIN_SOURCES=30`
- Adjust `DOMAIN_WEIGHT=0.5` for financial topics
- Add financial domain authority list

**Expected Result**:
- 5-8 conflicts
- Credibility range: 0.4-0.9
- Clear winners on most conflicts

## References

- [Contradiction Detection in NLP](https://arxiv.org/abs/1909.00428)
- [Fact-Checking with Knowledge Graphs](https://arxiv.org/abs/2010.03070)
- [Credibility Assessment in Information Retrieval](https://dl.acm.org/doi/10.1145/3331184.3331248)
