"""
Adversary Agent for the Adversarial Knowledge Cartographer.

This module implements the Adversary agent responsible for red-teaming the
current findings by identifying weaknesses and generating counter-evidence queries.
"""

import logging
import json
from typing import List, Dict
from datetime import datetime, timedelta

from langchain_core.messages import SystemMessage, HumanMessage
from utils.llm_factory import get_llm

from models.data_models import (
    WorkflowState,
    KnowledgeGraph,
    Source,
    Relationship
)
from config import config
from utils.logging_config import (
    log_phase_completion,
    log_data_quality_issue,
    log_unrecoverable_failure
)

logger = logging.getLogger(__name__)


class Weakness:
    """Represents a weakness identified in the current findings."""
    
    def __init__(
        self,
        weakness_type: str,
        description: str,
        affected_claims: List[str]
    ):
        """
        Initialize a weakness.
        
        Args:
            weakness_type: Type of weakness (single_source, outdated, potential_bias)
            description: Description of the weakness
            affected_claims: List of claims affected by this weakness
        """
        self.type = weakness_type
        self.description = description
        self.affected_claims = affected_claims


class AdversaryAgent:
    """
    Adversary agent responsible for red-teaming findings and generating counter-queries.
    
    The Adversary agent:
    1. Analyzes current knowledge graph for weaknesses
    2. Identifies single-source claims
    3. Detects outdated sources (> 2 years old)
    4. Identifies potential bias indicators
    5. Generates adversarial search queries to find counter-evidence
    """
    
    def __init__(
        self,
        max_retries: int = 3,
        min_counter_queries: int = 3,
        outdated_threshold_years: int = 2,
        llm=None
    ):
        """
        Initialize the Adversary agent.
        
        Args:
            max_retries: Maximum number of retry attempts for LLM calls
            min_counter_queries: Minimum number of counter-queries to generate
            outdated_threshold_years: Years threshold for considering sources outdated
            llm: Optional pre-configured LLM instance (for testing)
        """
        self.max_retries = max_retries
        self.min_counter_queries = min_counter_queries
        self.outdated_threshold_years = outdated_threshold_years
        self.llm = llm if llm is not None else self._initialize_llm()
        
        logger.info(
            f"AdversaryAgent initialized: min_counter_queries={min_counter_queries}, "
            f"outdated_threshold_years={outdated_threshold_years}"
        )
    
    def _initialize_llm(self):
        """
        Initialize the LLM based on configuration.
        
        Returns:
            Configured LLM instance
        """
        llm = get_llm()
        logger.info(f"Initialized {config.llm_provider} LLM: {config.llm_model}")
        return llm
    
    def identify_single_source_claims(
        self,
        knowledge_graph: KnowledgeGraph
    ) -> List[Weakness]:
        """
        Identify claims that rely on only a single source.
        
        Args:
            knowledge_graph: Current knowledge graph
            
        Returns:
            List of weaknesses for single-source claims
        """
        weaknesses = []
        
        # Count citations for each relationship
        citation_counts: Dict[str, List[Relationship]] = {}
        
        for rel in knowledge_graph.relationships:
            # Create a key for the relationship (source-relation-target)
            rel_key = f"{rel.source}|{rel.relation}|{rel.target}"
            
            if rel_key not in citation_counts:
                citation_counts[rel_key] = []
            citation_counts[rel_key].append(rel)
        
        # Identify single-source relationships
        for rel_key, rels in citation_counts.items():
            if len(rels) == 1:
                rel = rels[0]
                claim = f"{rel.source} {rel.relation} {rel.target}"
                
                weakness = Weakness(
                    weakness_type="single_source",
                    description=f"Claim relies on only one source: {rel.citation}",
                    affected_claims=[claim]
                )
                weaknesses.append(weakness)
                
                logger.debug(f"Single-source weakness identified: {claim}")
        
        logger.info(f"Identified {len(weaknesses)} single-source weaknesses")
        return weaknesses
    
    def detect_outdated_sources(
        self,
        sources: List[Source]
    ) -> List[Weakness]:
        """
        Detect sources that are older than the threshold.
        
        Args:
            sources: List of sources to check
            
        Returns:
            List of weaknesses for outdated sources
        """
        weaknesses = []
        cutoff_date = datetime.now() - timedelta(days=365 * self.outdated_threshold_years)
        
        for source in sources:
            if source.retrieved_at < cutoff_date:
                age_years = (datetime.now() - source.retrieved_at).days / 365
                
                weakness = Weakness(
                    weakness_type="outdated",
                    description=f"Source is {age_years:.1f} years old: {source.url}",
                    affected_claims=[source.title]
                )
                weaknesses.append(weakness)
                
                logger.debug(f"Outdated source detected: {source.title} ({age_years:.1f} years old)")
        
        logger.info(f"Identified {len(weaknesses)} outdated sources")
        return weaknesses
    
    def identify_bias_indicators(
        self,
        sources: List[Source]
    ) -> List[Weakness]:
        """
        Identify potential bias indicators in sources.
        
        Args:
            sources: List of sources to check
            
        Returns:
            List of weaknesses for potential bias
        """
        weaknesses = []
        
        # Common bias indicators
        bias_keywords = [
            "opinion", "editorial", "blog", "sponsored",
            "advertisement", "promoted", "partisan"
        ]
        
        # Potentially biased domains
        biased_domain_patterns = [
            ".blog", "wordpress.com", "medium.com", "substack.com"
        ]
        
        for source in sources:
            bias_found = []
            
            # Check for bias keywords in title or URL
            title_lower = source.title.lower()
            url_lower = source.url.lower()
            
            for keyword in bias_keywords:
                if keyword in title_lower or keyword in url_lower:
                    bias_found.append(f"keyword '{keyword}'")
            
            # Check for biased domain patterns
            for pattern in biased_domain_patterns:
                if pattern in source.domain.lower():
                    bias_found.append(f"domain pattern '{pattern}'")
            
            if bias_found:
                weakness = Weakness(
                    weakness_type="potential_bias",
                    description=f"Potential bias indicators: {', '.join(bias_found)}",
                    affected_claims=[source.title]
                )
                weaknesses.append(weakness)
                
                logger.debug(f"Bias indicators found in: {source.title}")
        
        logger.info(f"Identified {len(weaknesses)} sources with potential bias")
        return weaknesses
    
    def _create_adversary_prompt(
        self,
        topic: str,
        knowledge_graph: KnowledgeGraph,
        weaknesses: List[Weakness]
    ) -> str:
        """
        Create the Adversary system prompt for generating counter-queries.
        
        Args:
            topic: Research topic
            knowledge_graph: Current knowledge graph
            weaknesses: List of identified weaknesses
            
        Returns:
            Formatted prompt string
        """
        # Format current findings
        findings_text = f"Topic: {topic}\n\n"
        findings_text += f"Entities: {', '.join(knowledge_graph.entities[:20])}\n\n"
        findings_text += "Key Relationships:\n"
        
        for i, rel in enumerate(knowledge_graph.relationships[:10], 1):
            findings_text += f"{i}. {rel.source} {rel.relation} {rel.target}\n"
        
        # Format weaknesses
        weaknesses_text = "\n"
        for weakness in weaknesses[:10]:
            weaknesses_text += f"- {weakness.type}: {weakness.description}\n"
        
        prompt = f"""Role: You are a Red-Teamer and Academic Skeptic.

Input: The current draft findings on "{topic}".

Current Findings:
{findings_text}

Identified Weaknesses:
{weaknesses_text}

Task: Identify the Weakest Links in the current information.
- Look for claims that rely on a single source
- Look for outdated statistics (older than {self.outdated_threshold_years} years)
- Look for potential bias in the sources

Action: Generate {self.min_counter_queries} new, aggressive search queries designed to debunk 
the current findings.

Example: If the finding is "Coffee is good for health," your query 
should be "Negative cardiovascular effects of daily caffeine intake."

Output Format (JSON only):
{{
  "counter_queries": [
    "Query 1 designed to find counter-evidence",
    "Query 2 designed to find counter-evidence",
    "Query 3 designed to find counter-evidence"
  ]
}}

Generate queries that will help find evidence that contradicts or challenges the current findings.
Return ONLY valid JSON matching the schema above."""
        
        return prompt
    
    def generate_counter_queries(
        self,
        topic: str,
        knowledge_graph: KnowledgeGraph,
        weaknesses: List[Weakness]
    ) -> List[str]:
        """
        Generate adversarial search queries using LLM.
        
        Args:
            topic: Research topic
            knowledge_graph: Current knowledge graph
            weaknesses: List of identified weaknesses
            
        Returns:
            List of counter-evidence search queries
            
        Raises:
            Exception: If query generation fails after retries
        """
        prompt = self._create_adversary_prompt(topic, knowledge_graph, weaknesses)
        
        for attempt in range(self.max_retries):
            try:
                logger.debug(f"LLM query generation attempt {attempt + 1}/{self.max_retries}")
                
                # Create messages
                messages = [
                    SystemMessage(content="You are a Red-Teamer that generates adversarial search queries."),
                    HumanMessage(content=prompt)
                ]
                
                # Call LLM
                response = self.llm.invoke(messages)
                content = response.content
                
                # Parse JSON response
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0].strip()
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0].strip()
                
                data = json.loads(content)
                
                # Validate structure
                if not isinstance(data, dict) or "counter_queries" not in data:
                    raise ValueError("Response missing 'counter_queries' field")
                
                queries = data["counter_queries"]
                
                if not isinstance(queries, list) or len(queries) < self.min_counter_queries:
                    raise ValueError(f"Expected at least {self.min_counter_queries} queries")
                
                logger.info(f"Successfully generated {len(queries)} counter-queries")
                return queries
                
            except json.JSONDecodeError as e:
                logger.warning(f"JSON parsing failed (attempt {attempt + 1}): {e}")
                if attempt == self.max_retries - 1:
                    raise Exception(f"Failed to parse JSON after {self.max_retries} attempts: {e}")
                
            except Exception as e:
                logger.warning(f"Query generation failed (attempt {attempt + 1}): {e}")
                if attempt == self.max_retries - 1:
                    raise Exception(f"Query generation failed after {self.max_retries} attempts: {e}")
        
        raise Exception(f"Query generation failed after {self.max_retries} attempts")
    
    def execute(self, state: WorkflowState) -> WorkflowState:
        """
        Execute the Adversary agent to identify weaknesses and generate counter-queries.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated workflow state with adversarial queries
        """
        logger.info(
            f"Adversary agent executing for topic: '{state.topic}' "
            f"(iteration {state.iteration})"
        )
        
        # Check if we have a knowledge graph to analyze
        if not state.knowledge_graph or not state.knowledge_graph.relationships:
            logger.warning("No knowledge graph available for adversarial analysis")
            state.adversarial_queries = []
            state.status_message = "Adversary phase skipped: no knowledge graph available"
            return state
        
        try:
            # Identify weaknesses
            weaknesses = []
            
            # 1. Identify single-source claims
            single_source_weaknesses = self.identify_single_source_claims(state.knowledge_graph)
            weaknesses.extend(single_source_weaknesses)
            
            # 2. Detect outdated sources
            outdated_weaknesses = self.detect_outdated_sources(state.sources)
            weaknesses.extend(outdated_weaknesses)
            
            # 3. Identify bias indicators
            bias_weaknesses = self.identify_bias_indicators(state.sources)
            weaknesses.extend(bias_weaknesses)
            
            logger.info(f"Total weaknesses identified: {len(weaknesses)}")
            
            # Generate counter-queries if weaknesses found
            if weaknesses:
                counter_queries = self.generate_counter_queries(
                    state.topic,
                    state.knowledge_graph,
                    weaknesses
                )
                
                # Filter out queries that have already been executed
                new_queries = [q for q in counter_queries if q not in state.executed_queries]
                
                state.adversarial_queries = new_queries
                
                # Log phase completion with structured information
                log_phase_completion(
                    logger,
                    phase="adversary",
                    iteration=state.iteration,
                    weaknesses=len(weaknesses),
                    counter_queries=len(new_queries)
                )
                
                state.status_message = (
                    f"Adversary phase completed: identified {len(weaknesses)} weaknesses, "
                    f"generated {len(new_queries)} counter-queries"
                )
            else:
                state.adversarial_queries = []
                state.status_message = "Adversary phase completed: no significant weaknesses found"
            
        except Exception as e:
            log_unrecoverable_failure(logger, "adversary execution", e, "adversary")
            state.adversarial_queries = []
            state.status_message = f"Adversary phase failed: {e}"
        
        return state
