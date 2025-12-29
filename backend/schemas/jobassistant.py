"""Job Assistant API Schemas."""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, HttpUrl, Field


# ============================================================================
# Profile Schemas
# ============================================================================

class PersonalInfo(BaseModel):
    """Personal information."""
    name: str
    title: str
    email: str
    phone: str
    location: str
    linkedin: Optional[str] = None
    github: Optional[str] = None
    portfolio: Optional[str] = None
    available_for: List[str] = []


class Summary(BaseModel):
    """Professional summary."""
    years_experience: int
    core_identity: str
    unique_value: str


class Experience(BaseModel):
    """Work experience entry."""
    title: str
    company: str
    period: str
    duration_years: float
    type: str  # current, parallel, primary, past
    highlights: List[str]
    skills_used: List[str]
    relevance_tags: List[str]
    clients: Optional[List[str]] = None


class Education(BaseModel):
    """Education information."""
    degree: str
    university: str
    country: str
    focus: List[str]
    thesis: Optional[str] = None


class Certification(BaseModel):
    """Certification entry."""
    name: str
    issuer: str
    relevance: List[str]


class Skills(BaseModel):
    """Skills categorized."""
    management: List[str] = []
    technical: List[str] = []
    ai_ml: List[str] = []
    development: List[str] = []
    tools: List[str] = []
    languages: Dict[str, str] = {}


class Preferences(BaseModel):
    """Job preferences."""
    ideal_roles: List[str]
    avoid_roles: List[str]
    min_salary_eur: int
    target_salary_eur: int
    willing_to_travel: str
    remote_preference: str


class UniqueAngles(BaseModel):
    """Unique selling points."""
    kit_alumni: bool = False
    german_native: bool = False
    spain_based: bool = False
    ai_hands_on: bool = False
    enterprise_background: bool = False
    turnaround_specialist: bool = False


class UserProfileCreate(BaseModel):
    """Create/Update user profile."""
    personal: PersonalInfo
    summary: Summary
    experience: List[Experience]
    education: Education
    certifications: List[Certification]
    skills: Skills
    preferences: Preferences
    unique_angles: UniqueAngles


class UserProfileResponse(BaseModel):
    """User profile response - uses dict/list for JSONB fields."""
    id: int
    user_id: str
    personal: dict  # JSONB field - keep as dict
    summary: dict  # JSONB field - keep as dict
    experience: list  # JSONB field - keep as list
    education: dict  # JSONB field - keep as dict
    certifications: list  # JSONB field - keep as list
    skills: dict  # JSONB field - keep as dict
    preferences: dict  # JSONB field - keep as dict
    unique_angles: dict  # JSONB field - keep as dict
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Job Analysis Schemas
# ============================================================================

class JobAnalysisRequest(BaseModel):
    """Request to analyze a job."""
    job_description: Optional[str] = None
    job_url: Optional[HttpUrl] = None
    cv_text: Optional[str] = Field(None, description="User's CV/Resume text for analysis")
    cover_letter_text: Optional[str] = Field(None, description="User's existing cover letter text for analysis")
    additional_context: Optional[str] = Field(None, description="Additional context or notes for the analysis")
    homepage_url: Optional[str] = Field(None, description="User's personal homepage URL for additional context")
    linkedin_url: Optional[str] = Field(None, description="User's LinkedIn profile URL for additional context")
    generate_documents: bool = False

    class Config:
        json_schema_extra = {
            "example": {
                "job_description": "We are looking for a Senior Program Manager...",
                "cv_text": "John Doe - Senior Program Manager with 10 years experience...",
                "homepage_url": "https://www.johndoe.com",
                "linkedin_url": "https://www.linkedin.com/in/johndoe",
                "generate_documents": True
            }
        }


class Requirements(BaseModel):
    """Job requirements."""
    must_have: List[str]
    nice_to_have: List[str]
    years_experience: Dict[str, int]  # {"min": 5, "max": 10}
    education: str
    languages: List[str]
    certifications: List[str]


class RoleType(BaseModel):
    """Role type classification."""
    is_sales: bool = False
    is_delivery: bool = False
    is_technical: bool = False
    is_management: bool = False
    is_consulting: bool = False
    requires_coding: bool = False
    is_client_facing: bool = False
    requires_quota: bool = False


class CompanyInfo(BaseModel):
    """Company information."""
    size: str  # Startup/SMB/Enterprise
    industry: str
    culture_hints: List[str]


class JobAnalysisResult(BaseModel):
    """Structured job analysis result."""
    company: str
    role: str
    location: str
    remote_policy: str
    seniority: str
    salary_range: Dict[str, Any]  # {"min": 70000, "max": 90000, "currency": "EUR"}
    requirements: Requirements
    responsibilities: List[str]
    role_type: RoleType
    keywords: List[str]
    company_info: CompanyInfo
    red_flags: List[str]
    green_flags: List[str]


class FitScoreDetail(BaseModel):
    """Detailed comparison for a fit score category."""
    score: int  # 0-100
    candidate_value: str
    required_value: str
    comparison: str  # e.g., "20+ years vs. 10+ years required"


class FitScoreBreakdown(BaseModel):
    """Detailed fit score breakdown."""
    experience_match: int
    skills_match: int
    education_match: int
    location_match: int
    salary_match: int
    culture_match: int
    role_type_match: int

    # Detailed comparisons
    experience_detail: Optional[FitScoreDetail] = None
    skills_detail: Optional[FitScoreDetail] = None
    education_detail: Optional[FitScoreDetail] = None
    location_detail: Optional[FitScoreDetail] = None
    salary_detail: Optional[FitScoreDetail] = None
    culture_detail: Optional[FitScoreDetail] = None
    role_type_detail: Optional[FitScoreDetail] = None


class FitScore(BaseModel):
    """Fit score calculation."""
    total: int  # 0-100
    breakdown: FitScoreBreakdown
    matched_skills: List[str]
    missing_skills: List[str]


class ProbabilityFactor(BaseModel):
    """Factor affecting success probability."""
    factor: str
    impact: float


class SuccessProbability(BaseModel):
    """Success probability calculation."""
    probability: int  # 0-100
    factors: List[ProbabilityFactor]
    recommendation: str


class JobAnalysisResponse(BaseModel):
    """Complete job analysis response."""
    application_id: int
    job_analysis: JobAnalysisResult
    fit_score: FitScore
    success_probability: SuccessProbability
    cover_letter_text: Optional[str] = None
    cv_customization: Optional[Dict[str, Any]] = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Document Generation Schemas
# ============================================================================

class GenerateDocumentsRequest(BaseModel):
    """Request to generate documents for an application."""
    application_id: int


class GenerateDocumentsResponse(BaseModel):
    """Document generation response."""
    application_id: int
    cover_letter_text: str
    cv_customization: Dict[str, Any]
    documents_generated: bool = True


# ============================================================================
# Application Management Schemas
# ============================================================================

class ApplicationUpdateRequest(BaseModel):
    """Update application status."""
    status: Optional[str] = None  # analyzed, documents_generated, applied, interview, offer, rejected
    applied_date: Optional[datetime] = None
    response_date: Optional[datetime] = None
    notes: Optional[str] = None


class ApplicationListResponse(BaseModel):
    """Job application summary for list."""
    id: int
    company: str
    role: str
    fit_score: Optional[int]
    success_probability: Optional[int]
    status: str
    created_at: datetime
    applied_date: Optional[datetime] = None

    class Config:
        from_attributes = True


class ApplicationStatsResponse(BaseModel):
    """Application statistics."""
    total: int
    avg_fit_score: int
    avg_probability: int
    by_status: Dict[str, int]
    by_month: Dict[str, int]
    top_companies: List[Dict[str, Any]]
