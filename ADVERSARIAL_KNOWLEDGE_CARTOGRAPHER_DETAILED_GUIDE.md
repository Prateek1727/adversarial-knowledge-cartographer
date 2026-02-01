# Adversarial Knowledge Cartographer - Complete Technical Guide for Beginners

## Table of Contents
1. [What is the Adversarial Knowledge Cartographer?](#what-is-the-adversarial-knowledge-cartographer)
2. [The Big Picture: How It All Works](#the-big-picture-how-it-all-works)
3. [The Five AI Agents Explained in Detail](#the-five-ai-agents-explained-in-detail)
4. [Technical Architecture Deep Dive](#technical-architecture-deep-dive)
5. [Data Flow: From Topic to Knowledge Graph](#data-flow-from-topic-to-knowledge-graph)
6. [The Credibility Scoring System Explained](#the-credibility-scoring-system-explained)
7. [How Conflicts Are Detected and Resolved](#how-conflicts-are-detected-and-resolved)
8. [The Visualization System](#the-visualization-system)
9. [Real-World Example Walkthrough](#real-world-example-walkthrough)
10. [API and Integration Guide](#api-and-integration-guide)
11. [Understanding the Code Structure](#understanding-the-code-structure)
12. [Testing and Quality Assurance](#testing-and-quality-assurance)

## What is the Adversarial Knowledge Cartographer?

The Adversarial Knowledge Cartographer is an AI-powered research system that doesn't just collect information—it actively challenges its own findings to create more reliable research. Think of it as having a team of AI researchers where one person gathers information, another organizes it, a third person tries to poke holes in it, a fourth person judges the quality of sources, and a fifth person writes the final report.

### Why "Adversarial"?

The term "adversarial" means the system deliberately looks for opposing viewpoints and tries to challenge its own conclusions. This is like having a built-in devil's advocate that ensures you're not just seeing one side of the story.

### Why "Knowledge Cartographer"?

A cartographer makes maps. This system creates "maps" of knowledge—visual representations showing how different concepts, claims, and counter-claims connect to each other.

## The Big Picture: How It All Works

### The Research Cycle

```
1. You ask: "Is coffee good for health?"
   ↓
2. Scout Agent searches the web for sources
   ↓
3. Mapper Agent reads sources and builds a knowledge map
   ↓
4. Adversary Agent says "Wait, let me find counter-evidence"
   ↓
5. Judge Agent evaluates which sources are more trustworthy
   ↓
6. Synthesis Agent writes the final report
   ↓
7. You get a comprehensive analysis with visual knowledge map
```

### What Makes This Different?

**Traditional Research Tools:**
- Find sources ✓
- Summarize them ✓
- Present results ✓

**Adversarial Knowledge Cartographer:**
- Find sources ✓
- Summarize them ✓
- **Actively look for opposing views** ✓
- **Evaluate source credibility** ✓
- **Map conflicts and relationships** ✓
- **Provide visual knowledge graphs** ✓
- Present balanced results ✓

## The Five AI Agents Explained in Detail

### 1. 🔍 Scout Agent - The Information Hunter

**What it does:** Searches the internet for relevant information about your topic.

**How it works technically:**

1. **Query Generation**: Takes your topic and creates search queries
   ```python
   topic = "coffee health effects"
   queries = [
       "coffee health benefits research",
       "coffee cardiovascular effects studies", 
       "coffee health risks medical research"
   ]
   ```

2. **Web Search**: Uses search APIs to find sources
   - **Primary**: Tavily API (specialized for research)
   - **Backup**: Serper API (Google search)
   - **Strategy**: Searches multiple queries to get diverse perspectives

3. **Content Extraction**: Downloads and cleans the content
   ```python
   # For each search result:
   raw_html = download_webpage(url)
   clean_text = extract_article_text(raw_html)  # Using Trafilatura library
   source = Source(
       url=url,
       title=title,
       content=clean_text,
       domain=extract_domain(url),
       retrieved_at=datetime.now()
   )
   ```

4. **Quality Control**: Ensures diverse, high-quality sources
   - Minimum 10 sources
   - From different domains (.edu, .org, .gov, .com)
   - Filters out paywalled or inaccessible content

**Example Output:**
```json
[
  {
    "url": "https://www.harvard.edu/coffee-health-study",
    "title": "Coffee Consumption and Health Outcomes",
    "content": "A comprehensive study of 500,000 participants...",
    "domain": "harvard.edu",
    "retrieved_at": "2024-01-15T10:30:00Z"
  },
  // ... 9 more sources
]
```

### 2. 📊 Mapper Agent - The Knowledge Architect

**What it does:** Reads all the sources and builds a structured map of how concepts relate to each other.

**How it works technically:**

1. **Entity Extraction**: Identifies key concepts
   ```python
   # AI reads: "Coffee consumption reduces risk of Type 2 diabetes"
   entities = ["Coffee", "Type 2 Diabetes", "Cardiovascular Health"]
   ```

2. **Relationship Mapping**: Identifies how entities connect
   ```python
   relationships = [
       {
           "source": "Coffee",
           "relation": "reduces_risk_of", 
           "target": "Type 2 Diabetes",
           "citation": "Harvard Health Study 2023"
       }
   ]
   ```

3. **Conflict Detection**: Finds where sources disagree
   ```python
   conflicts = [
       {
           "point_of_contention": "Coffee's effect on heart disease",
           "side_a": "Coffee reduces heart disease risk",
           "side_a_citation": "Harvard Study",
           "side_b": "Coffee increases heart disease risk", 
           "side_b_citation": "Mayo Clinic Report"
       }
   ]
   ```

4. **Knowledge Graph Assembly**: Combines everything into a structured format
   ```python
   knowledge_graph = {
       "entities": ["Coffee", "Heart Disease", "Type 2 Diabetes"],
       "relationships": [...],
       "conflicts": [...]
   }
   ```

**The AI Prompt (Simplified):**
```
You are a Knowledge Cartographer. Analyze these sources about coffee and health.

Extract:
1. Key entities (concepts, substances, conditions)
2. Relationships between entities (how they affect each other)
3. Conflicts (where sources disagree)

Output as JSON only. Focus on disagreements between sources.
```

### 3. ⚔️ Adversary Agent - The Professional Skeptic

**What it does:** Actively tries to find weaknesses in the current findings and searches for counter-evidence.

**How it works technically:**

1. **Weakness Analysis**: Examines current findings for vulnerabilities
   ```python
   def analyze_weaknesses(knowledge_graph):
       weaknesses = []
       
       # Check for single-source claims
       for relationship in knowledge_graph.relationships:
           if count_supporting_sources(relationship) == 1:
               weaknesses.append({
                   "type": "single_source",
                   "description": f"Only one source supports: {relationship}",
                   "affected_claims": [relationship.relation]
               })
       
       # Check for outdated sources
       for source in sources:
           if source.age > 2_years:
               weaknesses.append({
                   "type": "outdated",
                   "description": f"Source from {source.date} may be outdated"
               })
       
       return weaknesses
   ```

2. **Counter-Query Generation**: Creates searches designed to find opposing evidence
   ```python
   # If current finding: "Coffee is healthy"
   counter_queries = [
       "coffee health risks cardiovascular",
       "negative effects daily caffeine consumption",
       "coffee addiction withdrawal symptoms"
   ]
   ```

3. **Red-Team Search**: Executes adversarial searches
   - Uses the Scout Agent with counter-queries
   - Specifically looks for evidence that contradicts current findings
   - Adds new sources to the knowledge base

**The AI Prompt (Simplified):**
```
You are a Red-Teamer. Your job is to find weaknesses in these research findings.

Current findings show coffee is mostly positive for health.

Find:
1. Claims supported by only one source
2. Outdated information (>2 years old)  
3. Potential biases in sources

Generate 3 aggressive search queries to find counter-evidence.
Example: "coffee cardiovascular risks long-term studies"
```

### 4. ⚖️ Judge Agent - The Credibility Evaluator

**What it does:** Evaluates how trustworthy each source is and assigns credibility scores.

**How it works technically:**

1. **Domain Authority Assessment** (40% of credibility score):
   ```python
   def calculate_domain_authority(url):
       domain = extract_domain(url)
       
       if domain.endswith('.edu') or domain.endswith('.gov'):
           return 1.0  # Highest credibility
       elif domain in PRESTIGIOUS_JOURNALS:
           return 0.95
       elif domain.endswith('.org'):
           return 0.8
       elif domain in REPUTABLE_NEWS:
           return 0.75
       elif domain == 'wikipedia.org':
           return 0.7
       else:
           return 0.6  # Default for .com sites
   ```

2. **Citation Indicators Assessment** (30% of credibility score):
   ```python
   def assess_citations(content):
       score = 0.0
       
       # Look for reference section
       if re.search(r'references|bibliography', content, re.IGNORECASE):
           score += 0.3
       
       # Look for academic formatting [1], [2] or (2023)
       if re.search(r'\[\d+\]|\(\d{4}\)', content):
           score += 0.2
           
       # Look for author credentials
       if re.search(r'Dr\.|PhD|Professor|Researcher', content):
           score += 0.3
           
       return min(score, 1.0)  # Cap at 1.0
   ```

3. **Recency Assessment** (30% of credibility score):
   ```python
   def calculate_recency_score(publication_date):
       age_years = (datetime.now() - publication_date).days / 365
       
       if age_years < 1:
           return 1.0
       elif age_years < 2:
           return 0.8
       elif age_years < 5:
           return 0.5
       else:
           return 0.3
   ```

4. **Final Score Calculation**:
   ```python
   def calculate_credibility_score(source):
       domain_score = calculate_domain_authority(source.url)
       citation_score = assess_citations(source.content)
       recency_score = calculate_recency_score(source.date)
       
       # Weighted average
       final_score = (
           domain_score * 0.4 +
           citation_score * 0.3 + 
           recency_score * 0.3
       )
       
       return final_score
   ```

**Example Credibility Scores:**
- Harvard Medical School article (2024): 0.94
- Mayo Clinic article (2023): 0.87
- Wikipedia article (2022): 0.65
- Random blog post (2020): 0.42

### 5. 📝 Synthesis Agent - The Report Writer

**What it does:** Combines all the evidence, weighs it by credibility, and writes the final research report.

**How it works technically:**

1. **Consensus Identification**: Finds claims most sources agree on
   ```python
   def find_consensus(knowledge_graph):
       consensus_claims = []
       
       for claim in all_claims:
           supporting_sources = count_supporting_sources(claim)
           total_sources = count_total_sources()
           
           agreement_percentage = supporting_sources / total_sources
           
           if agreement_percentage >= 0.9:  # 90% agreement
               consensus_claims.append(claim)
       
       return consensus_claims
   ```

2. **Battleground Analysis**: Identifies major disagreements
   ```python
   def analyze_battlegrounds(conflicts):
       battlegrounds = []
       
       for conflict in conflicts:
           # Analyze why sources disagree
           disagreement_reason = analyze_disagreement(conflict)
           
           # Determine verdict based on credibility
           verdict = resolve_conflict_by_credibility(conflict)
           
           battlegrounds.append({
               "topic": conflict.point_of_contention,
               "conflicting_claims": [conflict.side_a, conflict.side_b],
               "disagreement_reason": disagreement_reason,
               "verdict": verdict
           })
       
       return battlegrounds
   ```

3. **Credibility-Weighted Verdicts**: Resolves conflicts using source quality
   ```python
   def resolve_conflict_by_credibility(conflict):
       side_a_credibility = get_source_credibility(conflict.side_a_citation)
       side_b_credibility = get_source_credibility(conflict.side_b_citation)
       
       if side_a_credibility > side_b_credibility:
           return f"Evidence favors: {conflict.side_a}"
       else:
           return f"Evidence favors: {conflict.side_b}"
   ```

**The AI Prompt (Simplified):**
```
You are a Principal Investigator writing a final research report.

Analyze the evidence and write:

1. THE CONSENSUS: What do 90% of sources agree on?
2. THE BATTLEGROUND: Where do sources disagree and why?
3. THE VERDICT: Based on source credibility, which claims are more likely true?
4. THE GRAPH: Include the complete knowledge graph as JSON.

Weight your conclusions by source credibility scores.
```

## Technical Architecture Deep Dive

### The State Machine Pattern

The system uses a **state machine** architecture, which means it has defined states and transitions:

```python
# Simplified state machine
class WorkflowState:
    current_phase: str  # "scout", "mapper", "adversary", "judge", "synthesis"
    topic: str
    iteration: int
    sources: List[Source]
    knowledge_graph: KnowledgeGraph
    executed_queries: Set[str]
    max_iterations: int = 3

# State transitions
def next_phase(current_state):
    if current_state.phase == "scout":
        return "mapper"
    elif current_state.phase == "mapper":
        return "adversary"
    elif current_state.phase == "adversary":
        if has_weak_claims(current_state) and current_state.iteration < 3:
            return "scout"  # Loop back for more evidence
        else:
            return "judge"
    elif current_state.phase == "judge":
        return "synthesis"
    else:
        return "complete"
```

### The Technology Stack

**Core Framework:**
- **LangGraph**: Orchestrates the AI agents and manages state transitions
- **LangChain**: Handles communication with AI models (GPT-4, Claude)
- **Pydantic**: Ensures data has the correct structure (like type checking)

**Data Processing:**
- **Trafilatura**: Extracts clean text from messy HTML web pages
- **BeautifulSoup**: Parses HTML when Trafilatura isn't enough
- **NetworkX**: Analyzes the knowledge graph structure

**APIs and Services:**
- **Tavily API**: Primary web search (designed for AI research)
- **Serper API**: Backup web search (Google search API)
- **OpenAI/Anthropic**: AI models for reasoning and analysis

**Visualization:**
- **React**: Frontend framework for the user interface
- **React Flow**: 2D graph visualization library
- **Three.js**: 3D visualization and interactive graphics
- **D3.js**: Advanced graph algorithms and force simulations

### How Agents Communicate

Agents don't talk directly to each other. Instead, they all read from and write to a shared **WorkflowState**:

```python
# Agent communication pattern
class ScoutAgent:
    def execute(self, state: WorkflowState) -> WorkflowState:
        # Read current state
        topic = state.topic
        queries = state.adversarial_queries or [topic]
        
        # Do work
        sources = self.search_web(queries)
        
        # Update state
        state.sources.extend(sources)
        state.phase = "mapper"
        return state

class MapperAgent:
    def execute(self, state: WorkflowState) -> WorkflowState:
        # Read what Scout found
        sources = state.sources
        
        # Do work
        knowledge_graph = self.extract_knowledge(sources)
        
        # Update state
        state.knowledge_graph = knowledge_graph
        state.phase = "adversary"
        return state
```

### Error Handling Strategy

The system is designed to be resilient:

```python
class ResilientAgent:
    def execute_with_retry(self, operation, max_retries=3):
        for attempt in range(max_retries):
            try:
                return operation()
            except RateLimitError:
                # Wait longer each time (exponential backoff)
                wait_time = 2 ** attempt
                time.sleep(wait_time)
            except ValidationError as e:
                # Fix the data and try again
                self.fix_data_format(e)
            except NetworkError:
                # Try backup API
                self.switch_to_backup_api()
        
        # If all retries failed, continue with partial data
        logger.warning("Operation failed after retries, continuing with partial data")
        return self.get_partial_results()
```

## Data Flow: From Topic to Knowledge Graph

### Step 1: Topic Input
```
User Input: "Is coffee good for health?"
↓
Validation: Check if topic is meaningful (not empty, not just whitespace)
↓
State Initialization: Create WorkflowState with topic
```

### Step 2: Initial Search (Scout)
```
Search Queries Generated:
- "coffee health benefits research"
- "coffee health effects studies"
- "coffee medical research"
↓
Web Search Results: 15+ URLs found
↓
Content Extraction: Download and clean text from each URL
↓
Source Objects Created: 10+ valid sources with content
```

### Step 3: Knowledge Extraction (Mapper)
```
AI Analysis of Sources:
- Read all source content
- Extract entities: ["Coffee", "Heart Disease", "Type 2 Diabetes", "Antioxidants"]
- Extract relationships: [("Coffee", "reduces_risk_of", "Type 2 Diabetes")]
- Detect conflicts: Heart disease effects (some say good, some say bad)
↓
Knowledge Graph Created: Structured JSON with entities, relationships, conflicts
```

### Step 4: Adversarial Challenge (Adversary)
```
Weakness Analysis:
- "Coffee reduces anxiety" - only supported by 1 source (weakness!)
- "Coffee study from 2019" - getting outdated (weakness!)
↓
Counter-Queries Generated:
- "coffee anxiety increase caffeine"
- "coffee health risks 2024"
↓
New Search Round: Find counter-evidence
↓
Updated Knowledge Graph: Add conflicting information
```

### Step 5: Credibility Evaluation (Judge)
```
For each source:
- Harvard Health (.edu, recent, has citations) → 0.94 credibility
- Random blog (.com, old, no citations) → 0.35 credibility
↓
Annotated Knowledge Graph: Each relationship has credibility score
```

### Step 6: Final Synthesis
```
Analysis:
- Consensus: "Coffee contains antioxidants" (95% of sources agree)
- Battleground: "Coffee and heart disease" (sources conflict)
- Verdict: "Moderate coffee consumption likely beneficial" (high-credibility sources favor this)
↓
Final Report: Structured analysis with embedded knowledge graph JSON
```

## The Credibility Scoring System Explained

### Why Credibility Matters

Not all sources are created equal. A peer-reviewed study from Harvard Medical School should carry more weight than a random blog post. The credibility system quantifies this intuition.

### The Three Pillars of Credibility

#### 1. Domain Authority (40% of score)

This evaluates the reputation of the website:

```python
DOMAIN_SCORES = {
    # Government and Educational (Highest Trust)
    '.edu': 1.0,    # Universities
    '.gov': 1.0,    # Government agencies
    
    # Prestigious Organizations
    'nature.com': 0.95,      # Nature journal
    'nejm.org': 0.95,        # New England Journal of Medicine
    'who.int': 0.95,         # World Health Organization
    
    # Non-profits
    '.org': 0.8,             # Non-profit organizations
    
    # Reputable News
    'bbc.com': 0.75,         # BBC
    'reuters.com': 0.75,     # Reuters
    'nytimes.com': 0.75,     # New York Times
    
    # Reference Sites
    'wikipedia.org': 0.7,    # Wikipedia
    
    # Commercial (Default)
    '.com': 0.6              # Commercial sites
}
```

**Why this works:**
- Educational institutions have peer review processes
- Government agencies have regulatory oversight
- Prestigious journals have rigorous editorial standards
- Commercial sites may have conflicts of interest

#### 2. Citation Indicators (30% of score)

This looks for signs of academic rigor:

```python
def assess_academic_quality(content):
    score = 0.0
    
    # References section (+0.3)
    if has_references_section(content):
        score += 0.3
        
    # Academic citation format (+0.2)
    # Looks for: [1], [2] or (Smith, 2023) or (2023)
    if has_citation_format(content):
        score += 0.2
        
    # Author credentials (+0.3)  
    # Looks for: Dr., PhD, Professor, Researcher
    if has_author_credentials(content):
        score += 0.3
        
    return min(score, 1.0)  # Maximum 1.0
```

**Example Analysis:**
```
Article A: "Coffee is healthy according to recent studies [1][2][3]. 
Dr. Smith, a cardiologist at Harvard Medical School, notes..."
→ Has references ✓, citations ✓, credentials ✓ = 1.0

Article B: "I think coffee is great! My friend told me it's super healthy."
→ No references ✗, no citations ✗, no credentials ✗ = 0.0
```

#### 3. Recency (30% of score)

Science evolves. Newer research often has better methodology:

```python
def calculate_recency_score(publication_date):
    years_old = (today - publication_date).years
    
    if years_old < 1:
        return 1.0      # Very recent
    elif years_old < 2:
        return 0.8      # Recent
    elif years_old < 5:
        return 0.5      # Somewhat dated
    else:
        return 0.3      # Old
```

**Why recency matters:**
- Research methods improve over time
- Larger sample sizes in newer studies
- Better understanding of confounding factors
- Updated safety information

### Final Score Calculation

```python
final_credibility = (
    domain_authority * 0.4 +
    citation_indicators * 0.3 +
    recency * 0.3
)
```

**Real Examples:**

**High Credibility Source:**
- Harvard Health article (harvard.edu) = 1.0 domain
- Has references and author credentials = 0.8 citations  
- Published 6 months ago = 1.0 recency
- **Final Score: (1.0×0.4) + (0.8×0.3) + (1.0×0.3) = 0.94**

**Low Credibility Source:**
- Personal blog (myblog.com) = 0.6 domain
- No citations or credentials = 0.0 citations
- Published 4 years ago = 0.5 recency  
- **Final Score: (0.6×0.4) + (0.0×0.3) + (0.5×0.3) = 0.39**

## How Conflicts Are Detected and Resolved

### Conflict Detection Process

The Mapper Agent identifies conflicts by looking for contradictory claims:

```python
def detect_conflicts(relationships):
    conflicts = []
    
    # Group relationships by entity pairs
    entity_pairs = group_by_entity_pair(relationships)
    
    for (source_entity, target_entity), relations in entity_pairs.items():
        # Look for opposing relationships
        positive_relations = [r for r in relations if is_positive(r.relation)]
        negative_relations = [r for r in relations if is_negative(r.relation)]
        
        if positive_relations and negative_relations:
            conflict = Conflict(
                point_of_contention=f"{source_entity} effect on {target_entity}",
                side_a=positive_relations[0].relation,
                side_a_citation=positive_relations[0].citation,
                side_b=negative_relations[0].relation,
                side_b_citation=negative_relations[0].citation
            )
            conflicts.append(conflict)
    
    return conflicts
```

**Example Conflict Detection:**
```
Relationship 1: ("Coffee", "reduces_risk_of", "Heart Disease") - Harvard Study
Relationship 2: ("Coffee", "increases_risk_of", "Heart Disease") - Blog Post
↓
Conflict Detected: "Coffee effect on Heart Disease"
- Side A: "reduces risk" (Harvard)
- Side B: "increases risk" (Blog)
```

### Conflict Resolution Strategy

The Judge Agent resolves conflicts using credibility scores:

```python
def resolve_conflict(conflict):
    side_a_credibility = get_credibility(conflict.side_a_citation)
    side_b_credibility = get_credibility(conflict.side_b_citation)
    
    credibility_difference = abs(side_a_credibility - side_b_credibility)
    
    if credibility_difference > 0.2:  # Significant difference
        if side_a_credibility > side_b_credibility:
            verdict = f"Evidence favors: {conflict.side_a}"
            confidence = credibility_difference
        else:
            verdict = f"Evidence favors: {conflict.side_b}"
            confidence = credibility_difference
    else:
        verdict = "Evidence is mixed - more research needed"
        confidence = 0.5
    
    return verdict, confidence
```

**Example Resolution:**
```
Conflict: Coffee effect on Heart Disease
- Side A: "reduces risk" (Harvard Study, credibility: 0.94)
- Side B: "increases risk" (Blog Post, credibility: 0.39)
- Difference: 0.55 (significant)
↓
Verdict: "Evidence favors: Coffee reduces heart disease risk"
Confidence: 0.55 (moderate-high confidence)
```

### Types of Conflicts

1. **Direct Contradictions**: Same claim, opposite conclusions
   - "Coffee reduces anxiety" vs "Coffee increases anxiety"

2. **Magnitude Disputes**: Same direction, different strength
   - "Coffee slightly reduces diabetes risk" vs "Coffee dramatically reduces diabetes risk"

3. **Scope Disagreements**: Different populations or conditions
   - "Coffee is safe for healthy adults" vs "Coffee is dangerous for pregnant women"

4. **Temporal Conflicts**: Different time periods
   - "Short-term coffee consumption is safe" vs "Long-term coffee consumption causes problems"

## The Visualization System

### 2D Visualization (React Flow)

The 2D visualization uses React Flow to create an interactive graph:

```typescript
interface GraphNode {
  id: string;
  type: 'entity' | 'conflict';
  data: {
    label: string;
    credibility?: number;
    citations?: string[];
  };
  position: { x: number; y: number };
}

interface GraphEdge {
  id: string;
  source: string;
  target: string;
  label: string;
  type: 'support' | 'refute' | 'neutral';
  data: {
    citation: string;
    credibility: number;
  };
}
```

**Visual Encoding:**
- **Node Size**: Larger nodes = more connections (more important concepts)
- **Node Color**: Different colors for different entity types
- **Edge Color**: 
  - Green = positive relationship ("reduces risk")
  - Red = negative relationship ("increases risk")  
  - Gray = neutral relationship ("is related to")
- **Edge Thickness**: Thicker edges = higher credibility
- **Conflict Nodes**: Special pulsing border to draw attention

### 3D Visualization (Three.js)

The 3D visualization provides an immersive experience:

```typescript
// 3D Scene Setup
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, width/height, 0.1, 1000);
const renderer = new THREE.WebGLRenderer();

// Node Representation
class EntityNode3D {
  geometry = new THREE.SphereGeometry(radius);
  material = new THREE.MeshPhongMaterial({ color: nodeColor });
  mesh = new THREE.Mesh(geometry, material);
  
  // Size based on centrality
  radius = Math.log(connectionCount + 1) * 2;
}

// Relationship Visualization
class RelationshipEdge3D {
  // Animated particle trail between nodes
  particles = new THREE.Points(particleGeometry, particleMaterial);
  
  animate() {
    // Move particles along the edge path
    particles.position.lerp(targetPosition, 0.02);
  }
}
```

**3D Features:**
- **Physics Simulation**: Nodes repel each other, edges pull connected nodes together
- **Particle Trails**: Animated particles flow along edges to show relationships
- **Orbital Camera**: Smooth camera controls for exploration
- **Floating UI**: Information panels that follow nodes in 3D space
- **Real-time Filtering**: Hide/show nodes and edges dynamically

### Analytics Dashboard

The dashboard provides quantitative insights:

```typescript
interface GraphMetrics {
  nodeCount: number;
  edgeCount: number;
  conflictCount: number;
  averageCredibility: number;
  centralityScores: { [nodeId: string]: number };
  clusteringCoefficient: number;
  graphDensity: number;
}

// Centrality calculation (how "important" each node is)
function calculateCentrality(graph: Graph): { [nodeId: string]: number } {
  const centrality = {};
  
  for (const node of graph.nodes) {
    // Count direct connections
    const connections = graph.edges.filter(e => 
      e.source === node.id || e.target === node.id
    ).length;
    
    centrality[node.id] = connections;
  }
  
  return centrality;
}
```

**Dashboard Components:**
- **Graph Statistics**: Node count, edge count, conflict count
- **Credibility Distribution**: Histogram of source credibility scores
- **Centrality Analysis**: Which concepts are most connected
- **Conflict Analysis**: Types and frequency of disagreements
- **Timeline View**: How the graph evolved through research iterations

## Real-World Example Walkthrough

Let's trace through a complete research session on "Is coffee good for health?"

### Phase 1: Scout Agent Search

**Initial Queries:**
```
1. "coffee health benefits research"
2. "coffee health effects studies" 
3. "coffee medical research"
```

**Sources Found:**
```json
[
  {
    "url": "https://www.hsph.harvard.edu/news/hsph-in-the-news/coffee-health-benefits/",
    "title": "Coffee Health Benefits - Harvard School of Public Health",
    "domain": "harvard.edu",
    "content": "Multiple studies suggest coffee consumption is associated with reduced risk of type 2 diabetes, Parkinson's disease, and liver disease..."
  },
  {
    "url": "https://www.mayoclinic.org/healthy-lifestyle/nutrition-and-healthy-eating/in-depth/coffee/art-20045963",
    "title": "Coffee: Health benefits and risks - Mayo Clinic", 
    "domain": "mayoclinic.org",
    "content": "For most healthy adults, moderate coffee consumption appears to be safe and may provide health benefits..."
  },
  // ... 8 more sources
]
```

### Phase 2: Mapper Agent Analysis

**Entities Extracted:**
```json
[
  "Coffee", "Caffeine", "Type 2 Diabetes", "Heart Disease", 
  "Parkinson's Disease", "Liver Disease", "Anxiety", "Sleep",
  "Antioxidants", "Polyphenols", "Blood Pressure"
]
```

**Relationships Extracted:**
```json
[
  {
    "source": "Coffee",
    "relation": "reduces_risk_of",
    "target": "Type 2 Diabetes", 
    "citation": "Harvard School of Public Health"
  },
  {
    "source": "Coffee",
    "relation": "may_increase",
    "target": "Anxiety",
    "citation": "Mayo Clinic"
  },
  {
    "source": "Caffeine",
    "relation": "can_disrupt", 
    "target": "Sleep",
    "citation": "Sleep Foundation"
  }
]
```

**Conflicts Detected:**
```json
[
  {
    "point_of_contention": "Coffee effect on Heart Disease",
    "side_a": "Coffee consumption associated with reduced cardiovascular risk",
    "side_a_citation": "Harvard Health",
    "side_b": "High coffee intake may increase heart palpitations",
    "side_b_citation": "WebMD"
  }
]
```

### Phase 3: Adversary Agent Challenge

**Weakness Analysis:**
```
Weaknesses Found:
1. "Coffee reduces liver disease risk" - supported by only 1 source
2. "Coffee study from 2019" - getting outdated
3. Most sources are from health institutions - potential bias toward positive findings
```

**Counter-Queries Generated:**
```
1. "coffee health risks cardiovascular 2024"
2. "negative effects daily caffeine consumption"
3. "coffee addiction withdrawal symptoms"
```

**New Sources Found:**
```json
[
  {
    "url": "https://www.heart.org/coffee-risks-study",
    "title": "New Study Links High Coffee Intake to Heart Rhythm Issues",
    "content": "A 2024 study of 100,000 participants found that consuming more than 6 cups of coffee daily was associated with increased risk of atrial fibrillation..."
  }
]
```

### Phase 4: Judge Agent Credibility Scoring

**Credibility Scores Assigned:**
```json
[
  {
    "source": "Harvard School of Public Health",
    "domain_authority": 1.0,
    "citation_indicators": 0.9,
    "recency": 0.8,
    "overall_score": 0.91
  },
  {
    "source": "Mayo Clinic", 
    "domain_authority": 0.95,
    "citation_indicators": 0.8,
    "recency": 1.0,
    "overall_score": 0.89
  },
  {
    "source": "WebMD",
    "domain_authority": 0.6,
    "citation_indicators": 0.4,
    "recency": 0.7,
    "overall_score": 0.55
  }
]
```

### Phase 5: Synthesis Agent Report

**Final Report Structure:**

```markdown
# Coffee and Health: Research Analysis

## The Consensus (90%+ agreement)
- Coffee contains beneficial antioxidants and polyphenols
- Moderate consumption (3-5 cups/day) appears safe for most healthy adults
- Coffee is associated with reduced risk of Type 2 diabetes
- Coffee may have protective effects against Parkinson's disease

## The Battleground (Major disagreements)

### Heart Disease Effects
**Conflicting Claims:**
- Side A: "Coffee reduces cardiovascular disease risk" (Harvard Health, credibility: 0.91)
- Side B: "High coffee intake increases heart rhythm problems" (Heart.org, credibility: 0.87)

**Why they disagree:** Different dosage levels studied (moderate vs. high consumption)

**Verdict:** Evidence suggests moderate coffee consumption (3-5 cups) may be beneficial, but high consumption (6+ cups) may pose risks. Confidence: 0.75

### Anxiety and Sleep Effects  
**Conflicting Claims:**
- Side A: "Coffee increases anxiety in sensitive individuals" (Mayo Clinic, credibility: 0.89)
- Side B: "Coffee has no significant anxiety effects in regular users" (Blog, credibility: 0.35)

**Verdict:** Evidence favors that coffee can increase anxiety, especially in caffeine-sensitive individuals. Confidence: 0.54

## Key Insights
1. **Dosage matters**: Benefits seen at 3-5 cups/day, risks at 6+ cups/day
2. **Individual variation**: Effects vary significantly between people
3. **Timing matters**: Avoid coffee 6+ hours before bedtime
4. **Quality of evidence**: Most high-quality studies support moderate consumption

## Knowledge Graph JSON
{
  "entities": ["Coffee", "Heart Disease", "Type 2 Diabetes", ...],
  "relationships": [...],
  "conflicts": [...]
}
```

## API and Integration Guide

### Starting a Research Session

**Request:**
```http
POST /api/research
Content-Type: application/json

{
  "topic": "Is coffee good for health?",
  "max_iterations": 3,
  "min_sources": 10
}
```

**Response:**
```json
{
  "session_id": "research_abc123",
  "status": "started",
  "estimated_duration": "5-10 minutes",
  "message": "Research workflow initiated"
}
```

### Monitoring Progress

**Request:**
```http
GET /api/research/research_abc123/status
```

**Response (In Progress):**
```json
{
  "session_id": "research_abc123", 
  "status": "in_progress",
  "current_phase": "mapper",
  "iteration": 1,
  "progress": {
    "sources_collected": 12,
    "entities_extracted": 25,
    "relationships_found": 45,
    "conflicts_detected": 3
  },
  "estimated_remaining": "3-5 minutes"
}
```

**Response (Completed):**
```json
{
  "session_id": "research_abc123",
  "status": "completed", 
  "total_duration": "8 minutes",
  "final_stats": {
    "sources_analyzed": 15,
    "entities_found": 35,
    "relationships_mapped": 67,
    "conflicts_identified": 5,
    "iterations_completed": 2
  }
}
```

### Retrieving Results

**Get Knowledge Graph:**
```http
GET /api/research/research_abc123/graph
```

**Response:**
```json
{
  "nodes": [
    {
      "id": "coffee",
      "type": "entity",
      "data": {
        "label": "Coffee",
        "connections": 12,
        "centrality": 0.85
      },
      "position": { "x": 100, "y": 200 }
    }
  ],
  "edges": [
    {
      "id": "coffee_diabetes",
      "source": "coffee", 
      "target": "type2_diabetes",
      "label": "reduces risk of",
      "type": "support",
      "data": {
        "citation": "Harvard Health Study",
        "credibility": 0.91
      }
    }
  ]
}
```

**Get Final Report:**
```http
GET /api/research/research_abc123/report
```

**Response:**
```json
{
  "report": "# Coffee and Health: Research Analysis\n\n## The Consensus...",
  "metadata": {
    "word_count": 1250,
    "reading_time": "5 minutes",
    "credibility_weighted_score": 0.78
  }
}
```

### WebSocket Real-Time Updates

For real-time progress updates:

```javascript
const ws = new WebSocket('ws://localhost:8000/api/research/research_abc123/stream');

ws.onmessage = (event) => {
  const update = JSON.parse(event.data);
  
  switch(update.type) {
    case 'phase_change':
      console.log(`Now in ${update.phase} phase`);
      break;
    case 'sources_found':
      console.log(`Found ${update.count} new sources`);
      break;
    case 'conflict_detected':
      console.log(`New conflict: ${update.conflict.point_of_contention}`);
      break;
    case 'completed':
      console.log('Research completed!');
      break;
  }
};
```

## Understanding the Code Structure

### Project Organization

```
adversarial-knowledge-cartographer/
├── agents/                    # AI agent implementations
│   ├── scout.py              # Web search and content extraction
│   ├── mapper.py             # Knowledge graph construction
│   ├── adversary.py          # Counter-evidence search
│   ├── judge.py              # Credibility evaluation
│   ├── synthesis.py          # Report generation
│   └── workflow.py           # LangGraph orchestration
├── models/                   # Data structures
│   └── data_models.py        # Pydantic models for all data types
├── utils/                    # Utility functions
│   ├── llm_factory.py        # LLM client management
│   ├── error_handling.py     # Error recovery logic
│   └── logging_config.py     # Structured logging setup
├── api/                      # FastAPI backend
│   └── app.py                # REST API endpoints
├── frontend/                 # React visualization
│   ├── src/components/       # React components
│   ├── src/services/         # API client
│   └── src/types/            # TypeScript types
└── tests/                    # Test suite
    ├── test_*_properties.py  # Property-based tests
    └── test_*_units.py       # Unit tests
```

### Key Code Patterns

**Agent Base Class:**
```python
from abc import ABC, abstractmethod
from models.data_models import WorkflowState

class BaseAgent(ABC):
    def __init__(self, llm_client):
        self.llm = llm_client
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    def execute(self, state: WorkflowState) -> WorkflowState:
        """Execute agent logic and return updated state"""
        pass
    
    def execute_with_retry(self, state: WorkflowState, max_retries=3) -> WorkflowState:
        """Execute with error handling and retries"""
        for attempt in range(max_retries):
            try:
                return self.execute(state)
            except Exception as e:
                self.logger.warning(f"Attempt {attempt + 1} failed: {e}")
                if attempt == max_retries - 1:
                    raise
                time.sleep(2 ** attempt)  # Exponential backoff
```

**Structured Output Pattern:**
```python
from pydantic import BaseModel
from typing import List

class KnowledgeGraphOutput(BaseModel):
    entities: List[str]
    relationships: List[Relationship] 
    conflicts: List[Conflict]

class MapperAgent(BaseAgent):
    def extract_knowledge(self, sources: List[Source]) -> KnowledgeGraph:
        prompt = self.build_prompt(sources)
        
        # Use structured output to ensure valid JSON
        response = self.llm.with_structured_output(KnowledgeGraphOutput).invoke(prompt)
        
        # Validate and return
        return KnowledgeGraph(
            entities=response.entities,
            relationships=response.relationships,
            conflicts=response.conflicts
        )
```

**State Management Pattern:**
```python
from langgraph import StateGraph, END

def create_workflow():
    workflow = StateGraph(WorkflowState)
    
    # Add nodes (agents)
    workflow.add_node("scout", scout_agent.execute)
    workflow.add_node("mapper", mapper_agent.execute)
    workflow.add_node("adversary", adversary_agent.execute)
    workflow.add_node("judge", judge_agent.execute)
    workflow.add_node("synthesis", synthesis_agent.execute)
    
    # Add edges (transitions)
    workflow.add_edge("scout", "mapper")
    workflow.add_edge("mapper", "adversary")
    
    # Conditional edge for iteration
    workflow.add_conditional_edges(
        "adversary",
        should_continue_iteration,  # Function that decides
        {
            "continue": "scout",    # Loop back for more evidence
            "finish": "judge"       # Move to final phases
        }
    )
    
    workflow.add_edge("judge", "synthesis")
    workflow.add_edge("synthesis", END)
    
    return workflow.compile()
```

## Testing and Quality Assurance

### Property-Based Testing

The system uses property-based testing to verify universal properties:

```python
from hypothesis import given, strategies as st
import pytest

@given(st.text(min_size=1, max_size=100))
def test_property_1_workflow_initialization(topic):
    """Feature: adversarial-knowledge-cartographer, Property 1: 
    Workflow initialization with valid topics"""
    # Skip invalid topics
    assume(topic.strip() and not topic.isspace())
    
    workflow = WorkflowOrchestrator()
    state = workflow.initialize(topic)
    
    # Universal properties that should always hold
    assert state.current_phase == "scout"
    assert state.topic == topic
    assert state.iteration == 0
    assert len(state.sources) == 0
    assert state.status_message is not None

@given(st.lists(st.builds(Source), min_size=1, max_size=20))
def test_property_3_scout_source_diversity(sources):
    """Feature: adversarial-knowledge-cartographer, Property 3:
    Scout phase source diversity"""
    scout = ScoutAgent()
    
    # Mock the search to return our test sources
    with mock.patch.object(scout, 'search_web', return_value=sources):
        state = WorkflowState(topic="test", sources=[])
        result_state = scout.execute(state)
        
        # Property: Should have diverse domains
        domains = {extract_domain(s.url) for s in result_state.sources}
        assert len(domains) >= min(len(sources), 3)  # At least 3 different domains
```

### Unit Testing

Unit tests verify specific functionality:

```python
def test_credibility_score_calculation():
    """Test credibility scoring with known inputs"""
    judge = JudgeAgent()
    
    # High credibility source
    harvard_source = Source(
        url="https://www.harvard.edu/health/coffee-study",
        content="Dr. Smith et al. (2024) found in a study of 50,000 participants [1][2]...",
        retrieved_at=datetime.now() - timedelta(days=30)
    )
    
    score = judge.calculate_credibility(harvard_source)
    
    assert 0.8 <= score <= 1.0  # Should be high credibility
    
    # Low credibility source
    blog_source = Source(
        url="https://myblog.com/coffee-thoughts",
        content="I think coffee is great! My friend says it's healthy.",
        retrieved_at=datetime.now() - timedelta(days=1000)
    )
    
    score = judge.calculate_credibility(blog_source)
    
    assert 0.0 <= score <= 0.5  # Should be low credibility

def test_conflict_detection():
    """Test that conflicts are properly identified"""
    mapper = MapperAgent()
    
    sources = [
        Source(content="Coffee reduces heart disease risk according to Harvard study"),
        Source(content="Coffee increases cardiovascular problems says Mayo Clinic")
    ]
    
    knowledge_graph = mapper.extract_knowledge(sources)
    
    # Should detect the conflict
    assert len(knowledge_graph.conflicts) >= 1
    
    conflict = knowledge_graph.conflicts[0]
    assert "heart" in conflict.point_of_contention.lower()
    assert conflict.side_a != conflict.side_b
```

### Integration Testing

Integration tests verify the complete workflow:

```python
@pytest.mark.integration
def test_end_to_end_coffee_research(mock_search_api, mock_llm):
    """Test complete research workflow with mocked external services"""
    
    # Mock search results
    mock_search_api.return_value = [
        Source(url="https://harvard.edu/coffee", content="Coffee reduces diabetes risk"),
        Source(url="https://mayo.org/coffee", content="Coffee may increase anxiety"),
        # ... more sources
    ]
    
    # Mock LLM responses
    mock_llm.side_effect = [
        # Mapper response
        KnowledgeGraphOutput(
            entities=["Coffee", "Diabetes", "Anxiety"],
            relationships=[
                Relationship(source="Coffee", relation="reduces_risk_of", target="Diabetes", citation="Harvard")
            ],
            conflicts=[
                Conflict(point_of_contention="Coffee anxiety effects", ...)
            ]
        ),
        # Adversary response
        AdversarialOutput(
            weaknesses=[Weakness(type="single_source", ...)],
            counter_queries=["coffee anxiety increase studies"]
        ),
        # Synthesis response
        "# Coffee Research Report\n\n## Consensus\n..."
    ]
    
    # Execute workflow
    orchestrator = WorkflowOrchestrator()
    result = orchestrator.execute("coffee health effects")
    
    # Verify results
    assert result.status == "completed"
    assert len(result.knowledge_graph.entities) > 0
    assert len(result.knowledge_graph.conflicts) > 0
    assert result.synthesis_report is not None
    assert "consensus" in result.synthesis_report.lower()
```

### Performance Testing

```python
def test_workflow_performance():
    """Ensure workflow completes within reasonable time"""
    start_time = time.time()
    
    orchestrator = WorkflowOrchestrator()
    result = orchestrator.execute("coffee health", max_sources=5)  # Smaller test
    
    duration = time.time() - start_time
    
    # Should complete within 2 minutes for small test
    assert duration < 120
    assert result.status == "completed"

def test_visualization_performance():
    """Ensure visualization renders quickly"""
    # Create large test graph
    large_graph = create_test_graph(nodes=100, edges=200)
    
    start_time = time.time()
    
    # Render graph
    visualization = GraphVisualization(large_graph)
    rendered_data = visualization.prepare_for_frontend()
    
    render_time = time.time() - start_time
    
    # Should render within 3 seconds
    assert render_time < 3.0
    assert len(rendered_data['nodes']) == 100
    assert len(rendered_data['edges']) == 200
```

This comprehensive guide should give beginners a deep understanding of how the Adversarial Knowledge Cartographer works, from the high-level concept down to the technical implementation details. The system combines multiple AI agents, credibility evaluation, conflict detection, and advanced visualization to create a powerful research tool that goes far beyond simple information summarization.