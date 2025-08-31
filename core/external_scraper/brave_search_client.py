"""
Brave Search API client for content discovery.
"""

import asyncio
import aiohttp
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging
from urllib.parse import urlparse, quote_plus

from .models import ScrapingError
from .rate_limiter import RateLimiter, RateLimit

logger = logging.getLogger(__name__)


class BraveSearchResult:
    """Result from Brave Search API."""
    
    def __init__(self, data: Dict[str, Any]):
        self.title = data.get('title', '')
        self.url = data.get('url', '')
        self.description = data.get('description', '')
        self.published_date = data.get('published_date')
        self.language = data.get('language', 'en')
        self.family_friendly = data.get('family_friendly', True)
        self.type = data.get('type', 'web')
        self.age = data.get('age')
        self.rank = data.get('rank', 0)


class BraveSearchClient:
    """Client for Brave Search API."""
    
    def __init__(self, api_key: str, base_url: str = "https://api.search.brave.com"):
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Rate limiting: 30 requests per minute for free tier
        self.rate_limiter = RateLimiter(RateLimit(requests_per_minute=30))
        
        # Default headers
        self.headers = {
            'X-Subscription-Token': api_key,
            'Accept': 'application/json',
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
    
    async def search(self, query: str, options: Dict[str, Any] = None) -> List[BraveSearchResult]:
        """Search for content using Brave Search."""
        if not self.session:
            raise RuntimeError("Client not initialized. Use async context manager.")
        
        try:
            # Apply rate limiting
            await self.rate_limiter.acquire("brave_search")
            
            # Prepare query parameters
            params = {
                'q': query,
                'count': options.get('count', 10),
                'search_lang': options.get('search_lang', 'en_US'),
                'country': options.get('country', 'US'),
                'safesearch': options.get('safesearch', 'moderate'),
                'freshness': options.get('freshness', 'pd'),  # Past day
                'text_decorations': False,
                'spellcheck': True
            }
            
            # Add optional parameters
            if options.get('offset'):
                params['offset'] = options['offset']
            
            if options.get('ui_lang'):
                params['ui_lang'] = options['ui_lang']
            
            # Make request
            async with self.session.get(
                f"{self.base_url}/res/v1/web/search",
                params=params
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._process_search_response(data)
                else:
                    error_text = await response.text()
                    raise Exception(f"Brave Search API error: {response.status} - {error_text}")
        
        except asyncio.TimeoutError:
            logger.error(f"Brave Search timeout for query: {query}")
            return []
        
        except aiohttp.ClientError as e:
            logger.error(f"Brave Search network error for query {query}: {e}")
            return []
        
        except Exception as e:
            logger.error(f"Brave Search API error for query {query}: {e}")
            return []
    
    async def search_news(self, query: str, options: Dict[str, Any] = None) -> List[BraveSearchResult]:
        """Search for news content using Brave Search."""
        if not self.session:
            raise RuntimeError("Client not initialized. Use async context manager.")
        
        try:
            # Apply rate limiting
            await self.rate_limiter.acquire("brave_search")
            
            # Prepare query parameters
            params = {
                'q': query,
                'count': options.get('count', 10),
                'search_lang': options.get('search_lang', 'en_US'),
                'country': options.get('country', 'US'),
                'safesearch': options.get('safesearch', 'moderate'),
                'freshness': options.get('freshness', 'pd'),  # Past day
                'text_decorations': False,
                'spellcheck': True
            }
            
            # Add optional parameters
            if options.get('offset'):
                params['offset'] = options['offset']
            
            if options.get('ui_lang'):
                params['ui_lang'] = options['ui_lang']
            
            # Make request to news endpoint
            async with self.session.get(
                f"{self.base_url}/news/search",
                params=params
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._process_news_response(data)
                else:
                    error_text = await response.text()
                    raise Exception(f"Brave News API error: {response.status} - {error_text}")
        
        except asyncio.TimeoutError:
            logger.error(f"Brave News timeout for query: {query}")
            return []
        
        except aiohttp.ClientError as e:
            logger.error(f"Brave News network error for query {query}: {e}")
            return []
        
        except Exception as e:
            logger.error(f"Brave News API error for query {query}: {e}")
            return []
    
    async def search_author_content(self, author_name: str, domain: str = None, options: Dict[str, Any] = None) -> List[BraveSearchResult]:
        """Search for content by a specific author."""
        if not self.session:
            raise RuntimeError("Client not initialized. Use async context manager.")
        
        # Build search query
        query_parts = [f'"{author_name}"']
        
        if domain:
            query_parts.append(f'site:{domain}')
        
        # Add content type filters
        query_parts.extend([
            '("blog post" OR "article" OR "writing" OR "post")',
            '-"contact" -"about" -"profile" -"bio"'
        ])
        
        query = ' '.join(query_parts)
        
        # Use news search for more recent content
        return await self.search_news(query, options)
    
    async def search_blog_posts(self, topic: str, domain: str = None, options: Dict[str, Any] = None) -> List[BraveSearchResult]:
        """Search for blog posts on a specific topic."""
        if not self.session:
            raise RuntimeError("Client not initialized. Use async context manager.")
        
        # Build search query
        query_parts = [topic]
        
        if domain:
            query_parts.append(f'site:{domain}')
        
        # Add blog-specific filters
        query_parts.extend([
            '("blog post" OR "blog article" OR "blog entry")',
            '-"contact" -"about" -"profile"'
        ])
        
        query = ' '.join(query_parts)
        
        return await self.search(query, options)
    
    def _process_search_response(self, data: Dict[str, Any]) -> List[BraveSearchResult]:
        """Process the response from Brave Search API."""
        results = []
        
        try:
            web_results = data.get('web', {}).get('results', [])
            
            for result_data in web_results:
                try:
                    result = BraveSearchResult(result_data)
                    results.append(result)
                except Exception as e:
                    logger.warning(f"Error processing search result: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"Error processing Brave Search response: {e}")
        
        return results
    
    def _process_news_response(self, data: Dict[str, Any]) -> List[BraveSearchResult]:
        """Process the response from Brave News API."""
        results = []
        
        try:
            news_results = data.get('news', [])
            
            for result_data in news_results:
                try:
                    result = BraveSearchResult(result_data)
                    results.append(result)
                except Exception as e:
                    logger.warning(f"Error processing news result: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"Error processing Brave News response: {e}")
        
        return results
    
    async def get_rate_limit_status(self) -> Dict[str, Any]:
        """Get current rate limit status."""
        return self.rate_limiter.get_stats("brave_search")
    
    def is_query_valid(self, query: str) -> bool:
        """Check if a search query is valid."""
        if not query or not query.strip():
            return False
        
        # Check for minimum length
        if len(query.strip()) < 2:
            return False
        
        # Check for excessive length
        if len(query) > 500:
            return False
        
        return True
    
    def build_author_search_query(self, author_name: str, additional_terms: List[str] = None) -> str:
        """Build an optimized search query for finding author content."""
        if not author_name:
            return ""
        
        # Clean author name
        author_name = author_name.strip()
        
        # Build query parts
        query_parts = [f'"{author_name}"']
        
        # Add content type terms
        content_terms = [
            'blog post',
            'article',
            'writing',
            'post',
            'published'
        ]
        
        if additional_terms:
            content_terms.extend(additional_terms)
        
        # Add content type filter
        content_filter = ' OR '.join([f'"{term}"' for term in content_terms])
        query_parts.append(f'({content_filter})')
        
        # Exclude non-content pages
        exclude_terms = [
            'contact',
            'about',
            'profile',
            'bio',
            'resume',
            'linkedin',
            'twitter'
        ]
        
        exclude_filter = ' OR '.join([f'-"{term}"' for term in exclude_terms])
        query_parts.append(exclude_filter)
        
        return ' '.join(query_parts)
