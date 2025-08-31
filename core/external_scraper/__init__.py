"""
External Content Scraping System for the Blog Reviewer.

This module provides web scraping capabilities for extracting blog posts and articles
from external sources with rate limiting, error handling, and content normalization.
"""

from .scraper import ExternalScraper
from .firecrawl_client import FirecrawlClient
from .brave_search_client import BraveSearchClient
from .content_processor import ContentProcessor
from .rate_limiter import RateLimiter
from .models import (
    ScrapingJob,
    ScrapingResult,
    ContentMetadata,
    ScrapingConfig,
    ScrapingError
)

__all__ = [
    'ExternalScraper',
    'FirecrawlClient', 
    'BraveSearchClient',
    'ContentProcessor',
    'RateLimiter',
    'ScrapingJob',
    'ScrapingResult',
    'ContentMetadata',
    'ScrapingConfig',
    'ScrapingError'
]
