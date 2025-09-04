"""
Unit tests for workflow orchestrator.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, Mock, patch
from datetime import datetime
from bson import ObjectId

from core.review_orchestrator.orchestrator import WorkflowOrchestrator
from core.review_orchestrator.models import (
    WorkflowConfig, WorkflowStatus, TaskDefinition, TaskPriority
)


class TestWorkflowOrchestrator:
    """Test WorkflowOrchestrator class."""
    
    @pytest.fixture
    def mock_dependencies(self):
        """Create mock dependencies."""
        return {
            "db": AsyncMock(),
            "task_queue": AsyncMock(),
            "state_manager": AsyncMock(),
            "monitor": AsyncMock(),
            "error_handler": AsyncMock()
        }
    
    @pytest.fixture
    def orchestrator(self, mock_dependencies):
        """Create WorkflowOrchestrator instance."""
        return WorkflowOrchestrator(
            db=mock_dependencies["db"],
            task_queue=mock_dependencies["task_queue"],
            state_manager=mock_dependencies["state_manager"],
            monitor=mock_dependencies["monitor"],
            error_handler=mock_dependencies["error_handler"]
        )
    
    @pytest.fixture
    def sample_workflow_config(self):
        """Create sample workflow configuration."""
        return WorkflowConfig(
            name="blog_review",
            description="Blog review workflow",
            tasks=[
                TaskDefinition(
                    name="content_analysis",
                    description="Analyze content",
                    priority=TaskPriority.HIGH
                ),
                TaskDefinition(
                    name="style_review",
                    description="Review writing style",
                    priority=TaskPriority.MEDIUM,
                    dependencies=["content_analysis"]
                ),
                TaskDefinition(
                    name="grammar_check",
                    description="Check grammar",
                    priority=TaskPriority.MEDIUM,
                    dependencies=["content_analysis"]
                ),
                TaskDefinition(
                    name="final_report",
                    description="Generate final report",
                    priority=TaskPriority.HIGH,
                    dependencies=["style_review", "grammar_check"]
                )
            ]
        )
    
    @pytest.mark.asyncio
    async def test_start_workflow(self, orchestrator, sample_workflow_config, mock_dependencies):
        """Test starting a new workflow."""
        review_id = str(ObjectId())

        workflow_id = await orchestrator.start_workflow(sample_workflow_config, review_id)

        assert workflow_id is not None
        # Verify that save_workflow_state was called (not create_workflow_state)
        assert mock_dependencies["state_manager"].save_workflow_state.called

    @pytest.mark.asyncio
    async def test_get_workflow_status(self, orchestrator, mock_dependencies):
        """Test getting workflow status."""
        workflow_id = str(ObjectId())
        mock_workflow = AsyncMock()
        mock_workflow.status = WorkflowStatus.RUNNING

        mock_dependencies["state_manager"].get_workflow_state.return_value = mock_workflow

        status = await orchestrator.get_workflow_status(workflow_id)

        assert status == WorkflowStatus.RUNNING
        mock_dependencies["state_manager"].get_workflow_state.assert_called_once_with(workflow_id)

    @pytest.mark.asyncio
    async def test_cancel_workflow(self, orchestrator, mock_dependencies):
        """Test canceling a workflow."""
        workflow_id = str(ObjectId())
        mock_workflow = AsyncMock()
        mock_workflow.status = WorkflowStatus.RUNNING

        mock_dependencies["state_manager"].get_workflow_state.return_value = mock_workflow

        result = await orchestrator.cancel_workflow(workflow_id)

        assert result is True
        assert mock_workflow.status == WorkflowStatus.CANCELLED
        mock_dependencies["state_manager"].save_workflow_state.assert_called_once()

    @pytest.mark.asyncio
    async def test_cancel_nonexistent_workflow(self, orchestrator, mock_dependencies):
        """Test canceling a nonexistent workflow."""
        workflow_id = str(ObjectId())

        mock_dependencies["state_manager"].get_workflow_state.return_value = None

        result = await orchestrator.cancel_workflow(workflow_id)

        assert result is False