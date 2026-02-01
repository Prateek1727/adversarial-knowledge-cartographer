"""
Core data models for the Adversarial Knowledge Cartographer.

These Pydantic models define the structure for workflow state, sources,
knowledge graphs, and credibility scoring.
"""

from datetime import datetime
from typing import List, Optional, Set
from pydantic import BaseModel, Field, field_validator


class Source(BaseModel):
    """Represents a source document retrieved during research."""
    url: str
    title: str
    content: str
    domain: str
    retrieved_at: datetime
    query_used: str = ""

    @field_validator('url', 'title', 'content', 'domain')
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        """Ensure required string fields are non-empty."""
        if not v or not v.strip():
            raise ValueError("Field must be non-empty")
        return v


class Relationship(BaseModel):
    """Represents a knowledge triplet with source, relation, and target."""
    source: str
    relation: str
    target: str
    citation: str
    credibility: float = 1.0

    @field_validator('source', 'relation', 'target', 'citation')
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        """Ensure required string fields are non-empty."""
        if not v or not v.strip():
            raise ValueError("Field must be non-empty")
        return v

    @field_validator('credibility')
    @classmethod
    def validate_credibility_range(cls, v: float) -> float:
        """Ensure credibility score is between 0 and 1."""
        if not 0.0 <= v <= 1.0:
            raise ValueError("Credibility must be between 0.0 and 1.0")
        return v


class Conflict(BaseModel):
    """Represents a point of contention between sources."""
    point_of_contention: str
    side_a: str
    side_a_citation: str
    side_b: str
    side_b_citation: str
    side_a_credibility: float = 1.0
    side_b_credibility: float = 1.0

    @field_validator('point_of_contention', 'side_a', 'side_a_citation', 
                     'side_b', 'side_b_citation')
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        """Ensure required string fields are non-empty."""
        if not v or not v.strip():
            raise ValueError("Field must be non-empty")
        return v

    @field_validator('side_a_credibility', 'side_b_credibility')
    @classmethod
    def validate_credibility_range(cls, v: float) -> float:
        """Ensure credibility score is between 0 and 1."""
        if not 0.0 <= v <= 1.0:
            raise ValueError("Credibility must be between 0.0 and 1.0")
        return v


class KnowledgeGraph(BaseModel):
    """Represents the structured knowledge graph with entities, relationships, and conflicts."""
    entities: List[str] = Field(default_factory=list)
    relationships: List[Relationship] = Field(default_factory=list)
    conflicts: List[Conflict] = Field(default_factory=list)

    @field_validator('entities')
    @classmethod
    def validate_unique_entities(cls, v: List[str]) -> List[str]:
        """Ensure entities list contains no duplicates."""
        if len(v) != len(set(v)):
            raise ValueError("Entities must be unique")
        return v

    def validate_referential_integrity(self) -> bool:
        """
        Validate that all relationships reference entities that exist in the entities list.
        Returns True if valid, raises ValueError otherwise.
        """
        entity_set = set(self.entities)
        for rel in self.relationships:
            if rel.source not in entity_set:
                raise ValueError(f"Relationship source '{rel.source}' not in entities list")
            if rel.target not in entity_set:
                raise ValueError(f"Relationship target '{rel.target}' not in entities list")
        return True


class CredibilityScore(BaseModel):
    """Represents credibility scoring for a source."""
    source_url: str
    domain_authority: float
    citation_indicators: float
    recency: float
    overall_score: float

    @field_validator('domain_authority', 'citation_indicators', 'recency', 'overall_score')
    @classmethod
    def validate_score_range(cls, v: float) -> float:
        """Ensure all scores are between 0 and 1."""
        if not 0.0 <= v <= 1.0:
            raise ValueError("Score must be between 0.0 and 1.0")
        return v


class WorkflowState(BaseModel):
    """Represents the complete state of the research workflow."""
    topic: str
    iteration: int = 0
    sources: List[Source] = Field(default_factory=list)
    knowledge_graph: KnowledgeGraph = Field(default_factory=KnowledgeGraph)
    adversarial_queries: List[str] = Field(default_factory=list)
    executed_queries: Set[str] = Field(default_factory=set)
    synthesis_report: Optional[str] = None
    max_iterations: int = 3
    current_phase: str = "initialized"
    status_message: Optional[str] = None

    @field_validator('topic')
    @classmethod
    def validate_topic(cls, v: str) -> str:
        """Ensure topic is non-empty and contains meaningful content."""
        if not v or not v.strip():
            raise ValueError("Topic must be non-empty")
        return v

    @field_validator('iteration')
    @classmethod
    def validate_iteration(cls, v: int) -> int:
        """Ensure iteration is non-negative."""
        if v < 0:
            raise ValueError("Iteration must be non-negative")
        return v

    class Config:
        """Pydantic configuration."""
        # Allow set type for executed_queries
        arbitrary_types_allowed = False
