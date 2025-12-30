"""Elasticsearch Showcase API Router."""
from datetime import datetime
from typing import List, Optional
import fastapi
from fastapi import APIRouter, Depends, HTTPException, Query, File, UploadFile
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database import get_async_session
from backend.auth.dependencies import current_active_user
from backend.models.user import User
from backend.models.elasticsearch_showcase import UserElasticProfile, ElasticJobAnalysis
from backend.schemas.elasticsearch_showcase import (
    UserProfileRequest,
    UserProfileResponse,
    JobAnalysisRequest,
    JobAnalysisResponse,
    ComparisonReport,
    AdvancedFeatures,
    StatusResponse,
    ErrorResponse,
)
from backend.services.elasticsearch_service import ElasticsearchService
from backend.services.elasticsearch_comparison_service import ElasticsearchComparisonService
from backend.services.llm_gateway import LLMGateway
import logging
import json
import re

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/elasticsearch",
    tags=["Elasticsearch Showcase"],
)

# Initialize services
es_service = ElasticsearchService()
comparison_service = ElasticsearchComparisonService()
llm_gateway = LLMGateway()


# ============================================================================
# Helper Functions
# ============================================================================

def extract_skills_from_cv(cv_text: str) -> List[str]:
    """Extract skills from CV text using simple keyword matching."""
    # Common skills to look for (case-insensitive)
    common_skills = [
        "Python", "JavaScript", "TypeScript", "Java", "C++", "C#", "Go", "Rust",
        "React", "Vue", "Angular", "Node.js", "Django", "Flask", "FastAPI",
        "Docker", "Kubernetes", "AWS", "Azure", "GCP",
        "SQL", "PostgreSQL", "MySQL", "MongoDB", "Redis",
        "Git", "CI/CD", "Jenkins", "GitHub Actions",
        "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch",
        "REST API", "GraphQL", "Microservices",
        "Agile", "Scrum", "DevOps",
        "Linux", "Bash", "Shell"
    ]

    found_skills = []
    cv_lower = cv_text.lower()

    for skill in common_skills:
        if skill.lower() in cv_lower:
            found_skills.append(skill)

    return found_skills


def extract_experience_years(cv_text: str) -> Optional[int]:
    """Extract years of experience from CV text."""
    # Look for patterns like "X years", "X+ years", "X-Y years"
    patterns = [
        r'(\d+)\+?\s*years?\s+(?:of\s+)?experience',
        r'experience\s*:\s*(\d+)\+?\s*years?',
        r'(\d+)\+?\s*years?\s+in\s+(?:the\s+)?industry'
    ]

    for pattern in patterns:
        match = re.search(pattern, cv_text.lower())
        if match:
            return int(match.group(1))

    return None


def extract_education_level(cv_text: str) -> Optional[str]:
    """Extract education level from CV text."""
    cv_lower = cv_text.lower()

    if "phd" in cv_lower or "ph.d" in cv_lower or "doctorate" in cv_lower:
        return "PhD"
    elif "master" in cv_lower or "msc" in cv_lower or "m.sc" in cv_lower:
        return "Master"
    elif "bachelor" in cv_lower or "bsc" in cv_lower or "b.sc" in cv_lower:
        return "Bachelor"
    elif "associate" in cv_lower:
        return "Associate"

    return None


def extract_job_titles(cv_text: str) -> List[str]:
    """Extract job titles from CV text."""
    # Common job title patterns
    title_keywords = [
        "Software Engineer", "Developer", "Programmer",
        "Senior Engineer", "Lead Engineer", "Principal Engineer",
        "Data Scientist", "Data Engineer", "ML Engineer",
        "DevOps Engineer", "Site Reliability Engineer",
        "Full Stack Developer", "Frontend Developer", "Backend Developer",
        "Engineering Manager", "Technical Lead", "Team Lead",
        "Architect", "Solutions Architect", "System Architect"
    ]

    found_titles = []
    cv_lower = cv_text.lower()

    for title in title_keywords:
        if title.lower() in cv_lower:
            found_titles.append(title)

    return found_titles[:5]  # Return max 5 titles


async def extract_skills_with_llm(cv_text: str, provider: str = "grok") -> List[str]:
    """Extract skills from CV using LLM for better accuracy."""
    prompt = f"""Extract all technical and professional skills from this CV.
Return ONLY a JSON array of strings, no explanations.

CV:
{cv_text[:2000]}

Return format: ["skill1", "skill2", "skill3", ...]
"""

    try:
        response_dict = llm_gateway.generate(prompt=prompt, provider=provider)
        response = response_dict.get("response", "")

        # Extract JSON from response
        json_match = re.search(r'\[.*\]', response, re.DOTALL)
        if json_match:
            skills = json.loads(json_match.group(0))
            return skills[:50]  # Max 50 skills
        else:
            logger.warning("LLM didn't return valid JSON for skills extraction")
            return extract_skills_from_cv(cv_text)
    except Exception as e:
        logger.error(f"Error extracting skills with LLM: {e}")
        return extract_skills_from_cv(cv_text)


async def analyze_job_with_llm(job_description: str, cv_text: str, provider: str = "grok") -> dict:
    """Analyze job description and compare with CV using LLM."""
    prompt = f"""Analyze this job description and compare it with the candidate's CV.
Provide a detailed analysis in JSON format.

JOB DESCRIPTION:
{job_description}

CANDIDATE CV:
{cv_text}

Return ONLY valid JSON in this exact format:
{{
  "job_analysis": {{
    "company": "Company name or Unknown",
    "role": "Job title",
    "location": "Location or Remote",
    "remote_policy": "Remote/Hybrid/On-site",
    "seniority": "Junior/Mid/Senior/Lead",
    "salary_range": {{"min": null, "max": null, "currency": "EUR"}},
    "requirements": {{
      "must_have": ["skill1", "skill2"],
      "nice_to_have": ["skill3"],
      "years_experience": {{"min": 0, "max": null}},
      "education": "Education requirement",
      "languages": ["English"],
      "certifications": []
    }},
    "responsibilities": ["responsibility1", "responsibility2"],
    "keywords": ["keyword1", "keyword2"],
    "red_flags": ["any concerning aspects"],
    "green_flags": ["positive aspects"]
  }},
  "fit_score": {{
    "total": 85,
    "breakdown": {{
      "experience_match": 90,
      "skills_match": 85,
      "education_match": 100,
      "location_match": 80,
      "salary_match": 75,
      "culture_match": 80,
      "role_type_match": 90
    }},
    "matched_skills": ["Python", "FastAPI"],
    "missing_skills": ["Skill candidate doesn't have"]
  }},
  "success_probability": {{
    "probability": 75,
    "factors": [
      {{"factor": "Strong technical skills match", "impact": 15}},
      {{"factor": "Limited experience with X", "impact": -10}}
    ],
    "recommendation": "Apply - good fit with areas to highlight"
  }}
}}
"""

    try:
        response_dict = llm_gateway.generate(prompt=prompt, provider=provider)
        response = response_dict.get("response", "")

        # Extract JSON from response
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            analysis = json.loads(json_match.group(0))
            return analysis
        else:
            logger.error("LLM didn't return valid JSON for job analysis")
            # Return default structure
            return {
                "job_analysis": {
                    "company": "Unknown",
                    "role": "Position",
                    "location": "Unknown",
                    "remote_policy": "Unknown",
                    "seniority": "Unknown",
                    "salary_range": {"min": None, "max": None, "currency": "EUR"},
                    "requirements": {
                        "must_have": [],
                        "nice_to_have": [],
                        "years_experience": {"min": 0, "max": None},
                        "education": "Not specified",
                        "languages": [],
                        "certifications": []
                    },
                    "responsibilities": [],
                    "keywords": [],
                    "red_flags": [],
                    "green_flags": []
                },
                "fit_score": {
                    "total": 0,
                    "breakdown": {
                        "experience_match": 0,
                        "skills_match": 0,
                        "education_match": 0,
                        "location_match": 0,
                        "salary_match": 0,
                        "culture_match": 0,
                        "role_type_match": 0
                    },
                    "matched_skills": [],
                    "missing_skills": []
                },
                "success_probability": {
                    "probability": 0,
                    "factors": [],
                    "recommendation": "Unable to analyze - please try again"
                }
            }
    except Exception as e:
        logger.error(f"Error analyzing job with LLM: {e}")
        raise


# ============================================================================
# Profile Endpoints
# ============================================================================

@router.post("/profile", response_model=UserProfileResponse)
async def create_or_update_profile(
    profile_data: UserProfileRequest,
    provider: str = Query("grok", description="LLM provider for skill extraction"),
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    """
    Create or update user profile with CV and documents.

    This endpoint:
    1. Stores CV, cover letter, and URLs in PostgreSQL
    2. Extracts skills, experience, education using LLM
    3. Indexes data in Elasticsearch for fast searching
    """
    try:
        # Extract information from CV using LLM
        skills = await extract_skills_with_llm(profile_data.cv_text, provider)
        experience_years = extract_experience_years(profile_data.cv_text)
        education_level = extract_education_level(profile_data.cv_text)
        job_titles = extract_job_titles(profile_data.cv_text)

        # Check if profile exists
        statement = select(UserElasticProfile).where(UserElasticProfile.user_id == str(user.id))
        result = await db.execute(statement)
        existing_profile = result.scalars().first()

        if existing_profile:
            # Update existing profile
            existing_profile.cv_text = profile_data.cv_text
            existing_profile.cover_letter_text = profile_data.cover_letter_text
            existing_profile.homepage_url = profile_data.homepage_url
            existing_profile.linkedin_url = profile_data.linkedin_url
            existing_profile.skills_extracted = skills
            existing_profile.experience_years = experience_years
            existing_profile.education_level = education_level
            existing_profile.job_titles = job_titles
            existing_profile.updated_at = datetime.utcnow()

            db.add(existing_profile)
            await db.commit()
            await db.refresh(existing_profile)
            profile = existing_profile
        else:
            # Create new profile
            new_profile = UserElasticProfile(
                user_id=str(user.id),
                cv_text=profile_data.cv_text,
                cover_letter_text=profile_data.cover_letter_text,
                homepage_url=profile_data.homepage_url,
                linkedin_url=profile_data.linkedin_url,
                skills_extracted=skills,
                experience_years=experience_years,
                education_level=education_level,
                job_titles=job_titles,
            )
            db.add(new_profile)
            await db.commit()
            await db.refresh(new_profile)
            profile = new_profile

        # Index in Elasticsearch
        await es_service.index_cv_data(
            user_id=str(user.id),
            cv_text=profile_data.cv_text,
            skills=skills,
            experience_years=experience_years,
            education_level=education_level,
            job_titles=job_titles,
            homepage_url=profile_data.homepage_url,
            linkedin_url=profile_data.linkedin_url
        )

        logger.info(f"Profile created/updated for user {user.id}")
        return profile

    except Exception as e:
        logger.error(f"Error creating/updating profile: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/profile", response_model=UserProfileResponse)
async def get_profile(
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    """Get user profile."""
    statement = select(UserElasticProfile).where(UserElasticProfile.user_id == str(user.id))
    result = await db.execute(statement)
    profile = result.scalars().first()

    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    return profile


# ============================================================================
# Job Analysis Endpoints
# ============================================================================

@router.post("/analyze", response_model=JobAnalysisResponse)
async def analyze_job(
    analysis_request: JobAnalysisRequest,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    """
    Analyze job posting and compare ChromaDB vs Elasticsearch.

    This endpoint:
    1. Runs search in both ChromaDB and Elasticsearch
    2. Compares performance metrics
    3. Demonstrates advanced Elasticsearch features
    4. Stores results in database
    """
    try:
        # Check if profile exists
        statement = select(UserElasticProfile).where(UserElasticProfile.user_id == str(user.id))
        result = await db.execute(statement)
        profile = result.scalars().first()

        if not profile:
            raise HTTPException(
                status_code=404,
                detail="Profile not found. Please create a profile first by uploading your CV."
            )

        # Perform LLM-based job analysis (with fallback to default values)
        logger.info(f"Starting LLM job analysis for user {user.id}")
        try:
            llm_analysis = await analyze_job_with_llm(
                job_description=analysis_request.job_description,
                cv_text=profile.cv_text,
                provider=analysis_request.provider or "grok"
            )
            logger.info(f"LLM job analysis completed for user {user.id}")
        except Exception as e:
            logger.error(f"LLM analysis failed, using default values: {e}")
            # Use default empty analysis if LLM fails
            llm_analysis = {
                "job_analysis": {
                    "company": "Unknown",
                    "role": "Position",
                    "location": "Unknown",
                    "remote_policy": "Unknown",
                    "seniority": "Unknown",
                    "salary_range": {"min": None, "max": None, "currency": "EUR"},
                    "requirements": {
                        "must_have": [],
                        "nice_to_have": [],
                        "years_experience": {"min": 0, "max": None},
                        "education": "Not specified",
                        "languages": [],
                        "certifications": []
                    },
                    "responsibilities": [],
                    "keywords": [],
                    "red_flags": [],
                    "green_flags": []
                },
                "fit_score": {
                    "total": 0,
                    "breakdown": {
                        "experience_match": 0,
                        "skills_match": 0,
                        "education_match": 0,
                        "location_match": 0,
                        "salary_match": 0,
                        "culture_match": 0,
                        "role_type_match": 0
                    },
                    "matched_skills": [],
                    "missing_skills": []
                },
                "success_probability": {
                    "probability": 0,
                    "factors": [],
                    "recommendation": "Unable to analyze - LLM service unavailable"
                }
            }

        # Run comparison (with fallback to empty results)
        try:
            comparison_results = await comparison_service.compare_search_performance(
                user_id=str(user.id),
                job_description=analysis_request.job_description,
                required_skills=analysis_request.required_skills or []
            )
        except Exception as e:
            logger.warning(f"Comparison service failed, using empty results: {e}")
            comparison_results = {
                "chromadb": {"results": [], "search_time_ms": 0, "total_matches": 0, "relevance_scores": []},
                "elasticsearch": {"results": [], "search_time_ms": 0, "total_matches": 0, "max_score": 0},
                "performance_comparison": {},
                "feature_comparison": {}
            }

        # Get advanced features demo (with fallback to empty results)
        try:
            advanced_features = await comparison_service.get_advanced_features_demo(
                user_id=str(user.id),
                required_skills=analysis_request.required_skills or []
            )
        except Exception as e:
            logger.warning(f"Advanced features demo failed, using empty results: {e}")
            advanced_features = {
                "fuzzy_matching": {"results": []},
                "synonym_matching": {"results": []},
                "aggregations": {"results": {}}
            }

        # Create analysis record
        analysis = ElasticJobAnalysis(
            user_id=str(user.id),
            job_description=analysis_request.job_description,
            job_url=analysis_request.job_url,
            chromadb_results=comparison_results["chromadb"].get("results", {}),
            chromadb_search_time_ms=comparison_results["chromadb"].get("search_time_ms"),
            chromadb_matches_count=comparison_results["chromadb"].get("total_matches"),
            chromadb_relevance_score=comparison_results["chromadb"].get("relevance_scores", [0])[0] if comparison_results["chromadb"].get("relevance_scores") else None,
            elasticsearch_results=comparison_results["elasticsearch"].get("results", {}),
            elasticsearch_search_time_ms=comparison_results["elasticsearch"].get("search_time_ms"),
            elasticsearch_matches_count=comparison_results["elasticsearch"].get("total_matches"),
            elasticsearch_relevance_score=comparison_results["elasticsearch"].get("max_score"),
            fuzzy_matches=advanced_features.get("fuzzy_matching", {}).get("results", []),
            synonym_matches=advanced_features.get("synonym_matching", {}).get("results", []),
            skill_clusters=advanced_features.get("aggregations", {}).get("results", {}),
            performance_comparison=comparison_results.get("performance_comparison", {}),
            feature_comparison=comparison_results.get("feature_comparison", {}),
            # LLM Analysis Results
            job_analysis=llm_analysis.get("job_analysis", {}),
            fit_score=llm_analysis.get("fit_score", {}),
            success_probability=llm_analysis.get("success_probability", {}),
            provider=analysis_request.provider
        )

        db.add(analysis)
        await db.commit()
        await db.refresh(analysis)

        logger.info(f"Job analysis completed for user {user.id}, analysis ID {analysis.id}")
        return analysis

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing job: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/comparison/{analysis_id}", response_model=JobAnalysisResponse)
async def get_comparison(
    analysis_id: int,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    """Get specific analysis/comparison results by ID."""
    statement = select(ElasticJobAnalysis).where(
        ElasticJobAnalysis.id == analysis_id,
        ElasticJobAnalysis.user_id == str(user.id)
    )
    result = await db.execute(statement)
    analysis = result.scalars().first()

    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")

    return analysis


@router.get("/comparisons", response_model=List[JobAnalysisResponse])
async def list_comparisons(
    limit: int = Query(10, ge=1, le=50),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    """List all comparison analyses for current user."""
    statement = select(ElasticJobAnalysis).where(
        ElasticJobAnalysis.user_id == str(user.id)
    ).order_by(ElasticJobAnalysis.created_at.desc()).limit(limit).offset(offset)

    result = await db.execute(statement)
    analyses = result.scalars().all()

    return analyses


@router.get("/advanced-features")
async def get_advanced_features(
    user: User = Depends(current_active_user),
):
    """
    Get demonstration of Elasticsearch advanced features.

    Shows:
    - Fuzzy matching (typo tolerance)
    - Synonym support
    - Multi-field weighted search
    - Aggregations and analytics
    - Highlighting
    """
    # Check if profile exists
    # For demo purposes, we'll use common tech skills
    demo_skills = ["Python", "JavaScript", "Docker", "Kubernetes", "Machine Learning"]

    try:
        advanced_features = await comparison_service.get_advanced_features_demo(
            user_id=str(user.id),
            required_skills=demo_skills
        )
        return advanced_features
    except Exception as e:
        logger.error(f"Error getting advanced features: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/debug/columns")
async def check_columns(db: AsyncSession = Depends(get_async_session)):
    """Debug endpoint to check if LLM analysis columns exist."""
    try:
        result = await db.execute(text("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'elastic_job_analyses'
            AND column_name IN ('job_analysis', 'fit_score', 'success_probability')
            ORDER BY column_name;
        """))
        columns = [row[0] for row in result]

        return {
            "table": "elastic_job_analyses",
            "columns_found": columns,
            "all_present": len(columns) == 3,
            "expected": ["fit_score", "job_analysis", "success_probability"]
        }
    except Exception as e:
        return {"error": str(e)}


@router.get("/health")
async def health_check():
    """Check Elasticsearch connection health."""
    try:
        # Try to ping Elasticsearch
        health = es_service.client.cluster.health()
        return {
            "status": "healthy",
            "elasticsearch": {
                "status": health["status"],
                "number_of_nodes": health["number_of_nodes"],
                "active_shards": health["active_shards"]
            }
        }
    except Exception as e:
        logger.error(f"Elasticsearch health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }


@router.post("/parse-doc")
async def parse_doc_file(file: UploadFile = File(...)):
    """
    Parse .doc file and extract text.

    This endpoint accepts old .doc format files and attempts to extract text.
    Note: .doc is a legacy binary format - .docx is preferred.
    """
    try:
        import olefile
        import io

        # Read file contents
        file_content = await file.read()

        # Try to parse .doc file using olefile
        ole = olefile.OleFileIO(io.BytesIO(file_content))

        # Try to find WordDocument stream
        if ole.exists('WordDocument'):
            word_stream = ole.openstream('WordDocument')
            data = word_stream.read()

            # Extract text (very basic extraction - .doc format is complex)
            # This will get some text but may not be perfect
            text = data.decode('latin-1', errors='ignore')

            # Clean up non-printable characters
            import string
            printable = set(string.printable)
            text = ''.join(filter(lambda x: x in printable, text))

            ole.close()

            if text and len(text) > 10:
                return {"text": text, "success": True}
            else:
                raise ValueError("Could not extract meaningful text from .doc file")
        else:
            raise ValueError(".doc file structure not recognized")

    except Exception as e:
        logger.error(f"Error parsing .doc file: {e}")
        raise HTTPException(
            status_code=400,
            detail=f".doc file parsing failed: {str(e)}. Please save as .docx or copy/paste the text instead."
        )


@router.get("/fetch-url")
async def fetch_url_proxy(url: str = Query(..., description="URL to fetch")):
    """
    Proxy endpoint to fetch content from a URL.

    This bypasses CORS restrictions by fetching the URL from the backend.
    Used for loading job descriptions and CVs from external URLs.
    """
    try:
        import httpx

        # Validate URL
        if not url or not url.startswith(('http://', 'https://')):
            raise HTTPException(
                status_code=400,
                detail="Invalid URL. Must start with http:// or https://"
            )

        # Fetch the URL with timeout
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            response = await client.get(url)
            response.raise_for_status()

            # Return the text content
            return {"text": response.text, "success": True}

    except httpx.HTTPError as e:
        logger.error(f"Error fetching URL {url}: {e}")
        raise HTTPException(
            status_code=400,
            detail=f"Failed to fetch URL: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error fetching URL {url}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch URL: {str(e)}"
        )
