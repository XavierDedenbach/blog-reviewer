"""
Unit tests for error handling system.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, Mock, patch
from datetime import datetime
from bson import ObjectId

from core.review_orchestrator.error_handler import WorkflowErrorHandler
from core.review_orchestrator.models import TaskDefinition, RetryPolicy


class TestWorkflowErrorHandler:
    """Test WorkflowErrorHandler class."""
    
    @pytest.fixture
    def mock_logger(self):
        """Create mock logger."""
        return Mock()
    
    @pytest.fixture
    def error_handler(self, mock_logger):
        """Create WorkflowErrorHandler instance."""
        return WorkflowErrorHandler(logger=mock_logger)
    
    @pytest.mark.asyncio
    async def test_handle_task_error_with_retry(self, error_handler):
        """Test handling task error with retry."""
        task_id = ObjectId()
        error = Exception("Test error")
        retry_policy = RetryPolicy(max_retries=3, backoff_multiplier=2.0)
        
        result = await error_handler.handle_task_error(
            task_id, error, retry_count=1, retry_policy=retry_policy
        )
        
        assert result.should_retry is True
        assert result.delay > 0
        assert result.retry_count == 2
    
    @pytest.mark.asyncio
    async def test_handle_task_error_max_retries_reached(self, error_handler):
        """Test handling task error when max retries reached."""
        task_id = ObjectId()
        error = Exception("Test error")
        retry_policy = RetryPolicy(max_retries=3, backoff_multiplier=2.0)
        
        result = await error_handler.handle_task_error(
            task_id, error, retry_count=3, retry_policy=retry_policy
        )
        
        assert result.should_retry is False
        assert result.is_fatal is True
    
    @pytest.mark.asyncio
    async def test_handle_workflow_error(self, error_handler, mock_logger):
        """Test handling workflow-level error."""
        workflow_id = ObjectId()
        error = RuntimeError("Workflow failed")
        
        await error_handler.handle_workflow_error(workflow_id, error)
        
        # Verify error was logged
        mock_logger.error.assert_called()
        
        # Verify error context was saved
        assert workflow_id in error_handler.error_history
    
    @pytest.mark.asyncio
    async def test_calculate_backoff_delay(self, error_handler):
        """Test calculating backoff delay."""
        retry_policy = RetryPolicy(
            max_retries=5,
            base_delay=1.0,
            backoff_multiplier=2.0,
            max_delay=60.0
        )
        
        delay1 = error_handler.calculate_backoff_delay(retry_policy, 1)
        delay2 = error_handler.calculate_backoff_delay(retry_policy, 2)
        delay3 = error_handler.calculate_backoff_delay(retry_policy, 3)
        
        assert delay1 == 2.0  # 1.0 * 2^1
        assert delay2 == 4.0  # 1.0 * 2^2
        assert delay3 == 8.0  # 1.0 * 2^3
    
    @pytest.mark.asyncio
    async def test_is_retriable_error(self, error_handler):
        """Test determining if error is retriable."""
        # Network errors should be retriable
        network_error = ConnectionError("Connection failed")
        assert error_handler.is_retriable_error(network_error) is True
        
        # Timeout errors should be retriable
        timeout_error = asyncio.TimeoutError("Task timed out")
        assert error_handler.is_retriable_error(timeout_error) is True
        
        # Validation errors should not be retriable
        validation_error = ValueError("Invalid input")
        assert error_handler.is_retriable_error(validation_error) is False