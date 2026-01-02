"""Elasticsearch Showcase Database Models."""
from datetime import datetime
from sqlalchemy import String, Text, Integer, DateTime, Float
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from backend.database import Base


class UserElasticProfile(Base):
    """User profile for Elasticsearch showcase - persistent CV and documents."""

    __tablename__ = "elastic_user_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)

    # User Documents (persistent until updated)
    cv_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    cover_letter_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    homepage_url: Mapped[str | None] = mapped_column(String, nullable=True)
    linkedin_url: Mapped[str | None] = mapped_column(String, nullable=True)

    # Extracted Information (processed from CV)
    skills_extracted: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    experience_years: Mapped[int | None] = mapped_column(Integer, nullable=True)
    education_level: Mapped[str | None] = mapped_column(String, nullable=True)
    job_titles: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)

    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class ElasticJobAnalysis(Base):
    """Job analysis results comparing ChromaDB vs Elasticsearch."""

    __tablename__ = "elastic_job_analyses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String, index=True, nullable=False)

    # Job Information
    job_description: Mapped[str] = mapped_column(Text, nullable=False)
    job_url: Mapped[str | None] = mapped_column(String, nullable=True)

    # ChromaDB Results (from existing implementation)
    chromadb_results: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    chromadb_search_time_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    chromadb_matches_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    chromadb_relevance_score: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Elasticsearch Results
    elasticsearch_results: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    elasticsearch_search_time_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    elasticsearch_matches_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    elasticsearch_relevance_score: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Advanced Elasticsearch Features
    fuzzy_matches: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    synonym_matches: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    skill_clusters: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)

    # Comparison Metrics
    performance_comparison: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    feature_comparison: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)

    # LLM Job Analysis Results (for frontend display)
    job_analysis: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    fit_score: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    success_probability: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)  # Deprecated
    interview_success: Mapped[dict | None] = mapped_column(JSONB, nullable=True)  # New field

    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    provider: Mapped[str | None] = mapped_column(String, default="grok", nullable=True)


class ComparisonResult(Base):
    """Stores RAG comparison results with LLM judge evaluation."""

    __tablename__ = "rag_comparison_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String, index=True, nullable=False)

    # Query Information
    question: Mapped[str] = mapped_column(Text, nullable=False)

    # pgvector Results
    pgvector_answer: Mapped[str] = mapped_column(Text, nullable=False)
    pgvector_sources: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    pgvector_latency_ms: Mapped[float] = mapped_column(Float, nullable=False)

    # Elasticsearch Results
    elasticsearch_answer: Mapped[str] = mapped_column(Text, nullable=False)
    elasticsearch_sources: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    elasticsearch_latency_ms: Mapped[float] = mapped_column(Float, nullable=False)

    # LLM Judge Evaluation
    llm_evaluation: Mapped[dict] = mapped_column(JSONB, nullable=False)  # Full evaluation response
    pgvector_score: Mapped[float] = mapped_column(Float, nullable=False)
    elasticsearch_score: Mapped[float] = mapped_column(Float, nullable=False)
    winner: Mapped[str] = mapped_column(String, nullable=False)  # "pgvector", "elasticsearch", or "tie"
    reasoning: Mapped[str] = mapped_column(Text, nullable=False)

    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    provider: Mapped[str] = mapped_column(String, default="grok", nullable=False)
