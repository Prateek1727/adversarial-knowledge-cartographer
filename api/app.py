"""
FastAPI application for the Adversarial Knowledge Cartographer.

This module provides REST API endpoints for:
- Initiating research workflows
- Retrieving research session status
- Retrieving Knowledge Graph data in visualization format
"""

import logging
import uuid
import time
from datetime import datetime
from typing import Dict, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from models.data_models import WorkflowState, KnowledgeGraph
from agents.workflow import WorkflowOrchestrator
from config import config
from utils.logging_config import setup_logging

# Setup logging - check for environment override
import os
log_level = os.getenv("LOG_LEVEL", config.log_level)
setup_logging(log_level)
logger = logging.getLogger(__name__)

# Log startup with current log level
logger.info(f"🚀 API starting with log level: {log_level}")

# Initialize FastAPI app
app = FastAPI(
    title="Adversarial Knowledge Cartographer API",
    description="API for autonomous research with dialectic reasoning",
    version="1.0.0"
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all HTTP requests with timing information."""
    start_time = time.time()
    
    # Log incoming request
    logger.info(f"🌐 {request.method} {request.url.path} - Client: {request.client.host if request.client else 'unknown'}")
    
    # Process request
    response = await call_next(request)
    
    # Calculate processing time
    process_time = time.time() - start_time
    
    # Log response
    status_emoji = "✅" if response.status_code < 400 else "❌"
    logger.info(f"{status_emoji} {request.method} {request.url.path} - Status: {response.status_code} - Time: {process_time:.3f}s")
    
    return response

# In-memory storage for research sessions
# In production, use a database like PostgreSQL or Redis
research_sessions: Dict[str, WorkflowState] = {}

# Session status tracking
session_status: Dict[str, str] = {}  # session_id -> status ("running", "completed", "failed")


# Request/Response Models

class ResearchRequest(BaseModel):
    """Request model for initiating research."""
    topic: str = Field(..., description="Research topic to investigate", min_length=1)


class ResearchResponse(BaseModel):
    """Response model for research initiation."""
    session_id: str = Field(..., description="Unique session ID for tracking research progress")
    topic: str = Field(..., description="Research topic")
    status: str = Field(..., description="Current status of the research session")
    message: str = Field(..., description="Status message")


class SessionStatusResponse(BaseModel):
    """Response model for session status."""
    session_id: str = Field(..., description="Session ID")
    topic: str = Field(..., description="Research topic")
    status: str = Field(..., description="Current status (running, completed, failed)")
    current_phase: str = Field(..., description="Current workflow phase")
    iteration: int = Field(..., description="Current iteration number")
    sources_count: int = Field(..., description="Number of sources collected")
    entities_count: int = Field(..., description="Number of entities extracted")
    relationships_count: int = Field(..., description="Number of relationships identified")
    conflicts_count: int = Field(..., description="Number of conflicts detected")
    synthesis_available: bool = Field(..., description="Whether synthesis report is available")


class GraphNode(BaseModel):
    """Node in the visualization graph."""
    id: str = Field(..., description="Unique node identifier")
    label: str = Field(..., description="Node label (entity name)")
    type: str = Field(..., description="Node type (entity or conflict)")
    data: Dict = Field(default_factory=dict, description="Additional node data")


class GraphEdge(BaseModel):
    """Edge in the visualization graph."""
    id: str = Field(..., description="Unique edge identifier")
    source: str = Field(..., description="Source node ID")
    target: str = Field(..., description="Target node ID")
    label: str = Field(..., description="Edge label (relationship type)")
    type: str = Field(..., description="Edge type (support, refute, neutral)")
    data: Dict = Field(default_factory=dict, description="Additional edge data")


class GraphResponse(BaseModel):
    """Response model for graph visualization data."""
    session_id: str = Field(..., description="Session ID")
    nodes: list[GraphNode] = Field(..., description="Graph nodes")
    edges: list[GraphEdge] = Field(..., description="Graph edges")


# Helper Functions

def execute_workflow_background(session_id: str, topic: str):
    """
    Execute workflow in background.
    
    Args:
        session_id: Unique session identifier
        topic: Research topic
    """
    try:
        logger.info(f"🚀 Starting background workflow execution for session {session_id}")
        logger.info(f"📝 Research topic: '{topic}'")
        session_status[session_id] = "running"
        
        # Create workflow orchestrator
        logger.info(f"🔧 Creating workflow orchestrator (max_iterations={config.max_iterations})")
        orchestrator = WorkflowOrchestrator(
            max_iterations=config.max_iterations,
            enable_checkpoints=True
        )
        
        # Execute workflow
        logger.info(f"⚡ Executing research workflow for session {session_id}")
        final_state = orchestrator.execute(topic)
        
        # Store final state
        research_sessions[session_id] = final_state
        session_status[session_id] = "completed"
        
        logger.info(f"✅ Workflow execution completed successfully for session {session_id}")
        
        # Handle both dict and WorkflowState object for logging
        if isinstance(final_state, dict):
            sources_count = len(final_state.get("sources", []))
            kg = final_state.get("knowledge_graph", {})
            if isinstance(kg, dict):
                entities_count = len(kg.get("entities", []))
                relationships_count = len(kg.get("relationships", []))
            else:
                entities_count = len(kg.entities) if kg else 0
                relationships_count = len(kg.relationships) if kg else 0
        else:
            sources_count = len(final_state.sources)
            entities_count = len(final_state.knowledge_graph.entities)
            relationships_count = len(final_state.knowledge_graph.relationships)
        
        logger.info(f"📊 Final state: {sources_count} sources, {entities_count} entities, {relationships_count} relationships")
        
    except Exception as e:
        logger.error(f"❌ Workflow execution failed for session {session_id}: {e}")
        session_status[session_id] = "failed"
        
        # Store partial state if available
        if session_id in research_sessions:
            state = research_sessions[session_id]
            # Handle both dict and WorkflowState object
            if isinstance(state, dict):
                state["status_message"] = f"Workflow failed: {str(e)}"
            else:
                state.status_message = f"Workflow failed: {str(e)}"


def transform_graph_to_visualization(kg: KnowledgeGraph) -> tuple[list[GraphNode], list[GraphEdge]]:
    """
    Transform Knowledge Graph to visualization format.
    
    Args:
        kg: Knowledge Graph to transform
        
    Returns:
        Tuple of (nodes, edges) for visualization
    """
    nodes = []
    edges = []
    
    # Create nodes for entities
    for entity in kg.entities:
        node = GraphNode(
            id=entity,
            label=entity,
            type="entity",
            data={}
        )
        nodes.append(node)
    
    # Create edges for relationships
    for idx, rel in enumerate(kg.relationships):
        edge_type = "neutral"
        
        # Determine edge type based on relationship
        relation_lower = rel.relation.lower()
        if any(word in relation_lower for word in ["support", "increase", "cause", "enable"]):
            edge_type = "support"
        elif any(word in relation_lower for word in ["refute", "decrease", "prevent", "contradict"]):
            edge_type = "refute"
        
        edge = GraphEdge(
            id=f"rel_{idx}",
            source=rel.source,
            target=rel.target,
            label=rel.relation,
            type=edge_type,
            data={
                "citation": rel.citation,
                "credibility": rel.credibility
            }
        )
        edges.append(edge)
    
    # Create nodes and edges for conflicts
    for idx, conflict in enumerate(kg.conflicts):
        # Create a conflict node
        conflict_id = f"conflict_{idx}"
        conflict_node = GraphNode(
            id=conflict_id,
            label=conflict.point_of_contention,
            type="conflict",
            data={
                "side_a": conflict.side_a,
                "side_a_citation": conflict.side_a_citation,
                "side_a_credibility": conflict.side_a_credibility,
                "side_b": conflict.side_b,
                "side_b_citation": conflict.side_b_citation,
                "side_b_credibility": conflict.side_b_credibility
            }
        )
        nodes.append(conflict_node)
    
    return nodes, edges


# API Endpoints

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "Adversarial Knowledge Cartographer API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint with rate limit info."""
    health_info = {
        "status": "healthy", 
        "timestamp": datetime.utcnow().isoformat(),
        "llm_provider": config.llm_provider,
        "llm_model": config.llm_model
    }
    
    # Add rate limit guidance for Groq
    if config.llm_provider == "groq":
        health_info["rate_limits"] = {
            "daily_requests": "14,400 per day",
            "tokens_per_minute": "6,000 per minute",
            "recommendation": "Use MAX_ITERATIONS=1-2 for large topics"
        }
    
    return health_info


@app.post("/api/research", response_model=ResearchResponse)
async def initiate_research(
    request: ResearchRequest,
    background_tasks: BackgroundTasks
):
    """
    Initiate a new research workflow.
    
    This endpoint accepts a research topic and starts an asynchronous workflow
    that gathers sources, builds a knowledge graph, and generates a synthesis report.
    
    Args:
        request: Research request with topic
        background_tasks: FastAPI background tasks
        
    Returns:
        ResearchResponse with session ID for tracking
        
    Raises:
        HTTPException: If topic validation fails
    """
    try:
        # Validate topic
        topic = request.topic.strip()
        if not topic:
            raise HTTPException(
                status_code=400,
                detail="Topic must be non-empty"
            )
        
        if not any(c.isalnum() for c in topic):
            raise HTTPException(
                status_code=400,
                detail="Topic must contain meaningful content (alphanumeric characters)"
            )
        
        # Generate unique session ID
        session_id = str(uuid.uuid4())
        
        logger.info(f"🆔 Generated new session ID: {session_id}")
        logger.info(f"📋 Initializing research workflow for topic: '{topic}'")
        
        # Initialize workflow state
        initial_state = WorkflowState(
            topic=topic,
            iteration=0,
            max_iterations=config.max_iterations,
            current_phase="initialized",
            status_message=f"Research workflow initialized for topic: '{topic}'"
        )
        
        # Store initial state
        research_sessions[session_id] = initial_state
        session_status[session_id] = "running"
        
        logger.info(f"💾 Stored initial state for session {session_id}")
        
        # Execute workflow in background
        background_tasks.add_task(execute_workflow_background, session_id, topic)
        logger.info(f"🔄 Added background task for session {session_id}")
        
        logger.info(f"✨ Research initiated successfully for session {session_id}: '{topic}'")
        
        return ResearchResponse(
            session_id=session_id,
            topic=topic,
            status="running",
            message=f"Research workflow started for topic: '{topic}'"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to initiate research: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to initiate research: {str(e)}"
        )


@app.get("/api/research/{session_id}/status", response_model=SessionStatusResponse)
async def get_session_status(session_id: str):
    """
    Get the status of a research session.
    
    Args:
        session_id: Unique session identifier
        
    Returns:
        SessionStatusResponse with current status and progress
        
    Raises:
        HTTPException: If session not found
    """
    logger.info(f"📊 Status check requested for session {session_id}")
    
    if session_id not in research_sessions:
        logger.warning(f"⚠️ Session {session_id} not found")
        raise HTTPException(
            status_code=404,
            detail=f"Session {session_id} not found"
        )
    
    state = research_sessions[session_id]
    status = session_status.get(session_id, "unknown")
    
    # Handle both dict (from checkpoint) and WorkflowState object
    if isinstance(state, dict):
        kg = state.get("knowledge_graph", {})
        return SessionStatusResponse(
            session_id=session_id,
            topic=state.get("topic", ""),
            status=status,
            current_phase=state.get("current_phase", "unknown"),
            iteration=state.get("iteration", 0),
            sources_count=len(state.get("sources", [])),
            entities_count=len(kg.get("entities", [])) if isinstance(kg, dict) else (len(kg.entities) if kg else 0),
            relationships_count=len(kg.get("relationships", [])) if isinstance(kg, dict) else (len(kg.relationships) if kg else 0),
            conflicts_count=len(kg.get("conflicts", [])) if isinstance(kg, dict) else (len(kg.conflicts) if kg else 0),
            synthesis_available=state.get("synthesis_report") is not None
        )
    else:
        # WorkflowState object
        return SessionStatusResponse(
            session_id=session_id,
            topic=state.topic,
            status=status,
            current_phase=state.current_phase,
            iteration=state.iteration,
            sources_count=len(state.sources),
            entities_count=len(state.knowledge_graph.entities),
            relationships_count=len(state.knowledge_graph.relationships),
            conflicts_count=len(state.knowledge_graph.conflicts),
            synthesis_available=state.synthesis_report is not None
        )


@app.get("/api/research/{session_id}/graph", response_model=GraphResponse)
async def get_knowledge_graph(session_id: str):
    """
    Get the Knowledge Graph in visualization format.
    
    This endpoint transforms the Knowledge Graph into a format suitable for
    visualization libraries like React Flow or D3.js, with nodes representing
    entities and edges representing relationships.
    
    Args:
        session_id: Unique session identifier
        
    Returns:
        GraphResponse with nodes and edges arrays
        
    Raises:
        HTTPException: If session not found or graph not available
    """
    if session_id not in research_sessions:
        raise HTTPException(
            status_code=404,
            detail=f"Session {session_id} not found"
        )
    
    state = research_sessions[session_id]
    
    # Handle both dict and WorkflowState object
    if isinstance(state, dict):
        kg_data = state.get("knowledge_graph", {})
        if isinstance(kg_data, dict):
            entities = kg_data.get("entities", [])
        else:
            entities = kg_data.entities if kg_data else []
        
        if not entities:
            raise HTTPException(
                status_code=404,
                detail=f"Knowledge graph not yet available for session {session_id}"
            )
        
        # Reconstruct KnowledgeGraph if needed
        if isinstance(kg_data, dict):
            from models.data_models import Relationship, Conflict
            kg = KnowledgeGraph(
                entities=kg_data.get("entities", []),
                relationships=[Relationship(**r) if isinstance(r, dict) else r for r in kg_data.get("relationships", [])],
                conflicts=[Conflict(**c) if isinstance(c, dict) else c for c in kg_data.get("conflicts", [])]
            )
        else:
            kg = kg_data
    else:
        # WorkflowState object
        if not state.knowledge_graph.entities:
            raise HTTPException(
                status_code=404,
                detail=f"Knowledge graph not yet available for session {session_id}"
            )
        kg = state.knowledge_graph
    
    # Transform graph to visualization format
    nodes, edges = transform_graph_to_visualization(kg)
    
    logger.info(
        f"Retrieved graph for session {session_id}: "
        f"{len(nodes)} nodes, {len(edges)} edges"
    )
    
    return GraphResponse(
        session_id=session_id,
        nodes=nodes,
        edges=edges
    )


@app.get("/api/research/{session_id}/report")
async def get_synthesis_report(session_id: str):
    """
    Get the synthesis report for a completed research session.
    
    Args:
        session_id: Unique session identifier
        
    Returns:
        Synthesis report as plain text
        
    Raises:
        HTTPException: If session not found or report not available
    """
    if session_id not in research_sessions:
        raise HTTPException(
            status_code=404,
            detail=f"Session {session_id} not found"
        )
    
    state = research_sessions[session_id]
    
    # Handle both dict and WorkflowState object
    if isinstance(state, dict):
        synthesis_report = state.get("synthesis_report")
        topic = state.get("topic", "")
    else:
        synthesis_report = state.synthesis_report
        topic = state.topic
    
    if not synthesis_report:
        raise HTTPException(
            status_code=404,
            detail=f"Synthesis report not yet available for session {session_id}"
        )
    
    return {
        "session_id": session_id,
        "topic": topic,
        "report": synthesis_report
    }


@app.get("/api/research/{session_id}/graph/stats")
async def get_graph_statistics(session_id: str):
    """
    Get statistical information about the knowledge graph.
    
    Args:
        session_id: Unique session identifier
        
    Returns:
        Graph statistics including node counts, edge counts, and metrics
        
    Raises:
        HTTPException: If session not found or graph not available
    """
    if session_id not in research_sessions:
        raise HTTPException(
            status_code=404,
            detail=f"Session {session_id} not found"
        )
    
    state = research_sessions[session_id]
    
    # Handle both dict and WorkflowState object
    if isinstance(state, dict):
        kg_data = state.get("knowledge_graph", {})
        if isinstance(kg_data, dict):
            entities = kg_data.get("entities", [])
            relationships = kg_data.get("relationships", [])
            conflicts = kg_data.get("conflicts", [])
        else:
            entities = kg_data.entities if kg_data else []
            relationships = kg_data.relationships if kg_data else []
            conflicts = kg_data.conflicts if kg_data else []
    else:
        # WorkflowState object
        entities = state.knowledge_graph.entities
        relationships = state.knowledge_graph.relationships
        conflicts = state.knowledge_graph.conflicts
    
    if not entities:
        raise HTTPException(
            status_code=404,
            detail=f"Knowledge graph not yet available for session {session_id}"
        )
    
    # Calculate statistics
    total_nodes = len(entities) + len(conflicts)
    total_edges = len(relationships)
    
    # Calculate relationship type distribution
    relationship_types = {}
    for rel in relationships:
        rel_type = "neutral"
        if hasattr(rel, 'relation'):
            relation_lower = rel.relation.lower()
        else:
            relation_lower = rel.get('relation', '').lower()
            
        if any(word in relation_lower for word in ["support", "increase", "cause", "enable"]):
            rel_type = "support"
        elif any(word in relation_lower for word in ["refute", "decrease", "prevent", "contradict"]):
            rel_type = "refute"
        
        relationship_types[rel_type] = relationship_types.get(rel_type, 0) + 1
    
    # Calculate average credibility
    credibilities = []
    for rel in relationships:
        if hasattr(rel, 'credibility'):
            credibilities.append(rel.credibility)
        elif isinstance(rel, dict) and 'credibility' in rel:
            credibilities.append(rel['credibility'])
    
    avg_credibility = sum(credibilities) / len(credibilities) if credibilities else 0
    
    return {
        "session_id": session_id,
        "total_entities": len(entities),
        "total_conflicts": len(conflicts),
        "total_nodes": total_nodes,
        "total_relationships": total_edges,
        "relationship_types": relationship_types,
        "average_credibility": round(avg_credibility, 3),
        "graph_density": round(total_edges / (total_nodes * (total_nodes - 1)) if total_nodes > 1 else 0, 3)
    }


@app.get("/api/research/{session_id}/graph/entities")
async def get_entities_list(session_id: str):
    """
    Get a list of all entities in the knowledge graph with their connection counts.
    
    Args:
        session_id: Unique session identifier
        
    Returns:
        List of entities with metadata
        
    Raises:
        HTTPException: If session not found or graph not available
    """
    if session_id not in research_sessions:
        raise HTTPException(
            status_code=404,
            detail=f"Session {session_id} not found"
        )
    
    state = research_sessions[session_id]
    
    # Handle both dict and WorkflowState object
    if isinstance(state, dict):
        kg_data = state.get("knowledge_graph", {})
        if isinstance(kg_data, dict):
            entities = kg_data.get("entities", [])
            relationships = kg_data.get("relationships", [])
        else:
            entities = kg_data.entities if kg_data else []
            relationships = kg_data.relationships if kg_data else []
    else:
        # WorkflowState object
        entities = state.knowledge_graph.entities
        relationships = state.knowledge_graph.relationships
    
    if not entities:
        raise HTTPException(
            status_code=404,
            detail=f"Knowledge graph not yet available for session {session_id}"
        )
    
    # Count connections for each entity
    entity_connections = {entity: 0 for entity in entities}
    
    for rel in relationships:
        source = rel.source if hasattr(rel, 'source') else rel.get('source')
        target = rel.target if hasattr(rel, 'target') else rel.get('target')
        
        if source in entity_connections:
            entity_connections[source] += 1
        if target in entity_connections:
            entity_connections[target] += 1
    
    # Create entity list with metadata
    entity_list = []
    for entity in entities:
        entity_list.append({
            "name": entity,
            "connections": entity_connections[entity],
            "type": "entity"
        })
    
    # Sort by connection count (most connected first)
    entity_list.sort(key=lambda x: x["connections"], reverse=True)
    
    return {
        "session_id": session_id,
        "entities": entity_list,
        "total_count": len(entity_list)
    }


@app.get("/api/research/{session_id}/graph/conflicts")
async def get_conflicts_list(session_id: str):
    """
    Get a detailed list of all conflicts in the knowledge graph.
    
    Args:
        session_id: Unique session identifier
        
    Returns:
        List of conflicts with full details
        
    Raises:
        HTTPException: If session not found or graph not available
    """
    if session_id not in research_sessions:
        raise HTTPException(
            status_code=404,
            detail=f"Session {session_id} not found"
        )
    
    state = research_sessions[session_id]
    
    # Handle both dict and WorkflowState object
    if isinstance(state, dict):
        kg_data = state.get("knowledge_graph", {})
        if isinstance(kg_data, dict):
            conflicts = kg_data.get("conflicts", [])
        else:
            conflicts = kg_data.conflicts if kg_data else []
    else:
        # WorkflowState object
        conflicts = state.knowledge_graph.conflicts
    
    # Format conflicts for response
    conflict_list = []
    for idx, conflict in enumerate(conflicts):
        if hasattr(conflict, 'point_of_contention'):
            # Conflict object
            conflict_data = {
                "id": f"conflict_{idx}",
                "point_of_contention": conflict.point_of_contention,
                "side_a": conflict.side_a,
                "side_a_citation": conflict.side_a_citation,
                "side_a_credibility": conflict.side_a_credibility,
                "side_b": conflict.side_b,
                "side_b_citation": conflict.side_b_citation,
                "side_b_credibility": conflict.side_b_credibility
            }
        else:
            # Dict format
            conflict_data = {
                "id": f"conflict_{idx}",
                "point_of_contention": conflict.get("point_of_contention", ""),
                "side_a": conflict.get("side_a", ""),
                "side_a_citation": conflict.get("side_a_citation", ""),
                "side_a_credibility": conflict.get("side_a_credibility", 0),
                "side_b": conflict.get("side_b", ""),
                "side_b_citation": conflict.get("side_b_citation", ""),
                "side_b_credibility": conflict.get("side_b_credibility", 0)
            }
        
        conflict_list.append(conflict_data)
    
    return {
        "session_id": session_id,
        "conflicts": conflict_list,
        "total_count": len(conflict_list)
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=config.api_host,
        port=config.api_port,
        log_level=config.log_level.lower()
    )
