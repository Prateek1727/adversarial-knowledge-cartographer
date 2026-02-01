"""
Property-based tests for core data models.

These tests validate universal properties that should hold across all inputs
using the Hypothesis property-based testing framework.
"""

import json
from datetime import datetime
from hypothesis import given, strategies as st, assume
from models import (
    Source,
    Relationship,
    Conflict,
    KnowledgeGraph,
    CredibilityScore,
    WorkflowState,
)


# Custom strategies for generating test data
def non_empty_text_strategy():
    """Generate non-empty, non-whitespace text that is JSON-serializable."""
    return st.text(
        min_size=1,
        alphabet=st.characters(
            blacklist_characters="\x00\n\r\t ",
            blacklist_categories=("Zs", "Cc", "Cs")  # Cs = surrogate characters
        )
    ).filter(lambda x: x.strip())


@st.composite
def source_strategy(draw):
    """Generate valid Source objects."""
    return Source(
        url=draw(non_empty_text_strategy()),
        title=draw(non_empty_text_strategy()),
        content=draw(non_empty_text_strategy()),
        domain=draw(non_empty_text_strategy()),
        retrieved_at=datetime.now(),
        query_used=draw(st.text()),
    )


@st.composite
def relationship_strategy(draw, entities=None):
    """Generate valid Relationship objects."""
    if entities is None or len(entities) < 2:
        source = draw(non_empty_text_strategy())
        target = draw(non_empty_text_strategy())
    else:
        source = draw(st.sampled_from(entities))
        target = draw(st.sampled_from(entities))
    
    return Relationship(
        source=source,
        relation=draw(non_empty_text_strategy()),
        target=target,
        citation=draw(non_empty_text_strategy()),
        credibility=draw(st.floats(min_value=0.0, max_value=1.0)),
    )


@st.composite
def conflict_strategy(draw):
    """Generate valid Conflict objects."""
    return Conflict(
        point_of_contention=draw(non_empty_text_strategy()),
        side_a=draw(non_empty_text_strategy()),
        side_a_citation=draw(non_empty_text_strategy()),
        side_b=draw(non_empty_text_strategy()),
        side_b_citation=draw(non_empty_text_strategy()),
        side_a_credibility=draw(st.floats(min_value=0.0, max_value=1.0)),
        side_b_credibility=draw(st.floats(min_value=0.0, max_value=1.0)),
    )


@st.composite
def knowledge_graph_strategy(draw):
    """Generate valid KnowledgeGraph objects with referential integrity."""
    # Generate unique entities
    num_entities = draw(st.integers(min_value=2, max_value=10))
    entities = []
    for i in range(num_entities):
        entity = draw(non_empty_text_strategy())
        if entity not in entities:
            entities.append(entity)
    
    # Generate relationships that reference existing entities
    num_relationships = draw(st.integers(min_value=0, max_value=5))
    relationships = []
    for _ in range(num_relationships):
        if len(entities) >= 2:
            rel = draw(relationship_strategy(entities=entities))
            relationships.append(rel)
    
    # Generate conflicts
    num_conflicts = draw(st.integers(min_value=0, max_value=3))
    conflicts = [draw(conflict_strategy()) for _ in range(num_conflicts)]
    
    return KnowledgeGraph(
        entities=entities,
        relationships=relationships,
        conflicts=conflicts,
    )


# Feature: adversarial-knowledge-cartographer, Property 8: Knowledge graph JSON validity
@given(knowledge_graph_strategy())
def test_property_8_knowledge_graph_json_validity(kg):
    """
    **Feature: adversarial-knowledge-cartographer, Property 8: Knowledge graph JSON validity**
    **Validates: Requirements 3.5, 8.1, 8.5**
    
    For any knowledge graph output by the Mapper, serializing to JSON and parsing back
    should produce an equivalent structure that validates against the KnowledgeGraph schema.
    """
    # Serialize to JSON
    json_str = kg.model_dump_json()
    
    # Parse back from JSON
    parsed_data = json.loads(json_str)
    
    # Validate against schema by creating new instance
    kg_reconstructed = KnowledgeGraph(**parsed_data)
    
    # Verify equivalence
    assert kg_reconstructed.entities == kg.entities
    assert len(kg_reconstructed.relationships) == len(kg.relationships)
    assert len(kg_reconstructed.conflicts) == len(kg.conflicts)
    
    # Verify it's valid JSON
    assert isinstance(json_str, str)
    assert len(json_str) > 0


# Feature: adversarial-knowledge-cartographer, Property 22: Entity uniqueness in graph
@given(st.lists(non_empty_text_strategy(), min_size=1, max_size=20))
def test_property_22_entity_uniqueness_in_graph(entity_list):
    """
    **Feature: adversarial-knowledge-cartographer, Property 22: Entity uniqueness in graph**
    **Validates: Requirements 8.2**
    
    For any knowledge graph, the entities list should contain no duplicate entity identifiers.
    """
    # Remove duplicates to create valid input
    unique_entities = list(dict.fromkeys(entity_list))
    
    # Create knowledge graph with unique entities
    kg = KnowledgeGraph(entities=unique_entities)
    
    # Verify no duplicates
    assert len(kg.entities) == len(set(kg.entities))
    
    # Verify that attempting to create a graph with duplicates fails
    if len(entity_list) != len(unique_entities):
        try:
            KnowledgeGraph(entities=entity_list)
            assert False, "Should have raised ValueError for duplicate entities"
        except ValueError:
            pass  # Expected behavior


# Feature: adversarial-knowledge-cartographer, Property 23: Relationship field completeness
@given(relationship_strategy())
def test_property_23_relationship_field_completeness(relationship):
    """
    **Feature: adversarial-knowledge-cartographer, Property 23: Relationship field completeness**
    **Validates: Requirements 8.3**
    
    For any relationship in the knowledge graph, it should have non-empty values for
    source, relation, target, and citation fields.
    """
    # Verify all required fields are non-empty
    assert relationship.source and relationship.source.strip()
    assert relationship.relation and relationship.relation.strip()
    assert relationship.target and relationship.target.strip()
    assert relationship.citation and relationship.citation.strip()
    
    # Verify credibility is in valid range
    assert 0.0 <= relationship.credibility <= 1.0


# Feature: adversarial-knowledge-cartographer, Property 24: Conflict field completeness
@given(conflict_strategy())
def test_property_24_conflict_field_completeness(conflict):
    """
    **Feature: adversarial-knowledge-cartographer, Property 24: Conflict field completeness**
    **Validates: Requirements 8.4**
    
    For any conflict in the knowledge graph, it should have non-empty values for
    point_of_contention, side_a, side_a_citation, side_b, and side_b_citation fields.
    """
    # Verify all required fields are non-empty
    assert conflict.point_of_contention and conflict.point_of_contention.strip()
    assert conflict.side_a and conflict.side_a.strip()
    assert conflict.side_a_citation and conflict.side_a_citation.strip()
    assert conflict.side_b and conflict.side_b.strip()
    assert conflict.side_b_citation and conflict.side_b_citation.strip()
    
    # Verify credibility scores are in valid range
    assert 0.0 <= conflict.side_a_credibility <= 1.0
    assert 0.0 <= conflict.side_b_credibility <= 1.0


# Feature: adversarial-knowledge-cartographer, Property 27: Referential integrity
@given(knowledge_graph_strategy())
def test_property_27_referential_integrity(kg):
    """
    **Feature: adversarial-knowledge-cartographer, Property 27: Referential integrity**
    **Validates: Requirements 11.5**
    
    For any relationship in the knowledge graph, both the source and target entities
    should exist in the entities list.
    """
    # Verify referential integrity
    entity_set = set(kg.entities)
    
    for rel in kg.relationships:
        assert rel.source in entity_set, f"Relationship source '{rel.source}' not in entities list"
        assert rel.target in entity_set, f"Relationship target '{rel.target}' not in entities list"
    
    # Also test the built-in validation method
    assert kg.validate_referential_integrity() == True


@given(st.lists(non_empty_text_strategy(), min_size=2, max_size=10, unique=True),
       st.lists(non_empty_text_strategy(), min_size=1, max_size=5))
def test_property_27_referential_integrity_violation(entities, invalid_entity_names):
    """
    Test that referential integrity violations are detected.
    
    This test creates relationships that reference entities not in the entities list
    and verifies that validation fails.
    """
    # Filter out any invalid names that happen to be in entities
    invalid_names = [name for name in invalid_entity_names if name not in entities]
    
    if not invalid_names:
        # Skip if we don't have any truly invalid names
        assume(False)
    
    # Create a relationship with an invalid source
    invalid_rel = Relationship(
        source=invalid_names[0],
        relation="test_relation",
        target=entities[0] if entities else "valid_target",
        citation="test_citation",
    )
    
    # Create knowledge graph with invalid relationship
    kg = KnowledgeGraph(
        entities=entities,
        relationships=[invalid_rel],
        conflicts=[],
    )
    
    # Verify that validation detects the issue
    try:
        kg.validate_referential_integrity()
        assert False, "Should have raised ValueError for invalid referential integrity"
    except ValueError as e:
        assert "not in entities list" in str(e)
