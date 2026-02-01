# Adversarial Knowledge Cartographer
## Project Proposal

**Student Name**: [Your Name]  
**Course**: [Course Name/Number]  
**Instructor**: [Professor Name]  
**Date**: January 2026  
**Project Type**: Independent Research & Development

---

## 1. Project Overview

I propose to build an AI-powered research system that solves a critical problem: **existing AI tools like ChatGPT provide biased, single-perspective answers to controversial questions without acknowledging contradictions or evaluating source credibility.**

This system will use multiple AI agents working together to actively seek opposing viewpoints, evaluate source trustworthiness, and present balanced analysis with visual knowledge graphs.

---

## 2. The Problem I'm Solving

### Current Situation

When someone asks "Is coffee healthy?" to different tools:

**ChatGPT/Gemini**:
- Gives one answer: "Coffee has health benefits like antioxidants..."
- Doesn't mention contradicting studies
- Doesn't show which sources it's using
- No way to verify credibility

**Google Search**:
- Returns 100+ links
- User must manually read each one
- No guidance on which sources to trust
- Takes 30+ minutes to synthesize information

### The Core Problem

People researching controversial topics face three challenges:

1. **Hidden Bias**: AI assistants present one perspective as truth
2. **No Credibility Check**: Can't tell if information comes from Harvard or a random blog
3. **Missing Counter-Evidence**: Tools don't actively look for opposing viewpoints

### Why This Matters

Making decisions based on incomplete or biased information has real consequences:
- Health decisions (should I drink coffee?)
- Policy opinions (is climate change real?)
- Academic research (what does the literature actually say?)
- Business decisions (is this investment safe?)

---

## 3. My Proposed Solution

### What I'll Build

An intelligent system with **5 AI agents** that work together:

1. **Scout Agent**: Searches the web and collects sources
2. **Mapper Agent**: Extracts key information and identifies conflicts
3. **Adversary Agent**: Challenges findings and searches for counter-evidence
4. **Judge Agent**: Scores source credibility (.edu = trustworthy, random blog = less trustworthy)
5. **Synthesis Agent**: Creates final report showing both sides

### How It Works

```
User asks: "Is coffee healthy?"
    ↓
Scout finds 15 sources (Harvard, Mayo Clinic, health blogs)
    ↓
Mapper extracts: "Coffee reduces heart disease" vs "Coffee raises blood pressure"
    ↓
Judge scores: Harvard study = 0.95, Health blog = 0.45
    ↓
Adversary says: "All sources are pro-coffee, search for risks"
    ↓
Scout finds 10 more sources with opposing views
    ↓
Synthesis creates report: "High-credibility sources support benefits, 
but individual responses vary. Conflict exists on blood pressure."
```

### Key Innovation: Adversarial Approach

Unlike ChatGPT that gives one answer, my system **argues with itself**:
- Finds evidence for coffee benefits
- Then actively searches for coffee risks
- Presents both sides with credibility scores
- Shows where experts agree vs disagree

---

## 4. Technical Approach

### Architecture

**Multi-Agent System** using LangGraph (state machine for AI workflows):
- Each agent has a specific job
- Agents pass information to each other
- System loops up to 3 times to find counter-evidence

**Technology Stack**:
- Python for backend logic
- Groq API for AI (free tier: 14,400 requests/day)
- Tavily API for web search (free tier: 1,000 searches/month)

### Key Algorithms I'll Implement

**1. Credibility Scoring**
```
Score = (Domain × 0.5) + (Citations × 0.3) + (Recency × 0.2)

Domain scores:
- .edu, .gov = 1.0 (highest trust)
- .org = 0.8
- .com = 0.5
- blogs = 0.3
```

**2. Conflict Detection**
- Extract claims from each source
- Compare claims to find contradictions
- Group contradictions by topic
- Calculate which side has higher-credibility sources

**3. Adversarial Query Generation**
- Analyze current findings for bias
- If all sources agree → search for opposing views
- If only blogs found → search for academic sources
- Generate counter-queries automatically

---

## 5. Implementation Plan

### Phase 1: Core Agents (Weeks 1-3)
- Build Scout agent (web search)
- Build Mapper agent (extract information)
- Build Judge agent (score credibility)
- Test each agent individually

### Phase 2: Adversarial Logic (Weeks 4-5)
- Build Adversary agent
- Implement iterative workflow
- Add conflict detection algorithm

### Phase 3: Synthesis & Visualization (Weeks 6-7)
- Build Synthesis agent
- Create knowledge graph structure
- Build web interface

### Phase 4: Testing & Refinement (Week 8)
- Write comprehensive tests
- Test with real controversial topics
- Fix bugs and improve accuracy

---

## 6. Expected Outcomes

### Deliverables

1. **Working System**:
   - Web application with user interface
   - 5 AI agents working together
   - Knowledge graph visualization

2. **Documentation**:
   - Technical documentation
   - User guide
   - Code with comments

3. **Evaluation**:
   - Test on 10 controversial topics
   - Compare results with ChatGPT
   - Measure accuracy and balance

### Success Metrics

- **Conflict Detection**: Find contradictions in 80%+ of controversial topics
- **Credibility Accuracy**: 85%+ agreement with human evaluators on source trustworthiness
- **Balance**: Present both sides of debates (not just one perspective)
- **Speed**: Complete analysis in under 3 minutes

### Example Output

For "Is coffee healthy?":
```
Entities Found: 38 (Harvard, Mayo Clinic, caffeine, heart disease, etc.)
Relationships: 15 (caffeine → affects → heart rate)
Conflicts Detected: 3

Conflict 1: Heart Health Effects
  Side A: "Reduces heart disease risk by 15%"
    - Harvard study (credibility: 0.95)
    - Mayo Clinic (credibility: 0.90)
  Side B: "Increases cardiovascular risk"
    - Health blog (credibility: 0.45)
  Verdict: Side A supported by higher-credibility sources

Consensus Topics:
  - Coffee contains antioxidants (95% of sources agree)
  - Moderate consumption = 3-4 cups/day (90% agree)

Battleground Topics:
  - Blood pressure impact (conflicting evidence)
```

---

## 7. Technical Challenges & Solutions

### Challenge 1: API Rate Limits
**Problem**: Free APIs limit requests (30/minute for Groq)  
**Solution**: Implement retry logic with exponential backoff, save progress after each step

### Challenge 2: AI Hallucinations
**Problem**: AI might invent conflicts that don't exist  
**Solution**: Validate every claim appears in actual source text, require 2+ sources per side

### Challenge 3: Entity Deduplication
**Problem**: "USA" vs "United States" vs "U.S." are the same entity  
**Solution**: Use fuzzy string matching (85% similarity = same entity)

### Challenge 4: Workflow Failures
**Problem**: If system crashes mid-analysis, lose all progress  
**Solution**: Save state after each agent (checkpointing), can resume from last step

---

## 8. Why This Project is Valuable

### Academic Contribution

1. **Novel Approach**: First system to use adversarial agents for balanced research
2. **Transparent AI**: Shows exactly why sources are trusted (not a black box)
3. **Reproducible**: Same question always produces same analysis

### Practical Applications

- **Students**: Research controversial topics for papers
- **Journalists**: Fact-check claims and find opposing viewpoints
- **Researchers**: Synthesize literature on debated topics
- **General Public**: Make informed decisions on health, policy, etc.

### Learning Outcomes

Through this project, I will learn:
- Multi-agent AI system design
- LLM orchestration with LangGraph
- Natural language processing
- Knowledge graph construction
- Web scraping and API integration
- Software testing and quality assurance

---

## 9. Comparison with Existing Tools

| Feature | ChatGPT | Google | My System |
|---------|---------|--------|-----------|
| Finds contradictions | No | No | **Yes** |
| Shows source credibility | No | No | **Yes** |
| Actively seeks counter-evidence | No | No | **Yes** |
| Visual knowledge graph | No | No | **Yes** |
| Shows both sides of debates | No | Manual | **Automatic** |
| Time required | 30 sec | 30 min | **3 min** |

---


## 11. Resources Needed

### APIs (All Free Tier)
- Groq API (free: 14,400 requests/day)
- Tavily API (free: 1,000 searches/month)

### Software (All Free/Open Source)
- Python 3.11+
- LangChain & LangGraph
- React & TypeScript
- D3.js for visualization

### Hardware
- Standard laptop (no GPU needed, using cloud APIs)

---

## 12. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| API rate limits hit | High | Medium | Implement caching, retry logic |
| AI produces inaccurate results | Medium | High | Validate with source text, human review |
| Workflow too slow | Medium | Medium | Optimize API calls, parallel processing |
| Conflict detection misses contradictions | Medium | High | Test on diverse topics, refine algorithm |

---

## 13. Evaluation Plan

### Testing Strategy

1. **Unit Tests**: Test each agent individually
2. **Integration Tests**: Test agents working together
3. **Property-Based Tests**: Ensure credibility scores always 0.0-1.0, etc.
4. **Real-World Tests**: Run on 10 controversial topics

### Evaluation Metrics

1. **Accuracy**: Do detected conflicts actually exist in sources?
2. **Balance**: Are both sides of debates represented?
3. **Credibility**: Do scores match human judgment?
4. **Completeness**: Are major viewpoints captured?

### Comparison Baseline

Test same questions on:
- ChatGPT (single perspective?)
- Google Search (manual synthesis time?)
- My system (balanced? credible? fast?)

---
