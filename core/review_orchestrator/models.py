"""
Data models for workflow orchestrator.
"""

from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field
import uuid


# Use string-based IDs instead of ObjectId to avoid bson dependency
WorkflowId = str
ReviewId = str
TaskId = str


class WorkflowStatus(str, Enum):
    """Workflow execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"


class TaskStatus(str, Enum):
    """Task execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"


class TaskPriority(str, Enum):
    """Task priority levels."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class RetryPolicy(BaseModel):
    """Retry policy configuration."""
    max_attempts: int = Field(default=3, ge=1, le=10)
    delay_seconds: float = Field(default=1.0, ge=0.1, le=300.0)
    backoff_multiplier: float = Field(default=2.0, ge=1.0, le=10.0)
    max_delay_seconds: float = Field(default=300.0, ge=1.0, le=3600.0)


class TaskDefinition(BaseModel):
    """Definition of a workflow task."""
    id: TaskId = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    priority: TaskPriority = TaskPriority.NORMAL
    timeout_seconds: int = Field(default=300, ge=1, le=3600)
    retry_policy: RetryPolicy = Field(default_factory=RetryPolicy)
    dependencies: List[TaskId] = Field(default_factory=list)
    parameters: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class WorkflowState(BaseModel):
    """Current state of a workflow execution."""
    workflow_id: WorkflowId = Field(default_factory=lambda: str(uuid.uuid4()))
    review_id: ReviewId
    status: WorkflowStatus = WorkflowStatus.PENDING
    current_step: str
    completed_steps: List[str] = Field(default_factory=list)
    failed_steps: List[str] = Field(default_factory=list)
    step_data: Dict[str, Any] = Field(default_factory=dict)
    error_message: Optional[str] = None
    retry_count: int = Field(default=0, ge=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class WorkflowConfig(BaseModel):
    """Configuration for workflow execution."""
    name: str
    description: Optional[str] = None
    tasks: List[TaskDefinition]
    max_concurrent_tasks: int = Field(default=5, ge=1, le=50)
    timeout_minutes: int = Field(default=60, ge=1, le=1440)
    retry_policy: RetryPolicy = Field(default_factory=RetryPolicy)
    priority: TaskPriority = TaskPriority.NORMAL
    enabled: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class WorkflowMetrics(BaseModel):
    """Performance metrics for workflow execution."""
    workflow_id: WorkflowId
    total_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    retry_count: int = 0
    execution_time_seconds: float = 0.0
    queue_time_seconds: float = 0.0
    average_task_duration: float = 0.0
    throughput_tasks_per_minute: float = 0.0
    success_rate: float = 0.0
    error_rate: float = 0.0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    def calculate_success_rate(self) -> float:
        """Calculate success rate percentage."""
        if self.total_tasks == 0:
            return 0.0
        return (self.completed_tasks / self.total_tasks) * 100.0

    def calculate_error_rate(self) -> float:
        """Calculate error rate percentage."""
        if self.total_tasks == 0:
            return 0.0
        return (self.failed_tasks / self.total_tasks) * 100.0