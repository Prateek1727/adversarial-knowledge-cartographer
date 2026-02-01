"""
Synthesis Agent for the Adversarial Knowledge Cartographer.

This module implements the Synthesis agent responsible for generating the final
research report with consensus, battleground analysis, verdicts, and the knowledge graph.
"""

import logging
import json
from typing import List, Dict, Tuple

from langchain_core.messages import SystemMessage, HumanMessage
from utils.llm_factory import get_llm

from models.data_models import (
    WorkflowState,
    KnowledgeGraph,
    Relationship,
    Conflict
)
from config import config
from utils.logging_config import (
    log_phase_completion,
    log_unrecoverable_failure
)

logger = logging.getLogger(__name__)


class BattlegroundTopic:
    """Represents a battleground topic with conflicting claims."""
    
    def __init__(
        self,
        topic: str,
        conflicting_claims: List[str],
        disagreement_reason: str,
        verdict: str,
        verdict_confidence: float,
        supporting_evidence: List[str]
    ):
        """
        Initialize a battleground topic.
        
        Args:
            topic: The point of contention
            conflicting_claims: List of conflicting claims
            disagreement_reason: Why sources disagree
            verdict: Which side is more likely correct
            verdict_confidence: Confidence in the verdict (0-1)
            supporting_evidence: Evidence supporting the verdict
        """
        self.topic = topic
        self.conflicting_claims = conflicting_claims
        self.disagreement_reason = disagreement_reason
        self.verdict = verdict
        self.verdict_confidence = verdict_confidence
        self.supporting_evidence = supporting_evidence


class SynthesisAgent:
    """
    Synthesis agent responsible for generating the final research report.
    
    The Synthesis agent:
    1. Identifies consensus points (90%+ agreement)
    2. Analyzes battleground topics (conflicts)
    3. Generates verdicts based on credibility scores
    4. Structures the final report
    5. Appends the knowledge graph JSON
    """
    
    def __init__(
        self,
        consensus_threshold: float = 0.9,
        max_retries: int = 3,
        llm=None
    ):
        """
        Initialize the Synthesis agent.
        
        Args:
            consensus_threshold: Threshold for consensus (0-1)
            max_retries: Maximum number of retry attempts for LLM calls
            llm: Optional pre-configured LLM instance (for testing)
        """
        self.consensus_threshold = consensus_threshold
        self.max_retries = max_retries
        self.llm = llm if llm is not None else self._initialize_llm()
        
        logger.info(
            f"SynthesisAgent initialized: consensus_threshold={consensus_threshold}, "
            f"max_retries={max_retries}"
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

    def _create_synthesis_prompt(
        self,
        topic: str,
        knowledge_graph: KnowledgeGraph,
        consensus_points: List[str],
        battleground_topics: List[BattlegroundTopic]
    ) -> str:
        """
        Create the Synthesis system prompt for generating the final report.
        
        Args:
            topic: Research topic
            knowledge_graph: Final knowledge graph
            consensus_points: List of consensus points
            battleground_topics: List of battleground topics
            
        Returns:
            Formatted prompt string
        """
        # Format consensus points
        consensus_text = "\n".join(f"- {point}" for point in consensus_points)
        if not consensus_text:
            consensus_text = "- No strong consensus points identified"
        
        # Format battleground topics
        battleground_text = ""
        for i, bt in enumerate(battleground_topics, 1):
            battleground_text += f"\n{i}. {bt.topic}\n"
            battleground_text += f"   Conflicting Claims:\n"
            for claim in bt.conflicting_claims:
                battleground_text += f"   - {claim}\n"
            battleground_text += f"   Disagreement Reason: {bt.disagreement_reason}\n"
            battleground_text += f"   Verdict: {bt.verdict} (confidence: {bt.verdict_confidence:.2f})\n"
        
        if not battleground_text:
            battleground_text = "\nNo significant conflicts identified"
        
        # Format key relationships
        relationships_text = ""
        for i, rel in enumerate(knowledge_graph.relationships[:20], 1):
            relationships_text += f"{i}. {rel.source} {rel.relation} {rel.target} (credibility: {rel.credibility:.2f})\n"
        
        prompt = f"""Role: You are a Principal Investigator.

Task: Synthesize the gathered Triplets and Conflicts into a final strategic report on "{topic}".

Current Knowledge Graph Summary:
- Entities: {len(knowledge_graph.entities)}
- Relationships: {len(knowledge_graph.relationships)}
- Conflicts: {len(knowledge_graph.conflicts)}

Key Relationships:
{relationships_text}

Consensus Points (90%+ agreement):
{consensus_text}

Battleground Topics (Conflicts):
{battleground_text}

Structure your report with the following sections:

1. The Consensus: What do 90% or more of sources agree on?
2. The Battleground: Deeply analyze the specific points where sources disagreed. Why do they disagree? (e.g., Different methodologies? Different datasets? Different timeframes?)
3. The Verdict: Based on source credibility (domain authority, citation count), which side is more likely correct for each battleground topic?

Write a comprehensive synthesis report that provides strategic insights into the research landscape for "{topic}".
Focus on actionable insights and clear explanations of why sources agree or disagree.

Return your report as plain text with clear section headers."""
        
        return prompt
    
    def identify_consensus(
        self,
        knowledge_graph: KnowledgeGraph
    ) -> List[str]:
        """
        Identify consensus points where 90%+ of sources agree.
        
        A consensus point is a claim (relationship) that appears in multiple sources
        with high credibility and no significant conflicts.
        
        Args:
            knowledge_graph: Knowledge graph to analyze
            
        Returns:
            List of consensus point strings
        """
        logger.info("Identifying consensus points")
        
        consensus_points = []
        
        # Group relationships by claim (source-relation-target)
        claim_groups: Dict[str, List[Relationship]] = {}
        
        for rel in knowledge_graph.relationships:
            claim_key = f"{rel.source}|{rel.relation}|{rel.target}"
            if claim_key not in claim_groups:
                claim_groups[claim_key] = []
            claim_groups[claim_key].append(rel)
        
        # Calculate total number of unique sources
        total_sources = len(set(rel.citation for rel in knowledge_graph.relationships))
        
        if total_sources == 0:
            logger.warning("No sources found in relationships")
            return consensus_points
        
        # Identify claims with high agreement
        for claim_key, rels in claim_groups.items():
            # Calculate support ratio
            num_supporting_sources = len(set(rel.citation for rel in rels))
            support_ratio = num_supporting_sources / total_sources
            
            # Calculate average credibility
            avg_credibility = sum(rel.credibility for rel in rels) / len(rels)
            
            # Check if this is a consensus point
            if support_ratio >= self.consensus_threshold and avg_credibility >= 0.6:
                parts = claim_key.split("|")
                consensus_claim = f"{parts[0]} {parts[1]} {parts[2]} (supported by {num_supporting_sources} sources, avg credibility: {avg_credibility:.2f})"
                consensus_points.append(consensus_claim)
                
                logger.debug(
                    f"Consensus identified: {consensus_claim} "
                    f"(support: {support_ratio:.2%})"
                )
        
        logger.info(f"Identified {len(consensus_points)} consensus points")
        return consensus_points
    
    def extract_battleground_topics(
        self,
        knowledge_graph: KnowledgeGraph
    ) -> List[BattlegroundTopic]:
        """
        Extract battleground topics from conflicts in the knowledge graph.
        
        Args:
            knowledge_graph: Knowledge graph to analyze
            
        Returns:
            List of BattlegroundTopic objects
        """
        logger.info("Extracting battleground topics")
        
        battleground_topics = []
        
        for conflict in knowledge_graph.conflicts:
            # Determine verdict based on credibility scores
            if conflict.side_a_credibility > conflict.side_b_credibility:
                verdict = f"Side A is more likely correct: {conflict.side_a}"
                verdict_confidence = conflict.side_a_credibility
                supporting_evidence = [conflict.side_a_citation]
            elif conflict.side_b_credibility > conflict.side_a_credibility:
                verdict = f"Side B is more likely correct: {conflict.side_b}"
                verdict_confidence = conflict.side_b_credibility
                supporting_evidence = [conflict.side_b_citation]
            else:
                verdict = "Insufficient evidence to determine which side is correct"
                verdict_confidence = 0.5
                supporting_evidence = [conflict.side_a_citation, conflict.side_b_citation]
            
            # Analyze disagreement reason (simplified heuristic)
            disagreement_reason = self._analyze_disagreement_reason(conflict)
            
            battleground_topic = BattlegroundTopic(
                topic=conflict.point_of_contention,
                conflicting_claims=[
                    f"Side A: {conflict.side_a} (credibility: {conflict.side_a_credibility:.2f})",
                    f"Side B: {conflict.side_b} (credibility: {conflict.side_b_credibility:.2f})"
                ],
                disagreement_reason=disagreement_reason,
                verdict=verdict,
                verdict_confidence=verdict_confidence,
                supporting_evidence=supporting_evidence
            )
            
            battleground_topics.append(battleground_topic)
            
            logger.debug(f"Battleground topic extracted: {conflict.point_of_contention}")
        
        logger.info(f"Extracted {len(battleground_topics)} battleground topics")
        return battleground_topics
    
    def _analyze_disagreement_reason(self, conflict: Conflict) -> str:
        """
        Analyze why sources disagree (heuristic-based).
        
        Args:
            conflict: Conflict to analyze
            
        Returns:
            String describing the likely reason for disagreement
        """
        # Check for methodology-related keywords
        methodology_keywords = ["method", "approach", "technique", "algorithm"]
        if any(keyword in conflict.side_a.lower() or keyword in conflict.side_b.lower() 
               for keyword in methodology_keywords):
            return "Different methodologies or approaches"
        
        # Check for dataset-related keywords
        dataset_keywords = ["data", "dataset", "sample", "study", "research"]
        if any(keyword in conflict.side_a.lower() or keyword in conflict.side_b.lower() 
               for keyword in dataset_keywords):
            return "Different datasets or study populations"
        
        # Check for timeframe-related keywords
        timeframe_keywords = ["year", "recent", "historical", "current", "past"]
        if any(keyword in conflict.side_a.lower() or keyword in conflict.side_b.lower() 
               for keyword in timeframe_keywords):
            return "Different timeframes or temporal contexts"
        
        # Check for credibility difference
        credibility_diff = abs(conflict.side_a_credibility - conflict.side_b_credibility)
        if credibility_diff > 0.3:
            return "Significant difference in source credibility"
        
        # Default reason
        return "Conflicting interpretations or perspectives"
    
    def generate_synthesis_report(
        self,
        topic: str,
        knowledge_graph: KnowledgeGraph,
        consensus_points: List[str],
        battleground_topics: List[BattlegroundTopic]
    ) -> str:
        """
        Generate the synthesis report using LLM.
        
        Args:
            topic: Research topic
            knowledge_graph: Final knowledge graph
            consensus_points: List of consensus points
            battleground_topics: List of battleground topics
            
        Returns:
            Synthesis report as string
            
        Raises:
            Exception: If report generation fails after retries
        """
        prompt = self._create_synthesis_prompt(
            topic,
            knowledge_graph,
            consensus_points,
            battleground_topics
        )
        
        for attempt in range(self.max_retries):
            try:
                logger.debug(f"LLM synthesis attempt {attempt + 1}/{self.max_retries}")
                
                # Create messages
                messages = [
                    SystemMessage(content="You are a Principal Investigator synthesizing research findings."),
                    HumanMessage(content=prompt)
                ]
                
                # Call LLM
                response = self.llm.invoke(messages)
                report = response.content
                
                if not report or len(report.strip()) < 100:
                    raise ValueError("Generated report is too short or empty")
                
                logger.info(f"Successfully generated synthesis report ({len(report)} characters)")
                return report
                
            except Exception as e:
                logger.warning(f"Report generation failed (attempt {attempt + 1}): {e}")
                if attempt == self.max_retries - 1:
                    raise Exception(f"Report generation failed after {self.max_retries} attempts: {e}")
        
        raise Exception(f"Report generation failed after {self.max_retries} attempts")
    
    def serialize_knowledge_graph(self, knowledge_graph: KnowledgeGraph) -> str:
        """
        Serialize knowledge graph to JSON string.
        
        Args:
            knowledge_graph: Knowledge graph to serialize
            
        Returns:
            JSON string representation
            
        Raises:
            Exception: If serialization fails
        """
        try:
            logger.info("Serializing knowledge graph to JSON")
            
            # Convert to dictionary
            graph_dict = {
                "entities": knowledge_graph.entities,
                "relationships": [
                    {
                        "source": rel.source,
                        "relation": rel.relation,
                        "target": rel.target,
                        "citation": rel.citation,
                        "credibility": rel.credibility
                    }
                    for rel in knowledge_graph.relationships
                ],
                "conflicts": [
                    {
                        "point_of_contention": conflict.point_of_contention,
                        "side_a": conflict.side_a,
                        "side_a_citation": conflict.side_a_citation,
                        "side_a_credibility": conflict.side_a_credibility,
                        "side_b": conflict.side_b,
                        "side_b_citation": conflict.side_b_citation,
                        "side_b_credibility": conflict.side_b_credibility
                    }
                    for conflict in knowledge_graph.conflicts
                ]
            }
            
            # Serialize to JSON with pretty printing
            json_str = json.dumps(graph_dict, indent=2, ensure_ascii=False)
            
            # Validate by parsing back
            json.loads(json_str)
            
            logger.info(f"Knowledge graph serialized successfully ({len(json_str)} characters)")
            return json_str
            
        except Exception as e:
            logger.error(f"Failed to serialize knowledge graph: {e}")
            raise Exception(f"Knowledge graph serialization failed: {e}")
    
    def create_final_report(
        self,
        topic: str,
        knowledge_graph: KnowledgeGraph
    ) -> str:
        """
        Create the complete final report with all sections.
        
        Args:
            topic: Research topic
            knowledge_graph: Final knowledge graph
            
        Returns:
            Complete report string with all sections and JSON graph
        """
        logger.info(f"Creating final synthesis report for topic: '{topic}'")
        
        # Identify consensus points
        consensus_points = self.identify_consensus(knowledge_graph)
        
        # Extract battleground topics
        battleground_topics = self.extract_battleground_topics(knowledge_graph)
        
        # Generate synthesis report using LLM
        synthesis_text = self.generate_synthesis_report(
            topic,
            knowledge_graph,
            consensus_points,
            battleground_topics
        )
        
        # Serialize knowledge graph to JSON
        graph_json = self.serialize_knowledge_graph(knowledge_graph)
        
        # Assemble final report
        final_report = f"""# Adversarial Knowledge Cartographer - Research Report

## Topic: {topic}

{synthesis_text}

---

## Knowledge Graph (JSON)

```json
{graph_json}
```

---

## Report Metadata

- Total Entities: {len(knowledge_graph.entities)}
- Total Relationships: {len(knowledge_graph.relationships)}
- Total Conflicts: {len(knowledge_graph.conflicts)}
- Consensus Points: {len(consensus_points)}
- Battleground Topics: {len(battleground_topics)}
"""
        
        logger.info(
            f"Final report created: {len(final_report)} characters, "
            f"{len(consensus_points)} consensus points, "
            f"{len(battleground_topics)} battleground topics"
        )
        
        return final_report
    
    def execute(self, state: WorkflowState) -> WorkflowState:
        """
        Execute the Synthesis agent to generate the final report.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated workflow state with synthesis report
        """
        logger.info(
            f"Synthesis agent executing for topic: '{state.topic}'"
        )
        
        if not state.knowledge_graph or not state.knowledge_graph.relationships:
            logger.warning("No knowledge graph available for synthesis")
            state.status_message = "Synthesis phase skipped: no knowledge graph available"
            return state
        
        try:
            # Create final report
            final_report = self.create_final_report(
                state.topic,
                state.knowledge_graph
            )
            
            # Update state with synthesis report
            state.synthesis_report = final_report
            
            # Count consensus and battleground topics
            consensus_count = final_report.count("Consensus Points:")
            battleground_count = final_report.count("Battleground Topics:")
            
            # Log phase completion with structured information
            log_phase_completion(
                logger,
                phase="synthesis",
                iteration=state.iteration,
                report_length=len(final_report),
                entities=len(state.knowledge_graph.entities) if state.knowledge_graph else 0,
                relationships=len(state.knowledge_graph.relationships) if state.knowledge_graph else 0,
                conflicts=len(state.knowledge_graph.conflicts) if state.knowledge_graph else 0
            )
            
            state.status_message = (
                f"Synthesis phase completed: generated final report "
                f"({len(final_report)} characters)"
            )
            
        except Exception as e:
            log_unrecoverable_failure(logger, "synthesis execution", e, "synthesis")
            state.status_message = f"Synthesis phase failed: {e}"
        
        return state
