"""
Error handling and recovery for workflow orchestrator.
"""

import logging
from typing import Dict, Any, Optional, Callable
from datetime import datetime
from .models import WorkflowStatus
from .exceptions import WorkflowError, TaskExecutionError, TemporaryError

logger = logging.getLogger(__name__)


class WorkflowErrorHandler:
    """
    Handles errors and recovery strategies for workflow execution.

    Provides centralized error handling with configurable recovery strategies,
    error classification, and monitoring capabilities.
    """

    def __init__(self):
        self.error_handlers: Dict[str, Callable] = {}
        self.recovery_strategies: Dict[str, Callable] = {}
        self.error_counts: Dict[str, int] = {}
        self._setup_default_handlers()

    def _setup_default_handlers(self):
        """Set up default error handlers for common error types."""
        self.register_error_handler("TimeoutError", self._handle_timeout_error)
        self.register_error_handler("ConnectionError", self._handle_connection_error)
        self.register_error_handler("ValueError", self._handle_validation_error)
        self.register_error_handler("TemporaryError", self._handle_temporary_error)

        self.register_recovery_strategy("retry", self._retry_recovery)
        self.register_recovery_strategy("skip", self._skip_recovery)
        self.register_recovery_strategy("fail", self._fail_recovery)

    def register_error_handler(self, error_type: str, handler: Callable):
        """Register a custom error handler for specific error types."""
        self.error_handlers[error_type] = handler
        logger.debug(f"Registered error handler for {error_type}")

    def register_recovery_strategy(self, strategy_name: str, strategy: Callable):
        """Register a recovery strategy."""
        self.recovery_strategies[strategy_name] = strategy
        logger.debug(f"Registered recovery strategy: {strategy_name}")

    async def handle_error(self, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle an error with appropriate recovery strategy.

        Args:
            error: The exception that occurred
            context: Context information about the error

        Returns:
            Dict containing recovery action and metadata
        """
        error_type = type(error).__name__
        self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1

        logger.warning(f"Handling error {error_type}: {error}")

        # Try specific error handler first
        if error_type in self.error_handlers:
            return await self.error_handlers[error_type](error, context)

        # Fall back to generic handler
        return await self._handle_generic_error(error, context)

    async def _handle_timeout_error(self, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle timeout errors with retry strategy."""
        return {
            "action": "retry",
            "delay": 5.0,
            "max_attempts": 3,
            "reason": "Timeout occurred, will retry"
        }

    async def _handle_connection_error(self, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle connection errors with exponential backoff."""
        return {
            "action": "retry",
            "delay": 2.0,
            "max_attempts": 5,
            "backoff_multiplier": 2.0,
            "reason": "Connection error, will retry with backoff"
        }

    async def _handle_validation_error(self, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle validation errors - typically not recoverable."""
        return {
            "action": "fail",
            "reason": f"Validation error: {error}"
        }

    async def _handle_temporary_error(self, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle temporary errors with retry."""
        return {
            "action": "retry",
            "delay": 1.0,
            "max_attempts": 3,
            "reason": "Temporary error, will retry"
        }

    async def _handle_generic_error(self, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle generic errors."""
        # Check if it's a temporary error
        if isinstance(error, TemporaryError):
            return await self._handle_temporary_error(error, context)

        # Default to failure for unknown errors
        return {
            "action": "fail",
            "reason": f"Unhandled error: {error}"
        }

    async def _retry_recovery(self, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """Retry recovery strategy."""
        attempt = context.get("attempt", 0)
        max_attempts = context.get("max_attempts", 3)
        delay = context.get("delay", 1.0)
        backoff_multiplier = context.get("backoff_multiplier", 1.0)

        if attempt < max_attempts:
            actual_delay = delay * (backoff_multiplier ** attempt)
            return {
                "action": "retry",
                "delay": actual_delay,
                "next_attempt": attempt + 1
            }

        return {
            "action": "fail",
            "reason": f"Max retry attempts ({max_attempts}) exceeded"
        }

    async def _skip_recovery(self, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """Skip recovery strategy - mark as completed but log the error."""
        return {
            "action": "skip",
            "reason": f"Skipping error: {error}"
        }

    async def _fail_recovery(self, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """Fail recovery strategy - propagate the error."""
        return {
            "action": "fail",
            "reason": f"Error handling failed: {error}"
        }

    def get_error_stats(self) -> Dict[str, Any]:
        """Get error statistics."""
        return {
            "total_errors": sum(self.error_counts.values()),
            "error_types": self.error_counts.copy(),
            "most_common_error": max(self.error_counts.items(), key=lambda x: x[1], default=(None, 0))
        }

    async def execute_with_error_handling(self, operation: Callable, context: Dict[str, Any]) -> Any:
        """
        Execute an operation with error handling.

        Args:
            operation: The operation to execute
            context: Context for error handling

        Returns:
            Result of the operation
        """
        try:
            return await operation()
        except Exception as e:
            recovery_action = await self.handle_error(e, context)

            if recovery_action["action"] == "retry":
                # Implement retry logic here
                logger.info(f"Retrying operation due to: {recovery_action['reason']}")
                # This would typically involve scheduling a retry
                raise e  # For now, re-raise

            elif recovery_action["action"] == "skip":
                logger.warning(f"Skipping operation due to: {recovery_action['reason']}")
                return None

            else:  # fail
                logger.error(f"Failing operation due to: {recovery_action['reason']}")
                raise e
