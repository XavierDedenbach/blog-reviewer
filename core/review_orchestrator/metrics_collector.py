"""
Metrics collection system for workflow orchestrator.
"""

import asyncio
from typing import Dict, Any, List
from datetime import datetime, timedelta
from collections import defaultdict, deque
from bson import ObjectId

from .models import WorkflowMetrics


class MetricsCollector:
    """Collects and manages workflow metrics."""
    
    def __init__(self, retention_hours: int = 24):
        """Initialize metrics collector."""
        self.retention_hours = retention_hours
        self._metrics_history = deque(maxlen=1000)  # Keep last 1000 data points
        self._workflow_timings: Dict[str, datetime] = {}
        self._step_timings: Dict[str, List[float]] = defaultdict(list)
        self._error_counts: Dict[str, int] = defaultdict(int)
        self._lock = asyncio.Lock()
    
    async def record_workflow_started(self, workflow_id: ObjectId):
        """Record workflow start time."""
        async with self._lock:
            self._workflow_timings[str(workflow_id)] = datetime.utcnow()
    
    async def record_workflow_completed(self, workflow_id: ObjectId, success: bool = True):
        """Record workflow completion."""
        async with self._lock:
            workflow_key = str(workflow_id)
            if workflow_key in self._workflow_timings:
                start_time = self._workflow_timings.pop(workflow_key)
                duration = (datetime.utcnow() - start_time).total_seconds()
                
                self._metrics_history.append({
                    "timestamp": datetime.utcnow(),
                    "workflow_id": workflow_key,
                    "duration": duration,
                    "success": success,
                    "type": "workflow_completed"
                })
    
    async def record_step_timing(self, step_name: str, duration: float):
        """Record step execution timing."""
        async with self._lock:
            self._step_timings[step_name].append(duration)
            # Keep only last 100 timings per step
            if len(self._step_timings[step_name]) > 100:
                self._step_timings[step_name] = self._step_timings[step_name][-100:]
    
    async def record_error(self, error_type: str):
        """Record an error occurrence."""
        async with self._lock:
            self._error_counts[error_type] += 1
    
    async def record_system_metrics(self, metrics: Dict[str, Any]):
        """Record system-level metrics."""
        async with self._lock:
            self._metrics_history.append({
                "timestamp": datetime.utcnow(),
                "type": "system_metrics",
                **metrics
            })
    
    async def get_current_metrics(self) -> WorkflowMetrics:
        """Get current aggregated metrics."""
        async with self._lock:
            now = datetime.utcnow()
            cutoff = now - timedelta(hours=self.retention_hours)
            
            # Filter recent metrics
            recent_metrics = [
                m for m in self._metrics_history 
                if m["timestamp"] > cutoff
            ]
            
            # Calculate workflow metrics
            completed_workflows = [
                m for m in recent_metrics 
                if m.get("type") == "workflow_completed"
            ]
            
            successful_workflows = [
                m for m in completed_workflows 
                if m.get("success", False)
            ]
            
            # Calculate averages
            avg_duration = 0.0
            if completed_workflows:
                total_duration = sum(m.get("duration", 0) for m in completed_workflows)
                avg_duration = total_duration / len(completed_workflows)
            
            success_rate = 0.0
            if completed_workflows:
                success_rate = len(successful_workflows) / len(completed_workflows)
            
            # Calculate step timings
            step_avg_timings = {}
            for step_name, timings in self._step_timings.items():
                if timings:
                    step_avg_timings[step_name] = sum(timings) / len(timings)
            
            # Get latest system metrics
            system_metrics = {}
            for m in reversed(recent_metrics):
                if m.get("type") == "system_metrics":
                    system_metrics = {k: v for k, v in m.items() if k not in ["timestamp", "type"]}
                    break
            
            return WorkflowMetrics(
                total_workflows=len(completed_workflows),
                successful_workflows=len(successful_workflows),
                failed_workflows=len(completed_workflows) - len(successful_workflows),
                average_duration=avg_duration,
                success_rate=success_rate,
                step_timings=step_avg_timings,
                error_counts=dict(self._error_counts),
                system_metrics=system_metrics,
                collected_at=now
            )
    
    async def cleanup_old_metrics(self):
        """Clean up old metrics data."""
        async with self._lock:
            cutoff = datetime.utcnow() - timedelta(hours=self.retention_hours * 2)
            
            # Filter out old metrics
            self._metrics_history = deque(
                [m for m in self._metrics_history if m["timestamp"] > cutoff],
                maxlen=self._metrics_history.maxlen
            )
            
            # Clean up old workflow timings
            to_remove = []
            for workflow_id, start_time in self._workflow_timings.items():
                if start_time < cutoff:
                    to_remove.append(workflow_id)
            
            for workflow_id in to_remove:
                del self._workflow_timings[workflow_id]