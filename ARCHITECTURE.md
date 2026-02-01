# Architecture Documentation

## System Architecture Overview

The Adversarial Knowledge Cartographer implements a multi-agent workflow using LangGraph for orchestration. The system follows a dialectic reasoning pattern where specialized agents collaborate to gather, analyze, challenge, and synthesize research findings.

## High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Interface                          │
│  ┌──────────────────┐              ┌──────────────────────┐    │
│  │  CLI Interface   │              │  Web Frontend (React)│    │
│  │   (main.py)      │              │   + React Flow       │    │
│  └────────┬─────────┘              └──────────┬───────────┘    │
│           │                                    │                 │
└───────────┼────────────────────────────────────┼─────────────────┘
            │                                    │
            │                                    │ HTTP/REST
            │                                    │
┌───────────▼────────────────────────────────────▼─────────────────┐
│                      FastAPI Backend                             │
│  ┌────────────────────────────────────────────────────────┐     │
│  │              API Endpoints                              │     │
│  │  POST /api/research                                     │     │
│  │  GET  /api/research/{id}/status                        │     │
│  │  GET  /api/research/{id}/graph                         │     │
│  │  GET  /api/research/{id}/report                        │     │
│  └────────────────────┬───────────────────────────────────┘     │
└───────────────────────┼───────────────────────────────────────────┘
                        │
                        │
┌───────────────────────▼───────────────────────────────────────────┐
│                  Workflow Orchestrator (LangGraph)                │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                   State Machine                           │   │
│  │                                                           │   │
│  │   ┌─────────┐    ┌─────────┐    ┌──────────┐           │   │
│  │   │ Scout   │───▶│ Mapper  │───▶│Adversary │           │   │
│  │   │ Agent   │    │ Agent   │    │  Agent   │           │   │
│  │   └─────────┘    └─────────┘    └────┬─────┘           │   │
│  │                                       │                  │   │
│  │                                       │ Weak claims?     │   │
│  │                                       │                  │   │
│  │                                  ┌────▼─────┐           │   │
│  │                                  │ Decision │           │   │
│  │                                  │   Node   │           │   │
│  │                                  └────┬─────┘           │   │
│  │                                       │                  │   │
│  │                              Yes ◀────┘────▶ No         │   │
│  │                               │              │           │   │
│  │                          Loop back      ┌────▼─────┐    │   │
│  │                          (max 3x)       │  Judge   │    │   │
│  │                                         │  Agent   │    │   │
│  │                                         └────┬─────┘    │   │
│  │                                              │           │   │
│  │                                         ┌────▼─────┐    │   │
│  │                                         │Synthesis │    │   │
│  │                                         │  Agent   │    │   │
│  │                                         └──────────┘    │   │
│  └──────────────────────────────────────────────────────────┘   │
└───────────────────────────────────────────────────────────────────┘

## Agent Architecture

### Scout Agent
```
┌─────────────────────────────────────────────────────────┐
│                    Scout Agent                          │
│                                                         │
│  Input: Topic string + Optional adversarial queries    │
│                                                         │
│  ┌─────────────────────────────────────────────────┐  │
│  │  1. Generate search queries                     │  │
│  │     - Broad queries for initial search          │  │
│  │     - Targeted queries for adversarial search   │  │
│  └─────────────────┬───────────────────────────────┘  │
│                    │                                    │
│  ┌─────────────────▼───────────────────────────────┐  │
│  │  2. Execute web searches                        │  │
│  │     - Tavily API (primary)                      │  │
│  │     - Serper API (fallback)                     │  │
│  │     - Diversity mode enabled                    │  │
│  └─────────────────┬───────────────────────────────┘  │
│                    │                                    │
│  ┌─────────────────▼───────────────────────────────┐  │
│  │  3. Extract content                             │  │
│  │     - Trafilatura for clean text                │  │
│  │     - BeautifulSoup for HTML parsing            │  │
│  │     - Filter paywalled content                  │  │
│  └─────────────────┬───────────────────────────────┘  │
│                    │                                    │
│  ┌─────────────────▼───────────────────────────────┐  │
│  │  4. Validate and deduplicate                    │  │
│  │     - Ensure minimum source count               │  │
│  │     - Unique domains                            │  │
│  │     - Complete Source objects                   │  │
│  └─────────────────┬───────────────────────────────┘  │
│                    │                                    │
│  Output: List[Source]                                  │
└────────────────────┼────────────────────────────────────┘
                     │
                     ▼
              WorkflowState.sources
```

### Mapper Agent
```
┌─────────────────────────────────────────────────────────┐
│                    Mapper Agent                         │
│                                                         │
│  Input: List[Source]                                   │
│                                                         │
│  ┌─────────────────────────────────────────────────┐  │
│  │  1. Prepare LLM prompt                          │  │
│  │     - System: "You are a Knowledge Cartographer"│  │
│  │     - Include all source content                │  │
│  │     - Specify JSON schema                       │  │
│  └─────────────────┬───────────────────────────────┘  │
│                    │                                    │
│  ┌─────────────────▼───────────────────────────────┐  │
│  │  2. LLM structured output                       │  │
│  │     - Function calling mode                     │  │
│  │     - Pydantic schema enforcement               │  │
│  │     - Retry on malformed JSON                   │  │
│  └─────────────────┬───────────────────────────────┘  │
│                    │                                    │
│  ┌─────────────────▼───────────────────────────────┐  │
│  │  3. Extract entities                            │  │
│  │     - Deduplicate with fuzzy matching           │  │
│  │     - Edit distance < 3                         │  │
│  │     - Maintain unique list                      │  │
│  └─────────────────┬───────────────────────────────┘  │
│                    │                                    │
│  ┌─────────────────▼───────────────────────────────┐  │
│  │  4. Extract relationships                       │  │
│  │     - Knowledge Triplets (source-relation-target)│ │
│  │     - Include citations                         │  │
│  │     - Validate references                       │  │
│  └─────────────────┬───────────────────────────────┘  │
│                    │                                    │
│  ┌─────────────────▼───────────────────────────────┐  │
│  │  5. Detect conflicts                            │  │
│  │     - Identify contradictions                   │  │
│  │     - Extract both sides with citations         │  │
│  └─────────────────┬───────────────────────────────┘  │
│                    │                                    │
│  ┌─────────────────▼───────────────────────────────┐  │
│  │  6. Build KnowledgeGraph                        │  │
│  │     - Validate referential integrity            │  │
│  │     - Serialize to JSON                         │  │
│  └─────────────────┬───────────────────────────────┘  │
│                    │                                    │
│  Output: KnowledgeGraph                                │
└────────────────────┼────────────────────────────────────┘
                     │
                     ▼
         WorkflowState.knowledge_graph
```

### Adversary Agent
```
┌─────────────────────────────────────────────────────────┐
│                  Adversary Agent                        │
│                                                         │
│  Input: KnowledgeGraph + Sources                       │
│                                                         │
│  ┌─────────────────────────────────────────────────┐  │
│  │  1. Analyze weaknesses                          │  │
│  │     - Single-source claims                      │  │
│  │     - Outdated sources (>2 years)               │  │
│  │     - Potential bias indicators                 │  │
│  └─────────────────┬───────────────────────────────┘  │
│                    │                                    │
│  ┌─────────────────▼───────────────────────────────┐  │
│  │  2. Generate counter-queries                    │  │
│  │     - Minimum 3 queries                         │  │
│  │     - Designed to debunk findings               │  │
│  │     - Target weak claims                        │  │
│  └─────────────────┬───────────────────────────────┘  │
│                    │                                    │
│  ┌─────────────────▼───────────────────────────────┐  │
│  │  3. Deduplicate queries                         │  │
│  │     - Check against executed_queries            │  │
│  │     - Prevent redundant searches                │  │
│  └─────────────────┬───────────────────────────────┘  │
│                    │                                    │
│  Output: List[str] adversarial_queries                 │
└────────────────────┼────────────────────────────────────┘
                     │
                     ▼
        WorkflowState.adversarial_queries
```

### Judge Agent
```
┌─────────────────────────────────────────────────────────┐
│                    Judge Agent                          │
│                                                         │
│  Input: KnowledgeGraph + Sources                       │
│                                                         │
│  ┌─────────────────────────────────────────────────┐  │
│  │  1. Calculate domain authority                  │  │
│  │     - .edu, .gov: 1.0                           │  │
│  │     - .org: 0.8                                 │  │
│  │     - .com: 0.5-0.7                             │  │
│  └─────────────────┬───────────────────────────────┘  │
│                    │                                    │
│  ┌─────────────────▼───────────────────────────────┐  │
│  │  2. Assess citation indicators                  │  │
│  │     - References present: +0.3                  │  │
│  │     - Academic formatting: +0.2                 │  │
│  │     - Author credentials: +0.3                  │  │
│  └─────────────────┬───────────────────────────────┘  │
│                    │                                    │
│  ┌─────────────────▼───────────────────────────────┐  │
│  │  3. Calculate recency score                     │  │
│  │     - <1 year: 1.0                              │  │
│  │     - 1-2 years: 0.8                            │  │
│  │     - 2-5 years: 0.5                            │  │
│  │     - >5 years: 0.3                             │  │
│  └─────────────────┬───────────────────────────────┘  │
│                    │                                    │
│  ┌─────────────────▼───────────────────────────────┐  │
│  │  4. Compute overall credibility                 │  │
│  │     - Weighted average:                         │  │
│  │       domain * 0.4 + citation * 0.3 + recency * 0.3│
│  │     - Normalize to [0.0, 1.0]                   │  │
│  └─────────────────┬───────────────────────────────┘  │
│                    │                                    │
│  ┌─────────────────▼───────────────────────────────┐  │
│  │  5. Annotate graph                              │  │
│  │     - Add credibility to relationships          │  │
│  │     - Add credibility to conflict sides         │  │
│  └─────────────────┬───────────────────────────────┘  │
│                    │                                    │
│  Output: KnowledgeGraph (with credibility scores)      │
└────────────────────┼────────────────────────────────────┘
                     │
                     ▼
         WorkflowState.knowledge_graph
```

### Synthesis Agent
```
┌─────────────────────────────────────────────────────────┐
│                  Synthesis Agent                        │
│                                                         │
│  Input: KnowledgeGraph (with credibility)              │
│                                                         │
│  ┌─────────────────────────────────────────────────┐  │
│  │  1. Identify consensus                          │  │
│  │     - Claims with >90% source agreement         │  │
│  │     - Extract consensus points                  │  │
│  └─────────────────┬───────────────────────────────┘  │
│                    │                                    │
│  ┌─────────────────▼───────────────────────────────┐  │
│  │  2. Analyze battleground                        │  │
│  │     - Extract conflicts from graph              │  │
│  │     - Identify disagreement reasons             │  │
│  │     - Compare methodologies/datasets            │  │
│  └─────────────────┬───────────────────────────────┘  │
│                    │                                    │
│  ┌─────────────────▼───────────────────────────────┐  │
│  │  3. Generate verdicts                           │  │
│  │     - Use credibility scores                    │  │
│  │     - Determine likely correct claims           │  │
│  │     - Provide confidence levels                 │  │
│  └─────────────────┬───────────────────────────────┘  │
│                    │                                    │
│  ┌─────────────────▼───────────────────────────────┐  │
│  │  4. Structure report                            │  │
│  │     - Consensus section                         │  │
│  │     - Battleground section                      │  │
│  │     - Verdict section                           │  │
│  │     - Append KnowledgeGraph JSON                │  │
│  └─────────────────┬───────────────────────────────┘  │
│                    │                                    │
│  Output: SynthesisReport (string)                      │
└────────────────────┼────────────────────────────────────┘
                     │
                     ▼
         WorkflowState.synthesis_report
```

## Data Flow Architecture

```
┌──────────────┐
│ User Input   │
│   (Topic)    │
└──────┬───────┘
       │
       ▼
┌──────────────────────────────────────────────────────┐
│              WorkflowState                           │
│  ┌────────────────────────────────────────────────┐ │
│  │ topic: str                                     │ │
│  │ iteration: int                                 │ │
│  │ sources: List[Source]                          │ │
│  │ knowledge_graph: KnowledgeGraph                │ │
│  │ adversarial_queries: List[str]                 │ │
│  │ executed_queries: Set[str]                     │ │
│  │ synthesis_report: Optional[str]                │ │
│  │ max_iterations: int = 3                        │ │
│  └────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────┐
│              Scout Phase                             │
│  Input: topic + adversarial_queries                  │
│  Output: sources                                     │
└──────┬───────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────┐
│              Mapper Phase                            │
│  Input: sources                                      │
│  Output: knowledge_graph                             │
│          (entities, relationships, conflicts)        │
└──────┬───────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────┐
│            Adversary Phase                           │
│  Input: knowledge_graph + sources                    │
│  Output: adversarial_queries                         │
└──────┬───────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────┐
│           Decision Node                              │
│  Condition: adversarial_queries AND iteration < max  │
│  Yes: Loop back to Scout Phase                       │
│  No: Continue to Judge Phase                         │
└──────┬───────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────┐
│              Judge Phase                             │
│  Input: knowledge_graph + sources                    │
│  Output: knowledge_graph (with credibility scores)   │
└──────┬───────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────┐
│            Synthesis Phase                           │
│  Input: knowledge_graph (with credibility)           │
│  Output: synthesis_report                            │
└──────┬───────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────┐
│              Final Output                            │
│  - Synthesis Report (Markdown)                       │
│  - Knowledge Graph (JSON)                            │
│  - Visualization Data (nodes + edges)                │
└──────────────────────────────────────────────────────┘
```

## Data Models

### Core Models Hierarchy

```
WorkflowState
├── topic: str
├── iteration: int
├── sources: List[Source]
│   └── Source
│       ├── url: str
│       ├── title: str
│       ├── content: str
│       ├── domain: str
│       ├── retrieved_at: datetime
│       └── query_used: str
├── knowledge_graph: KnowledgeGraph
│   ├── entities: List[str]
│   ├── relationships: List[Relationship]
│   │   └── Relationship
│   │       ├── source: str
│   │       ├── relation: str
│   │       ├── target: str
│   │       ├── citation: str
│   │       └── credibility: float
│   └── conflicts: List[Conflict]
│       └── Conflict
│           ├── point_of_contention: str
│           ├── side_a: str
│           ├── side_a_citation: str
│           ├── side_a_credibility: float
│           ├── side_b: str
│           ├── side_b_citation: str
│           └── side_b_credibility: float
├── adversarial_queries: List[str]
├── executed_queries: Set[str]
├── synthesis_report: Optional[str]
└── max_iterations: int
```

## Technology Stack

### Backend

```
┌─────────────────────────────────────────────────────┐
│                  Python 3.11+                       │
├─────────────────────────────────────────────────────┤
│  Core Framework                                     │
│  ├── LangGraph: State machine orchestration        │
│  ├── LangChain: LLM integration                    │
│  └── Pydantic: Data validation                     │
├─────────────────────────────────────────────────────┤
│  LLM Integration                                    │
│  ├── OpenAI GPT-4 / GPT-4-turbo                    │
│  └── Anthropic Claude-3                            │
├─────────────────────────────────────────────────────┤
│  Search & Retrieval                                 │
│  ├── Tavily API: Web search                        │
│  ├── Serper API: Alternative search                │
│  ├── Trafilatura: Content extraction               │
│  └── BeautifulSoup4: HTML parsing                  │
├─────────────────────────────────────────────────────┤
│  API Layer                                          │
│  ├── FastAPI: REST API framework                   │
│  ├── Uvicorn: ASGI server                          │
│  └── Pydantic: Request/response validation         │
├─────────────────────────────────────────────────────┤
│  Testing                                            │
│  ├── pytest: Test framework                        │
│  ├── Hypothesis: Property-based testing            │
│  └── pytest-mock: Mocking utilities                │
└─────────────────────────────────────────────────────┘
```

### Frontend

```
┌─────────────────────────────────────────────────────┐
│                  React 19 + TypeScript              │
├─────────────────────────────────────────────────────┤
│  Visualization                                      │
│  └── React Flow: Graph rendering                   │
├─────────────────────────────────────────────────────┤
│  HTTP Client                                        │
│  └── Axios: API communication                      │
├─────────────────────────────────────────────────────┤
│  Testing                                            │
│  └── React Testing Library: Component tests        │
└─────────────────────────────────────────────────────┘
```

## Deployment Architecture

### Development Environment

```
┌─────────────────────────────────────────────────────┐
│ 