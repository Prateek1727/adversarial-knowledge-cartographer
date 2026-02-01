"""
Property-based tests for the Judge Agent.

These tests verify universal properties that should hold across all inputs
for credibility scoring, annotation, and conflict resolution.
"""

import pytest
from datetime import datetime, timedelta
from hypothesis import given, strategies as st, assume, settings
from agents.judge import JudgeAgent
from models.data_models import (
    Source,
    KnowledgeGraph,
    Relationship,
    Conflict,
    CredibilityScore
)


# Custom strategies for generating test data
@st.composite
def source_strategy(draw):
    """Generate a random Source object."""
    domains = [
        'example.edu',
        'example.gov',
        'example.org',
        'example.com',
        'nature.com',
        'arxiv.org',
        'wikipedia.org'
    ]
    
    domain = draw(st.sampled_from(domains))
    url = f"https://{domain}/article/{draw(st.integers(min_value=1, max_value=10000))}"
    title = draw(st.text(min_size=10, max_size=100))
    
    # Generate content with varying citation indicators
    content_base = draw(st.text(min_size=100, max_size=1000))
    
    # Randomly add citation indicators
    if draw(st.booleans()):
        content_base += "\n\nReferences:\n[1] Some citation\n[2] Another citation"
    if draw(st.booleans()):
        content_base += "\nDr. Smith, PhD"
    
    # Generate a date within the last 10 years
    days_ago = draw(st.integers(min_value=0, max_value=3650))
    retrieved_at = datetime.now() - timedelta(days=days_ago)
    
    return Source(
        url=url,
        title=title,
        content=content_base,
        domain=domain,
        retrieved_at=retrieved_at,
        query_used=draw(st.text(min_size=5, max_size=50))
    )


@st.composite
def relationship_strategy(draw, entities, source_urls):
    """Generate a random Relationship object."""
    assume(len(entities) >= 2)
    assume(len(source_urls) >= 1)
    
    source_entity = draw(st.sampled_from(entities))
    target_entity = draw(st.sampled_from([e for e in entities if e != source_entity]))
    relation = draw(st.text(min_size=5, max_size=50))
    citation = draw(st.sampled_from(source_urls))
    
    return Relationship(
        source=source_entity,
        relation=relation,
        target=target_entity,
        citation=citation,
        credibility=1.0
    )


@st.composite
def conflict_strategy(draw, source_urls):
    """Generate a random Conflict object."""
    assume(len(source_urls) >= 2)
    
    return Conflict(
        point_of_contention=draw(st.text(min_size=10, max_size=100)),
        side_a=draw(st.text(min_size=10, max_size=100)),
        side_a_citation=draw(st.sampled_from(source_urls)),
        side_b=draw(st.text(min_size=10, max_size=100)),
        side_b_citation=draw(st.sampled_from(source_urls)),
        side_a_credibility=1.0,
        side_b_credibility=1.0
    )


@st.composite
def knowledge_graph_strategy(draw):
    """Generate a random KnowledgeGraph with relationships and conflicts."""
    # Generate entities
    num_entities = draw(st.integers(min_value=2, max_value=10))
    entities = [f"Entity_{i}" for i in range(num_entities)]
    
    # Generate sources
    num_sources = draw(st.integers(min_value=2, max_value=5))
    sources = [draw(source_strategy()) for _ in range(num_sources)]
    source_urls = [s.url for s in sources]
    
    # Generate relationships
    num_relationships = draw(st.integers(min_value=1, max_value=10))
    relationships = [
        draw(relationship_strategy(entities, source_urls))
        for _ in range(num_relationships)
    ]
    
    # Generate conflicts
    num_conflicts = draw(st.integers(min_value=0, max_value=5))
    conflicts = [
        draw(conflict_strategy(source_urls))
        for _ in range(num_conflicts)
    ]
    
    kg = KnowledgeGraph(
        entities=entities,
        relationships=relationships,
        conflicts=conflicts
    )
    
    return kg, sources


# Property 13: Credibility score normalization
@given(source_strategy())
@settings(max_examples=100)
def test_property_13_credibility_score_normalization(source):
    """
    Feature: adversarial-knowledge-cartographer, Property 13: Credibility score normalization
    
    For any source evaluated by the Judge agent, the assigned credibility score
    should be a float between 0.0 and 1.0 inclusive.
    
    Validates: Requirements 5.3
    """
    judge = JudgeAgent()
    
    # Evaluate source credibility
    credibility_score = judge.evaluate_source_credibility(source)
    
    # Verify all component scores are normalized
    assert 0.0 <= credibility_score.domain_authority <= 1.0, \
        f"Domain authority {credibility_score.domain_authority} not in [0, 1]"
    
    assert 0.0 <= credibility_score.citation_indicators <= 1.0, \
        f"Citation indicators {credibility_score.citation_indicators} not in [0, 1]"
    
    assert 0.0 <= credibility_score.recency <= 1.0, \
        f"Recency {credibility_score.recency} not in [0, 1]"
    
    assert 0.0 <= credibility_score.overall_score <= 1.0, \
        f"Overall score {credibility_score.overall_score} not in [0, 1]"


# Property 14: Credibility annotation completeness
@given(knowledge_graph_strategy())
@settings(max_examples=100)
def test_property_14_credibility_annotation_completeness(graph_and_sources):
    """
    Feature: adversarial-knowledge-cartographer, Property 14: Credibility annotation completeness
    
    For any relationship in the knowledge graph after Judge phase, it should have
    a credibility score field populated.
    
    Validates: Requirements 5.5
    """
    knowledge_graph, sources = graph_and_sources
    judge = JudgeAgent()
    
    # Evaluate all sources
    credibility_scores = judge.evaluate_all_sources(sources)
    
    # Annotate knowledge graph
    annotated_graph = judge.annotate_knowledge_graph(knowledge_graph, credibility_scores)
    
    # Verify all relationships have credibility scores
    for rel in annotated_graph.relationships:
        assert hasattr(rel, 'credibility'), \
            f"Relationship missing credibility field: {rel}"
        
        assert 0.0 <= rel.credibility <= 1.0, \
            f"Relationship credibility {rel.credibility} not in [0, 1]"
    
    # Verify all conflicts have credibility scores for both sides
    for conflict in annotated_graph.conflicts:
        assert hasattr(conflict, 'side_a_credibility'), \
            f"Conflict missing side_a_credibility field: {conflict}"
        
        assert hasattr(conflict, 'side_b_credibility'), \
            f"Conflict missing side_b_credibility field: {conflict}"
        
        assert 0.0 <= conflict.side_a_credibility <= 1.0, \
            f"Conflict side A credibility {conflict.side_a_credibility} not in [0, 1]"
        
        assert 0.0 <= conflict.side_b_credibility <= 1.0, \
            f"Conflict side B credibility {conflict.side_b_credibility} not in [0, 1]"


# Property 15: Conflict resolution by credibility
@given(st.floats(min_value=0.0, max_value=1.0), st.floats(min_value=0.0, max_value=1.0))
@settings(max_examples=100)
def test_property_15_conflict_resolution_by_credibility(side_a_cred, side_b_cred):
    """
    Feature: adversarial-knowledge-cartographer, Property 15: Conflict resolution by credibility
    
    For any conflict with two sides having different credibility scores, the verdict
    should favor the side with the higher credibility score.
    
    Validates: Requirements 5.4, 7.4
    """
    judge = JudgeAgent()
    
    # Create a conflict with the given credibility scores
    conflict = Conflict(
        point_of_contention="Test conflict",
        side_a="Side A claim",
        side_a_citation="https://example.com/a",
        side_b="Side B claim",
        side_b_citation="https://example.com/b",
        side_a_credibility=side_a_cred,
        side_b_credibility=side_b_cred
    )
    
    # Resolve the conflict
    resolution = judge.resolve_conflict(conflict)
    
    # Verify resolution matches credibility comparison
    if side_a_cred > side_b_cred:
        assert resolution == "side_a", \
            f"Expected side_a to win ({side_a_cred} > {side_b_cred}), got {resolution}"
    elif side_b_cred > side_a_cred:
        assert resolution == "side_b", \
            f"Expected side_b to win ({side_b_cred} > {side_a_cred}), got {resolution}"
    else:
        assert resolution == "tie", \
            f"Expected tie ({side_a_cred} == {side_b_cred}), got {resolution}"
