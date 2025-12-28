"""Job Assistant Database Models."""
from datetime import datetime
from sqlalchemy import String, Text, Integer, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from backend.database import Base


class UserProfile(Base):
    """User profile for job applications."""

    __tablename__ = "job_assistant_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)

    # Profile Data (JSONB)
    personal: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    summary: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    experience: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    education: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    certifications: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    skills: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    preferences: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    unique_angles: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)

    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class JobApplication(Base):
    """Job Application record with analysis and documents."""

    __tablename__ = "job_applications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String, index=True, nullable=False)

    # Job Information
    company: Mapped[str] = mapped_column(String, index=True, nullable=False)
    role: Mapped[str] = mapped_column(String, nullable=False)
    location: Mapped[str | None] = mapped_column(String, nullable=True)
    remote_policy: Mapped[str | None] = mapped_column(String, nullable=True)
    seniority: Mapped[str | None] = mapped_column(String, nullable=True)
    job_url: Mapped[str | None] = mapped_column(String, nullable=True)
    job_description: Mapped[str] = mapped_column(Text, nullable=False)

    # Analysis Results (JSONB)
    job_analysis: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    fit_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    fit_breakdown: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    matched_skills: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    missing_skills: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)

    # Probability Calculation
    success_probability: Mapped[int | None] = mapped_column(Integer, nullable=True)
    probability_factors: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    recommendation: Mapped[str | None] = mapped_column(String, nullable=True)

    # Salary
    salary_min: Mapped[int | None] = mapped_column(Integer, nullable=True)
    salary_max: Mapped[int | None] = mapped_column(Integer, nullable=True)
    salary_currency: Mapped[str | None] = mapped_column(String, default="EUR", nullable=True)

    # Flags
    green_flags: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    red_flags: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)

    # Generated Documents
    cover_letter_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    cv_customization: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    cover_letter_path: Mapped[str | None] = mapped_column(String, nullable=True)
    cv_path: Mapped[str | None] = mapped_column(String, nullable=True)

    # Documents storage (PDFs and other files as Base64 in JSONB)
    # Format: {"cover_letter_pdf": "base64...", "cv_pdf": "base64...", "additional": [{"name": "...", "data": "base64..."}]}
    documents: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)

    # Application Status
    status: Mapped[str] = mapped_column(String, default="analyzed", nullable=False)
    applied_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    response_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Profile snapshot
    profile_snapshot: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
