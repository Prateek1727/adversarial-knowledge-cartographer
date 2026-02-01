# Core Algorithms Explained - Adversarial Knowledge Cartographer

> A detailed code-level explanation of the main algorithms used in the system

---

## Table of Contents

1. [Overview](#overview)
2. [Credibility Scoring Algorithm](#credibility-scoring-algorithm)
3. [Entity Deduplication Algorithm](#entity-deduplication-algorithm)
4. [Conflict Detection Algorithm](#conflict-detection-algorithm)
5. [Adversarial Query Generation](#adversarial-query-generation)
6. [Knowledge Graph Construction](#knowledge-graph-construction)
7. [Consensus Identification](#consensus-identification)
8. [Workflow Orchestration](#workflow-orchestration)

---

## Overview

This document explains the core algorithms that power the Adversarial Knowledge Cartographer. Each section includes:
- Algorithm purpose and context
- Step-by-step explanation
- Code walkthrough with comments
- Example inputs and outputs
- Time and space complexity

---

## Credibility Scoring Algorithm

### Purpose
Evaluate the trustworthiness of sources using a transparent, configurable scoring system.

### Location
`agents/judge.py` - `JudgeAgent` class

### Algorithm Steps

The credibility score is calculated using three weighted components:

```
Overall Score = (Domain Authority × 0.4) + (Citation Indicators × 0.3) + (Recency × 0.3)
```

#### Step 1: Domain Authority Scoring

**Purpose**: Evaluate source based on domain type and reputation

**Rules**:
- `.edu` and `.gov` domains: 1.0 (highest trust)
- `.org` domains: 0.8 (high trust)
- Recognized journals (nature.com, science.org): 0.95
- News outlets (bbc.com, reuters.com): 0.75
- `.com` domains: 0.6 (moderate trust)
- Unknown domains: 0.5 (low trust)


**Code Walkthrough**:

```python
def _calculate_domain_authority(self, url: str) -> float:
    """Calculate domain authority score based on URL."""
    parsed = urlparse(url)
    domain = parsed.netloc.lower()
    
    # Remove 'www.' prefix
    if domain.startswith('www.'):
        domain = domain[4:]
    
    # Check specific high-authority domains
    if domain in self.HIGH_AUTHORITY_DOMAINS:
        return self.HIGH_AUTHORITY_DOMAINS[domain]  # e.g., 0.95 for nature.com
    
    # Check TLD-based scoring
    for tld, score in self.DOMAIN_AUTHORITY_SCORES.items():
        if domain.endswith(tld):
            return score  # e.g., 1.0 for .edu
    
    # Default scoring
    if domain.endswith('.com'):
        return 0.6
    
    return 0.5  # Unknown domains
```

**Example**:
```python
Input:  "https://www.harvard.edu/study"
Output: 1.0 (educational domain)

Input:  "https://nature.com/article"
Output: 0.95 (recognized journal)

Input:  "https://randomsite.com/blog"
Output: 0.6 (commercial domain)
```

**Complexity**: O(1) - constant time lookup

---

#### Step 2: Citation Indicators Scoring

**Purpose**: Assess academic rigor based on content analysis

**Rules**:
- References section present: +0.3
- Academic citation formatting ([1], (2023)): +0.2
- Author credentials (Dr., PhD, Professor): +0.3
- Maximum score: 1.0

**Code Walkthrough**:

```python
def _assess_citation_indicators(self, content: str) -> float:
    """Assess citation indicators in source content."""
    score = 0.0
    content_lower = content.lower()
    
    # Check for references section
    references_patterns = [
        r'\breferences\b',
        r'\bbibliography\b',
        r'\bworks cited\b'
    ]
    
    for pattern in references_patterns:
        if re.search(pattern, content_lower):
            score += 0.3  # Found references section
            break
    
    # Check for academic formatting
    citation_patterns = [
        r'\[\d+\]',           # [1], [2], etc.
        r'\(\d{4}\)',         # (2023), (2024)
        r'\[[\w\s]+,\s*\d{4}\]'  # [Author, 2023]
    ]
    
    for pattern in citation_patterns:
        if re.search(pattern, content):
            score += 0.2  # Found citation formatting
            break
    
    # Check for author credentials
    credential_patterns = [
        r'\bdr\.\s+\w+',
        r'\bphd\b',
        r'\bprofessor\b'
    ]
    
    for pattern in credential_patterns:
        if re.search(pattern, content_lower):
            score += 0.3  # Found credentials
            break
    
    return min(score, 1.0)  # Cap at 1.0
```

**Example**:
```python
Input:  "Study by Dr. Smith. References: [1] Nature 2023..."
Output: 0.8 (credentials + references + citations)

Input:  "Blog post about health..."
Output: 0.0 (no indicators)
```

**Complexity**: O(n) where n = content length (regex scanning)

---


#### Step 3: Recency Scoring

**Purpose**: Favor more recent information

**Rules**:
- Less than 1 year old: 1.0
- 1-2 years old: 0.8
- 2-5 years old: 0.5
- More than 5 years old: 0.3

**Code Walkthrough**:

```python
def _calculate_recency_score(self, retrieved_at: datetime) -> float:
    """Calculate recency score based on publication date."""
    now = datetime.now()
    age_days = (now - retrieved_at).days
    age_years = age_days / 365.25
    
    if age_years < 1:
        return 1.0
    elif age_years < 2:
        return 0.8
    elif age_years < 5:
        return 0.5
    else:
        return 0.3
```

**Example**:
```python
Input:  retrieved_at = "2025-01-01" (current year)
Output: 1.0 (very recent)

Input:  retrieved_at = "2020-01-01" (5 years ago)
Output: 0.3 (outdated)
```

**Complexity**: O(1) - simple date arithmetic

---

#### Step 4: Weighted Overall Score

**Purpose**: Combine all components into final credibility score

**Formula**:
```
Overall = (Domain × 0.4) + (Citations × 0.3) + (Recency × 0.3)
```

**Code Walkthrough**:

```python
def _calculate_overall_score(
    self,
    domain_authority: float,
    citation_indicators: float,
    recency: float
) -> float:
    """Calculate weighted overall credibility score."""
    overall = (
        domain_authority * 0.4 +      # 40% weight
        citation_indicators * 0.3 +   # 30% weight
        recency * 0.3                 # 30% weight
    )
    
    # Ensure score is within bounds [0.0, 1.0]
    return max(0.0, min(1.0, overall))
```

**Complete Example**:

```python
# Harvard study from 2024 with references
domain_authority = 1.0      # .edu domain
citation_indicators = 0.8   # Has references and citations
recency = 1.0               # Published this year

overall = (1.0 × 0.4) + (0.8 × 0.3) + (1.0 × 0.3)
        = 0.4 + 0.24 + 0.3
        = 0.94  # Very high credibility

# Blog post from 2020 with no citations
domain_authority = 0.6      # .com domain
citation_indicators = 0.0   # No academic indicators
recency = 0.3               # 5 years old

overall = (0.6 × 0.4) + (0.0 × 0.3) + (0.3 × 0.3)
        = 0.24 + 0.0 + 0.09
        = 0.33  # Low credibility
```

**Complexity**: O(1) - simple arithmetic

**Total Credibility Algorithm Complexity**: O(n) where n = content length

---

## Entity Deduplication Algorithm

### Purpose
Remove duplicate entities using fuzzy string matching to handle variations in naming.

### Location
`agents/mapper.py` - `MapperAgent._deduplicate_entities()`

### Algorithm Steps

Uses **Sequence Matcher** algorithm to find similar entity names.

#### Step 1: Similarity Calculation

**Purpose**: Calculate how similar two strings are

**Algorithm**: Longest Common Subsequence (LCS) ratio

**Code Walkthrough**:

```python
from difflib import SequenceMatcher

def _calculate_similarity(self, str1: str, str2: str) -> float:
    """Calculate similarity between two strings."""
    # SequenceMatcher uses Ratcliff/Obershelp algorithm
    # Returns ratio of matching characters to total characters
    return SequenceMatcher(None, str1.lower(), str2.lower()).ratio()
```

**Example**:
```python
Input:  "Coffee", "coffee"
Output: 1.0 (exact match, case-insensitive)

Input:  "Coffee", "Caffeine"
Output: 0.57 (some similarity)

Input:  "Coffee", "Tea"
Output: 0.0 (no similarity)
```

**Complexity**: O(m × n) where m, n = string lengths

---


#### Step 2: Deduplication Process

**Purpose**: Keep only unique entities, merging similar ones

**Threshold**: 0.85 (85% similarity required to consider duplicates)

**Code Walkthrough**:

```python
def _deduplicate_entities(self, entities: List[str]) -> List[str]:
    """Deduplicate entities using fuzzy matching."""
    if not entities:
        return []
    
    unique_entities = []
    
    for entity in entities:
        entity = entity.strip()
        if not entity:
            continue
        
        # Check if similar to any existing unique entity
        is_duplicate = False
        for unique_entity in unique_entities:
            similarity = self._calculate_similarity(entity, unique_entity)
            
            if similarity >= 0.85:  # 85% threshold
                # This is a duplicate, skip it
                is_duplicate = True
                break
        
        if not is_duplicate:
            unique_entities.append(entity)
    
    return unique_entities
```

**Step-by-Step Example**:

```python
Input entities: ["Coffee", "coffee", "Caffeine", "Heart Health", "Heart health"]

Step 1: Process "Coffee"
  - unique_entities = []
  - No existing entities to compare
  - Add "Coffee"
  - unique_entities = ["Coffee"]

Step 2: Process "coffee"
  - Compare with "Coffee": similarity = 1.0 (≥ 0.85)
  - Is duplicate! Skip it
  - unique_entities = ["Coffee"]

Step 3: Process "Caffeine"
  - Compare with "Coffee": similarity = 0.57 (< 0.85)
  - Not duplicate, add it
  - unique_entities = ["Coffee", "Caffeine"]

Step 4: Process "Heart Health"
  - Compare with "Coffee": similarity = 0.0 (< 0.85)
  - Compare with "Caffeine": similarity = 0.0 (< 0.85)
  - Not duplicate, add it
  - unique_entities = ["Coffee", "Caffeine", "Heart Health"]

Step 5: Process "Heart health"
  - Compare with "Coffee": similarity = 0.0 (< 0.85)
  - Compare with "Caffeine": similarity = 0.0 (< 0.85)
  - Compare with "Heart Health": similarity = 0.96 (≥ 0.85)
  - Is duplicate! Skip it
  - unique_entities = ["Coffee", "Caffeine", "Heart Health"]

Output: ["Coffee", "Caffeine", "Heart Health"]
```

**Complexity**: O(n² × m) where:
- n = number of entities
- m = average entity name length

**Optimization Note**: For large entity lists (>1000), consider using:
- Locality-Sensitive Hashing (LSH)
- BK-trees for approximate string matching
- Current implementation is sufficient for typical use (50-200 entities)

---

## Conflict Detection Algorithm

### Purpose
Identify contradictory claims between sources in the knowledge graph.

### Location
`agents/mapper.py` - Extracted by LLM, validated in `MapperAgent`

### Algorithm Overview

The conflict detection uses a **two-phase approach**:
1. **LLM-based extraction**: AI identifies contradictions in source content
2. **Validation**: Ensure conflicts reference valid sources

### Phase 1: LLM Extraction

**Prompt Strategy**:

```python
prompt = f"""
Extract conflicts where sources disagree about "{topic}".

For each conflict, identify:
1. Point of contention (what they disagree about)
2. Side A: First viewpoint with evidence
3. Side B: Opposing viewpoint with evidence
4. Citations for both sides

Output Format:
{{
  "conflicts": [
    {{
      "point_of_contention": "Effect on heart health",
      "side_a": "Coffee reduces cardiovascular disease risk",
      "side_a_citation": "https://harvard.edu/study",
      "side_b": "Coffee increases heart palpitations",
      "side_b_citation": "https://blog.com/article"
    }}
  ]
}}
"""
```

**Example LLM Output**:

```json
{
  "conflicts": [
    {
      "point_of_contention": "Effect of coffee on heart health",
      "side_a": "Coffee consumption reduces risk of cardiovascular disease by 15%",
      "side_a_citation": "https://harvard.edu/coffee-study-2024",
      "side_b": "Coffee increases heart palpitations and blood pressure",
      "side_b_citation": "https://healthblog.com/coffee-risks"
    }
  ]
}
```

---


### Phase 2: Validation and Credibility Annotation

**Purpose**: Validate citations and add credibility scores

**Code Walkthrough**:

```python
def _extract_conflicts(self, conflicts_data: List[dict]) -> List[Conflict]:
    """Extract and validate conflicts from LLM response."""
    conflicts = []
    
    for conflict_data in conflicts_data:
        # Validate required fields
        required_fields = [
            'point_of_contention',
            'side_a',
            'side_a_citation',
            'side_b',
            'side_b_citation'
        ]
        
        if not all(key in conflict_data for key in required_fields):
            logger.warning(f"Conflict missing required fields")
            continue
        
        # Create Conflict object
        conflict = Conflict(
            point_of_contention=conflict_data['point_of_contention'],
            side_a=conflict_data['side_a'],
            side_a_citation=conflict_data['side_a_citation'],
            side_b=conflict_data['side_b'],
            side_b_citation=conflict_data['side_b_citation'],
            side_a_credibility=1.0,  # Will be updated by Judge
            side_b_credibility=1.0   # Will be updated by Judge
        )
        
        conflicts.append(conflict)
    
    return conflicts
```

**Complete Example**:

```python
# Input from LLM
conflict_data = {
    "point_of_contention": "Effect on heart health",
    "side_a": "Reduces cardiovascular disease risk",
    "side_a_citation": "https://harvard.edu/study",
    "side_b": "Increases heart palpitations",
    "side_b_citation": "https://blog.com/article"
}

# After Judge agent adds credibility scores
conflict = Conflict(
    point_of_contention="Effect on heart health",
    side_a="Reduces cardiovascular disease risk",
    side_a_citation="https://harvard.edu/study",
    side_a_credibility=0.95,  # High credibility (.edu)
    side_b="Increases heart palpitations",
    side_b_citation="https://blog.com/article",
    side_b_credibility=0.33   # Low credibility (blog)
)

# Verdict: Side A is more credible (0.95 > 0.33)
```

**Complexity**: O(c) where c = number of conflicts (typically 3-10)

---

## Adversarial Query Generation

### Purpose
Generate search queries designed to find counter-evidence and challenge current findings.

### Location
`agents/adversary.py` - `AdversaryAgent`

### Algorithm Steps

#### Step 1: Weakness Identification

**Three types of weaknesses**:

1. **Single-Source Claims**: Claims supported by only one source
2. **Outdated Sources**: Sources older than 2 years
3. **Bias Indicators**: Sources with potential bias

**Code Walkthrough**:

```python
def identify_single_source_claims(
    self,
    knowledge_graph: KnowledgeGraph
) -> List[Weakness]:
    """Identify claims that rely on only a single source."""
    weaknesses = []
    
    # Group relationships by claim
    claim_groups = {}
    
    for rel in knowledge_graph.relationships:
        # Create unique key for the claim
        claim_key = f"{rel.source}|{rel.relation}|{rel.target}"
        
        if claim_key not in claim_groups:
            claim_groups[claim_key] = []
        claim_groups[claim_key].append(rel)
    
    # Identify single-source relationships
    for claim_key, rels in claim_groups.items():
        if len(rels) == 1:  # Only one source supports this claim
            rel = rels[0]
            claim = f"{rel.source} {rel.relation} {rel.target}"
            
            weakness = Weakness(
                weakness_type="single_source",
                description=f"Claim relies on only one source: {rel.citation}",
                affected_claims=[claim]
            )
            weaknesses.append(weakness)
    
    return weaknesses
```

**Example**:

```python
# Knowledge Graph has these relationships:
relationships = [
    Relationship("Coffee", "reduces", "Heart Disease", citation="harvard.edu"),
    Relationship("Coffee", "contains", "Caffeine", citation="harvard.edu"),
    Relationship("Coffee", "contains", "Caffeine", citation="mayo.edu"),
    Relationship("Coffee", "improves", "Focus", citation="blog.com")
]

# Analysis:
# "Coffee reduces Heart Disease" - 1 source (WEAKNESS!)
# "Coffee contains Caffeine" - 2 sources (OK)
# "Coffee improves Focus" - 1 source (WEAKNESS!)

weaknesses = [
    Weakness("single_source", "Coffee reduces Heart Disease"),
    Weakness("single_source", "Coffee improves Focus")
]
```

**Complexity**: O(r) where r = number of relationships

---


#### Step 2: Counter-Query Generation

**Purpose**: Generate search queries to find evidence that contradicts weak claims

**Strategy**: Use LLM to generate adversarial queries based on identified weaknesses

**Code Walkthrough**:

```python
def generate_counter_queries(
    self,
    topic: str,
    knowledge_graph: KnowledgeGraph,
    weaknesses: List[Weakness]
) -> List[str]:
    """Generate adversarial search queries using LLM."""
    
    # Create prompt with current findings and weaknesses
    prompt = f"""
    Role: You are a Red-Teamer and Academic Skeptic.
    
    Current Findings on "{topic}":
    - Entities: {knowledge_graph.entities}
    - Key Claims: {knowledge_graph.relationships[:10]}
    
    Identified Weaknesses:
    {weaknesses}
    
    Task: Generate 3 aggressive search queries designed to debunk 
    the current findings.
    
    Example: If finding is "Coffee is good for health," 
    your query should be "Negative cardiovascular effects of daily caffeine intake."
    
    Output Format:
    {{
      "counter_queries": [
        "Query 1 designed to find counter-evidence",
        "Query 2 designed to find counter-evidence",
        "Query 3 designed to find counter-evidence"
      ]
    }}
    """
    
    # Call LLM
    response = self.llm.invoke(prompt)
    data = json.loads(response.content)
    
    return data["counter_queries"]
```

**Example**:

```python
# Input
topic = "Is coffee healthy?"
weaknesses = [
    Weakness("single_source", "Coffee reduces heart disease risk")
]

# LLM generates counter-queries
counter_queries = [
    "coffee cardiovascular disease risks long-term studies",
    "negative effects of caffeine on heart health",
    "coffee consumption and increased blood pressure research"
]

# These queries will be used in the next Scout iteration
# to find sources that challenge the current findings
```

**Complexity**: O(1) LLM call + O(w) where w = number of weaknesses

---

## Knowledge Graph Construction

### Purpose
Build a structured representation of knowledge with entities, relationships, and conflicts.

### Location
`agents/mapper.py` - `MapperAgent.build_knowledge_graph()`

### Algorithm Steps

#### Step 1: Entity Extraction

**Purpose**: Identify all concepts mentioned in sources

**Process**:
1. LLM extracts entities from source content
2. Deduplicate using fuzzy matching (see Entity Deduplication section)
3. Validate entity names are non-empty

**Code Walkthrough**:

```python
def build_knowledge_graph(
    self,
    topic: str,
    sources: List[Source]
) -> KnowledgeGraph:
    """Build a Knowledge Graph from sources."""
    
    # Step 1: Extract knowledge using LLM
    knowledge_data = self._extract_knowledge_with_retry(topic, sources)
    
    # Step 2: Extract and deduplicate entities
    raw_entities = knowledge_data.get('entities', [])
    unique_entities = self._deduplicate_entities(raw_entities)
    
    # Step 3: Extract relationships
    relationships_data = knowledge_data.get('relationships', [])
    relationships = self._extract_relationships(relationships_data, sources)
    
    # Step 4: Extract conflicts
    conflicts_data = knowledge_data.get('conflicts', [])
    conflicts = self._extract_conflicts(conflicts_data)
    
    # Step 5: Build Knowledge Graph
    knowledge_graph = KnowledgeGraph(
        entities=unique_entities,
        relationships=relationships,
        conflicts=conflicts
    )
    
    return knowledge_graph
```

---

#### Step 2: Relationship Extraction with Validation

**Purpose**: Extract connections between entities with citations

**Validation Rules**:
1. Both source and target entities must exist in entity list
2. Citation must reference a valid source URL
3. Relationship must have all required fields

**Code Walkthrough**:

```python
def _extract_relationships(
    self,
    relationships_data: List[dict],
    sources: List[Source]
) -> List[Relationship]:
    """Extract and validate relationships from LLM response."""
    relationships = []
    entity_names = set(self.unique_entities)
    
    for rel_data in relationships_data:
        # Validate required fields
        if not all(key in rel_data for key in ['source', 'relation', 'target', 'citation']):
            continue
        
        # Check if entities exist
        source_entity = rel_data['source']
        target_entity = rel_data['target']
        
        if source_entity not in entity_names:
            # Try fuzzy matching
            match = self._find_best_entity_match(source_entity, entity_names)
            if match:
                source_entity = match
            else:
                continue  # Skip invalid relationship
        
        if target_entity not in entity_names:
            # Try fuzzy matching
            match = self._find_best_entity_match(target_entity, entity_names)
            if match:
                target_entity = match
            else:
                continue  # Skip invalid relationship
        
        # Create Relationship object
        relationship = Relationship(
            source=source_entity,
            relation=rel_data['relation'],
            target=target_entity,
            citation=rel_data['citation'],
            credibility=1.0  # Will be updated by Judge
        )
        
        relationships.append(relationship)
    
    return relationships
```

**Example**:

```python
# LLM extracts relationships
relationships_data = [
    {
        "source": "Coffee",
        "relation": "contains",
        "target": "Caffeine",
        "citation": "https://harvard.edu/study"
    },
    {
        "source": "coffee",  # Different case
        "relation": "reduces",
        "target": "Heart Disease Risk",
        "citation": "https://mayo.edu/research"
    }
]

# Validation process
entities = ["Coffee", "Caffeine", "Heart Disease Risk"]

# Relationship 1: Valid
# - "Coffee" exists in entities ✓
# - "Caffeine" exists in entities ✓
# - Citation is valid ✓
# Result: ACCEPTED

# Relationship 2: Needs fuzzy matching
# - "coffee" not in entities, but fuzzy match to "Coffee" ✓
# - "Heart Disease Risk" exists in entities ✓
# - Citation is valid ✓
# Result: ACCEPTED (with "coffee" → "Coffee")

final_relationships = [
    Relationship("Coffee", "contains", "Caffeine", "harvard.edu", 1.0),
    Relationship("Coffee", "reduces", "Heart Disease Risk", "mayo.edu", 1.0)
]
```

**Complexity**: O(r × e) where:
- r = number of relationships
- e = number of entities

---


#### Step 3: Referential Integrity Validation

**Purpose**: Ensure all relationships reference valid entities

**Code Walkthrough**:

```python
def validate_referential_integrity(self):
    """Validate that all relationships reference valid entities."""
    entity_set = set(self.entities)
    
    for rel in self.relationships:
        if rel.source not in entity_set:
            raise ValueError(
                f"Relationship source '{rel.source}' not in entity list"
            )
        
        if rel.target not in entity_set:
            raise ValueError(
                f"Relationship target '{rel.target}' not in entity list"
            )
```

**Example**:

```python
# Valid Knowledge Graph
entities = ["Coffee", "Caffeine", "Health"]
relationships = [
    Relationship("Coffee", "contains", "Caffeine", ...),
    Relationship("Coffee", "affects", "Health", ...)
]
# Validation: PASS ✓

# Invalid Knowledge Graph
entities = ["Coffee", "Caffeine"]
relationships = [
    Relationship("Coffee", "affects", "Health", ...)  # "Health" not in entities!
]
# Validation: FAIL ✗
# Error: "Relationship target 'Health' not in entity list"
```

**Complexity**: O(r) where r = number of relationships

---

## Consensus Identification

### Purpose
Identify claims where 90%+ of sources agree, indicating strong consensus.

### Location
`agents/synthesis.py` - `SynthesisAgent.identify_consensus()`

### Algorithm Steps

#### Step 1: Group Relationships by Claim

**Purpose**: Find all sources that support each claim

**Code Walkthrough**:

```python
def identify_consensus(
    self,
    knowledge_graph: KnowledgeGraph
) -> List[str]:
    """Identify consensus points where 90%+ of sources agree."""
    consensus_points = []
    
    # Group relationships by claim (source-relation-target)
    claim_groups = {}
    
    for rel in knowledge_graph.relationships:
        # Create unique key for the claim
        claim_key = f"{rel.source}|{rel.relation}|{rel.target}"
        
        if claim_key not in claim_groups:
            claim_groups[claim_key] = []
        claim_groups[claim_key].append(rel)
    
    # Calculate total number of unique sources
    total_sources = len(set(rel.citation for rel in knowledge_graph.relationships))
    
    # Identify claims with high agreement
    for claim_key, rels in claim_groups.items():
        # Count unique sources supporting this claim
        num_supporting_sources = len(set(rel.citation for rel in rels))
        
        # Calculate support ratio
        support_ratio = num_supporting_sources / total_sources
        
        # Calculate average credibility
        avg_credibility = sum(rel.credibility for rel in rels) / len(rels)
        
        # Check if this is a consensus point
        if support_ratio >= 0.9 and avg_credibility >= 0.6:
            parts = claim_key.split("|")
            consensus_claim = (
                f"{parts[0]} {parts[1]} {parts[2]} "
                f"(supported by {num_supporting_sources} sources, "
                f"avg credibility: {avg_credibility:.2f})"
            )
            consensus_points.append(consensus_claim)
    
    return consensus_points
```

**Step-by-Step Example**:

```python
# Knowledge Graph with 10 unique sources
relationships = [
    # Claim 1: "Coffee contains Caffeine"
    Relationship("Coffee", "contains", "Caffeine", "source1.com", 0.9),
    Relationship("Coffee", "contains", "Caffeine", "source2.com", 0.95),
    Relationship("Coffee", "contains", "Caffeine", "source3.com", 0.85),
    Relationship("Coffee", "contains", "Caffeine", "source4.com", 0.9),
    Relationship("Coffee", "contains", "Caffeine", "source5.com", 0.8),
    Relationship("Coffee", "contains", "Caffeine", "source6.com", 0.95),
    Relationship("Coffee", "contains", "Caffeine", "source7.com", 0.9),
    Relationship("Coffee", "contains", "Caffeine", "source8.com", 0.85),
    Relationship("Coffee", "contains", "Caffeine", "source9.com", 0.9),
    # 9 out of 10 sources support this claim
    
    # Claim 2: "Coffee reduces Heart Disease"
    Relationship("Coffee", "reduces", "Heart Disease", "source1.com", 0.95),
    Relationship("Coffee", "reduces", "Heart Disease", "source2.com", 0.9),
    # Only 2 out of 10 sources support this claim
]

total_sources = 10

# Analyze Claim 1: "Coffee contains Caffeine"
supporting_sources = 9
support_ratio = 9 / 10 = 0.9 (90%)
avg_credibility = (0.9 + 0.95 + 0.85 + 0.9 + 0.8 + 0.95 + 0.9 + 0.85 + 0.9) / 9 = 0.89

# Check consensus criteria:
# support_ratio >= 0.9? YES (0.9 >= 0.9) ✓
# avg_credibility >= 0.6? YES (0.89 >= 0.6) ✓
# Result: CONSENSUS!

consensus_points = [
    "Coffee contains Caffeine (supported by 9 sources, avg credibility: 0.89)"
]

# Analyze Claim 2: "Coffee reduces Heart Disease"
supporting_sources = 2
support_ratio = 2 / 10 = 0.2 (20%)
avg_credibility = (0.95 + 0.9) / 2 = 0.925

# Check consensus criteria:
# support_ratio >= 0.9? NO (0.2 < 0.9) ✗
# Result: NOT CONSENSUS (insufficient agreement)
```

**Complexity**: O(r) where r = number of relationships

---


## Workflow Orchestration

### Purpose
Coordinate all agents through an iterative research cycle using a state machine.

### Location
`agents/workflow.py` - `WorkflowOrchestrator`

### State Machine Design

The workflow uses **LangGraph** to implement a finite state machine with conditional transitions.

**States**:
1. Scout - Gather sources
2. Mapper - Extract knowledge
3. Adversary - Challenge findings
4. Decision - Continue or proceed?
5. Judge - Evaluate credibility
6. Synthesis - Generate report

**Transitions**:
```
Scout → Mapper → Adversary → Decision
                              ↓
                    ┌─────────┴─────────┐
                    ↓                   ↓
                Continue            Proceed
                    ↓                   ↓
                Scout               Judge → Synthesis → END
```

### Algorithm Steps

#### Step 1: Initialize Workflow State

**Purpose**: Create initial state with topic validation

**Code Walkthrough**:

```python
def initialize(self, topic: str) -> WorkflowState:
    """Initialize the workflow with a research topic."""
    
    # Validate topic is non-empty
    if not topic or not topic.strip():
        raise ValueError("Topic must be non-empty")
    
    # Check for meaningful content
    if not any(c.isalnum() for c in topic):
        raise ValueError("Topic must contain alphanumeric characters")
    
    # Create initial workflow state
    state = WorkflowState(
        topic=topic.strip(),
        iteration=0,
        max_iterations=3,
        current_phase="initialized",
        sources=[],
        knowledge_graph=None,
        adversarial_queries=[],
        executed_queries=set(),
        synthesis_report=None,
        status_message=f"Research workflow initialized for topic: '{topic.strip()}'"
    )
    
    return state
```

**Example**:

```python
# Valid initialization
topic = "Is coffee healthy?"
state = orchestrator.initialize(topic)
# state.topic = "Is coffee healthy?"
# state.iteration = 0
# state.sources = []

# Invalid initialization
topic = "   "  # Only whitespace
state = orchestrator.initialize(topic)
# Raises: ValueError("Topic must be non-empty")
```

**Complexity**: O(n) where n = topic length (validation)

---

#### Step 2: Execute Agent Nodes

**Purpose**: Run each agent and update state

**Code Walkthrough**:

```python
def _scout_node(self, state: WorkflowState) -> WorkflowState:
    """Scout agent node: Gather diverse sources."""
    state.current_phase = "scout"
    
    try:
        # Execute Scout agent
        state = self.scout_agent.execute(state)
        
        # Save checkpoint
        self._save_checkpoint(state, "scout")
        
    except Exception as e:
        logger.error(f"Scout phase failed: {e}")
        state.status_message = f"Scout phase failed: {e}"
    
    return state

def _mapper_node(self, state: WorkflowState) -> WorkflowState:
    """Mapper agent node: Extract knowledge."""
    state.current_phase = "mapper"
    
    try:
        # Execute Mapper agent
        state = self.mapper_agent.execute(state)
        
        # Save checkpoint
        self._save_checkpoint(state, "mapper")
        
    except Exception as e:
        logger.error(f"Mapper phase failed: {e}")
        state.status_message = f"Mapper phase failed: {e}"
    
    return state

# Similar nodes for adversary, judge, synthesis...
```

**Example State Progression**:

```python
# Initial State
state = WorkflowState(
    topic="Is coffee healthy?",
    iteration=0,
    sources=[],
    knowledge_graph=None
)

# After Scout
state = scout_node(state)
# state.sources = [Source1, Source2, ..., Source20]
# state.current_phase = "scout"

# After Mapper
state = mapper_node(state)
# state.knowledge_graph = KnowledgeGraph(
#     entities=["Coffee", "Caffeine", "Health"],
#     relationships=[...],
#     conflicts=[...]
# )
# state.current_phase = "mapper"

# After Adversary
state = adversary_node(state)
# state.adversarial_queries = [
#     "coffee negative health effects",
#     "caffeine cardiovascular risks"
# ]
# state.iteration = 1
# state.current_phase = "adversary"
```

**Complexity**: O(1) per node (agent execution complexity varies)

---

#### Step 3: Decision Logic

**Purpose**: Determine whether to continue iterating or proceed to evaluation

**Decision Criteria**:
1. If `iteration >= max_iterations` → Proceed to Judge
2. If `adversarial_queries` is empty → Proceed to Judge
3. Otherwise → Continue to Scout (loop back)

**Code Walkthrough**:

```python
def _should_continue_iteration(
    self,
    state: WorkflowState
) -> Literal["continue", "proceed"]:
    """Decision function to determine if another iteration is needed."""
    
    # Check if max iterations reached
    if state.iteration >= state.max_iterations:
        logger.info(f"Maximum iterations ({state.max_iterations}) reached")
        return "proceed"
    
    # Check if adversarial queries were generated
    if state.adversarial_queries and len(state.adversarial_queries) > 0:
        logger.info(f"Weak claims found, continuing iteration {state.iteration + 1}")
        return "continue"
    
    # No weak claims found, proceed to evaluation
    logger.info("Sufficient evidence gathered, proceeding to Judge")
    return "proceed"
```

**Decision Tree Example**:

```python
# Scenario 1: First iteration, weaknesses found
state.iteration = 1
state.max_iterations = 3
state.adversarial_queries = ["coffee risks", "caffeine dangers"]

decision = _should_continue_iteration(state)
# iteration < max_iterations? YES (1 < 3)
# adversarial_queries not empty? YES
# Result: "continue" → Loop back to Scout

# Scenario 2: Max iterations reached
state.iteration = 3
state.max_iterations = 3
state.adversarial_queries = ["some query"]

decision = _should_continue_iteration(state)
# iteration >= max_iterations? YES (3 >= 3)
# Result: "proceed" → Move to Judge

# Scenario 3: No weaknesses found
state.iteration = 1
state.max_iterations = 3
state.adversarial_queries = []

decision = _should_continue_iteration(state)
# iteration < max_iterations? YES (1 < 3)
# adversarial_queries empty? YES
# Result: "proceed" → Move to Judge
```

**Complexity**: O(1) - simple conditional checks

---


#### Step 4: Complete Workflow Execution

**Purpose**: Execute the entire state machine from start to finish

**Code Walkthrough**:

```python
def execute(self, topic: str) -> WorkflowState:
    """Execute the complete research workflow for a given topic."""
    
    # Initialize workflow state
    state = self.initialize(topic)
    
    try:
        # Execute the graph (LangGraph handles state transitions)
        final_state = self.graph.invoke(state)
        
        return final_state
        
    except Exception as e:
        logger.error(f"Workflow execution failed: {e}")
        
        # Attempt to recover from last checkpoint
        if self.enable_checkpoints:
            checkpoints = self.checkpoint_manager.list_checkpoints()
            if checkpoints:
                latest_checkpoint = sorted(checkpoints)[-1]
                recovered_state = self.checkpoint_manager.load_checkpoint(
                    latest_checkpoint
                )
                return recovered_state
        
        raise
```

**Complete Execution Example**:

```python
# Initialize orchestrator
orchestrator = WorkflowOrchestrator(max_iterations=2)

# Execute workflow
topic = "Is coffee healthy?"
final_state = orchestrator.execute(topic)

# Execution trace:
# 
# Iteration 0:
#   Scout → Gather 20 sources
#   Mapper → Extract 35 entities, 48 relationships, 3 conflicts
#   Adversary → Identify 5 weaknesses, generate 3 counter-queries
#   Decision → Continue (weaknesses found)
#
# Iteration 1:
#   Scout → Gather 15 more sources (using counter-queries)
#   Mapper → Extract 12 new entities, 23 new relationships, 2 new conflicts
#   Adversary → Identify 2 weaknesses, generate 2 counter-queries
#   Decision → Continue (weaknesses found)
#
# Iteration 2:
#   Scout → Gather 10 more sources
#   Mapper → Extract 8 new entities, 15 new relationships, 1 new conflict
#   Adversary → Identify 1 weakness, generate 1 counter-query
#   Decision → Proceed (max iterations reached)
#
# Judge → Evaluate 45 sources, annotate knowledge graph with credibility
# Synthesis → Generate final report with consensus and battlegrounds
#
# Final State:
#   - 45 sources from 38 unique domains
#   - 55 entities
#   - 86 relationships
#   - 6 conflicts
#   - 3 consensus points
#   - 6 battleground topics
#   - Complete synthesis report with knowledge graph JSON
```

**Total Workflow Complexity**:
- Time: O(i × (s + r × e + c)) where:
  - i = number of iterations (typically 2-3)
  - s = number of sources per iteration (10-30)
  - r = number of relationships (50-200)
  - e = number of entities (30-100)
  - c = number of conflicts (3-10)
- Space: O(s + e + r + c) - stores all collected data

---

## Performance Characteristics

### Overall System Performance

**Typical Research Session**:
- Duration: 2-3 minutes
- API Calls: 15-25 (LLM + Search)
- Sources Collected: 30-50
- Entities Extracted: 40-80
- Relationships: 60-150
- Conflicts: 3-10

**Bottlenecks**:
1. **LLM Calls**: 1-3 seconds each (Mapper, Adversary, Synthesis)
2. **Web Scraping**: 0.5-2 seconds per source (Scout)
3. **Entity Deduplication**: O(n²) but n is small (50-100)

**Optimization Strategies**:
1. **Parallel Source Collection**: Fetch multiple sources concurrently
2. **Caching**: Cache LLM responses for repeated queries
3. **Batch Processing**: Process multiple relationships in single LLM call
4. **Early Termination**: Stop if sufficient consensus found

---

## Algorithm Comparison Table

| Algorithm | Time Complexity | Space Complexity | Bottleneck |
|-----------|----------------|------------------|------------|
| Credibility Scoring | O(n) | O(1) | Regex scanning |
| Entity Deduplication | O(n² × m) | O(n) | String comparison |
| Conflict Detection | O(c) | O(c) | LLM extraction |
| Adversarial Query Gen | O(w) | O(w) | LLM generation |
| Knowledge Graph Build | O(r × e) | O(e + r + c) | Validation |
| Consensus Identification | O(r) | O(r) | Grouping |
| Workflow Orchestration | O(i × s) | O(s + e + r) | Iterations |

Where:
- n = content length or entity count
- m = average string length
- c = number of conflicts
- w = number of weaknesses
- r = number of relationships
- e = number of entities
- s = number of sources
- i = number of iterations

---

## Key Takeaways

1. **Credibility Scoring**: Transparent, configurable, no black-box ML
2. **Entity Deduplication**: Fuzzy matching handles naming variations
3. **Conflict Detection**: LLM-based extraction with validation
4. **Adversarial Approach**: Actively seeks counter-evidence
5. **Knowledge Graph**: Structured representation with referential integrity
6. **Consensus**: Statistical approach (90% threshold)
7. **Workflow**: State machine with iterative refinement

All algorithms prioritize:
- Transparency (explainable decisions)
- Robustness (error handling and validation)
- Efficiency (reasonable time/space complexity)
- Correctness (property-based testing)

---

## Further Reading

For implementation details, see:
- `agents/judge.py` - Credibility scoring
- `agents/mapper.py` - Knowledge graph construction
- `agents/adversary.py` - Weakness identification
- `agents/synthesis.py` - Consensus and battleground analysis
- `agents/workflow.py` - State machine orchestration

For testing, see:
- `tests/test_judge_properties.py` - Credibility algorithm tests
- `tests/test_mapper_properties.py` - Entity deduplication tests
- `tests/test_workflow_properties.py` - Workflow orchestration tests

---

**Version**: 1.0.0  
**Last Updated**: January 2026  
**License**: MIT
