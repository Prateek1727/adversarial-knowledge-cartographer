"""
Scout Agent for the Adversarial Knowledge Cartographer.

This module implements the Scout agent responsible for gathering diverse sources
through web search APIs (Tavily and Serper) with fallback mechanisms and rate limiting.
"""

import logging
import time
from datetime import datetime
from typing import List, Optional
from urllib.parse import urlparse
import httpx
import trafilatura
from bs4 import BeautifulSoup

from models.data_models import Source, WorkflowState
from config import config
from utils.logging_config import (
    log_phase_completion,
    log_source_collection,
    log_data_quality_issue,
    log_fallback_activation,
    log_unrecoverable_failure
)

logger = logging.getLogger(__name__)


class SearchAPIError(Exception):
    """Exception raised when search API calls fail."""
    pass


class ScoutAgent:
    """
    Scout agent responsible for gathering diverse sources on a research topic.
    
    The Scout agent:
    1. Executes web searches using Tavily or Serper APIs
    2. Extracts clean content from search results
    3. Validates and collects sources with unique domains
    4. Implements rate limiting and exponential backoff
    """
    
    def __init__(
        self,
        min_sources: int = 10,
        max_sources_per_query: int = 10,
        max_retries: int = 3,
        initial_backoff: float = 1.0
    ):
        """
        Initialize the Scout agent.
        
        Args:
            min_sources: Minimum number of sources to collect
            max_sources_per_query: Maximum sources per search query
            max_retries: Maximum number of retry attempts for failed requests
            initial_backoff: Initial backoff time in seconds for exponential backoff
        """
        self.min_sources = min_sources
        self.max_sources_per_query = max_sources_per_query
        self.max_retries = max_retries
        self.initial_backoff = initial_backoff
        self.client = httpx.Client(timeout=30.0)
        
        logger.info(
            f"ScoutAgent initialized: min_sources={min_sources}, "
            f"max_sources_per_query={max_sources_per_query}"
        )
    
    def __del__(self):
        """Clean up HTTP client on deletion."""
        if hasattr(self, 'client'):
            self.client.close()
    
    def search_tavily(self, query: str, max_results: int = 10) -> List[dict]:
        """
        Execute search using Tavily API.
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            
        Returns:
            List of search result dictionaries
            
        Raises:
            SearchAPIError: If the API call fails after retries
        """
        if not config.tavily_api_key:
            raise SearchAPIError("Tavily API key not configured")
        
        url = "https://api.tavily.com/search"
        headers = {"Content-Type": "application/json"}
        payload = {
            "api_key": config.tavily_api_key,
            "query": query,
            "search_depth": "advanced",
            "include_domains": [],
            "exclude_domains": [],
            "max_results": max_results,
            "include_answer": False,
            "include_raw_content": True
        }
        
        for attempt in range(self.max_retries):
            try:
                logger.debug(f"Tavily API request (attempt {attempt + 1}): query='{query}'")
                response = self.client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                
                data = response.json()
                results = data.get("results", [])
                logger.info(f"Tavily API returned {len(results)} results for query: '{query}'")
                return results
                
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429:  # Rate limit
                    backoff_time = self.initial_backoff * (2 ** attempt)
                    logger.warning(
                        f"Tavily API rate limit hit, backing off for {backoff_time}s "
                        f"(attempt {attempt + 1}/{self.max_retries})"
                    )
                    time.sleep(backoff_time)
                else:
                    logger.error(f"Tavily API HTTP error: {e}")
                    raise SearchAPIError(f"Tavily API error: {e}")
                    
            except Exception as e:
                logger.error(f"Tavily API request failed: {e}")
                if attempt == self.max_retries - 1:
                    raise SearchAPIError(f"Tavily API failed after {self.max_retries} attempts: {e}")
                time.sleep(self.initial_backoff * (2 ** attempt))
        
        raise SearchAPIError(f"Tavily API failed after {self.max_retries} attempts")
    
    def search_serper(self, query: str, max_results: int = 10) -> List[dict]:
        """
        Execute search using Serper API.
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            
        Returns:
            List of search result dictionaries
            
        Raises:
            SearchAPIError: If the API call fails after retries
        """
        if not config.serper_api_key:
            raise SearchAPIError("Serper API key not configured")
        
        url = "https://google.serper.dev/search"
        headers = {
            "X-API-KEY": config.serper_api_key,
            "Content-Type": "application/json"
        }
        payload = {
            "q": query,
            "num": max_results
        }
        
        for attempt in range(self.max_retries):
            try:
                logger.debug(f"Serper API request (attempt {attempt + 1}): query='{query}'")
                response = self.client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                
                data = response.json()
                results = data.get("organic", [])
                logger.info(f"Serper API returned {len(results)} results for query: '{query}'")
                
                # Transform Serper format to match Tavily format
                transformed_results = []
                for result in results:
                    transformed_results.append({
                        "url": result.get("link", ""),
                        "title": result.get("title", ""),
                        "content": result.get("snippet", ""),
                        "raw_content": None  # Serper doesn't provide raw content
                    })
                
                return transformed_results
                
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429:  # Rate limit
                    backoff_time = self.initial_backoff * (2 ** attempt)
                    logger.warning(
                        f"Serper API rate limit hit, backing off for {backoff_time}s "
                        f"(attempt {attempt + 1}/{self.max_retries})"
                    )
                    time.sleep(backoff_time)
                else:
                    logger.error(f"Serper API HTTP error: {e}")
                    raise SearchAPIError(f"Serper API error: {e}")
                    
            except Exception as e:
                logger.error(f"Serper API request failed: {e}")
                if attempt == self.max_retries - 1:
                    raise SearchAPIError(f"Serper API failed after {self.max_retries} attempts: {e}")
                time.sleep(self.initial_backoff * (2 ** attempt))
        
        raise SearchAPIError(f"Serper API failed after {self.max_retries} attempts")
    
    def search(self, query: str, max_results: int = 10) -> List[dict]:
        """
        Execute search with automatic fallback between providers.
        
        Tries the configured primary provider first, then falls back to the alternative.
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            
        Returns:
            List of search result dictionaries
            
        Raises:
            SearchAPIError: If both providers fail
        """
        primary_provider = config.search_provider
        
        try:
            if primary_provider == "tavily":
                return self.search_tavily(query, max_results)
            else:
                return self.search_serper(query, max_results)
        except SearchAPIError as e:
            logger.warning(f"Primary search provider ({primary_provider}) failed: {e}")
            
            # Try fallback provider
            fallback_provider = "serper" if primary_provider == "tavily" else "tavily"
            log_fallback_activation(
                logger,
                primary=primary_provider,
                fallback=fallback_provider,
                reason=str(e)
            )
            
            try:
                if fallback_provider == "tavily":
                    return self.search_tavily(query, max_results)
                else:
                    return self.search_serper(query, max_results)
            except SearchAPIError as fallback_error:
                logger.error(f"Fallback provider ({fallback_provider}) also failed: {fallback_error}")
                raise SearchAPIError(
                    f"Both search providers failed. Primary ({primary_provider}): {e}, "
                    f"Fallback ({fallback_provider}): {fallback_error}"
                )
    
    def extract_content(self, url: str, fallback_content: Optional[str] = None) -> Optional[str]:
        """
        Extract clean text content from a URL using trafilatura.
        
        Args:
            url: URL to extract content from
            fallback_content: Fallback content to use if extraction fails
            
        Returns:
            Extracted text content, or None if extraction fails
        """
        try:
            logger.debug(f"Extracting content from: {url}")
            
            # Download the page
            downloaded = trafilatura.fetch_url(url)
            if not downloaded:
                logger.warning(f"Failed to download content from: {url}")
                return fallback_content
            
            # Extract clean text
            content = trafilatura.extract(downloaded, include_comments=False, include_tables=False)
            
            if content and len(content.strip()) > 100:  # Minimum content length
                logger.debug(f"Successfully extracted {len(content)} characters from: {url}")
                return content
            else:
                logger.warning(f"Extracted content too short or empty from: {url}")
                return fallback_content
                
        except Exception as e:
            logger.warning(f"Content extraction failed for {url}: {e}")
            return fallback_content
    
    def extract_domain(self, url: str) -> str:
        """
        Extract domain name from URL.
        
        Args:
            url: URL to extract domain from
            
        Returns:
            Domain name (e.g., "example.com")
        """
        try:
            parsed = urlparse(url)
            domain = parsed.netloc
            # Remove www. prefix if present
            if domain.startswith("www."):
                domain = domain[4:]
            return domain
        except Exception as e:
            logger.warning(f"Failed to extract domain from {url}: {e}")
            return url
    
    def is_accessible(self, url: str, content: str) -> bool:
        """
        Check if content is accessible (not paywalled or blocked).
        
        Args:
            url: URL of the content
            content: Extracted content
            
        Returns:
            True if content appears accessible, False otherwise
        """
        if not content or len(content.strip()) < 100:
            return False
        
        # Check for common paywall indicators
        paywall_indicators = [
            "subscribe to continue",
            "subscription required",
            "sign in to read",
            "become a member",
            "paywall",
            "premium content",
            "this article is for subscribers"
        ]
        
        content_lower = content.lower()
        for indicator in paywall_indicators:
            if indicator in content_lower:
                logger.debug(f"Paywall detected in {url}: '{indicator}'")
                return False
        
        return True
    
    def collect_sources(
        self,
        query: str,
        existing_domains: set,
        max_sources: int = 10
    ) -> List[Source]:
        """
        Collect sources from a search query with domain diversity.
        
        Args:
            query: Search query string
            existing_domains: Set of domains already collected
            max_sources: Maximum number of sources to collect
            
        Returns:
            List of Source objects
        """
        sources = []
        
        try:
            # Execute search
            search_results = self.search(query, max_results=max_sources * 2)
            
            for result in search_results:
                if len(sources) >= max_sources:
                    break
                
                url = result.get("url", "")
                title = result.get("title", "")
                snippet = result.get("content", "")
                
                if not url or not title:
                    logger.debug(f"Skipping result with missing URL or title")
                    continue
                
                # Extract domain and check for uniqueness
                domain = self.extract_domain(url)
                if domain in existing_domains:
                    logger.debug(f"Skipping duplicate domain: {domain}")
                    continue
                
                # Extract full content
                raw_content = result.get("raw_content")
                content = self.extract_content(url, fallback_content=snippet or raw_content)
                
                if not content:
                    logger.debug(f"Skipping {url}: content extraction failed")
                    continue
                
                # Check if content is accessible
                if not self.is_accessible(url, content):
                    logger.debug(f"Skipping {url}: content not accessible (paywall or blocked)")
                    continue
                
                # Create Source object
                try:
                    source = Source(
                        url=url,
                        title=title,
                        content=content,
                        domain=domain,
                        retrieved_at=datetime.now(),
                        query_used=query
                    )
                    sources.append(source)
                    existing_domains.add(domain)
                    logger.info(f"Collected source: {title} ({domain})")
                    
                except Exception as e:
                    logger.warning(f"Failed to create Source object for {url}: {e}")
                    continue
            
        except SearchAPIError as e:
            logger.error(f"Search failed for query '{query}': {e}")
        
        return sources
    
    def execute(self, state: WorkflowState) -> WorkflowState:
        """
        Execute the Scout agent to gather diverse sources.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated workflow state with collected sources
        """
        logger.info(f"Scout agent executing for topic: '{state.topic}' (iteration {state.iteration})")
        
        # Track existing domains to ensure diversity
        existing_domains = {source.domain for source in state.sources}
        logger.debug(f"Existing domains: {len(existing_domains)}")
        
        # Determine queries to execute
        queries = []
        
        if state.iteration == 0:
            # Initial broad search
            queries = [
                state.topic,
                f"{state.topic} overview",
                f"{state.topic} research",
                f"{state.topic} analysis"
            ]
        else:
            # Use adversarial queries from previous iteration
            queries = [q for q in state.adversarial_queries if q not in state.executed_queries]
            logger.info(f"Using {len(queries)} adversarial queries")
        
        # Collect sources from each query
        new_sources = []
        for query in queries:
            if len(state.sources) + len(new_sources) >= self.min_sources:
                break
            
            sources = self.collect_sources(
                query,
                existing_domains,
                max_sources=self.max_sources_per_query
            )
            new_sources.extend(sources)
            state.executed_queries.add(query)
        
        # Add new sources to state
        state.sources.extend(new_sources)
        
        # Log phase completion with structured information
        log_phase_completion(
            logger,
            phase="scout",
            iteration=state.iteration,
            new_sources=len(new_sources),
            total_sources=len(state.sources),
            unique_domains=len(existing_domains)
        )
        
        # Log source collection
        log_source_collection(
            logger,
            source_count=len(state.sources),
            unique_domains=len(existing_domains),
            phase="scout"
        )
        
        # Check for data quality issues
        if len(state.sources) < self.min_sources:
            log_data_quality_issue(
                logger,
                issue=f"Collected only {len(state.sources)} sources (minimum: {self.min_sources})",
                phase="scout",
                severity="warning"
            )
        
        # Update status message
        state.status_message = (
            f"Scout phase completed: {len(state.sources)} sources from "
            f"{len(existing_domains)} unique domains"
        )
        
        return state
