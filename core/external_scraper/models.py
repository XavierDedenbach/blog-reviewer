"""
Data models for external content scraping.
"""

from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, HttpUrl


class ScrapingStatus(str, Enum):
    """Status of a scraping job."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ContentType(str, Enum):
    """Type of content being scraped."""
    ARTICLE = "article"
    BLOG_POST = "blog_post"
    RSS_FEED = "rss_feed"
    WEBPAGE = "webpage"


class ScrapingError(BaseModel):
    """Error information for scraping failures."""
    
    error_type: str = Field(..., description="Type of error (network, parsing, rate_limit, etc.)")
    message: str = Field(..., description="Human-readable error message")
    url: Optional[str] = Field(None, description="URL that caused the error")
    status_code: Optional[int] = Field(None, description="HTTP status code if applicable")
    retry_count: int = Field(default=0, description="Number of retry attempts made")
    timestamp: datetime = Field(default_factory=datetime.now, description="When the error occurred")


class ContentMetadata(BaseModel):
    """Metadata extracted from scraped content."""
    
    title: Optional[str] = Field(None, description="Content title")
    author: Optional[str] = Field(None, description="Content author")
    published_date: Optional[datetime] = Field(None, description="Publication date")
    last_modified: Optional[datetime] = Field(None, description="Last modified date")
    language: Optional[str] = Field(default="en", description="Content language")
    word_count: Optional[int] = Field(None, description="Approximate word count")
    reading_time: Optional[int] = Field(None, description="Estimated reading time in minutes")
    tags: List[str] = Field(default=[], description="Content tags or categories")
    description: Optional[str] = Field(None, description="Content description or summary")
    canonical_url: Optional[str] = Field(None, description="Canonical URL if different from source")
    og_image: Optional[str] = Field(None, description="Open Graph image URL")
    og_description: Optional[str] = Field(None, description="Open Graph description")


class ScrapingResult(BaseModel):
    """Result of a content scraping operation."""
    
    url: str = Field(..., description="Source URL")
    content_type: ContentType = Field(..., description="Type of content scraped")
    content: str = Field(..., description="Extracted content (cleaned)")
    raw_html: Optional[str] = Field(None, description="Raw HTML content")
    metadata: ContentMetadata = Field(..., description="Extracted metadata")
    scraping_time: float = Field(..., description="Time taken to scrape in seconds")
    content_hash: str = Field(..., description="SHA-256 hash of content for deduplication")
    quality_score: Optional[float] = Field(None, ge=0, le=1, description="Content quality score (0-1)")
    errors: List[ScrapingError] = Field(default=[], description="Any errors encountered")
    is_duplicate: bool = Field(default=False, description="Whether this content is a duplicate")


class ScrapingConfig(BaseModel):
    """Configuration for scraping operations."""
    
    rate_limit_requests_per_minute: int = Field(default=60, description="Requests per minute limit")
    max_retries: int = Field(default=3, description="Maximum retry attempts for failed requests")
    timeout_seconds: int = Field(default=30, description="Request timeout in seconds")
    delay_between_requests: float = Field(default=1.0, description="Delay between requests in seconds")
    user_agent: str = Field(
        default="BlogReviewer/1.0 (https://github.com/blog-reviewer; contact@example.com)",
        description="User agent string for requests"
    )
    respect_robots_txt: bool = Field(default=True, description="Whether to respect robots.txt")
    extract_images: bool = Field(default=False, description="Whether to extract image URLs")
    extract_links: bool = Field(default=True, description="Whether to extract link URLs")
    min_content_length: int = Field(default=100, description="Minimum content length in characters")
    max_content_length: int = Field(default=100000, description="Maximum content length in characters")
    allowed_domains: List[str] = Field(default=[], description="List of allowed domains to scrape")
    blocked_domains: List[str] = Field(default=[], description="List of blocked domains")
    content_filters: List[str] = Field(default=[], description="Content filtering keywords")


class ScrapingJob(BaseModel):
    """A scraping job with configuration and status tracking."""
    
    job_id: str = Field(..., description="Unique job identifier")
    urls: List[str] = Field(..., description="URLs to scrape")
    config: ScrapingConfig = Field(..., description="Scraping configuration")
    status: ScrapingStatus = Field(default=ScrapingStatus.PENDING, description="Current job status")
    created_at: datetime = Field(default_factory=datetime.now, description="Job creation timestamp")
    started_at: Optional[datetime] = Field(None, description="When scraping started")
    completed_at: Optional[datetime] = Field(None, description="When scraping completed")
    progress: float = Field(default=0.0, ge=0, le=1, description="Progress percentage (0-1)")
    results: List[ScrapingResult] = Field(default=[], description="Scraping results")
    errors: List[ScrapingError] = Field(default=[], description="Job-level errors")
    total_urls: int = Field(..., description="Total number of URLs to process")
    processed_urls: int = Field(default=0, description="Number of URLs processed")
    successful_urls: int = Field(default=0, description="Number of successfully scraped URLs")
    failed_urls: int = Field(default=0, description="Number of failed URLs")
    metadata: Dict[str, Any] = Field(default={}, description="Additional job metadata")
