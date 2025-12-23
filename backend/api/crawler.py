"""API endpoints for URL crawling."""
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, HttpUrl, Field
from typing import Optional, Dict, Any, List
import logging

from backend.services.url_crawler import get_crawler_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/crawler", tags=["crawler"])


# Request/Response Models
class URLFetchRequest(BaseModel):
    """Request model for fetching a URL."""
    url: HttpUrl = Field(..., description="URL to fetch and extract content from")
    extract_type: str = Field(
        default="general",
        description="Type of extraction: 'general' or 'job_description'"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "url": "https://example.com/job-posting",
                "extract_type": "general"
            }
        }


class MetadataResponse(BaseModel):
    """Metadata extracted from a webpage."""
    description: str = Field(default="", description="Page meta description")
    author: str = Field(default="", description="Page author")
    keywords: List[str] = Field(default_factory=list, description="Page keywords")
    language: str = Field(default="", description="Page language")


class URLFetchResponse(BaseModel):
    """Response model for URL fetch."""
    url: str = Field(..., description="Original URL requested")
    final_url: str = Field(..., description="Final URL after redirects")
    title: str = Field(..., description="Page title")
    content: str = Field(..., description="Extracted text content")
    metadata: MetadataResponse = Field(..., description="Page metadata")
    status_code: int = Field(..., description="HTTP status code")
    content_type: str = Field(..., description="Content-Type header")
    content_length: int = Field(..., description="Length of extracted content in characters")

    class Config:
        json_schema_extra = {
            "example": {
                "url": "https://example.com",
                "final_url": "https://example.com",
                "title": "Example Domain",
                "content": "This domain is for use in illustrative examples...",
                "metadata": {
                    "description": "Example domain",
                    "author": "",
                    "keywords": [],
                    "language": "en"
                },
                "status_code": 200,
                "content_type": "text/html",
                "content_length": 1234
            }
        }


class JobDescriptionResponse(BaseModel):
    """Response model for job description extraction."""
    title: str = Field(..., description="Job title")
    description: str = Field(..., description="Full job description")
    company: str = Field(default="", description="Company name")
    location: str = Field(default="", description="Job location")
    salary: str = Field(default="", description="Salary information")
    requirements: List[str] = Field(default_factory=list, description="Job requirements")
    benefits: List[str] = Field(default_factory=list, description="Job benefits")
    url: str = Field(..., description="Job posting URL")

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Senior Python Developer",
                "description": "We are looking for a Senior Python Developer...",
                "company": "Tech Corp",
                "location": "Berlin, Germany",
                "salary": "€70,000 - €90,000",
                "requirements": [
                    "5+ years Python experience",
                    "FastAPI knowledge",
                    "PostgreSQL proficiency"
                ],
                "benefits": [
                    "Remote work",
                    "Health insurance",
                    "Professional development"
                ],
                "url": "https://example.com/jobs/123"
            }
        }


class URLValidateRequest(BaseModel):
    """Request model for URL validation."""
    url: HttpUrl = Field(..., description="URL to validate")


class URLValidateResponse(BaseModel):
    """Response model for URL validation."""
    url: str = Field(..., description="URL that was validated")
    is_valid: bool = Field(..., description="Whether URL is valid")
    message: str = Field(..., description="Validation message")


# API Endpoints
@router.post("/fetch", response_model=URLFetchResponse, status_code=status.HTTP_200_OK)
async def fetch_url(request: URLFetchRequest):
    """
    Fetch and extract content from a URL.

    This endpoint fetches content from the provided URL and extracts:
    - Page title
    - Main text content
    - Metadata (description, author, keywords, language)

    **Supported content types:**
    - text/html
    - text/plain
    - application/xhtml+xml

    **Limits:**
    - Maximum content size: 10MB
    - Request timeout: 30 seconds

    **Example usage:**
    ```python
    import requests

    response = requests.post(
        "http://localhost:8000/crawler/fetch",
        json={"url": "https://example.com"}
    )
    data = response.json()
    print(data['title'])
    print(data['content'][:500])
    ```
    """
    try:
        crawler = get_crawler_service()
        result = crawler.fetch_url(str(request.url))

        return URLFetchResponse(
            url=result['url'],
            final_url=result['final_url'],
            title=result['title'],
            content=result['content'],
            metadata=MetadataResponse(**result['metadata']),
            status_code=result['status_code'],
            content_type=result['content_type'],
            content_length=len(result['content'])
        )

    except ValueError as e:
        logger.warning(f"Invalid URL or content: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error fetching URL: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch URL: {str(e)}"
        )


@router.post("/job-description", response_model=JobDescriptionResponse, status_code=status.HTTP_200_OK)
async def fetch_job_description(request: URLFetchRequest):
    """
    Fetch and extract job description from a URL.

    This specialized endpoint extracts job-specific information:
    - Job title
    - Company name
    - Location
    - Salary range
    - Requirements
    - Benefits

    **Domain Whitelist:** Only allows crawling from trusted job boards:
    - LinkedIn, StepStone, Indeed, XING, Monster, Glassdoor, and others

    **Use case:** Extract structured job posting data for CV matching.

    **Example usage:**
    ```python
    import requests

    response = requests.post(
        "http://localhost:8000/crawler/job-description",
        json={"url": "https://linkedin.com/jobs/view/123"}
    )
    job_data = response.json()
    print(f"Job: {job_data['title']} at {job_data['company']}")
    print(f"Requirements: {job_data['requirements']}")
    ```
    """
    try:
        crawler = get_crawler_service()

        # Check if domain is allowed (safety measure from Grok's approach)
        if not crawler.check_job_domain(str(request.url)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Domain not allowed for job crawling. Only trusted job boards are supported."
            )

        result = crawler.extract_job_description(str(request.url))

        return JobDescriptionResponse(**result)

    except ValueError as e:
        logger.warning(f"Invalid URL or content: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error fetching job description: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch job description: {str(e)}"
        )


@router.post("/validate", response_model=URLValidateResponse, status_code=status.HTTP_200_OK)
async def validate_url(request: URLValidateRequest):
    """
    Validate a URL without fetching content.

    This lightweight endpoint checks if a URL is well-formed and uses http/https.

    **Example usage:**
    ```python
    import requests

    response = requests.post(
        "http://localhost:8000/crawler/validate",
        json={"url": "https://example.com"}
    )
    result = response.json()
    if result['is_valid']:
        print("URL is valid!")
    ```
    """
    try:
        crawler = get_crawler_service()
        is_valid = crawler.validate_url(str(request.url))

        return URLValidateResponse(
            url=str(request.url),
            is_valid=is_valid,
            message="URL is valid" if is_valid else "URL is invalid or uses unsupported protocol"
        )

    except Exception as e:
        logger.error(f"Error validating URL: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to validate URL: {str(e)}"
        )


@router.get("/health", status_code=status.HTTP_200_OK)
async def crawler_health():
    """
    Health check endpoint for crawler service.

    Returns service status and capabilities.
    """
    return {
        "status": "healthy",
        "service": "url_crawler",
        "version": "1.0.0",
        "capabilities": [
            "general_content_extraction",
            "job_description_extraction",
            "url_validation"
        ],
        "limits": {
            "max_content_size_mb": 10,
            "timeout_seconds": 30
        }
    }
