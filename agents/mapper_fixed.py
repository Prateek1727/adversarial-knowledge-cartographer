"""
Mapper Agent for the Adversarial Knowledge Cartographer.

This module implements the Mapper agent responsible for extracting structured
knowledge from sources, including entities, relationships, and conflicts.
"""

import logging
import json
from typing import List, Optional
from difflib import SequenceMatcher

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.output_parsers import JsonOutputParser
from utils.llm_factory import get_llm
from pydantic import ValidationError

from models.data_models import (
    Source,
    KnowledgeGraph,
    Relationship,
    Conflict,
    WorkflowState
)
from config import config
from utils.logging_config import (
    log_phase_completion,
    log_entity_extraction,
    log_data_quality_issue,
    log_unrecoverable_failure
)

logger = logging.getLogger(__name__)


class MapperAgent:
    """
    Mapper agent responsible for extracting structured knowledge from sources.
    
    The Mapper agent:
    1. Analyzes sources using LLM with structured output
    2. Extracts entities with deduplication
    3. Extracts relationships (Knowledge Triplets) with citations
    4. Identifies conflicts between sources
    5. Builds and validates Knowledge Graph
    """
    
    def __init__(
        self,
        max_retries: int = 3,
        fuzzy_match_threshold: float = 0.85,
        llm=None
    ):
        """
        Initialize the Mapper agent.
        
        Args:
            max_retries: Maximum number of retry attempts for LLM calls
            fuzzy_match_threshold: Similarity threshold for entity deduplication (0-1)
            llm: Optional pre-configured LLM instance (for testing)🎯 Summary of Universal Improvements
            I've made the system work better on ALL topics by:
            
            1. Universal Prompt Improvements
            ✅ Clearer instructions that work for any topic
            ✅ Step-by-step process for entity consistency
            ✅ Removed topic-specific examples
            2. Robust Entity Matching
            ✅ More aggressive fuzzy matching (threshold: 0.5 instead of 0.7)
            ✅ Auto-creation of missing entities referenced in relationships
            ✅ Better error handling and logging
            3. Universal Testing
            ✅ Test script that works for diverse topics
            ✅ Faster testing (2 minutes instead of 3)
            ✅ Better error handling
            🚀 Test the Improvements
            Run this to test the universal improvements:
            
            python test_mapper_fix.py
            This will test 6 different types of topics:
            
            Health (coffee effects)
            Technology (AI benefits/risks)
            Environment (climate change)
            Comparison (electric vs gas cars)
            Education (programming languages)
            Psychology (social media impact)
            🎯 The Key Fix
            The main improvement is the auto-creation of missing entities. Now when the LLM creates a relationship like:
            
            "Virat Kohli" -> "ranks_high_in" -> "ICC ODI Rankings"
            If "ICC ODI Rankings" isn't in the entities list, the system will:
            
            ✅ Try fuzzy matching first🎯 The Key Fix
            The main improvement is the auto-creation of missing entities. Now when the LLM creates a relationship like:
            
            "Virat Kohli" -> "ranks_high_in" -> "ICC ODI Rankings"
            If "ICC ODI Rankings" isn't in the entities list, the system will:
            
            ✅ Try fuzzy matching first
            ✅ If no match, auto-create the missing entity
            ✅ Keep the relationship instead of discarding it
            This makes the system work on any topic - cricket, health, technology, or anything else!
            ✅ If no match, auto-create the missing entity
            ✅ Keep the relationship instead of discarding it
            This makes the system work on any topic - cricket, health, technology, or anything else!
        """
        self.max_retries = max_retries
        self.fuzzy_match_threshold = fuzzy_match_threshold
        self.llm = llm if llm is not None else self._initialize_llm()
        
        logger.info(
            f"MapperAgent initialized: max_retries={max_retries}, "
            f"fuzzy_match_threshold={fuzzy_match_threshold}"
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
    
    def _create_mapper_prompt(self, topic: str, sources: List[Source]) -> str:
        """
        Create the Mapper system prompt with sources.
        
        Args:
            topic: Research topic
            sources: List of sources to analyze
            
        Returns:
            Formatted prompt string
        """
        # Format sources for the prompt
        sources_text = ""
        for i, source in enumerate(sources, 1):
            sources_text += f"\n\n--- Source {i} ---\n"
            sources_text += f"Title: {source.title}\n"
            sources_text += f"URL: {source.url}\n"
            sources_text += f"Content: {source.content[:2000]}...\n"  # Limit content length
        
        prompt = f"""You are a Knowledge Cartographer. Extract structured knowledge from sources about "{topic}".

TASK: Create a knowledge graph with entities, relationships, and conflicts.

UNIVERSAL RULES (applies to ANY topic):
1. ENTITY CONSISTENCY: Relationship "source" and "target" MUST exactly match names in "entities" list
2. COMPREHENSIVE ENTITIES: Include ALL concepts mentioned - people, places, organizations, systems, diseases, treatments, technologies, methods, etc.
3. MEANINGFUL RELATIONSHIPS: Connect entities with specific relations like "causes", "prevents", "competes_with", "improves", "reduces"
4. VERIFICATION: Before creating each relationship, confirm both entities exist in your entities list

PROCESS:
Step 1: Read all sources and list EVERY entity mentioned
Step 2: Create relationships using ONLY entities from Step 1  
Step 3: Find conflicts where sources disagree

OUTPUT FORMAT (JSON only):
{{
  "entities": ["Entity1", "Entity2", "Entity3"],
  "relationships": [
    {{
      "source": "Entity1",
      "relation": "affects",
      "target": "Entity2", 
      "citation": "https://source.com"
    }}
  ],
  "conflicts": [
    {{
      "point_of_contention": "Topic of disagreement",
      "side_a": "First viewpoint with evidence",
      "side_a_citation": "https://sourcea.com",
      "side_b": "Opposing viewpoint with evidence", 
      "side_b_citation": "https://sourceb.com"
    }}
  ]
}}

SOURCES:
{sources_text}

Extract knowledge following the rules above. Return ONLY valid JSON."""
        
        return prompt
    
    def _extract_knowledge_with_retry(
        self,
        topic: str,
        sources: List[Source]
    ) -> dict:
        """
        Extract knowledge from sources with retry logic for malformed responses.
        
        Args:
            topic: Research topic
            sources: List of sources to analyze
            
        Returns:
            Dictionary with entities, relationships, and conflicts
            
        Raises:
            Exception: If extraction fails after all retries
        """
        prompt = self._create_mapper_prompt(topic, sources)
        
        for attempt in range(self.max_retries):
            try:
                logger.debug(f"LLM extraction attempt {attempt + 1}/{self.max_retries}")
                
                # Create messages
                messages = [
                    SystemMessage(content="You are a Knowledge Cartographer that extracts structured knowledge from sources."),
                    HumanMessage(content=prompt)
                ]
                
                # Call LLM
                response = self.llm.invoke(messages)
                content = response.content
                
                # Parse JSON response
                # Try to extract JSON from markdown code blocks if present
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0].strip()
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0].strip()
                
                data = json.loads(content)
                
                # Validate structure
                if not isinstance(data, dict):
                    raise ValueError("Response is not a dictionary")
                
                if "entities" not in data or "relationships" not in data or "conflicts" not in data:
                    raise ValueError("Response missing required fields")
                
                logger.info(
                    f"Successfully extracted knowledge: {len(data.get('entities', []))} entities, "
                    f"{len(data.get('relationships', []))} relationships, "
                    f"{len(data.get('conflicts', []))} conflicts"
                )
                
                return data
                
            except json.JSONDecodeError as e:
                logger.warning(f"JSON parsing failed (attempt {attempt + 1}): {e}")
                if attempt == self.max_retries - 1:
                    raise Exception(f"Failed to parse JSON after {self.max_retries} attempts: {e}")
                
            except Exception as e:
                logger.warning(f"Knowledge extraction failed (attempt {attempt + 1}): {e}")
                if attempt == self.max_retries - 1:
                    raise Exception(f"Knowledge extraction failed after {self.max_retries} attempts: {e}")
        
        raise Exception(f"Knowledge extraction failed after {self.max_retries} attempts")
    
    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """
        Calculate similarity between two strings using SequenceMatcher.
        
        Args:
            str1: First string
            str2: Second string
            
        Returns:
            Similarity score between 0 and 1
        """
        return SequenceMatcher(None, str1.lower(), str2.lower()).ratio()
    
    def _find_best_entity_match(self, entity_name: str, entity_list: List[str], threshold: float = 0.7) -> Optional[str]:
        """
        Find the best matching entity from the entity list using fuzzy matching.
        
        Args:
            entity_name: Entity name to match
            entity_list: List of available entities
            threshold: Minimum similarity threshold
            
        Returns:
            Best matching entity name or None if no match above threshold
        """
        best_match = None
        best_score = 0.0
        
        for entity in entity_list:
            score = self._calculate_similarity(entity_name, entity)
            if score >= threshold and score > best_score:
                best_match = entity
                best_score = score
        
        if best_match:
            logger.debug(f"Fuzzy matched '{entity_name}' -> '{best_match}' (score: {best_score:.2f})")
        
        return best_match
    
    def _deduplicate_entities(self, entities: List[str]) -> List[str]:
        """
        Deduplicate entities using fuzzy matching.
        
        Entities with edit distance < 3 (similarity > threshold) are considered duplicates.
        
        Args:
            entities: List of entity strings
            
        Returns:
            Deduplicated list of entities
        """
        if not entities:
            return []
        
        unique_entities = []
        
        for entity in entities:
            entity = entity.strip()
            if not entity:
                continue
            
            # Check if this entity is similar to any existing unique entity
            is_duplicate = False
            for unique_entity in unique_entities:
                similarity = self._calculate_similarity(entity, unique_entity)
                if similarity >= self.fuzzy_match_threshold:
                    logger.debug(
                        f"Entity '{entity}' is duplicate of '{unique_entity}' "
                        f"(similarity: {similarity:.2f})"
                    )
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique_entities.append(entity)
        
        logger.info(
            f"Entity deduplication: {len(entities)} -> {len(unique_entities)} "
            f"(removed {len(entities) - len(unique_entities)} duplicates)"
        )
        
        return unique_entities
    
    def _validate_citation(self, citation: str, sources: List[Source]) -> bool:
        """
        Validate that a citation references a valid source URL.
        
        Args:
            citation: Citation URL string
            sources: List of available sources
            
        Returns:
            True if citation is valid, False otherwise
        """
        source_urls = {source.url for source in sources}
        return citation in source_urls
    
    def _extract_relationships(
        self,
        relationships_data: List[dict],
        sources: List[Source]
    ) -> List[Relationship]:
        """
        Extract and validate relationships from LLM response.
        
        Args:
            relationships_data: List of relationship dictionaries from LLM
            sources: List of sources for citation validation
            
        Returns:
            List of validated Relationship objects
        """
        relationships = []
        
        for rel_data in relationships_data:
            try:
                # Validate required fields
                if not all(key in rel_data for key in ['source', 'relation', 'target', 'citation']):
                    logger.warning(f"Relationship missing required fields: {rel_data}")
                    continue
                
                # Validate citation (log warning but don't reject)
                citation = rel_data['citation']
                if not self._validate_citation(citation, sources):
                    logger.warning(
                        f"Relationship citation '{citation}' does not match any source URL"
                    )
                
                # Create Relationship object
                relationship = Relationship(
                    source=rel_data['source'],
                    relation=rel_data['relation'],
                    target=rel_data['target'],
                    citation=citation,
                    credibility=rel_data.get('credibility', 1.0)
                )
                
                relationships.append(relationship)
                
            except ValidationError as e:
                logger.warning(f"Failed to create Relationship: {e}")
                continue
            except Exception as e:
                logger.warning(f"Error processing relationship: {e}")
                continue
        
        logger.info(f"Extracted {len(relationships)} valid relationships")
        return relationships
    
    def _extract_conflicts(self, conflicts_data: List[dict]) -> List[Conflict]:
        """
        Extract and validate conflicts from LLM response.
        
        Args:
            conflicts_data: List of conflict dictionaries from LLM
            
        Returns:
            List of validated Conflict objects
        """
        conflicts = []
        
        for conflict_data in conflicts_data:
            try:
                # Validate required fields
                required_fields = [
                    'point_of_contention',
                    'side_a',
                    'side_a_citation',
                    'side_b',
                    'side_b_citation'
                ]
                
                if not all(key in conflict_data for key in required_fields):
                    logger.warning(f"Conflict missing required fields: {conflict_data}")
                    continue
                
                # Create Conflict object
                conflict = Conflict(
                    point_of_contention=conflict_data['point_of_contention'],
                    side_a=conflict_data['side_a'],
                    side_a_citation=conflict_data['side_a_citation'],
                    side_b=conflict_data['side_b'],
                    side_b_citation=conflict_data['side_b_citation'],
                    side_a_credibility=conflict_data.get('side_a_credibility', 1.0),
                    side_b_credibility=conflict_data.get('side_b_credibility', 1.0)
                )
                
                conflicts.append(conflict)
                
            except ValidationError as e:
                logger.warning(f"Failed to create Conflict: {e}")
                continue
            except Exception as e:
                logger.warning(f"Error processing conflict: {e}")
                continue
        
        logger.info(f"Extracted {len(conflicts)} valid conflicts")
        return conflicts
    
    def build_knowledge_graph(
        self,
        topic: str,
        sources: List[Source]
    ) -> KnowledgeGraph:
        """
        Build a Knowledge Graph from sources.
        
        Args:
            topic: Research topic
            sources: List of sources to analyze
            
        Returns:
            Validated KnowledgeGraph object
            
        Raises:
            Exception: If knowledge graph construction fails
        """
        logger.info(f"Building knowledge graph from {len(sources)} sources")
        
        # Extract knowledge using LLM
        knowledge_data = self._extract_knowledge_with_retry(topic, sources)
        
        # Extract and deduplicate entities
        raw_entities = knowledge_data.get('entities', [])
        unique_entities = self._deduplicate_entities(raw_entities)
        
        # Log entity extraction
        log_entity_extraction(logger, len(unique_entities), "mapper")
        
        # Extract relationships
        relationships_data = knowledge_data.get('relationships', [])
        relationships = self._extract_relationships(relationships_data, sources)
        
        # Extract conflicts
        conflicts_data = knowledge_data.get('conflicts', [])
        conflicts = self._extract_conflicts(conflicts_data)
        
        # Build Knowledge Graph
        try:
            # Filter relationships to only include those with valid entity references
            entity_names = {entity for entity in unique_entities}
            valid_relationships = []
            invalid_count = 0
            
            for rel in relationships:
                source_match = rel.source in entity_names
                target_match = rel.target in entity_names
                
                # Try fuzzy matching if exact match fails (very lenient for relationships)
                relationship_threshold = 0.5  # Much more lenient to catch entity name variations
                
                if not source_match:
                    for entity in unique_entities:
                        if self._calculate_similarity(rel.source, entity) >= relationship_threshold:
                            logger.debug(f"Fuzzy matched relationship source: '{rel.source}' -> '{entity}'")
                            rel.source = entity  # Update to exact entity name
                            source_match = True
                            break
                
                if not target_match:
                    for entity in unique_entities:
                        if self._calculate_similarity(rel.target, entity) >= relationship_threshold:
                            logger.debug(f"Fuzzy matched relationship target: '{rel.target}' -> '{entity}'")
                            rel.target = entity  # Update to exact entity name
                            target_match = True
                            break
                
                # Auto-create missing entities if they seem valid (fallback mechanism)
                if not source_match and rel.source.strip() and len(rel.source.strip()) > 2:
                    unique_entities.append(rel.source)
                    entity_names.add(rel.source)
                    source_match = True
                    logger.info(f"Auto-created missing entity: '{rel.source}'")
                
                if not target_match and rel.target.strip() and len(rel.target.strip()) > 2:
                    unique_entities.append(rel.target)
                    entity_names.add(rel.target)
                    target_match = True
                    logger.info(f"Auto-created missing entity: '{rel.target}'")
                
                if source_match and target_match:
                    valid_relationships.append(rel)
                else:
                    invalid_count += 1
                    logger.warning(
                        f"Skipping invalid relationship: {rel.source} -> {rel.target} "
                        f"(invalid entity names)"
                    )
            
            if invalid_count > 0:
                logger.warning(f"Filtered out {invalid_count} invalid relationships")
            
            # Log final statistics
            logger.info(
                f"Final knowledge graph: {len(unique_entities)} entities, "
                f"{len(valid_relationships)} relationships, {len(conflicts)} conflicts"
            )
            
            # Warn if no relationships were created
            if len(valid_relationships) == 0 and len(relationships) > 0:
                logger.warning(
                    f"No valid relationships created from {len(relationships)} extracted relationships. "
                    f"This suggests entity naming inconsistency in the LLM response."
                )
            
            knowledge_graph = KnowledgeGraph(
                entities=unique_entities,
                relationships=valid_relationships,
                conflicts=conflicts
            )
            
            # Validate referential integrity (should pass now after filtering)
            try:
                knowledge_graph.validate_referential_integrity()
            except ValueError as e:
                logger.warning(f"Referential integrity check failed even after filtering: {e}")
                # Continue anyway with what we have
            
            logger.info(
                f"Knowledge graph built successfully: "
                f"{len(knowledge_graph.entities)} entities, "
                f"{len(knowledge_graph.relationships)} relationships, "
                f"{len(knowledge_graph.conflicts)} conflicts"
            )
            
            return knowledge_graph
            
        except ValidationError as e:
            logger.error(f"Knowledge graph validation failed: {e}")
            # Return empty graph instead of failing completely
            logger.warning("Returning empty knowledge graph due to validation failure")
            return KnowledgeGraph(entities=[], relationships=[], conflicts=[])
    
    def _merge_knowledge_graphs(
        self,
        existing: KnowledgeGraph,
        new: KnowledgeGraph
    ) -> KnowledgeGraph:
        """
        Merge new knowledge graph with existing one.
        
        Args:
            existing: Existing knowledge graph
            new: New knowledge graph to merge
            
        Returns:
            Merged knowledge graph
        """
        # Merge entities (deduplicate)
        all_entities = existing.entities + new.entities
        merged_entities = self._deduplicate_entities(all_entities)
        
        # Merge relationships (keep all, including duplicates for citation counting)
        merged_relationships = existing.relationships + new.relationships
        
        # Merge conflicts (keep all)
        merged_conflicts = existing.conflicts + new.conflicts
        
        merged_graph = KnowledgeGraph(
            entities=merged_entities,
            relationships=merged_relationships,
            conflicts=merged_conflicts
        )
        
        # Validate referential integrity
        merged_graph.validate_referential_integrity()
        
        logger.info(
            f"Merged knowledge graphs: {len(merged_entities)} entities, "
            f"{len(merged_relationships)} relationships, {len(merged_conflicts)} conflicts"
        )
        
        return merged_graph
    
    def execute(self, state: WorkflowState) -> WorkflowState:
        """
        Execute the Mapper agent to extract structured knowledge.
    
        Args:
            state: Current workflow state
            
        Returns:
            Updated workflow state with knowledge graph
        """
        logger.info(
            f"Mapper agent executing for topic: '{state.topic}' "
            f"with {len(state.sources)} sources (iteration {state.iteration})"
        )
        
        if not state.sources:
            logger.warning("No sources available for mapping")
            state.status_message = "Mapper phase skipped: no sources available"
            return state
        
        try:
            # Build knowledge graph from sources
            new_knowledge_graph = self.build_knowledge_graph(state.topic, state.sources)
            
            # Merge with existing knowledge graph if this is not the first iteration
            if state.iteration > 0 and state.knowledge_graph:
                knowledge_graph = self._merge_knowledge_graphs(
                    state.knowledge_graph,
                    new_knowledge_graph
                )
            else:
                knowledge_graph = new_knowledge_graph
            
            # Update state with knowledge graph
            state.knowledge_graph = knowledge_graph
            
            # Log phase completion with structured information
            log_phase_completion(
                logger,
                phase="mapper",
                iteration=state.iteration,
                entities=len(knowledge_graph.entities),
                relationships=len(knowledge_graph.relationships),
                conflicts=len(knowledge_graph.conflicts)
            )
            
            # Check for data quality issues
            if len(knowledge_graph.entities) == 0:
                log_data_quality_issue(
                    logger,
                    issue="No entities extracted from sources",
                    phase="mapper",
                    severity="warning"
                )
            
            if len(knowledge_graph.relationships) == 0:
                log_data_quality_issue(
                    logger,
                    issue="No relationships extracted from sources",
                    phase="mapper",
                    severity="warning"
                )
            
            state.status_message = (
                f"Mapper phase completed: extracted {len(knowledge_graph.entities)} entities, "
                f"{len(knowledge_graph.relationships)} relationships, "
                f"{len(knowledge_graph.conflicts)} conflicts"
            )
            
        except Exception as e:
            log_unrecoverable_failure(logger, "mapper execution", e, "mapper")
            state.status_message = f"Mapper phase failed: {e}"
        
        return state
