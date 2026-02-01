# Adversarial Knowledge Cartographer - Complete Beginner's Guide

## What is the Adversarial Knowledge Cartographer?

The Adversarial Knowledge Cartographer is an AI-powered research system that automatically investigates complex topics by gathering information from multiple sources, analyzing conflicting viewpoints, and creating comprehensive research reports. Think of it as having a team of AI researchers working together to give you a balanced, well-researched analysis of any topic.

## How Does It Work? (The Big Picture)

Imagine you want to research "Is coffee good for health?" Instead of manually searching through dozens of websites and trying to make sense of conflicting information, the system does this automatically:

1. **🔍 Searches** for relevant sources across the internet
2. **📊 Analyzes** the information and builds a knowledge map
3. **⚔️ Challenges** its own findings to find weaknesses
4. **⚖️ Evaluates** how trustworthy each source is
5. **📝 Synthesizes** everything into a comprehensive report

## The Five AI Agents (Your Research Team)

The system uses five specialized AI agents that work together like a research team:

### 1. 🔍 Scout Agent - The Information Gatherer
**What it does:** Searches the internet for relevant sources about your topic.

**How it works:**
- Takes your research topic (e.g., "is coffee good for health")
- Uses search APIs (like Tavily or Serper) to find relevant articles
- Collects content from websites, academic papers, news articles, etc.
- Aims to gather at least 10 diverse sources

**Example:** For coffee research, it might find:
- Harvard Health articles
- Mayo Clinic studies
- Medical journals
- News articles about coffee research

### 2. 📊 Mapper Agent - The Knowledge Builder
**What it does:** Reads all the sources and builds a structured knowledge map.

**How it works:**
- Extracts key entities (things) like "Coffee", "Heart Disease", "Antioxidants"
- Identifies relationships between entities like "Coffee reduces risk of Type 2 Diabetes"
- Spots conflicts where sources disagree
- Creates a knowledge graph showing how everything connects

**Example output:**
- **Entities:** Coffee, Caffeine, Heart Disease, Cancer, Anxiety
- **Relationships:** "Coffee → reduces risk of → Type 2 Diabetes"
- **Conflicts:** Some sources say coffee increases heart disease risk, others say it decreases it

### 3. ⚔️ Adversary Agent - The Devil's Advocate
**What it does:** Challenges the findings to find weak spots and biases.

**How it works:**
- Looks for gaps in the research
- Identifies claims that need more evidence
- Generates new search queries to find counter-arguments
- Acts like a skeptical researcher asking "But what about...?"

**Example:** If most sources say coffee is healthy, it might search for:
- "coffee health risks"
- "negative effects of caffeine"
- "coffee addiction problems"

### 4. ⚖️ Judge Agent - The Credibility Evaluator
**What it does:** Evaluates how trustworthy each source is and assigns credibility scores.

**How it works:** (This is the detailed part you asked about!)

### 5. 📝 Synthesis Agent - The Report Writer
**What it does:** Combines everything into a final research report.

**How it works:**
- Analyzes all the evidence and conflicts
- Weighs different viewpoints based on credibility
- Writes a comprehensive report with conclusions
- Provides actionable insights and recommendations

## How Credibility Scoring Works (Detailed Explanation)

The Judge Agent is like a fact-checker that evaluates how much we should trust each source. It looks at three main factors:

### Factor 1: Domain Authority (40% of the score)
**What it is:** How trustworthy is the website domain?

**Scoring system:**
- **1.0 (Perfect):** Government (.gov) and educational (.edu) sites
  - Example: nih.gov, harvard.edu
- **0.95 (Excellent):** Prestigious journals and organizations
  - Example: nature.com, who.int, ieee.org
- **0.8 (Good):** Non-profit organizations (.org)
  - Example: heart.org, cancer.org
- **0.75 (Decent):** Reputable news sources
  - Example: bbc.com, reuters.com, nytimes.com
- **0.7 (Moderate):** Wikipedia and similar
- **0.6 (Average):** Commercial sites (.com)
- **0.5 (Low):** Unknown or questionable domains

**Why this matters:** A study from Harvard Medical School (.edu) is generally more trustworthy than a blog post from an unknown .com site.

### Factor 2: Citation Indicators (30% of the score)
**What it is:** Does the source show signs of academic rigor?

**The system looks for:**
- **References section** (+0.3 points): Does it cite other studies?
- **Academic formatting** (+0.2 points): Numbered citations like [1], [2] or (2023)
- **Author credentials** (+0.3 points): Written by Dr., PhD, Professor, Researcher?

**Examples:**
- ✅ **High score:** "According to Smith et al. (2023) [1], coffee consumption was associated with..."
- ❌ **Low score:** "Everyone knows coffee is bad for you."

### Factor 3: Recency (30% of the score)
**What it is:** How recent is the information?

**Scoring system:**
- **1.0:** Less than 1 year old
- **0.8:** 1-2 years old
- **0.5:** 2-5 years old
- **0.3:** More than 5 years old

**Why this matters:** Medical research evolves quickly. A 2024 study might have better methodology than a 2010 study.

### Final Credibility Score Calculation

The system combines all three factors using this formula:

```
Final Score = (Domain Authority × 0.4) + (Citations × 0.3) + (Recency × 0.3)
```

**Example calculation:**
- Harvard Health article (harvard.edu): Domain = 1.0
- Has references and author credentials: Citations = 0.8
- Published 6 months ago: Recency = 1.0
- **Final Score:** (1.0 × 0.4) + (0.8 × 0.3) + (1.0 × 0.3) = **0.94**

**Another example:**
- Random blog post (.com): Domain = 0.6
- No citations or credentials: Citations = 0.0
- Published 3 years ago: Recency = 0.5
- **Final Score:** (0.6 × 0.4) + (0.0 × 0.3) + (0.5 × 0.3) = **0.39**

## The Complete Research Process (Step by Step)

Let's follow a complete research cycle for "Is coffee good for health?":

### Step 1: Initial Search (Scout)
- Searches for "coffee health benefits research"
- Finds 10+ sources from various websites
- Collects full text content from each source

### Step 2: Knowledge Mapping (Mapper)
- Reads all sources and extracts key information
- **Entities found:** Coffee, Caffeine, Heart Disease, Cancer, Diabetes, Anxiety
- **Relationships found:** 
  - "Coffee reduces risk of Type 2 Diabetes" (from Harvard study)
  - "Caffeine increases anxiety" (from Mayo Clinic)
- **Conflicts identified:** 
  - Harvard says coffee reduces heart disease risk
  - Another source says coffee increases heart disease risk

### Step 3: Adversarial Challenge (Adversary)
- Notices most sources are positive about coffee
- Generates counter-queries: "coffee health risks", "caffeine addiction"
- Triggers another Scout round to find opposing viewpoints

### Step 4: Credibility Evaluation (Judge)
- Evaluates each source:
  - Harvard Health: 0.85 credibility
  - Mayo Clinic: 0.82 credibility
  - Random blog: 0.35 credibility
- Assigns these scores to all relationships and conflicts

### Step 5: Final Synthesis (Synthesis)
- Analyzes all evidence weighted by credibility
- Resolves conflicts by favoring higher-credibility sources
- Generates final report with conclusions and recommendations

## Understanding the API Response

When you make a request to the system, here's what you get back:

### 1. Session Status
```json
{
  "session_id": "abc-123",
  "status": "completed",
  "sources_count": 10,
  "entities_count": 85,
  "relationships_count": 108,
  "conflicts_count": 8
}
```

### 2. Knowledge Graph
The graph shows:
- **Nodes:** Entities (Coffee, Heart Disease) and Conflicts
- **Edges:** Relationships between entities with credibility scores

### 3. Final Report
A comprehensive analysis including:
- **Consensus points:** Where most sources agree
- **Battleground topics:** Where sources disagree
- **Credibility-weighted conclusions:** Final judgments based on source quality
- **Actionable insights:** Practical recommendations

## Why This Approach Works

### Traditional Research Problems:
- ❌ Information overload
- ❌ Cherry-picking sources that confirm your bias
- ❌ Difficulty weighing conflicting information
- ❌ Time-consuming manual analysis

### Adversarial Knowledge Cartographer Solutions:
- ✅ Automatically processes many sources
- ✅ Actively seeks opposing viewpoints
- ✅ Objectively evaluates source credibility
- ✅ Provides balanced, evidence-based conclusions

## Real-World Example: Coffee Research Results

From the actual API response you shared, here's what the system found:

**Topic:** "Is coffee good for health?"

**Sources Analyzed:** 10 sources with credibility scores ranging from 0.5 to 0.88

**Key Findings:**
- **85 entities** identified (Coffee, Caffeine, various health conditions)
- **108 relationships** mapped (how coffee affects different health aspects)
- **8 major conflicts** found where sources disagreed

**Major Conflicts Identified:**
1. **Heart Disease:** Some sources say coffee helps, others say it hurts
2. **Cancer:** Mixed evidence on cancer risk/protection
3. **Anxiety:** Disagreement on whether coffee increases or decreases anxiety
4. **Sleep:** Conflicting views on sleep impact

**Credibility-Weighted Conclusions:**
- Moderate coffee consumption (3-5 cups/day) appears beneficial overall
- Individual factors matter (some people should avoid coffee)
- Antioxidants and polyphenols may be more important than caffeine
- More research needed on gut health impacts

## Getting Started

1. **Access the API:** Go to http://localhost:8000/docs
2. **Start Research:** POST to `/api/research` with your topic
3. **Monitor Progress:** GET `/api/research/{session_id}/status`
4. **View Results:** GET `/api/research/{session_id}/graph` and `/api/research/{session_id}/report`

## Tips for Best Results

1. **Use specific topics:** "Effects of coffee on cardiovascular health" vs. "coffee"
2. **Controversial topics work well:** The system excels at analyzing debates
3. **Be patient:** Complex research takes 5-15 minutes
4. **Review the conflicts:** The most interesting insights are often in the disagreements

## Technical Architecture

The system is built with:
- **Backend:** Python FastAPI with specialized AI agents
- **Frontend:** React with 3D visualization
- **AI Models:** GPT-4, Claude, or Llama for text analysis
- **Search APIs:** Tavily or Serper for web search
- **Visualization:** Interactive knowledge graphs

This creates a powerful research tool that combines the thoroughness of academic research with the speed and objectivity of AI analysis.