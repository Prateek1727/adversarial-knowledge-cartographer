# Adversarial Knowledge Cartographer

> A production-grade multi-agent AI research system that transforms controversial topics into structured knowledge graphs with conflict detection and transparent credibility scoring.

## What It Does

This system automates the research process that would normally take hours of manual work. Instead of just summarizing information, it actively seeks out contradictions and evaluates source trustworthiness to give you a balanced, evidence-based analysis.

The system transforms research topics into structured knowledge graphs by:
- Gathering 30-50 sources from web searches across diverse domains
- Extracting entities (concepts) and relationships between them
- Identifying conflicts where sources disagree
- Scoring source credibility using transparent algorithms
- Generating comprehensive reports with consensus points and battleground topics
- Creating interactive 2D and 3D visualizations of the knowledge landscape

## How It Differs from ChatGPT/Gemini

**ChatGPT/Gemini**: Provide single-perspective answers based on training data, may present biased or incomplete information without highlighting contradictions.

**This System**:
- **Actively seeks contradictions** - Uses an adversarial agent to challenge its own findings
- **Models conflicts explicitly** - Presents both sides of disagreements with credibility scores
- **Transparent source evaluation** - Shows exactly why sources are trusted (domain, citations, recency)
- **Structured knowledge graphs** - Visualizes relationships and conflicts, not just text
- **Iterative refinement** - Loops through multiple research cycles to find counter-evidence
- **Reproducible results** - Same query produces consistent, traceable analysis

**Example**: Ask "Is coffee healthy?"
- ChatGPT: "Coffee has health benefits like antioxidants..."
- This System: "Conflict detected: Harvard study (0.95 credibility) shows benefits vs Blog (0.45 credibility) shows risks. Verdict: Benefits supported by higher-quality sources."

## Key Features

**Adversarial Analysis**: Actively challenges its own findings to find opposing evidence

**Conflict Detection**: Identifies and presents contradictory claims with credibility scores

**Transparent Scoring**: Evaluates sources based on domain authority (.edu, .gov), citations, and recency

**Interactive Visualization**: 2D and 3D knowledge graphs with filtering and search

**Free to Run**: Uses Groq (14,400 requests/day) and Tavily (1,000 searches/month) free tiers

## Example Usage

**Input**: "Is coffee good for health?"

**Output**:
- Knowledge graph with 40 entities and 12 relationships
- Identified 3 conflicts between sources
- Credibility-weighted analysis showing:
  - Side A: "Coffee reduces heart disease risk" (Harvard study, 0.95 credibility)
  - Side B: "Coffee increases blood pressure" (Blog article, 0.45 credibility)
- Verdict: Long-term benefits supported by higher-credibility sources

## Technical Stack

**Backend Architecture**:
- Python 3.11+ with FastAPI for REST API
- LangGraph for multi-agent workflow orchestration (state machine)
- LangChain for LLM integration and prompt management
- Pydantic for data validation and type safety
- Hypothesis for property-based testing (32 comprehensive tests)

**AI & Search**:
- LLM: Groq API with Llama 3.1 70B (14,400 free requests/day)
- Search: Tavily API for web search (1,000 free searches/month)
- Content Extraction: Trafilatura for clean text extraction


**Quality Assurance**:
- 32 property-based tests ensuring correctness
- Over 90% code coverage
- CI/CD pipeline with GitHub Actions
- Structured logging and error handling

## Architecture

The system uses a multi-agent architecture where five specialized AI agents work together in an orchestrated workflow:

1. **Scout Agent**: Searches the web and collects 10-20 sources per iteration from diverse domains
2. **Mapper Agent**: Extracts entities, relationships, and conflicts using LLM-powered analysis
3. **Adversary Agent**: Acts as a "red team" - identifies weaknesses and generates counter-queries to find opposing evidence
4. **Judge Agent**: Evaluates source credibility using a transparent 3-component algorithm (domain authority, citations, recency)
5. **Synthesis Agent**: Generates the final report with consensus points, battleground analysis, and verdicts

The system iterates up to 3 times, refining analysis based on adversarial challenges. This iterative approach ensures balanced coverage of multiple perspectives.

## Performance

- **Analysis time**: 2-3 minutes per research topic
- **Free tier capacity**: ~200 research sessions per month (zero cost)
- **Typical output**: 40-80 entities, 60-150 relationships, 3-10 conflicts
- **Source diversity**: 30-50 sources from 25-40 unique domains

## Use Cases

**Academic Research**: Synthesize multiple perspectives on controversial topics, identify consensus vs. debate areas, evaluate source quality automatically

**Fact-Checking**: Quickly gather evidence for and against claims, compare source credibility, identify potential misinformation

**Business Intelligence**: Analyze competing viewpoints on technologies, markets, or strategies with transparent source evaluation

**Journalism**: Research complex stories with multiple perspectives, identify credible sources, map argument landscapes

**Personal Decision-Making**: Make informed choices on health, finance, or lifestyle topics by understanding all sides of the debate

## Project Highlights

- **Production-Ready**: Comprehensive error handling, logging, testing, and monitoring
- **Transparent Algorithms**: No black-box ML - all credibility scoring is explainable
- **Cost-Effective**: Runs entirely on free-tier APIs (Groq + Tavily)

