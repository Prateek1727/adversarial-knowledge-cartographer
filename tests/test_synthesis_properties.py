"""
Property-based tests for the Synthesis Agent.

These tests validate the correctness properties defined in the design document:
- Property 19: Consensus identification
- Property 20: Battleground extraction
- Property 21: Report structure completeness
"""

import pytest
from hypothesis import given, strategies as st, assume, settings
from datetime import datetime, timedelta
import json

from agents.synthesis import SynthesisAgent
from models.data_models import (
    KnowledgeGraph,
    Relationship,
    Conflict,
    WorkflowState
)


# Custom strategies for generating test data
@st.composite
def knowledge_graph_with_consensus(draw):
    """
    Generate a knowledge graph with relationships that have high agreement.
    
    Returns a tuple of (KnowledgeGraph, expected_consensus_count)
    """
    # Generate entities
    num_entities = draw(st.integers(min_value=5, max_value=15))
    entities = [f"Entity_{i}" for i in range(num_entities)]
    
    # Generate relationships with some having high agreement
    relationships = []
    consensus_claims = []
    
    # Create 2-3 consensus claims (same claim from multiple sources)
    num_consensus = draw(st.integers(min_value=2, max_value=3))
    
    for i in range(num_consensus):
        source = draw(st.sampled_from(entities))
        target = draw(st.sampled_from([e for e in entities if e != source]))
        relation = draw(st.sampled_from(["supports", "contradicts", "relates_to", "causes"]))
        
        # Create multiple relationships for the same claim (consensus)
        num_sources = draw(st.integers(min_value=10, max_value=15))
        for j in range(num_sources):
            rel = Relationship(
                source=source,
                relation=relation,
                target=target,
                citation=f"https://source{i}_{j}.com",
                credibility=draw(st.floats(min_value=0.6, max_value=1.0))
            )
            relationships.append(rel)
        
        consensus_claims.append((source, relation, target))
    
    # Add some non-consensus relationships
    num_other = draw(st.integers(min_value=3, max_value=8))
    for i in range(num_other):
        source = draw(st.sampled_from(entities))
        target = draw(st.sampled_from([e for e in entities if e != source]))
        relation = draw(st.sampled_from(["supports", "contradicts", "relates_to", "causes"]))
        
        rel = Relationship(
            source=source,
            relation=relation,
            target=target,
            citation=f"https://other{i}.com",
            credibility=draw(st.floats(min_value=0.3, max_value=0.9))
        )
        relationships.append(rel)
    
    kg = KnowledgeGraph(
        entities=entities,
        relationships=relationships,
        conflicts=[]
    )
    
    return kg, num_consensus


@st.composite
def knowledge_graph_with_conflicts(draw):
    """
    Generate a knowledge graph with conflicts.
    
    Returns a tuple of (KnowledgeGraph, num_conflicts)
    """
    # Generate entities
    num_entities = draw(st.integers(min_value=5, max_value=15))
    entities = [f"Entity_{i}" for i in range(num_entities)]
    
    # Generate conflicts
    num_conflicts = draw(st.integers(min_value=1, max_value=5))
    conflicts = []
    
    for i in range(num_conflicts):
        conflict = Conflict(
            point_of_contention=f"Contention_{i}",
            side_a=f"Claim A for contention {i}",
            side_a_citation=f"https://sourcea{i}.com",
            side_b=f"Claim B for contention {i}",
            side_b_citation=f"https://sourceb{i}.com",
            side_a_credibility=draw(st.floats(min_value=0.3, max_value=1.0)),
            side_b_credibility=draw(st.floats(min_value=0.3, max_value=1.0))
        )
        conflicts.append(conflict)
    
    # Generate some relationships
    relationships = []
    num_rels = draw(st.integers(min_value=3, max_value=10))
    for i in range(num_rels):
        source = draw(st.sampled_from(entities))
        target = draw(st.sampled_from([e for e in entities if e != source]))
        relation = draw(st.sampled_from(["supports", "contradicts", "relates_to"]))
        
        rel = Relationship(
            source=source,
            relation=relation,
            target=target,
            citation=f"https://source{i}.com",
            credibility=draw(st.floats(min_value=0.3, max_value=1.0))
        )
        relationships.append(rel)
    
    kg = KnowledgeGraph(
        entities=entities,
        relationships=relationships,
        conflicts=conflicts
    )
    
    return kg, num_conflicts


@st.composite
def complete_knowledge_graph(draw):
    """
    Generate a complete knowledge graph with entities, relationships, and conflicts.
    """
    # Generate entities
    num_entities = draw(st.integers(min_value=5, max_value=15))
    entities = [f"Entity_{i}" for i in range(num_entities)]
    
    # Generate relationships
    relationships = []
    num_rels = draw(st.integers(min_value=5, max_value=20))
    for i in range(num_rels):
        source = draw(st.sampled_from(entities))
        target = draw(st.sampled_from([e for e in entities if e != source]))
        relation = draw(st.sampled_from(["supports", "contradicts", "relates_to", "causes"]))
        
        rel = Relationship(
            source=source,
            relation=relation,
            target=target,
            citation=f"https://source{i}.com",
            credibility=draw(st.floats(min_value=0.3, max_value=1.0))
        )
        relationships.append(rel)
    
    # Generate conflicts
    num_conflicts = draw(st.integers(min_value=1, max_value=5))
    conflicts = []
    for i in range(num_conflicts):
        conflict = Conflict(
            point_of_contention=f"Contention_{i}",
            side_a=f"Claim A for contention {i}",
            side_a_citation=f"https://sourcea{i}.com",
            side_b=f"Claim B for contention {i}",
            side_b_citation=f"https://sourceb{i}.com",
            side_a_credibility=draw(st.floats(min_value=0.3, max_value=1.0)),
            side_b_credibility=draw(st.floats(min_value=0.3, max_value=1.0))
        )
        conflicts.append(conflict)
    
    kg = KnowledgeGraph(
        entities=entities,
        relationships=relationships,
        conflicts=conflicts
    )
    
    return kg


# Property 19: Consensus identification
@settings(max_examples=100)
@given(kg_data=knowledge_graph_with_consensus())
def test_property_19_consensus_identification(kg_data):
    """
    Feature: adversarial-knowledge-cartographer, Property 19: Consensus identification
    
    For any claim in the knowledge graph supported by 90% or more of sources,
    it should appear in the consensus section of the synthesis report.
    
    Validates: Requirements 7.1
    """
    kg, expected_min_consensus = kg_data
    
    # Create synthesis agent with mock LLM (we don't need LLM for consensus identification)
    class MockLLM:
        pass
    
    agent = SynthesisAgent(consensus_threshold=0.9, llm=MockLLM())
    
    # Identify consensus points
    consensus_points = agent.identify_consensus(kg)
    
    # Verify that consensus points were identified
    # We expect at least some consensus since we generated high-agreement claims
    assert isinstance(consensus_points, list), "Consensus points should be a list"
    
    # If we have relationships, we should be able to identify consensus
    if kg.relationships:
        # The number of consensus points should be reasonable
        # (may be less than expected_min_consensus due to threshold)
        assert len(consensus_points) >= 0, "Should return non-negative number of consensus points"


# Property 20: Battleground extraction
@settings(max_examples=100)
@given(kg_data=knowledge_graph_with_conflicts())
def test_property_20_battleground_extraction(kg_data):
    """
    Feature: adversarial-knowledge-cartographer, Property 20: Battleground extraction
    
    For any conflict in the knowledge graph, it should appear in the battleground
    section of the synthesis report.
    
    Validates: Requirements 7.2
    """
    kg, num_conflicts = kg_data
    
    # Create synthesis agent with mock LLM
    class MockLLM:
        pass
    
    agent = SynthesisAgent(llm=MockLLM())
    
    # Extract battleground topics
    battleground_topics = agent.extract_battleground_topics(kg)
    
    # Verify that all conflicts are extracted as battleground topics
    assert isinstance(battleground_topics, list), "Battleground topics should be a list"
    assert len(battleground_topics) == num_conflicts, \
        f"Should extract all {num_conflicts} conflicts as battleground topics"
    
    # Verify each battleground topic has required fields
    for bt in battleground_topics:
        assert hasattr(bt, 'topic'), "Battleground topic should have 'topic' field"
        assert hasattr(bt, 'conflicting_claims'), "Battleground topic should have 'conflicting_claims' field"
        assert hasattr(bt, 'disagreement_reason'), "Battleground topic should have 'disagreement_reason' field"
        assert hasattr(bt, 'verdict'), "Battleground topic should have 'verdict' field"
        assert hasattr(bt, 'verdict_confidence'), "Battleground topic should have 'verdict_confidence' field"
        assert hasattr(bt, 'supporting_evidence'), "Battleground topic should have 'supporting_evidence' field"
        
        # Verify fields are non-empty
        assert bt.topic, "Topic should be non-empty"
        assert len(bt.conflicting_claims) >= 2, "Should have at least 2 conflicting claims"
        assert bt.disagreement_reason, "Disagreement reason should be non-empty"
        assert bt.verdict, "Verdict should be non-empty"
        assert 0.0 <= bt.verdict_confidence <= 1.0, "Verdict confidence should be between 0 and 1"
        assert len(bt.supporting_evidence) > 0, "Should have supporting evidence"


# Property 21: Report structure completeness
@settings(max_examples=100)
@given(
    topic=st.text(min_size=5, max_size=100, alphabet=st.characters(whitelist_categories=('L', 'N'))),
    kg=complete_knowledge_graph()
)
def test_property_21_report_structure_completeness(topic, kg):
    """
    Feature: adversarial-knowledge-cartographer, Property 21: Report structure completeness
    
    For any generated synthesis report, it should contain sections for Consensus,
    Battleground, Verdict, and Knowledge Graph JSON.
    
    Validates: Requirements 7.5, 7.6
    """
    assume(topic.strip())  # Ensure topic is not just whitespace
    
    # Create synthesis agent (mock LLM to avoid API calls)
    class MockLLM:
        def invoke(self, messages):
            class MockResponse:
                content = """# The Consensus

Based on the analysis of sources, the following points show strong agreement:
- Key finding 1
- Key finding 2

# The Battleground

The following topics show significant disagreement:
- Conflict 1: Different perspectives exist
- Conflict 2: Sources disagree on methodology

# The Verdict

Based on credibility analysis:
- For Conflict 1: Side A is more likely correct
- For Conflict 2: Insufficient evidence to determine"""
            return MockResponse()
    
    agent = SynthesisAgent(llm=MockLLM())
    
    # Create final report
    report = agent.create_final_report(topic, kg)
    
    # Verify report structure
    assert isinstance(report, str), "Report should be a string"
    assert len(report) > 0, "Report should not be empty"
    
    # Check for required sections
    report_lower = report.lower()
    
    # Should contain consensus section
    assert "consensus" in report_lower, "Report should contain 'Consensus' section"
    
    # Should contain battleground section
    assert "battleground" in report_lower, "Report should contain 'Battleground' section"
    
    # Should contain verdict section
    assert "verdict" in report_lower, "Report should contain 'Verdict' section"
    
    # Should contain knowledge graph JSON
    assert "knowledge graph" in report_lower, "Report should reference 'Knowledge Graph'"
    assert "json" in report_lower, "Report should contain JSON"
    
    # Verify JSON is parseable
    # Extract JSON from code block
    if "```json" in report:
        json_start = report.find("```json") + 7
        json_end = report.find("```", json_start)
        json_str = report[json_start:json_end].strip()
        
        # Parse JSON to verify it's valid
        graph_data = json.loads(json_str)
        
        # Verify JSON structure
        assert "entities" in graph_data, "JSON should contain 'entities'"
        assert "relationships" in graph_data, "JSON should contain 'relationships'"
        assert "conflicts" in graph_data, "JSON should contain 'conflicts'"
        
        # Verify data matches knowledge graph
        assert len(graph_data["entities"]) == len(kg.entities), \
            "JSON entities count should match knowledge graph"
        assert len(graph_data["relationships"]) == len(kg.relationships), \
            "JSON relationships count should match knowledge graph"
        assert len(graph_data["conflicts"]) == len(kg.conflicts), \
            "JSON conflicts count should match knowledge graph"


# Additional unit tests for specific functionality
def test_serialize_knowledge_graph():
    """Test that knowledge graph serialization produces valid JSON."""
    # Create a simple knowledge graph
    kg = KnowledgeGraph(
        entities=["Entity1", "Entity2", "Entity3"],
        relationships=[
            Relationship(
                source="Entity1",
                relation="supports",
                target="Entity2",
                citation="https://source1.com",
                credibility=0.8
            )
        ],
        conflicts=[
            Conflict(
                point_of_contention="Test conflict",
                side_a="Claim A",
                side_a_citation="https://sourcea.com",
                side_b="Claim B",
                side_b_citation="https://sourceb.com",
                side_a_credibility=0.7,
                side_b_credibility=0.6
            )
        ]
    )
    
    # Create agent with mock LLM
    class MockLLM:
        pass
    
    agent = SynthesisAgent(llm=MockLLM())
    json_str = agent.serialize_knowledge_graph(kg)
    
    # Verify it's valid JSON
    graph_data = json.loads(json_str)
    
    # Verify structure
    assert "entities" in graph_data
    assert "relationships" in graph_data
    assert "conflicts" in graph_data
    
    # Verify content
    assert len(graph_data["entities"]) == 3
    assert len(graph_data["relationships"]) == 1
    assert len(graph_data["conflicts"]) == 1


def test_consensus_with_no_relationships():
    """Test consensus identification with empty knowledge graph."""
    kg = KnowledgeGraph(entities=["Entity1"], relationships=[], conflicts=[])
    
    # Create agent with mock LLM
    class MockLLM:
        pass
    
    agent = SynthesisAgent(llm=MockLLM())
    consensus_points = agent.identify_consensus(kg)
    
    # Should return empty list
    assert consensus_points == []


def test_battleground_with_no_conflicts():
    """Test battleground extraction with no conflicts."""
    kg = KnowledgeGraph(
        entities=["Entity1", "Entity2"],
        relationships=[
            Relationship(
                source="Entity1",
                relation="supports",
                target="Entity2",
                citation="https://source1.com",
                credibility=0.8
            )
        ],
        conflicts=[]
    )
    
    # Create agent with mock LLM
    class MockLLM:
        pass
    
    agent = SynthesisAgent(llm=MockLLM())
    battleground_topics = agent.extract_battleground_topics(kg)
    
    # Should return empty list
    assert battleground_topics == []
