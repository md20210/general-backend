#!/usr/bin/env python3
"""
Test script to verify URL crawling functionality
"""
import asyncio
import httpx
from bs4 import BeautifulSoup
import re


async def crawl_url(url: str, max_length: int = 10000) -> str:
    """
    Crawl URL and extract clean text content.
    """
    try:
        # Add https:// if URL doesn't have a protocol
        if not url.startswith(('http://', 'https://')):
            url = f'https://{url}'

        print(f"🔍 Crawling: {url}")

        async with httpx.AsyncClient(
            timeout=30.0,
            follow_redirects=True,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
        ) as client:
            response = await client.get(url)

            print(f"📊 Status Code: {response.status_code}")

            if response.status_code != 200:
                print(f"❌ URL {url} returned status code {response.status_code}")
                return ""

            # Try to parse HTML
            try:
                # Parse HTML
                soup = BeautifulSoup(response.text, 'html.parser')

                # Remove script, style, nav, footer, header elements
                for element in soup(["script", "style", "nav", "footer", "header", "aside", "iframe", "noscript"]):
                    element.decompose()

                # Get text from main content areas (prioritize main, article, section)
                main_content = soup.find('main') or soup.find('article') or soup.find('div', class_=re.compile(r'content|main|body'))

                if main_content:
                    text = main_content.get_text(separator=' ', strip=True)
                    print("✅ Found main content area")
                else:
                    text = soup.get_text(separator=' ', strip=True)
                    print("⚠️  Using full page text (no main content found)")

                # Clean whitespace
                lines = (line.strip() for line in text.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                text = ' '.join(chunk for chunk in chunks if chunk)

                # Truncate if too long
                if len(text) > max_length:
                    text = text[:max_length] + "..."

                print(f"📝 Extracted {len(text)} characters")
                return text

            except ImportError:
                print("❌ BeautifulSoup not available")
                return ""

    except httpx.TimeoutException:
        print(f"⏱️  Timeout while crawling {url}")
        return ""
    except Exception as e:
        print(f"❌ Failed to crawl {url}: {e}")
        return ""


async def main():
    """Test crawling with sample URLs"""
    test_urls = [
        "https://dabrock.info",
        "https://www.linkedin.com/in/michael-dabrock-b2838a80/",
        "https://example.com"
    ]

    for url in test_urls:
        print(f"\n{'='*60}")
        content = await crawl_url(url)
        if content:
            print(f"✅ SUCCESS - Preview (first 200 chars):")
            print(f"{content[:200]}...")
        else:
            print(f"❌ FAILED - No content extracted")
        print(f"{'='*60}\n")


if __name__ == "__main__":
    asyncio.run(main())
