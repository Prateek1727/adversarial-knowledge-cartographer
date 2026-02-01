# Adversarial Knowledge Cartographer API

FastAPI backend for the Adversarial Knowledge Cartographer research system.

## Running the API

### Development Mode

```bash
# From the project root
python api/app.py
```

Or using uvicorn directly:

```bash
uvicorn api.app:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode

```bash
uvicorn api.app:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Endpoints

### Health Check

**GET /** - Root endpoint with API information

**GET /health** - Health check endpoint

### Research Workflow

**POST /api/research** - Initiate a new research workflow

Request body:
```json
{
  "topic": "Climate change effects on agriculture"
}
```

Response:
```json
{
  "session_id": "uuid-here",
  "topic": "Climate change effects on agriculture",
  "status": "running",
  "message": "Research workflow started..."
}
```

**GET /api/research/{session_id}/status** - Get research session status

Response:
```json
{
  "session_id": "uuid-here",
  "topic": "Climate change effects on agriculture",
  "status": "completed",
  "current_phase": "synthesis",
  "iteration": 2,
  "sources_count": 15,
  "entities_count": 42,
  "relationships_count": 78,
  "conflicts_count": 5,
  "synthesis_available": true
}
```

**GET /api/research/{session_id}/graph** - Get Knowledge Graph in visualization format

Response:
```json
{
  "session_id": "uuid-here",
  "nodes": [
    {
      "id": "Entity A",
      "label": "Entity A",
      "type": "entity",
      "data": {}
    },
    {
      "id": "conflict_0",
      "label": "Point of contention",
      "type": "conflict",
      "data": {
        "side_a": "Claim A",
        "side_a_citation": "https://...",
        "side_a_credibility": 0.9,
        "side_b": "Claim B",
        "side_b_citation": "https://...",
        "side_b_credibility": 0.7
      }
    }
  ],
  "edges": [
    {
      "id": "rel_0",
      "source": "Entity A",
      "target": "Entity B",
      "label": "supports",
      "type": "support",
      "data": {
        "citation": "https://...",
        "credibility": 0.85
      }
    }
  ]
}
```

**GET /api/research/{session_id}/report** - Get synthesis report

Response:
```json
{
  "session_id": "uuid-here",
  "topic": "Climate change effects on agriculture",
  "report": "# Synthesis Report\n\n## Consensus\n..."
}
```

## Configuration

The API uses environment variables for configuration. See `.env.example` for available options:

- `API_HOST` - API server host (default: 0.0.0.0)
- `API_PORT` - API server port (default: 8000)
- `MAX_ITERATIONS` - Maximum adversarial iterations (default: 3)
- `OPENAI_API_KEY` - OpenAI API key (required if using OpenAI)
- `TAVILY_API_KEY` - Tavily search API key (required if using Tavily)

## CORS Configuration

The API is configured with permissive CORS settings for development. In production, update the `allow_origins` list in `api/app.py` to specify allowed origins.

## Session Storage

Currently, research sessions are stored in-memory. For production deployments, consider:

- Using Redis for session storage
- Using PostgreSQL for persistent storage
- Implementing session cleanup/expiration

## Testing

Run the integration tests:

```bash
pytest tests/test_api_endpoints.py -v
```

## API Documentation

Once the server is running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
