"""Elasticsearch Showcase API Schemas."""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, HttpUrl, Field


# ============================================================================
# Profile Schemas
# ============================================================================

class UserProfileRequest(BaseModel):
    """Request to create/update user profile."""
    cv_text: str = Field(..., description="Full CV/resume text")
    cover_letter_text: Optional[str] = Field(None, description="Cover letter text")
    homepage_url: Optional[str] = Field(None, description="Personal homepage URL")
    linkedin_url: Optional[str] = Field(None, description="LinkedIn profile URL")


class UserProfileResponse(BaseModel):
    """User profile response."""
    user_id: str
    cv_text: str
    cover_letter_text: Optional[str]
    homepage_url: Optional[str]
    linkedin_url: Optional[str]
    skills_extracted: List[str]
    experience_years: Optional[int]
    education_level: Optional[str]
    job_titles: List[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Job Analysis Schemas
# ============================================================================

class JobAnalysisRequest(BaseModel):
    """Request to analyze a job posting."""
    job_description: Optional[str] = Field(None, description="Full job description text")
    job_url: Optional[str] = Field(None, description="URL to job posting")
    required_skills: Optional[List[str]] = Field(None, description="List of required skills")
    provider: str = Field("grok", description="LLM provider for analysis")


# ============================================================================
# Search Result Schemas
# ============================================================================

class ChromaDBSearchResult(BaseModel):
    """ChromaDB search result."""
    search_time_ms: float
    total_matches: int
    results: List[Dict[str, Any]]
    relevance_scores: List[float]


class ElasticsearchSearchResult(BaseModel):
    """Elasticsearch search result."""
    search_time_ms: float
    total_matches: int
    max_score: float
    results: List[Dict[str, Any]]
    relevance_scores: List[float]


class PerformanceComparison(BaseModel):
    """Performance comparison metrics."""
    chromadb_time_ms: float
    elasticsearch_time_ms: float
    speedup_factor: float
    faster_system: str
    time_saved_ms: float
    percentage_difference: float


class SystemFeatures(BaseModel):
    """Features of a vector store system."""
    features: List[str]
    strengths: List[str]
    limitations: List[str]


class FeatureComparison(BaseModel):
    """Feature comparison between systems."""
    chromadb: SystemFeatures
    elasticsearch: SystemFeatures


# ============================================================================
# Advanced Features Schemas
# ============================================================================

class FuzzyMatch(BaseModel):
    """Fuzzy match result."""
    searched_skill: str
    matched_text: List[str]
    score: float


class SynonymMatch(BaseModel):
    """Synonym match result."""
    searched_skill: str
    score: float
    cv_skills: str


class SkillCluster(BaseModel):
    """Skill cluster from aggregations."""
    skill: str
    count: int


class Aggregations(BaseModel):
    """Elasticsearch aggregations result."""
    skill_clusters: List[Dict[str, Any]]
    avg_experience: Optional[float]
    education_breakdown: List[Dict[str, Any]]


class FuzzyMatchingDemo(BaseModel):
    """Fuzzy matching demonstration."""
    description: str
    example: str
    results: List[FuzzyMatch]
    benefit: str


class SynonymMatchingDemo(BaseModel):
    """Synonym matching demonstration."""
    description: str
    examples: List[str]
    results: List[SynonymMatch]
    benefit: str


class WeightedSearchDemo(BaseModel):
    """Weighted search demonstration."""
    description: str
    configuration: Dict[str, str]
    benefit: str


class HighlightingDemo(BaseModel):
    """Highlighting demonstration."""
    description: str
    benefit: str
    example: str


class AggregationsDemo(BaseModel):
    """Aggregations demonstration."""
    description: str
    results: Aggregations
    benefit: str


class AdvancedFeatures(BaseModel):
    """All advanced Elasticsearch features."""
    fuzzy_matching: FuzzyMatchingDemo
    synonym_matching: SynonymMatchingDemo
    weighted_search: WeightedSearchDemo
    highlighting: HighlightingDemo
    aggregations: AggregationsDemo


# ============================================================================
# Comparison Report Schemas
# ============================================================================

class ComparisonSummary(BaseModel):
    """Summary of comparison."""
    chromadb_search_time_ms: float
    elasticsearch_search_time_ms: float
    performance_winner: str
    speedup_factor: float


class Recommendation(BaseModel):
    """Recommendation based on comparison."""
    performance: str
    features: str
    use_case_chromadb: str
    use_case_elasticsearch: str
    overall: str


class SearchComparison(BaseModel):
    """Search comparison results."""
    chromadb: ChromaDBSearchResult
    elasticsearch: ElasticsearchSearchResult
    performance_comparison: PerformanceComparison
    feature_comparison: FeatureComparison


class ComparisonReport(BaseModel):
    """Full comparison report."""
    summary: ComparisonSummary
    search_comparison: SearchComparison
    advanced_features: AdvancedFeatures
    recommendation: Recommendation


# ============================================================================
# Job Analysis Response Schema
# ============================================================================

class JobAnalysisResponse(BaseModel):
    """Response from job analysis."""
    id: int
    user_id: str
    job_description: str
    job_url: Optional[str]

    # ChromaDB Results
    chromadb_results: Dict[str, Any]
    chromadb_search_time_ms: Optional[float]
    chromadb_matches_count: Optional[int]
    chromadb_relevance_score: Optional[float]

    # Elasticsearch Results
    elasticsearch_results: Dict[str, Any]
    elasticsearch_search_time_ms: Optional[float]
    elasticsearch_matches_count: Optional[int]
    elasticsearch_relevance_score: Optional[float]

    # Advanced Features
    fuzzy_matches: List[Dict[str, Any]]
    synonym_matches: List[Dict[str, Any]]
    skill_clusters: Dict[str, Any]

    # Comparison
    performance_comparison: Dict[str, Any]
    feature_comparison: Dict[str, Any]

    # LLM Job Analysis (for frontend display)
    job_analysis: Dict[str, Any]
    fit_score: Dict[str, Any]
    success_probability: Optional[Dict[str, Any]] = None  # Deprecated, kept for backward compatibility
    interview_success: Optional[Dict[str, Any]] = None  # New field replacing success_probability

    created_at: datetime
    provider: Optional[str]

    class Config:
        from_attributes = True


# ============================================================================
# Simple Response Schemas
# ============================================================================

class StatusResponse(BaseModel):
    """Simple status response."""
    status: str
    message: str


class ErrorResponse(BaseModel):
    """Error response."""
    error: str
    detail: Optional[str] = None
