# Free API Setup Guide

This guide shows you how to get **completely free API keys** to run the Adversarial Knowledge Cartographer.

## 🎁 Best Free Option (Recommended)

### Option 1: Groq + Tavily (Most Generous)

**Total Cost: $0/month**
- 14,400 LLM requests/day (Groq)
- 1,000 searches/month (Tavily)

#### Step 1: Get Groq API Key (Free - Most Generous!)

1. Go to https://console.groq.com/
2. Click "Sign Up" (use Google/GitHub for quick signup)
3. Once logged in, click "API Keys" in the left sidebar
4. Click "Create API Key"
5. Copy your API key (starts with `gsk_...`)

**Why Groq?**
- ✅ Completely free
- ✅ 14,400 requests per day (very generous!)
- ✅ Fast inference (faster than OpenAI)
- ✅ Good quality models (Llama 3.1, Mixtral)
- ✅ No credit card required

#### Step 2: Get Tavily API Key (Free)

1. Go to https://tavily.com/
2. Click "Get API Key" or "Sign Up"
3. Sign up with email or Google
4. Verify your email
5. Go to dashboard and copy your API key

**Why Tavily?**
- ✅ 1,000 searches/month free
- ✅ Research-focused search results
- ✅ Clean, structured data
- ✅ No credit card required

#### Step 3: Update Your .env File

```bash
# LLM Configuration - Using Groq (FREE!)
LLM_PROVIDER=groq
GROQ_API_KEY=gsk_your_groq_key_here

# LLM Model Configuration
LLM_MODEL=llama-3.1-70b-versatile
LLM_TEMPERATURE=0.1

# Search API Configuration - Using Tavily
SEARCH_PROVIDER=tavily
TAVILY_API_KEY=tvly-your_tavily_key_here

# Workflow Configuration
MAX_ITERATIONS=3
MIN_SOURCES=10
MAX_SOURCES_PER_QUERY=10

# Credibility Scoring Configuration
DOMAIN_WEIGHT=0.4
CITATION_WEIGHT=0.3
RECENCY_WEIGHT=0.3

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Logging Configuration
LOG_LEVEL=INFO
```

---

## 💳 Alternative Free Options

### Option 2: OpenAI + Tavily (New Account Credits)

**Cost: Free for first ~250 requests**
- $5 free credit for new OpenAI accounts
- 1,000 searches/month (Tavily)

#### Get OpenAI API Key

1. Go to https://platform.openai.com/signup
2. Sign up with email
3. Verify your email and phone number
4. Go to https://platform.openai.com/api-keys
5. Click "Create new secret key"
6. Copy your API key (starts with `sk-...`)

**Note:** New accounts get $5 free credit (expires after 3 months)

#### .env Configuration

```bash
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your_openai_key_here
LLM_MODEL=gpt-3.5-turbo  # Cheaper than gpt-4
SEARCH_PROVIDER=tavily
TAVILY_API_KEY=tvly-your_tavily_key_here
```

---

### Option 3: Anthropic + Serper (Alternative)

**Cost: Free for first ~500 requests**
- $5 free credit for new Anthropic accounts
- 2,500 searches/month (Serper)

#### Get Anthropic API Key

1. Go to https://console.anthropic.com/
2. Sign up with email
3. Verify your email
4. Go to API Keys section
5. Create new API key
6. Copy your key

#### Get Serper API Key

1. Go to https://serper.dev/
2. Sign up with Google
3. Go to dashboard
4. Copy your API key

#### .env Configuration

```bash
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-your_anthropic_key_here
LLM_MODEL=claude-3-haiku-20240307  # Cheapest Claude model
SEARCH_PROVIDER=serper
SERPER_API_KEY=your_serper_key_here
```

---

## 📊 Free Tier Comparison

| Provider | Free Tier | Best For | Signup |
|----------|-----------|----------|--------|
| **Groq** | 14,400 req/day | Testing & Development | ⭐ Easiest |
| **OpenAI** | $5 credit (~250 req) | Production Quality | Medium |
| **Anthropic** | $5 credit (~500 req) | Long Context | Medium |
| **Tavily** | 1,000 searches/month | Research Searches | Easy |
| **Serper** | 2,500 searches/month | Google Results | Easy |

---

## 🚀 Quick Start After Getting Keys

1. **Copy your keys into .env file**
   ```bash
   # Edit the .env file in the project root
   # Replace the placeholder values with your actual keys
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Test your configuration**
   ```bash
   python verify_setup.py
   ```

4. **Start the API server**
   ```bash
   python -m uvicorn api.app:app --reload --port 8000
   ```

5. **Test with a simple query**
   ```bash
   curl -X POST http://localhost:8000/api/research \
     -H "Content-Type: application/json" \
     -d '{"topic": "Is coffee good for health?"}'
   ```

---

## 💡 Tips for Staying Within Free Limits

### For Groq (14,400 requests/day)
- ✅ More than enough for development
- ✅ Can run ~100 full research workflows per day
- ✅ Resets daily

### For Tavily (1,000 searches/month)
- ✅ ~33 searches per day
- ✅ Each workflow uses ~4-8 searches
- ✅ Can run ~125-250 workflows per month
- 💡 Reduce `MAX_SOURCES_PER_QUERY` to 5 to conserve searches

### For OpenAI ($5 credit)
- 💡 Use `gpt-3.5-turbo` instead of `gpt-4` (10x cheaper)
- 💡 Reduce `MAX_ITERATIONS` to 1 or 2
- 💡 Reduce `MIN_SOURCES` to 5
- ✅ $5 = ~250 full workflows with gpt-3.5-turbo

---

## 🔧 Optimizing for Free Tier

Add these to your `.env` to reduce API usage:

```bash
# Reduce iterations (1-2 instead of 3)
MAX_ITERATIONS=1

# Reduce sources (5 instead of 10)
MIN_SOURCES=5
MAX_SOURCES_PER_QUERY=5
```

This will:
- ✅ Use 50% fewer API calls
- ✅ Run 2x faster
- ✅ Still produce good results
- ✅ Let you test more topics

---

## ❓ Troubleshooting

### "Invalid API key"
- Check you copied the entire key (no spaces)
- Make sure key starts with correct prefix:
  - Groq: `gsk_...`
  - OpenAI: `sk-...`
  - Anthropic: `sk-ant-...`
  - Tavily: `tvly-...`

### "Rate limit exceeded"
- Wait a few minutes and try again
- For Groq: You've hit daily limit (14,400 requests)
- For Tavily: You've hit monthly limit (1,000 searches)

### "Configuration error"
- Make sure `.env` file is in project root
- Check all required keys are set
- Run `python verify_setup.py` to diagnose

---

## 🎉 Ready to Go!

Once you have your keys configured, you can:

1. **Run the backend**: `python -m uvicorn api.app:app --reload --port 8000`
2. **Run the frontend**: `cd frontend && npm start`
3. **Start researching**: Open http://localhost:3000

**Recommended first query**: "Is coffee good or bad for health?"
- Great for testing conflict detection
- Shows the full workflow
- Produces interesting results

---

## 📚 Additional Resources

- **Groq Documentation**: https://console.groq.com/docs
- **Tavily Documentation**: https://docs.tavily.com/
- **OpenAI Documentation**: https://platform.openai.com/docs
- **Project README**: See `README.md` for full documentation

---

**Need help?** Check the troubleshooting section in `README.md` or `QUICKSTART.md`
