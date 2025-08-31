"""
Unit tests for external scraper models.
"""

import pytest
from datetime import datetime
from core.external_scraper.models import (
    ScrapingStatus, ContentType, ScrapingError, ContentMetadata,
    ScrapingResult, ScrapingConfig, ScrapingJob
)


class TestScrapingStatus:
    """Test ScrapingStatus enum."""
    
    def test_scraping_status_values(self):
        """Test that all expected status values exist."""
        assert ScrapingStatus.PENDING == "pending"
        assert ScrapingStatus.IN_PROGRESS == "in_progress"
        assert ScrapingStatus.COMPLETED == "completed"
        assert ScrapingStatus.FAILED == "failed"
        assert ScrapingStatus.CANCELLED == "cancelled"


class TestContentType:
    """Test ContentType enum."""
    
    def test_content_type_values(self):
        """Test that all expected content type values exist."""
        assert ContentType.ARTICLE == "article"
        assert ContentType.BLOG_POST == "blog_post"
        assert ContentType.RSS_FEED == "rss_feed"
        assert ContentType.WEBPAGE == "webpage"


class TestScrapingError:
    """Test ScrapingError model."""
    
    def test_scraping_error_creation(self):
        """Test creating a ScrapingError."""
        error = ScrapingError(
            error_type="network",
            message="Connection timeout",
            url="https://example.com",
            status_code=408,
            retry_count=2
        )
        
        assert error.error_type == "network"
        assert error.message == "Connection timeout"
        assert error.url == "https://example.com"
        assert error.status_code == 408
        assert error.retry_count == 2
        assert isinstance(error.timestamp, datetime)
    
    def test_scraping_error_defaults(self):
        """Test ScrapingError with default values."""
        error = ScrapingError(
            error_type="api",
            message="API error"
        )
        
        assert error.error_type == "api"
        assert error.message == "API error"
        assert error.url is None
        assert error.status_code is None
        assert error.retry_count == 0
        assert isinstance(error.timestamp, datetime)


class TestContentMetadata:
    """Test ContentMetadata model."""
    
    def test_content_metadata_creation(self):
        """Test creating ContentMetadata."""
        metadata = ContentMetadata(
            title="Test Article",
            author="John Doe",
            published_date=datetime(2024, 1, 1),
            language="en",
            word_count=1000,
            reading_time=5,
            tags=["technology", "programming"],
            description="A test article"
        )
        
        assert metadata.title == "Test Article"
        assert metadata.author == "John Doe"
        assert metadata.published_date == datetime(2024, 1, 1)
        assert metadata.language == "en"
        assert metadata.word_count == 1000
        assert metadata.reading_time == 5
        assert metadata.tags == ["technology", "programming"]
        assert metadata.description == "A test article"
    
    def test_content_metadata_defaults(self):
        """Test ContentMetadata with default values."""
        metadata = ContentMetadata()
        
        assert metadata.title is None
        assert metadata.author is None
        assert metadata.published_date is None
        assert metadata.language == "en"
        assert metadata.word_count is None
        assert metadata.reading_time is None
        assert metadata.tags == []
        assert metadata.description is None


class TestScrapingResult:
    """Test ScrapingResult model."""
    
    def test_scraping_result_creation(self):
        """Test creating ScrapingResult."""
        metadata = ContentMetadata(title="Test Article")
        error = ScrapingError(error_type="test", message="Test error")
        
        result = ScrapingResult(
            url="https://example.com",
            content_type=ContentType.ARTICLE,
            content="Test content",
            raw_html="<html>Test</html>",
            metadata=metadata,
            scraping_time=1.5,
            content_hash="abc123",
            quality_score=0.9,
            errors=[error],
            is_duplicate=False
        )
        
        assert result.url == "https://example.com"
        assert result.content_type == ContentType.ARTICLE
        assert result.content == "Test content"
        assert result.raw_html == "<html>Test</html>"
        assert result.metadata == metadata
        assert result.scraping_time == 1.5
        assert result.content_hash == "abc123"
        assert result.quality_score == 0.9
        assert result.errors == [error]
        assert result.is_duplicate is False
    
    def test_scraping_result_defaults(self):
        """Test ScrapingResult with default values."""
        metadata = ContentMetadata()
        result = ScrapingResult(
            url="https://example.com",
            content_type=ContentType.WEBPAGE,
            content="Test content",
            metadata=metadata,
            scraping_time=1.0,
            content_hash="abc123"
        )
        
        assert result.raw_html is None
        assert result.quality_score is None
        assert result.errors == []
        assert result.is_duplicate is False


class TestScrapingConfig:
    """Test ScrapingConfig model."""
    
    def test_scraping_config_creation(self):
        """Test creating ScrapingConfig."""
        config = ScrapingConfig(
            rate_limit_requests_per_minute=30,
            max_retries=5,
            timeout_seconds=60,
            delay_between_requests=2.0,
            user_agent="Custom Agent",
            respect_robots_txt=False,
            extract_images=True,
            extract_links=False,
            min_content_length=200,
            max_content_length=50000,
            allowed_domains=["example.com"],
            blocked_domains=["spam.com"],
            content_filters=["advertisement"]
        )
        
        assert config.rate_limit_requests_per_minute == 30
        assert config.max_retries == 5
        assert config.timeout_seconds == 60
        assert config.delay_between_requests == 2.0
        assert config.user_agent == "Custom Agent"
        assert config.respect_robots_txt is False
        assert config.extract_images is True
        assert config.extract_links is False
        assert config.min_content_length == 200
        assert config.max_content_length == 50000
        assert config.allowed_domains == ["example.com"]
        assert config.blocked_domains == ["spam.com"]
        assert config.content_filters == ["advertisement"]
    
    def test_scraping_config_defaults(self):
        """Test ScrapingConfig with default values."""
        config = ScrapingConfig()
        
        assert config.rate_limit_requests_per_minute == 60
        assert config.max_retries == 3
        assert config.timeout_seconds == 30
        assert config.delay_between_requests == 1.0
        assert "BlogReviewer" in config.user_agent
        assert config.respect_robots_txt is True
        assert config.extract_images is False
        assert config.extract_links is True
        assert config.min_content_length == 100
        assert config.max_content_length == 100000
        assert config.allowed_domains == []
        assert config.blocked_domains == []
        assert config.content_filters == []


class TestScrapingJob:
    """Test ScrapingJob model."""
    
    def test_scraping_job_creation(self):
        """Test creating ScrapingJob."""
        config = ScrapingConfig()
        metadata = {"author": "John Doe"}
        
        job = ScrapingJob(
            job_id="test-job-123",
            urls=["https://example.com", "https://test.com"],
            config=config,
            status=ScrapingStatus.PENDING,
            created_at=datetime(2024, 1, 1),
            started_at=datetime(2024, 1, 1, 12, 0),
            completed_at=datetime(2024, 1, 1, 12, 5),
            progress=0.5,
            results=[],
            errors=[],
            total_urls=2,
            processed_urls=1,
            successful_urls=1,
            failed_urls=0,
            metadata=metadata
        )
        
        assert job.job_id == "test-job-123"
        assert job.urls == ["https://example.com", "https://test.com"]
        assert job.config == config
        assert job.status == ScrapingStatus.PENDING
        assert job.created_at == datetime(2024, 1, 1)
        assert job.started_at == datetime(2024, 1, 1, 12, 0)
        assert job.completed_at == datetime(2024, 1, 1, 12, 5)
        assert job.progress == 0.5
        assert job.results == []
        assert job.errors == []
        assert job.total_urls == 2
        assert job.processed_urls == 1
        assert job.successful_urls == 1
        assert job.failed_urls == 0
        assert job.metadata == metadata
    
    def test_scraping_job_defaults(self):
        """Test ScrapingJob with default values."""
        config = ScrapingConfig()
        job = ScrapingJob(
            job_id="test-job-123",
            urls=["https://example.com"],
            config=config,
            total_urls=1
        )
        
        assert job.status == ScrapingStatus.PENDING
        assert isinstance(job.created_at, datetime)
        assert job.started_at is None
        assert job.completed_at is None
        assert job.progress == 0.0
        assert job.results == []
        assert job.errors == []
        assert job.processed_urls == 0
        assert job.successful_urls == 0
        assert job.failed_urls == 0
        assert job.metadata == {}
