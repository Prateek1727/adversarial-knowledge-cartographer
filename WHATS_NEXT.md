# 🎉 You're All Set! What's Next?

Your Adversarial Knowledge Cartographer is configured and ready to run!

## ✅ What You've Done

- ✅ Added API keys (Groq + Tavily)
- ✅ Installed dependencies
- ✅ Configuration validated
- ✅ Groq support added

## 🚀 Start the Server (Choose One Method)

### Method 1: Using the Startup Script (Easiest)
```bash
start_server.bat
```

### Method 2: Manual Command
```bash
python -m uvicorn api.app:app --reload --host 0.0.0.0 --port 8000
```

### Method 3: Using Python Directly
```bash
python api/app.py
```

## 🌐 Access Your Application

Once the server starts, you'll see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

**Open these URLs:**
- **API Server**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs (Swagger UI)
- **Alternative Docs**: http://localhost:8000/redoc

## 🧪 Test Your Setup

### Quick Test via Browser

1. Open: http://localhost:8000/docs
2. Click on `POST /api/research`
3. Click "Try it out"
4. Enter a topic like: `"Is coffee good for health?"`
5. Click "Execute"
6. Watch the research workflow run!

### Test via Command Line

```bash
curl -X POST http://localhost:8000/api/research \
  -H "Content-Type: application/json" \
  -d "{\"topic\": \"Is coffee good for health?\"}"
```

You'll get a response like:
```json
{
  "session_id": "abc-123-def",
  "topic": "Is coffee good for health?",
  "status": "running",
  "message": "Research workflow started..."
}
```

### Check Status

```bash
curl http://localhost:8000/api/research/{session_id}/status
```

### Get Results

```bash
# Get knowledge graph
curl http://localhost:8000/api/research/{session_id}/graph

# Get synthesis report
curl http://localhost:8000/api/research/{session_id}/report
```

## 🎨 Start the Frontend (Optional)

The frontend provides an interactive visualization of the knowledge graph.

### Step 1: Install Frontend Dependencies
```bash
cd frontend
npm install
```

### Step 2: Start Frontend Server
```bash
npm start
```

### Step 3: Open Browser
The frontend will automatically open at: http://localhost:3000

**Features:**
- Interactive graph visualization
- Color-coded relationships (green=support, red=refute)
- Conflict highlighting
- Detail panels with citations
- Zoom and pan controls

## 📝 Example Research Topics

Try these topics to see the system in action:

### Controversial Topics (Great for Conflict Detection)
- "Is coffee good or bad for health?"
- "Nuclear energy safety and environmental impact"
- "Effectiveness of remote work vs office work"
- "Cryptocurrency as investment vs speculation"
- "Are video games harmful or beneficial?"

### Technical Topics (Great for Credibility Scoring)
- "Time complexity of quicksort algorithm"
- "Quantum computing practical applications"
- "Machine learning model interpretability"
- "Blockchain consensus mechanisms"

### Current Events (Great for Recency Scoring)
- "Latest developments in renewable energy"
- "Recent advances in cancer treatment"
- "Current state of artificial intelligence regulation"
- "Electric vehicle adoption trends"

## 🔍 Understanding the Output

### Knowledge Graph Structure

The system produces a structured knowledge graph with:

**Entities**: Key concepts, people, organizations
```json
{
  "id": "e1",
  "name": "Coffee consumption",
  "type": "concept",
  "description": "Regular intake of coffee beverages"
}
```

**Relationships**: Connections between entities
```json
{
  "source": "e1",
  "target": "e2",
  "type": "supports",
  "description": "Moderate coffee consumption reduces heart disease risk",
  "credibility_score": 0.85,
  "citations": ["https://..."]
}
```

**Conflicts**: Contradictory claims
```json
{
  "id": "c1",
  "entity_ids": ["e1", "e2"],
  "description": "Conflicting evidence on coffee's cardiovascular effects",
  "conflicting_claims": [
    "Coffee reduces heart disease risk (credibility: 0.85)",
    "Coffee increases blood pressure (credibility: 0.72)"
  ]
}
```

### Synthesis Report

The final report includes:
- Executive summary
- Key findings with credibility scores
- Conflict analysis
- Source evaluation
- Conclusions

## 💡 Tips for Best Results

### 1. Choose Good Topics
- ✅ Controversial topics with multiple viewpoints
- ✅ Topics with academic research available
- ✅ Current events with recent coverage
- ❌ Avoid very niche or obscure topics
- ❌ Avoid topics with limited online sources

### 2. Optimize for Free Tier
Your current config uses:
- **Groq**: 14,400 requests/day (very generous!)
- **Tavily**: 1,000 searches/month

To conserve searches, you can reduce in `.env`:
```bash
MAX_ITERATIONS=1  # Instead of 3
MIN_SOURCES=5     # Instead of 10
```

### 3. Monitor Your Usage
- Groq resets daily (14,400 requests)
- Tavily resets monthly (1,000 searches)
- Each workflow uses ~4-8 searches
- You can run ~125-250 workflows per month

## 🐛 Troubleshooting

### Server Won't Start

**Error**: "Address already in use"
```bash
# Kill process on port 8000
netstat -ano | findstr :8000
taskkill /PID <process_id> /F
```

**Error**: "Module not found"
```bash
# Reinstall dependencies
pip install -r requirements.txt
```

### API Key Errors

**Error**: "GROQ_API_KEY environment variable is required"
- Check `.env` file exists in project root
- Verify key is correct (starts with `gsk_`)
- Restart terminal/server after editing `.env`

**Error**: "Invalid API key"
- Verify you copied the entire key
- Check for extra spaces
- Generate a new key if needed

### Slow Responses

- First request is always slower (model loading)
- Subsequent requests are faster
- Groq is typically very fast (< 1 second)
- Full workflow takes ~2 minutes

### No Results

- Check server logs for errors
- Verify API keys are valid
- Try a simpler topic first
- Check internet connection

## 📊 Monitor Your Workflow

### Check Server Logs

The server logs show:
- Incoming requests
- Agent execution progress
- Source collection
- Entity extraction
- Conflict detection
- Errors and warnings

### Check Session Status

```bash
curl http://localhost:8000/api/research/{session_id}/status
```

Returns:
```json
{
  "session_id": "...",
  "status": "running",  // or "completed", "failed"
  "current_phase": "mapper",
  "iteration": 1,
  "sources_count": 10,
  "entities_count": 15,
  "relationships_count": 20,
  "conflicts_count": 3
}
```

## 🎓 Learn More

### Documentation
- **README.md** - Complete project documentation
- **QUICKSTART.md** - Quick start guide
- **ARCHITECTURE.md** - System architecture
- **API_COMPARISON.md** - API provider comparison
- **FREE_API_SETUP.md** - Detailed API setup guide

### Specification Files
- **requirements.md** - EARS-compliant requirements
- **design.md** - System design with correctness properties
- **tasks.md** - Implementation task list

### Code Structure
- **agents/** - Multi-agent system implementation
- **models/** - Data models
- **api/** - REST API
- **frontend/** - React visualization
- **tests/** - Property-based and unit tests

## 🚀 Next Steps

1. **Start the server** using `start_server.bat`
2. **Test with a simple query** via http://localhost:8000/docs
3. **Try different topics** to see conflict detection
4. **Start the frontend** for visual exploration
5. **Explore the code** to understand the system
6. **Run tests** with `pytest` to see property-based testing

## 🎉 You're Ready!

Your Adversarial Knowledge Cartographer is fully configured and ready to explore conflicting viewpoints!

**Quick Start Command:**
```bash
start_server.bat
```

Then open: http://localhost:8000/docs

---

**Questions?** Check the troubleshooting section or review the documentation files.

**Happy researching!** 🔍📊🤖
