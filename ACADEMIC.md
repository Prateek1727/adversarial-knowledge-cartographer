# Adversarial Knowledge Cartographer

Name: Prateek Anand 

Roll Number: 2301155

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
