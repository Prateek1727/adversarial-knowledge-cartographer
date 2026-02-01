"""
Property-based tests for Scout Agent.

These tests validate universal properties that should hold for source collection,
diversity, and state transitions.
"""

import pytest
from hypothesis import given, strategies as st, assume, settings
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
from agents.scout import ScoutAgent, SearchAPIError
from models.data_models import Source, WorkflowState, KnowledgeGraph


# Helper strategies for generating test data
@st.composite
def source_strategy(draw):
    """Generate a valid Source object."""
    domain = draw(st.text(alphabet="abcdefghijklmnopqrstuvwxyz", min_size=3, max_size=15))
    return Source(
        url=f"https://{domain}.com/article",
        title=draw(st.text(min_size=5, max_size=100)),
        content=draw(st.text(min_size=100, max_size=1000)),
        domain=f"{domain}.com",
        retrieved_at=datetime.now(),
        query_used=draw(st.text(min_size=3, max_size=50))
    )


@st.composite
def search_result_strategy(draw, domain=None):
    """Generate a mock search result."""
    if domain is None:
        domain = draw(st.text(alphabet="abcdefghijklmnopqrstuvwxyz", min_size=3, max_size=15))
    
    return {
        "url": f"https://{domain}.com/article-{draw(st.integers(min_value=1, max_value=1000))}",
        "title": draw(st.text(min_size=10, max_size=100)),
        "content": draw(st.text(min_size=100, max_size=500)),
        "raw_content": draw(st.text(min_size=200, max_size=1000))
    }


# Property 3: Scout phase source diversity
@given(
    st.integers(min_value=10, max_value=20),  # Number of unique domains
    st.text(min_size=5, max_size=50)  # Topic
)
@settings(max_examples=50, deadline=None)
def test_property_3_scout_phase_source_diversity(num_domains: int, topic: str):
    """
    Feature: adversarial-knowledge-cartographer, Property 3: 
    Scout phase source diversity
    
    For any successful Scout execution, the collected sources should include 
    at least 10 sources with unique domain names.
    
    Validates: Requirements 2.2
    """
    assume(any(c.isalnum() for c in topic))
    
    # Create mock search results with unique domains
    mock_results = []
    domains = [f"domain{i}" for i in range(num_domains)]
    
    for i, domain in enumerate(domains):
        mock_results.append({
            "url": f"https://{domain}.com/article",
            "title": f"Article {i} from {domain}",
            "content": f"This is content from {domain}. " * 20,  # Sufficient length
            "raw_content": f"Raw content from {domain}. " * 30
        })
    
    # Create Scout agent
    scout = ScoutAgent(min_sources=10, max_sources_per_query=num_domains)
    
    # Mock the search method to return our controlled results
    with patch.object(scout, 'search', return_value=mock_results):
        # Mock extract_content to return the content from results
        def mock_extract(url, fallback_content=None):
            for result in mock_results:
                if result["url"] == url:
                    return result["content"]
            return fallback_content
        
        with patch.object(scout, 'extract_content', side_effect=mock_extract):
            # Create initial state
            state = WorkflowState(
                topic=topic,
                iteration=0,
                current_phase="scout"
            )
            
            # Execute Scout agent
            updated_state = scout.execute(state)
            
            # Verify source diversity
            collected_domains = {source.domain for source in updated_state.sources}
            
            # Should have at least 10 unique domains
            assert len(collected_domains) >= 10, (
                f"Expected at least 10 unique domains, got {len(collected_domains)}"
            )
            
            # All domains should be unique (no duplicates)
            assert len(collected_domains) == len(updated_state.sources), (
                "Sources should all have unique domains"
            )


# Property 4: Source completeness
@given(
    st.lists(search_result_strategy(), min_size=1, max_size=15),
    st.text(min_size=5, max_size=50)
)
@settings(max_examples=50, deadline=None)
def test_property_4_source_completeness(search_results: list, topic: str):
    """
    Feature: adversarial-knowledge-cartographer, Property 4: 
    Source completeness
    
    For any source collected by the Scout agent, the Source object should have 
    non-empty content, title, and URL fields.
    
    Validates: Requirements 2.3
    """
    assume(any(c.isalnum() for c in topic))
    assume(len(search_results) > 0)
    
    # Create Scout agent
    scout = ScoutAgent(min_sources=5, max_sources_per_query=15)
    
    # Mock the search method
    with patch.object(scout, 'search', return_value=search_results):
        # Mock extract_content to return content from results
        def mock_extract(url, fallback_content=None):
            for result in search_results:
                if result["url"] == url:
                    return result.get("content") or result.get("raw_content") or fallback_content
            return fallback_content
        
        with patch.object(scout, 'extract_content', side_effect=mock_extract):
            # Create initial state
            state = WorkflowState(
                topic=topic,
                iteration=0,
                current_phase="scout"
            )
            
            # Execute Scout agent
            updated_state = scout.execute(state)
            
            # Verify all collected sources have complete fields
            for source in updated_state.sources:
                # URL should be non-empty
                assert source.url, f"Source URL is empty"
                assert source.url.strip(), f"Source URL is whitespace only"
                
                # Title should be non-empty
                assert source.title, f"Source title is empty for {source.url}"
                assert source.title.strip(), f"Source title is whitespace only for {source.url}"
                
                # Content should be non-empty
                assert source.content, f"Source content is empty for {source.url}"
                assert source.content.strip(), f"Source content is whitespace only for {source.url}"
                
                # Domain should be non-empty
                assert source.domain, f"Source domain is empty for {source.url}"
                assert source.domain.strip(), f"Source domain is whitespace only for {source.url}"
                
                # Retrieved_at should be set
                assert source.retrieved_at is not None, f"Source retrieved_at is None for {source.url}"
                assert isinstance(source.retrieved_at, datetime), (
                    f"Source retrieved_at is not a datetime for {source.url}"
                )


# Property 5: Scout to Mapper state transition
@given(
    st.integers(min_value=5, max_value=20),  # Number of sources
    st.text(min_size=5, max_size=50)  # Topic
)
@settings(max_examples=50, deadline=None)
def test_property_5_scout_to_mapper_state_transition(num_sources: int, topic: str):
    """
    Feature: adversarial-knowledge-cartographer, Property 5: 
    Scout to Mapper state transition
    
    For any completed Scout phase, the workflow state should transition to 
    Mapper phase with all collected sources available in the state.
    
    Validates: Requirements 2.5
    """
    assume(any(c.isalnum() for c in topic))
    
    # Create mock search results
    mock_results = []
    for i in range(num_sources):
        mock_results.append({
            "url": f"https://domain{i}.com/article",
            "title": f"Article {i}",
            "content": f"Content for article {i}. " * 20,
            "raw_content": f"Raw content for article {i}. " * 30
        })
    
    # Create Scout agent
    scout = ScoutAgent(min_sources=5, max_sources_per_query=num_sources)
    
    # Mock the search method
    with patch.object(scout, 'search', return_value=mock_results):
        # Mock extract_content
        def mock_extract(url, fallback_content=None):
            for result in mock_results:
                if result["url"] == url:
                    return result["content"]
            return fallback_content
        
        with patch.object(scout, 'extract_content', side_effect=mock_extract):
            # Create initial state (before Scout)
            initial_state = WorkflowState(
                topic=topic,
                iteration=0,
                current_phase="initialized"
            )
            
            initial_source_count = len(initial_state.sources)
            
            # Execute Scout agent
            updated_state = scout.execute(initial_state)
            
            # Verify state transition properties
            # 1. Sources should be added to the state
            assert len(updated_state.sources) > initial_source_count, (
                "Scout should add sources to the state"
            )
            
            # 2. All sources should be accessible in the state
            assert len(updated_state.sources) > 0, (
                "State should contain collected sources"
            )
            
            # 3. Sources should be valid Source objects
            for source in updated_state.sources:
                assert isinstance(source, Source), (
                    f"All items in state.sources should be Source objects, got {type(source)}"
                )
            
            # 4. State should maintain topic
            assert updated_state.topic == topic, (
                "State topic should be preserved through Scout phase"
            )
            
            # 5. Status message should be updated
            assert updated_state.status_message is not None, (
                "Scout should update status message"
            )
            assert "Scout" in updated_state.status_message or "sources" in updated_state.status_message, (
                "Status message should indicate Scout completion"
            )


# Edge case tests
def test_scout_handles_empty_search_results():
    """Test that Scout handles empty search results gracefully."""
    scout = ScoutAgent(min_sources=10)
    
    with patch.object(scout, 'search', return_value=[]):
        state = WorkflowState(
            topic="test topic",
            iteration=0,
            current_phase="scout"
        )
        
        updated_state = scout.execute(state)
        
        # Should not crash, but may have no sources
        assert isinstance(updated_state, WorkflowState)
        assert len(updated_state.sources) == 0


def test_scout_filters_duplicate_domains():
    """Test that Scout filters out duplicate domains."""
    scout = ScoutAgent(min_sources=5)
    
    # Create results with duplicate domains
    mock_results = [
        {"url": "https://example.com/article1", "title": "Article 1", 
         "content": "Content 1 " * 20, "raw_content": "Raw 1 " * 30},
        {"url": "https://example.com/article2", "title": "Article 2", 
         "content": "Content 2 " * 20, "raw_content": "Raw 2 " * 30},
        {"url": "https://other.com/article3", "title": "Article 3", 
         "content": "Content 3 " * 20, "raw_content": "Raw 3 " * 30},
    ]
    
    with patch.object(scout, 'search', return_value=mock_results):
        with patch.object(scout, 'extract_content', side_effect=lambda url, fallback_content=None: fallback_content):
            state = WorkflowState(
                topic="test topic",
                iteration=0,
                current_phase="scout"
            )
            
            updated_state = scout.execute(state)
            
            # Should only have 2 sources (one from example.com, one from other.com)
            domains = {source.domain for source in updated_state.sources}
            assert len(domains) == len(updated_state.sources), (
                "Should not have duplicate domains"
            )


def test_scout_skips_paywalled_content():
    """Test that Scout skips paywalled content."""
    scout = ScoutAgent(min_sources=5)
    
    mock_results = [
        {"url": "https://paywall.com/article", "title": "Paywalled Article",
         "content": "Subscribe to continue reading this article. " * 10,
         "raw_content": "Subscribe to continue " * 20},
        {"url": "https://free.com/article", "title": "Free Article",
         "content": "This is free content. " * 20,
         "raw_content": "Free content " * 30},
    ]
    
    with patch.object(scout, 'search', return_value=mock_results):
        with patch.object(scout, 'extract_content', side_effect=lambda url, fallback_content=None: fallback_content):
            state = WorkflowState(
                topic="test topic",
                iteration=0,
                current_phase="scout"
            )
            
            updated_state = scout.execute(state)
            
            # Should only collect the free article
            assert len(updated_state.sources) == 1
            assert updated_state.sources[0].domain == "free.com"


def test_scout_handles_extraction_failures():
    """Test that Scout handles content extraction failures gracefully."""
    scout = ScoutAgent(min_sources=5)
    
    mock_results = [
        {"url": "https://good.com/article", "title": "Good Article",
         "content": "Good content " * 20, "raw_content": "Raw good " * 30},
        {"url": "https://bad.com/article", "title": "Bad Article",
         "content": "", "raw_content": ""},  # Empty content
    ]
    
    with patch.object(scout, 'search', return_value=mock_results):
        # Mock extract_content to return None for bad.com
        def mock_extract(url, fallback_content=None):
            if "bad.com" in url:
                return None
            return fallback_content
        
        with patch.object(scout, 'extract_content', side_effect=mock_extract):
            state = WorkflowState(
                topic="test topic",
                iteration=0,
                current_phase="scout"
            )
            
            updated_state = scout.execute(state)
            
            # Should only collect the good article
            assert len(updated_state.sources) == 1
            assert updated_state.sources[0].domain == "good.com"


def test_scout_uses_adversarial_queries_in_later_iterations():
    """Test that Scout uses adversarial queries in iterations > 0."""
    scout = ScoutAgent(min_sources=5)
    
    mock_results = [
        {"url": "https://example.com/article", "title": "Article",
         "content": "Content " * 20, "raw_content": "Raw " * 30},
    ]
    
    with patch.object(scout, 'search', return_value=mock_results) as mock_search:
        with patch.object(scout, 'extract_content', side_effect=lambda url, fallback_content=None: fallback_content):
            state = WorkflowState(
                topic="original topic",
                iteration=1,  # Not first iteration
                current_phase="scout",
                adversarial_queries=["adversarial query 1", "adversarial query 2"]
            )
            
            updated_state = scout.execute(state)
            
            # Verify that search was called with adversarial queries
            assert mock_search.called
            # At least one call should use an adversarial query
            call_args = [call[0][0] for call in mock_search.call_args_list]
            assert any(q in state.adversarial_queries for q in call_args), (
                "Scout should use adversarial queries in later iterations"
            )
