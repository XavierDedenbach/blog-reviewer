"""
Unit tests for workflow orchestrator models.
"""

import pytest
from datetime import datetime, timedelta
from bson import ObjectId
from pydantic import ValidationError

from core.review_orchestrator.models import (
    WorkflowState, TaskDefinition, TaskStatus, WorkflowStatus,
    WorkflowConfig, TaskPriority, RetryPolicy, WorkflowMetrics
)


class TestWorkflowState:
    """Test WorkflowState model."""
    
    def test_workflow_state_creation(self):
        """Test creating a workflow state."""
        workflow_id = ObjectId()
        review_id = ObjectId()
        
        state = WorkflowState(
            workflow_id=workflow_id,
            review_id=review_id,
            status=WorkflowStatus.PENDING,
            current_step="content_analysis",
            total_steps=4
        )
        
        assert state.workflow_id == workflow_id
        assert state.review_id == review_id
        assert state.status == WorkflowStatus.PENDING
        assert state.current_step == "content_analysis"
        assert state.total_steps == 4
        assert state.progress == 0.0
        assert state.retry_count == 0
        assert isinstance(state.created_at, datetime)
        assert state.updated_at == state.created_at
    
    def test_workflow_state_progress_calculation(self):
        """Test progress calculation."""
        state = WorkflowState(
            workflow_id=ObjectId(),
            review_id=ObjectId(),
            status=WorkflowStatus.IN_PROGRESS,
            current_step="style_analysis",
            total_steps=4,
            completed_steps=2
        )
        
        assert state.progress == 0.5
    
    def test_workflow_state_invalid_progress(self):
        """Test invalid progress values."""
        with pytest.raises(ValidationError):
            WorkflowState(
                workflow_id=ObjectId(),
                review_id=ObjectId(),
                status=WorkflowStatus.IN_PROGRESS,
                current_step="test",
                total_steps=4,
                completed_steps=5  # More completed than total
            )
    
    def test_workflow_state_status_transitions(self):
        """Test valid status transitions."""
        state = WorkflowState(
            workflow_id=ObjectId(),
            review_id=ObjectId(),
            status=WorkflowStatus.PENDING,
            current_step="init",
            total_steps=3
        )
        
        # Valid transitions
        valid_transitions = [
            (WorkflowStatus.PENDING, WorkflowStatus.IN_PROGRESS),
            (WorkflowStatus.IN_PROGRESS, WorkflowStatus.COMPLETED),
            (WorkflowStatus.IN_PROGRESS, WorkflowStatus.FAILED),
            (WorkflowStatus.FAILED, WorkflowStatus.RETRYING),
            (WorkflowStatus.RETRYING, WorkflowStatus.IN_PROGRESS),
        ]
        
        for from_status, to_status in valid_transitions:
            state.status = from_status
            assert state.can_transition_to(to_status)


class TestTaskDefinition:
    """Test TaskDefinition model."""
    
    def test_task_definition_creation(self):
        """Test creating a task definition."""
        task = TaskDefinition(
            name="content_analysis",
            description="Analyze content structure and quality",
            priority=TaskPriority.HIGH,
            timeout_seconds=300,
            retry_policy=RetryPolicy(max_retries=3, backoff_multiplier=2.0)
        )
        
        assert task.name == "content_analysis"
        assert task.priority == TaskPriority.HIGH
        assert task.timeout_seconds == 300
        assert task.retry_policy.max_retries == 3
        assert task.retry_policy.backoff_multiplier == 2.0
    
    def test_task_definition_defaults(self):
        """Test task definition default values."""
        task = TaskDefinition(
            name="test_task",
            description="Test task"
        )
        
        assert task.priority == TaskPriority.MEDIUM
        assert task.timeout_seconds == 60
        assert task.dependencies == []
        assert task.retry_policy.max_retries == 3
        assert task.retry_policy.base_delay_seconds == 1
        assert task.retry_policy.backoff_multiplier == 2.0
    
    def test_task_priority_ordering(self):
        """Test task priority ordering."""
        high_task = TaskDefinition(name="high", description="High priority", priority=TaskPriority.HIGH)
        medium_task = TaskDefinition(name="medium", description="Medium priority", priority=TaskPriority.MEDIUM)
        low_task = TaskDefinition(name="low", description="Low priority", priority=TaskPriority.LOW)
        
        assert high_task.priority.value > medium_task.priority.value
        assert medium_task.priority.value > low_task.priority.value


class TestWorkflowConfig:
    """Test WorkflowConfig model."""
    
    def test_workflow_config_creation(self):
        """Test creating workflow configuration."""
        tasks = [
            TaskDefinition(name="task1", description="First task"),
            TaskDefinition(name="task2", description="Second task", dependencies=["task1"]),
            TaskDefinition(name="task3", description="Third task", dependencies=["task2"])
        ]
        
        config = WorkflowConfig(
            name="blog_review",
            description="Complete blog review workflow",
            tasks=tasks,
            max_concurrent_tasks=2,
            overall_timeout_seconds=1800
        )
        
        assert config.name == "blog_review"
        assert len(config.tasks) == 3
        assert config.max_concurrent_tasks == 2
        assert config.overall_timeout_seconds == 1800
    
    def test_workflow_config_validation(self):
        """Test workflow configuration validation."""
        # Test circular dependency detection
        tasks = [
            TaskDefinition(name="task1", description="First task", dependencies=["task2"]),
            TaskDefinition(name="task2", description="Second task", dependencies=["task1"])
        ]
        
        with pytest.raises(ValidationError, match="Circular dependency detected"):
            WorkflowConfig(
                name="invalid_workflow",
                description="Workflow with circular dependencies",
                tasks=tasks
            )
    
    def test_workflow_config_dependency_validation(self):
        """Test dependency validation."""
        tasks = [
            TaskDefinition(name="task1", description="First task", dependencies=["nonexistent"])
        ]
        
        with pytest.raises(ValidationError, match="Unknown dependency"):
            WorkflowConfig(
                name="invalid_workflow",
                description="Workflow with invalid dependency",
                tasks=tasks
            )


class TestWorkflowMetrics:
    """Test WorkflowMetrics model."""
    
    def test_workflow_metrics_creation(self):
        """Test creating workflow metrics."""
        start_time = datetime.utcnow()
        end_time = start_time + timedelta(minutes=5)
        
        metrics = WorkflowMetrics(
            workflow_id=ObjectId(),
            start_time=start_time,
            end_time=end_time,
            total_tasks=5,
            completed_tasks=5,
            failed_tasks=0,
            retried_tasks=1
        )
        
        assert metrics.duration_seconds == 300  # 5 minutes
        assert metrics.success_rate == 1.0
        assert metrics.retry_rate == 0.2  # 1/5
    
    def test_workflow_metrics_calculations(self):
        """Test metrics calculations."""
        metrics = WorkflowMetrics(
            workflow_id=ObjectId(),
            start_time=datetime.utcnow(),
            total_tasks=10,
            completed_tasks=8,
            failed_tasks=2,
            retried_tasks=3
        )
        
        assert metrics.success_rate == 0.8
        assert metrics.failure_rate == 0.2
        assert metrics.retry_rate == 0.3