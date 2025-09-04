"""
Workflow state management system.
"""

from typing import Dict, Optional, List, Any
from datetime import datetime
import asyncio
import logging
from contextlib import asynccontextmanager

from .models import (
    WorkflowState, WorkflowStatus, WorkflowId, ReviewId
)

logger = logging.getLogger(__name__)


class WorkflowStateManager:
    """Manages workflow state transitions and persistence."""
    
    def __init__(self):
        self._states: Dict[WorkflowId, WorkflowState] = {}
        self._locks: Dict[WorkflowId, asyncio.Lock] = {}
        self._observers: List[callable] = []
    
    async def create_workflow_state(
        self, 
        review_id: ReviewId,
        initial_step: str = "start",
        workflow_id: Optional[WorkflowId] = None
    ) -> WorkflowState:
        """Create a new workflow state."""
        state = WorkflowState(
            workflow_id=workflow_id or str(len(self._states) + 1),
            review_id=review_id,
            current_step=initial_step,
            status=WorkflowStatus.PENDING
        )
        
        await self._store_state(state)
        await self._notify_observers('state_created', state)
        
        logger.info(f"Created workflow state {state.workflow_id} for review {review_id}")
        return state
    
    async def get_workflow_state(self, workflow_id: WorkflowId) -> Optional[WorkflowState]:
        """Get workflow state by ID."""
        return self._states.get(workflow_id)
    
    async def update_workflow_state(
        self, 
        workflow_id: WorkflowId, 
        **updates
    ) -> Optional[WorkflowState]:
        """Update workflow state with new data."""
        async with self._get_lock(workflow_id):
            state = self._states.get(workflow_id)
            if not state:
                logger.warning(f"Workflow state {workflow_id} not found")
                return None
            
            # Update fields
            for field, value in updates.items():
                if hasattr(state, field):
                    setattr(state, field, value)
            
            state.updated_at = datetime.utcnow()
            
            await self._store_state(state)
            await self._notify_observers('state_updated', state)
            
            logger.debug(f"Updated workflow state {workflow_id}")
            return state
    
    async def transition_workflow_status(
        self,
        workflow_id: WorkflowId,
        new_status: WorkflowStatus,
        error_message: Optional[str] = None
    ) -> bool:
        """Transition workflow to new status."""
        async with self._get_lock(workflow_id):
            state = self._states.get(workflow_id)
            if not state:
                logger.error(f"Cannot transition unknown workflow {workflow_id}")
                return False
            
            old_status = state.status
            
            # Validate transition
            if not self._is_valid_transition(old_status, new_status):
                logger.error(f"Invalid status transition from {old_status} to {new_status}")
                return False
            
            # Update state
            state.status = new_status
            state.updated_at = datetime.utcnow()
            
            if error_message:
                state.error_message = error_message
            
            # Set timestamps
            if new_status == WorkflowStatus.RUNNING and not state.started_at:
                state.started_at = datetime.utcnow()
            elif new_status in [WorkflowStatus.COMPLETED, WorkflowStatus.FAILED, WorkflowStatus.CANCELLED]:
                state.completed_at = datetime.utcnow()
            
            await self._store_state(state)
            await self._notify_observers('status_changed', state, old_status)
            
            logger.info(f"Transitioned workflow {workflow_id} from {old_status} to {new_status}")
            return True
    
    async def advance_workflow_step(
        self,
        workflow_id: WorkflowId,
        next_step: str,
        step_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Advance workflow to next step."""
        async with self._get_lock(workflow_id):
            state = self._states.get(workflow_id)
            if not state:
                return False
            
            # Mark current step as completed
            if state.current_step not in state.completed_steps:
                state.completed_steps.append(state.current_step)
            
            # Update step data
            if step_data:
                state.step_data.update(step_data)
            
            # Move to next step
            state.current_step = next_step
            state.updated_at = datetime.utcnow()
            
            await self._store_state(state)
            await self._notify_observers('step_advanced', state)
            
            logger.info(f"Advanced workflow {workflow_id} to step {next_step}")
            return True
    
    async def mark_step_failed(
        self,
        workflow_id: WorkflowId,
        step: str,
        error_message: str
    ) -> bool:
        """Mark a workflow step as failed."""
        async with self._get_lock(workflow_id):
            state = self._states.get(workflow_id)
            if not state:
                return False
            
            if step not in state.failed_steps:
                state.failed_steps.append(step)
            
            state.error_message = error_message
            state.updated_at = datetime.utcnow()
            
            await self._store_state(state)
            await self._notify_observers('step_failed', state)
            
            logger.error(f"Step {step} failed in workflow {workflow_id}: {error_message}")
            return True
    
    async def increment_retry_count(self, workflow_id: WorkflowId) -> int:
        """Increment and return retry count for workflow."""
        async with self._get_lock(workflow_id):
            state = self._states.get(workflow_id)
            if not state:
                return 0
            
            state.retry_count += 1
            state.updated_at = datetime.utcnow()
            
            await self._store_state(state)
            
            logger.info(f"Incremented retry count for workflow {workflow_id} to {state.retry_count}")
            return state.retry_count
    
    async def get_workflows_by_status(self, status: WorkflowStatus) -> List[WorkflowState]:
        """Get all workflows with specified status."""
        return [state for state in self._states.values() if state.status == status]
    
    async def get_workflows_by_review(self, review_id: ReviewId) -> List[WorkflowState]:
        """Get all workflows for a review."""
        return [state for state in self._states.values() if state.review_id == review_id]
    
    def add_observer(self, observer: callable):
        """Add state change observer."""
        self._observers.append(observer)
    
    def remove_observer(self, observer: callable):
        """Remove state change observer."""
        if observer in self._observers:
            self._observers.remove(observer)
    
    @asynccontextmanager
    async def workflow_transaction(self, workflow_id: WorkflowId):
        """Context manager for workflow state transactions."""
        async with self._get_lock(workflow_id):
            state = self._states.get(workflow_id)
            if state:
                original_state = state.copy()
                try:
                    yield state
                    await self._store_state(state)
                except Exception:
                    # Rollback on error
                    self._states[workflow_id] = original_state
                    raise
    
    async def _store_state(self, state: WorkflowState):
        """Store workflow state (in-memory for now)."""
        self._states[state.workflow_id] = state
    
    async def _notify_observers(self, event: str, state: WorkflowState, *args):
        """Notify all observers of state change."""
        for observer in self._observers:
            try:
                if asyncio.iscoroutinefunction(observer):
                    await observer(event, state, *args)
                else:
                    observer(event, state, *args)
            except Exception as e:
                logger.error(f"Observer error: {e}")
    
    def _get_lock(self, workflow_id: WorkflowId) -> asyncio.Lock:
        """Get or create lock for workflow."""
        if workflow_id not in self._locks:
            self._locks[workflow_id] = asyncio.Lock()
        return self._locks[workflow_id]
    
    def _is_valid_transition(self, from_status: WorkflowStatus, to_status: WorkflowStatus) -> bool:
        """Check if status transition is valid."""
        valid_transitions = {
            WorkflowStatus.PENDING: [WorkflowStatus.RUNNING, WorkflowStatus.CANCELLED],
            WorkflowStatus.RUNNING: [WorkflowStatus.COMPLETED, WorkflowStatus.FAILED, WorkflowStatus.CANCELLED, WorkflowStatus.RETRYING],
            WorkflowStatus.FAILED: [WorkflowStatus.RETRYING, WorkflowStatus.CANCELLED],
            WorkflowStatus.RETRYING: [WorkflowStatus.RUNNING, WorkflowStatus.FAILED, WorkflowStatus.CANCELLED],
            WorkflowStatus.COMPLETED: [],  # Terminal state
            WorkflowStatus.CANCELLED: []   # Terminal state
        }
        
        return to_status in valid_transitions.get(from_status, [])


# Alias for backward compatibility
StateManager = WorkflowStateManager