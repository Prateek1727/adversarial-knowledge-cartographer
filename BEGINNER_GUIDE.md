# Adversarial Knowledge Cartographer - Complete Beginner's Guide

> A friendly, step-by-step explanation of what this project does and how it works

---

## Table of Contents

1. [What Problem Does This Solve?](#what-problem-does-this-solve)
2. [How Is This Different from Google or ChatGPT?](#how-is-this-different-from-google-or-chatgpt)
3. [Real-World Example](#real-world-example)
4. [How Does It Work? (Simple Explanation)](#how-does-it-work-simple-explanation)
5. [The Five AI Agents Explained](#the-five-ai-agents-explained)
6. [Understanding the Output](#understanding-the-output)
7. [Technical Terms Explained](#technical-terms-explained)
8. [How to Install and Run](#how-to-install-and-run)
9. [What Can You Use This For?](#what-can-you-use-this-for)
10. [Frequently Asked Questions](#frequently-asked-questions)

---

## What Problem Does This Solve?

Imagine you want to research a controversial topic like "Is coffee good for your health?" 

If you search online, you'll find:
- Some articles saying coffee is great for you
- Other articles saying coffee is harmful
- No clear way to know which sources to trust
- Conflicting information everywhere

**This project solves that problem** by:
1. Automatically gathering information from many sources
2. Finding where sources disagree with each other
3. Evaluating which sources are more trustworthy
4. Presenting both sides of the argument clearly
5. Helping you make an informed decision

---

## How Is This Different from Google or ChatGPT?

### Google Search
- **What it does**: Shows you a list of websites
- **Problem**: You have to read everything yourself and figure out what's true
- **Time**: Hours of manual work

### ChatGPT/Gemini
- **What it does**: Gives you one answer based on its training
- **Problem**: Doesn't show you conflicting viewpoints or source credibility
- **Bias**: May present one-sided information

### This System (Adversarial Knowledge Cartographer)
- **What it does**: 
  - Searches the web for current information
  - Finds contradictions automatically
  - Shows you both sides with credibility scores
  - Creates visual maps of how ideas connect
- **Advantage**: Balanced, transparent, and shows you the full picture
- **Time**: 2-3 minutes automated analysis

---

## Real-World Example

Let's walk through a complete example to see how this works.

### Your Question
"Is intermittent fasting effective for weight loss?"

### What Happens Behind the Scenes

**Step 1: Information Gathering (30 seconds)**
The system searches the web and finds 20 articles from:
- Harvard Medical School
- Mayo Clinic
- Health blogs
- Fitness websites
- Scientific journals

**Step 2: Analysis (15 seconds)**
The system reads all articles and identifies:
- Key concepts: "intermittent fasting", "weight loss", "insulin", "metabolism"
- Relationships: "intermittent fasting" → "affects" → "insulin levels"
- Conflicts: Some sources say it works, others say it doesn't

**Step 3: Finding Contradictions (10 seconds)**
The system actively looks for opposing views:
- "Does intermittent fasting preserve muscle mass?"
- "Are there any negative side effects?"
- "Does it work for everyone?"

**Step 4: Credibility Scoring (5 seconds)**
The system evaluates each source:
- Harvard Medical School article: 0.95 (very trustworthy)
- Random blog post: 0.45 (less trustworthy)
- Mayo Clinic study: 0.92 (very trustworthy)

**Step 5: Final Report (20 seconds)**
The system generates a comprehensive report showing:

```
CONSENSUS (What everyone agrees on):
- Intermittent fasting can lead to calorie reduction
- It affects insulin sensitivity
- Results vary by individual

CONFLICTS (Where sources disagree):

Conflict #1: Muscle Mass Preservation
- Side A: "Intermittent fasting preserves muscle mass"
  Sources: 3 studies (average credibility: 0.72)
  
- Side B: "Intermittent fasting may cause muscle loss"
  Sources: 2 studies (average credibility: 0.68)
  
Why they disagree: Different fasting protocols (16:8 vs 5:2)

VERDICT:
Intermittent fasting is effective for weight loss (credibility: 0.82)
but individual results vary based on adherence and protocol.
```

### Visual Output
You also get an interactive graph showing:
- Circles (nodes) representing concepts like "fasting", "weight loss", "insulin"
- Lines (edges) connecting related concepts
- Red highlights showing conflicts
- Color coding based on credibility scores

---

## How Does It Work? (Simple Explanation)

Think of this system as a team of five specialized researchers working together:

```
You ask a question
       ↓
[Scout] Searches the internet and collects articles
       ↓
[Mapper] Reads articles and creates a knowledge map
       ↓
[Adversary] Challenges the findings and looks for opposite views
       ↓
[Decision] Should we search more? (repeats up to 3 times)
       ↓
[Judge] Evaluates which sources are trustworthy
       ↓
[Synthesis] Writes the final report
       ↓
You get a comprehensive analysis
```

---

## The Five AI Agents Explained

### 1. Scout Agent (The Researcher)

**Job**: Find information on the internet

**What it does**:
- Takes your question (e.g., "Is coffee healthy?")
- Searches the web using Tavily (a search engine)
- Collects 10-20 articles from different websites
- Extracts the text content from each article

**Think of it as**: A librarian gathering books on your topic

**Example Output**:
```
Found 20 sources:
- harvard.edu/coffee-health-study
- mayoclinic.org/coffee-benefits
- healthblog.com/coffee-risks
... (17 more)
```

---

### 2. Mapper Agent (The Organizer)

**Job**: Read all the articles and organize the information

**What it does**:
- Reads through all 20 articles
- Identifies key concepts (entities): "coffee", "heart health", "caffeine"
- Finds relationships: "coffee" → "reduces risk of" → "heart disease"
- Spots conflicts: One source says X, another says opposite of X

**Think of it as**: A student making a mind map from textbooks

**Example Output**:
```
Entities found: Coffee, Heart Health, Caffeine, Blood Pressure
Relationships: 
- Coffee → contains → Caffeine
- Coffee → reduces → Heart Disease Risk
- Caffeine → increases → Blood Pressure

Conflicts detected:
- Conflict: Effect on heart health
  Side A: Reduces risk (8 sources)
  Side B: Increases risk (2 sources)
```

---

### 3. Adversary Agent (The Devil's Advocate)

**Job**: Challenge the findings and look for opposite viewpoints

**What it does**:
- Reviews what the Mapper found
- Asks: "What if this is wrong?"
- Generates new search queries to find counter-evidence
- Example: If most sources say coffee is good, search for "coffee health risks"

**Think of it as**: A debate opponent who challenges every claim

**Example Output**:
```
Weaknesses found:
- Only 2 sources discuss long-term effects
- No sources from the past year
- Missing perspective on caffeine sensitivity

New searches needed:
- "coffee long-term health effects 2024"
- "coffee risks for sensitive individuals"
- "coffee contradictory studies"
```

---

### 4. Judge Agent (The Fact-Checker)

**Job**: Evaluate which sources are trustworthy

**What it does**:
- Looks at each source's website domain
  - .edu (universities) = very trustworthy (0.9)
  - .gov (government) = very trustworthy (0.9)
  - .org (organizations) = trustworthy (0.7-0.8)
  - .com (commercial) = varies (0.4-0.7)
- Checks if the article has references and citations
- Considers how recent the information is
- Calculates a credibility score from 0.0 to 1.0

**Think of it as**: A teacher grading the reliability of sources

**Example Output**:
```
Source credibility scores:
- harvard.edu/study → 0.95 (excellent)
- mayoclinic.org/article → 0.92 (excellent)
- healthnews.com/blog → 0.65 (moderate)
- randomsite.com/post → 0.42 (low)
```

---

### 5. Synthesis Agent (The Report Writer)

**Job**: Write the final comprehensive report

**What it does**:
- Takes all the information from other agents
- Organizes it into clear sections:
  - What everyone agrees on (consensus)
  - Where sources disagree (conflicts)
  - Which side is more credible (verdict)
- Creates a readable report
- Includes the knowledge graph data

**Think of it as**: A journalist writing a balanced news article

**Example Output**:
```
RESEARCH REPORT: Is Coffee Healthy?

CONSENSUS:
Based on 20 sources, these facts are widely agreed upon:
- Coffee contains antioxidants
- Caffeine is a stimulant
- Effects vary by individual

CONFLICTS:
Point of Contention: Long-term heart health effects

Side A (Credibility: 0.87): Coffee reduces heart disease risk
- Supported by 8 studies
- Includes Harvard and Mayo Clinic research
- Based on large population studies

Side B (Credibility: 0.58): Coffee may increase heart problems
- Supported by 2 articles
- Focuses on short-term blood pressure spikes
- Smaller sample sizes

VERDICT:
Evidence strongly suggests coffee has long-term heart health benefits
for most people, though short-term blood pressure increases can occur.
Recommendation: Moderate consumption (1-3 cups/day) appears safe for
most individuals based on high-credibility sources.
```

---

## Understanding the Output

When the system finishes, you get two main things:

### 1. A Written Report

This is like a research paper that includes:

**Consensus Section**: What all sources agree on
```
Everyone agrees that:
- Coffee contains caffeine
- Caffeine affects the nervous system
- Individual responses vary
```

**Battleground Section**: Where sources disagree
```
Disagreement: Does coffee cause dehydration?
- 12 sources say NO (average credibility: 0.82)
- 3 sources say YES (average credibility: 0.54)
Winner: NO - supported by higher-quality sources
```

**Verdict Section**: The system's conclusion based on evidence
```
Based on credibility-weighted analysis:
Coffee does NOT cause dehydration in regular consumers.
The body adapts to regular caffeine intake.
```

### 2. A Knowledge Graph

This is a visual map showing:

**Nodes (Circles)**: Represent concepts
- "Coffee"
- "Heart Health"
- "Caffeine"
- "Blood Pressure"

**Edges (Lines)**: Show relationships
- Coffee → contains → Caffeine
- Coffee → affects → Heart Health
- Caffeine → increases → Blood Pressure

**Colors**: Indicate credibility
- Green = High credibility (0.8-1.0)
- Yellow = Medium credibility (0.5-0.8)
- Red = Low credibility (0.0-0.5)

**Conflicts**: Highlighted with special markers
- Shows both sides of disagreements
- Displays credibility scores for each side

---

## Technical Terms Explained

### API (Application Programming Interface)
**Simple explanation**: A way for programs to talk to each other
**Example**: When this system searches the web, it uses Tavily's API to get search results

### Agent
**Simple explanation**: A specialized AI program that does one specific job
**Example**: The Scout Agent only searches for information, the Judge Agent only evaluates credibility

### Knowledge Graph
**Simple explanation**: A visual map showing how ideas connect to each other
**Example**: Like a mind map with circles (concepts) and lines (relationships)

### Credibility Score
**Simple explanation**: A number from 0 to 1 showing how trustworthy a source is
**Example**: Harvard study = 0.95, random blog = 0.45

### LLM (Large Language Model)
**Simple explanation**: An AI that can understand and generate human language
**Example**: ChatGPT, Gemini, or in this project, Llama 3.1

### Multi-Agent System
**Simple explanation**: Multiple AI programs working together as a team
**Example**: Our 5 agents (Scout, Mapper, Adversary, Judge, Synthesis) collaborating

### Property-Based Testing
**Simple explanation**: Testing that checks if rules always work, not just specific examples
**Example**: Instead of testing "Is 2+2=4?", test "Is any number plus zero equal to itself?"

### REST API
**Simple explanation**: A way to access the system over the internet using web addresses
**Example**: Going to http://localhost:8000/api/research to start a research session

### Docker
**Simple explanation**: A tool that packages software so it runs the same way on any computer
**Example**: Like a shipping container that works on any ship

---

## How to Install and Run

### Prerequisites (What You Need First)

1. **Python 3.11 or newer**
   - What it is: A programming language
   - How to check: Open terminal and type `python --version`
   - Where to get: https://www.python.org/downloads/

2. **Free API Keys** (Don't worry, they're actually free!)
   - **Groq**: For the AI brain (14,400 requests/day free)
     - Get it: https://console.groq.com/keys
   - **Tavily**: For web searching (1,000 searches/month free)
     - Get it: https://tavily.com/

### Installation Steps

**Step 1: Download the Project**
```bash
# If you have git installed:
git clone <repository-url>
cd adversarial-knowledge-cartographer

# Or download the ZIP file from GitHub and extract it
```

**Step 2: Set Up API Keys**
```bash
# Copy the example configuration file
cp .env.example .env

# Open .env in a text editor and add your keys:
GROQ_API_KEY=your_groq_key_here
TAVILY_API_KEY=your_tavily_key_here
```

**Step 3: Install (Easiest Method)**

**On Windows**:
```bash
# Just double-click this file:
setup.bat

# Or run in terminal:
setup.bat
```

**On Mac/Linux**:
```bash
# Make it executable and run:
chmod +x setup.sh
./setup.sh
```

**Step 4: Start the System**

**On Windows**:
```bash
# Double-click this file:
start_server.bat

# Or run in terminal:
python api/app.py
```

**On Mac/Linux**:
```bash
python api/app.py
```

You should see:
```
INFO: Uvicorn running on http://0.0.0.0:8000
INFO: Application startup complete
```

**Step 5: Use the System**

Open your web browser and go to:
```
http://localhost:8000/docs
```

You'll see a web interface where you can:
1. Click on "POST /api/research"
2. Click "Try it out"
3. Type your question: "Is coffee healthy?"
4. Click "Execute"
5. Wait 2-3 minutes
6. Get your results!

---

## What Can You Use This For?

### 1. Academic Research
**Scenario**: You're writing a paper on climate change
**How it helps**: 
- Finds sources from multiple perspectives
- Identifies areas of scientific consensus
- Highlights ongoing debates
- Evaluates source credibility automatically

### 2. Fact-Checking
**Scenario**: You see a viral claim on social media
**How it helps**:
- Quickly gathers evidence for and against the claim
- Shows which sources are trustworthy
- Presents both sides fairly
- Helps you make an informed judgment

### 3. Personal Health Decisions
**Scenario**: Deciding whether to try a new diet
**How it helps**:
- Finds medical studies and expert opinions
- Identifies potential risks and benefits
- Shows where doctors disagree
- Weights evidence by source quality

### 4. Business Research
**Scenario**: Evaluating a new technology for your company
**How it helps**:
- Gathers market analysis from multiple sources
- Identifies competing viewpoints
- Shows industry consensus vs. outliers
- Helps make data-driven decisions

### 5. Understanding Controversial Topics
**Scenario**: Want to understand both sides of a political issue
**How it helps**:
- Presents arguments from all perspectives
- Evaluates source bias and credibility
- Shows where facts end and opinions begin
- Promotes balanced understanding

---

## Frequently Asked Questions

### Q: Do I need to know programming to use this?
**A**: No! Once it's installed, you just type questions into a web interface. However, basic command line knowledge helps with installation.

### Q: Is it really free?
**A**: Yes! The system uses free-tier APIs from Groq and Tavily. You can do about 200 research sessions per month at no cost.

### Q: How long does each research session take?
**A**: Typically 2-3 minutes. The system is doing a lot of work automatically that would take you hours manually.

### Q: Can I trust the results?
**A**: The system shows you exactly where information comes from and how credible each source is. You make the final judgment, but the system helps by organizing and evaluating the evidence.

### Q: What topics work best?
**A**: Controversial topics with multiple viewpoints work great:
- "Is X healthy/safe/effective?"
- "X vs Y comparison"
- "Benefits and risks of X"
- Current events with conflicting reports

### Q: What topics don't work well?
**A**: 
- Simple facts: "What is 2+2?" (use a calculator)
- Purely subjective: "What's the best color?" (no factual answer)
- Too broad: "Tell me about science" (be specific)

### Q: How is credibility calculated?
**A**: Three factors, each weighted:
- **Domain authority (40%)**: .edu and .gov sites score higher
- **Citations (30%)**: Articles with references score higher
- **Recency (30%)**: Newer information scores higher (adjustable)

### Q: Can I see the source code?
**A**: Yes! This is open-source. All code is available in the project files. The main agents are in the `agents/` folder.

### Q: What if I get an error?
**A**: Common issues:
- "API key not found": Check your .env file has the correct keys
- "Rate limit exceeded": Wait a few minutes or use fewer iterations
- "Port already in use": Another program is using port 8000, close it or use a different port

### Q: Can I customize it?
**A**: Yes! You can adjust:
- Number of sources to gather (MIN_SOURCES in .env)
- Number of iterations (MAX_ITERATIONS in .env)
- Credibility weights (DOMAIN_WEIGHT, CITATION_WEIGHT, RECENCY_WEIGHT)
- Which LLM model to use (LLM_MODEL in .env)

### Q: Does it work offline?
**A**: No, it needs internet to:
- Search for current information
- Use the AI models (Groq)
- Access web content

### Q: How accurate is it?
**A**: The system is as accurate as its sources. It doesn't create information, it analyzes existing information. The credibility scoring helps you identify more reliable sources, but you should always verify important information.

### Q: Can I use it for my homework/thesis?
**A**: Yes, but remember:
- Always cite your actual sources, not this tool
- Verify important claims independently
- Use it as a research assistant, not a replacement for critical thinking
- Check your school's policies on AI tools

---

## Next Steps

Now that you understand how the system works, you can:

1. **Try it out**: Install and run your first research query
2. **Experiment**: Try different types of questions
3. **Explore the code**: Look at the `agents/` folder to see how each agent works
4. **Customize**: Adjust settings in the `.env` file
5. **Contribute**: If you find bugs or have ideas, contribute to the project!

---

## Getting Help

If you need assistance:

1. **Check the documentation**: 
   - HOW_TO_RUN.md for installation help
   - PROJECT_SUMMARY.md for a quick overview
   - EXAMPLES.md for usage examples

2. **Common issues**: See the Troubleshooting section in PROJECT_DOCUMENTATION.md

3. **Ask questions**: Open an issue on GitHub

4. **Community**: Join discussions with other users

---

## Conclusion

The Adversarial Knowledge Cartographer is a powerful tool that automates the research process while maintaining transparency and balance. It doesn't replace human judgment, but it makes research faster, more thorough, and more balanced.

Think of it as having a team of research assistants who:
- Never get tired
- Always check multiple sources
- Actively look for opposing viewpoints
- Evaluate source credibility objectively
- Present information clearly and fairly

Whether you're a student, researcher, journalist, or just curious about controversial topics, this tool can help you make more informed decisions based on comprehensive, balanced analysis.

Happy researching!

---

**Version**: 1.0.0  
**Last Updated**: January 2026  
**License**: MIT (free to use)



---

## Project Structure Explained (For Beginners)

When you download this project, you'll see many folders and files. Here's what each one does, explained in simple terms.

### Think of It Like a House

Imagine the project as a house:
- **Rooms** = Folders (each has a specific purpose)
- **Furniture** = Files (the actual things that do work)
- **Blueprint** = Documentation (tells you how everything works)

---

### The Main Folders (Rooms in Your House)

```
adversarial-knowledge-cartographer/
├── agents/           ← The AI workers (most important!)
├── models/           ← Data blueprints
├── api/              ← The web server
├── frontend/         ← The visual interface (optional)
├── tests/            ← Quality checks
├── utils/            ← Helper tools
├── docs/             ← Instruction manuals
└── [configuration files at the root]
```

---

### 1. agents/ Folder - The AI Workers

**What it is**: The brain of the system - where the 5 AI agents live

**Think of it as**: The office where your research team works

**Files inside**:
```
agents/
├── scout.py         ← The researcher who searches the web
├── mapper.py        ← The organizer who creates knowledge maps
├── adversary.py     ← The critic who challenges findings
├── judge.py         ← The fact-checker who rates sources
├── synthesis.py     ← The writer who creates the final report
└── workflow.py      ← The manager who coordinates everyone
```

**What each file does**:

- **scout.py**: 
  - Searches Google/web for articles
  - Downloads and reads web pages
  - Collects 10-20 sources per search

- **mapper.py**:
  - Reads all the articles
  - Finds key concepts (entities)
  - Identifies relationships between concepts
  - Spots conflicts between sources

- **adversary.py**:
  - Looks for weaknesses in the research
  - Generates new search queries
  - Tries to find opposite viewpoints

- **judge.py**:
  - Evaluates each source's trustworthiness
  - Checks domain (.edu vs .com)
  - Looks for citations and references
  - Assigns credibility scores (0.0 to 1.0)

- **synthesis.py**:
  - Takes all the information
  - Writes the final report
  - Organizes consensus, conflicts, and verdicts

- **workflow.py**:
  - Coordinates all the agents
  - Decides when to loop back for more research
  - Manages the overall process

**You'll modify these if**: You want to change how the AI agents work

---

### 2. models/ Folder - Data Blueprints

**What it is**: Defines what data looks like

**Think of it as**: The forms and templates everyone uses

**Files inside**:
```
models/
└── data_models.py   ← Defines all data structures
```

**What it contains**:

- **Source**: Template for a web article (URL, title, content, domain)
- **Entity**: Template for a concept (just a name like "Coffee")
- **Relationship**: Template for connections ("Coffee" → "affects" → "Health")
- **Conflict**: Template for disagreements (Side A vs Side B)
- **KnowledgeGraph**: Template for the complete map
- **WorkflowState**: Template for tracking progress

**Example from the file**:
```python
class Source:
    url: str              # "https://harvard.edu/study"
    title: str            # "Coffee Health Benefits"
    content: str          # The article text
    domain: str           # "harvard.edu"
    retrieved_at: datetime # When we got it
```

**You'll modify this if**: You want to add new types of data

---

### 3. api/ Folder - The Web Server

**What it is**: The part that lets you use the system through a web browser

**Think of it as**: The reception desk where you submit requests

**Files inside**:
```
api/
├── app.py           ← Main server program
└── README.md        ← Instructions for the API
```

**What app.py does**:
- Starts a web server on port 8000
- Receives your research questions
- Calls the agents to do the work
- Sends back the results

**Endpoints (like different service windows)**:
- `POST /api/research` - Submit a new research question
- `GET /api/research/{id}/status` - Check if it's done
- `GET /api/research/{id}/report` - Get the final report
- `GET /api/research/{id}/graph` - Get the knowledge graph

**You'll modify this if**: You want to add new API features

---

### 4. frontend/ Folder - The Visual Interface

**What it is**: The pretty website where you can see graphs (optional)

**Think of it as**: The showroom where results are displayed nicely

**Structure**:
```
frontend/
├── src/
│   ├── components/      ← UI pieces (buttons, graphs, panels)
│   ├── services/        ← Talks to the API
│   └── utils/           ← Helper functions
├── public/              ← Images and static files
└── package.json         ← List of dependencies
```

**Key components**:
- **GraphVisualization.tsx**: Shows the 2D knowledge graph
- **Advanced3DGraph.tsx**: Shows the 3D knowledge graph
- **AnalyticsDashboard.tsx**: Shows statistics
- **DetailPanel.tsx**: Shows information about selected nodes

**You'll modify this if**: You want to change how the graphs look

---

### 5. tests/ Folder - Quality Checks

**What it is**: Automated tests that make sure everything works correctly

**Think of it as**: The quality control department

**Files inside**:
```
tests/
├── test_scout_properties.py      ← Tests for Scout agent
├── test_mapper_properties.py     ← Tests for Mapper agent
├── test_adversary_properties.py  ← Tests for Adversary agent
├── test_judge_properties.py      ← Tests for Judge agent
├── test_synthesis_properties.py  ← Tests for Synthesis agent
├── test_workflow_properties.py   ← Tests for overall workflow
└── test_api_endpoints.py         ← Tests for web server
```

**What tests do**:
- Check that agents work correctly
- Verify credibility scores are between 0 and 1
- Ensure no duplicate entities
- Confirm relationships are valid
- Test error handling

**Example test**:
```python
def test_credibility_always_valid():
    """Make sure credibility scores are always 0.0 to 1.0"""
    score = calculate_credibility("https://harvard.edu")
    assert 0.0 <= score <= 1.0  # Must be true!
```

**You'll modify this if**: You add new features and need to test them

---

### 6. utils/ Folder - Helper Tools

**What it is**: Useful functions that multiple parts of the system need

**Think of it as**: The toolbox with shared tools

**Files inside**:
```
utils/
├── error_handling.py    ← Handles errors gracefully
├── logging_config.py    ← Records what's happening
└── llm_factory.py       ← Connects to AI models (Groq)
```

**What each does**:

- **error_handling.py**: 
  - Catches errors before they crash the system
  - Provides helpful error messages
  - Logs errors for debugging

- **logging_config.py**:
  - Records what the system is doing
  - Helps debug problems
  - Tracks performance

- **llm_factory.py**:
  - Connects to Groq (the AI service)
  - Sends questions to the AI
  - Gets responses back

**You'll modify this if**: You want to change error messages or logging

---

### 7. docs/ Folder - Instruction Manuals

**What it is**: Detailed documentation about design decisions

**Think of it as**: The library with reference books

**Structure**:
```
docs/
├── adr/                 ← Architecture Decision Records
│   ├── 001-why-langgraph.md
│   ├── 002-credibility-scoring.md
│   ├── 003-property-based-testing.md
│   ├── 004-free-tier-architecture.md
│   └── 005-conflict-detection-strategy.md
└── DEPLOYMENT.md        ← How to deploy to production
```

**What ADRs are**: Documents explaining why we made certain choices

**Example**: "Why did we choose LangGraph instead of building from scratch?"

**You'll read this if**: You want to understand why things are built this way

---

### Configuration Files (At the Root)

These files sit in the main folder and control how everything works:

#### Essential Files

**`.env`** - Your Secret Settings
```
What it is: Stores your API keys and configuration
Think of it as: Your personal settings file
Contains:
- GROQ_API_KEY=your_key_here
- TAVILY_API_KEY=your_key_here
- MAX_ITERATIONS=2
- MIN_SOURCES=20
```

**`config.py`** - Configuration Manager
```
What it is: Reads the .env file and makes settings available
Think of it as: The settings reader
You'll modify: Rarely (it just reads .env)
```

**`requirements.txt`** - Python Dependencies
```
What it is: List of Python packages needed
Think of it as: Shopping list for Python libraries
Contains:
- fastapi
- langchain
- hypothesis
- pydantic
```

**`docker-compose.yml`** - Container Setup
```
What it is: Instructions for running in Docker
Think of it as: Recipe for setting up the whole system
You'll use: If you want to run with Docker
```

#### Startup Scripts

**`setup.bat`** (Windows) / **`setup.sh`** (Mac/Linux)
```
What it does: Installs everything automatically
When to use: First time setup
What it does:
1. Creates a virtual environment
2. Installs Python packages
3. Sets up the database
```

**`start_server.bat`** (Windows) / **`start_server.sh`** (Mac/Linux)
```
What it does: Starts the web server
When to use: Every time you want to use the system
What it does:
1. Activates the virtual environment
2. Starts the API server on port 8000
```

#### Documentation Files

**`README.md`** - Project Overview
```
What it is: The main introduction to the project
Read this: First, to understand what the project does
```

**`BEGINNER_GUIDE.md`** - This File!
```
What it is: Detailed explanation for beginners
Read this: To understand how everything works
```

**`PROJECT_SUMMARY.md`** - Quick Summary
```
What it is: One-page overview
Read this: When you need a quick reference
```

**`HOW_TO_RUN.md`** - Running Instructions
```
What it is: Step-by-step guide to run the system
Read this: When you're ready to start using it
```

---

### File Types Explained

You'll see different file extensions. Here's what they mean:

**`.py`** - Python Files
```
What: Python programming language files
Contains: The actual code that runs
Example: scout.py, mapper.py
```

**`.md`** - Markdown Files
```
What: Documentation files (like this one!)
Contains: Text with formatting
Example: README.md, BEGINNER_GUIDE.md
```

**`.tsx`** / **`.ts`** - TypeScript Files
```
What: TypeScript files (for the frontend)
Contains: Code for the visual interface
Example: GraphVisualization.tsx
```

**`.json`** - JSON Files
```
What: Data files in JSON format
Contains: Configuration or data
Example: package.json
```

**`.yml`** / **`.yaml`** - YAML Files
```
What: Configuration files
Contains: Settings in YAML format
Example: docker-compose.yml
```

**`.env`** - Environment File
```
What: Secret settings file
Contains: API keys and configuration
Example: .env
```

---

### How Files Work Together

Here's how a research request flows through the files:

```
1. You type a question in your browser
   ↓
2. Browser sends request to api/app.py
   ↓
3. app.py calls agents/workflow.py
   ↓
4. workflow.py coordinates the agents:
   - agents/scout.py searches the web
   - agents/mapper.py analyzes results
   - agents/adversary.py challenges findings
   - agents/judge.py scores credibility
   - agents/synthesis.py writes report
   ↓
5. Results stored using models/data_models.py
   ↓
6. app.py sends results back to browser
   ↓
7. frontend/ displays the results beautifully
```

---

### What You Need to Know vs What You Can Ignore

**If you just want to USE the system**:
- Focus on: `.env`, `start_server.bat`, `README.md`
- Ignore: Everything else

**If you want to UNDERSTAND how it works**:
- Read: `BEGINNER_GUIDE.md`, `agents/` folder
- Skim: `models/data_models.py`, `api/app.py`
- Ignore: `tests/`, `docs/`

**If you want to MODIFY the system**:
- Study: `agents/` folder, `models/data_models.py`
- Understand: `api/app.py`, `config.py`
- Reference: `tests/` folder, `docs/`

**If you want to CONTRIBUTE to the project**:
- Read everything!
- Start with: `CONTRIBUTING.md`
- Follow: Code style in existing files

---

### Common Questions About Structure

**Q: Why are there so many files?**
A: Each file has one specific job. This makes the code easier to understand and maintain. It's like having separate drawers for socks, shirts, and pants instead of one big pile.

**Q: Can I delete files I don't need?**
A: Be careful! Files are interconnected. If you don't need the frontend, you can delete the `frontend/` folder. But don't delete anything from `agents/`, `models/`, or `api/`.

**Q: Where do I start reading the code?**
A: Start with `agents/workflow.py` - it shows how everything connects. Then read each agent file (`scout.py`, `mapper.py`, etc.) in order.

**Q: What if I break something?**
A: That's what `tests/` is for! Run `pytest` to check if everything still works. If tests pass, you're probably okay.

**Q: How do I know what each function does?**
A: Look for comments and docstrings in the code:
```python
def calculate_credibility(url: str) -> float:
    """
    Calculate credibility score for a source.
    
    Args:
        url: The source URL
        
    Returns:
        Score between 0.0 and 1.0
    """
```

---

### Visual Map of the Project

```
YOUR COMPUTER
│
├── adversarial-knowledge-cartographer/  ← Main folder
│   │
│   ├── agents/          ← THE BRAIN (AI workers)
│   │   ├── scout.py     ← Searches web
│   │   ├── mapper.py    ← Organizes info
│   │   ├── adversary.py ← Challenges findings
│   │   ├── judge.py     ← Rates sources
│   │   └── synthesis.py ← Writes report
│   │
│   ├── api/             ← THE INTERFACE (web server)
│   │   └── app.py       ← Receives your questions
│   │
│   ├── models/          ← THE BLUEPRINTS (data structures)
│   │   └── data_models.py
│   │
│   ├── frontend/        ← THE DISPLAY (visual interface)
│   │   └── src/components/
│   │
│   ├── tests/           ← THE QUALITY CHECK (automated tests)
│   │
│   ├── utils/           ← THE TOOLBOX (helper functions)
│   │
│   ├── docs/            ← THE LIBRARY (documentation)
│   │
│   └── [config files]   ← THE SETTINGS (configuration)
│       ├── .env         ← Your API keys
│       ├── config.py    ← Settings manager
│       └── requirements.txt ← Dependencies
```

---

### Next Steps

Now that you understand the structure:

1. **Explore**: Open the folders and look at the files
2. **Read**: Start with `agents/workflow.py` to see how it all connects
3. **Experiment**: Try modifying small things (like credibility weights in `.env`)
4. **Test**: Run `pytest` to make sure everything still works
5. **Learn**: Read the code comments to understand what each part does

Remember: You don't need to understand everything at once. Start with the parts you're interested in and gradually explore more!

---

