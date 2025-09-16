# Test for Workflow Entity Domain Logic

import pytest
from datetime import datetime
from app.domain import (
    Workflow, WorkflowStatus, WorkflowNotFoundException,
    WorkflowExecutedEvent, WorkflowExecutionException
)


class TestWorkflowEntity:
    """Test Workflow entity business logic"""
    
    def test_workflow_creation_with_valid_data(self):
        """Test Workflow entity creation with valid data"""
        # Arrange
        config = {
            "trigger_type": "webhook",
            "actions": ["send_email", "create_post"]
        }
        
        # Act
        workflow = Workflow(
            id="123",
            name="Test Workflow",
            description="A test workflow",
            status=WorkflowStatus.INACTIVE,
            config=config,
            user_id="user-123"
        )
        
        # Assert
        assert workflow.id == "123"
        assert workflow.name == "Test Workflow"
        assert workflow.description == "A test workflow"
        assert workflow.status == WorkflowStatus.INACTIVE
        assert workflow.config == config
        assert workflow.user_id == "user-123"
        assert workflow.created_at is not None
        assert workflow.updated_at is not None
    
    def test_workflow_activate(self):
        """Test Workflow activation"""
        # Arrange
        workflow = Workflow(
            id="123",
            name="Test Workflow",
            description="A test workflow",
            status=WorkflowStatus.INACTIVE,
            config={"trigger_type": "webhook", "actions": ["send_email"]},
            user_id="user-123"
        )
        original_updated_at = workflow.updated_at
        
        # Act
        workflow.activate()
        
        # Assert
        assert workflow.status == WorkflowStatus.ACTIVE
        assert workflow.updated_at > original_updated_at
    
    def test_workflow_deactivate(self):
        """Test Workflow deactivation"""
        # Arrange
        workflow = Workflow(
            id="123",
            name="Test Workflow",
            description="A test workflow",
            status=WorkflowStatus.ACTIVE,
            config={"trigger_type": "webhook", "actions": ["send_email"]},
            user_id="user-123"
        )
        original_updated_at = workflow.updated_at
        
        # Act
        workflow.deactivate()
        
        # Assert
        assert workflow.status == WorkflowStatus.INACTIVE
        assert workflow.updated_at > original_updated_at
    
    def test_workflow_pause_from_active(self):
        """Test Workflow pause from active status"""
        # Arrange
        workflow = Workflow(
            id="123",
            name="Test Workflow",
            description="A test workflow",
            status=WorkflowStatus.ACTIVE,
            config={"trigger_type": "webhook", "actions": ["send_email"]},
            user_id="user-123"
        )
        original_updated_at = workflow.updated_at
        
        # Act
        workflow.pause()
        
        # Assert
        assert workflow.status == WorkflowStatus.PAUSED
        assert workflow.updated_at > original_updated_at
    
    def test_workflow_pause_from_non_active_fails(self):
        """Test that pausing non-active workflow fails"""
        # Arrange
        workflow = Workflow(
            id="123",
            name="Test Workflow",
            description="A test workflow",
            status=WorkflowStatus.INACTIVE,
            config={"trigger_type": "webhook", "actions": ["send_email"]},
            user_id="user-123"
        )
        
        # Act & Assert
        with pytest.raises(ValueError, match="Only active workflows can be paused"):
            workflow.pause()
    
    def test_workflow_creation_without_description(self):
        """Test Workflow creation without optional description"""
        # Arrange
        config = {"trigger_type": "webhook", "actions": ["send_email"]}
        
        # Act
        workflow = Workflow(
            id="123",
            name="Test Workflow",
            description=None,
            status=WorkflowStatus.INACTIVE,
            config=config,
            user_id="user-123"
        )
        
        # Assert
        assert workflow.id == "123"
        assert workflow.name == "Test Workflow"
        assert workflow.description is None
        assert workflow.status == WorkflowStatus.INACTIVE
        assert workflow.config == config
        assert workflow.user_id == "user-123"
    
    def test_workflow_creation_with_different_statuses(self):
        """Test Workflow creation with different statuses"""
        statuses = [
            WorkflowStatus.ACTIVE,
            WorkflowStatus.INACTIVE,
            WorkflowStatus.ERROR,
            WorkflowStatus.PAUSED
        ]
        
        for status in statuses:
            # Act
            workflow = Workflow(
                id=f"workflow-{status.value}",
                name=f"Test {status.value} Workflow",
                description=f"A {status.value} workflow",
                status=status,
                config={"trigger_type": "webhook", "actions": ["send_email"]},
                user_id="user-123"
            )
            
            # Assert
            assert workflow.status == status


class TestWorkflowStatusEnum:
    """Test WorkflowStatus enum values"""
    
    def test_workflow_status_values(self):
        """Test WorkflowStatus enum has correct values"""
        assert WorkflowStatus.ACTIVE.value == "active"
        assert WorkflowStatus.INACTIVE.value == "inactive"
        assert WorkflowStatus.ERROR.value == "error"
        assert WorkflowStatus.PAUSED.value == "paused"
    
    def test_workflow_status_from_string(self):
        """Test creating WorkflowStatus from string"""
        assert WorkflowStatus("active") == WorkflowStatus.ACTIVE
        assert WorkflowStatus("inactive") == WorkflowStatus.INACTIVE
        assert WorkflowStatus("error") == WorkflowStatus.ERROR
        assert WorkflowStatus("paused") == WorkflowStatus.PAUSED


class TestWorkflowDomainExceptions:
    """Test Workflow domain exceptions"""
    
    def test_workflow_not_found_exception(self):
        """Test WorkflowNotFoundException"""
        # Act & Assert
        with pytest.raises(WorkflowNotFoundException):
            raise WorkflowNotFoundException("Workflow 123 not found")
    
    def test_workflow_not_found_exception_message(self):
        """Test WorkflowNotFoundException message"""
        # Arrange
        workflow_id = "nonexistent-workflow"
        
        # Act
        exception = WorkflowNotFoundException(f"Workflow {workflow_id} not found")
        
        # Assert
        assert str(exception) == f"Workflow {workflow_id} not found"
        assert isinstance(exception, Exception)
    
    def test_workflow_execution_exception(self):
        """Test WorkflowExecutionException"""
        # Act & Assert
        with pytest.raises(WorkflowExecutionException):
            raise WorkflowExecutionException("Workflow execution failed")
    
    def test_workflow_execution_exception_message(self):
        """Test WorkflowExecutionException message"""
        # Arrange
        error_message = "Workflow execution timeout"
        
        # Act
        exception = WorkflowExecutionException(error_message)
        
        # Assert
        assert str(exception) == error_message
        assert isinstance(exception, Exception)


class TestWorkflowExecutedEvent:
    """Test WorkflowExecutedEvent domain event"""
    
    def test_workflow_executed_event_creation(self):
        """Test WorkflowExecutedEvent creation"""
        # Arrange
        execution_data = {
            "trigger_data": {"user_id": "user-123"},
            "execution_time": "2024-01-01T00:00:00Z"
        }
        
        # Act
        event = WorkflowExecutedEvent(
            workflow_id="workflow-123",
            user_id="user-123",
            execution_data=execution_data
        )
        
        # Assert
        assert event.workflow_id == "workflow-123"
        assert event.user_id == "user-123"
        assert event.execution_data == execution_data
        assert event.event_id is not None
        assert event.occurred_at is not None
    
    def test_workflow_executed_event_auto_generated_fields(self):
        """Test WorkflowExecutedEvent auto-generated fields"""
        # Act
        event = WorkflowExecutedEvent(
            workflow_id="workflow-123",
            user_id="user-123",
            execution_data={"test": "data"}
        )
        
        # Assert
        assert event.event_id is not None
        assert len(event.event_id) > 0
        assert event.occurred_at is not None
        assert isinstance(event.occurred_at, datetime)


class TestWorkflowDomainService:
    """Test WorkflowDomainService business logic"""
    
    def test_validate_workflow_config_valid(self):
        """Test valid workflow configuration validation"""
        # Arrange
        from app.domain import WorkflowDomainService
        service = WorkflowDomainService()
        config = {
            "trigger_type": "webhook",
            "actions": ["send_email", "create_post"]
        }
        
        # Act
        is_valid = service.validate_workflow_config(config)
        
        # Assert
        assert is_valid is True
    
    def test_validate_workflow_config_missing_trigger_type(self):
        """Test workflow configuration validation with missing trigger_type"""
        # Arrange
        from app.domain import WorkflowDomainService
        service = WorkflowDomainService()
        config = {
            "actions": ["send_email"]
        }
        
        # Act
        is_valid = service.validate_workflow_config(config)
        
        # Assert
        assert is_valid is False
    
    def test_validate_workflow_config_missing_actions(self):
        """Test workflow configuration validation with missing actions"""
        # Arrange
        from app.domain import WorkflowDomainService
        service = WorkflowDomainService()
        config = {
            "trigger_type": "webhook"
        }
        
        # Act
        is_valid = service.validate_workflow_config(config)
        
        # Assert
        assert is_valid is False
    
    def test_can_execute_workflow_active(self):
        """Test workflow execution check for active workflow"""
        # Arrange
        from app.domain import WorkflowDomainService
        service = WorkflowDomainService()
        workflow = Workflow(
            id="123",
            name="Test Workflow",
            description="A test workflow",
            status=WorkflowStatus.ACTIVE,
            config={"trigger_type": "webhook", "actions": ["send_email"]},
            user_id="user-123"
        )
        
        # Act
        can_execute = service.can_execute_workflow(workflow)
        
        # Assert
        assert can_execute is True
    
    def test_can_execute_workflow_inactive(self):
        """Test workflow execution check for inactive workflow"""
        # Arrange
        from app.domain import WorkflowDomainService
        service = WorkflowDomainService()
        workflow = Workflow(
            id="123",
            name="Test Workflow",
            description="A test workflow",
            status=WorkflowStatus.INACTIVE,
            config={"trigger_type": "webhook", "actions": ["send_email"]},
            user_id="user-123"
        )
        
        # Act
        can_execute = service.can_execute_workflow(workflow)
        
        # Assert
        assert can_execute is False
