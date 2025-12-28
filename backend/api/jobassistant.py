"""Job Assistant API Router."""
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database import get_async_session
from backend.auth.dependencies import current_active_user
from backend.models.user import User
from backend.models.jobassistant import JobApplication, UserProfile
from backend.schemas.jobassistant import (
    UserProfileCreate,
    UserProfileResponse,
    JobAnalysisRequest,
    JobAnalysisResponse,
    GenerateDocumentsRequest,
    GenerateDocumentsResponse,
    ApplicationUpdateRequest,
    ApplicationListResponse,
    ApplicationStatsResponse,
)
from backend.services.jobassistant_service import JobAssistantService
from backend.services.document_processor import document_processor
from backend.config import settings
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/jobassistant",
    tags=["Job Assistant"],
)

service = JobAssistantService()


# ============================================================================
# Debug Endpoint
# ============================================================================


@router.get("/debug/config")
async def debug_config(user: User = Depends(current_active_user)):
    """Debug endpoint to check LLM API configuration."""
    return {
        "grok_api_key_configured": bool(settings.GROK_API_KEY),
        "grok_api_key_length": len(settings.GROK_API_KEY) if settings.GROK_API_KEY else 0,
        "anthropic_api_key_configured": bool(settings.ANTHROPIC_API_KEY),
        "anthropic_api_key_length": len(settings.ANTHROPIC_API_KEY) if settings.ANTHROPIC_API_KEY else 0,
        "ollama_base_url": settings.OLLAMA_BASE_URL,
    }


# ============================================================================
# Profile Endpoints
# ============================================================================


@router.post("/profile", response_model=UserProfileResponse)
async def create_or_update_profile(
    profile_data: UserProfileCreate,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    """Create or update user profile."""
    # Check if profile exists
    statement = select(UserProfile).where(UserProfile.user_id == str(user.id))
    result = await db.execute(statement)
    existing_profile = result.scalars().first()

    if existing_profile:
        # Update existing
        existing_profile.personal = profile_data.personal.model_dump()
        existing_profile.summary = profile_data.summary.model_dump()
        existing_profile.experience = [exp.model_dump() for exp in profile_data.experience]
        existing_profile.education = profile_data.education.model_dump()
        existing_profile.certifications = [cert.model_dump() for cert in profile_data.certifications]
        existing_profile.skills = profile_data.skills.model_dump()
        existing_profile.preferences = profile_data.preferences.model_dump()
        existing_profile.unique_angles = profile_data.unique_angles.model_dump()
        existing_profile.updated_at = datetime.utcnow()
        db.add(existing_profile)
        await db.commit()
        await db.refresh(existing_profile)
        return existing_profile
    else:
        # Create new
        new_profile = UserProfile(
            user_id=str(user.id),
            personal=profile_data.personal.model_dump(),
            summary=profile_data.summary.model_dump(),
            experience=[exp.model_dump() for exp in profile_data.experience],
            education=profile_data.education.model_dump(),
            certifications=[cert.model_dump() for cert in profile_data.certifications],
            skills=profile_data.skills.model_dump(),
            preferences=profile_data.preferences.model_dump(),
            unique_angles=profile_data.unique_angles.model_dump(),
        )
        db.add(new_profile)
        await db.commit()
        await db.refresh(new_profile)
        return new_profile


@router.get("/profile", response_model=UserProfileResponse)
async def get_profile(
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    """Get user profile."""
    statement = select(UserProfile).where(UserProfile.user_id == str(user.id))
    result = await db.execute(statement)
    profile = result.scalars().first()

    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found. Please create one first.")

    return profile


# ============================================================================
# Job Analysis Endpoints
# ============================================================================


@router.post("/analyze", response_model=JobAnalysisResponse)
async def analyze_job(
    request: JobAnalysisRequest,
    provider: str = Query("anthropic", description="LLM provider: anthropic, grok, ollama"),
    model: Optional[str] = Query(None, description="Specific model to use"),
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    """
    Analyze a job posting and calculate fit score.

    Returns complete analysis including fit score and success probability.
    Optionally generates cover letter and CV customization if requested.

    NOTE: Uses ONLY uploaded data (CV, URLs, context) - NOT the stored profile.
    """
    # Get job description
    if not request.job_description and not request.job_url:
        raise HTTPException(
            status_code=400,
            detail="Either job_description or job_url must be provided",
        )

    job_description = request.job_description
    if request.job_url and not job_description:
        # TODO: Implement web scraping
        raise HTTPException(
            status_code=501,
            detail="URL scraping not yet implemented. Please provide job_description text.",
        )

    try:
        # Build additional context from URLs
        context_parts = []
        if request.additional_context:
            context_parts.append(request.additional_context)

        # Scrape homepage if provided
        if request.homepage_url:
            try:
                logger.info(f"Scraping homepage: {request.homepage_url}")
                homepage_data = document_processor.scrape_website(request.homepage_url, max_length=5000)
                context_parts.append(f"\n\n=== Personal Homepage ===\n{homepage_data['content'][:5000]}")
            except Exception as e:
                logger.warning(f"Failed to scrape homepage: {str(e)}")

        # Scrape LinkedIn if provided
        if request.linkedin_url:
            try:
                logger.info(f"Scraping LinkedIn: {request.linkedin_url}")
                linkedin_data = document_processor.scrape_website(request.linkedin_url, max_length=5000)
                context_parts.append(f"\n\n=== LinkedIn Profile ===\n{linkedin_data['content'][:5000]}")
            except Exception as e:
                logger.warning(f"Failed to scrape LinkedIn: {str(e)}")

        full_context = "\n".join(context_parts) if context_parts else None

        # 1. Analyze job
        logger.info(f"Analyzing job for user {user.email}")
        logger.info(f"Provider selected: {provider}, Model: {model}")
        logger.info(f"GROK API key configured: {bool(settings.GROK_API_KEY)}, length: {len(settings.GROK_API_KEY)}")
        logger.info(f"Anthropic API key configured: {bool(settings.ANTHROPIC_API_KEY)}, length: {len(settings.ANTHROPIC_API_KEY)}")

        job_analysis = await service.analyze_job(
            job_description=job_description,
            additional_context=full_context,
            provider=provider,
            model=model,
        )

        # 2. Calculate fit score (using only CV text, no profile)
        logger.info("Calculating fit score from uploaded data")
        fit_score = service.calculate_fit_score_from_cv(
            job_analysis=job_analysis,
            cv_text=request.cv_text or "",
        )

        # 3. Calculate probability
        logger.info("Calculating success probability")
        probability = service.calculate_probability_simple(
            fit_score=fit_score,
            job_analysis=job_analysis,
        )

        # 4. Generate documents if requested
        cover_letter_text = None
        cv_customization = None
        status = "analyzed"

        if request.generate_documents:
            logger.info("Generating cover letter from uploaded data")
            cover_letter_text = await service.generate_cover_letter_from_cv(
                job_analysis=job_analysis,
                cv_text=request.cv_text or "",
                fit_score=fit_score,
                existing_cover_letter=request.cover_letter_text,
                provider=provider,
                model=model,
            )

            logger.info("Customizing CV")
            cv_customization = await service.customize_cv(
                job_analysis=job_analysis,
                profile=None,  # No profile
                fit_score=fit_score,
                cv_text=request.cv_text,
                provider=provider,
                model=model,
            )
            status = "documents_generated"

        # 5. Save to database
        logger.info("Saving application to database")
        application = JobApplication(
            user_id=str(user.id),
            company=job_analysis.company,
            role=job_analysis.role,
            location=job_analysis.location,
            remote_policy=job_analysis.remote_policy,
            seniority=job_analysis.seniority,
            job_url=str(request.job_url) if request.job_url else None,
            job_description=job_description,
            job_analysis=job_analysis.model_dump(),
            fit_score=fit_score.total,
            fit_breakdown=fit_score.breakdown.model_dump(),
            matched_skills=fit_score.matched_skills,
            missing_skills=fit_score.missing_skills,
            success_probability=probability.probability,
            probability_factors=[f.model_dump() for f in probability.factors],
            recommendation=probability.recommendation,
            salary_min=job_analysis.salary_range.get("min"),
            salary_max=job_analysis.salary_range.get("max"),
            salary_currency=job_analysis.salary_range.get("currency", "EUR"),
            green_flags=job_analysis.green_flags,
            red_flags=job_analysis.red_flags,
            cover_letter_text=cover_letter_text,
            cv_customization=cv_customization or {},
            status=status,
            profile_snapshot={
                "personal": profile.personal,
                "summary": profile.summary,
                "experience": profile.experience[:3],  # Save top 3 experiences
            },
        )

        db.add(application)
        await db.commit()
        await db.refresh(application)

        logger.info(f"Application {application.id} created successfully")

        # Return response
        return JobAnalysisResponse(
            application_id=application.id,
            job_analysis=job_analysis,
            fit_score=fit_score,
            success_probability=probability,
            cover_letter_text=cover_letter_text,
            cv_customization=cv_customization,
            status=status,
            created_at=application.created_at,
        )

    except Exception as e:
        logger.error(f"Error analyzing job: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error analyzing job: {str(e)}")


@router.post("/applications/{application_id}/generate", response_model=GenerateDocumentsResponse)
async def generate_documents(
    application_id: int,
    provider: str = Query("anthropic", description="LLM provider: anthropic, grok, ollama"),
    model: Optional[str] = Query(None, description="Specific model to use"),
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    """Generate cover letter and CV customization for an existing application."""
    # Get application
    statement = select(JobApplication).where(
        JobApplication.id == application_id,
        JobApplication.user_id == str(user.id),
    )
    result = await db.execute(statement)
    application = result.scalars().first()

    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    # Get profile
    statement = select(UserProfile).where(UserProfile.user_id == str(user.id))
    result = await db.execute(statement)
    profile = result.scalars().first()

    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    try:
        # Reconstruct objects from database
        from backend.schemas.jobassistant import JobAnalysisResult, FitScore, FitScoreBreakdown

        job_analysis = JobAnalysisResult(**application.job_analysis)
        fit_score = FitScore(
            total=application.fit_score,
            breakdown=FitScoreBreakdown(**application.fit_breakdown),
            matched_skills=application.matched_skills,
            missing_skills=application.missing_skills,
        )

        # Generate documents
        cover_letter_text = await service.generate_cover_letter(
            job_analysis=job_analysis,
            profile=profile,  # Pass the ORM object directly
            fit_score=fit_score,
            provider=provider,
            model=model,
        )

        cv_customization = await service.customize_cv(
            job_analysis=job_analysis,
            profile=profile,  # Pass the ORM object directly
            fit_score=fit_score,
            provider=provider,
            model=model,
        )

        # Update application
        application.cover_letter_text = cover_letter_text
        application.cv_customization = cv_customization
        application.status = "documents_generated"
        application.updated_at = datetime.utcnow()
        db.add(application)
        await db.commit()

        return GenerateDocumentsResponse(
            application_id=application.id,
            cover_letter_text=cover_letter_text,
            cv_customization=cv_customization,
            documents_generated=True,
        )

    except Exception as e:
        logger.error(f"Error generating documents: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error generating documents: {str(e)}")


# ============================================================================
# Application Management Endpoints
# ============================================================================


@router.get("/applications", response_model=List[ApplicationListResponse])
async def list_applications(
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(50, le=100),
    offset: int = Query(0),
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    """List user's job applications."""
    statement = select(JobApplication).where(JobApplication.user_id == str(user.id))

    if status:
        statement = statement.where(JobApplication.status == status)

    statement = statement.order_by(desc(JobApplication.created_at)).offset(offset).limit(limit)

    result = await db.execute(statement)
    applications = result.scalars().all()

    return [
        ApplicationListResponse(
            id=app.id,
            company=app.company,
            role=app.role,
            fit_score=app.fit_score,
            success_probability=app.success_probability,
            status=app.status,
            created_at=app.created_at,
            applied_date=app.applied_date,
        )
        for app in applications
    ]


@router.get("/applications/{application_id}", response_model=JobAnalysisResponse)
async def get_application(
    application_id: int,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    """Get detailed application information."""
    statement = select(JobApplication).where(
        JobApplication.id == application_id,
        JobApplication.user_id == str(user.id),
    )
    result = await db.execute(statement)
    application = result.scalars().first()

    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    # Reconstruct response
    from backend.schemas.jobassistant import (
        JobAnalysisResult,
        FitScore,
        FitScoreBreakdown,
        SuccessProbability,
        ProbabilityFactor,
    )

    return JobAnalysisResponse(
        application_id=application.id,
        job_analysis=JobAnalysisResult(**application.job_analysis),
        fit_score=FitScore(
            total=application.fit_score,
            breakdown=FitScoreBreakdown(**application.fit_breakdown),
            matched_skills=application.matched_skills,
            missing_skills=application.missing_skills,
        ),
        success_probability=SuccessProbability(
            probability=application.success_probability,
            factors=[ProbabilityFactor(**f) for f in application.probability_factors],
            recommendation=application.recommendation,
        ),
        cover_letter_text=application.cover_letter_text,
        cv_customization=application.cv_customization,
        status=application.status,
        created_at=application.created_at,
    )


@router.patch("/applications/{application_id}", response_model=ApplicationListResponse)
async def update_application(
    application_id: int,
    update_data: ApplicationUpdateRequest,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    """Update application status and metadata."""
    statement = select(JobApplication).where(
        JobApplication.id == application_id,
        JobApplication.user_id == str(user.id),
    )
    result = await db.execute(statement)
    application = result.scalars().first()

    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    # Update fields
    if update_data.status:
        application.status = update_data.status
    if update_data.applied_date:
        application.applied_date = update_data.applied_date
    if update_data.response_date:
        application.response_date = update_data.response_date
    if update_data.notes is not None:
        application.notes = update_data.notes

    application.updated_at = datetime.utcnow()
    db.add(application)
    await db.commit()
    await db.refresh(application)

    return ApplicationListResponse(
        id=application.id,
        company=application.company,
        role=application.role,
        fit_score=application.fit_score,
        success_probability=application.success_probability,
        status=application.status,
        created_at=application.created_at,
        applied_date=application.applied_date,
    )


@router.delete("/applications/{application_id}")
async def delete_application(
    application_id: int,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    """Delete an application."""
    statement = select(JobApplication).where(
        JobApplication.id == application_id,
        JobApplication.user_id == str(user.id),
    )
    result = await db.execute(statement)
    application = result.scalars().first()

    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    await db.delete(application)
    await db.commit()

    return {"message": "Application deleted successfully"}


@router.get("/stats", response_model=ApplicationStatsResponse)
async def get_stats(
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    """Get application statistics."""
    # Get all applications for user
    statement = select(JobApplication).where(JobApplication.user_id == str(user.id))
    result = await db.execute(statement)
    applications = result.scalars().all()

    if not applications:
        return ApplicationStatsResponse(
            total=0,
            avg_fit_score=0,
            avg_probability=0,
            by_status={},
            by_month={},
            top_companies=[],
        )

    # Calculate stats
    total = len(applications)
    avg_fit_score = int(sum(app.fit_score or 0 for app in applications) / total)
    avg_probability = int(sum(app.success_probability or 0 for app in applications) / total)

    # By status
    by_status = {}
    for app in applications:
        by_status[app.status] = by_status.get(app.status, 0) + 1

    # By month
    by_month = {}
    for app in applications:
        month_key = app.created_at.strftime("%Y-%m")
        by_month[month_key] = by_month.get(month_key, 0) + 1

    # Top companies
    company_counts = {}
    for app in applications:
        company_counts[app.company] = company_counts.get(app.company, 0) + 1

    top_companies = [
        {"company": company, "count": count}
        for company, count in sorted(company_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    ]

    return ApplicationStatsResponse(
        total=total,
        avg_fit_score=avg_fit_score,
        avg_probability=avg_probability,
        by_status=by_status,
        by_month=by_month,
        top_companies=top_companies,
    )


@router.post("/parse-document")
async def parse_document(
    file: UploadFile = File(...),
    user: User = Depends(current_active_user),
):
    """
    Parse uploaded document (PDF, DOCX, TXT) and extract text.

    Returns:
        JSON with extracted text
    """
    try:
        # Read file content
        content = await file.read()

        # Determine file type and extract text
        filename = file.filename.lower() if file.filename else ""

        if filename.endswith('.pdf'):
            import io
            text = document_processor.extract_from_pdf(io.BytesIO(content))
        elif filename.endswith('.docx') or filename.endswith('.doc'):
            import io
            text = document_processor.extract_from_docx(io.BytesIO(content))
        elif filename.endswith('.txt'):
            text = content.decode('utf-8')
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type. Supported: PDF, DOCX, TXT"
            )

        return {
            "text": text,
            "filename": file.filename,
            "length": len(text)
        }

    except Exception as e:
        logger.error(f"Error parsing document: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to parse document: {str(e)}"
        )


@router.post("/parse-url")
async def parse_url(
    url: str = Query(..., description="URL to scrape"),
    user: User = Depends(current_active_user),
):
    """
    Scrape URL and extract job description text.

    Returns:
        JSON with extracted text
    """
    try:
        result = document_processor.scrape_website(url, max_length=20000)

        # Combine title, description, and content
        text = f"{result['title']}\n\n{result['description']}\n\n{result['content']}"

        return {
            "text": text.strip(),
            "url": url,
            "title": result['title'],
            "length": len(text)
        }

    except Exception as e:
        logger.error(f"Error scraping URL: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to scrape URL: {str(e)}"
        )
