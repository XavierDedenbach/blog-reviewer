"""
Main workflow orchestrator implementation.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from concurrent.futures import ThreadPoolExecutor

from .models import (
    WorkflowState, WorkflowConfig, TaskDefinition, 
    WorkflowStatus, TaskStatus, TaskPriority, WorkflowMetrics
)
from .state_manager import StateManager
from .task_queue import TaskQueue


logger = logging.getLogger(__name__)


class WorkflowOrchestrator:
    """Main workflow orchestration engine."""
    
    def __init__(self, max_workers: int = 10):
        """Initialize the orchestrator."""
        self.max_workers = max_workers
        self.state_manager = StateManager()
        self.task_queue = TaskQueue()
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.task_handlers: Dict[str, Callable] = {}
        self.active_workflows: Dict[str, WorkflowState] = {}
        self.running = False
        
    async def start(self):
        """Start the orchestrator."""
        logger.info("Starting workflow orchestrator")
        self.running = True
        # Start background task processing
        asyncio.create_task(self._process_tasks())
        
    async def stop(self):
        """Stop the orchestrator."""
        logger.info("Stopping workflow orchestrator")
        self.running = False
        self.executor.shutdown(wait=True)
        
    def register_task_handler(self, task_type: str, handler: Callable):
        """Register a task handler."""
        self.task_handlers[task_type] = handler
        logger.debug(f"Registered handler for task type: {task_type}")
        
    async def start_workflow(self, workflow_config: WorkflowConfig, review_id: str) -> str:
        """Start a new workflow."""
        workflow_state = WorkflowState(
            review_id=review_id,
            status=WorkflowStatus.PENDING
        )
        
        # Save initial state
        await self.state_manager.save_state(workflow_state)
        self.active_workflows[workflow_state.workflow_id] = workflow_state
        
        # Schedule initial tasks
        await self._schedule_initial_tasks(workflow_config, workflow_state)
        
        # Update state to running
        workflow_state.status = WorkflowStatus.RUNNING
        workflow_state.started_at = datetime.utcnow()
        await self.state_manager.save_state(workflow_state)
        
        logger.info(f"Started workflow {workflow_state.workflow_id}")
        return workflow_state.workflow_id
        
    async def get_workflow_state(self, workflow_id: str) -> Optional[WorkflowState]:
        """Get current workflow state."""
        return await self.state_manager.get_state(workflow_id)
        
    async def cancel_workflow(self, workflow_id: str) -> bool:
        """Cancel a running workflow."""
        workflow_state = await self.get_workflow_state(workflow_id)
        if not workflow_state:
            return False
            
        workflow_state.status = WorkflowStatus.CANCELLED
        workflow_state.updated_at = datetime.utcnow()
        await self.state_manager.save_state(workflow_state)
        
        # Cancel pending tasks
        await self.task_queue.cancel_workflow_tasks(workflow_id)
        
        if workflow_id in self.active_workflows:
            del self.active_workflows[workflow_id]
            
        logger.info(f"Cancelled workflow {workflow_id}")
        return True
        
    async def retry_workflow(self, workflow_id: str) -> bool:
        """Retry a failed workflow."""
        workflow_state = await self.get_workflow_state(workflow_id)
        if not workflow_state or workflow_state.status != WorkflowStatus.FAILED:
            return False
            
        # Reset failed steps and restart
        workflow_state.failed_steps.clear()
        workflow_state.status = WorkflowStatus.RUNNING
        workflow_state.updated_at = datetime.utcnow()
        await self.state_manager.save_state(workflow_state)
        
        logger.info(f"Retrying workflow {workflow_id}")
        return True
        
    async def get_workflow_metrics(self, workflow_id: str) -> Optional[WorkflowMetrics]:
        """Get workflow performance metrics."""
        workflow_state = await self.get_workflow_state(workflow_id)
        if not workflow_state:
            return None
            
        metrics = WorkflowMetrics(
            workflow_id=workflow_id,
            total_tasks=len(workflow_state.completed_steps) + len(workflow_state.failed_steps),
            completed_tasks=len(workflow_state.completed_steps),
            failed_tasks=len(workflow_state.failed_steps),
            queue_size=await self.task_queue.get_queue_size()
        )
        
        # Calculate duration if workflow is completed
        if workflow_state.started_at and workflow_state.completed_at:
            duration = (workflow_state.completed_at - workflow_state.started_at).total_seconds()
            metrics.total_duration = duration
            if duration > 0:
                metrics.throughput = metrics.completed_tasks / duration
                
        metrics.error_rate = metrics.calculate_error_rate()
        return metrics
        
    async def _schedule_initial_tasks(self, config: WorkflowConfig, workflow_state: WorkflowState):
        """Schedule initial tasks for a workflow."""
        for task_def in config.steps:
            if not task_def.dependencies:  # No dependencies, can start immediately
                await self.task_queue.enqueue_task(
                    task_def, workflow_state.workflow_id, workflow_state.review_id
                )
                
    async def _process_tasks(self):
        """Background task processing loop."""
        while self.running:
            try:
                task = await self.task_queue.dequeue_task()
                if task:
                    asyncio.create_task(self._execute_task(task))
                else:
                    await asyncio.sleep(0.1)  # Short delay when no tasks
            except Exception as e:
                logger.error(f"Error in task processing loop: {e}")
                await asyncio.sleep(1)
                
    async def _execute_task(self, task_info: Dict[str, Any]):
        """Execute a single task."""
        task_def = task_info['task_definition']
        workflow_id = task_info['workflow_id']
        
        try:
            # Get task handler
            handler = self.task_handlers.get(task_def.task_type)
            if not handler:
                raise ValueError(f"No handler registered for task type: {task_def.task_type}")
                
            # Execute task
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                self.executor, 
                handler, 
                task_def.parameters
            )
            
            # Update workflow state
            await self._handle_task_completion(workflow_id, task_def.name, result)
            
        except Exception as e:
            logger.error(f"Task {task_def.name} failed: {e}")
            await self._handle_task_failure(workflow_id, task_def.name, str(e))
            
    async def _handle_task_completion(self, workflow_id: str, task_name: str, result: Any):
        """Handle successful task completion."""
        workflow_state = await self.get_workflow_state(workflow_id)
        if not workflow_state:
            return
            
        workflow_state.completed_steps.append(task_name)
        workflow_state.current_step = None
        workflow_state.updated_at = datetime.utcnow()
        
        # Check if workflow is complete
        if self._is_workflow_complete(workflow_state):
            workflow_state.status = WorkflowStatus.COMPLETED
            workflow_state.completed_at = datetime.utcnow()
            if workflow_id in self.active_workflows:
                del self.active_workflows[workflow_id]
                
        await self.state_manager.save_state(workflow_state)
        
    async def _handle_task_failure(self, workflow_id: str, task_name: str, error: str):
        """Handle task failure."""
        workflow_state = await self.get_workflow_state(workflow_id)
        if not workflow_state:
            return
            
        workflow_state.failed_steps.append(task_name)
        workflow_state.current_step = None
        workflow_state.status = WorkflowStatus.FAILED
        workflow_state.updated_at = datetime.utcnow()
        
        if workflow_id in self.active_workflows:
            del self.active_workflows[workflow_id]
            
        await self.state_manager.save_state(workflow_state)
        
    def _is_workflow_complete(self, workflow_state: WorkflowState) -> bool:
        """Check if workflow is complete."""
        # Simple implementation - workflow is complete if no failed steps
        return len(workflow_state.failed_steps) == 0