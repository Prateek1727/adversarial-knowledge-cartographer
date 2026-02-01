# Usage Examples

This document provides detailed examples of using the Adversarial Knowledge Cartographer for various research scenarios.

## Table of Contents

1. [Basic Usage](#basic-usage)
2. [API Examples](#api-examples)
3. [Programmatic Usage](#programmatic-usage)
4. [Example Research Topics](#example-research-topics)
5. [Interpreting Results](#interpreting-results)
6. [Advanced Usage](#advanced-usage)

## Basic Usage

### Starting a Research Session

The simplest way to use the system is through the API:

```bash
# Start the backend API
python api/app.py

# In another terminal, start a research session
curl -X POST http://localhost:8000/api/research \
  -H "Content-Type: application/json" \
  -d '{"topic": "Is coffee good for health?"}'
```

### Monitoring Progress

```bash
# Get session status
curl http://localhost:8000/api/research/{session_id}/status

# Example response:
{
  "session_id": "abc-123",
  "topic": "Is coffee good for health?",
  "status": "running",
  "current_phase": "adversary",
  "iteration": 2,
  "sources_count": 15,
  "entities_count": 28,
  "relationships_count": 45,
  "conflicts_count": 3
}
```

### Retrieving Results

```bash
# Get the knowledge graph
curl http://localhost:8000/api/research/{session_id}/graph > graph.json

# Get the synthesis report
curl http://localhost:8000/api/research/{session_id}/report > report.json
```

## API Examples

### Example 1: Controversial Health Topic

**Topic**: "Effects of intermittent fasting on metabolism"

```bash
curl -X POST http://localhost:8000/api/research \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Effects of intermittent fasting on metabolism"
  }'
```

**Expected Output**:
- **Consensus**: General agreement on insulin sensitivity improvement
- **Battleground**: Conflicting claims about muscle mass preservation
- **Conflicts**: Studies with different fasting protocols showing different results
- **Verdict**: Credibility-weighted analysis favoring peer-reviewed studies

### Example 2: Technical Topic

**Topic**: "Time complexity of quicksort algorithm"

```bash
curl -X POST http://localhost:8000/api/research \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Time complexity of quicksort algorithm"
  }'
```

**Expected Output**:
- **Consensus**: Average case O(n log n), worst case O(n²)
- **Battleground**: Practical performance vs theoretical complexity
- **High Credibility Sources**: Academic textbooks (.edu domains)
- **Conflicts**: Different pivot selection strategies

### Example 3: Current Events

**Topic**: "Latest developments in renewable energy storage"

```bash
curl -X POST http://localhost:8000/api/research \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Latest developments in renewable energy storage"
  }'
```

**Expected Output**:
- **High Recency Scores**: Recent articles weighted heavily
- **Conflicts**: Different battery technologies competing
- **Battleground**: Cost-effectiveness claims from different manufacturers

## Programmatic Usage

### Example 1: Basic Workflow Execution

```python
from agents import WorkflowOrchestrator
from config import config

# Initialize orchestrator
orchestrator = WorkflowOrchestrator(max_iterations=3)

# Execute research
result = orchestrator.execute("Is nuclear energy safe?")

# Access knowledge graph
print(f"Entities: {len(result.knowledge_graph.entities)}")
print(f"Relationships: {len(result.knowledge_graph.relationships)}")
print(f"Conflicts: {len(result.knowledge_graph.conflicts)}")

# Print synthesis report
print("\n=== SYNTHESIS REPORT ===")
print(result.synthesis_report)
```

### Example 2: Custom Configuration

```python
from agents import WorkflowOrchestrator, ScoutAgent, MapperAgent
from models.data_models import WorkflowState

# Create custom orchestrator with specific settings
orchestrator = WorkflowOrchestrator(
    max_iterations=2,  # Fewer iterations for faster results
    min_sources=15     # More sources for better coverage
)

# Execute with custom topic
topic = "Effectiveness of meditation for anxiety reduction"
result = orchestrator.execute(topic)

# Analyze conflicts
for conflict in result.knowledge_graph.conflicts:
    print(f"\nConflict: {conflict.point_of_contention}")
    print(f"Side A: {conflict.side_a}")
    print(f"  Citation: {conflict.side_a_citation}")
    print(f"  Credibility: {conflict.side_a_credibility:.2f}")
    print(f"Side B: {conflict.side_b}")
    print(f"  Citation: {conflict.side_b_citation}")
    print(f"  Credibility: {conflict.side_b_credibility:.2f}")
```

### Example 3: Accessing Individual Agents

```python
from agents import ScoutAgent, MapperAgent, JudgeAgent
from config import config

# Initialize agents
scout = ScoutAgent(
    search_provider=config.search_provider,
    api_key=config.tavily_api_key
)

mapper = MapperAgent(
    llm_provider=config.llm_provider,
    api_key=config.openai_api_key
)

judge = JudgeAgent()

# Scout phase: Gather sources
sources = scout.search("Climate change impact on coral reefs")
print(f"Collected {len(sources)} sources")

# Mapper phase: Extract knowledge
knowledge_graph = mapper.extract_knowledge(sources)
print(f"Extracted {len(knowledge_graph.entities)} entities")
print(f"Found {len(knowledge_graph.conflicts)} conflicts")

# Judge phase: Evaluate credibility
scored_graph = judge.evaluate_credibility(knowledge_graph, sources)
print(f"Scored {len(scored_graph.relationships)} relationships")
```

### Example 4: Iterating Through Workflow States

```python
from agents import WorkflowOrchestrator
from models.data_models import WorkflowState

orchestrator = WorkflowOrchestrator(max_iterations=3)

# Execute with state tracking
topic = "Cryptocurrency as investment vs speculation"
state = WorkflowState(topic=topic, iteration=0)

# Track each iteration
for iteration in range(3):
    print(f"\n=== ITERATION {iteration + 1} ===")
    
    # Scout phase
    state = orchestrator.scout_phase(state)
    print(f"Sources collected: {len(state.sources)}")
    
    # Mapper phase
    state = orchestrator.mapper_phase(state)
    print(f"Entities: {len(state.knowledge_graph.entities)}")
    print(f"Conflicts: {len(state.knowledge_graph.conflicts)}")
    
    # Adversary phase
    state = orchestrator.adversary_phase(state)
    print(f"Adversarial queries: {len(state.adversarial_queries)}")
    
    # Check if we should continue
    if not state.adversarial_queries or iteration >= 2:
        break

# Judge and synthesis
state = orchestrator.judge_phase(state)
state = orchestrator.synthesis_phase(state)

print("\n=== FINAL REPORT ===")
print(state.synthesis_report)
```

## Example Research Topics

### Controversial Topics (Good for Conflict Detection)

#### Health & Wellness
- "Is coffee good or bad for health?"
- "Effectiveness of homeopathy vs placebo"
- "Vegan diet vs omnivorous diet for health"
- "Benefits and risks of intermittent fasting"
- "Effectiveness of meditation for mental health"

#### Technology & Society
- "Impact of social media on mental health"
- "Artificial intelligence job displacement vs creation"
- "Privacy vs security in digital surveillance"
- "Cryptocurrency as investment vs speculation"
- "Remote work productivity vs office work"

#### Environment & Energy
- "Nuclear energy safety and environmental impact"
- "Electric vehicles vs hydrogen fuel cells"
- "Effectiveness of carbon offset programs"
- "GMO crops benefits vs risks"
- "Wind energy vs solar energy efficiency"

### Technical Topics (Good for Credibility Scoring)

#### Computer Science
- "Time complexity of quicksort algorithm"
- "Blockchain scalability trilemma"
- "Quantum computing practical applications"
- "Machine learning model interpretability"
- "Microservices vs monolithic architecture"

#### Science & Engineering
- "CRISPR gene editing accuracy and safety"
- "Fusion energy feasibility timeline"
- "Graphene commercial applications"
- "Quantum entanglement practical uses"
- "Carbon capture technology effectiveness"

### Current Events (Good for Recency Scoring)

- "Latest developments in renewable energy storage"
- "Recent advances in cancer immunotherapy"
- "Current state of artificial intelligence regulation"
- "Recent findings on COVID-19 long-term effects"
- "Latest space exploration missions and discoveries"

## Interpreting Results

### Understanding the Knowledge Graph

The knowledge graph contains three main components:

#### 1. Entities
```json
{
  "entities": [
    "Coffee consumption",
    "Cardiovascular health",
    "Caffeine",
    "Heart disease risk"
  ]
}
```

**Interpretation**: These are the key concepts extracted from sources.

#### 2. Relationships
```json
{
  "relationships": [
    {
      "source": "Coffee consumption",
      "relation": "reduces_risk_of",
      "target": "Heart disease",
      "citation": "https://example.com/study1",
      "credibility": 0.85
    }
  ]
}
```

**Interpretation**: 
- **Credibility > 0.8**: High-quality source (.edu, .gov, peer-reviewed)
- **Credibility 0.5-0.8**: Moderate-quality source (.org, reputable .com)
- **Credibility < 0.5**: Lower-quality source (blogs, opinion pieces)

#### 3. Conflicts
```json
{
  "conflicts": [
    {
      "point_of_contention": "Effect of coffee on heart health",
      "side_a": "Coffee reduces heart disease risk",
      "side_a_citation": "https://harvard.edu/study",
      "side_a_credibility": 0.95,
      "side_b": "Coffee increases heart disease risk",
      "side_b_citation": "https://blog.com/article",
      "side_b_credibility": 0.45
    }
  ]
}
```

**Interpretation**: The conflict shows disagreement, but Side A has much higher credibility (0.95 vs 0.45), suggesting the Harvard study is more reliable.

### Understanding the Synthesis Report

The synthesis report has four main sections:

#### 1. Consensus Section
```
## The Consensus

Based on analysis of 15 sources, the following points have >90% agreement:

- Coffee consumption (1-3 cups/day) is associated with reduced risk of type 2 diabetes
- Caffeine has stimulant effects on the central nervous system
- Coffee contains antioxidants and beneficial compounds
```

**Interpretation**: These are well-established facts with broad source agreement.

#### 2. Battleground Section
```
## The Battleground

### Point of Contention: Effect on cardiovascular health

**Claim A**: Coffee reduces cardiovascular disease risk
- Sources: 8 studies (avg credibility: 0.87)
- Evidence: Large cohort studies, meta-analyses
- Methodology: Long-term observational studies

**Claim B**: Coffee increases heart palpitations and blood pressure
- Sources: 4 studies (avg credibility: 0.72)
- Evidence: Short-term clinical trials
- Methodology: Acute caffeine administration studies

**Why they disagree**: Different timeframes (long-term vs acute effects)
```

**Interpretation**: Both claims may be true in different contexts. Long-term consumption shows benefits, but acute effects can include temporary blood pressure increases.

#### 3. Verdict Section
```
## The Verdict

Based on credibility-weighted analysis:

**Likely Correct**: Coffee reduces long-term cardiovascular disease risk
- Supported by higher-credibility sources (0.87 avg)
- Larger sample sizes
- Peer-reviewed meta-analyses

**Context-Dependent**: Acute cardiovascular effects
- Short-term blood pressure increases are real but temporary
- Individual sensitivity varies
```

**Interpretation**: The system weighs evidence by credibility and provides nuanced conclusions.

#### 4. Knowledge Graph JSON
```json
{
  "entities": [...],
  "relationships": [...],
  "conflicts": [...]
}
```

**Interpretation**: Complete structured data for visualization or further analysis.

## Advanced Usage

### Custom Credibility Weights

Adjust credibility scoring weights in `.env`:

```bash
# Emphasize domain authority
DOMAIN_WEIGHT=0.6
CITATION_WEIGHT=0.2
RECENCY_WEIGHT=0.2

# Emphasize recency (for current events)
DOMAIN_WEIGHT=0.2
CITATION_WEIGHT=0.2
RECENCY_WEIGHT=0.6
```

### Controlling Iteration Depth

```bash
# Quick research (1 iteration)
MAX_ITERATIONS=1

# Thorough research (5 iterations)
MAX_ITERATIONS=5
```

**Trade-offs**:
- More iterations = more thorough but slower
- Fewer iterations = faster but may miss counter-evidence

### Filtering Results by Credibility

```python
from agents import WorkflowOrchestrator

orchestrator = WorkflowOrchestrator()
result = orchestrator.execute("Topic here")

# Filter high-credibility relationships only
high_quality = [
    rel for rel in result.knowledge_graph.relationships
    if rel.credibility > 0.8
]

print(f"High-quality relationships: {len(high_quality)}")
for rel in high_quality:
    print(f"{rel.source} -> {rel.relation} -> {rel.target}")
    print(f"  Credibility: {rel.credibility:.2f}")
    print(f"  Citation: {rel.citation}")
```

### Exporting Results

```python
import json
from agents import WorkflowOrchestrator

orchestrator = WorkflowOrchestrator()
result = orchestrator.execute("Topic here")

# Export knowledge graph
with open("knowledge_graph.json", "w") as f:
    json.dump(result.knowledge_graph.dict(), f, indent=2)

# Export synthesis report
with open("synthesis_report.md", "w") as f:
    f.write(result.synthesis_report)

print("Results exported successfully!")
```

### Batch Processing Multiple Topics

```python
from agents import WorkflowOrchestrator
import json

topics = [
    "Is coffee good for health?",
    "Nuclear energy safety",
    "Remote work effectiveness"
]

orchestrator = WorkflowOrchestrator(max_iterations=2)
results = {}

for topic in topics:
    print(f"\nResearching: {topic}")
    result = orchestrator.execute(topic)
    results[topic] = {
        "entities": len(result.knowledge_graph.entities),
        "relationships": len(result.knowledge_graph.relationships),
        "conflicts": len(result.knowledge_graph.conflicts),
        "report": result.synthesis_report
    }

# Save batch results
with open("batch_results.json", "w") as f:
    json.dump(results, f, indent=2)
```

### Visualizing Results

```python
from agents import WorkflowOrchestrator
import networkx as nx
import matplotlib.pyplot as plt

orchestrator = WorkflowOrchestrator()
result = orchestrator.execute("Topic here")

# Create NetworkX graph
G = nx.DiGraph()

# Add nodes
for entity in result.knowledge_graph.entities:
    G.add_node(entity)

# Add edges
for rel in result.knowledge_graph.relationships:
    G.add_edge(
        rel.source,
        rel.target,
        label=rel.relation,
        credibility=rel.credibility
    )

# Draw graph
plt.figure(figsize=(12, 8))
pos = nx.spring_layout(G)
nx.draw(G, pos, with_labels=True, node_color='lightblue',
        node_size=1500, font_size=10, arrows=True)
plt.title("Knowledge Graph Visualization")
plt.savefig("knowledge_graph.png")
print("Graph saved to knowledge_graph.png")
```

## Tips for Best Results

### 1. Topic Formulation

**Good topics**:
- "Effects of X on Y"
- "X vs Y comparison"
- "Is X true or false?"
- "Benefits and risks of X"

**Poor topics**:
- Too broad: "Tell me about science"
- Too narrow: "What is 2+2?"
- Non-factual: "What is the meaning of life?"

### 2. Interpreting Conflicts

- Look at credibility scores first
- Consider source types (.edu > .com)
- Check publication dates for recency
- Read the "Why they disagree" analysis

### 3. Handling Errors

If research fails:
- Check API keys are valid
- Verify internet connection
- Try a different topic
- Reduce MAX_ITERATIONS
- Check logs for detailed errors

### 4. Performance Optimization

For faster results:
- Reduce MAX_ITERATIONS to 1-2
- Lower MIN_SOURCES to 5-8
- Use GPT-3.5-turbo instead of GPT-4
- Enable result caching

## Next Steps

- Explore the [API documentation](api/README.md)
- Try the [frontend visualization](frontend/README.md)
- Review the [design document](.kiro/specs/adversarial-knowledge-cartographer/design.md)
- Check the [requirements](.kiro/specs/adversarial-knowledge-cartographer/requirements.md)
