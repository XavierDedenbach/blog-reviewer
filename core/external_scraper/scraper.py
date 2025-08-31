"""
Main external scraper orchestrator.
"""

import asyncio
import uuid
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime
import logging

from .models import (
    ScrapingJob, ScrapingResult, ScrapingConfig, ScrapingStatus,
    ScrapingError, ContentType, ContentMetadata
)
from .firecrawl_client import FirecrawlClient
from .brave_search_client import BraveSearchClient
from .content_processor import ContentProcessor
from .rate_limiter import DelayedRateLimiter

logger = logging.getLogger(__name__)


class ExternalScraper:
    """Main external scraper orchestrator."""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        
        # Initialize components
        self.firecrawl_client: Optional[FirecrawlClient] = None
        self.brave_search_client: Optional[BraveSearchClient] = None
        self.content_processor = ContentProcessor()
        self.delay_limiter = DelayedRateLimiter(delay_seconds=1.0)
        
        # Active jobs
        self.active_jobs: Dict[str, ScrapingJob] = {}
        
        # Content deduplication cache
        self.content_hashes: set = set()
        
        # Progress callback
        self.progress_callback: Optional[Callable[[str, float], None]] = None
    
    async def initialize(self, firecrawl_api_key: str, brave_search_api_key: str):
        """Initialize the scraper with API keys."""
        self.firecrawl_client = FirecrawlClient(firecrawl_api_key)
        self.brave_search_client = BraveSearchClient(brave_search_api_key)
        
        # Initialize clients
        await self.firecrawl_client.__aenter__()
        await self.brave_search_client.__aenter__()
        
        logger.info("External scraper initialized successfully")
    
    async def cleanup(self):
        """Clean up resources."""
        if self.firecrawl_client:
            await self.firecrawl_client.__aexit__(None, None, None)
        
        if self.brave_search_client:
            await self.brave_search_client.__aexit__(None, None, None)
        
        logger.info("External scraper cleaned up")
    
    async def create_scraping_job(
        self,
        urls: List[str],
        config: ScrapingConfig = None,
        metadata: Dict[str, Any] = None
    ) -> ScrapingJob:
        """Create a new scraping job."""
        job_id = str(uuid.uuid4())
        
        if config is None:
            config = ScrapingConfig()
        
        job = ScrapingJob(
            job_id=job_id,
            urls=urls,
            config=config,
            total_urls=len(urls),
            metadata=metadata or {}
        )
        
        self.active_jobs[job_id] = job
        logger.info(f"Created scraping job {job_id} with {len(urls)} URLs")
        
        return job
    
    async def execute_job(self, job_id: str) -> ScrapingJob:
        """Execute a scraping job."""
        if job_id not in self.active_jobs:
            raise ValueError(f"Job {job_id} not found")
        
        job = self.active_jobs[job_id]
        job.status = ScrapingStatus.IN_PROGRESS
        job.started_at = datetime.now()
        
        logger.info(f"Starting scraping job {job_id}")
        
        try:
            # Process URLs in batches
            batch_size = 5  # Process 5 URLs at a time
            total_urls = len(job.urls)
            
            for i in range(0, total_urls, batch_size):
                batch_urls = job.urls[i:i + batch_size]
                
                # Scrape batch
                batch_results = await self._scrape_urls_batch(batch_urls, job.config)
                
                # Process results
                for result in batch_results:
                    if result.errors:
                        job.failed_urls += 1
                        job.errors.extend(result.errors)
                    else:
                        job.successful_urls += 1
                    
                    job.results.append(result)
                    job.processed_urls += 1
                
                # Update progress
                progress = job.processed_urls / job.total_urls
                job.progress = progress
                
                # Call progress callback
                if self.progress_callback:
                    self.progress_callback(job_id, progress)
                
                # Apply delay between batches
                if i + batch_size < total_urls:
                    await asyncio.sleep(job.config.delay_between_requests)
            
            # Mark job as completed
            job.status = ScrapingStatus.COMPLETED
            job.completed_at = datetime.now()
            
            logger.info(f"Completed scraping job {job_id}: {job.successful_urls} successful, {job.failed_urls} failed")
            
        except Exception as e:
            job.status = ScrapingStatus.FAILED
            job.completed_at = datetime.now()
            
            error = ScrapingError(
                error_type="job_execution",
                message=f"Job execution failed: {str(e)}",
                retry_count=0
            )
            job.errors.append(error)
            
            logger.error(f"Failed scraping job {job_id}: {e}")
        
        return job
    
    async def _scrape_urls_batch(self, urls: List[str], config: ScrapingConfig) -> List[ScrapingResult]:
        """Scrape a batch of URLs."""
        if not self.firecrawl_client:
            raise RuntimeError("Firecrawl client not initialized")
        
        # Apply delay between requests
        await self.delay_limiter.acquire("scraping")
        
        # Scrape URLs concurrently
        results = await self.firecrawl_client.scrape_multiple_urls(urls)
        
        # Process and validate results
        processed_results = []
        for result in results:
            processed_result = await self._process_scraping_result(result, config)
            processed_results.append(processed_result)
        
        return processed_results
    
    async def _process_scraping_result(self, result: ScrapingResult, config: ScrapingConfig) -> ScrapingResult:
        """Process and validate a scraping result."""
        if not result.content:
            return result
        
        # Check content length
        if len(result.content) < config.min_content_length:
            error = ScrapingError(
                error_type="content_validation",
                message=f"Content too short ({len(result.content)} chars, minimum {config.min_content_length})",
                url=result.url,
                retry_count=0
            )
            result.errors.append(error)
            return result
        
        if len(result.content) > config.max_content_length:
            error = ScrapingError(
                error_type="content_validation",
                message=f"Content too long ({len(result.content)} chars, maximum {config.max_content_length})",
                url=result.url,
                retry_count=0
            )
            result.errors.append(error)
            return result
        
        # Check for duplicates
        if result.content_hash in self.content_hashes:
            result.is_duplicate = True
            error = ScrapingError(
                error_type="duplicate_content",
                message="Content is a duplicate",
                url=result.url,
                retry_count=0
            )
            result.errors.append(error)
        else:
            self.content_hashes.add(result.content_hash)
        
        # Validate content quality
        quality_score, issues = self.content_processor.validate_content_quality(
            result.content, result.metadata.model_dump()
        )
        result.quality_score = quality_score
        
        # Add quality issues to errors
        for issue in issues:
            error = ScrapingError(
                error_type="quality_issue",
                message=issue,
                url=result.url,
                retry_count=0
            )
            result.errors.append(error)
        
        return result
    
    async def discover_author_content(
        self,
        author_name: str,
        domain: str = None,
        max_results: int = 20
    ) -> List[ScrapingResult]:
        """Discover content by a specific author."""
        if not self.brave_search_client:
            raise RuntimeError("Brave Search client not initialized")
        
        logger.info(f"Discovering content for author: {author_name}")
        
        # Search for author content
        search_results = await self.brave_search_client.search_author_content(
            author_name, domain, {'count': max_results}
        )
        
        # Extract URLs
        urls = [result.url for result in search_results if result.url]
        
        if not urls:
            logger.warning(f"No content found for author: {author_name}")
            return []
        
        # Scrape discovered URLs
        config = ScrapingConfig()
        job = await self.create_scraping_job(urls, config, {'author_name': author_name})
        await self.execute_job(job.job_id)
        
        return job.results
    
    async def search_and_scrape(
        self,
        query: str,
        max_results: int = 10,
        config: ScrapingConfig = None
    ) -> List[ScrapingResult]:
        """Search for content and scrape the results."""
        if not self.brave_search_client:
            raise RuntimeError("Brave Search client not initialized")
        
        logger.info(f"Searching and scraping for query: {query}")
        
        # Search for content
        search_results = await self.brave_search_client.search(
            query, {'count': max_results}
        )
        
        # Extract URLs
        urls = [result.url for result in search_results if result.url]
        
        if not urls:
            logger.warning(f"No results found for query: {query}")
            return []
        
        # Scrape discovered URLs
        if config is None:
            config = ScrapingConfig()
        
        job = await self.create_scraping_job(urls, config, {'search_query': query})
        await self.execute_job(job.job_id)
        
        return job.results
    
    async def scrape_rss_feed(self, feed_url: str, config: ScrapingConfig = None) -> List[ScrapingResult]:
        """Scrape content from an RSS feed."""
        # For now, we'll use the basic scraping approach
        # In the future, we could add a dedicated RSS parser
        return await self.search_and_scrape(f'site:{feed_url}', 20, config)
    
    def get_job_status(self, job_id: str) -> Optional[ScrapingJob]:
        """Get the status of a scraping job."""
        return self.active_jobs.get(job_id)
    
    def list_jobs(self, status: ScrapingStatus = None) -> List[ScrapingJob]:
        """List all jobs, optionally filtered by status."""
        jobs = list(self.active_jobs.values())
        
        if status:
            jobs = [job for job in jobs if job.status == status]
        
        return jobs
    
    def cancel_job(self, job_id: str) -> bool:
        """Cancel a scraping job."""
        if job_id not in self.active_jobs:
            return False
        
        job = self.active_jobs[job_id]
        if job.status in [ScrapingStatus.PENDING, ScrapingStatus.IN_PROGRESS]:
            job.status = ScrapingStatus.CANCELLED
            job.completed_at = datetime.now()
            logger.info(f"Cancelled scraping job {job_id}")
            return True
        
        return False
    
    def set_progress_callback(self, callback: Callable[[str, float], None]):
        """Set a callback function for progress updates."""
        self.progress_callback = callback
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get system status and statistics."""
        status = {
            'active_jobs': len([j for j in self.active_jobs.values() if j.status == ScrapingStatus.IN_PROGRESS]),
            'total_jobs': len(self.active_jobs),
            'content_hashes': len(self.content_hashes),
            'firecrawl_available': self.firecrawl_client is not None,
            'brave_search_available': self.brave_search_client is not None
        }
        
        # Add rate limit status
        if self.firecrawl_client:
            status['firecrawl_rate_limit'] = await self.firecrawl_client.get_rate_limit_status()
        
        if self.brave_search_client:
            status['brave_search_rate_limit'] = await self.brave_search_client.get_rate_limit_status()
        
        return status
    
    def clear_job_history(self, older_than_days: int = 7):
        """Clear old job history."""
        cutoff_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        cutoff_date = cutoff_date.replace(day=cutoff_date.day - older_than_days)
        
        jobs_to_remove = []
        for job_id, job in self.active_jobs.items():
            if job.created_at < cutoff_date:
                jobs_to_remove.append(job_id)
        
        for job_id in jobs_to_remove:
            del self.active_jobs[job_id]
        
        logger.info(f"Cleared {len(jobs_to_remove)} old jobs")
    
    def get_content_statistics(self) -> Dict[str, Any]:
        """Get content scraping statistics."""
        total_results = sum(len(job.results) for job in self.active_jobs.values())
        successful_results = sum(
            len([r for r in job.results if not r.errors])
            for job in self.active_jobs.values()
        )
        failed_results = total_results - successful_results
        
        return {
            'total_results': total_results,
            'successful_results': successful_results,
            'failed_results': failed_results,
            'success_rate': successful_results / total_results if total_results > 0 else 0,
            'unique_content_hashes': len(self.content_hashes),
            'total_jobs': len(self.active_jobs)
        }
