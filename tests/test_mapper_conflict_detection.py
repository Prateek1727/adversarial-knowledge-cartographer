"""
Unit tests for Mapper agent conflict detection.

These tests validate that the Mapper agent correctly identifies conflicts
when sources contain contradictory information.
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch

from agents.mapper import MapperAgent
from models.data_models import Source, Conflict


class TestMapperConflictDetection:
    """Unit tests for conflict detection in Mapper agent."""
    
    def test_conflict_extraction_with_contradictions(self):
        """
        Test conflict extraction with sources containing known contradictions.
        
        Validates: Requirements 3.4
        """
        # Create sources with contradictory information
        sources = [
            Source(
                url="https://source-a.com/article1",
                title="Coffee is Healthy",
                content="Recent studies show that coffee consumption reduces the risk of heart disease by 20%.",
                domain="source-a.com",
                retrieved_at=datetime.now(),
                query_used="coffee health effects"
            ),
            Source(
                url="https://source-b.com/article2",
                title="Coffee Health Risks",
                content="Research indicates that excessive coffee intake increases cardiovascular risk by 15%.",
                domain="source-b.com",
                retrieved_at=datetime.now(),
                query_used="coffee health effects"
            )
        ]
        
        # Create mapper with mock LLM
        mock_llm = Mock()
        mapper = MapperAgent(llm=mock_llm)
        
        # Mock the LLM response to return a conflict
        mock_conflict_data = {
            "entities": ["Coffee", "Heart Disease", "Cardiovascular Risk"],
            "relationships": [
                {
                    "source": "Coffee",
                    "relation": "reduces_risk_of",
                    "target": "Heart Disease",
                    "citation": "https://source-a.com/article1"
                },
                {
                    "source": "Coffee",
                    "relation": "increases_risk_of",
                    "target": "Cardiovascular Risk",
                    "citation": "https://source-b.com/article2"
                }
            ],
            "conflicts": [
                {
                    "point_of_contention": "Effect of coffee on cardiovascular health",
                    "side_a": "Coffee reduces heart disease risk by 20%",
                    "side_a_citation": "https://source-a.com/article1",
                    "side_b": "Coffee increases cardiovascular risk by 15%",
                    "side_b_citation": "https://source-b.com/article2"
                }
            ]
        }
        
        with patch.object(mapper, '_extract_knowledge_with_retry', return_value=mock_conflict_data):
            kg = mapper.build_knowledge_graph("coffee health effects", sources)
            
            # Verify conflict was extracted
            assert len(kg.conflicts) == 1, f"Expected 1 conflict, got {len(kg.conflicts)}"
            
            conflict = kg.conflicts[0]
            assert conflict.point_of_contention == "Effect of coffee on cardiovascular health"
            assert "reduces" in conflict.side_a.lower() or "20%" in conflict.side_a
            assert "increases" in conflict.side_b.lower() or "15%" in conflict.side_b
            assert conflict.side_a_citation == "https://source-a.com/article1"
            assert conflict.side_b_citation == "https://source-b.com/article2"
    
    def test_conflict_field_completeness(self):
        """
        Test that extracted conflicts have all required fields populated.
        
        Validates: Requirements 3.4
        """
        # Create mapper with mock LLM (not needed for this test)
        mock_llm = Mock()
        mapper = MapperAgent(llm=mock_llm)
        
        # Test with complete conflict data
        conflicts_data = [
            {
                "point_of_contention": "Algorithm efficiency",
                "side_a": "O(n) complexity",
                "side_a_citation": "https://paper-a.com",
                "side_b": "O(n^2) worst case",
                "side_b_citation": "https://paper-b.com"
            }
        ]
        
        conflicts = mapper._extract_conflicts(conflicts_data)
        
        assert len(conflicts) == 1
        conflict = conflicts[0]
        
        # Verify all required fields are present and non-empty
        assert conflict.point_of_contention
        assert conflict.side_a
        assert conflict.side_a_citation
        assert conflict.side_b
        assert conflict.side_b_citation
    
    def test_conflict_extraction_with_missing_fields(self):
        """
        Test that conflicts with missing required fields are rejected.
        
        Validates: Requirements 3.4
        """
        # Create mapper with mock LLM (not needed for this test)
        mock_llm = Mock()
        mapper = MapperAgent(llm=mock_llm)
        
        # Test with incomplete conflict data (missing side_b_citation)
        conflicts_data = [
            {
                "point_of_contention": "Algorithm efficiency",
                "side_a": "O(n) complexity",
                "side_a_citation": "https://paper-a.com",
                "side_b": "O(n^2) worst case"
                # Missing side_b_citation
            }
        ]
        
        conflicts = mapper._extract_conflicts(conflicts_data)
        
        # Conflict should be rejected due to missing field
        assert len(conflicts) == 0, "Conflict with missing fields should be rejected"
    
    def test_multiple_conflicts_extraction(self):
        """
        Test extraction of multiple conflicts from sources.
        
        Validates: Requirements 3.4
        """
        # Create mapper with mock LLM (not needed for this test)
        mock_llm = Mock()
        mapper = MapperAgent(llm=mock_llm)
        
        conflicts_data = [
            {
                "point_of_contention": "Climate change causes",
                "side_a": "Primarily human-caused",
                "side_a_citation": "https://climate-a.org",
                "side_b": "Natural cycles dominant",
                "side_b_citation": "https://climate-b.org"
            },
            {
                "point_of_contention": "Temperature increase rate",
                "side_a": "1.5°C by 2030",
                "side_a_citation": "https://temp-a.org",
                "side_b": "2.0°C by 2040",
                "side_b_citation": "https://temp-b.org"
            }
        ]
        
        conflicts = mapper._extract_conflicts(conflicts_data)
        
        assert len(conflicts) == 2, f"Expected 2 conflicts, got {len(conflicts)}"
        
        # Verify both conflicts are properly structured
        for conflict in conflicts:
            assert conflict.point_of_contention
            assert conflict.side_a
            assert conflict.side_a_citation
            assert conflict.side_b
            assert conflict.side_b_citation
    
    def test_no_conflicts_when_sources_agree(self):
        """
        Test that no conflicts are extracted when sources agree.
        
        Validates: Requirements 3.4
        """
        sources = [
            Source(
                url="https://source-a.com/article1",
                title="Water is Essential",
                content="Water is essential for human survival and health.",
                domain="source-a.com",
                retrieved_at=datetime.now(),
                query_used="water health"
            ),
            Source(
                url="https://source-b.com/article2",
                title="Importance of Water",
                content="Drinking water is crucial for maintaining good health.",
                domain="source-b.com",
                retrieved_at=datetime.now(),
                query_used="water health"
            )
        ]
        
        # Create mapper with mock LLM
        mock_llm = Mock()
        mapper = MapperAgent(llm=mock_llm)
        
        # Mock LLM response with no conflicts
        mock_data = {
            "entities": ["Water", "Health"],
            "relationships": [
                {
                    "source": "Water",
                    "relation": "essential_for",
                    "target": "Health",
                    "citation": "https://source-a.com/article1"
                }
            ],
            "conflicts": []
        }
        
        with patch.object(mapper, '_extract_knowledge_with_retry', return_value=mock_data):
            kg = mapper.build_knowledge_graph("water health", sources)
            
            # Verify no conflicts were extracted
            assert len(kg.conflicts) == 0, f"Expected 0 conflicts, got {len(kg.conflicts)}"
