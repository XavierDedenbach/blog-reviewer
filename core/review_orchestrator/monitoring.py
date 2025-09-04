"""
Workflow monitoring and metrics collection module.
"""

import asyncio
import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import defaultdict
import logging

from .models import WorkflowMetrics, WorkflowStatus, TaskStatus


@dataclass
class PerformanceMetrics:
    """Performance metrics for workflow monitoring."""
    
    total_workflows: int = 0
    successful_workflows: int = 0
    failed_workflows: int = 0
    avg_completion_time: float = 0.0
    max_completion_time: float = 0.0
    min_completion_time: float = float('inf')
    active_workflows: int = 0
    queue_depth: int = 0
    error_rate: float = 0.0
    throughput: float = 0.0
    last_updated: datetime = field(default_factory=datetime.utcnow)


class WorkflowMonitor:
    """Monitor workflow execution and collect metrics."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.metrics = PerformanceMetrics()
        self.workflow_start_times: Dict[str, datetime] = {}
        self.completion_times: List[float] = []
        self.error_counts: Dict[str, int] = defaultdict(int)
        self.task_metrics: Dict[str, Dict[str, Any]] = {}
        self._monitoring_active = False
        
    async def start_monitoring(self):
        """Start the monitoring system."""
        self._monitoring_active = True
        self.logger.info("Workflow monitoring started")
        
        # Start background metrics collection
        asyncio.create_task(self._collect_metrics_loop())
    
    async def stop_monitoring(self):
        """Stop the monitoring system."""
        self._monitoring_active = False
        self.logger.info("Workflow monitoring stopped")
    
    def record_workflow_start(self, workflow_id: str):
        """Record when a workflow starts."""
        self.workflow_start_times[workflow_id] = datetime.utcnow()
        self.metrics.active_workflows += 1
        self.metrics.total_workflows += 1
        
        self.logger.debug(f"Workflow {workflow_id} started")
    
    def record_workflow_completion(self, workflow_id: str, status: WorkflowStatus):
        """Record when a workflow completes."""
        if workflow_id in self.workflow_start_times:
            start_time = self.workflow_start_times[workflow_id]
            completion_time = (datetime.utcnow() - start_time).total_seconds()
            
            self.completion_times.append(completion_time)
            
            # Update metrics
            self.metrics.active_workflows -= 1
            
            if status == WorkflowStatus.COMPLETED:
                self.metrics.successful_workflows += 1
            else:
                self.metrics.failed_workflows += 1
            
            # Update completion time stats
            self._update_completion_time_stats()
            
            # Clean up
            del self.workflow_start_times[workflow_id]
            
            self.logger.debug(
                f"Workflow {workflow_id} completed with status {status} "
                f"in {completion_time:.2f}s"
            )
    
    def record_task_execution(self, task_id: str, status: TaskStatus, 
                            execution_time: float, error: Optional[str] = None):
        """Record task execution metrics."""
        if task_id not in self.task_metrics:
            self.task_metrics[task_id] = {
                'executions': 0,
                'total_time': 0.0,
                'errors': 0,
                'last_status': None
            }
        
        metrics = self.task_metrics[task_id]
        metrics['executions'] += 1
        metrics['total_time'] += execution_time
        metrics['last_status'] = status
        
        if error:
            metrics['errors'] += 1
            self.error_counts[error] += 1
        
        self.logger.debug(f"Task {task_id} executed in {execution_time:.2f}s with status {status}")
    
    def record_error(self, error_type: str, context: Dict[str, Any]):
        """Record an error occurrence."""
        self.error_counts[error_type] += 1
        
        # Update error rate
        total_operations = self.metrics.total_workflows
        total_errors = sum(self.error_counts.values())
        self.metrics.error_rate = total_errors / total_operations if total_operations > 0 else 0.0
        
        self.logger.warning(f"Error recorded: {error_type}, context: {context}")
    
    def get_workflow_metrics(self) -> WorkflowMetrics:
        """Get current workflow metrics."""
        self._update_metrics()
        
        return WorkflowMetrics(
            total_tasks=sum(m['executions'] for m in self.task_metrics.values()),
            completed_tasks=len([m for m in self.task_metrics.values() 
                               if m['last_status'] == TaskStatus.COMPLETED]),
            failed_tasks=len([m for m in self.task_metrics.values() 
                            if m['last_status'] == TaskStatus.FAILED]),
            avg_task_duration=self._calculate_avg_task_duration(),
            total_duration=self.metrics.avg_completion_time,
            error_count=sum(self.error_counts.values()),
            retry_count=0,  # TODO: Track retries
            created_at=self.metrics.last_updated
        )
    
    def get_performance_metrics(self) -> PerformanceMetrics:
        """Get current performance metrics."""
        self._update_metrics()
        return self.metrics
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get system health indicators."""
        return {
            'status': 'healthy' if self.metrics.error_rate < 0.05 else 'degraded',
            'active_workflows': self.metrics.active_workflows,
            'error_rate': self.metrics.error_rate,
            'avg_completion_time': self.metrics.avg_completion_time,
            'queue_depth': self.metrics.queue_depth,
            'throughput': self.metrics.throughput,
            'uptime': (datetime.utcnow() - self.metrics.last_updated).total_seconds()
        }
    
    def _update_completion_time_stats(self):
        """Update completion time statistics."""
        if not self.completion_times:
            return
        
        self.metrics.avg_completion_time = sum(self.completion_times) / len(self.completion_times)
        self.metrics.max_completion_time = max(self.completion_times)
        self.metrics.min_completion_time = min(self.completion_times)
        
        # Keep only recent completion times (last 1000)
        if len(self.completion_times) > 1000:
            self.completion_times = self.completion_times[-1000:]
    
    def _calculate_avg_task_duration(self) -> float:
        """Calculate average task duration."""
        if not self.task_metrics:
            return 0.0
        
        total_time = sum(m['total_time'] for m in self.task_metrics.values())
        total_executions = sum(m['executions'] for m in self.task_metrics.values())
        
        return total_time / total_executions if total_executions > 0 else 0.0
    
    def _update_metrics(self):
        """Update current metrics."""
        now = datetime.utcnow()
        time_diff = (now - self.metrics.last_updated).total_seconds()
        
        if time_diff > 0:
            # Calculate throughput (workflows per second)
            self.metrics.throughput = self.metrics.successful_workflows / time_diff
        
        self.metrics.last_updated = now
    
    async def _collect_metrics_loop(self):
        """Background loop for collecting metrics."""
        while self._monitoring_active:
            try:
                self._update_metrics()
                await asyncio.sleep(10)  # Update every 10 seconds
            except Exception as e:
                self.logger.error(f"Error in metrics collection loop: {e}")
                await asyncio.sleep(1)