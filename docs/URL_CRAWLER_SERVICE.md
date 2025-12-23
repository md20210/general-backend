# URL Crawler Service Documentation

## Overview

The URL Crawler Service provides web scraping and content extraction capabilities for the General Backend. It allows fetching content from URLs, extracting text, metadata, and specialized information like job descriptions.

**Service Location**: `backend/services/url_crawler.py`
**API Endpoints**: `backend/api/crawler.py`
**Base URL**: `/crawler`

---

## Features

### 🌐 General Content Extraction
- Fetch and parse HTML pages
- Extract title, main content, and metadata
- Remove navigation, scripts, and styling
- Clean and format extracted text

### 💼 Job Description Extraction
- Specialized extraction for job postings
- Extract company, location, salary
- Parse requirements and benefits
- Structured data output

### ✅ URL Validation
- Validate URL format
- Check for http/https protocol
- Lightweight pre-check before fetching

---

## API Endpoints

### 1. Fetch URL Content

**Endpoint**: `POST /crawler/fetch`

Fetch and extract content from any URL.

#### Request
```json
{
  "url": "https://example.com",
  "extract_type": "general"
}
```

#### Response
```json
{
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
```

#### Example (Python)
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

#### Example (cURL)
```bash
curl -X POST "http://localhost:8000/crawler/fetch" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

---

### 2. Fetch Job Description

**Endpoint**: `POST /crawler/job-description`

Extract structured job posting information.

#### Request
```json
{
  "url": "https://jobs.example.com/posting/123"
}
```

#### Response
```json
{
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
  "url": "https://jobs.example.com/posting/123"
}
```

#### Example (Python)
```python
import requests

response = requests.post(
    "http://localhost:8000/crawler/job-description",
    json={"url": "https://jobs.example.com/posting/123"}
)
job_data = response.json()
print(f"Job: {job_data['title']} at {job_data['company']}")
print(f"Requirements: {job_data['requirements']}")
```

---

### 3. Validate URL

**Endpoint**: `POST /crawler/validate`

Check if a URL is valid before fetching.

#### Request
```json
{
  "url": "https://example.com"
}
```

#### Response
```json
{
  "url": "https://example.com",
  "is_valid": true,
  "message": "URL is valid"
}
```

#### Example (Python)
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

---

### 4. Health Check

**Endpoint**: `GET /crawler/health`

Check service status and capabilities.

#### Response
```json
{
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
```

---

## Service Configuration

### Limits
- **Max Content Size**: 10 MB
- **Request Timeout**: 30 seconds
- **Supported Protocols**: http, https
- **Supported Content Types**: text/html, text/plain, application/xhtml+xml

### Headers
The crawler sends standard browser headers to avoid blocking:
```python
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) ...
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
Accept-Language: en-US,en;q=0.5
```

---

## Content Extraction Logic

### Title Extraction (Priority Order)
1. `<title>` tag
2. `<meta property="og:title">` (Open Graph)
3. `<h1>` tag
4. Fallback: "Untitled"

### Main Content Extraction
1. Remove `<script>`, `<style>`, `<nav>`, `<footer>`, `<header>`, `<aside>`
2. Search for main content containers:
   - `<article>`
   - `<main>`
   - `[role="main"]`
   - `.content`, `#content`
   - `.post`, `.article`
3. Fallback to `<body>`
4. Clean excessive whitespace

### Metadata Extraction
- **Description**: `<meta name="description">` or `og:description`
- **Author**: `<meta name="author">` or `article:author`
- **Keywords**: `<meta name="keywords">` (comma-separated)
- **Language**: `<html lang="...">`

---

## Integration with Other Services

### CV Matcher Integration
```python
# Fetch job description from URL
job_data = await fetch_job_description({"url": job_url})

# Use in CV matching
match_result = await analyze_cv_match(
    employer_text=job_data['description'],
    applicant_text=cv_text
)
```

### Document Storage Integration
```python
# Fetch content from URL
content = await fetch_url({"url": url})

# Store as document
document = await create_document(
    name=content['title'],
    content=content['content'],
    type="web_page"
)
```

### RAG Integration
```python
# Fetch content
content = await fetch_url({"url": url})

# Add to vector store
await vector_service.add_documents([{
    "content": content['content'],
    "metadata": {
        "source": "web",
        "url": content['url'],
        "title": content['title']
    }
}])
```

---

## Error Handling

### HTTP Errors
- **400 Bad Request**: Invalid URL or unsupported content type
- **500 Internal Server Error**: Fetch failed, timeout, or parsing error

### Common Errors
```python
# Invalid URL
{
  "detail": "Invalid URL: not-a-url"
}

# Timeout
{
  "detail": "Failed to fetch URL: Request timeout"
}

# Content too large
{
  "detail": "Content too large: 15000000 bytes (max: 10000000)"
}

# Unsupported content type
{
  "detail": "Unsupported content type: application/pdf"
}
```

---

## Use Cases

### 1. Job Board Scraping
```python
# Scrape job posting
job = requests.post(
    f"{API_BASE}/crawler/job-description",
    json={"url": "https://linkedin.com/jobs/123"}
).json()

# Use in CV matching
match = requests.post(
    f"{API_BASE}/llm/analyze",
    json={
        "employer_text": job['description'],
        "applicant_text": cv_text
    }
).json()
```

### 2. Company Research
```python
# Fetch company page
company_info = requests.post(
    f"{API_BASE}/crawler/fetch",
    json={"url": "https://company.com/about"}
).json()

# Use in chat context
chat_response = requests.post(
    f"{API_BASE}/chat/message",
    json={
        "message": "Tell me about this company",
        "system_context": company_info['content']
    }
).json()
```

### 3. Content Aggregation
```python
urls = [
    "https://blog.example.com/post1",
    "https://blog.example.com/post2",
    "https://blog.example.com/post3"
]

contents = []
for url in urls:
    result = requests.post(
        f"{API_BASE}/crawler/fetch",
        json={"url": url}
    ).json()
    contents.append({
        "title": result['title'],
        "content": result['content'],
        "url": url
    })

# Process aggregated content
```

---

## Performance Considerations

### Caching
The service does not implement caching by default. For production use, consider:
- **Redis caching** for frequently accessed URLs
- **TTL-based cache expiration** (e.g., 1 hour)
- **Cache key**: `url_crawler:{url_hash}`

### Rate Limiting
Implement rate limiting to avoid:
- Overloading target websites
- IP blocking
- Service abuse

Recommended limits:
- **Per-user**: 10 requests/minute
- **Per-IP**: 50 requests/minute
- **Global**: 1000 requests/minute

### Async Processing
For large-scale scraping, consider:
- Background task queue (Celery, Redis Queue)
- Webhook callbacks for results
- Batch processing endpoints

---

## Security Considerations

### SSRF Protection
The service validates URLs but does **not** prevent SSRF attacks. In production:
- Block internal IP ranges (127.0.0.1, 192.168.x.x, 10.x.x.x)
- Whitelist allowed domains
- Use proxy/firewall rules

### Content Sanitization
Extracted content is plain text, but:
- Be cautious with `metadata` fields (may contain HTML)
- Sanitize before displaying in frontend
- Validate before storing in database

### Legal Compliance
Ensure compliance with:
- **robots.txt** directives
- **Website terms of service**
- **Copyright laws**
- **GDPR** (if storing scraped data)

---

## Testing

### Unit Tests
```python
# Test URL validation
def test_validate_url():
    crawler = URLCrawlerService()
    assert crawler.validate_url("https://example.com") == True
    assert crawler.validate_url("ftp://example.com") == False
    assert crawler.validate_url("not-a-url") == False

# Test content extraction
def test_fetch_url():
    crawler = URLCrawlerService()
    result = crawler.fetch_url("https://example.com")
    assert result['title'] == "Example Domain"
    assert len(result['content']) > 0
```

### Integration Tests
```bash
# Test fetch endpoint
curl -X POST "http://localhost:8000/crawler/fetch" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'

# Test job description endpoint
curl -X POST "http://localhost:8000/crawler/job-description" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://jobs.example.com/123"}'

# Test validation endpoint
curl -X POST "http://localhost:8000/crawler/validate" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

---

## Future Enhancements

- [ ] JavaScript rendering (Playwright/Selenium)
- [ ] PDF content extraction
- [ ] Image extraction and OCR
- [ ] Multi-URL batch processing
- [ ] Recursive crawling (sitemaps)
- [ ] Screenshot capture
- [ ] Custom extraction rules (CSS selectors)
- [ ] Webhook notifications
- [ ] Redis caching layer
- [ ] Rate limiting middleware

---

## Changelog

### Version 1.0.0 (2025-12-23)
- ✅ Initial release
- ✅ General content extraction
- ✅ Job description extraction
- ✅ URL validation
- ✅ Metadata extraction
- ✅ Health check endpoint
- ✅ Swagger documentation

---

## Support

- **API Documentation**: https://general-backend-production-a734.up.railway.app/docs
- **Service**: `backend/services/url_crawler.py`
- **API Endpoints**: `backend/api/crawler.py`

For issues or questions, check the FastAPI Swagger UI at `/docs` for interactive testing.
