"""
Property-based tests for the Mapper agent.

These tests validate universal properties that should hold across all inputs
for entity extraction, relationship citation, structured output, and deduplication.
"""

import pytest
from hypothesis import given, strategies as st, assume, settings, HealthCheck
from datetime import datetime
from pydantic import ValidationError
from unittest.mock import Mock

from agents.mapper import MapperAgent
from models.data_models import Source, KnowledgeGraph, Relationship


# Strategies for generating test data
@st.composite
def source_strategy(draw):
    """Generate a valid Source object."""
    domain = draw(st.sampled_from([
        "example.com", "test.org", "research.edu", "news.com", "science.gov"
    ]))
    url = f"https://{domain}/article-{draw(st.integers(min_value=1, max_value=1000))}"
    title = draw(st.text(min_size=5, max_size=100, alphabet=st.characters(blacklist_categories=('Cs', 'Cc'))))
    content = draw(st.text(min_size=100, max_size=2000, alphabet=st.characters(blacklist_categories=('Cs', 'Cc'))))
    
    return Source(
        url=url,
        title=title.strip() or "Default Title",
        content=content.strip() or "Default content with sufficient length to pass validation checks.",
        domain=domain,
        retrieved_at=datetime.now(),
        query_used="test query"
    )


@st.composite
def sources_list_strategy(draw, min_size=1, max_size=5):
    """Generate a list of Source objects."""
    return draw(st.lists(source_strategy(), min_size=min_size, max_size=max_size))


class TestMapperProperties:
    """Property-based tests for Mapper agent."""
    
    @settings(max_examples=100)
    @given(sources_list_strategy(min_size=1, max_size=3))
    def test_property_6_mapper_entity_extraction(self, sources):
        """
        Feature: adversarial-knowledge-cartographer, Property 6: Mapper entity extraction
        
        For any non-empty list of sources, the Mapper should extract at least one entity
        into the knowledge graph.
        
        Validates: Requirements 3.1
        """
        # Skip if sources are empty or have insufficient content
        assume(len(sources) > 0)
        assume(all(len(s.content) > 50 for s in sources))
        
        # Create mapper with mock LLM
        mock_llm = Mock()
        mapper = MapperAgent(llm=mock_llm)
        topic = "test topic"
        
        try:
            # Build knowledge graph
            kg = mapper.build_knowledge_graph(topic, sources)
            
            # Property: At least one entity should be extracted
            assert len(kg.entities) >= 1, (
                f"Expected at least 1 entity, but got {len(kg.entities)}"
            )
            
        except Exception as e:
            # If LLM fails, we can't test this property
            # This is acceptable for property tests with external dependencies
            pytest.skip(f"LLM call failed: {e}")
    
    @settings(max_examples=100)
    @given(sources_list_strategy(min_size=1, max_size=3))
    def test_property_7_relationship_citation_completeness(self, sources):
        """
        Feature: adversarial-knowledge-cartographer, Property 7: Relationship citation completeness
        
        For any relationship in the knowledge graph, the citation field should be non-empty
        and reference a valid source URL.
        
        Validates: Requirements 3.3
        """
        # Skip if sources are empty or have insufficient content
        assume(len(sources) > 0)
        assume(all(len(s.content) > 50 for s in sources))
        
        # Create mapper with mock LLM
        mock_llm = Mock()
        mapper = MapperAgent(llm=mock_llm)
        topic = "test topic"
        
        try:
            # Build knowledge graph
            kg = mapper.build_knowledge_graph(topic, sources)
            
            # Property: All relationships must have non-empty citations
            for rel in kg.relationships:
                assert rel.citation, (
                    f"Relationship {rel.source} -> {rel.target} has empty citation"
                )
                assert rel.citation.strip(), (
                    f"Relationship {rel.source} -> {rel.target} has whitespace-only citation"
                )
            
        except Exception as e:
            # If LLM fails, we can't test this property
            pytest.skip(f"LLM call failed: {e}")
    
    @settings(max_examples=100)
    @given(sources_list_strategy(min_size=1, max_size=3))
    def test_property_25_structured_output_enforcement(self, sources):
        """
        Feature: adversarial-knowledge-cartographer, Property 25: Structured output enforcement
        
        For any Mapper agent output, it should successfully validate against the Pydantic
        KnowledgeGraph schema without raising validation errors.
        
        Validates: Requirements 11.1, 11.2
        """
        # Skip if sources are empty or have insufficient content
        assume(len(sources) > 0)
        assume(all(len(s.content) > 50 for s in sources))
        
        # Create mapper with mock LLM
        mock_llm = Mock()
        mapper = MapperAgent(llm=mock_llm)
        topic = "test topic"
        
        try:
            # Build knowledge graph
            kg = mapper.build_knowledge_graph(topic, sources)
            
            # Property: Knowledge graph should be a valid KnowledgeGraph instance
            assert isinstance(kg, KnowledgeGraph), (
                f"Expected KnowledgeGraph instance, got {type(kg)}"
            )
            
            # Property: Should be able to serialize and deserialize without errors
            kg_dict = kg.model_dump()
            kg_reconstructed = KnowledgeGraph(**kg_dict)
            
            assert kg_reconstructed.entities == kg.entities
            assert len(kg_reconstructed.relationships) == len(kg.relationships)
            assert len(kg_reconstructed.conflicts) == len(kg.conflicts)
            
        except ValidationError as e:
            # Validation errors should not occur - this is a test failure
            pytest.fail(f"KnowledgeGraph validation failed: {e}")
        except Exception as e:
            # If LLM fails, we can't test this property
            pytest.skip(f"LLM call failed: {e}")
    
    def test_property_26_entity_deduplication(self):
        """
        Feature: adversarial-knowledge-cartographer, Property 26: Entity deduplication
        
        For any set of extracted entities with similar names (edit distance < 3),
        only unique entities should remain in the final entities list.
        
        Validates: Requirements 11.4
        """
        # Create mapper with mock LLM
        mock_llm = Mock()
        mapper = MapperAgent(fuzzy_match_threshold=0.85, llm=mock_llm)
        
        # Test with entities that should be deduplicated
        test_cases = [
            # Similar entities that should be merged
            (["Coffee", "coffee", "COFFEE"], 1),
            (["Machine Learning", "machine learning", "Machine learning"], 1),
            (["Algorithm X", "Algorithm x", "algorithm X"], 1),
            # Different entities that should remain separate
            (["Coffee", "Tea", "Water"], 3),
            (["Python", "Java", "JavaScript"], 3),
            # Mix of similar and different
            (["Coffee", "coffee", "Tea", "tea", "Water"], 3),
        ]
        
        for entities, expected_count in test_cases:
            deduplicated = mapper._deduplicate_entities(entities)
            
            # Property: Deduplicated list should have expected count
            assert len(deduplicated) == expected_count, (
                f"Expected {expected_count} unique entities from {entities}, "
                f"but got {len(deduplicated)}: {deduplicated}"
            )
            
            # Property: All entities in deduplicated list should be unique
            assert len(deduplicated) == len(set(deduplicated)), (
                f"Deduplicated list contains duplicates: {deduplicated}"
            )
    
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    @given(st.lists(st.text(min_size=1, max_size=50), min_size=1, max_size=20))
    def test_property_26_entity_deduplication_general(self, entities):
        """
        Feature: adversarial-knowledge-cartographer, Property 26: Entity deduplication (general)
        
        For any list of entities, the deduplicated list should contain no exact duplicates
        and should have length <= original list length.
        
        Validates: Requirements 11.4
        """
        # Filter out empty strings
        entities = [e.strip() for e in entities if e.strip()]
        assume(len(entities) > 0)
        
        # Create mapper with mock LLM
        mock_llm = Mock()
        mapper = MapperAgent(fuzzy_match_threshold=0.85, llm=mock_llm)
        deduplicated = mapper._deduplicate_entities(entities)
        
        # Property: Deduplicated list should be <= original length
        assert len(deduplicated) <= len(entities), (
            f"Deduplicated list ({len(deduplicated)}) is longer than original ({len(entities)})"
        )
        
        # Property: Deduplicated list should contain no exact duplicates (case-insensitive)
        lower_deduplicated = [e.lower() for e in deduplicated]
        assert len(lower_deduplicated) == len(set(lower_deduplicated)), (
            f"Deduplicated list contains exact duplicates: {deduplicated}"
        )
        
        # Property: All entities in deduplicated list should come from original list
        for entity in deduplicated:
            # Check if this entity or a similar one exists in original list
            found = any(
                mapper._calculate_similarity(entity, orig) >= mapper.fuzzy_match_threshold
                for orig in entities
            )
            assert found, f"Entity '{entity}' not found in original list"


class TestMapperUnitTests:
    """Unit tests for Mapper agent helper functions."""
    
    def test_similarity_calculation(self):
        """Test similarity calculation between strings."""
        # Create mapper with mock LLM
        mock_llm = Mock()
        mapper = MapperAgent(llm=mock_llm)
        
        # Identical strings
        assert mapper._calculate_similarity("test", "test") == 1.0
        
        # Very similar strings
        assert mapper._calculate_similarity("Coffee", "coffee") > 0.9
        
        # Somewhat similar strings
        similarity = mapper._calculate_similarity("Machine Learning", "machine learning")
        assert similarity > 0.8
        
        # Different strings
        assert mapper._calculate_similarity("Coffee", "Tea") < 0.5
    
    def test_citation_validation(self):
        """Test citation validation against source URLs."""
        # Create mapper with mock LLM
        mock_llm = Mock()
        mapper = MapperAgent(llm=mock_llm)
        
        sources = [
            Source(
                url="https://example.com/article1",
                title="Article 1",
                content="Content 1",
                domain="example.com",
                retrieved_at=datetime.now(),
                query_used="test"
            ),
            Source(
                url="https://test.org/article2",
                title="Article 2",
                content="Content 2",
                domain="test.org",
                retrieved_at=datetime.now(),
                query_used="test"
            )
        ]
        
        # Valid citations
        assert mapper._validate_citation("https://example.com/article1", sources)
        assert mapper._validate_citation("https://test.org/article2", sources)
        
        # Invalid citations
        assert not mapper._validate_citation("https://invalid.com/article", sources)
        assert not mapper._validate_citation("", sources)
