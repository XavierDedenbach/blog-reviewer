"""
Unit tests for workflow monitoring system.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, Mock
from datetime import datetime, timedelta
from bson import ObjectId

from core.review_orchestrator.workflow_monitor import WorkflowMonitor
from core.review_orchestrator.models import WorkflowMetrics, WorkflowStatus


class TestWorkflowMonitor:
    """Test WorkflowMonitor class."""
    
    @pytest.fixture
    def mock_db(self):
        """Create mock database."""
        db = AsyncMock()
        collection = AsyncMock()
        db.workflow_metrics = collection
        return db
    
    @pytest.fixture
    def monitor(self, mock_db):
        """Create WorkflowMonitor instance."""
        return WorkflowMonitor(mock_db)
    
    @pytest.mark.asyncio
    async def test_record_workflow_start(self, monitor, mock_db):
        """Test recording workflow start."""
        workflow_id = ObjectId()
        
        await monitor.record_workflow_start(workflow_id)
        
        # Verify metrics were saved
        mock_db.workflow_metrics.insert_one.assert_called_once()
        call_args = mock_db.workflow_metrics.insert_one.call_args[0][0]
        assert call_args["workflow_id"] == workflow_id
        assert call_args["status"] == WorkflowStatus.PENDING
        assert "start_time" in call_args
    
    @pytest.mark.asyncio
    async def test_record_task_completion(self, monitor, mock_db):
        """Test recording task completion."""
        workflow_id = ObjectId()
        task_name = "content_analysis"
        duration = 5.2
        
        await monitor.record_task_completion(workflow_id, task_name, duration)
        
        # Verify metrics were updated
        mock_db.workflow_metrics.update_one.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_workflow_metrics(self, monitor, mock_db):
        """Test retrieving workflow metrics."""
        workflow_id = ObjectId()
        mock_metrics = {
            "_id": ObjectId(),
            "workflow_id": workflow_id,
            "status": WorkflowStatus.COMPLETED,
            "start_time": datetime.utcnow(),
            "end_time": datetime.utcnow(),
            "total_duration": 30.5,
            "task_metrics": {
                "content_analysis": {"duration": 10.0, "status": "completed"}
            }
        }
        mock_db.workflow_metrics.find_one.return_value = mock_metrics
        
        result = await monitor.get_workflow_metrics(workflow_id)
        
        assert result.workflow_id == workflow_id
        assert result.status == WorkflowStatus.COMPLETED
        assert result.total_duration == 30.5
    
    @pytest.mark.asyncio
    async def test_calculate_performance_metrics(self, monitor):
        """Test calculating performance metrics."""
        # Mock data for calculation
        metrics_data = [
            {"total_duration": 25.0, "status": WorkflowStatus.COMPLETED},
            {"total_duration": 30.0, "status": WorkflowStatus.COMPLETED},
            {"total_duration": 35.0, "status": WorkflowStatus.COMPLETED},
        ]
        
        result = await monitor.calculate_performance_metrics(metrics_data)
        
        assert result["average_duration"] == 30.0
        assert result["success_rate"] == 1.0
        assert result["total_workflows"] == 3