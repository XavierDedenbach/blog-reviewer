"""
Custom exceptions for workflow orchestrator.
"""


class WorkflowError(Exception):
    """Base exception for workflow errors."""
    pass


class WorkflowStateError(WorkflowError):
    """Error in workflow state management."""
    pass


class TaskExecutionError(WorkflowError):
    """Error in task execution."""
    pass


class WorkflowConfigError(WorkflowError):
    """Error in workflow configuration."""
    pass


class RetryExhaustedError(WorkflowError):
    """Error when retry attempts are exhausted."""
    pass


class InvalidTransitionError(WorkflowStateError):
    """Error for invalid state transitions."""
    pass


class TaskNotFoundError(TaskExecutionError):
    """Error when a task is not found."""
    pass


class DependencyError(TaskExecutionError):
    """Error with task dependencies."""
    pass


class TemporaryError(WorkflowError):
    """Temporary error that should be retried."""
    pass