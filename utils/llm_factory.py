"""
LLM Factory for creating language model instances.

This module provides a factory function to create LLM instances
based on the configured provider (OpenAI, Anthropic, or Groq).
"""

import logging
import time
from typing import Any, Callable
from functools import wraps
from config import config

logger = logging.getLogger(__name__)


def with_rate_limit_retry(max_retries: int = 3, base_delay: float = 1.0):
    """
    Decorator to add exponential backoff retry logic for rate limiting.
    
    Args:
        max_retries: Maximum number of retries
        base_delay: Base delay in seconds (will be exponentially increased)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    error_str = str(e).lower()
                    
                    # Check if it's a rate limiting error
                    if any(phrase in error_str for phrase in [
                        "rate limit", "429", "too many requests", 
                        "quota exceeded", "rate_limit_exceeded"
                    ]):
                        if attempt < max_retries:
                            delay = base_delay * (2 ** attempt)  # Exponential backoff
                            logger.warning(
                                f"⏳ Rate limit hit (attempt {attempt + 1}/{max_retries + 1}). "
                                f"Retrying in {delay:.1f}s... Error: {e}"
                            )
                            time.sleep(delay)
                            continue
                        else:
                            logger.error(f"❌ Rate limit exceeded after {max_retries} retries: {e}")
                    
                    # Re-raise non-rate-limit errors immediately
                    raise e
            
            # If we get here, all retries failed
            raise last_exception
        
        return wrapper
    return decorator


def get_llm(**kwargs: Any) -> Any:
    """
    Get an LLM instance based on the configured provider.
    
    Args:
        **kwargs: Additional arguments to pass to the LLM constructor
        
    Returns:
        LLM instance (ChatOpenAI, ChatAnthropic, or ChatGroq)
        
    Raises:
        ValueError: If provider is not configured or API key is missing
    """
    # Merge default config with kwargs
    llm_kwargs = {
        "model": config.llm_model,
        "temperature": config.llm_temperature,
        **kwargs
    }
    
    if config.llm_provider == "openai":
        if not config.openai_api_key:
            raise ValueError("OpenAI API key not configured")
        
        from langchain_openai import ChatOpenAI
        logger.debug(f"Creating ChatOpenAI with model={llm_kwargs['model']}")
        return ChatOpenAI(
            api_key=config.openai_api_key,
            **llm_kwargs
        )
    
    elif config.llm_provider == "anthropic":
        if not config.anthropic_api_key:
            raise ValueError("Anthropic API key not configured")
        
        from langchain_anthropic import ChatAnthropic
        logger.debug(f"Creating ChatAnthropic with model={llm_kwargs['model']}")
        return ChatAnthropic(
            api_key=config.anthropic_api_key,
            **llm_kwargs
        )
    
    elif config.llm_provider == "groq":
        if not config.groq_api_key:
            raise ValueError("Groq API key not configured")
        
        try:
            from langchain_groq import ChatGroq
        except ImportError:
            raise ImportError(
                "langchain-groq is not installed. Install it with: pip install langchain-groq"
            )
        
        # Add rate limiting and retry configuration for Groq
        groq_kwargs = {
            **llm_kwargs,
            "max_retries": 3,  # Retry on rate limits
            "request_timeout": 60,  # Longer timeout for retries
        }
        
        logger.debug(f"Creating ChatGroq with model={groq_kwargs['model']}, max_retries=3")
        return ChatGroq(
            api_key=config.groq_api_key,
            **groq_kwargs
        )
    
    else:
        raise ValueError(
            f"Unsupported LLM provider: {config.llm_provider}. "
            f"Supported providers: openai, anthropic, groq"
        )
