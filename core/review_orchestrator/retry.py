"""
Retry mechanism implementation for workflow orchestrator.
"""

import asyncio
import random
from typing import Callable, Any, Optional, Dict, List
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import logging

from .models import RetryPolicy


class RetryStrategy(Enum):
    """Retry strategy types."""
    FIXED_DELAY = "fixed_delay"
    EXPONENTIAL_BACKOFF = "exponential_backoff"
    LINEAR_BACKOFF = "linear_backoff"
    RANDOM_JITTER = "random_jitter"


@dataclass
class RetryContext:
    """Context for retry operations."""
    attempt: int
    max_attempts: int
    last_error: Optional[Exception]
    start_time: datetime
    total_delay: float
    strategy: RetryStrategy


class RetryHandler:
    """Handle retry logic for failed operations."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.retry_history: Dict[str, List[RetryContext]] = {}
    
    async def execute_with_retry(
        self,
        operation: Callable,
        retry_policy: RetryPolicy,
        operation_id: str,
        *args,
        **kwargs
    ) -> Any:
        """Execute an operation with retry logic."""
        
        context = RetryContext(
            attempt=0,
            max_attempts=retry_policy.max_attempts,
            last_error=None,
            start_time=datetime.utcnow(),
            total_delay=0.0,
            strategy=RetryStrategy(retry_policy.strategy)
        )
        
        while context.attempt < context.max_attempts:
            try:
                context.attempt += 1
                
                self.logger.debug(
                    f"Executing operation {operation_id}, attempt {context.attempt}/{context.max_attempts}"
                )
                
                # Execute the operation
                result = await operation(*args, **kwargs)
                
                # Success - log and return
                if context.attempt > 1:
                    self.logger.info(
                        f"Operation {operation_id} succeeded on attempt {context.attempt}"
                    )
                
                self._record_success(operation_id, context)
                return result
                
            except Exception as e:
                context.last_error = e
                
                # Check if this error should be retried
                if not self._should_retry_error(e, retry_policy):
                    self.logger.error(
                        f"Operation {operation_id} failed with non-retryable error: {e}"
                    )
                    self._record_failure(operation_id, context)
                    raise e
                
                # Check if we have more attempts
                if context.attempt >= context.max_attempts:
                    self.logger.error(
                        f"Operation {operation_id} failed after {context.attempt} attempts: {e}"
                    )
                    self._record_failure(operation_id, context)
                    raise e
                
                # Calculate delay and wait
                delay = self._calculate_delay(context, retry_policy)
                context.total_delay += delay
                
                self.logger.warning(
                    f"Operation {operation_id} failed on attempt {context.attempt}: {e}. "
                    f"Retrying in {delay:.2f}s"
                )
                
                await asyncio.sleep(delay)
        
        # Should not reach here, but just in case
        raise context.last_error or Exception("Max retry attempts exceeded")
    
    def _should_retry_error(self, error: Exception, retry_policy: RetryPolicy) -> bool:
        """Determine if an error should trigger a retry."""
        error_type = type(error).__name__
        
        # If no specific error types defined, retry all errors
        if not retry_policy.retryable_errors:
            return True
        
        return error_type in retry_policy.retryable_errors
    
    def _calculate_delay(self, context: RetryContext, retry_policy: RetryPolicy) -> float:
        """Calculate delay before next retry attempt."""
        base_delay = retry_policy.base_delay
        
        if context.strategy == RetryStrategy.FIXED_DELAY:
            return base_delay
        
        elif context.strategy == RetryStrategy.EXPONENTIAL_BACKOFF:
            delay = base_delay * (retry_policy.backoff_multiplier ** (context.attempt - 1))
            
        elif context.strategy == RetryStrategy.LINEAR_BACKOFF:
            delay = base_delay * context.attempt
            
        elif context.strategy == RetryStrategy.RANDOM_JITTER:
            jitter = random.uniform(0.5, 1.5)
            delay = base_delay * jitter
            
        else:
            delay = base_delay
        
        # Apply max delay limit
        if retry_policy.max_delay:
            delay = min(delay, retry_policy.max_delay)
        
        return delay
    
    def _record_success(self, operation_id: str, context: RetryContext):
        """Record successful operation."""
        if operation_id not in self.retry_history:
            self.retry_history[operation_id] = []
        
        self.retry_history[operation_id].append(context)
        
        # Keep only recent history (last 100 operations)
        if len(self.retry_history[operation_id]) > 100:
            self.retry_history[operation_id] = self.retry_history[operation_id][-100:]
    
    def _record_failure(self, operation_id: str, context: RetryContext):
        """Record failed operation."""
        if operation_id not in self.retry_history:
            self.retry_history[operation_id] = []
        
        self.retry_history[operation_id].append(context)
        
        # Keep only recent history
        if len(self.retry_history[operation_id]) > 100:
            self.retry_history[operation_id] = self.retry_history[operation_id][-100:]
    
    def get_retry_stats(self, operation_id: Optional[str] = None) -> Dict[str, Any]:
        """Get retry statistics."""
        if operation_id:
            history = self.retry_history.get(operation_id, [])
            return self._calculate_stats(history)
        
        # Overall stats
        all_history = []
        for histories in self.retry_history.values():
            all_history.extend(histories)
        
        return self._calculate_stats(all_history)
    
    def _calculate_stats(self, history: List[RetryContext]) -> Dict[str, Any]:
        """Calculate statistics from retry history."""
        if not history:
            return {
                'total_operations': 0,
                'successful_operations': 0,
                'failed_operations': 0,
                'avg_attempts': 0.0,
                'avg_total_delay': 0.0,
                'success_rate': 0.0
            }
        
        successful = len([ctx for ctx in history if ctx.last_error is None])
        failed = len(history) - successful
        
        avg_attempts = sum(ctx.attempt for ctx in history) / len(history)
        avg_delay = sum(ctx.total_delay for ctx in history) / len(history)
        
        return {
            'total_operations': len(history),
            'successful_operations': successful,
            'failed_operations': failed,
            'avg_attempts': avg_attempts,
            'avg_total_delay': avg_delay,
            'success_rate': successful / len(history) if history else 0.0
        }


# Convenience retry decorators
def retry_on_failure(retry_policy: RetryPolicy):
    """Decorator for adding retry logic to functions."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            retry_handler = RetryHandler()
            operation_id = f"{func.__module__}.{func.__name__}"
            return await retry_handler.execute_with_retry(
                func, retry_policy, operation_id, *args, **kwargs
            )
        return wrapper
    return decorator


def create_default_retry_policy() -> RetryPolicy:
    """Create a default retry policy."""
    return RetryPolicy(
        max_attempts=3,
        base_delay=1.0,
        backoff_multiplier=2.0,
        max_delay=30.0,
        strategy="exponential_backoff",
        retryable_errors=["TimeoutError", "ConnectionError", "TemporaryError"]
    )