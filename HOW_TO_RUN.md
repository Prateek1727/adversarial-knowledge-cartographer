# How to Run the Adversarial Knowledge Cartographer

This guide provides step-by-step instructions to run the project on your Windows system.

## ✅ Prerequisites Check

Before starting, verify you have:
- ✅ Python 3.11+ installed
- ✅ API keys configured in `.env` file (already done!)
- ✅ Dependencies installed

## 🚀 Quick Start (3 Steps)

### Step 1: Activate Virtual Environment

**Option A: Using the Batch File (EASIEST)**
```cmd
RUN_SERVER.bat
```
This will automatically activate the environment and start the server!

**Option B: Manual Activation**

If using **Command Prompt (cmd)**:
```cmd
venv\Scripts\activate.bat
```

If using **PowerShell**:
```powershell
.\venv\Scripts\Activate.ps1
```

If you get an error in PowerShell about execution policy, run this first:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

You should see `(venv)` appear at the start of your command prompt.

### Step 2: Start the Backend Server

```cmd
python -m uvicorn api.app:app --reload --host 0.0.0.0 --port 8000
```

**Alternative method:**
```cmd
cd api
python app.py
```

**Expected Output:**
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 3: Access the API

Open your browser and go to:
- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 🎯 Using the System

### Method 1: Via Web Interface (Swagger UI)

1. Go to http://localhost:8000/docs
2. Click on `POST /api/research`
3. Click "Try it out"
4. Enter a research topic:
   ```json
   {
     "topic": "Is coffee good for health?"
   }
   ```
5. Click "Execute"
6. Copy the `session_id` from the response
7. Wait 2-3 minutes for processing
8. Use `GET /api/research/{session_id}/status` to check progress
9. Use `GET /api/research/{session_id}/report` to get results

### Method 2: Via Python Script

Create a file `run_research.py`:

```python
import requests
import time
import json

# Start research
response = requests.post(
    "http://localhost:8000/api/research",
    json={"topic": "Is coffee good for health?"}
)
session_id = response.json()["session_id"]
print(f"Session ID: {session_id}")
print("Research started... waiting for completion...")

# Poll for completion
while True:
    status = requests.get(f"http://localhost:8000/api/research/{session_id}/status")
    status_data = status.json()
    
    if status_data["status"] == "completed":
        print("✅ Research completed!")
        break
    elif status_data["status"] == "failed":
        print("❌ Research failed!")
        print(status_data.get("error"))
        break
    
    print(f"Status: {status_data['status']} - Phase: {status_data.get('current_phase', 'unknown')}")
    time.sleep(10)

# Get results
report = requests.get(f"http://localhost:8000/api/research/{session_id}/report")
print("\n" + "="*80)
print("SYNTHESIS REPORT")
print("="*80)
print(report.json()["report"])

# Get knowledge graph
graph = requests.get(f"http://localhost:8000/api/research/{session_id}/graph")
graph_data = graph.json()
print(f"\n📊 Knowledge Graph:")
print(f"   Nodes: {len(graph_data['nodes'])}")
print(f"   Edges: {len(graph_data['edges'])}")
```

Run it:
```cmd
python run_research.py
```

### Method 3: Via Command Line (curl)

**Start research:**
```cmd
curl -X POST http://localhost:8000/api/research ^
  -H "Content-Type: application/json" ^
  -d "{\"topic\": \"Is coffee good for health?\"}"
```

**Check status:**
```cmd
curl http://localhost:8000/api/research/{session_id}/status
```

**Get report:**
```cmd
curl http://localhost:8000/api/research/{session_id}/report
```

**Get graph:**
```cmd
curl http://localhost:8000/api/research/{session_id}/graph
```

## 🎨 Optional: Run the Frontend Visualization

### Option A: Using the Batch File (EASIEST)

**From the project root directory:**
```cmd
RUN_FRONTEND.bat
```

Or double-click the `RUN_FRONTEND.bat` file!

This will automatically:
1. ✅ Navigate to the frontend directory
2. ✅ Install dependencies (if needed)
3. ✅ Start the React development server
4. ✅ Open your browser to http://localhost:3000

### Option B: Manual Commands

In a **new terminal window**:

```cmd
cd frontend
npm install
npm start
```

The frontend will open at http://localhost:3000

### ⚠️ Important Note

Make sure the **backend server is running first** on port 8000, otherwise the frontend won't have any data to display!

You should have **TWO terminal windows** open:
1. **Terminal 1**: Backend server (running `RUN_SERVER.bat`)
2. **Terminal 2**: Frontend server (running `RUN_FRONTEND.bat` or `npm start`)

### Frontend Features

- Interactive 3D knowledge graph visualization
- Real-time filtering and search
- Analytics dashboard with graph metrics
- Node details with citations and credibility scores
- 2D and 3D visualization modes
- Export capabilities

## 📝 Example Research Topics

### Controversial Topics (Best Results)
```
"Is coffee good or bad for health?"
"Nuclear energy safety and environmental impact"
"Effectiveness of remote work vs office work"
"Cryptocurrency as investment vs speculation"
"Are electric vehicles better for the environment?"
"Is intermittent fasting effective for weight loss?"
```

### Technical Topics
```
"Time complexity of quicksort algorithm"
"Quantum computing practical applications"
"Machine learning model interpretability"
```

### Policy Topics
```
"Should minimum wage be increased?"
"Is universal basic income effective?"
"Do gun control laws reduce crime?"
```

## 🔍 Understanding the Output

### Synthesis Report Structure

The report includes:

1. **Executive Summary**: High-level overview of findings
2. **Consensus Points**: What 90%+ of sources agree on
3. **Battleground Topics**: Areas of significant disagreement
4. **Conflict Analysis**: Why sources disagree (methodology, data, timeframe)
5. **Credibility-Weighted Verdicts**: Which claims are more likely correct
6. **Knowledge Graph JSON**: Complete structured data

### Knowledge Graph Structure

```json
{
  "nodes": [
    {
      "id": "Coffee",
      "label": "Coffee",
      "type": "entity",
      "credibility": 0.85
    }
  ],
  "edges": [
    {
      "source": "Coffee",
      "target": "Heart Health",
      "label": "affects",
      "type": "relationship",
      "citation": "https://example.com/study"
    }
  ]
}
```

## ⚙️ Configuration Options

Edit `.env` file to customize:

### Change LLM Model
```bash
# Faster but less accurate
LLM_MODEL=llama-3.1-8b-instant

# More accurate but slower
LLM_MODEL=llama-3.3-70b-versatile
```

### Adjust Iteration Count
```bash
# Fewer iterations = faster results
MAX_ITERATIONS=1

# More iterations = more thorough analysis
MAX_ITERATIONS=3
```

### Change Source Count
```bash
# Fewer sources = faster but less comprehensive
MIN_SOURCES=5

# More sources = slower but more thorough
MIN_SOURCES=15
```

## 🐛 Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'models'"

**Solution:**
```cmd
# Make sure you're in the project root directory
cd D:\AI Agents

# Activate virtual environment
venv\Scripts\activate

# Run with Python module syntax
python -m uvicorn api.app:app --reload --host 0.0.0.0 --port 8000
```

### Issue: "Port 8000 is already in use"

**Solution:**
```cmd
# Find and kill the process using port 8000
netstat -ano | findstr :8000
taskkill /PID <process_id> /F

# Or use a different port
python -m uvicorn api.app:app --reload --host 0.0.0.0 --port 8001
```

### Issue: "API key not found"

**Solution:**
```cmd
# Check .env file exists
dir .env

# Verify API keys are set
type .env

# Restart the server after editing .env
```

### Issue: "Rate limit exceeded"

**Solution:**
- Wait a few minutes and try again
- Reduce `MAX_SOURCES_PER_QUERY` in `.env`
- Switch to a different LLM model
- Use a simpler research topic

### Issue: Server starts but API returns errors

**Solution:**
```cmd
# Check server logs in the terminal
# Look for specific error messages

# Verify dependencies are installed
pip install -r requirements.txt

# Test configuration
python -c "from config import config; print(config.llm_provider)"
```

### Issue: Frontend can't connect to backend

**Solution:**
1. Verify backend is running on port 8000
2. Check `frontend/.env` or `frontend/src/services/api.ts` has correct API URL
3. Restart both frontend and backend

## 📊 Performance Expectations

### Typical Workflow Timing

- **Scout Phase**: 20-30 seconds (searching 10 sources)
- **Mapper Phase**: 15-25 seconds (extracting entities and relationships)
- **Adversary Phase**: 10-15 seconds (generating counter-queries)
- **Judge Phase**: 5-10 seconds (evaluating credibility)
- **Synthesis Phase**: 15-25 seconds (generating report)

**Total Time**: 2-3 minutes per research session

### API Rate Limits (Free Tier)

- **Groq**: 14,400 requests/day
- **Tavily**: 1,000 searches/month
- **Capacity**: ~200 full research workflows/month

Each workflow uses:
- 4-8 Tavily searches
- 5-10 Groq LLM calls

## 🔄 Stopping the Server

Press `Ctrl+C` in the terminal where the server is running.

Or if running in background:
```cmd
# Find the process
netstat -ano | findstr :8000

# Kill it
taskkill /PID <process_id> /F
```

## 📚 Additional Resources

- **API Documentation**: http://localhost:8000/docs (when server is running)
- **Project README**: `README.md`
- **Quick Start Guide**: `QUICKSTART.md`
- **API Reference**: `API_REFERENCE_GUIDE.md`
- **Optimal Questions**: `OPTIMAL_RESEARCH_QUESTIONS.md`
- **Real-World Applications**: `REAL_WORLD_APPLICATIONS_AND_ROADMAP.md`

## 🎯 Next Steps

1. ✅ Start the server (Step 1-2 above)
2. ✅ Try a research topic via Swagger UI
3. ✅ Review the synthesis report
4. ✅ Explore the knowledge graph
5. ✅ Try different controversial topics
6. ✅ Experiment with configuration options
7. ✅ (Optional) Run the frontend visualization

## 💡 Pro Tips

1. **Start Simple**: Begin with well-known controversial topics like "coffee health effects"
2. **Monitor Logs**: Keep the server terminal visible to see what's happening
3. **Be Patient**: First run may take 2-3 minutes as the system gathers and analyzes sources
4. **Check Status**: Use the status endpoint to track progress
5. **Save Session IDs**: You can retrieve results later using the session ID
6. **Experiment**: Try different topics to see how the system handles various types of debates

## 🚀 Ready to Start!

Run these commands now:

```cmd
# 1. Activate environment
venv\Scripts\activate

# 2. Start server
python -m uvicorn api.app:app --reload --host 0.0.0.0 --port 8000

# 3. Open browser to http://localhost:8000/docs

# 4. Start researching!
```

Happy researching! 🔍📊🎯