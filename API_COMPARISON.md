# Free API Comparison

## 🏆 Recommended: Groq + Tavily

| Feature | Groq | OpenAI | Anthropic |
|---------|------|--------|-----------|
| **Free Tier** | 14,400 req/day | $5 credit (~250 req) | $5 credit (~500 req) |
| **Cost** | FREE forever | Pay after credit | Pay after credit |
| **Speed** | ⚡ Very Fast | Medium | Medium |
| **Quality** | ⭐⭐⭐⭐ Good | ⭐⭐⭐⭐⭐ Excellent | ⭐⭐⭐⭐⭐ Excellent |
| **Signup** | Easy (Google/GitHub) | Medium (phone required) | Medium (email verify) |
| **Best For** | Development & Testing | Production | Long context |
| **Models** | Llama 3.1, Mixtral | GPT-3.5, GPT-4 | Claude 3 |

## 🔍 Search API Comparison

| Feature | Tavily | Serper | SerpAPI |
|---------|--------|--------|---------|
| **Free Tier** | 1,000/month | 2,500/month | 100/month |
| **Quality** | ⭐⭐⭐⭐⭐ Research-focused | ⭐⭐⭐⭐ Google results | ⭐⭐⭐⭐ Google results |
| **Signup** | Easy | Easy (Google) | Medium |
| **Best For** | Research queries | General search | Limited testing |
| **Data Format** | Clean, structured | Raw Google | Raw Google |

## 💰 Cost Estimates (After Free Tier)

### Per Research Workflow (10 sources, 3 iterations)

| Provider | Cost per Workflow | 100 Workflows |
|----------|------------------|---------------|
| **Groq** | $0.00 | $0.00 |
| **OpenAI (GPT-3.5)** | ~$0.02 | ~$2.00 |
| **OpenAI (GPT-4)** | ~$0.20 | ~$20.00 |
| **Anthropic (Haiku)** | ~$0.01 | ~$1.00 |
| **Anthropic (Sonnet)** | ~$0.05 | ~$5.00 |

### Search Costs

| Provider | Cost per Search | 1,000 Searches |
|----------|----------------|----------------|
| **Tavily** | $0.00 (free tier) | $0.00 |
| **Serper** | $0.00 (free tier) | $0.00 |
| **After free tier** | ~$0.002 | ~$2.00 |

## 🎯 Recommendations by Use Case

### 1. Just Testing / Learning
**Use: Groq + Tavily**
- ✅ Completely free
- ✅ 14,400 requests/day
- ✅ No credit card needed
- ✅ Perfect for experimentation

### 2. Building a Demo
**Use: Groq + Tavily**
- ✅ Free and fast
- ✅ Good enough quality
- ✅ Can run hundreds of queries
- ✅ Upgrade later if needed

### 3. Production / Best Quality
**Use: OpenAI (GPT-4) + Tavily**
- ⭐ Best quality results
- 💰 ~$0.20 per workflow
- ✅ Most reliable
- ✅ Best for important research

### 4. Long Research Papers
**Use: Anthropic (Claude) + Tavily**
- ⭐ 200K token context window
- 💰 ~$0.05 per workflow
- ✅ Handles long documents
- ✅ Good for academic research

## 📊 Free Tier Limits

### How Many Workflows Can You Run?

| Provider Combo | Workflows/Day | Workflows/Month |
|----------------|---------------|-----------------|
| **Groq + Tavily** | ~1,800 | ~33 (search limited) |
| **OpenAI + Tavily** | ~25 (credit limited) | ~33 (search limited) |
| **Anthropic + Serper** | ~50 (credit limited) | ~83 (search limited) |

**Note:** Tavily's 1,000 searches/month is usually the limiting factor (each workflow uses ~4-8 searches)

## 🔧 Optimization Tips

### To Stay Within Free Limits

1. **Reduce iterations**
   ```bash
   MAX_ITERATIONS=1  # Instead of 3
   ```
   Saves: 66% of API calls

2. **Reduce sources**
   ```bash
   MIN_SOURCES=5  # Instead of 10
   MAX_SOURCES_PER_QUERY=5
   ```
   Saves: 50% of search calls

3. **Use Groq for development**
   - Switch to OpenAI/Anthropic only for production
   - Test everything with Groq first (free!)

4. **Cache results**
   - Save research results locally
   - Reuse for testing/development

## ⚡ Quick Decision Guide

**Choose Groq if:**
- ✅ You want completely free
- ✅ You're testing/learning
- ✅ You need high volume
- ✅ Speed matters

**Choose OpenAI if:**
- ✅ You need best quality
- ✅ You're building production app
- ✅ Budget allows ~$0.02-0.20 per query
- ✅ You want most reliable

**Choose Anthropic if:**
- ✅ You need long context (200K tokens)
- ✅ You're processing long documents
- ✅ Budget allows ~$0.01-0.05 per query
- ✅ You want good quality + value

## 🎁 Best Free Setup (Recommended)

```bash
# .env configuration
LLM_PROVIDER=groq
GROQ_API_KEY=gsk_your_key_here
LLM_MODEL=llama-3.1-70b-versatile

SEARCH_PROVIDER=tavily
TAVILY_API_KEY=tvly_your_key_here

# Optimize for free tier
MAX_ITERATIONS=2
MIN_SOURCES=5
MAX_SOURCES_PER_QUERY=5
```

**This gives you:**
- ✅ ~1,800 workflows per day (Groq limit)
- ✅ ~200 workflows per month (Tavily limit)
- ✅ $0 cost
- ✅ Good quality results
- ✅ Fast execution

---

**Ready to get started?** See `GET_FREE_KEYS.md` for signup instructions!
