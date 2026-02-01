# Adversarial Knowledge Cartographer - Complete API Reference Guide

## Overview

The Adversarial Knowledge Cartographer uses multiple types of APIs to function. This guide explains all the APIs used, their purposes, and how they work together.

## 🔍 External APIs (Third-Party Services)

### 1. Search APIs - For Finding Information

#### **Tavily API** (Primary Search Provider)
- **Purpose:** Advanced web search with AI-optimized results
- **URL:** `https://api.tavily.com/search`
- **What it does:**
  - Searches the internet for relevant sources
  - Returns clean, structured search results
  - Provides raw content extraction
  - Optimized for AI research tasks

**Request Example:**
```json
{
  "api_key": "your_tavily_key",
  "query": "coffee health benefits research",
  "search_depth": "advanced",
  "max_results": 10,
  "include_raw_content": true
}
```

**Response Example:**
```json
{
  "results": [
    {
      "url": "https://harvard.edu/coffee-study",
      "title": "Coffee Health Benefits Study",
      "content": "Research shows coffee may reduce...",
      "raw_content": "Full article text..."
    }
  ]
}
```

#### **Serper API** (Fallback Search Provider)
- **Purpose:** Google search results via API
- **URL:** `https://google.serper.dev/search`
- **What it does:**
  - Provides Google search results
  - Used as backup when Tavily fails
  - Returns organic search results

**Request Example:**
```json
{
  "q": "coffee health benefits research",
  "num": 10
}
```

**Response Example:**
```json
{
  "organic": [
    {
      "link": "https://harvard.edu/coffee-study",
      "title": "Coffee Health Benefits Study",
      "snippet": "Research shows coffee may reduce..."
    }
  ]
}
```

### 2. AI/LLM APIs - For Text Analysis

#### **OpenAI API** (Primary AI Provider)
- **Purpose:** Advanced language understanding and generation
- **Models Used:** GPT-4, GPT-3.5-turbo
- **What it does:**
  - Analyzes source content
  - Extracts entities and relationships
  - Identifies conflicts between sources
  - Generates synthesis reports

**Functions:**
- Entity extraction from text
- Relationship mapping
- Conflict detection
- Report generation

#### **Anthropic API** (Alternative AI Provider)
- **Purpose:** Claude AI models for text analysis
- **Models Used:** Claude-3, Claude-2
- **What it does:**
  - Same functions as OpenAI
  - Used as alternative/backup
  - Different reasoning approach

#### **Groq API** (Fast AI Provider)
- **Purpose:** Ultra-fast inference with Llama models
- **Models Used:** Llama-3.1-8b-instant, Llama-3.1-70b
- **What it does:**
  - Same AI functions but faster
  - Good for real-time applications
  - Rate limited (14,400 requests/day)

**Rate Limits:**
- **Daily requests:** 14,400 per day
- **Tokens per minute:** 6,000
- **Recommendation:** Use MAX_ITERATIONS=1-2 for large topics

## 🏠 Internal APIs (System's Own REST API)

The system provides its own REST API for users to interact with:

### Base URL: `http://localhost:8000`

### 1. **Health Check**
- **Endpoint:** `GET /health`
- **Purpose:** Check if the system is running
- **Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-12-16T08:00:00Z",
  "llm_provider": "groq",
  "llm_model": "llama-3.1-8b-instant",
  "rate_limits": {
    "daily_requests": "14,400 per day",
    "tokens_per_minute": "6,000 per minute"
  }
}
```

### 2. **Start Research**
- **Endpoint:** `POST /api/research`
- **Purpose:** Begin a new research workflow
- **Request:**
```json
{
  "topic": "is coffee good for health"
}
```
- **Response:**
```json
{
  "session_id": "abc-123-def",
  "topic": "is coffee good for health",
  "status": "running",
  "message": "Research workflow started"
}
```

### 3. **Check Research Status**
- **Endpoint:** `GET /api/research/{session_id}/status`
- **Purpose:** Monitor research progress
- **Response:**
```json
{
  "session_id": "abc-123-def",
  "topic": "is coffee good for health",
  "status": "completed",
  "current_phase": "synthesis",
  "iteration": 3,
  "sources_count": 10,
  "entities_count": 85,
  "relationships_count": 108,
  "conflicts_count": 8,
  "synthesis_available": true
}
```

### 4. **Get Knowledge Graph**
- **Endpoint:** `GET /api/research/{session_id}/graph`
- **Purpose:** Retrieve the knowledge graph for visualization
- **Response:**
```json
{
  "session_id": "abc-123-def",
  "nodes": [
    {
      "id": "Coffee",
      "label": "Coffee",
      "type": "entity",
      "data": {}
    },
    {
      "id": "conflict_0",
      "label": "Coffee and heart disease relationship",
      "type": "conflict",
      "data": {
        "side_a": "Coffee reduces heart disease risk",
        "side_a_credibility": 0.85,
        "side_b": "Coffee increases heart disease risk",
        "side_b_credibility": 0.62
      }
    }
  ],
  "edges": [
    {
      "id": "rel_0",
      "source": "Coffee",
      "target": "Heart Disease",
      "label": "reduces_risk_of",
      "type": "neutral",
      "data": {
        "citation": "https://harvard.edu/study",
        "credibility": 0.85
      }
    }
  ]
}
```

### 5. **Get Research Report**
- **Endpoint:** `GET /api/research/{session_id}/report`
- **Purpose:** Get the final synthesis report
- **Response:**
```json
{
  "session_id": "abc-123-def",
  "topic": "is coffee good for health",
  "report": "# Research Report\n\n## Consensus Points\n..."
}
```

### 6. **Get Graph Statistics**
- **Endpoint:** `GET /api/research/{session_id}/graph/stats`
- **Purpose:** Get statistical information about the knowledge graph
- **Response:**
```json
{
  "session_id": "abc-123-def",
  "total_entities": 85,
  "total_conflicts": 8,
  "total_nodes": 93,
  "total_relationships": 108,
  "relationship_types": {
    "support": 14,
    "neutral": 94
  },
  "average_credibility": 0.686,
  "graph_density": 0.013
}
```

### 7. **Get Entities List**
- **Endpoint:** `GET /api/research/{session_id}/graph/entities`
- **Purpose:** Get all entities with connection counts
- **Response:**
```json
{
  "session_id": "abc-123-def",
  "entities": [
    {
      "name": "Coffee",
      "connections": 59,
      "type": "entity"
    },
    {
      "name": "Caffeine",
      "connections": 9,
      "type": "entity"
    }
  ],
  "total_count": 85
}
```

### 8. **Get Conflicts List**
- **Endpoint:** `GET /api/research/{session_id}/graph/conflicts`
- **Purpose:** Get detailed list of all conflicts
- **Response:**
```json
{
  "session_id": "abc-123-def",
  "conflicts": [
    {
      "id": "conflict_0",
      "point_of_contention": "Coffee and heart disease relationship",
      "side_a": "Coffee reduces heart disease risk",
      "side_a_citation": "https://harvard.edu/study",
      "side_a_credibility": 0.85,
      "side_b": "Coffee increases heart disease risk",
      "side_b_citation": "https://mayo.edu/research",
      "side_b_credibility": 0.62
    }
  ],
  "total_count": 8
}
```

## 🔧 Supporting APIs and Libraries

### Content Extraction
- **Trafilatura Library**
  - **Purpose:** Extract clean text from web pages
  - **Function:** Removes ads, navigation, and extracts main content
  - **Usage:** `trafilatura.extract(html_content)`

### HTTP Client
- **HTTPX Library**
  - **Purpose:** Make HTTP requests to external APIs
  - **Features:** Async support, timeout handling, retry logic
  - **Usage:** All API calls use this for reliability

## 📊 API Usage Flow

Here's how all the APIs work together in a typical research session:

### 1. **User Initiates Research**
```
User → POST /api/research → System
```

### 2. **Scout Agent Searches**
```
System → Tavily API → Web Search Results
System → Trafilatura → Clean Content Extraction
```

### 3. **Mapper Agent Analyzes**
```
System → OpenAI/Claude/Groq API → Entity Extraction
System → OpenAI/Claude/Groq API → Relationship Mapping
System → OpenAI/Claude/Groq API → Conflict Detection
```

### 4. **Adversary Agent Challenges**
```
System → OpenAI/Claude/Groq API → Weakness Analysis
System → Tavily API → Counter-argument Search
```

### 5. **Judge Agent Evaluates**
```
System → Internal Credibility Algorithm → Source Scoring
```

### 6. **Synthesis Agent Reports**
```
System → OpenAI/Claude/Groq API → Final Report Generation
```

### 7. **User Gets Results**
```
User → GET /api/research/{id}/report → Final Report
User → GET /api/research/{id}/graph → Knowledge Graph
```

## 🔑 API Keys Required

To run the system, you need API keys for:

### Required (Choose One):
- **OpenAI API Key** - For GPT models
- **Anthropic API Key** - For Claude models  
- **Groq API Key** - For Llama models (free tier available)

### Required (Choose One):
- **Tavily API Key** - For advanced search
- **Serper API Key** - For Google search

### Configuration:
Set these in your `.env` file:
```env
# LLM Provider (choose one)
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
GROQ_API_KEY=your_groq_key

# Search Provider (choose one)
TAVILY_API_KEY=your_tavily_key
SERPER_API_KEY=your_serper_key

# Configuration
LLM_PROVIDER=groq
SEARCH_PROVIDER=tavily
```

## 🚨 Rate Limits and Error Handling

### Search APIs:
- **Tavily:** 1000 requests/month (free tier)
- **Serper:** 2500 requests/month (free tier)

### AI APIs:
- **OpenAI:** Pay per token
- **Anthropic:** Pay per token
- **Groq:** 14,400 requests/day (free tier)

### Error Handling:
- **Automatic Fallback:** If Tavily fails, switches to Serper
- **Retry Logic:** Exponential backoff for rate limits
- **Graceful Degradation:** System continues with partial data if some APIs fail

## 🎯 Best Practices

1. **Use Groq for Development:** Free tier with good performance
2. **Monitor Rate Limits:** Check `/health` endpoint for current limits
3. **Handle Async Operations:** Research takes 5-15 minutes
4. **Cache Results:** Save session IDs to avoid re-running research
5. **Error Recovery:** System automatically handles most API failures

This comprehensive API ecosystem enables the Adversarial Knowledge Cartographer to perform sophisticated research analysis by combining web search, AI analysis, and structured data presentation.