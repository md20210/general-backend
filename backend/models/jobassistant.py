"""Job Assistant Database Models."""
from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel
from sqlalchemy import Column, Text
from sqlalchemy.dialects.postgresql import JSON


class JobApplication(SQLModel, table=True):
    """Job Application record with analysis and documents."""

    __tablename__ = "job_applications"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)  # Links to user

    # Job Information
    company: str = Field(index=True)
    role: str
    location: Optional[str] = None
    remote_policy: Optional[str] = None  # Remote/Hybrid/Office
    seniority: Optional[str] = None
    job_url: Optional[str] = None
    job_description: str = Field(sa_column=Column(Text))

    # Analysis Results (JSON)
    job_analysis: dict = Field(default={}, sa_column=Column(JSON))
    fit_score: Optional[int] = None  # 0-100
    fit_breakdown: dict = Field(default={}, sa_column=Column(JSON))
    matched_skills: list = Field(default=[], sa_column=Column(JSON))
    missing_skills: list = Field(default=[], sa_column=Column(JSON))

    # Probability Calculation
    success_probability: Optional[int] = None  # 0-100
    probability_factors: list = Field(default=[], sa_column=Column(JSON))
    recommendation: Optional[str] = None

    # Salary
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    salary_currency: Optional[str] = "EUR"

    # Flags
    green_flags: list = Field(default=[], sa_column=Column(JSON))
    red_flags: list = Field(default=[], sa_column=Column(JSON))

    # Generated Documents (paths or base64)
    cover_letter_text: Optional[str] = Field(default=None, sa_column=Column(Text))
    cv_customization: dict = Field(default={}, sa_column=Column(JSON))
    cover_letter_path: Optional[str] = None
    cv_path: Optional[str] = None

    # Application Status
    status: str = Field(default="analyzed")  # analyzed, documents_generated, applied, interview, offer, rejected
    applied_date: Optional[datetime] = None
    response_date: Optional[datetime] = None
    notes: Optional[str] = Field(default=None, sa_column=Column(Text))

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Profile used for this application
    profile_snapshot: dict = Field(default={}, sa_column=Column(JSON))


class UserProfile(SQLModel, table=True):
    """User profile for job applications."""

    __tablename__ = "job_assistant_profiles"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(unique=True, index=True)

    # Profile Data (JSON structure from profile.json)
    personal: dict = Field(default={}, sa_column=Column(JSON))
    summary: dict = Field(default={}, sa_column=Column(JSON))
    experience: list = Field(default=[], sa_column=Column(JSON))
    education: dict = Field(default={}, sa_column=Column(JSON))
    certifications: list = Field(default=[], sa_column=Column(JSON))
    skills: dict = Field(default={}, sa_column=Column(JSON))
    preferences: dict = Field(default={}, sa_column=Column(JSON))
    unique_angles: dict = Field(default={}, sa_column=Column(JSON))

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
