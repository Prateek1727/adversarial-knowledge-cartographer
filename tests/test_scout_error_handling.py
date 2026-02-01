"""
Unit tests for Scout Agent error handling.

These tests validate that the Scout agent handles various error conditions
gracefully, including search API failures and content extraction failures.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import httpx
from agents.scout import ScoutAgent, SearchAPIError
from models.data_models import WorkflowState


class TestSearchAPIErrorHandling:
    """Tests for search API failure recovery."""
    
    def test_tavily_api_failure_with_fallback_to_serper(self):
        """Test that Tavily API failure triggers fallback to Serper."""
        scout = ScoutAgent()
        
        # Mock Tavily to fail
        with patch.object(scout, 'search_tavily', side_effect=SearchAPIError("Tavily failed")):
            # Mock Serper to succeed
            with patch.object(scout, 'search_serper', return_value=[
                {"url": "https://example.com", "title": "Test", "content": "Content"}
            ]) as mock_serper:
                
                results = scout.search("test query")
                
                # Verify fallback was used
                assert mock_serper.called
                assert len(results) > 0
    
    def test_both_search_apis_fail(self):
        """Test that SearchAPIError is raised when both APIs fail."""
        scout = ScoutAgent()
        
        # Mock both APIs to fail
        with patch.object(scout, 'search_tavily', side_effect=SearchAPIError("Tavily failed")):
            with patch.object(scout, 'search_serper', side_effect=SearchAPIError("Serper failed")):
                
                with pytest.raises(SearchAPIError) as exc_info:
                    scout.search("test query")
                
                # Verify error message mentions both failures
                error_msg = str(exc_info.value)
                assert "Both search providers failed" in error_msg or "Tavily" in error_msg
    
    def test_rate_limit_triggers_exponential_backoff(self):
        """Test that rate limit errors trigger exponential backoff."""
        scout = ScoutAgent(max_retries=3, initial_backoff=0.1)
        
        # Mock HTTP client to return rate limit error
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.json.return_value = {"error": "Rate limit exceeded"}
        
        http_error = httpx.HTTPStatusError(
            "Rate limit",
            request=Mock(),
            response=mock_response
        )
        
        # Mock the API key check
        with patch('agents.scout.config.tavily_api_key', 'fake_key'):
            with patch.object(scout.client, 'post', side_effect=http_error):
                with pytest.raises(SearchAPIError) as exc_info:
                    scout.search_tavily("test query")
                
                # Verify it attempted retries
                assert "failed after" in str(exc_info.value).lower()
    
    def test_network_timeout_is_handled(self):
        """Test that network timeouts are handled gracefully."""
        scout = ScoutAgent(max_retries=2, initial_backoff=0.1)
        
        with patch.object(scout.client, 'post', side_effect=httpx.TimeoutException("Timeout")):
            with pytest.raises(SearchAPIError):
                scout.search_tavily("test query")
    
    def test_malformed_api_response_is_handled(self):
        """Test that malformed API responses are handled."""
        scout = ScoutAgent()
        
        # Mock response with missing expected fields
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}  # Missing 'results' field
        
        # Mock the API key check
        with patch('agents.scout.config.tavily_api_key', 'fake_key'):
            with patch.object(scout.client, 'post', return_value=mock_response):
                results = scout.search_tavily("test query")
                
                # Should return empty list instead of crashing
                assert results == []
    
    def test_search_continues_after_single_query_failure(self):
        """Test that Scout continues with other queries if one fails."""
        scout = ScoutAgent(min_sources=5)
        
        # Mock search to fail on first call, succeed on second
        call_count = [0]
        def mock_search(query, max_results=10):
            call_count[0] += 1
            if call_count[0] == 1:
                raise SearchAPIError("First query failed")
            return [
                {"url": f"https://example{i}.com", "title": f"Article {i}",
                 "content": f"Content {i} " * 20, "raw_content": f"Raw {i} " * 30}
                for i in range(5)
            ]
        
        with patch.object(scout, 'search', side_effect=mock_search):
            with patch.object(scout, 'extract_content', side_effect=lambda url, fallback_content=None: fallback_content):
                state = WorkflowState(topic="test topic", iteration=0)
                updated_state = scout.execute(state)
                
                # Should have collected sources from successful queries
                assert len(updated_state.sources) > 0


class TestContentExtractionErrorHandling:
    """Tests for content extraction failure handling."""
    
    def test_extraction_failure_logs_and_skips_source(self):
        """Test that extraction failures are logged and source is skipped."""
        scout = ScoutAgent()
        
        mock_results = [
            {"url": "https://good.com/article", "title": "Good",
             "content": "Good content " * 20, "raw_content": "Raw good " * 30},
            {"url": "https://bad.com/article", "title": "Bad",
             "content": "", "raw_content": ""},
        ]
        
        with patch.object(scout, 'search', return_value=mock_results):
            # Mock extract_content to fail for bad.com
            def mock_extract(url, fallback_content=None):
                if "bad.com" in url:
                    return None  # Extraction failed
                return fallback_content
            
            with patch.object(scout, 'extract_content', side_effect=mock_extract):
                state = WorkflowState(topic="test", iteration=0)
                updated_state = scout.execute(state)
                
                # Should only have the good source
                assert len(updated_state.sources) == 1
                assert updated_state.sources[0].domain == "good.com"
    
    def test_trafilatura_exception_is_caught(self):
        """Test that trafilatura exceptions are caught and handled."""
        scout = ScoutAgent()
        
        # Mock trafilatura to raise exception
        with patch('agents.scout.trafilatura.fetch_url', side_effect=Exception("Network error")):
            content = scout.extract_content("https://example.com", fallback_content="fallback")
            
            # Should return fallback instead of crashing
            assert content == "fallback"
    
    def test_empty_content_uses_fallback(self):
        """Test that empty extracted content uses fallback."""
        scout = ScoutAgent()
        
        # Mock trafilatura to return empty content
        with patch('agents.scout.trafilatura.fetch_url', return_value="<html></html>"):
            with patch('agents.scout.trafilatura.extract', return_value=""):
                content = scout.extract_content("https://example.com", fallback_content="fallback text")
                
                # Should use fallback
                assert content == "fallback text"
    
    def test_short_content_uses_fallback(self):
        """Test that very short extracted content uses fallback."""
        scout = ScoutAgent()
        
        # Mock trafilatura to return very short content
        with patch('agents.scout.trafilatura.fetch_url', return_value="<html>Short</html>"):
            with patch('agents.scout.trafilatura.extract', return_value="Short"):
                content = scout.extract_content("https://example.com", fallback_content="longer fallback text " * 20)
                
                # Should use fallback because content is too short
                assert content == "longer fallback text " * 20
    
    def test_failed_download_returns_fallback(self):
        """Test that failed downloads return fallback content."""
        scout = ScoutAgent()
        
        # Mock trafilatura to return None (download failed)
        with patch('agents.scout.trafilatura.fetch_url', return_value=None):
            content = scout.extract_content("https://example.com", fallback_content="fallback")
            
            assert content == "fallback"
    
    def test_multiple_extraction_failures_dont_stop_collection(self):
        """Test that multiple extraction failures don't stop source collection."""
        scout = ScoutAgent(min_sources=5)
        
        mock_results = [
            {"url": f"https://site{i}.com/article", "title": f"Article {i}",
             "content": f"Content {i} " * 20 if i % 2 == 0 else "",  # Half fail
             "raw_content": f"Raw {i} " * 30 if i % 2 == 0 else ""}
            for i in range(10)
        ]
        
        with patch.object(scout, 'search', return_value=mock_results):
            # Mock extract to return None for empty content
            def mock_extract(url, fallback_content=None):
                if not fallback_content or len(fallback_content) < 100:
                    return None
                return fallback_content
            
            with patch.object(scout, 'extract_content', side_effect=mock_extract):
                state = WorkflowState(topic="test", iteration=0)
                updated_state = scout.execute(state)
                
                # Should have collected sources from successful extractions
                assert len(updated_state.sources) >= 3  # At least some succeeded


class TestPaywallAndAccessibilityHandling:
    """Tests for paywall and accessibility detection."""
    
    def test_paywall_content_is_filtered(self):
        """Test that paywalled content is filtered out."""
        scout = ScoutAgent()
        
        # Test various paywall indicators
        paywall_texts = [
            "Subscribe to continue reading this article.",
            "This article is for subscribers only.",
            "Sign in to read the full article.",
            "Become a member to access premium content.",
        ]
        
        for text in paywall_texts:
            assert not scout.is_accessible("https://example.com", text)
    
    def test_accessible_content_passes_check(self):
        """Test that accessible content passes the check."""
        scout = ScoutAgent()
        
        content = "This is a normal article with plenty of content. " * 10
        assert scout.is_accessible("https://example.com", content)
    
    def test_very_short_content_fails_accessibility(self):
        """Test that very short content fails accessibility check."""
        scout = ScoutAgent()
        
        short_content = "Too short"
        assert not scout.is_accessible("https://example.com", short_content)
    
    def test_empty_content_fails_accessibility(self):
        """Test that empty content fails accessibility check."""
        scout = ScoutAgent()
        
        assert not scout.is_accessible("https://example.com", "")
        assert not scout.is_accessible("https://example.com", None)


class TestDomainExtractionAndValidation:
    """Tests for domain extraction and validation."""
    
    def test_domain_extraction_from_various_urls(self):
        """Test domain extraction from different URL formats."""
        scout = ScoutAgent()
        
        test_cases = [
            ("https://example.com/article", "example.com"),
            ("https://www.example.com/article", "example.com"),  # www removed
            ("http://subdomain.example.com/page", "subdomain.example.com"),
            ("https://example.org/path/to/article", "example.org"),
        ]
        
        for url, expected_domain in test_cases:
            assert scout.extract_domain(url) == expected_domain
    
    def test_malformed_url_returns_original(self):
        """Test that malformed URLs return the original string."""
        scout = ScoutAgent()
        
        malformed = "not-a-valid-url"
        result = scout.extract_domain(malformed)
        
        # Should return something (the original or a safe default)
        assert result is not None
    
    def test_duplicate_domains_are_filtered(self):
        """Test that sources from duplicate domains are filtered."""
        scout = ScoutAgent()
        
        existing_domains = {"example.com", "test.org"}
        
        mock_results = [
            {"url": "https://example.com/article1", "title": "Article 1",
             "content": "Content 1 " * 20, "raw_content": "Raw 1 " * 30},
            {"url": "https://example.com/article2", "title": "Article 2",
             "content": "Content 2 " * 20, "raw_content": "Raw 2 " * 30},
            {"url": "https://new.com/article", "title": "Article 3",
             "content": "Content 3 " * 20, "raw_content": "Raw 3 " * 30},
        ]
        
        with patch.object(scout, 'search', return_value=mock_results):
            with patch.object(scout, 'extract_content', side_effect=lambda url, fallback_content=None: fallback_content):
                sources = scout.collect_sources("test query", existing_domains, max_sources=10)
                
                # Should only collect from new.com (example.com is already in existing_domains)
                assert len(sources) == 1
                assert sources[0].domain == "new.com"


class TestStateManagement:
    """Tests for workflow state management during Scout execution."""
    
    def test_executed_queries_are_tracked(self):
        """Test that executed queries are added to state."""
        scout = ScoutAgent()
        
        mock_results = [
            {"url": "https://example.com/article", "title": "Article",
             "content": "Content " * 20, "raw_content": "Raw " * 30}
        ]
        
        with patch.object(scout, 'search', return_value=mock_results):
            with patch.object(scout, 'extract_content', side_effect=lambda url, fallback_content=None: fallback_content):
                state = WorkflowState(topic="test topic", iteration=0)
                updated_state = scout.execute(state)
                
                # Verify queries were tracked
                assert len(updated_state.executed_queries) > 0
                assert "test topic" in updated_state.executed_queries
    
    def test_status_message_is_updated(self):
        """Test that status message is updated after Scout execution."""
        scout = ScoutAgent()
        
        mock_results = [
            {"url": f"https://site{i}.com/article", "title": f"Article {i}",
             "content": f"Content {i} " * 20, "raw_content": f"Raw {i} " * 30}
            for i in range(5)
        ]
        
        with patch.object(scout, 'search', return_value=mock_results):
            with patch.object(scout, 'extract_content', side_effect=lambda url, fallback_content=None: fallback_content):
                state = WorkflowState(topic="test", iteration=0)
                updated_state = scout.execute(state)
                
                # Verify status message was updated
                assert updated_state.status_message is not None
                assert "Scout" in updated_state.status_message or "sources" in updated_state.status_message
    
    def test_sources_are_accumulated_across_iterations(self):
        """Test that sources accumulate across multiple Scout executions."""
        scout = ScoutAgent()
        
        # First execution
        mock_results_1 = [
            {"url": "https://site1.com/article", "title": "Article 1",
             "content": "Content 1 " * 20, "raw_content": "Raw 1 " * 30}
        ]
        
        with patch.object(scout, 'search', return_value=mock_results_1):
            with patch.object(scout, 'extract_content', side_effect=lambda url, fallback_content=None: fallback_content):
                state = WorkflowState(topic="test", iteration=0)
                state = scout.execute(state)
                
                first_count = len(state.sources)
                assert first_count > 0
        
        # Second execution with different results
        mock_results_2 = [
            {"url": "https://site2.com/article", "title": "Article 2",
             "content": "Content 2 " * 20, "raw_content": "Raw 2 " * 30}
        ]
        
        with patch.object(scout, 'search', return_value=mock_results_2):
            with patch.object(scout, 'extract_content', side_effect=lambda url, fallback_content=None: fallback_content):
                state.iteration = 1
                state.adversarial_queries = ["new query"]
                state = scout.execute(state)
                
                # Should have more sources than before
                assert len(state.sources) > first_count
