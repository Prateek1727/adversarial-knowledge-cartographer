# Deployment Guide - Adversarial Knowledge Cartographer

This guide will help you deploy your project to the cloud and showcase it as a professional portfolio piece.

## 🎯 Deployment Options Overview

| Platform | Backend | Frontend | Cost | Difficulty | Best For |
|----------|---------|----------|------|------------|----------|
| **Render** | ✅ | ✅ | Free tier | Easy | Quick demo |
| **Railway** | ✅ | ✅ | $5/month | Easy | Production-ready |
| **Vercel + Railway** | Railway | Vercel | Free + $5 | Medium | Best performance |
| **AWS** | EC2/ECS | S3+CloudFront | ~$20/month | Hard | Enterprise |
| **Heroku** | ✅ | ✅ | $7/month | Easy | Traditional |

**Recommended for Portfolio**: Render (Free) or Railway ($5/month)

---

## 🚀 Option 1: Deploy to Render (FREE - Recommended for Portfolio)

Render offers free hosting for both backend and frontend with automatic deployments from GitHub.

### Step 1: Prepare Your Repository

1. **Create a GitHub repository** (if you haven't already)
2. **Add a `.gitignore` file**:

```gitignore
# Python
venv/
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
*.so
*.egg
*.egg-info/
dist/
build/

# Environment variables
.env
.env.local

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log

# Testing
.pytest_cache/
.hypothesis/
.coverage
htmlcov/

# Frontend
frontend/node_modules/
frontend/build/
frontend/.env.local

# Checkpoints
.checkpoints/
```

3. **Create `requirements.txt`** (if not exists):

```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
python-dotenv==1.0.0
httpx==0.25.1
beautifulsoup4==4.12.2
trafilatura==1.6.2
langchain==0.0.340
langchain-groq==0.0.1
langgraph==0.0.20
pytest==7.4.3
pytest-asyncio==0.21.1
hypothesis==6.92.1
```

4. **Push to GitHub**:

```bash
git init
git add .
git commit -m "Initial commit - Adversarial Knowledge Cartographer"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/adversarial-knowledge-cartographer.git
git push -u origin main
```

### Step 2: Deploy Backend to Render

1. **Go to** [render.com](https://render.com) and sign up
2. **Click "New +"** → **"Web Service"**
3. **Connect your GitHub repository**
4. **Configure the service**:

```yaml
Name: adversarial-knowledge-cartographer-api
Environment: Python 3
Region: Oregon (US West) or closest to you
Branch: main
Root Directory: (leave empty)
Build Command: pip install -r requirements.txt
Start Command: uvicorn api.app:app --host 0.0.0.0 --port $PORT
```

5. **Add Environment Variables**:

Click "Advanced" → "Add Environment Variable":

```
LLM_PROVIDER=groq
GROQ_API_KEY=your_groq_key_here
SEARCH_PROVIDER=tavily
TAVILY_API_KEY=your_tavily_key_here
LLM_MODEL=llama-3.1-8b-instant
LLM_TEMPERATURE=0.1
MAX_ITERATIONS=3
MIN_SOURCES=10
MAX_SOURCES_PER_QUERY=10
DOMAIN_WEIGHT=0.4
CITATION_WEIGHT=0.3
RECENCY_WEIGHT=0.3
LOG_LEVEL=INFO
```

6. **Select Plan**: Free (512 MB RAM, spins down after 15 min of inactivity)
7. **Click "Create Web Service"**
8. **Wait for deployment** (5-10 minutes)
9. **Copy your backend URL**: `https://adversarial-knowledge-cartographer-api.onrender.com`

### Step 3: Deploy Frontend to Render

1. **Update frontend API URL**:

Edit `frontend/src/services/api.ts`:

```typescript
const API_BASE_URL = process.env.REACT_APP_API_URL || 
  'https://adversarial-knowledge-cartographer-api.onrender.com';
```

2. **Commit and push changes**:

```bash
git add frontend/src/services/api.ts
git commit -m "Update API URL for production"
git push
```

3. **In Render, click "New +"** → **"Static Site"**
4. **Connect your GitHub repository**
5. **Configure the static site**:

```yaml
Name: adversarial-knowledge-cartographer
Branch: main
Root Directory: frontend
Build Command: npm install && npm run build
Publish Directory: build
```

6. **Add Environment Variable**:

```
REACT_APP_API_URL=https://adversarial-knowledge-cartographer-api.onrender.com
```

7. **Click "Create Static Site"**
8. **Wait for deployment** (3-5 minutes)
9. **Your app is live!** 🎉

**Your URLs**:
- Frontend: `https://adversarial-knowledge-cartographer.onrender.com`
- Backend API: `https://adversarial-knowledge-cartographer-api.onrender.com/docs`

---

## 🚂 Option 2: Deploy to Railway (Recommended for Production)

Railway offers better performance and doesn't spin down like Render's free tier.

### Step 1: Prepare for Railway

1. **Create `railway.json`** in project root:

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "uvicorn api.app:app --host 0.0.0.0 --port $PORT",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

2. **Create `Procfile`**:

```
web: uvicorn api.app:app --host 0.0.0.0 --port $PORT
```

3. **Commit changes**:

```bash
git add railway.json Procfile
git commit -m "Add Railway configuration"
git push
```

### Step 2: Deploy Backend to Railway

1. **Go to** [railway.app](https://railway.app) and sign up
2. **Click "New Project"** → **"Deploy from GitHub repo"**
3. **Select your repository**
4. **Add environment variables** (same as Render)
5. **Click "Deploy"**
6. **Generate domain**: Settings → Generate Domain
7. **Copy your backend URL**: `https://your-app.up.railway.app`

### Step 3: Deploy Frontend

**Option A: Railway (Recommended)**

1. **Click "New"** → **"GitHub Repo"** → Select same repo
2. **Configure**:
   - Root Directory: `frontend`
   - Build Command: `npm install && npm run build`
   - Start Command: `npx serve -s build -p $PORT`
3. **Add environment variable**:
   ```
   REACT_APP_API_URL=https://your-backend.up.railway.app
   ```
4. **Generate domain**

**Option B: Vercel (Better for React)**

1. **Go to** [vercel.com](https://vercel.com)
2. **Import your GitHub repository**
3. **Configure**:
   - Framework Preset: Create React App
   - Root Directory: `frontend`
   - Build Command: `npm run build`
   - Output Directory: `build`
4. **Add environment variable**:
   ```
   REACT_APP_API_URL=https://your-backend.up.railway.app
   ```
5. **Deploy**

---

## 🐳 Option 3: Docker Deployment (Any Platform)

### Step 1: Create Dockerfile for Backend

Create `Dockerfile` in project root:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "api.app:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Step 2: Create Dockerfile for Frontend

Create `frontend/Dockerfile`:

```dockerfile
FROM node:18-alpine as build

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm install

# Copy source and build
COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### Step 3: Create docker-compose.yml

```yaml
version: '3.8'

services:
  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - LLM_PROVIDER=groq
      - GROQ_API_KEY=${GROQ_API_KEY}
      - SEARCH_PROVIDER=tavily
      - TAVILY_API_KEY=${TAVILY_API_KEY}
      - LLM_MODEL=llama-3.1-8b-instant
    restart: unless-stopped

  frontend:
    build: ./frontend
    ports:
      - "80:80"
    environment:
      - REACT_APP_API_URL=http://localhost:8000
    depends_on:
      - backend
    restart: unless-stopped
```

### Step 4: Deploy to Any Cloud

**AWS ECS, Google Cloud Run, Azure Container Instances, DigitalOcean App Platform**

All support Docker deployments. Push your images to Docker Hub or use their container registries.

---

## 📱 Option 4: Quick Demo with Ngrok (For Interviews/Presentations)

Perfect for live demos without permanent deployment.

### Step 1: Install Ngrok

```bash
# Download from https://ngrok.com/download
# Or use chocolatey on Windows:
choco install ngrok
```

### Step 2: Start Your Local Servers

```bash
# Terminal 1: Backend
RUN_SERVER.bat

# Terminal 2: Frontend
RUN_FRONTEND.bat
```

### Step 3: Expose with Ngrok

```bash
# Terminal 3: Expose backend
ngrok http 8000

# Terminal 4: Expose frontend
ngrok http 3000
```

### Step 4: Share Your URLs

Ngrok will give you public URLs like:
- Backend: `https://abc123.ngrok.io`
- Frontend: `https://def456.ngrok.io`

Update frontend to use the ngrok backend URL and share the frontend URL!

---

## 🎨 Making Your Project Portfolio-Ready

### 1. Create an Impressive README

Update your `README.md` with:

```markdown
# 🔍 Adversarial Knowledge Cartographer

> An AI-powered research system that actively seeks disagreements, maps argument topologies, and produces credibility-weighted analysis of controversial topics.

[![Live Demo](https://img.shields.io/badge/demo-live-success)](https://your-app.onrender.com)
[![Python](https://img.shields.io/badge/python-3.11+-blue)](https://www.python.org/)
[![React](https://img.shields.io/badge/react-18+-61dafb)](https://reactjs.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

## 🎯 Live Demo

**Try it now**: [https://your-app.onrender.com](https://your-app.onrender.com)

**Example Topics**:
- "Is coffee good for health?"
- "Nuclear energy safety"
- "Remote work effectiveness"

## ✨ Key Features

- 🤖 **Multi-Agent Architecture**: 5 specialized AI agents working in concert
- 🔄 **Adversarial Validation**: Actively challenges findings through 3 iterative cycles
- 📊 **Credibility Scoring**: Domain authority, citations, and recency-based evaluation
- 🎨 **3D Visualization**: Interactive knowledge graph with advanced analytics
- ⚡ **Property-Based Testing**: 32 correctness properties ensuring reliability

## 🏗️ Architecture

[Include your architecture diagram]

## 🚀 Quick Start

[Your installation instructions]

## 📸 Screenshots

[Add screenshots of your 3D visualization, synthesis reports, etc.]

## 🎓 Technical Highlights

- **LangGraph** for agent orchestration
- **Property-based testing** with Hypothesis
- **Formal correctness properties** with EARS requirements
- **Advanced 3D visualization** with Three.js
- **Real-time conflict detection** and credibility analysis

## 📊 Performance

- Processes 10+ sources in ~2 minutes
- Handles complex controversial topics
- Generates credibility-weighted verdicts
- Exports structured JSON knowledge graphs

## 🤝 Contributing

[Your contribution guidelines]

## 📄 License

MIT License - see LICENSE file

## 👤 Author

**Your Name**
- Portfolio: [your-portfolio.com](https://your-portfolio.com)
- LinkedIn: [linkedin.com/in/yourname](https://linkedin.com/in/yourname)
- GitHub: [@yourname](https://github.com/yourname)
```

### 2. Add Screenshots and Demo Video

Create a `docs/` folder with:
- Screenshots of the 3D visualization
- GIF of the workflow in action
- Architecture diagram
- Sample research reports

### 3. Create a Landing Page

Add `frontend/src/pages/Landing.tsx`:

```typescript
export const Landing = () => {
  return (
    <div className="landing">
      <h1>Adversarial Knowledge Cartographer</h1>
      <p>AI-powered research that actively seeks disagreement</p>
      <button onClick={() => navigate('/research')}>
        Try Live Demo
      </button>
      
      <div className="features">
        <Feature icon="🤖" title="Multi-Agent System" />
        <Feature icon="🔄" title="Adversarial Validation" />
        <Feature icon="📊" title="Credibility Scoring" />
        <Feature icon="🎨" title="3D Visualization" />
      </div>
      
      <div className="demo-video">
        {/* Embed your demo video */}
      </div>
    </div>
  );
};
```

### 4. Add Analytics

Add Google Analytics or Plausible to track usage:

```html
<!-- In frontend/public/index.html -->
<script async src="https://www.googletagmanager.com/gtag/js?id=YOUR_ID"></script>
```

### 5. Create a Demo Video

Record a 2-3 minute video showing:
1. Entering a controversial topic
2. Watching the workflow progress
3. Exploring the 3D knowledge graph
4. Reading the synthesis report
5. Highlighting key features

Upload to YouTube and embed in your README.

---

## 📈 Monitoring & Maintenance

### Set Up Error Tracking

**Sentry** (Free tier):

```python
# In api/app.py
import sentry_sdk

sentry_sdk.init(
    dsn="your-sentry-dsn",
    traces_sample_rate=1.0,
)
```

### Set Up Uptime Monitoring

**UptimeRobot** (Free):
- Monitor your deployed URL
- Get alerts if it goes down
- Shows 99.9% uptime on your portfolio

### Set Up Logging

**Papertrail** or **Logtail** (Free tier):
- Centralized log management
- Search and filter logs
- Set up alerts for errors

---

## 💼 Portfolio Presentation Tips

### 1. Project Description

"Built an AI-powered research system using multi-agent architecture that actively seeks contradictions in controversial topics, evaluates source credibility, and generates interactive 3D knowledge graphs. Implemented 32 property-based tests ensuring correctness across all workflows."

### 2. Technical Skills Demonstrated

- **AI/ML**: LangChain, LangGraph, multi-agent systems
- **Backend**: Python, FastAPI, async programming
- **Frontend**: React, TypeScript, Three.js, D3.js
- **Testing**: Property-based testing, Hypothesis, pytest
- **Architecture**: State machines, agent orchestration, RESTful APIs
- **DevOps**: Docker, CI/CD, cloud deployment
- **Best Practices**: EARS requirements, formal correctness properties

### 3. Key Metrics to Highlight

- "Processes 10+ sources in under 2 minutes"
- "32 correctness properties with 100+ test iterations each"
- "Handles complex multi-agent workflows with 5 specialized agents"
- "Interactive 3D visualization with real-time filtering"
- "Credibility-weighted analysis using domain authority, citations, and recency"

### 4. Problem Solved

"Traditional research tools simply summarize information. This system actively seeks disagreement, maps argument structures, and provides credibility-weighted verdicts on contested claims - transforming controversial topics from confusing noise into navigable knowledge graphs."

---

## 🎯 Next Steps After Deployment

1. ✅ **Test thoroughly** with various topics
2. ✅ **Add sample research results** to showcase
3. ✅ **Create demo video** (2-3 minutes)
4. ✅ **Write blog post** about the architecture
5. ✅ **Share on LinkedIn** with demo link
6. ✅ **Submit to Show HN** on Hacker News
7. ✅ **Add to your resume** and portfolio
8. ✅ **Prepare for technical interviews** about the system

---

## 🚨 Important Notes

### Free Tier Limitations

**Render Free Tier**:
- Spins down after 15 minutes of inactivity
- First request after spin-down takes 30-60 seconds
- 512 MB RAM limit
- Good for: Portfolio demos, interviews

**Railway**:
- $5/month for always-on
- Better performance
- No spin-down delays
- Good for: Production showcase

### API Key Security

**Never commit API keys!**

Use environment variables and add to `.gitignore`:
```
.env
.env.local
.env.production
```

For deployment, add keys through the platform's dashboard.

### Cost Estimates

**Free Tier (Render)**:
- Backend: Free (with spin-down)
- Frontend: Free
- APIs: Free (Groq + Tavily)
- **Total: $0/month**

**Production (Railway + Vercel)**:
- Backend: $5/month (Railway)
- Frontend: Free (Vercel)
- APIs: Free (Groq + Tavily)
- **Total: $5/month**

---

## 📞 Support

If you encounter issues during deployment:

1. Check the deployment logs in your platform dashboard
2. Verify all environment variables are set correctly
3. Test API keys locally first
4. Review the platform-specific documentation
5. Open an issue on GitHub

---

**Ready to deploy?** Start with Render's free tier for a quick portfolio demo, then upgrade to Railway if you need always-on availability!

Good luck with your deployment! 🚀