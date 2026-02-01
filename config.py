"""Configuration management for the Adversarial Knowledge Cartographer.

This module handles loading and validating configuration from environment variables.
"""

import os
from typing import Optional
from pydantic import BaseModel, Field, field_validator
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config(BaseModel):
    """Application configuration loaded from environment variables."""
    
    # LLM Configuration
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API key")
    anthropic_api_key: Optional[str] = Field(default=None, description="Anthropic API key")
    groq_api_key: Optional[str] = Field(default=None, description="Groq API key")
    llm_provider: str = Field(default="openai", description="LLM provider to use (openai, anthropic, or groq)")
    llm_model: str = Field(default="gpt-4", description="LLM model name")
    llm_temperature: float = Field(default=0.1, description="LLM temperature for generation")
    
    # Search API Configuration
    tavily_api_key: Optional[str] = Field(default=None, description="Tavily API key")
    serper_api_key: Optional[str] = Field(default=None, description="Serper API key")
    search_provider: str = Field(default="tavily", description="Search provider to use (tavily or serper)")
    
    # Workflow Configuration
    max_iterations: int = Field(default=3, description="Maximum number of adversarial iterations")
    min_sources: int = Field(default=10, description="Minimum number of sources to collect")
    max_sources_per_query: int = Field(default=10, description="Maximum sources per search query")
    
    # Credibility Scoring Configuration
    domain_weight: float = Field(default=0.4, description="Weight for domain authority in credibility score")
    citation_weight: float = Field(default=0.3, description="Weight for citation indicators in credibility score")
    recency_weight: float = Field(default=0.3, description="Weight for recency in credibility score")
    
    # API Configuration
    api_host: str = Field(default="0.0.0.0", description="API server host")
    api_port: int = Field(default=8000, description="API server port")
    
    # Logging Configuration
    log_level: str = Field(default="INFO", description="Logging level")
    
    @field_validator("llm_provider")
    @classmethod
    def validate_llm_provider(cls, v: str) -> str:
        """Validate LLM provider is supported."""
        if v not in ["openai", "anthropic", "groq"]:
            raise ValueError("llm_provider must be 'openai', 'anthropic', or 'groq'")
        return v
    
    @field_validator("search_provider")
    @classmethod
    def validate_search_provider(cls, v: str) -> str:
        """Validate search provider is supported."""
        if v not in ["tavily", "serper"]:
            raise ValueError("search_provider must be 'tavily' or 'serper'")
        return v
    
    @field_validator("max_iterations")
    @classmethod
    def validate_max_iterations(cls, v: int) -> int:
        """Validate max iterations is positive."""
        if v < 1:
            raise ValueError("max_iterations must be at least 1")
        return v
    
    @field_validator("min_sources")
    @classmethod
    def validate_min_sources(cls, v: int) -> int:
        """Validate min sources is positive."""
        if v < 1:
            raise ValueError("min_sources must be at least 1")
        return v
    
    def validate_api_keys(self) -> None:
        """Validate that required API keys are present."""
        # Check LLM API key
        if self.llm_provider == "openai" and not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required when using OpenAI")
        if self.llm_provider == "anthropic" and not self.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is required when using Anthropic")
        if self.llm_provider == "groq" and not self.groq_api_key:
            raise ValueError("GROQ_API_KEY environment variable is required when using Groq")
        
        # Check search API key
        if self.search_provider == "tavily" and not self.tavily_api_key:
            raise ValueError("TAVILY_API_KEY environment variable is required when using Tavily")
        if self.search_provider == "serper" and not self.serper_api_key:
            raise ValueError("SERPER_API_KEY environment variable is required when using Serper")
    
    @classmethod
    def from_env(cls) -> "Config":
        """Load configuration from environment variables."""
        return cls(
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
            groq_api_key=os.getenv("GROQ_API_KEY"),
            llm_provider=os.getenv("LLM_PROVIDER", "openai"),
            llm_model=os.getenv("LLM_MODEL", "gpt-4"),
            llm_temperature=float(os.getenv("LLM_TEMPERATURE", "0.1")),
            tavily_api_key=os.getenv("TAVILY_API_KEY"),
            serper_api_key=os.getenv("SERPER_API_KEY"),
            search_provider=os.getenv("SEARCH_PROVIDER", "tavily"),
            max_iterations=int(os.getenv("MAX_ITERATIONS", "3")),
            min_sources=int(os.getenv("MIN_SOURCES", "10")),
            max_sources_per_query=int(os.getenv("MAX_SOURCES_PER_QUERY", "10")),
            domain_weight=float(os.getenv("DOMAIN_WEIGHT", "0.4")),
            citation_weight=float(os.getenv("CITATION_WEIGHT", "0.3")),
            recency_weight=float(os.getenv("RECENCY_WEIGHT", "0.3")),
            api_host=os.getenv("API_HOST", "0.0.0.0"),
            api_port=int(os.getenv("API_PORT", "8000")),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
        )


# Global configuration instance
config = Config.from_env()
