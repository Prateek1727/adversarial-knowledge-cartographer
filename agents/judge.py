"""
Judge Agent for the Adversarial Knowledge Cartographer.

This module implements the Judge agent responsible for evaluating source
credibility and weighting conflicting claims based on credibility scores.
"""

import logging
import re
from datetime import datetime
from typing import List, Dict
from urllib.parse import urlparse

from models.data_models import (
    Source,
    KnowledgeGraph,
    Relationship,
    Conflict,
    CredibilityScore,
    WorkflowState
)
from utils.logging_config import (
    log_phase_completion,
    log_unrecoverable_failure
)

logger = logging.getLogger(__name__)


class JudgeAgent:
    """
    Judge agent responsible for evaluating source credibility and weighting claims.
    
    The Judge agent:
    1. Evaluates each source based on domain authority, citations, and recency
    2. Calculates normalized credibility scores (0.0 to 1.0)
    3. Annotates knowledge graph relationships with credibility scores
    4. Annotates conflicts with credibility scores for each side
    5. Resolves conflicts by comparing credibility scores
    """
    
    # Domain authority scoring rules
    DOMAIN_AUTHORITY_SCORES = {
        '.edu': 1.0,
        '.gov': 1.0,
        '.org': 0.8,
    }
    
    # Recognized high-authority domains
    HIGH_AUTHORITY_DOMAINS = {
        'nature.com': 0.95,
        'science.org': 0.95,
        'ieee.org': 0.95,
        'acm.org': 0.95,
        'nih.gov': 1.0,
        'who.int': 0.95,
        'arxiv.org': 0.85,
        'wikipedia.org': 0.7,
        'bbc.com': 0.75,
        'reuters.com': 0.75,
        'nytimes.com': 0.75,
    }
    
    # Weights for overall credibility score calculation
    DOMAIN_WEIGHT = 0.4
    CITATION_WEIGHT = 0.3
    RECENCY_WEIGHT = 0.3
    
    def __init__(self):
        """Initialize the Judge agent."""
        logger.info("JudgeAgent initialized")
    
    def _calculate_domain_authority(self, url: str) -> float:
        """
        Calculate domain authority score based on URL.
        
        Scoring rules:
        - .edu, .gov: 1.0
        - .org: 0.8
        - Recognized journals/authorities: 0.9-0.95
        - .com: 0.5-0.7 based on reputation
        
        Args:
            url: Source URL
            
        Returns:
            Domain authority score between 0.0 and 1.0
        """
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            # Remove 'www.' prefix if present
            if domain.startswith('www.'):
                domain = domain[4:]
            
            # Check for specific high-authority domains
            if domain in self.HIGH_AUTHORITY_DOMAINS:
                score = self.HIGH_AUTHORITY_DOMAINS[domain]
                logger.debug(f"Domain '{domain}' matched high-authority list: {score}")
                return score
            
            # Check TLD-based scoring
            for tld, score in self.DOMAIN_AUTHORITY_SCORES.items():
                if domain.endswith(tld):
                    logger.debug(f"Domain '{domain}' matched TLD '{tld}': {score}")
                    return score
            
            # Default .com scoring (moderate authority)
            if domain.endswith('.com'):
                score = 0.6
                logger.debug(f"Domain '{domain}' is .com: {score}")
                return score
            
            # Unknown domains get lower score
            score = 0.5
            logger.debug(f"Domain '{domain}' is unknown: {score}")
            return score
            
        except Exception as e:
            logger.warning(f"Failed to parse URL '{url}': {e}")
            return 0.5
    
    def _assess_citation_indicators(self, content: str) -> float:
        """
        Assess citation indicators in source content.
        
        Looks for:
        - References section: +0.3
        - Academic formatting (numbered citations, brackets): +0.2
        - Author credentials (Dr., PhD, Professor): +0.3
        
        Args:
            content: Source content text
            
        Returns:
            Citation indicator score between 0.0 and 1.0
        """
        score = 0.0
        content_lower = content.lower()
        
        # Check for references section
        references_patterns = [
            r'\breferences\b',
            r'\bbibliography\b',
            r'\bworks cited\b',
            r'\bcitations\b'
        ]
        
        for pattern in references_patterns:
            if re.search(pattern, content_lower):
                score += 0.3
                logger.debug("Found references section: +0.3")
                break
        
        # Check for academic formatting (citations in brackets or numbered)
        citation_patterns = [
            r'\[\d+\]',  # [1], [2], etc.
            r'\(\d{4}\)',  # (2023), (2024), etc.
            r'\[[\w\s]+,\s*\d{4}\]',  # [Author, 2023]
        ]
        
        for pattern in citation_patterns:
            if re.search(pattern, content):
                score += 0.2
                logger.debug("Found academic citation formatting: +0.2")
                break
        
        # Check for author credentials
        credential_patterns = [
            r'\bdr\.\s+\w+',
            r'\bphd\b',
            r'\bprofessor\b',
            r'\bresearcher\b',
            r'\bscientist\b'
        ]
        
        for pattern in credential_patterns:
            if re.search(pattern, content_lower):
                score += 0.3
                logger.debug("Found author credentials: +0.3")
                break
        
        # Ensure score doesn't exceed 1.0
        score = min(score, 1.0)
        
        logger.debug(f"Citation indicators score: {score}")
        return score
    
    def _calculate_recency_score(self, retrieved_at: datetime) -> float:
        """
        Calculate recency score based on publication/retrieval date.
        
        Scoring rules:
        - < 1 year: 1.0
        - 1-2 years: 0.8
        - 2-5 years: 0.5
        - > 5 years: 0.3
        
        Args:
            retrieved_at: Date when source was retrieved
            
        Returns:
            Recency score between 0.0 and 1.0
        """
        now = datetime.now()
        age_days = (now - retrieved_at).days
        age_years = age_days / 365.25
        
        if age_years < 1:
            score = 1.0
        elif age_years < 2:
            score = 0.8
        elif age_years < 5:
            score = 0.5
        else:
            score = 0.3
        
        logger.debug(f"Source age: {age_years:.1f} years, recency score: {score}")
        return score
    
    def _calculate_overall_score(
        self,
        domain_authority: float,
        citation_indicators: float,
        recency: float
    ) -> float:
        """
        Calculate weighted overall credibility score.
        
        Formula: (domain * 0.4) + (citations * 0.3) + (recency * 0.3)
        
        Args:
            domain_authority: Domain authority score (0-1)
            citation_indicators: Citation indicators score (0-1)
            recency: Recency score (0-1)
            
        Returns:
            Overall credibility score between 0.0 and 1.0
        """
        overall = (
            domain_authority * self.DOMAIN_WEIGHT +
            citation_indicators * self.CITATION_WEIGHT +
            recency * self.RECENCY_WEIGHT
        )
        
        # Ensure score is within bounds
        overall = max(0.0, min(1.0, overall))
        
        logger.debug(
            f"Overall score: {overall:.3f} "
            f"(domain={domain_authority:.3f}, citations={citation_indicators:.3f}, "
            f"recency={recency:.3f})"
        )
        
        return overall
    
    def evaluate_source_credibility(self, source: Source) -> CredibilityScore:
        """
        Evaluate credibility of a single source.
        
        Args:
            source: Source to evaluate
            
        Returns:
            CredibilityScore object with all component scores
        """
        logger.debug(f"Evaluating credibility for source: {source.url}")
        
        # Calculate component scores
        domain_authority = self._calculate_domain_authority(source.url)
        citation_indicators = self._assess_citation_indicators(source.content)
        recency = self._calculate_recency_score(source.retrieved_at)
        
        # Calculate overall score
        overall_score = self._calculate_overall_score(
            domain_authority,
            citation_indicators,
            recency
        )
        
        credibility_score = CredibilityScore(
            source_url=source.url,
            domain_authority=domain_authority,
            citation_indicators=citation_indicators,
            recency=recency,
            overall_score=overall_score
        )
        
        logger.info(
            f"Source credibility evaluated: {source.url} -> {overall_score:.3f}"
        )
        
        return credibility_score

    def evaluate_all_sources(self, sources: List[Source]) -> Dict[str, CredibilityScore]:
        """
        Evaluate credibility for all sources.
        
        Args:
            sources: List of sources to evaluate
            
        Returns:
            Dictionary mapping source URL to CredibilityScore
        """
        logger.info(f"Evaluating credibility for {len(sources)} sources")
        
        credibility_scores = {}
        
        for source in sources:
            try:
                score = self.evaluate_source_credibility(source)
                credibility_scores[source.url] = score
            except Exception as e:
                logger.error(f"Failed to evaluate source {source.url}: {e}")
                # Assign default low credibility on error
                credibility_scores[source.url] = CredibilityScore(
                    source_url=source.url,
                    domain_authority=0.5,
                    citation_indicators=0.0,
                    recency=0.5,
                    overall_score=0.35
                )
        
        logger.info(f"Evaluated {len(credibility_scores)} sources successfully")
        return credibility_scores
    
    def annotate_relationships_with_credibility(
        self,
        relationships: List[Relationship],
        credibility_scores: Dict[str, CredibilityScore]
    ) -> List[Relationship]:
        """
        Annotate relationships with credibility scores from their citations.
        
        Args:
            relationships: List of relationships to annotate
            credibility_scores: Dictionary mapping source URL to CredibilityScore
            
        Returns:
            List of relationships with updated credibility scores
        """
        logger.info(f"Annotating {len(relationships)} relationships with credibility scores")
        
        annotated_relationships = []
        
        for rel in relationships:
            # Get credibility score for the citation
            citation_url = rel.citation
            
            if citation_url in credibility_scores:
                credibility = credibility_scores[citation_url].overall_score
            else:
                logger.warning(
                    f"No credibility score found for citation '{citation_url}', "
                    f"using default 0.5"
                )
                credibility = 0.5
            
            # Create new relationship with updated credibility
            annotated_rel = Relationship(
                source=rel.source,
                relation=rel.relation,
                target=rel.target,
                citation=rel.citation,
                credibility=credibility
            )
            
            annotated_relationships.append(annotated_rel)
        
        logger.info(f"Annotated {len(annotated_relationships)} relationships")
        return annotated_relationships
    
    def annotate_conflicts_with_credibility(
        self,
        conflicts: List[Conflict],
        credibility_scores: Dict[str, CredibilityScore]
    ) -> List[Conflict]:
        """
        Annotate conflicts with credibility scores for each side.
        
        Args:
            conflicts: List of conflicts to annotate
            credibility_scores: Dictionary mapping source URL to CredibilityScore
            
        Returns:
            List of conflicts with updated credibility scores
        """
        logger.info(f"Annotating {len(conflicts)} conflicts with credibility scores")
        
        annotated_conflicts = []
        
        for conflict in conflicts:
            # Get credibility scores for both sides
            side_a_url = conflict.side_a_citation
            side_b_url = conflict.side_b_citation
            
            if side_a_url in credibility_scores:
                side_a_credibility = credibility_scores[side_a_url].overall_score
            else:
                logger.warning(
                    f"No credibility score found for side A citation '{side_a_url}', "
                    f"using default 0.5"
                )
                side_a_credibility = 0.5
            
            if side_b_url in credibility_scores:
                side_b_credibility = credibility_scores[side_b_url].overall_score
            else:
                logger.warning(
                    f"No credibility score found for side B citation '{side_b_url}', "
                    f"using default 0.5"
                )
                side_b_credibility = 0.5
            
            # Create new conflict with updated credibility scores
            annotated_conflict = Conflict(
                point_of_contention=conflict.point_of_contention,
                side_a=conflict.side_a,
                side_a_citation=conflict.side_a_citation,
                side_b=conflict.side_b,
                side_b_citation=conflict.side_b_citation,
                side_a_credibility=side_a_credibility,
                side_b_credibility=side_b_credibility
            )
            
            annotated_conflicts.append(annotated_conflict)
        
        logger.info(f"Annotated {len(annotated_conflicts)} conflicts")
        return annotated_conflicts
    
    def resolve_conflict(self, conflict: Conflict) -> str:
        """
        Resolve a conflict by comparing credibility scores.
        
        Args:
            conflict: Conflict to resolve
            
        Returns:
            String indicating which side has stronger support ("side_a", "side_b", or "tie")
        """
        if conflict.side_a_credibility > conflict.side_b_credibility:
            logger.debug(
                f"Conflict resolved in favor of side A: "
                f"{conflict.side_a_credibility:.3f} > {conflict.side_b_credibility:.3f}"
            )
            return "side_a"
        elif conflict.side_b_credibility > conflict.side_a_credibility:
            logger.debug(
                f"Conflict resolved in favor of side B: "
                f"{conflict.side_b_credibility:.3f} > {conflict.side_a_credibility:.3f}"
            )
            return "side_b"
        else:
            logger.debug(
                f"Conflict is a tie: "
                f"{conflict.side_a_credibility:.3f} == {conflict.side_b_credibility:.3f}"
            )
            return "tie"
    
    def annotate_knowledge_graph(
        self,
        knowledge_graph: KnowledgeGraph,
        credibility_scores: Dict[str, CredibilityScore]
    ) -> KnowledgeGraph:
        """
        Annotate entire knowledge graph with credibility scores.
        
        Args:
            knowledge_graph: Knowledge graph to annotate
            credibility_scores: Dictionary mapping source URL to CredibilityScore
            
        Returns:
            New KnowledgeGraph with credibility annotations
        """
        logger.info("Annotating knowledge graph with credibility scores")
        
        # Annotate relationships
        annotated_relationships = self.annotate_relationships_with_credibility(
            knowledge_graph.relationships,
            credibility_scores
        )
        
        # Annotate conflicts
        annotated_conflicts = self.annotate_conflicts_with_credibility(
            knowledge_graph.conflicts,
            credibility_scores
        )
        
        # Create new knowledge graph with annotations
        annotated_graph = KnowledgeGraph(
            entities=knowledge_graph.entities,
            relationships=annotated_relationships,
            conflicts=annotated_conflicts
        )
        
        logger.info("Knowledge graph annotation completed")
        return annotated_graph
    
    def execute(self, state: WorkflowState) -> WorkflowState:
        """
        Execute the Judge agent to evaluate credibility and annotate the knowledge graph.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated workflow state with credibility-annotated knowledge graph
        """
        logger.info(
            f"Judge agent executing for topic: '{state.topic}' "
            f"with {len(state.sources)} sources"
        )
        
        if not state.sources:
            logger.warning("No sources available for credibility evaluation")
            state.status_message = "Judge phase skipped: no sources available"
            return state
        
        if not state.knowledge_graph or not state.knowledge_graph.relationships:
            logger.warning("No knowledge graph available for annotation")
            state.status_message = "Judge phase skipped: no knowledge graph available"
            return state
        
        try:
            # Evaluate credibility for all sources
            credibility_scores = self.evaluate_all_sources(state.sources)
            
            # Annotate knowledge graph with credibility scores
            annotated_graph = self.annotate_knowledge_graph(
                state.knowledge_graph,
                credibility_scores
            )
            
            # Update state with annotated knowledge graph
            state.knowledge_graph = annotated_graph
            
            # Calculate average credibility for reporting
            avg_credibility = sum(
                score.overall_score for score in credibility_scores.values()
            ) / len(credibility_scores) if credibility_scores else 0.0
            
            # Log phase completion with structured information
            log_phase_completion(
                logger,
                phase="judge",
                iteration=state.iteration,
                sources_evaluated=len(credibility_scores),
                avg_credibility=f"{avg_credibility:.3f}"
            )
            
            state.status_message = (
                f"Judge phase completed: evaluated {len(credibility_scores)} sources, "
                f"average credibility: {avg_credibility:.3f}"
            )
            
        except Exception as e:
            log_unrecoverable_failure(logger, "judge execution", e, "judge")
            state.status_message = f"Judge phase failed: {e}"
        
        return state
