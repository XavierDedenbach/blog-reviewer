"""
End-to-end integration tests for workflow orchestration.
"""

import pytest
import asyncio
from datetime import datetime
from bson import ObjectId

from core.review_orchestrator.orchestrator import WorkflowOrchestrator
from core.review_orchestrator.models import WorkflowConfig, TaskDefinition, TaskPriority, WorkflowStatus
from core.database.connection import DatabaseConnection


class TestWorkflowEndToEnd:
    """Test complete workflow execution end-to-end."""
    
    @pytest_asyncio.fixture
    async def orchestrator(self, clean_real_db):
        """Create orchestrator with real database."""
        config = WorkflowConfig(
            name="test_review_workflow",
            description="Test workflow for integration testing",
            timeout_seconds=300,
            max_concurrent_tasks=2,
            tasks=[
                TaskDefinition(
                    name="content_analysis",
                    description="Analyze content structure",
                    priority=TaskPriority.HIGH,
                    timeout_seconds=60
                ),
                TaskDefinition(
                    name="grammar_check",
                    description="Check grammar and style",
                    priority=TaskPriority.MEDIUM,
                    timeout_seconds=45
                ),
                TaskDefinition(
                    name="final_review",
                    description="Generate final review",
                    priority=TaskPriority.LOW,
                    timeout_seconds=30
                )
            ]
        )
        
        return WorkflowOrchestrator(database=clean_real_db, config=config)
    
    @pytest.mark.asyncio
    async def test_complete_workflow_execution(self, orchestrator):
        """Test executing a complete review workflow."""
        review_id = ObjectId()
        
        # Start workflow
        workflow_id = await orchestrator.start_workflow(review_id)
        assert workflow_id is not None
        
        # Monitor workflow progress
        max_wait = 60  # seconds
        wait_time = 0
        
        while wait_time < max_wait:
            status = await orchestrator.get_workflow_status(workflow_id)
            
            if status == WorkflowStatus.COMPLETED:
                break
            elif status == WorkflowStatus.FAILED:
                pytest.fail("Workflow failed unexpectedly")
            
            await asyncio.sleep(1)
            wait_time += 1
        
        # Verify final state
        final_status = await orchestrator.get_workflow_status(workflow_id)
        assert final_status == WorkflowStatus.COMPLETED
        
        # Verify all tasks completed
        state = await orchestrator.get_workflow_state(workflow_id)
        assert state.completed_tasks == len(orchestrator.config.tasks)
        assert state.failed_tasks == 0
    
    @pytest.mark.asyncio
    async def test_workflow_error_recovery(self, orchestrator):
        """Test workflow recovery from task failures."""
        review_id = ObjectId()
        
        # Mock a failing task
        with pytest.mock.patch.object(
            orchestrator.task_executor, 
            'execute_task',
            side_effect=[Exception("Simulated failure"), True, True]
        ):
            workflow_id = await orchestrator.start_workflow(review_id)
            
            # Wait for workflow completion
            await self._wait_for_workflow_completion(orchestrator, workflow_id)
            
            # Verify workflow recovered and completed
            final_status = await orchestrator.get_workflow_status(workflow_id)
            assert final_status == WorkflowStatus.COMPLETED
    
    @pytest.mark.asyncio
    async def test_concurrent_workflows(self, orchestrator):
        """Test handling multiple concurrent workflows."""
        review_ids = [ObjectId() for _ in range(3)]
        
        # Start multiple workflows concurrently
        workflow_ids = await asyncio.gather(*[
            orchestrator.start_workflow(review_id) 
            for review_id in review_ids
        ])
        
        # Wait for all workflows to complete
        await asyncio.gather(*[
            self._wait_for_workflow_completion(orchestrator, workflow_id)
            for workflow_id in workflow_ids
        ])
        
        # Verify all workflows completed successfully
        statuses = await asyncio.gather(*[
            orchestrator.get_workflow_status(workflow_id)
            for workflow_id in workflow_ids
        ])
        
        assert all(status == WorkflowStatus.COMPLETED for status in statuses)
    
    async def _wait_for_workflow_completion(self, orchestrator, workflow_id, max_wait=60):
        """Helper to wait for workflow completion."""
        wait_time = 0
        while wait_time < max_wait:
            status = await orchestrator.get_workflow_status(workflow_id)
            if status in [WorkflowStatus.COMPLETED, WorkflowStatus.FAILED]:
                break
            await asyncio.sleep(1)
            wait_time += 1