"""
Workflow monitoring and metrics collection system.

Provides comprehensive monitoring capabilities for workflow execution,
including performance metrics, error tracking, and system health monitoring.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from bson import ObjectId

from .models import WorkflowMetrics, WorkflowStatus, TaskStatus


@dataclass
class PerformanceMetrics:
    """Performance metrics summary."""
    average_duration: float
    success_rate: float
    total_workflows: int
    active_workflows: int
    failed_workflows: int
    avg_tasks_per_workflow: float


class WorkflowMonitor:
    """
    Monitors workflow execution and collects performance metrics.
    
    Provides real-time monitoring of workflow execution, performance metrics
    collection, and system health tracking. Integrates with the orchestration
    engine to provide visibility into workflow operations.
    """
    
    def __init__(self, database, logger: Optional[logging.Logger] = None):
        """
        Initialize workflow monitor.
        
        Args:
            database: Database connection
            logger: Optional logger instance
        """
        self.database = database
        self.logger = logger or logging.getLogger(__name__)
        self.metrics_collection = database.workflow_metrics
        self.events_collection = database.workflow_events
        
        # In-memory metrics for fast access
        self._active_workflows: Dict[ObjectId, datetime] = {}
        self._performance_cache: Dict[str, Any] = {}
        self._cache_expiry = datetime.utcnow()
        self._cache_ttl = timedelta(minutes=5)
    
    async def record_workflow_start(self, workflow_id: ObjectId, review_id: ObjectId,
                                  config_name: str) -> None:
        """
        Record workflow start event and initialize metrics.
        
        Args:
            workflow_id: Unique workflow identifier
            review_id: Associated review ID
            config_name: Workflow configuration name
        """
        try:
            start_time = datetime.utcnow()
            
            metrics_doc = {
                "_id": workflow_id,
                "workflow_id": workflow_id,
                "review_id": review_id,
                "config_name": config_name,
                "status": WorkflowStatus.PENDING,
                "start_time": start_time,
                "end_time": None,
                "total_duration": None,
                "task_metrics": {},
                "error_count": 0,
                "retry_count": 0,
                "created_at": start_time
            }
            
            await self.metrics_collection.insert_one(metrics_doc)
            self._active_workflows[workflow_id] = start_time
            
            # Record event
            await self._record_event(workflow_id, "workflow_started", {
                "review_id": review_id,
                "config_name": config_name
            })
            
            self.logger.info(f"Recorded workflow start: {workflow_id}")
            
        except Exception as e:
            self.logger.error(f"Error recording workflow start: {e}")
            raise
    
    async def record_workflow_completion(self, workflow_id: ObjectId, 
                                       status: WorkflowStatus) -> None:
        """
        Record workflow completion and calculate final metrics.
        
        Args:
            workflow_id: Workflow identifier
            status: Final workflow status
        """
        try:
            end_time = datetime.utcnow()
            start_time = self._active_workflows.get(workflow_id)
            
            update_doc = {
                "status": status,
                "end_time": end_time,
                "updated_at": end_time
            }
            
            if start_time:
                total_duration = (end_time - start_time).total_seconds()
                update_doc["total_duration"] = total_duration
                del self._active_workflows[workflow_id]
            
            await self.metrics_collection.update_one(
                {"_id": workflow_id},
                {"$set": update_doc}
            )
            
            # Record event
            await self._record_event(workflow_id, "workflow_completed", {
                "final_status": status,
                "duration": update_doc.get("total_duration")
            })
            
            # Clear performance cache
            self._invalidate_cache()
            
            self.logger.info(f"Recorded workflow completion: {workflow_id} - {status}")
            
        except Exception as e:
            self.logger.error(f"Error recording workflow completion: {e}")
            raise
    
    async def record_task_start(self, workflow_id: ObjectId, task_name: str,
                              task_id: ObjectId) -> None:
        """
        Record task start within workflow.
        
        Args:
            workflow_id: Parent workflow ID
            task_name: Name of the task
            task_id: Task identifier
        """
        try:
            start_time = datetime.utcnow()
            
            await self.metrics_collection.update_one(
                {"_id": workflow_id},
                {
                    "$set": {
                        f"task_metrics.{task_name}": {
                            "task_id": task_id,
                            "status": TaskStatus.PENDING,
                            "start_time": start_time,
                            "end_time": None,
                            "duration": None,
                            "retry_count": 0,
                            "error_message": None
                        }
                    }
                }
            )
            
            await self._record_event(workflow_id, "task_started", {
                "task_name": task_name,
                "task_id": task_id
            })
            
        except Exception as e:
            self.logger.error(f"Error recording task start: {e}")
    
    async def record_task_completion(self, workflow_id: ObjectId, task_name: str,
                                   status: TaskStatus, error_message: str = None) -> None:
        """
        Record task completion within workflow.
        
        Args:
            workflow_id: Parent workflow ID
            task_name: Name of the completed task
            status: Final task status
            error_message: Optional error message if task failed
        """
        try:
            end_time = datetime.utcnow()
            
            # Get current task metrics to calculate duration
            workflow_doc = await self.metrics_collection.find_one({"_id": workflow_id})
            if workflow_doc and task_name in workflow_doc.get("task_metrics", {}):
                task_metrics = workflow_doc["task_metrics"][task_name]
                start_time = task_metrics.get("start_time")
                
                duration = None
                if start_time:
                    duration = (end_time - start_time).total_seconds()
                
                update_doc = {
                    f"task_metrics.{task_name}.status": status,
                    f"task_metrics.{task_name}.end_time": end_time,
                    f"task_metrics.{task_name}.duration": duration
                }
                
                if error_message:
                    update_doc[f"task_metrics.{task_name}.error_message"] = error_message
                
                await self.metrics_collection.update_one(
                    {"_id": workflow_id},
                    {"$set": update_doc}
                )
                
                await self._record_event(workflow_id, "task_completed", {
                    "task_name": task_name,
                    "status": status,
                    "duration": duration,
                    "error_message": error_message
                })
            
        except Exception as e:
            self.logger.error(f"Error recording task completion: {e}")
    
    async def record_error(self, workflow_id: ObjectId, error_message: str,
                          task_name: str = None) -> None:
        """
        Record error occurrence in workflow.
        
        Args:
            workflow_id: Workflow identifier
            error_message: Error description
            task_name: Optional task name where error occurred
        """
        try:
            await self.metrics_collection.update_one(
                {"_id": workflow_id},
                {"$inc": {"error_count": 1}}
            )
            
            await self._record_event(workflow_id, "error_occurred", {
                "error_message": error_message,
                "task_name": task_name
            })
            
            self.logger.warning(f"Recorded error for workflow {workflow_id}: {error_message}")
            
        except Exception as e:
            self.logger.error(f"Error recording workflow error: {e}")
    
    async def get_workflow_metrics(self, workflow_id: ObjectId) -> Optional[WorkflowMetrics]:
        """
        Retrieve metrics for a specific workflow.
        
        Args:
            workflow_id: Workflow identifier
            
        Returns:
            WorkflowMetrics object or None if not found
        """
        try:
            doc = await self.metrics_collection.find_one({"_id": workflow_id})
            if doc:
                return WorkflowMetrics(**doc)
            return None
            
        except Exception as e:
            self.logger.error(f"Error retrieving workflow metrics: {e}")
            return None
    
    async def get_performance_summary(self, time_range: timedelta = None) -> PerformanceMetrics:
        """
        Get performance summary for specified time range.
        
        Args:
            time_range: Time range to analyze (default: last 24 hours)
            
        Returns:
            PerformanceMetrics summary
        """
        if time_range is None:
            time_range = timedelta(days=1)
        
        # Check cache first
        cache_key = f"performance_summary_{time_range.total_seconds()}"
        if (cache_key in self._performance_cache and 
            datetime.utcnow() < self._cache_expiry):
            return self._performance_cache[cache_key]
        
        try:
            start_time = datetime.utcnow() - time_range
            
            pipeline = [
                {"$match": {"start_time": {"$gte": start_time}}},
                {"$group": {
                    "_id": None,
                    "total_workflows": {"$sum": 1},
                    "completed_workflows": {
                        "$sum": {"$cond": [{"$eq": ["$status", WorkflowStatus.COMPLETED]}, 1, 0]}
                    },
                    "failed_workflows": {
                        "$sum": {"$cond": [{"$eq": ["$status", WorkflowStatus.FAILED]}, 1, 0]}
                    },
                    "average_duration": {"$avg": "$total_duration"},
                    "total_tasks": {"$sum": {"$size": {"$objectToArray": "$task_metrics"}}}
                }}
            ]
            
            result = await self.metrics_collection.aggregate(pipeline).to_list(1)
            
            if result:
                data = result[0]
                metrics = PerformanceMetrics(
                    average_duration=data.get("average_duration", 0.0),
                    success_rate=data.get("completed_workflows", 0) / max(data.get("total_workflows", 1), 1),
                    total_workflows=data.get("total_workflows", 0),
                    active_workflows=len(self._active_workflows),
                    failed_workflows=data.get("failed_workflows", 0),
                    avg_tasks_per_workflow=data.get("total_tasks", 0) / max(data.get("total_workflows", 1), 1)
                )
            else:
                metrics = PerformanceMetrics(
                    average_duration=0.0,
                    success_rate=1.0,
                    total_workflows=0,
                    active_workflows=len(self._active_workflows),
                    failed_workflows=0,
                    avg_tasks_per_workflow=0.0
                )
            
            # Cache result
            self._performance_cache[cache_key] = metrics
            self._cache_expiry = datetime.utcnow() + self._cache_ttl
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error getting performance summary: {e}")
            # Return default metrics on error
            return PerformanceMetrics(
                average_duration=0.0,
                success_rate=0.0,
                total_workflows=0,
                active_workflows=0,
                failed_workflows=0,
                avg_tasks_per_workflow=0.0
            )
    
    async def get_active_workflows(self) -> List[ObjectId]:
        """Get list of currently active workflow IDs."""
        return list(self._active_workflows.keys())
    
    async def cleanup_old_metrics(self, retention_days: int = 30) -> int:
        """
        Clean up old metrics data beyond retention period.
        
        Args:
            retention_days: Number of days to retain metrics
            
        Returns:
            Number of records deleted
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
            
            result = await self.metrics_collection.delete_many({
                "start_time": {"$lt": cutoff_date}
            })
            
            #