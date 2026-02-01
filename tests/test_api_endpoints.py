"""
Integration tests for FastAPI endpoints.

Tests the workflow execution endpoint, graph retrieval endpoint, and error responses.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from api.app import app, research_sessions, session_status
from models.data_models import (
    WorkflowState, KnowledgeGraph, Relationship, Conflict, Source
)


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def mock_workflow_state():
    """Create a mock workflow state with sample data."""
    kg = KnowledgeGraph(
        entities=["Entity A", "Entity B", "Entity C"],
        relationships=[
            Relationship(
                source="Entity A",
                relation="supports",
                target="Entity B",
                citation="https://example.com/source1",
                credibility=0.85
            ),
            Relationship(
                source="Entity B",
                relation="contradicts",
                target="Entity C",
                citation="https://example.com/source2",
                credibility=0.75
            )
        ],
        conflicts=[
            Conflict(
                point_of_contention="Test Conflict",
                side_a="Claim A",
                side_a_citation="https://example.com/a",
                side_b="Claim B",
                side_b_citation="https://example.com/b",
                side_a_credibility=0.9,
                side_b_credibility=0.7
            )
        ]
    )
    
    state = WorkflowState(
        topic="Test Topic",
        iteration=1,
        sources=[
            Source(
                url="https://example.com/source1",
                title="Test Source 1",
                content="Test content 1",
                domain="example.com",
                retrieved_at=datetime.utcnow(),
                query_used="test query"
            )
        ],
        knowledge_graph=kg,
        current_phase="synthesis",
        synthesis_report="Test synthesis report with findings."
    )
    
    return state


@pytest.fixture(autouse=True)
def clear_sessions():
    """Clear research sessions before and after each test."""
    research_sessions.clear()
    session_status.clear()
    yield
    research_sessions.clear()
    session_status.clear()


class TestRootEndpoints:
    """Test root and health check endpoints."""
    
    def test_root_endpoint(self, client):
        """Test root endpoint returns API information."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "status" in data
        assert data["status"] == "running"
    
    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data


class TestWorkflowExecutionEndpoint:
    """Test workflow execution endpoint (POST /api/research)."""
    
    @patch('api.app.WorkflowOrchestrator')
    def test_initiate_research_success(self, mock_orchestrator_class, client):
        """Test successful research initiation."""
        # Mock the orchestrator
        mock_orchestrator = Mock()
        mock_orchestrator_class.return_value = mock_orchestrator
        
        # Make request
        response = client.post(
            "/api/research",
            json={"topic": "Climate change effects"}
        )
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert data["topic"] == "Climate change effects"
        assert data["status"] == "running"
        assert "message" in data
        
        # Verify session was created
        session_id = data["session_id"]
        assert session_id in research_sessions
        assert session_id in session_status
    
    def test_initiate_research_empty_topic(self, client):
        """Test research initiation with empty topic."""
        response = client.post(
            "/api/research",
            json={"topic": "   "}
        )
        
        assert response.status_code == 400
        assert "non-empty" in response.json()["detail"].lower()
    
    def test_initiate_research_invalid_topic(self, client):
        """Test research initiation with invalid topic (no alphanumeric chars)."""
        response = client.post(
            "/api/research",
            json={"topic": "!!!@@@###"}
        )
        
        assert response.status_code == 400
        assert "meaningful content" in response.json()["detail"].lower()
    
    def test_initiate_research_missing_topic(self, client):
        """Test research initiation without topic field."""
        response = client.post(
            "/api/research",
            json={}
        )
        
        assert response.status_code == 422  # Validation error


class TestSessionStatusEndpoint:
    """Test session status endpoint (GET /api/research/{session_id}/status)."""
    
    def test_get_status_success(self, client, mock_workflow_state):
        """Test retrieving status for existing session."""
        # Create a session
        session_id = "test-session-123"
        research_sessions[session_id] = mock_workflow_state
        session_status[session_id] = "completed"
        
        # Get status
        response = client.get(f"/api/research/{session_id}/status")
        
        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == session_id
        assert data["topic"] == "Test Topic"
        assert data["status"] == "completed"
        assert data["current_phase"] == "synthesis"
        assert data["iteration"] == 1
        assert data["sources_count"] == 1
        assert data["entities_count"] == 3
        assert data["relationships_count"] == 2
        assert data["conflicts_count"] == 1
        assert data["synthesis_available"] is True
    
    def test_get_status_not_found(self, client):
        """Test retrieving status for non-existent session."""
        response = client.get("/api/research/nonexistent-session/status")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


class TestGraphRetrievalEndpoint:
    """Test graph retrieval endpoint (GET /api/research/{session_id}/graph)."""
    
    def test_get_graph_success(self, client, mock_workflow_state):
        """Test retrieving graph for existing session."""
        # Create a session
        session_id = "test-session-456"
        research_sessions[session_id] = mock_workflow_state
        
        # Get graph
        response = client.get(f"/api/research/{session_id}/graph")
        
        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == session_id
        assert "nodes" in data
        assert "edges" in data
        
        # Verify nodes
        nodes = data["nodes"]
        assert len(nodes) >= 3  # At least 3 entity nodes
        entity_nodes = [n for n in nodes if n["type"] == "entity"]
        assert len(entity_nodes) == 3
        assert any(n["label"] == "Entity A" for n in entity_nodes)
        
        # Verify conflict nodes
        conflict_nodes = [n for n in nodes if n["type"] == "conflict"]
        assert len(conflict_nodes) == 1
        assert conflict_nodes[0]["label"] == "Test Conflict"
        
        # Verify edges
        edges = data["edges"]
        assert len(edges) == 2
        assert any(e["label"] == "supports" for e in edges)
        assert any(e["label"] == "contradicts" for e in edges)
        
        # Verify edge data includes citation and credibility
        for edge in edges:
            assert "citation" in edge["data"]
            assert "credibility" in edge["data"]
    
    def test_get_graph_not_found(self, client):
        """Test retrieving graph for non-existent session."""
        response = client.get("/api/research/nonexistent-session/graph")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_get_graph_not_available(self, client):
        """Test retrieving graph when knowledge graph is not yet available."""
        # Create a session with empty knowledge graph
        session_id = "test-session-789"
        state = WorkflowState(
            topic="Test Topic",
            iteration=0,
            current_phase="scout"
        )
        research_sessions[session_id] = state
        
        # Try to get graph
        response = client.get(f"/api/research/{session_id}/graph")
        
        assert response.status_code == 404
        assert "not yet available" in response.json()["detail"].lower()


class TestSynthesisReportEndpoint:
    """Test synthesis report endpoint (GET /api/research/{session_id}/report)."""
    
    def test_get_report_success(self, client, mock_workflow_state):
        """Test retrieving synthesis report for completed session."""
        # Create a session
        session_id = "test-session-report"
        research_sessions[session_id] = mock_workflow_state
        
        # Get report
        response = client.get(f"/api/research/{session_id}/report")
        
        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == session_id
        assert data["topic"] == "Test Topic"
        assert data["report"] == "Test synthesis report with findings."
    
    def test_get_report_not_found(self, client):
        """Test retrieving report for non-existent session."""
        response = client.get("/api/research/nonexistent-session/report")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_get_report_not_available(self, client):
        """Test retrieving report when synthesis is not yet complete."""
        # Create a session without synthesis report
        session_id = "test-session-no-report"
        state = WorkflowState(
            topic="Test Topic",
            iteration=0,
            current_phase="scout"
        )
        research_sessions[session_id] = state
        
        # Try to get report
        response = client.get(f"/api/research/{session_id}/report")
        
        assert response.status_code == 404
        assert "not yet available" in response.json()["detail"].lower()


class TestGraphTransformation:
    """Test graph transformation logic."""
    
    def test_edge_type_classification(self, client, mock_workflow_state):
        """Test that edge types are correctly classified based on relationship."""
        session_id = "test-edge-types"
        research_sessions[session_id] = mock_workflow_state
        
        response = client.get(f"/api/research/{session_id}/graph")
        edges = response.json()["edges"]
        
        # Find the "supports" edge
        support_edge = next(e for e in edges if e["label"] == "supports")
        assert support_edge["type"] == "support"
        
        # Find the "contradicts" edge
        contradict_edge = next(e for e in edges if e["label"] == "contradicts")
        assert contradict_edge["type"] == "refute"
    
    def test_conflict_node_data(self, client, mock_workflow_state):
        """Test that conflict nodes contain all required data."""
        session_id = "test-conflict-data"
        research_sessions[session_id] = mock_workflow_state
        
        response = client.get(f"/api/research/{session_id}/graph")
        nodes = response.json()["nodes"]
        
        conflict_nodes = [n for n in nodes if n["type"] == "conflict"]
        assert len(conflict_nodes) == 1
        
        conflict = conflict_nodes[0]
        assert "side_a" in conflict["data"]
        assert "side_b" in conflict["data"]
        assert "side_a_citation" in conflict["data"]
        assert "side_b_citation" in conflict["data"]
        assert "side_a_credibility" in conflict["data"]
        assert "side_b_credibility" in conflict["data"]


class TestErrorHandling:
    """Test error handling in API endpoints."""
    
    def test_workflow_initialization_error(self, client):
        """Test handling of workflow initialization errors (validation)."""
        # Test with whitespace-only topic that passes Pydantic but fails our validation
        response = client.post(
            "/api/research",
            json={"topic": "   "}
        )
        
        assert response.status_code == 400
        assert "non-empty" in response.json()["detail"].lower()
    
    @patch('api.app.execute_workflow_background')
    def test_background_workflow_error_handling(self, mock_execute, client):
        """Test that background workflow errors are handled gracefully."""
        # The endpoint should return 200 even if background task will fail
        # The error is tracked in session_status
        response = client.post(
            "/api/research",
            json={"topic": "Test topic"}
        )
        
        assert response.status_code == 200
        session_id = response.json()["session_id"]
        
        # Verify session was created
        assert session_id in research_sessions
        assert session_id in session_status
