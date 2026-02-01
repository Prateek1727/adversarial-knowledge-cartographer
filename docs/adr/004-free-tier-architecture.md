# ADR 004: Free-Tier Architecture Design

**Status:** Accepted  
**Date:** 2025-01-08  
**Deciders:** Core Team  

## Context

We wanted to build a production-grade AI research system that:
- Costs $0/month to run for demos and portfolio
- Handles real research workloads
- Demonstrates enterprise architecture patterns
- Remains accessible to students and indie developers

## Decision

We architected the system to use **100% free-tier services**:

1. **LLM**: Groq (14,400 requests/day, 6K tokens/min)
2. **Search**: Tavily (1,000 searches/month free)
3. **Deployment**: Docker Compose (self-hosted)
4. **Storage**: Local filesystem with checkpoints
5. **Caching**: Redis (optional, for rate limiting)

## Rationale

### Why Groq?

**Pros:**
- Fastest inference (300+ tokens/sec)
- Free tier: 14,400 requests/day
- Supports Llama 3.1 70B (high quality)
- LangChain integration

**Cons:**
- Rate limits: 30 requests/min, 6K tokens/min
- Requires careful iteration management

**Mitigation:**
- Set `MAX_ITERATIONS=1-2` for large topics
- Implement exponential backoff
- Cache LLM responses locally

### Why Tavily?

**Pros:**
- 1,000 searches/month free
- High-quality results (better than Google Custom Search)
- Returns clean, structured data
- No credit card required

**Cons:**
- 1,000 searches = ~30-50 research sessions
- No real-time data

**Mitigation:**
- Set `MAX_SOURCES_PER_QUERY=10` (not 15)
- Implement search result caching
- Use `MIN_SOURCES=20` (not 50)

### Cost Comparison

| Service | Free Tier | Paid Tier | Our Usage |
|---------|-----------|-----------|-----------|
| Groq | 14,400 req/day | N/A | ~100 req/session |
| Tavily | 1,000 searches/mo | $0.001/search | ~20 searches/session |
| OpenAI GPT-4 | $0 | $0.03/1K tokens | Would cost $5-10/session |
| Anthropic Claude | $0 | $0.015/1K tokens | Would cost $3-5/session |

**Savings**: ~$150-300/month for 30 research sessions

## Alternatives Considered

### 1. OpenAI GPT-4 + Serper

**Pros:**
- Higher quality outputs
- More reliable
- Better for complex reasoning

**Cons:**
- $5-10 per research session
- $150-300/month for portfolio demo
- Barrier for students

**Verdict**: Too expensive for free portfolio project

### 2. Local LLMs (Ollama) + DuckDuckGo

**Pros:**
- Truly free
- No rate limits
- Full privacy

**Cons:**
- Requires GPU (RTX 3090+)
- Slower inference (10-20 tokens/sec)
- Lower quality outputs
- DuckDuckGo search is limited

**Verdict**: Not practical for most users

### 3. Anthropic Claude + Brave Search

**Pros:**
- Claude is excellent for research
- Brave Search has free tier

**Cons:**
- Claude costs $0.015/1K tokens
- Still $3-5 per session

**Verdict**: Better than OpenAI, but not free

## Consequences

### Positive
- $0/month operational cost
- Accessible to students and indie devs
- Demonstrates cost-conscious architecture
- Forces efficient prompt engineering
- Shows understanding of rate limits

### Negative
- Rate limit management complexity
- Quality trade-offs vs GPT-4
- Monthly search limit (1,000)
- Requires careful configuration

## Rate Limit Management

### Groq Limits
- 30 requests/minute
- 6,000 tokens/minute
- 14,400 requests/day

### Our Strategy
```python
# Exponential backoff
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
def call_llm(prompt):
    return groq_client.chat(prompt)

# Token counting
def estimate_tokens(text):
    return len(text) // 4  # Rough estimate

# Request throttling
rate_limiter = RateLimiter(max_calls=25, period=60)
```

### Configuration for Free Tier
```bash
# .env for free tier
MAX_ITERATIONS=2          # Not 5
MIN_SOURCES=20            # Not 50
MAX_SOURCES_PER_QUERY=10  # Not 15
LLM_TEMPERATURE=0.1       # Deterministic
```

## Scaling Path

When ready to scale:

1. **Phase 1: Increase Limits** ($10-20/month)
   - Groq: No paid tier yet
   - Tavily: $10/month for 10K searches
   - Redis Cloud: Free tier sufficient

2. **Phase 2: Upgrade LLM** ($50-100/month)
   - Switch to OpenAI GPT-4
   - Keep Tavily
   - Add PostgreSQL for sessions

3. **Phase 3: Enterprise** ($500+/month)
   - OpenAI GPT-4 Turbo
   - Dedicated search API
   - AWS/GCP deployment
   - Monitoring (DataDog, Sentry)

## Monitoring Free Tier Usage

```python
# Track API usage
class UsageTracker:
    def __init__(self):
        self.groq_requests = 0
        self.tavily_searches = 0
    
    def log_groq_request(self):
        self.groq_requests += 1
        if self.groq_requests > 14000:
            logger.warning("Approaching Groq daily limit")
    
    def log_tavily_search(self):
        self.tavily_searches += 1
        if self.tavily_searches > 950:
            logger.warning("Approaching Tavily monthly limit")
```

## References

- [Groq Pricing](https://groq.com/pricing/)
- [Tavily API Pricing](https://tavily.com/pricing)
- [LangChain Rate Limiting](https://python.langchain.com/docs/guides/rate_limiting)
