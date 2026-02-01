# ADR 002: Credibility Scoring Algorithm

**Status:** Accepted  
**Date:** 2025-01-08  
**Deciders:** Core Team  

## Context

Research quality depends heavily on source credibility. We needed a systematic way to score sources based on:
- Domain authority (e.g., .edu, .gov, established news outlets)
- Citation indicators (references, footnotes, bibliography)
- Recency (newer sources for current topics)

## Decision

We implemented a **weighted composite credibility score** with three components:

```
credibility = (domain_weight × domain_score) + 
              (citation_weight × citation_score) + 
              (recency_weight × recency_score)
```

Default weights: `domain=0.4, citation=0.3, recency=0.3`

## Rationale

### Domain Authority (40%)

High-credibility domains:
- `.edu` (universities): 0.9
- `.gov` (government): 0.9
- Established news (NYT, BBC, Reuters): 0.8
- Academic publishers (Nature, Science): 0.9
- Think tanks (Brookings, RAND): 0.7

Medium-credibility:
- `.org` (non-profits): 0.6
- Industry publications: 0.6
- Professional blogs: 0.5

Low-credibility:
- Personal blogs: 0.3
- Social media: 0.2
- Unknown domains: 0.4

### Citation Indicators (30%)

Presence of:
- References section: +0.3
- Footnotes: +0.2
- Bibliography: +0.2
- DOI/ISBN: +0.3

### Recency (30%)

Age-based decay:
- < 1 year: 1.0
- 1-2 years: 0.8
- 2-5 years: 0.6
- 5-10 years: 0.4
- > 10 years: 0.2

## Alternatives Considered

1. **Binary Credibility (trusted/untrusted)**
   - Too simplistic, loses nuance
   - Doesn't account for context

2. **ML-Based Scoring**
   - Requires training data
   - Black box, hard to explain
   - Overkill for current needs

3. **PageRank-Style Algorithm**
   - Requires link graph
   - Computationally expensive
   - Not suitable for real-time research

## Consequences

### Positive
- Transparent, explainable scoring
- Configurable weights for different domains
- Fast computation (no external APIs)
- Works well for financial, scientific, and general topics

### Negative
- Manual domain classification required
- May miss emerging credible sources
- Recency bias may undervalue historical context

## Configuration

Users can adjust weights in `.env`:

```bash
DOMAIN_WEIGHT=0.4
CITATION_WEIGHT=0.3
RECENCY_WEIGHT=0.3
```

For financial analysis, increase domain weight:
```bash
DOMAIN_WEIGHT=0.5
CITATION_WEIGHT=0.3
RECENCY_WEIGHT=0.2
```

## Future Improvements

1. Add citation count from Google Scholar
2. Implement domain reputation API (e.g., NewsGuard)
3. Add peer review indicators
4. Context-aware scoring (topic-specific weights)

## References

- [Evaluating Information Sources](https://guides.library.cornell.edu/evaluate)
- [CRAAP Test for Source Evaluation](https://library.csuchico.edu/help/source-or-information-good)
