"""
Rate limiting utilities for external API requests.
"""

import asyncio
import time
from typing import Dict, Optional, Callable, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class RateLimit:
    """Rate limit configuration."""
    requests_per_minute: int
    requests_per_hour: Optional[int] = None
    requests_per_day: Optional[int] = None


class RateLimiter:
    """Rate limiter for managing API request rates."""
    
    def __init__(self, rate_limit: RateLimit):
        self.rate_limit = rate_limit
        self.request_times: Dict[str, list] = {}
        self.lock = asyncio.Lock()
    
    async def acquire(self, key: str = "default") -> None:
        """Acquire permission to make a request."""
        async with self.lock:
            current_time = time.time()
            
            # Initialize request times for this key
            if key not in self.request_times:
                self.request_times[key] = []
            
            # Clean old request times
            self._clean_old_requests(key, current_time)
            
            # Check rate limits
            await self._check_rate_limits(key, current_time)
            
            # Record this request
            self.request_times[key].append(current_time)
    
    def _clean_old_requests(self, key: str, current_time: float) -> None:
        """Remove old request times that are no longer relevant."""
        if key not in self.request_times:
            return
            
        request_times = self.request_times[key]
        
        # Remove requests older than 1 minute
        cutoff_time = current_time - 60
        request_times[:] = [t for t in request_times if t > cutoff_time]
        
        # Remove requests older than 1 hour if hourly limit is set
        if self.rate_limit.requests_per_hour:
            cutoff_time = current_time - 3600
            request_times[:] = [t for t in request_times if t > cutoff_time]
        
        # Remove requests older than 1 day if daily limit is set
        if self.rate_limit.requests_per_day:
            cutoff_time = current_time - 86400
            request_times[:] = [t for t in request_times if t > cutoff_time]
    
    async def _check_rate_limits(self, key: str, current_time: float) -> None:
        """Check if rate limits would be exceeded."""
        request_times = self.request_times[key]
        
        # Check per-minute limit
        minute_ago = current_time - 60
        requests_in_minute = len([t for t in request_times if t > minute_ago])
        
        if requests_in_minute >= self.rate_limit.requests_per_minute:
            wait_time = 60 - (current_time - request_times[0])
            if wait_time > 0:
                logger.info(f"Rate limit exceeded for {key}, waiting {wait_time:.2f} seconds")
                await asyncio.sleep(wait_time)
        
        # Check per-hour limit
        if self.rate_limit.requests_per_hour:
            hour_ago = current_time - 3600
            requests_in_hour = len([t for t in request_times if t > hour_ago])
            
            if requests_in_hour >= self.rate_limit.requests_per_hour:
                wait_time = 3600 - (current_time - request_times[0])
                if wait_time > 0:
                    logger.info(f"Hourly rate limit exceeded for {key}, waiting {wait_time:.2f} seconds")
                    await asyncio.sleep(wait_time)
        
        # Check per-day limit
        if self.rate_limit.requests_per_day:
            day_ago = current_time - 86400
            requests_in_day = len([t for t in request_times if t > day_ago])
            
            if requests_in_day >= self.rate_limit.requests_per_day:
                wait_time = 86400 - (current_time - request_times[0])
                if wait_time > 0:
                    logger.info(f"Daily rate limit exceeded for {key}, waiting {wait_time:.2f} seconds")
                    await asyncio.sleep(wait_time)
    
    def get_stats(self, key: str = "default") -> Dict[str, Any]:
        """Get rate limiting statistics."""
        current_time = time.time()
        request_times = self.request_times.get(key, [])
        
        # Clean old requests for accurate stats
        self._clean_old_requests(key, current_time)
        
        minute_ago = current_time - 60
        hour_ago = current_time - 3600
        day_ago = current_time - 86400
        
        return {
            "requests_in_minute": len([t for t in request_times if t > minute_ago]),
            "requests_in_hour": len([t for t in request_times if t > hour_ago]),
            "requests_in_day": len([t for t in request_times if t > day_ago]),
            "rate_limit_per_minute": self.rate_limit.requests_per_minute,
            "rate_limit_per_hour": self.rate_limit.requests_per_hour,
            "rate_limit_per_day": self.rate_limit.requests_per_day,
        }


class DelayedRateLimiter:
    """Rate limiter that enforces delays between requests."""
    
    def __init__(self, delay_seconds: float = 1.0):
        self.delay_seconds = delay_seconds
        self.last_request_time: Dict[str, float] = {}
        self.lock = asyncio.Lock()
    
    async def acquire(self, key: str = "default") -> None:
        """Acquire permission to make a request with delay enforcement."""
        async with self.lock:
            current_time = time.time()
            last_time = self.last_request_time.get(key, 0)
            
            time_since_last = current_time - last_time
            if time_since_last < self.delay_seconds:
                wait_time = self.delay_seconds - time_since_last
                logger.debug(f"Enforcing delay for {key}, waiting {wait_time:.2f} seconds")
                await asyncio.sleep(wait_time)
            
            self.last_request_time[key] = time.time()
    
    def get_stats(self, key: str = "default") -> Dict[str, Any]:
        """Get delay statistics."""
        current_time = time.time()
        last_time = self.last_request_time.get(key, 0)
        
        return {
            "time_since_last_request": current_time - last_time,
            "delay_seconds": self.delay_seconds,
        }
