# Quick Start Guide

## Installation

### Automated Setup (Recommended)

**Windows:**
```bash
setup.bat
```

**macOS/Linux:**
```bash
chmod +x setup.sh
./setup.sh
```

### Manual Setup

1. Create virtual environment:
```bash
python -m venv venv
```

2. Activate virtual environment:
   - **Windows:** `venv\Scripts\activate`
   - **macOS/Linux:** `source venv/bin/activate`

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit `.env` and add your API keys:
   - Get OpenAI API key: https://platform.openai.com/api-keys
   - Get Tavily API key: https://tavily.com/

Minimum required configuration:
```
LLM_PROVIDER=openai
OPENAI_API_KEY=your_key_here
SEARCH_PROVIDER=tavily
TAVILY_API_KEY=your_key_here
```

## Verify Installation

Run the configuration test:
```bash
pytest tests/test_config.py -v
```

Run the main application:
```bash
python main.py
```

## Next Steps

- Review the [README.md](README.md) for detailed documentation
- Check the design document at `.kiro/specs/adversarial-knowledge-cartographer/design.md`
- Review the requirements at `.kiro/specs/adversarial-knowledge-cartographer/requirements.md`
- Follow the implementation tasks at `.kiro/specs/adversarial-knowledge-cartographer/tasks.md`

## Troubleshooting

### "No module named pytest"
Make sure you've activated the virtual environment and installed dependencies:
```bash
# Windows
venv\Scripts\activate
pip install -r requirements.txt

# macOS/Linux
source venv/bin/activate
pip install -r requirements.txt
```

### "Configuration error: OPENAI_API_KEY environment variable is required"
Make sure you've:
1. Created a `.env` file (copy from `.env.example`)
2. Added your API keys to the `.env` file
3. Restarted your terminal or reloaded environment variables

### Python version issues
This project requires Python 3.11 or higher. Check your version:
```bash
python --version
```
