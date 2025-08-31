"""
Unit tests for rate limiting utilities.
"""

import pytest
import asyncio
import time
from core.external_scraper.rate_limiter import RateLimiter, DelayedRateLimiter, RateLimit


class TestRateLimit:
    """Test RateLimit dataclass."""
    
    def test_rate_limit_creation(self):
        """Test creating RateLimit."""
        rate_limit = RateLimit(
            requests_per_minute=60,
            requests_per_hour=1000,
            requests_per_day=10000
        )
        
        assert rate_limit.requests_per_minute == 60
        assert rate_limit.requests_per_hour == 1000
        assert rate_limit.requests_per_day == 10000
    
    def test_rate_limit_minimal(self):
        """Test RateLimit with only per-minute limit."""
        rate_limit = RateLimit(requests_per_minute=30)
        
        assert rate_limit.requests_per_minute == 30
        assert rate_limit.requests_per_hour is None
        assert rate_limit.requests_per_day is None


class TestRateLimiter:
    """Test RateLimiter class."""
    
    @pytest.mark.asyncio
    async def test_rate_limiter_creation(self):
        """Test creating RateLimiter."""
        rate_limit = RateLimit(requests_per_minute=60)
        limiter = RateLimiter(rate_limit)
        
        assert limiter.rate_limit == rate_limit
        assert limiter.request_times == {}
    
    @pytest.mark.asyncio
    async def test_rate_limiter_acquire_single(self):
        """Test acquiring a single request."""
        rate_limit = RateLimit(requests_per_minute=60)
        limiter = RateLimiter(rate_limit)
        
        start_time = time.time()
        await limiter.acquire("test_key")
        end_time = time.time()
        
        # Should not delay for first request
        assert end_time - start_time < 0.1
        assert "test_key" in limiter.request_times
        assert len(limiter.request_times["test_key"]) == 1
    
    @pytest.mark.asyncio
    async def test_rate_limiter_acquire_multiple(self):
        """Test acquiring multiple requests within limit."""
        rate_limit = RateLimit(requests_per_minute=10)
        limiter = RateLimiter(rate_limit)
        
        start_time = time.time()
        
        # Make 5 requests (within limit)
        for i in range(5):
            await limiter.acquire("test_key")
        
        end_time = time.time()
        
        # Should not delay significantly
        assert end_time - start_time < 0.5
        assert len(limiter.request_times["test_key"]) == 5
    
    @pytest.mark.asyncio
    async def test_rate_limiter_exceed_limit(self):
        """Test exceeding rate limit causes delay."""
        rate_limit = RateLimit(requests_per_minute=2)  # Very low limit for testing
        limiter = RateLimiter(rate_limit)
        
        start_time = time.time()
        
        # Make 3 requests (exceeding limit)
        for i in range(3):
            await limiter.acquire("test_key")
        
        end_time = time.time()
        
        # Should delay when exceeding limit
        assert end_time - start_time > 0.5  # Should have some delay
        assert len(limiter.request_times["test_key"]) == 3
    
    @pytest.mark.asyncio
    async def test_rate_limiter_multiple_keys(self):
        """Test rate limiting with multiple keys."""
        rate_limit = RateLimit(requests_per_minute=5)
        limiter = RateLimiter(rate_limit)
        
        # Make requests with different keys
        await limiter.acquire("key1")
        await limiter.acquire("key2")
        await limiter.acquire("key1")
        
        assert "key1" in limiter.request_times
        assert "key2" in limiter.request_times
        assert len(limiter.request_times["key1"]) == 2
        assert len(limiter.request_times["key2"]) == 1
    
    @pytest.mark.asyncio
    async def test_rate_limiter_get_stats(self):
        """Test getting rate limiter statistics."""
        rate_limit = RateLimit(requests_per_minute=60, requests_per_hour=1000)
        limiter = RateLimiter(rate_limit)
        
        # Make some requests
        await limiter.acquire("test_key")
        await limiter.acquire("test_key")
        
        stats = limiter.get_stats("test_key")
        
        assert stats["requests_in_minute"] == 2
        assert stats["requests_in_hour"] == 2
        assert stats["requests_in_day"] == 2
        assert stats["rate_limit_per_minute"] == 60
        assert stats["rate_limit_per_hour"] == 1000
        assert stats["rate_limit_per_day"] is None
    
    @pytest.mark.asyncio
    async def test_rate_limiter_cleanup_old_requests(self):
        """Test that old requests are cleaned up."""
        rate_limit = RateLimit(requests_per_minute=60)
        limiter = RateLimiter(rate_limit)
        
        # Simulate old requests (more than 1 minute ago)
        old_time = time.time() - 70  # 70 seconds ago
        limiter.request_times["test_key"] = [old_time, old_time - 10]
        
        # Make a new request
        await limiter.acquire("test_key")
        
        # Old requests should be cleaned up
        assert len(limiter.request_times["test_key"]) == 1
        assert limiter.request_times["test_key"][0] > time.time() - 10


class TestDelayedRateLimiter:
    """Test DelayedRateLimiter class."""
    
    @pytest.mark.asyncio
    async def test_delayed_rate_limiter_creation(self):
        """Test creating DelayedRateLimiter."""
        limiter = DelayedRateLimiter(delay_seconds=1.0)
        
        assert limiter.delay_seconds == 1.0
        assert limiter.last_request_time == {}
    
    @pytest.mark.asyncio
    async def test_delayed_rate_limiter_first_request(self):
        """Test first request has no delay."""
        limiter = DelayedRateLimiter(delay_seconds=1.0)
        
        start_time = time.time()
        await limiter.acquire("test_key")
        end_time = time.time()
        
        # First request should not delay
        assert end_time - start_time < 0.1
        assert "test_key" in limiter.last_request_time
    
    @pytest.mark.asyncio
    async def test_delayed_rate_limiter_subsequent_requests(self):
        """Test subsequent requests respect delay."""
        limiter = DelayedRateLimiter(delay_seconds=0.1)  # Short delay for testing
        
        # First request
        await limiter.acquire("test_key")
        
        # Second request should delay
        start_time = time.time()
        await limiter.acquire("test_key")
        end_time = time.time()
        
        # Should have some delay
        assert end_time - start_time >= 0.05  # Allow some tolerance
    
    @pytest.mark.asyncio
    async def test_delayed_rate_limiter_multiple_keys(self):
        """Test delay enforcement with multiple keys."""
        limiter = DelayedRateLimiter(delay_seconds=0.1)
        
        # Make requests with different keys
        await limiter.acquire("key1")
        await limiter.acquire("key2")
        
        # Should not delay between different keys
        start_time = time.time()
        await limiter.acquire("key1")
        end_time = time.time()
        
        # Should delay for same key
        assert end_time - start_time >= 0.05
    
    @pytest.mark.asyncio
    async def test_delayed_rate_limiter_get_stats(self):
        """Test getting delay statistics."""
        limiter = DelayedRateLimiter(delay_seconds=1.0)
        
        # Make a request
        await limiter.acquire("test_key")
        
        # Wait a bit
        await asyncio.sleep(0.1)
        
        stats = limiter.get_stats("test_key")
        
        assert "time_since_last_request" in stats
        assert "delay_seconds" in stats
        assert stats["delay_seconds"] == 1.0
        assert stats["time_since_last_request"] > 0
    
    @pytest.mark.asyncio
    async def test_delayed_rate_limiter_no_delay_after_wait(self):
        """Test no delay when enough time has passed."""
        limiter = DelayedRateLimiter(delay_seconds=0.1)
        
        # First request
        await limiter.acquire("test_key")
        
        # Wait longer than delay
        await asyncio.sleep(0.2)
        
        # Second request should not delay
        start_time = time.time()
        await limiter.acquire("test_key")
        end_time = time.time()
        
        # Should not delay significantly
        assert end_time - start_time < 0.05
