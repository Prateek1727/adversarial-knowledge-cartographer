"""
Unit tests for Adversary Agent bias detection.

These tests validate the bias detection functionality with known bias patterns.
"""

import pytest
from datetime import datetime

from agents.adversary import AdversaryAgent
from models.data_models import Source


# Mock LLM for testing (bias detection doesn't use LLM)
class MockLLM:
    """Mock LLM that returns predefined responses."""
    
    def invoke(self, messages):
        """Return mock response."""
        class MockResponse:
            content = '{"counter_queries": ["query1", "query2", "query3"]}'
        return MockResponse()


class TestBiasDetection:
    """Unit tests for bias detection in sources."""
    
    def test_bias_detection_with_opinion_keyword(self):
        """Test bias detection with 'opinion' keyword in title."""
        agent = AdversaryAgent(llm=MockLLM())
        
        sources = [
            Source(
                url="https://example.com/article",
                title="Opinion: Why X is the best",
                content="This is an opinion piece about X." * 20,
                domain="example.com",
                retrieved_at=datetime.now(),
                query_used="test query"
            )
        ]
        
        weaknesses = agent.identify_bias_indicators(sources)
        
        assert len(weaknesses) == 1
        assert weaknesses[0].type == "potential_bias"
        assert "opinion" in weaknesses[0].description.lower()
    
    def test_bias_detection_with_editorial_keyword(self):
        """Test bias detection with 'editorial' keyword in URL."""
        agent = AdversaryAgent(llm=MockLLM())
        
        sources = [
            Source(
                url="https://example.com/editorial/article",
                title="Important Article",
                content="This is an editorial piece." * 20,
                domain="example.com",
                retrieved_at=datetime.now(),
                query_used="test query"
            )
        ]
        
        weaknesses = agent.identify_bias_indicators(sources)
        
        assert len(weaknesses) == 1
        assert weaknesses[0].type == "potential_bias"
        assert "editorial" in weaknesses[0].description.lower()
    
    def test_bias_detection_with_blog_domain(self):
        """Test bias detection with blog domain pattern."""
        agent = AdversaryAgent(llm=MockLLM())
        
        sources = [
            Source(
                url="https://myblog.wordpress.com/article",
                title="My Thoughts on X",
                content="This is a blog post about X." * 20,
                domain="myblog.wordpress.com",
                retrieved_at=datetime.now(),
                query_used="test query"
            )
        ]
        
        weaknesses = agent.identify_bias_indicators(sources)
        
        assert len(weaknesses) == 1
        assert weaknesses[0].type == "potential_bias"
        assert "wordpress.com" in weaknesses[0].description.lower()
    
    def test_bias_detection_with_sponsored_content(self):
        """Test bias detection with 'sponsored' keyword."""
        agent = AdversaryAgent(llm=MockLLM())
        
        sources = [
            Source(
                url="https://example.com/sponsored-content",
                title="Sponsored: Amazing Product Review",
                content="This is sponsored content." * 20,
                domain="example.com",
                retrieved_at=datetime.now(),
                query_used="test query"
            )
        ]
        
        weaknesses = agent.identify_bias_indicators(sources)
        
        assert len(weaknesses) == 1
        assert weaknesses[0].type == "potential_bias"
        assert "sponsored" in weaknesses[0].description.lower()
    
    def test_bias_detection_with_multiple_indicators(self):
        """Test bias detection with multiple bias indicators."""
        agent = AdversaryAgent(llm=MockLLM())
        
        sources = [
            Source(
                url="https://myblog.medium.com/opinion-piece",
                title="Opinion: My Editorial View",
                content="This is an opinion editorial." * 20,
                domain="myblog.medium.com",
                retrieved_at=datetime.now(),
                query_used="test query"
            )
        ]
        
        weaknesses = agent.identify_bias_indicators(sources)
        
        assert len(weaknesses) == 1
        assert weaknesses[0].type == "potential_bias"
        # Should detect multiple indicators
        description_lower = weaknesses[0].description.lower()
        assert "opinion" in description_lower or "medium.com" in description_lower
    
    def test_no_bias_detection_for_neutral_sources(self):
        """Test that neutral sources are not flagged for bias."""
        agent = AdversaryAgent(llm=MockLLM())
        
        sources = [
            Source(
                url="https://example.edu/research/article",
                title="Research Study on X",
                content="This is a research article about X." * 20,
                domain="example.edu",
                retrieved_at=datetime.now(),
                query_used="test query"
            ),
            Source(
                url="https://news.example.com/article",
                title="News Report on Y",
                content="This is a news report about Y." * 20,
                domain="news.example.com",
                retrieved_at=datetime.now(),
                query_used="test query"
            )
        ]
        
        weaknesses = agent.identify_bias_indicators(sources)
        
        assert len(weaknesses) == 0
    
    def test_bias_detection_with_mixed_sources(self):
        """Test bias detection with mix of biased and neutral sources."""
        agent = AdversaryAgent(llm=MockLLM())
        
        sources = [
            Source(
                url="https://example.edu/research",
                title="Research Study",
                content="Research content." * 20,
                domain="example.edu",
                retrieved_at=datetime.now(),
                query_used="test query"
            ),
            Source(
                url="https://blog.example.com/opinion",
                title="Opinion: My View",
                content="Opinion content." * 20,
                domain="blog.example.com",
                retrieved_at=datetime.now(),
                query_used="test query"
            ),
            Source(
                url="https://news.example.com/article",
                title="News Article",
                content="News content." * 20,
                domain="news.example.com",
                retrieved_at=datetime.now(),
                query_used="test query"
            )
        ]
        
        weaknesses = agent.identify_bias_indicators(sources)
        
        # Should only flag the biased source
        assert len(weaknesses) == 1
        assert weaknesses[0].type == "potential_bias"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
