"""
Property-based tests for workflow orchestration.

These tests validate universal properties that should hold across all inputs
for workflow initialization and execution.
"""

import pytest
from hypothesis import given, strategies as st, assume, settings
from unittest.mock import Mock
from agents.workflow import WorkflowOrchestrator
from agents.scout import ScoutAgent
from agents.mapper import MapperAgent
from agents.adversary import AdversaryAgent
from models.data_models import WorkflowState


# Property 1: Workflow initialization with valid topics
@given(st.text(min_size=1, max_size=500))
@settings(deadline=None)
def test_property_1_workflow_initialization_valid_topics(topic: str):
    """
    Feature: adversarial-knowledge-cartographer, Property 1: 
    Workflow initialization with valid topics
    
    For any non-empty topic string with alphanumeric content, initializing 
    the workflow should transition the system state to Scout Phase and emit 
    a status message.
    
    Validates: Requirements 1.1, 1.3, 1.4
    """
    # Assume topic has meaningful content (at least one alphanumeric character)
    assume(any(c.isalnum() for c in topic))
    assume(topic.strip())  # Not just whitespace
    
    # Create orchestrator with mock agents
    mock_scout = Mock(spec=ScoutAgent)
    mock_mapper = Mock(spec=MapperAgent)
    mock_adversary = Mock(spec=AdversaryAgent)
    mock_judge = Mock()
    mock_synthesis = Mock()
    orchestrator = WorkflowOrchestrator(
        max_iterations=3,
        scout_agent=mock_scout,
        mapper_agent=mock_mapper,
        adversary_agent=mock_adversary,
        judge_agent=mock_judge,
        synthesis_agent=mock_synthesis
    )
    state = orchestrator.initialize(topic)
    
    # Verify state is properly initialized
    assert isinstance(state, WorkflowState)
    assert state.topic == topic.strip()
    assert state.current_phase == "initialized"
    assert state.status_message is not None
    assert len(state.status_message) > 0
    assert state.iteration == 0
    assert state.max_iterations == 3


# Property 2: Invalid topic rejection
@given(
    st.one_of(
        st.just(""),  # Empty string
        st.text(alphabet=" \t\n\r", min_size=1, max_size=20),  # Whitespace only
        st.text(alphabet="!@#$%^&*()_+-=[]{}|;:',.<>?/~`", min_size=1, max_size=20)  # Special chars only
    )
)
@settings(deadline=None)
def test_property_2_invalid_topic_rejection(topic: str):
    """
    Feature: adversarial-knowledge-cartographer, Property 2: 
    Invalid topic rejection
    
    For any string composed entirely of whitespace or special characters 
    (no alphanumeric content), the system should reject the topic and not 
    initialize the workflow.
    
    Validates: Requirements 1.2
    """
    # Create orchestrator with mock agents
    mock_scout = Mock(spec=ScoutAgent)
    mock_mapper = Mock(spec=MapperAgent)
    mock_adversary = Mock(spec=AdversaryAgent)
    mock_judge = Mock()
    mock_synthesis = Mock()
    orchestrator = WorkflowOrchestrator(
        max_iterations=3,
        scout_agent=mock_scout,
        mapper_agent=mock_mapper,
        adversary_agent=mock_adversary,
        judge_agent=mock_judge,
        synthesis_agent=mock_synthesis
    )
    
    # Should raise ValueError for invalid topics
    with pytest.raises(ValueError) as exc_info:
        orchestrator.initialize(topic)
    
    # Verify error message is meaningful
    assert "Topic must" in str(exc_info.value) or "meaningful content" in str(exc_info.value)


# Additional edge case tests for topic validation
def test_empty_string_topic():
    """Test that empty string is rejected."""
    mock_scout = Mock(spec=ScoutAgent)
    mock_mapper = Mock(spec=MapperAgent)
    mock_adversary = Mock(spec=AdversaryAgent)
    mock_judge = Mock()
    mock_synthesis = Mock()
    orchestrator = WorkflowOrchestrator(scout_agent=mock_scout, mapper_agent=mock_mapper, adversary_agent=mock_adversary, judge_agent=mock_judge, synthesis_agent=mock_synthesis)
    with pytest.raises(ValueError):
        orchestrator.initialize("")


def test_whitespace_only_topic():
    """Test that whitespace-only strings are rejected."""
    mock_scout = Mock(spec=ScoutAgent)
    mock_mapper = Mock(spec=MapperAgent)
    mock_adversary = Mock(spec=AdversaryAgent)
    mock_judge = Mock()
    mock_synthesis = Mock()
    orchestrator = WorkflowOrchestrator(scout_agent=mock_scout, mapper_agent=mock_mapper, adversary_agent=mock_adversary, judge_agent=mock_judge, synthesis_agent=mock_synthesis)
    for whitespace in ["   ", "\t", "\n", " \t\n "]:
        with pytest.raises(ValueError):
            orchestrator.initialize(whitespace)


def test_special_characters_only_topic():
    """Test that strings with only special characters are rejected."""
    mock_scout = Mock(spec=ScoutAgent)
    mock_mapper = Mock(spec=MapperAgent)
    mock_adversary = Mock(spec=AdversaryAgent)
    mock_judge = Mock()
    mock_synthesis = Mock()
    orchestrator = WorkflowOrchestrator(scout_agent=mock_scout, mapper_agent=mock_mapper, adversary_agent=mock_adversary, judge_agent=mock_judge, synthesis_agent=mock_synthesis)
    for special in ["!!!", "...", "---", "###", "***"]:
        with pytest.raises(ValueError):
            orchestrator.initialize(special)


def test_valid_topic_with_leading_trailing_whitespace():
    """Test that valid topics with whitespace are trimmed."""
    mock_scout = Mock(spec=ScoutAgent)
    mock_mapper = Mock(spec=MapperAgent)
    mock_adversary = Mock(spec=AdversaryAgent)
    mock_judge = Mock()
    mock_synthesis = Mock()
    orchestrator = WorkflowOrchestrator(scout_agent=mock_scout, mapper_agent=mock_mapper, adversary_agent=mock_adversary, judge_agent=mock_judge, synthesis_agent=mock_synthesis)
    state = orchestrator.initialize("  valid topic  ")
    assert state.topic == "valid topic"
    assert state.status_message is not None


def test_valid_topic_with_mixed_content():
    """Test that topics with alphanumeric and special characters work."""
    mock_scout = Mock(spec=ScoutAgent)
    mock_mapper = Mock(spec=MapperAgent)
    mock_adversary = Mock(spec=AdversaryAgent)
    mock_judge = Mock()
    mock_synthesis = Mock()
    orchestrator = WorkflowOrchestrator(scout_agent=mock_scout, mapper_agent=mock_mapper, adversary_agent=mock_adversary, judge_agent=mock_judge, synthesis_agent=mock_synthesis)
    topics = [
        "AI safety",
        "climate-change",
        "COVID-19 vaccines",
        "What is quantum computing?",
        "Machine learning (ML) basics"
    ]
    for topic in topics:
        state = orchestrator.initialize(topic)
        assert state.topic == topic.strip()
        assert state.current_phase == "initialized"
        assert state.status_message is not None



# Property 17: Maximum iteration limit
@given(st.integers(min_value=1, max_value=10))
@settings(deadline=None)
def test_property_17_maximum_iteration_limit(max_iterations: int):
    """
    Feature: adversarial-knowledge-cartographer, Property 17: 
    Maximum iteration limit
    
    For any workflow execution, the system should not exceed the configured
    maximum number of Scout-Mapper-Adversary cycles before proceeding to Synthesis.
    
    Validates: Requirements 6.4
    """
    # Create orchestrator with mock agents
    mock_scout = Mock(spec=ScoutAgent)
    mock_mapper = Mock(spec=MapperAgent)
    mock_adversary = Mock(spec=AdversaryAgent)
    mock_judge = Mock()
    mock_synthesis = Mock()
    orchestrator = WorkflowOrchestrator(
        max_iterations=max_iterations,
        scout_agent=mock_scout,
        mapper_agent=mock_mapper,
        adversary_agent=mock_adversary,
        judge_agent=mock_judge,
        synthesis_agent=mock_synthesis
    )
    
    # Create a state that simulates being at the iteration limit
    state = WorkflowState(
        topic="test topic",
        iteration=max_iterations,
        max_iterations=max_iterations,
        current_phase="adversary",
        adversarial_queries=["query1", "query2", "query3"]  # Weak claims found
    )
    
    # The decision function should return "proceed" when at max iterations
    decision = orchestrator._should_continue_iteration(state)
    assert decision == "proceed", f"Expected 'proceed' at max iterations, got '{decision}'"
    
    # Test one iteration before the limit
    if max_iterations > 1:
        state_before_limit = WorkflowState(
            topic="test topic",
            iteration=max_iterations - 1,
            max_iterations=max_iterations,
            current_phase="adversary",
            adversarial_queries=["query1", "query2", "query3"]  # Weak claims found
        )
        
        decision_before = orchestrator._should_continue_iteration(state_before_limit)
        assert decision_before == "continue", f"Expected 'continue' before max iterations, got '{decision_before}'"


def test_iteration_limit_with_no_weak_claims():
    """Test that workflow proceeds when no weak claims are found, regardless of iteration count."""
    mock_scout = Mock(spec=ScoutAgent)
    mock_mapper = Mock(spec=MapperAgent)
    mock_adversary = Mock(spec=AdversaryAgent)
    mock_judge = Mock()
    mock_synthesis = Mock()
    orchestrator = WorkflowOrchestrator(max_iterations=3, scout_agent=mock_scout, mapper_agent=mock_mapper, adversary_agent=mock_adversary, judge_agent=mock_judge, synthesis_agent=mock_synthesis)
    
    # State with no adversarial queries (no weak claims)
    state = WorkflowState(
        topic="test topic",
        iteration=1,
        max_iterations=3,
        current_phase="adversary",
        adversarial_queries=[]  # No weak claims
    )
    
    decision = orchestrator._should_continue_iteration(state)
    assert decision == "proceed", "Should proceed when no weak claims found"


def test_iteration_limit_at_zero():
    """Test that iteration 0 with weak claims continues."""
    mock_scout = Mock(spec=ScoutAgent)
    mock_mapper = Mock(spec=MapperAgent)
    mock_adversary = Mock(spec=AdversaryAgent)
    mock_judge = Mock()
    mock_synthesis = Mock()
    orchestrator = WorkflowOrchestrator(max_iterations=3, scout_agent=mock_scout, mapper_agent=mock_mapper, adversary_agent=mock_adversary, judge_agent=mock_judge, synthesis_agent=mock_synthesis)
    
    state = WorkflowState(
        topic="test topic",
        iteration=0,
        max_iterations=3,
        current_phase="adversary",
        adversarial_queries=["query1"]  # Weak claims found
    )
    
    decision = orchestrator._should_continue_iteration(state)
    assert decision == "continue", "Should continue at iteration 0 with weak claims"


def test_iteration_exactly_at_limit():
    """Test that reaching exactly the max iteration limit triggers proceed."""
    for max_iter in [1, 2, 3, 5, 10]:
        mock_scout = Mock(spec=ScoutAgent)
        mock_mapper = Mock(spec=MapperAgent)
        mock_adversary = Mock(spec=AdversaryAgent)
        mock_judge = Mock()
        mock_synthesis = Mock()
        orchestrator = WorkflowOrchestrator(max_iterations=max_iter, scout_agent=mock_scout, mapper_agent=mock_mapper, adversary_agent=mock_adversary, judge_agent=mock_judge, synthesis_agent=mock_synthesis)
        
        state = WorkflowState(
            topic="test topic",
            iteration=max_iter,
            max_iterations=max_iter,
            current_phase="adversary",
            adversarial_queries=["query1", "query2"]  # Weak claims present
        )
        
        decision = orchestrator._should_continue_iteration(state)
        assert decision == "proceed", f"Should proceed at max_iterations={max_iter}"
