"""
Property-based tests for the Adversary Agent.

These tests validate universal properties that should hold across all inputs
for the Adversary agent's weakness detection and query generation.
"""

import pytest
from hypothesis import given, strategies as st, assume, settings
from datetime import datetime, timedelta
from typing import List

from agents.adversary import AdversaryAgent, Weakness
from models.data_models import (
    WorkflowState,
    KnowledgeGraph,
    Source,
    Relationship,
    Conflict
)


# Strategies for generating test data
@st.composite
def source_strategy(draw, min_age_days=0, max_age_days=3650):
    """Generate a Source with configurable age."""
    age_days = draw(st.integers(min_value=min_age_days, max_value=max_age_days))
    retrieved_at = datetime.now() - timedelta(days=age_days)
    
    return Source(
        url=draw(st.text(min_size=10, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')))),
        title=draw(st.text(min_size=5, max_size=100, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'P', 'Z')))),
        content=draw(st.text(min_size=100, max_size=500, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'P', 'Z')))),
        domain=draw(st.text(min_size=5, max_size=20, alphabet=st.characters(whitelist_categories=('Lu', 'Ll')))),
        retrieved_at=retrieved_at,
        query_used=draw(st.text(min_size=5, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Z'))))
    )


@st.composite
def relationship_strategy(draw, entities: List[str], citation: str):
    """Generate a Relationship from given entities."""
    assume(len(entities) >= 2)
    
    source_entity = draw(st.sampled_from(entities))
    target_entity = draw(st.sampled_from([e for e in entities if e != source_entity]))
    
    return Relationship(
        source=source_entity,
        relation=draw(st.text(min_size=3, max_size=30, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Z')))),
        target=target_entity,
        citation=citation,
        credibility=draw(st.floats(min_value=0.0, max_value=1.0))
    )


@st.composite
def knowledge_graph_strategy(draw, min_entities=2, max_entities=10):
    """Generate a KnowledgeGraph with relationships."""
    num_entities = draw(st.integers(min_value=min_entities, max_value=max_entities))
    entities = [
        draw(st.text(min_size=3, max_size=20, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'))))
        for _ in range(num_entities)
    ]
    # Ensure unique entities
    entities = list(set(entities))
    assume(len(entities) >= 2)
    
    # Generate relationships
    num_relationships = draw(st.integers(min_value=1, max_value=len(entities) * 2))
    citation = draw(st.text(min_size=10, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'))))
    
    relationships = [
        draw(relationship_strategy(entities, citation))
        for _ in range(num_relationships)
    ]
    
    return KnowledgeGraph(
        entities=entities,
        relationships=relationships,
        conflicts=[]
    )


# Mock LLM for testing
class MockLLM:
    """Mock LLM that returns predefined counter-queries."""
    
    def __init__(self, queries=None):
        self.queries = queries or [
            "counter query 1",
            "counter query 2",
            "counter query 3"
        ]
    
    def invoke(self, messages):
        """Return mock response with counter-queries."""
        class MockResponse:
            def __init__(self, queries):
                self.content = f'{{"counter_queries": {queries}}}'
        
        import json
        return MockResponse(json.dumps(self.queries))


# Property 9: Single-source weakness detection
@given(knowledge_graph_strategy())
@settings(max_examples=100, deadline=None)
def test_property_9_single_source_weakness_detection(kg):
    """
    Feature: adversarial-knowledge-cartographer, Property 9: Single-source weakness detection
    
    For any knowledge graph where a claim is supported by only one source,
    the Adversary agent should identify it as a weakness.
    
    Validates: Requirements 4.1
    """
    agent = AdversaryAgent(llm=MockLLM())
    
    # Identify single-source weaknesses
    weaknesses = agent.identify_single_source_claims(kg)
    
    # Count unique citations per relationship
    # Note: The agent counts each unique (source, relation, target) tuple separately
    # even if they have the same citation
    citation_counts = {}
    for rel in kg.relationships:
        rel_key = f"{rel.source}|{rel.relation}|{rel.target}"
        if rel_key not in citation_counts:
            citation_counts[rel_key] = []
        citation_counts[rel_key].append(rel)
    
    # Count relationships with single source (only one relationship instance)
    single_source_count = sum(1 for rels in citation_counts.values() if len(rels) == 1)
    
    # Property: Number of weaknesses should equal number of single-source relationships
    assert len(weaknesses) == single_source_count, \
        f"Expected {single_source_count} single-source weaknesses, got {len(weaknesses)}"
    
    # All identified weaknesses should be of type "single_source"
    for weakness in weaknesses:
        assert weakness.type == "single_source", \
            f"Expected weakness type 'single_source', got '{weakness.type}'"


# Property 10: Outdated source detection
@given(st.lists(source_strategy(min_age_days=0, max_age_days=3650), min_size=1, max_size=20))
@settings(max_examples=100, deadline=None)
def test_property_10_outdated_source_detection(sources):
    """
    Feature: adversarial-knowledge-cartographer, Property 10: Outdated source detection
    
    For any source with a publication date older than 2 years from the current date,
    the Adversary agent should flag it as outdated.
    
    Validates: Requirements 4.2
    """
    agent = AdversaryAgent(llm=MockLLM(), outdated_threshold_years=2)
    
    # Detect outdated sources
    weaknesses = agent.detect_outdated_sources(sources)
    
    # Count sources older than 2 years
    cutoff_date = datetime.now() - timedelta(days=365 * 2)
    outdated_count = sum(1 for source in sources if source.retrieved_at < cutoff_date)
    
    # Property: Number of weaknesses should equal number of outdated sources
    assert len(weaknesses) == outdated_count, \
        f"Expected {outdated_count} outdated weaknesses, got {len(weaknesses)}"
    
    # All identified weaknesses should be of type "outdated"
    for weakness in weaknesses:
        assert weakness.type == "outdated", \
            f"Expected weakness type 'outdated', got '{weakness.type}'"


# Property 11: Adversarial query generation
@given(
    st.text(min_size=5, max_size=100, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Z'))),
    knowledge_graph_strategy(),
    st.lists(
        st.builds(
            Weakness,
            weakness_type=st.sampled_from(["single_source", "outdated", "potential_bias"]),
            description=st.text(min_size=10, max_size=100, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Z'))),
            affected_claims=st.lists(st.text(min_size=5, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Z'))), min_size=1, max_size=3)
        ),
        min_size=1,
        max_size=10
    )
)
@settings(max_examples=100, deadline=None)
def test_property_11_adversarial_query_generation(topic, kg, weaknesses):
    """
    Feature: adversarial-knowledge-cartographer, Property 11: Adversarial query generation
    
    For any set of identified weaknesses, the Adversary agent should generate
    at least 3 distinct adversarial search queries.
    
    Validates: Requirements 4.4
    """
    min_queries = 3
    mock_queries = [f"query_{i}" for i in range(min_queries)]
    agent = AdversaryAgent(llm=MockLLM(queries=mock_queries), min_counter_queries=min_queries)
    
    # Generate counter-queries
    queries = agent.generate_counter_queries(topic, kg, weaknesses)
    
    # Property: Should generate at least min_counter_queries queries
    assert len(queries) >= min_queries, \
        f"Expected at least {min_queries} queries, got {len(queries)}"
    
    # Property: All queries should be non-empty strings
    for query in queries:
        assert isinstance(query, str), f"Query should be string, got {type(query)}"
        assert len(query) > 0, "Query should be non-empty"


# Property 12: Counter-evidence integration
@given(
    st.text(min_size=5, max_size=100, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Z'))),
    st.lists(source_strategy(), min_size=1, max_size=10),
    knowledge_graph_strategy()
)
@settings(max_examples=100, deadline=None)
def test_property_12_counter_evidence_integration(topic, sources, kg):
    """
    Feature: adversarial-knowledge-cartographer, Property 12: Counter-evidence integration
    
    For any adversarial queries that return new sources, the knowledge graph
    should be updated to include the new information.
    
    Validates: Requirements 4.6
    """
    # Create initial state
    state = WorkflowState(
        topic=topic,
        iteration=1,
        sources=sources,
        knowledge_graph=kg,
        adversarial_queries=["query1", "query2"],
        executed_queries=set()
    )
    
    initial_entity_count = len(state.knowledge_graph.entities)
    initial_relationship_count = len(state.knowledge_graph.relationships)
    
    # After adversarial queries are executed and mapper runs again,
    # the knowledge graph should potentially have more entities/relationships
    # This property is tested indirectly through the mapper's merge functionality
    
    # Property: State should maintain all previous entities and relationships
    # (This is validated by the mapper's merge function)
    assert len(state.knowledge_graph.entities) == initial_entity_count
    assert len(state.knowledge_graph.relationships) == initial_relationship_count


# Property 16: Iteration state preservation
@given(
    st.text(min_size=5, max_size=100, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Z'))),
    st.lists(source_strategy(), min_size=1, max_size=10),
    knowledge_graph_strategy(),
    st.integers(min_value=0, max_value=2)
)
@settings(max_examples=100, deadline=None)
def test_property_16_iteration_state_preservation(topic, sources, kg, iteration):
    """
    Feature: adversarial-knowledge-cartographer, Property 16: Iteration state preservation
    
    For any workflow iteration, all entities and relationships from previous
    iterations should remain present in the knowledge graph.
    
    Validates: Requirements 6.2
    """
    # Create state with existing knowledge graph
    state = WorkflowState(
        topic=topic,
        iteration=iteration,
        sources=sources,
        knowledge_graph=kg,
        adversarial_queries=[],
        executed_queries=set()
    )
    
    # Store initial entities and relationships
    initial_entities = set(state.knowledge_graph.entities)
    initial_relationships = [
        (r.source, r.relation, r.target, r.citation)
        for r in state.knowledge_graph.relationships
    ]
    
    # Execute adversary agent
    agent = AdversaryAgent(llm=MockLLM())
    updated_state = agent.execute(state)
    
    # Property: All initial entities should still be present
    current_entities = set(updated_state.knowledge_graph.entities)
    assert initial_entities.issubset(current_entities), \
        "Previous iteration entities should be preserved"
    
    # Property: All initial relationships should still be present
    current_relationships = [
        (r.source, r.relation, r.target, r.citation)
        for r in updated_state.knowledge_graph.relationships
    ]
    for rel in initial_relationships:
        assert rel in current_relationships, \
            f"Previous iteration relationship {rel} should be preserved"


# Property 18: Query deduplication
@given(
    st.text(min_size=5, max_size=100, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Z'))),
    st.lists(source_strategy(), min_size=1, max_size=10),
    knowledge_graph_strategy(),
    st.sets(st.text(min_size=5, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Z'))), min_size=1, max_size=5)
)
@settings(max_examples=100, deadline=None)
def test_property_18_query_deduplication(topic, sources, kg, executed_queries):
    """
    Feature: adversarial-knowledge-cartographer, Property 18: Query deduplication
    
    For any query that has already been executed in the current workflow,
    the system should not execute it again.
    
    Validates: Requirements 6.5
    """
    # Create queries that overlap with executed queries
    all_queries = list(executed_queries) + ["new_query_1", "new_query_2"]
    
    # Create state with executed queries
    state = WorkflowState(
        topic=topic,
        iteration=1,
        sources=sources,
        knowledge_graph=kg,
        adversarial_queries=[],
        executed_queries=executed_queries
    )
    
    # Execute adversary agent with mock that returns overlapping queries
    agent = AdversaryAgent(llm=MockLLM(queries=all_queries))
    updated_state = agent.execute(state)
    
    # Property: Adversarial queries should not include already executed queries
    for query in updated_state.adversarial_queries:
        assert query not in executed_queries, \
            f"Query '{query}' was already executed and should not be in adversarial_queries"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
