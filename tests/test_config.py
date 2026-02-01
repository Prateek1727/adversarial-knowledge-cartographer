"""Unit tests for configuration management."""

import pytest
from config import Config


class TestConfig:
    """Test suite for Config class."""
    
    def test_config_defaults(self):
        """Test that Config has sensible defaults."""
        config = Config()
        assert config.llm_provider == "openai"
        assert config.llm_model == "gpt-4"
        assert config.llm_temperature == 0.1
        assert config.search_provider == "tavily"
        assert config.max_iterations == 3
        assert config.min_sources == 10
        assert config.domain_weight == 0.4
        assert config.citation_weight == 0.3
        assert config.recency_weight == 0.3
    
    def test_llm_provider_validation(self):
        """Test that invalid LLM provider raises error."""
        with pytest.raises(ValueError, match="llm_provider must be"):
            Config(llm_provider="invalid")
    
    def test_search_provider_validation(self):
        """Test that invalid search provider raises error."""
        with pytest.raises(ValueError, match="search_provider must be"):
            Config(search_provider="invalid")
    
    def test_max_iterations_validation(self):
        """Test that max_iterations must be positive."""
        with pytest.raises(ValueError, match="max_iterations must be at least 1"):
            Config(max_iterations=0)
    
    def test_min_sources_validation(self):
        """Test that min_sources must be positive."""
        with pytest.raises(ValueError, match="min_sources must be at least 1"):
            Config(min_sources=0)
    
    def test_validate_api_keys_openai(self):
        """Test that OpenAI API key validation works."""
        config = Config(llm_provider="openai", openai_api_key=None)
        with pytest.raises(ValueError, match="OPENAI_API_KEY"):
            config.validate_api_keys()
    
    def test_validate_api_keys_anthropic(self):
        """Test that Anthropic API key validation works."""
        config = Config(llm_provider="anthropic", anthropic_api_key=None)
        with pytest.raises(ValueError, match="ANTHROPIC_API_KEY"):
            config.validate_api_keys()
    
    def test_validate_api_keys_tavily(self):
        """Test that Tavily API key validation works."""
        config = Config(
            llm_provider="openai",
            openai_api_key="test",
            search_provider="tavily",
            tavily_api_key=None
        )
        with pytest.raises(ValueError, match="TAVILY_API_KEY"):
            config.validate_api_keys()
    
    def test_validate_api_keys_serper(self):
        """Test that Serper API key validation works."""
        config = Config(
            llm_provider="openai",
            openai_api_key="test",
            search_provider="serper",
            serper_api_key=None
        )
        with pytest.raises(ValueError, match="SERPER_API_KEY"):
            config.validate_api_keys()
    
    def test_validate_api_keys_success(self):
        """Test that validation passes with all required keys."""
        config = Config(
            llm_provider="openai",
            openai_api_key="test_key",
            search_provider="tavily",
            tavily_api_key="test_key"
        )
        # Should not raise
        config.validate_api_keys()
