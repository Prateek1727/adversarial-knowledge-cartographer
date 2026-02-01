"""
Unit tests for Judge Agent credibility calculation.

These tests verify specific examples of domain authority scoring,
citation indicator assessment, and recency scoring.
"""

import pytest
from datetime import datetime, timedelta
from agents.judge import JudgeAgent
from models.data_models import Source


class TestDomainAuthorityScoring:
    """Test domain authority scoring logic."""
    
    def test_edu_domain_gets_max_score(self):
        """Test that .edu domains receive 1.0 authority score."""
        judge = JudgeAgent()
        score = judge._calculate_domain_authority("https://stanford.edu/article")
        assert score == 1.0
    
    def test_gov_domain_gets_max_score(self):
        """Test that .gov domains receive 1.0 authority score."""
        judge = JudgeAgent()
        score = judge._calculate_domain_authority("https://nih.gov/research")
        assert score == 1.0
    
    def test_org_domain_gets_high_score(self):
        """Test that .org domains receive 0.8 authority score."""
        judge = JudgeAgent()
        score = judge._calculate_domain_authority("https://example.org/article")
        assert score == 0.8
    
    def test_com_domain_gets_moderate_score(self):
        """Test that .com domains receive 0.6 authority score."""
        judge = JudgeAgent()
        score = judge._calculate_domain_authority("https://example.com/article")
        assert score == 0.6
    
    def test_recognized_journal_gets_high_score(self):
        """Test that recognized journals receive high authority scores."""
        judge = JudgeAgent()
        
        # Test Nature
        score = judge._calculate_domain_authority("https://nature.com/article")
        assert score == 0.95
        
        # Test Science
        score = judge._calculate_domain_authority("https://science.org/article")
        assert score == 0.95
        
        # Test IEEE
        score = judge._calculate_domain_authority("https://ieee.org/paper")
        assert score == 0.95
    
    def test_arxiv_gets_good_score(self):
        """Test that arXiv receives 0.85 authority score."""
        judge = JudgeAgent()
        score = judge._calculate_domain_authority("https://arxiv.org/abs/2301.12345")
        assert score == 0.85
    
    def test_wikipedia_gets_moderate_score(self):
        """Test that Wikipedia receives 0.7 authority score."""
        judge = JudgeAgent()
        score = judge._calculate_domain_authority("https://wikipedia.org/wiki/Topic")
        assert score == 0.7
    
    def test_www_prefix_is_handled(self):
        """Test that www. prefix is properly handled."""
        judge = JudgeAgent()
        score = judge._calculate_domain_authority("https://www.nature.com/article")
        assert score == 0.95
    
    def test_unknown_domain_gets_default_score(self):
        """Test that unknown domains receive 0.5 default score."""
        judge = JudgeAgent()
        score = judge._calculate_domain_authority("https://unknown-site.xyz/article")
        assert score == 0.5


class TestCitationIndicatorAssessment:
    """Test citation indicator assessment logic."""
    
    def test_references_section_adds_score(self):
        """Test that references section adds 0.3 to score."""
        judge = JudgeAgent()
        content = "Some article content.\n\nReferences:\n1. Citation one\n2. Citation two"
        score = judge._assess_citation_indicators(content)
        assert score >= 0.3
    
    def test_bibliography_section_adds_score(self):
        """Test that bibliography section adds 0.3 to score."""
        judge = JudgeAgent()
        content = "Some article content.\n\nBibliography:\n- Book one\n- Book two"
        score = judge._assess_citation_indicators(content)
        assert score >= 0.3
    
    def test_numbered_citations_add_score(self):
        """Test that numbered citations add 0.2 to score."""
        judge = JudgeAgent()
        content = "This is supported by research [1] and further evidence [2]."
        score = judge._assess_citation_indicators(content)
        assert score >= 0.2
    
    def test_year_citations_add_score(self):
        """Test that year-based citations add 0.2 to score."""
        judge = JudgeAgent()
        content = "Research shows (2023) that this is true (2024)."
        score = judge._assess_citation_indicators(content)
        assert score >= 0.2
    
    def test_author_credentials_add_score(self):
        """Test that author credentials add 0.3 to score."""
        judge = JudgeAgent()
        
        # Test Dr. title
        content = "Written by Dr. Smith who is an expert."
        score = judge._assess_citation_indicators(content)
        assert score >= 0.3
        
        # Test PhD
        content = "The author has a PhD in the field."
        score = judge._assess_citation_indicators(content)
        assert score >= 0.3
        
        # Test Professor
        content = "Professor Johnson conducted this research."
        score = judge._assess_citation_indicators(content)
        assert score >= 0.3
    
    def test_multiple_indicators_combine(self):
        """Test that multiple indicators combine up to 1.0."""
        judge = JudgeAgent()
        content = """
        Written by Dr. Smith, PhD.
        
        This research [1] shows evidence (2023).
        
        References:
        [1] Previous work
        """
        score = judge._assess_citation_indicators(content)
        assert score >= 0.8  # Should have all three components
        assert score <= 1.0  # Should not exceed 1.0
    
    def test_no_indicators_gives_zero(self):
        """Test that content with no indicators gives 0.0 score."""
        judge = JudgeAgent()
        content = "Just some plain text with no academic indicators."
        score = judge._assess_citation_indicators(content)
        assert score == 0.0


class TestRecencyScoring:
    """Test recency scoring logic."""
    
    def test_recent_source_gets_max_score(self):
        """Test that sources < 1 year old get 1.0 recency score."""
        judge = JudgeAgent()
        recent_date = datetime.now() - timedelta(days=180)  # 6 months ago
        score = judge._calculate_recency_score(recent_date)
        assert score == 1.0
    
    def test_one_year_old_source_gets_high_score(self):
        """Test that sources 1-2 years old get 0.8 recency score."""
        judge = JudgeAgent()
        date = datetime.now() - timedelta(days=540)  # 1.5 years ago
        score = judge._calculate_recency_score(date)
        assert score == 0.8
    
    def test_three_year_old_source_gets_moderate_score(self):
        """Test that sources 2-5 years old get 0.5 recency score."""
        judge = JudgeAgent()
        date = datetime.now() - timedelta(days=1095)  # 3 years ago
        score = judge._calculate_recency_score(date)
        assert score == 0.5
    
    def test_old_source_gets_low_score(self):
        """Test that sources > 5 years old get 0.3 recency score."""
        judge = JudgeAgent()
        date = datetime.now() - timedelta(days=2190)  # 6 years ago
        score = judge._calculate_recency_score(date)
        assert score == 0.3
    
    def test_very_recent_source(self):
        """Test that sources from today get 1.0 recency score."""
        judge = JudgeAgent()
        today = datetime.now()
        score = judge._calculate_recency_score(today)
        assert score == 1.0


class TestOverallCredibilityCalculation:
    """Test overall credibility score calculation."""
    
    def test_weighted_average_formula(self):
        """Test that overall score uses correct weighted average."""
        judge = JudgeAgent()
        
        # Test with known values
        domain = 1.0
        citations = 0.6
        recency = 0.8
        
        expected = (domain * 0.4) + (citations * 0.3) + (recency * 0.3)
        actual = judge._calculate_overall_score(domain, citations, recency)
        
        assert abs(actual - expected) < 0.001
    
    def test_overall_score_is_normalized(self):
        """Test that overall score is always between 0 and 1."""
        judge = JudgeAgent()
        
        # Test various combinations
        test_cases = [
            (0.0, 0.0, 0.0),
            (1.0, 1.0, 1.0),
            (0.5, 0.5, 0.5),
            (1.0, 0.0, 0.5),
            (0.3, 0.7, 0.9),
        ]
        
        for domain, citations, recency in test_cases:
            score = judge._calculate_overall_score(domain, citations, recency)
            assert 0.0 <= score <= 1.0
    
    def test_high_quality_source_gets_high_score(self):
        """Test that high-quality sources get high overall scores."""
        judge = JudgeAgent()
        
        # .edu domain, good citations, recent
        score = judge._calculate_overall_score(1.0, 0.8, 1.0)
        assert score >= 0.9
    
    def test_low_quality_source_gets_low_score(self):
        """Test that low-quality sources get low overall scores."""
        judge = JudgeAgent()
        
        # Unknown domain, no citations, old
        score = judge._calculate_overall_score(0.5, 0.0, 0.3)
        assert score <= 0.4


class TestSourceCredibilityEvaluation:
    """Test complete source credibility evaluation."""
    
    def test_evaluate_edu_source_with_citations(self):
        """Test evaluation of high-quality .edu source."""
        judge = JudgeAgent()
        
        source = Source(
            url="https://stanford.edu/research/article",
            title="Research Article",
            content="Written by Dr. Smith.\n\nReferences:\n[1] Citation",
            domain="stanford.edu",
            retrieved_at=datetime.now() - timedelta(days=30),
            query_used="test query"
        )
        
        credibility = judge.evaluate_source_credibility(source)
        
        assert credibility.domain_authority == 1.0
        assert credibility.citation_indicators >= 0.6
        assert credibility.recency == 1.0
        assert credibility.overall_score >= 0.85
    
    def test_evaluate_com_source_without_citations(self):
        """Test evaluation of moderate-quality .com source."""
        judge = JudgeAgent()
        
        source = Source(
            url="https://example.com/blog/post",
            title="Blog Post",
            content="Just some blog content with no academic indicators at all.",
            domain="example.com",
            retrieved_at=datetime.now() - timedelta(days=1095),  # 3 years
            query_used="test query"
        )
        
        credibility = judge.evaluate_source_credibility(source)
        
        assert credibility.domain_authority == 0.6
        assert credibility.citation_indicators == 0.0
        assert credibility.recency == 0.5
        # Overall = (0.6 * 0.4) + (0.0 * 0.3) + (0.5 * 0.3) = 0.24 + 0 + 0.15 = 0.39
        assert 0.35 <= credibility.overall_score <= 0.45
    
    def test_evaluate_nature_source(self):
        """Test evaluation of Nature journal source."""
        judge = JudgeAgent()
        
        source = Source(
            url="https://nature.com/articles/12345",
            title="Scientific Article",
            content="Research by Professor Jones.\n\nReferences:\n[1] Study",
            domain="nature.com",
            retrieved_at=datetime.now() - timedelta(days=100),
            query_used="test query"
        )
        
        credibility = judge.evaluate_source_credibility(source)
        
        assert credibility.domain_authority == 0.95
        assert credibility.citation_indicators >= 0.6
        assert credibility.recency == 1.0
        assert credibility.overall_score >= 0.85
