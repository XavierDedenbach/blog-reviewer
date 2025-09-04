"""
Task queue implementation with priority-based scheduling.
"""

import asyncio
import heapq
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from enum import Enum
import logging
import time
import uuid

logger = logging.getLogger(__name__)


class TaskPriority(Enum):
    """Task priority levels."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class TaskStatus(Enum):
    """Task execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"


@dataclass
class TaskDefinition:
    """Definition of a task to be executed."""
    task_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    priority: TaskPriority = TaskPriority.MEDIUM
    func: Optional[Callable] = None
    args: tuple = field(default_factory=tuple)
    kwargs: dict = field(default_factory=dict)
    max_retries: int = 3
    retry_delay: float = 1.0
    timeout: Optional[float] = None
    depends_on: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    
    def __lt__(self, other):
        """Compare tasks by priority (higher priority first) then by creation time."""
        if self.priority.value != other.priority.value:
            return self.priority.value > other.priority.value
        return self.created_at < other.created_at


@dataclass
class TaskResult:
    """Result of task execution."""
    task_id: str
    status: TaskStatus
    result: Any = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    retry_count: int = 0


class TaskQueue:
    """Priority-based async task queue with dependency management."""
    
    def __init__(self, max_concurrent_tasks: int = 10):
        self.max_concurrent_tasks = max_concurrent_tasks
        self._queue: List[TaskDefinition] = []
        self._running_tasks: Dict[str, asyncio.Task] = {}
        self._completed_tasks: Dict[str, TaskResult] = {}
        self._task_results: Dict[str, TaskResult] = {}
        self._lock = asyncio.Lock()
        self._shutdown = False
        self._worker_tasks: List[asyncio.Task] = []
        
    async def add_task(self, task: TaskDefinition) -> str:
        """Add a task to the queue."""
        async with self._lock:
            heapq.heappush(self._queue, task)
            logger.info(f"Added task {task.task_id} to queue")
            return task.task_id
    
    async def schedule_task(
        self, 
        func: Callable, 
        *args, 
        priority: TaskPriority = TaskPriority.MEDIUM,
        name: str = "",
        **kwargs
    ) -> str:
        """Schedule a task for execution."""
        task = TaskDefinition(
            name=name or func.__name__,
            priority=priority,
            func=func,
            args=args,
            kwargs=kwargs
        )
        return await self.add_task(task)
    
    async def get_task_status(self, task_id: str) -> Optional[TaskStatus]:
        """Get the status of a task."""
        if task_id in self._running_tasks:
            return TaskStatus.RUNNING
        if task_id in self._task_results:
            return self._task_results[task_id].status
        # Check if task is still in queue
        for task in self._queue:
            if task.task_id == task_id:
                return TaskStatus.PENDING
        return None
    
    async def get_task_result(self, task_id: str) -> Optional[TaskResult]:
        """Get the result of a completed task."""
        return self._task_results.get(task_id)
    
    def _can_run_task(self, task: TaskDefinition) -> bool:
        """Check if a task's dependencies are satisfied."""
        for dep_id in task.depends_on:
            if dep_id not in self._completed_tasks:
                return False
            if self._completed_tasks[dep_id].status != TaskStatus.COMPLETED:
                return False
        return True
    
    async def _get_next_task(self) -> Optional[TaskDefinition]:
        """Get the next task that can be executed."""
        async with self._lock:
            available_tasks = []
            remaining_tasks = []
            
            while self._queue:
                task = heapq.heappop(self._queue)
                if self._can_run_task(task):
                    available_tasks.append(task)
                else:
                    remaining_tasks.append(task)
            
            # Put remaining tasks back in queue
            for task in remaining_tasks:
                heapq.heappush(self._queue, task)
            
            # Return highest priority available task
            if available_tasks:
                available_tasks.sort()
                return available_tasks[0]
            
            return None
    
    async def _execute_task(self, task: TaskDefinition) -> TaskResult:
        """Execute a single task."""
        result = TaskResult(
            task_id=task.task_id,
            status=TaskStatus.RUNNING,
            started_at=datetime.now()
        )
        
        try:
            logger.info(f"Executing task {task.task_id}: {task.name}")
            
            if asyncio.iscoroutinefunction(task.func):
                if task.timeout:
                    task_result = await asyncio.wait_for(
                        task.func(*task.args, **task.kwargs),
                        timeout=task.timeout
                    )
                else:
                    task_result = await task.func(*task.args, **task.kwargs)
            else:
                if task.timeout:
                    task_result = await asyncio.wait_for(
                        asyncio.get_event_loop().run_in_executor(
                            None, lambda: task.func(*task.args, **task.kwargs)
                        ),
                        timeout=task.timeout
                    )
                else:
                    task_result = await asyncio.get_event_loop().run_in_executor(
                        None, lambda: task.func(*task.args, **task.kwargs)
                    )
            
            result.result = task_result
            result.status = TaskStatus.COMPLETED
            result.completed_at = datetime.now()
            
            logger.info(f"Task {task.task_id} completed successfully")
            
        except Exception as e:
            result.error = str(e)
            result.status = TaskStatus.FAILED
            result.completed_at = datetime.now()
            
            logger.error(f"Task {task.task_id} failed: {e}")
            
            # Handle retries
            if result.retry_count < task.max_retries:
                result.retry_count += 1
                result.status = TaskStatus.RETRYING
                logger.info(f"Retrying task {task.task_id} (attempt {result.retry_count})")
                
                # Add delay before retry
                await asyncio.sleep(task.retry_delay * result.retry_count)
                
                # Re-queue the task
                await self.add_task(task)
        
        return result
    
    async def _worker(self):
        """Worker coroutine that processes tasks from the queue."""
        while not self._shutdown:
            try:
                # Check if we can run more tasks
                if len(self._running_tasks) >= self.max_concurrent_tasks:
                    await asyncio.sleep(0.1)
                    continue
                
                # Get next task
                task = await self._get_next_task()
                if not task:
                    await asyncio.sleep(0.1)
                    continue
                
                # Execute task
                async def run_task():
                    try:
                        result = await self._execute_task(task)
                        async with self._lock:
                            self._task_results[task.task_id] = result
                            if result.status == TaskStatus.COMPLETED:
                                self._completed_tasks[task.task_id] = result
                            if task.task_id in self._running_tasks:
                                del self._running_tasks[task.task_id]
                    except Exception as e:
                        logger.error(f"Unexpected error in task {task.task_id}: {e}")
                        async with self._lock:
                            if task.task_id in self._running_tasks:
                                del self._running_tasks[task.task_id]
                
                # Start task
                task_coroutine = asyncio.create_task(run_task())
                async with self._lock:
                    self._running_tasks[task.task_id] = task_coroutine
                
            except Exception as e:
                logger.error(f"Error in task queue worker: {e}")
                await asyncio.sleep(1)
    
    async def start(self):
        """Start the task queue workers."""
        if self._worker_tasks:
            return  # Already started
        
        self._shutdown = False
        # Start multiple workers for better concurrency
        num_workers = min(self.max_concurrent_tasks, 5)
        for _ in range(num_workers):
            worker = asyncio.create_task(self._worker())
            self._worker_tasks.append(worker)
        
        logger.info(f"Started task queue with {num_workers} workers")
    
    async def stop(self):
        """Stop the task queue and wait for running tasks to complete."""
        self._shutdown = True
        
        # Wait for workers to stop
        if self._worker_tasks:
            await asyncio.gather(*self._worker_tasks, return_exceptions=True)
            self._worker_tasks.clear()
        
        # Wait for running tasks to complete
        if self._running_tasks:
            await asyncio.gather(*self._running_tasks.values(), return_exceptions=True)
            self._running_tasks.clear()
        
        logger.info("Task queue stopped")
    
    async def wait_for_completion(self, timeout: Optional[float] = None) -> bool:
        """Wait for all tasks to complete."""
        start_time = time.time()
        
        while True:
            async with self._lock:
                if not self._queue and not self._running_tasks:
                    return True
            
            if timeout and (time.time() - start_time) > timeout:
                return False
            
            await asyncio.sleep(0.1)
    
    def get_queue_stats(self) -> Dict[str, Any]:
        """Get queue statistics."""
        return {
            "queue_size": len(self._queue),
            "running_tasks": len(self._running_tasks),
            "completed_tasks": len(self._completed_tasks),
            "total_results": len(self._task_results),
            "max_concurrent": self.max_concurrent_tasks
        }