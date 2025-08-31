"""
Firecrawl MCP client for web scraping.
"""

import asyncio
import aiohttp
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging
from urllib.parse import urlparse

from .models import ScrapingError, ScrapingResult, ContentType, ContentMetadata
from .rate_limiter import RateLimiter, RateLimit

logger = logging.getLogger(__name__)


class FirecrawlClient:
    """Client for Firecrawl MCP web scraping service."""
    
    def __init__(self, api_key: str, base_url: str = "https://api.firecrawl.dev"):
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Rate limiting: 60 requests per minute
        self.rate_limiter = RateLimiter(RateLimit(requests_per_minute=60))
        
        # Default headers
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'User-Agent': 'BlogReviewer/1.0'
        }
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession(
            headers=self.headers,
            timeout=aiohttp.ClientTimeout(total=30)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def scrape_url(self, url: str, options: Dict[str, Any] = None) -> ScrapingResult:
        """Scrape a single URL using Firecrawl."""
        if not self.session:
            raise RuntimeError("Client not initialized. Use async context manager.")
        
        start_time = datetime.now()
        
        try:
            # Apply rate limiting
            await self.rate_limiter.acquire("firecrawl")
            
            # Prepare request payload
            payload = {
                "url": url,
                "pageOptions": {
                    "onlyMainContent": True,
                    "includeHtml": True,
                    "waitFor": 2000,  # Wait 2 seconds for dynamic content
                    "screenshot": False,
                    "pdf": False,
                    "extractMetadata": True
                }
            }
            
            if options:
                payload["pageOptions"].update(options)
            
            # Make request
            async with self.session.post(
                f"{self.base_url}/scrape",
                json=payload
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return await self._process_scraping_response(data, url, start_time)
                else:
                    error_text = await response.text()
                    raise Exception(f"Firecrawl API error: {response.status} - {error_text}")
        
        except asyncio.TimeoutError:
            error = ScrapingError(
                error_type="timeout",
                message="Request timed out",
                url=url,
                retry_count=0
            )
            return self._create_error_result(url, error, start_time)
        
        except aiohttp.ClientError as e:
            error = ScrapingError(
                error_type="network",
                message=f"Network error: {str(e)}",
                url=url,
                retry_count=0
            )
            return self._create_error_result(url, error, start_time)
        
        except Exception as e:
            error = ScrapingError(
                error_type="api",
                message=f"API error: {str(e)}",
                url=url,
                retry_count=0
            )
            return self._create_error_result(url, error, start_time)
    
    async def scrape_multiple_urls(self, urls: List[str], options: Dict[str, Any] = None) -> List[ScrapingResult]:
        """Scrape multiple URLs concurrently."""
        if not self.session:
            raise RuntimeError("Client not initialized. Use async context manager.")
        
        # Limit concurrency to avoid overwhelming the API
        semaphore = asyncio.Semaphore(5)
        
        async def scrape_with_semaphore(url: str) -> ScrapingResult:
            async with semaphore:
                return await self.scrape_url(url, options)
        
        # Scrape URLs concurrently
        tasks = [scrape_with_semaphore(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                error = ScrapingError(
                    error_type="exception",
                    message=f"Unexpected error: {str(result)}",
                    url=urls[i],
                    retry_count=0
                )
                processed_results.append(self._create_error_result(urls[i], error, datetime.now()))
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def _process_scraping_response(self, data: Dict[str, Any], url: str, start_time: datetime) -> ScrapingResult:
        """Process the response from Firecrawl API."""
        try:
            # Extract content
            content = data.get('markdown', '')
            html = data.get('html', '')
            
            # Extract metadata
            metadata = self._extract_metadata_from_response(data, url)
            
            # Calculate scraping time
            scraping_time = (datetime.now() - start_time).total_seconds()
            
            # Generate content hash
            content_hash = self._generate_content_hash(content)
            
            # Determine content type
            content_type = self._determine_content_type(url, metadata)
            
            # Create result
            return ScrapingResult(
                url=url,
                content_type=content_type,
                content=content,
                raw_html=html,
                metadata=metadata,
                scraping_time=scraping_time,
                content_hash=content_hash,
                quality_score=1.0  # Firecrawl provides high-quality content
            )
        
        except Exception as e:
            logger.error(f"Error processing Firecrawl response for {url}: {e}")
            error = ScrapingError(
                error_type="processing",
                message=f"Error processing response: {str(e)}",
                url=url,
                retry_count=0
            )
            return self._create_error_result(url, error, start_time)
    
    def _extract_metadata_from_response(self, data: Dict[str, Any], url: str) -> ContentMetadata:
        """Extract metadata from Firecrawl response."""
        metadata = data.get('metadata', {})
        
        return ContentMetadata(
            title=metadata.get('title'),
            author=metadata.get('author'),
            published_date=self._parse_date(metadata.get('publishedDate')),
            last_modified=self._parse_date(metadata.get('lastModified')),
            language=metadata.get('language', 'en'),
            word_count=metadata.get('wordCount'),
            reading_time=metadata.get('readingTime'),
            tags=metadata.get('tags', []),
            description=metadata.get('description'),
            canonical_url=metadata.get('canonicalUrl'),
            og_image=metadata.get('ogImage'),
            og_description=metadata.get('ogDescription')
        )
    
    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse date string into datetime object."""
        if not date_str:
            return None
        
        try:
            # Try ISO format first
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except ValueError:
            try:
                # Try common formats
                formats = [
                    '%Y-%m-%dT%H:%M:%S',
                    '%Y-%m-%d %H:%M:%S',
                    '%Y-%m-%d',
                    '%B %d, %Y',
                    '%b %d, %Y'
                ]
                
                for fmt in formats:
                    try:
                        return datetime.strptime(date_str, fmt)
                    except ValueError:
                        continue
                
                return None
            except:
                return None
    
    def _determine_content_type(self, url: str, metadata: ContentMetadata) -> ContentType:
        """Determine the type of content based on URL and metadata."""
        url_lower = url.lower()
        
        # Check for RSS feeds
        if any(ext in url_lower for ext in ['.rss', '.xml', '/feed']):
            return ContentType.RSS_FEED
        
        # Check for blog posts
        if any(path in url_lower for path in ['/blog/', '/post/', '/article/']):
            return ContentType.BLOG_POST
        
        # Check for articles
        if any(path in url_lower for path in ['/article/', '/news/', '/story/']):
            return ContentType.ARTICLE
        
        # Default to webpage
        return ContentType.WEBPAGE
    
    def _generate_content_hash(self, content: str) -> str:
        """Generate SHA-256 hash of content."""
        import hashlib
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    def _create_error_result(self, url: str, error: ScrapingError, start_time: datetime) -> ScrapingResult:
        """Create a result object for failed scraping."""
        scraping_time = (datetime.now() - start_time).total_seconds()
        
        return ScrapingResult(
            url=url,
            content_type=ContentType.WEBPAGE,
            content="",
            metadata=ContentMetadata(),
            scraping_time=scraping_time,
            content_hash="",
            errors=[error]
        )
    
    async def get_rate_limit_status(self) -> Dict[str, Any]:
        """Get current rate limit status."""
        return self.rate_limiter.get_stats("firecrawl")
    
    def is_url_supported(self, url: str) -> bool:
        """Check if a URL is supported by Firecrawl."""
        try:
            parsed = urlparse(url)
            return parsed.scheme in ['http', 'https'] and parsed.netloc
        except:
            return False
