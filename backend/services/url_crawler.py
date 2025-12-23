"""URL Crawler Service for fetching and extracting content from web pages."""
import requests
from bs4 import BeautifulSoup
from typing import Optional, Dict, Any
import logging
from urllib.parse import urlparse
import re

logger = logging.getLogger(__name__)


class URLCrawlerService:
    """Service for crawling and extracting content from URLs."""

    # Allowed domains for job posting crawling (whitelist for safety)
    ALLOWED_JOB_DOMAINS = {
        "linkedin.com", "stepstone.de", "indeed.com", "indeed.de",
        "xing.com", "monster.de", "glassdoor.com", "glassdoor.de",
        "jobware.de", "jobscout24.de", "stellenanzeigen.de",
        "karriere.de", "jobvector.de", "meinestadt.de"
    }

    def __init__(self, timeout: int = 30, max_content_length: int = 10_000_000):
        """
        Initialize URL Crawler Service.

        Args:
            timeout: Request timeout in seconds
            max_content_length: Maximum content length to download (10MB default)
        """
        self.timeout = timeout
        self.max_content_length = max_content_length
        self.headers = {
            'User-Agent': 'CV-Matcher-Bot/1.0 (+https://www.dabrock.info)',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }

    def validate_url(self, url: str) -> bool:
        """
        Validate if URL is well-formed and uses http/https.

        Args:
            url: URL to validate

        Returns:
            True if valid, False otherwise
        """
        try:
            result = urlparse(url)
            return all([result.scheme in ['http', 'https'], result.netloc])
        except Exception:
            return False

    def check_job_domain(self, url: str) -> bool:
        """
        Check if URL is from an allowed job posting domain.

        Args:
            url: URL to check

        Returns:
            True if domain is allowed, False otherwise
        """
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            # Remove www. prefix
            domain = domain.replace('www.', '')
            return any(allowed in domain for allowed in self.ALLOWED_JOB_DOMAINS)
        except Exception:
            return False

    def fetch_url(self, url: str) -> Dict[str, Any]:
        """
        Fetch content from a URL and extract text, metadata.

        Args:
            url: URL to fetch

        Returns:
            Dictionary with extracted data:
            {
                'url': str,
                'title': str,
                'content': str,
                'metadata': {
                    'description': str,
                    'author': str,
                    'keywords': list[str],
                    'language': str
                },
                'status_code': int,
                'content_type': str
            }

        Raises:
            ValueError: If URL is invalid
            requests.RequestException: If fetch fails
        """
        # Validate URL
        if not self.validate_url(url):
            raise ValueError(f"Invalid URL: {url}")

        logger.info(f"Fetching URL: {url}")

        try:
            # Fetch URL with streaming to check content length
            response = requests.get(
                url,
                headers=self.headers,
                timeout=self.timeout,
                stream=True,
                allow_redirects=True
            )

            # Check content length
            content_length = response.headers.get('content-length')
            if content_length and int(content_length) > self.max_content_length:
                raise ValueError(f"Content too large: {content_length} bytes (max: {self.max_content_length})")

            # Check status code
            response.raise_for_status()

            # Get content type
            content_type = response.headers.get('content-type', '').lower()

            # Only process HTML/text content
            if not any(ct in content_type for ct in ['text/html', 'text/plain', 'application/xhtml']):
                raise ValueError(f"Unsupported content type: {content_type}")

            # Read content
            html_content = response.content

            # Parse with BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')

            # Extract title
            title = self._extract_title(soup)

            # Extract main content
            content = self._extract_content(soup)

            # Extract metadata
            metadata = self._extract_metadata(soup)

            logger.info(f"Successfully fetched URL: {url} ({len(content)} chars)")

            return {
                'url': url,
                'title': title,
                'content': content,
                'metadata': metadata,
                'status_code': response.status_code,
                'content_type': content_type,
                'final_url': response.url  # In case of redirects
            }

        except requests.exceptions.Timeout:
            logger.error(f"Timeout fetching URL: {url}")
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching URL {url}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error processing URL {url}: {str(e)}")
            raise

    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract page title."""
        # Try <title> tag
        if soup.title and soup.title.string:
            return soup.title.string.strip()

        # Try og:title meta tag
        og_title = soup.find('meta', property='og:title')
        if og_title and og_title.get('content'):
            return og_title['content'].strip()

        # Try h1 tag
        h1 = soup.find('h1')
        if h1:
            return h1.get_text(strip=True)

        return "Untitled"

    def _extract_content(self, soup: BeautifulSoup) -> str:
        """Extract main text content from page."""
        # Remove script, style, nav, header, footer elements (improved from Grok's approach)
        for script in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 'form']):
            script.decompose()

        # Try to find main content areas
        main_content = None

        # Try common content containers
        for selector in ['article', 'main', '[role="main"]', '.content', '#content', '.post', '.article']:
            if selector.startswith('.') or selector.startswith('#'):
                # Class or ID selector
                attr = 'class' if selector.startswith('.') else 'id'
                value = selector[1:]
                main_content = soup.find(attrs={attr: value})
            elif selector.startswith('['):
                # Attribute selector
                main_content = soup.find(attrs={'role': 'main'})
            else:
                # Tag selector
                main_content = soup.find(selector)

            if main_content:
                break

        # If no main content found, use body
        if not main_content:
            main_content = soup.find('body')

        if not main_content:
            main_content = soup

        # Extract text (improved whitespace handling from Grok)
        text = main_content.get_text(separator=' ', strip=True)

        # Clean up excessive whitespace (Grok's approach)
        text = ' '.join(text.split())

        # Limit length to prevent excessive content (safety measure from Grok)
        if len(text) > 50000:
            text = text[:50000] + "... [content truncated]"

        # Re-add paragraph breaks for readability
        text = re.sub(r'([.!?])\s+([A-Z])', r'\1\n\n\2', text)

        return text.strip()

    def _extract_metadata(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract metadata from page."""
        metadata = {
            'description': '',
            'author': '',
            'keywords': [],
            'language': ''
        }

        # Description
        desc_tag = soup.find('meta', attrs={'name': 'description'})
        if not desc_tag:
            desc_tag = soup.find('meta', property='og:description')
        if desc_tag and desc_tag.get('content'):
            metadata['description'] = desc_tag['content'].strip()

        # Author
        author_tag = soup.find('meta', attrs={'name': 'author'})
        if not author_tag:
            author_tag = soup.find('meta', property='article:author')
        if author_tag and author_tag.get('content'):
            metadata['author'] = author_tag['content'].strip()

        # Keywords
        keywords_tag = soup.find('meta', attrs={'name': 'keywords'})
        if keywords_tag and keywords_tag.get('content'):
            keywords = keywords_tag['content'].split(',')
            metadata['keywords'] = [k.strip() for k in keywords if k.strip()]

        # Language
        html_tag = soup.find('html')
        if html_tag and html_tag.get('lang'):
            metadata['language'] = html_tag['lang'].strip()

        return metadata

    def extract_job_description(self, url: str) -> Dict[str, Any]:
        """
        Specialized extraction for job description pages.

        Args:
            url: URL of job posting

        Returns:
            Dictionary with job-specific fields
        """
        data = self.fetch_url(url)

        # Parse content for job-specific fields
        soup = BeautifulSoup(data['content'], 'html.parser')

        job_data = {
            'title': data['title'],
            'description': data['content'],
            'company': self._extract_company(soup),
            'location': self._extract_location(soup),
            'salary': self._extract_salary(soup),
            'requirements': self._extract_requirements(data['content']),
            'benefits': self._extract_benefits(data['content']),
            'url': url
        }

        return job_data

    def _extract_company(self, soup: BeautifulSoup) -> str:
        """Extract company name from job posting."""
        # Try common selectors
        for selector in ['.company', '#company', '[itemprop="hiringOrganization"]']:
            elem = soup.select_one(selector)
            if elem:
                return elem.get_text(strip=True)
        return ""

    def _extract_location(self, soup: BeautifulSoup) -> str:
        """Extract location from job posting."""
        for selector in ['.location', '#location', '[itemprop="jobLocation"]']:
            elem = soup.select_one(selector)
            if elem:
                return elem.get_text(strip=True)
        return ""

    def _extract_salary(self, soup: BeautifulSoup) -> str:
        """Extract salary information."""
        for selector in ['.salary', '#salary', '[itemprop="baseSalary"]']:
            elem = soup.select_one(selector)
            if elem:
                return elem.get_text(strip=True)
        return ""

    def _extract_requirements(self, text: str) -> list:
        """Extract requirements from job description text."""
        requirements = []

        # Look for common requirement sections
        req_patterns = [
            r'(?i)requirements?:?\s*\n(.*?)(?:\n\n|$)',
            r'(?i)qualifications?:?\s*\n(.*?)(?:\n\n|$)',
            r'(?i)you should have:?\s*\n(.*?)(?:\n\n|$)'
        ]

        for pattern in req_patterns:
            match = re.search(pattern, text, re.DOTALL)
            if match:
                req_text = match.group(1)
                # Split by bullet points or newlines
                reqs = re.split(r'\n\s*[-•*]\s*|\n', req_text)
                requirements.extend([r.strip() for r in reqs if r.strip()])
                break

        return requirements[:10]  # Limit to 10 requirements

    def _extract_benefits(self, text: str) -> list:
        """Extract benefits from job description text."""
        benefits = []

        # Look for benefits section
        ben_patterns = [
            r'(?i)benefits?:?\s*\n(.*?)(?:\n\n|$)',
            r'(?i)we offer:?\s*\n(.*?)(?:\n\n|$)',
            r'(?i)perks:?\s*\n(.*?)(?:\n\n|$)'
        ]

        for pattern in ben_patterns:
            match = re.search(pattern, text, re.DOTALL)
            if match:
                ben_text = match.group(1)
                bens = re.split(r'\n\s*[-•*]\s*|\n', ben_text)
                benefits.extend([b.strip() for b in bens if b.strip()])
                break

        return benefits[:10]  # Limit to 10 benefits


# Singleton instance
_crawler_service = None


def get_crawler_service() -> URLCrawlerService:
    """Get or create crawler service singleton."""
    global _crawler_service
    if _crawler_service is None:
        _crawler_service = URLCrawlerService()
    return _crawler_service
