# Test for Command Handlers

import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime
from app.application import (
    CreateUserCommand, UpdateUserCommand, CreateContentCommand, UpdateContentCommand,
    PublishContentCommand, CreateWorkflowCommand, ExecuteWorkflowCommand,
    CreateUserHandler, UpdateUserHandler, CreateContentHandler, UpdateContentHandler,
    PublishContentHandler, CreateWorkflowHandler, ExecuteWorkflowHandler
)
from app.domain import (
    User, Content, Workflow, Email, ContentType, ContentStatus, WorkflowStatus,
    UserNotFoundException, ContentNotFoundException, WorkflowNotFoundException,
    ContentDomainService, WorkflowDomainService
)


class TestCreateUserHandler:
    """Test CreateUserHandler command handler"""
    
    @pytest.fixture
    def mock_user_repository(self):
        return AsyncMock()
    
    @pytest.fixture
    def mock_event_bus(self):
        return AsyncMock()
    
    @pytest.fixture
    def handler(self, mock_user_repository, mock_event_bus):
        return CreateUserHandler(mock_user_repository, mock_event_bus)
    
    @pytest.mark.asyncio
    async def test_create_user_success(self, handler, mock_user_repository, mock_event_bus):
        """Test successful user creation"""
        # Arrange
        command = CreateUserCommand(
            email="test@example.com",
            name="Test User",
            avatar_url="https://example.com/avatar.jpg"
        )
        mock_user_repository.get_by_email.return_value = None
        
        # Act
        user = await handler.handle(command)
        
        # Assert
        assert isinstance(user, User)
        assert user.email.value == "test@example.com"
        assert user.name == "Test User"
        assert user.avatar_url == "https://example.com/avatar.jpg"
        mock_user_repository.save.assert_called_once_with(user)
        mock_event_bus.publish.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_user_email_already_exists(self, handler, mock_user_repository, mock_event_bus):
        """Test user creation with existing email fails"""
        # Arrange
        command = CreateUserCommand(
            email="existing@example.com",
            name="Test User"
        )
        existing_user = User(
            id="existing-id",
            email=Email("existing@example.com"),
            name="Existing User"
        )
        mock_user_repository.get_by_email.return_value = existing_user
        
        # Act & Assert
        with pytest.raises(ValueError, match="User with this email already exists"):
            await handler.handle(command)
    
    @pytest.mark.asyncio
    async def test_create_user_without_avatar(self, handler, mock_user_repository, mock_event_bus):
        """Test user creation without avatar URL"""
        # Arrange
        command = CreateUserCommand(
            email="test@example.com",
            name="Test User"
        )
        mock_user_repository.get_by_email.return_value = None
        
        # Act
        user = await handler.handle(command)
        
        # Assert
        assert user.avatar_url is None


class TestUpdateUserHandler:
    """Test UpdateUserHandler command handler"""
    
    @pytest.fixture
    def mock_user_repository(self):
        return AsyncMock()
    
    @pytest.fixture
    def mock_event_bus(self):
        return AsyncMock()
    
    @pytest.fixture
    def handler(self, mock_user_repository, mock_event_bus):
        return UpdateUserHandler(mock_user_repository, mock_event_bus)
    
    @pytest.mark.asyncio
    async def test_update_user_success(self, handler, mock_user_repository, mock_event_bus):
        """Test successful user update"""
        # Arrange
        command = UpdateUserCommand(
            user_id="user-123",
            name="Updated Name",
            avatar_url="https://example.com/new-avatar.jpg"
        )
        existing_user = User(
            id="user-123",
            email=Email("test@example.com"),
            name="Original Name"
        )
        mock_user_repository.get_by_id.return_value = existing_user
        
        # Act
        updated_user = await handler.handle(command)
        
        # Assert
        assert updated_user.name == "Updated Name"
        assert updated_user.avatar_url == "https://example.com/new-avatar.jpg"
        mock_user_repository.save.assert_called_once_with(updated_user)
    
    @pytest.mark.asyncio
    async def test_update_user_not_found(self, handler, mock_user_repository, mock_event_bus):
        """Test user update with non-existent user fails"""
        # Arrange
        command = UpdateUserCommand(
            user_id="nonexistent-user",
            name="Updated Name"
        )
        mock_user_repository.get_by_id.return_value = None
        
        # Act & Assert
        with pytest.raises(UserNotFoundException):
            await handler.handle(command)


class TestCreateContentHandler:
    """Test CreateContentHandler command handler"""
    
    @pytest.fixture
    def mock_content_repository(self):
        return AsyncMock()
    
    @pytest.fixture
    def mock_user_repository(self):
        return AsyncMock()
    
    @pytest.fixture
    def mock_event_bus(self):
        return AsyncMock()
    
    @pytest.fixture
    def handler(self, mock_content_repository, mock_user_repository, mock_event_bus):
        return CreateContentHandler(mock_content_repository, mock_user_repository, mock_event_bus)
    
    @pytest.mark.asyncio
    async def test_create_content_success(self, handler, mock_content_repository, mock_user_repository, mock_event_bus):
        """Test successful content creation"""
        # Arrange
        command = CreateContentCommand(
            title="Test Content",
            content_type="blog_article",
            content_body="This is test content",
            user_id="user-123"
        )
        existing_user = User(
            id="user-123",
            email=Email("test@example.com"),
            name="Test User"
        )
        mock_user_repository.get_by_id.return_value = existing_user
        
        # Act
        content = await handler.handle(command)
        
        # Assert
        assert isinstance(content, Content)
        assert content.title == "Test Content"
        assert content.content_type == ContentType.BLOG_ARTICLE
        assert content.content_body == "This is test content"
        assert content.user_id == "user-123"
        assert content.status == ContentStatus.DRAFT
        mock_content_repository.save.assert_called_once_with(content)
        mock_event_bus.publish.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_content_user_not_found(self, handler, mock_content_repository, mock_user_repository, mock_event_bus):
        """Test content creation with non-existent user fails"""
        # Arrange
        command = CreateContentCommand(
            title="Test Content",
            content_type="blog_article",
            content_body="This is test content",
            user_id="nonexistent-user"
        )
        mock_user_repository.get_by_id.return_value = None
        
        # Act & Assert
        with pytest.raises(UserNotFoundException):
            await handler.handle(command)


class TestUpdateContentHandler:
    """Test UpdateContentHandler command handler"""
    
    @pytest.fixture
    def mock_content_repository(self):
        return AsyncMock()
    
    @pytest.fixture
    def mock_event_bus(self):
        return AsyncMock()
    
    @pytest.fixture
    def handler(self, mock_content_repository, mock_event_bus):
        return UpdateContentHandler(mock_content_repository, mock_event_bus)
    
    @pytest.mark.asyncio
    async def test_update_content_success(self, handler, mock_content_repository, mock_event_bus):
        """Test successful content update"""
        # Arrange
        command = UpdateContentCommand(
            content_id="content-123",
            title="Updated Title",
            content_body="Updated content",
            user_id="user-123"
        )
        existing_content = Content(
            id="content-123",
            title="Original Title",
            content_type=ContentType.BLOG_ARTICLE,
            content_body="Original content",
            user_id="user-123"
        )
        mock_content_repository.get_by_id.return_value = existing_content
        
        # Act
        updated_content = await handler.handle(command)
        
        # Assert
        assert updated_content.title == "Updated Title"
        assert updated_content.content_body == "Updated content"
        mock_content_repository.save.assert_called_once_with(updated_content)
    
    @pytest.mark.asyncio
    async def test_update_content_not_found(self, handler, mock_content_repository, mock_event_bus):
        """Test content update with non-existent content fails"""
        # Arrange
        command = UpdateContentCommand(
            content_id="nonexistent-content",
            title="Updated Title",
            content_body="Updated content",
            user_id="user-123"
        )
        mock_content_repository.get_by_id.return_value = None
        
        # Act & Assert
        with pytest.raises(ContentNotFoundException):
            await handler.handle(command)
    
    @pytest.mark.asyncio
    async def test_update_content_unauthorized_user(self, handler, mock_content_repository, mock_event_bus):
        """Test content update with unauthorized user fails"""
        # Arrange
        command = UpdateContentCommand(
            content_id="content-123",
            title="Updated Title",
            content_body="Updated content",
            user_id="unauthorized-user"
        )
        existing_content = Content(
            id="content-123",
            title="Original Title",
            content_type=ContentType.BLOG_ARTICLE,
            content_body="Original content",
            user_id="user-123"
        )
        mock_content_repository.get_by_id.return_value = existing_content
        
        # Act & Assert
        with pytest.raises(ValueError, match="User not authorized to update this content"):
            await handler.handle(command)


class TestPublishContentHandler:
    """Test PublishContentHandler command handler"""
    
    @pytest.fixture
    def mock_content_repository(self):
        return AsyncMock()
    
    @pytest.fixture
    def mock_event_bus(self):
        return AsyncMock()
    
    @pytest.fixture
    def mock_content_domain_service(self):
        return MagicMock()
    
    @pytest.fixture
    def handler(self, mock_content_repository, mock_event_bus, mock_content_domain_service):
        return PublishContentHandler(mock_content_repository, mock_event_bus, mock_content_domain_service)
    
    @pytest.mark.asyncio
    async def test_publish_content_success(self, handler, mock_content_repository, mock_event_bus, mock_content_domain_service):
        """Test successful content publishing"""
        # Arrange
        command = PublishContentCommand(
            content_id="content-123",
            user_id="user-123"
        )
        existing_content = Content(
            id="content-123",
            title="Test Content",
            content_type=ContentType.BLOG_ARTICLE,
            content_body="Test content",
            user_id="user-123",
            status=ContentStatus.READY
        )
        mock_content_repository.get_by_id.return_value = existing_content
        mock_content_domain_service.validate_content_for_publication.return_value = True
        
        # Act
        published_content = await handler.handle(command)
        
        # Assert
        assert published_content.status == ContentStatus.PUBLISHED
        assert published_content.published_at is not None
        mock_content_repository.save.assert_called_once_with(published_content)
        assert mock_event_bus.publish.call_count == 1  # One for published event
    
    @pytest.mark.asyncio
    async def test_publish_content_not_ready(self, handler, mock_content_repository, mock_event_bus, mock_content_domain_service):
        """Test content publishing with invalid content fails"""
        # Arrange
        command = PublishContentCommand(
            content_id="content-123",
            user_id="user-123"
        )
        existing_content = Content(
            id="content-123",
            title="Test Content",
            content_type=ContentType.BLOG_ARTICLE,
            content_body="Test content",
            user_id="user-123",
            status=ContentStatus.READY
        )
        mock_content_repository.get_by_id.return_value = existing_content
        mock_content_domain_service.validate_content_for_publication.return_value = False
        
        # Act & Assert
        with pytest.raises(ValueError, match="Content is not ready for publication"):
            await handler.handle(command)


class TestCreateWorkflowHandler:
    """Test CreateWorkflowHandler command handler"""
    
    @pytest.fixture
    def mock_workflow_repository(self):
        return AsyncMock()
    
    @pytest.fixture
    def mock_event_bus(self):
        return AsyncMock()
    
    @pytest.fixture
    def mock_workflow_domain_service(self):
        return MagicMock()
    
    @pytest.fixture
    def handler(self, mock_workflow_repository, mock_event_bus, mock_workflow_domain_service):
        return CreateWorkflowHandler(mock_workflow_repository, mock_event_bus, mock_workflow_domain_service)
    
    @pytest.mark.asyncio
    async def test_create_workflow_success(self, handler, mock_workflow_repository, mock_event_bus, mock_workflow_domain_service):
        """Test successful workflow creation"""
        # Arrange
        command = CreateWorkflowCommand(
            name="Test Workflow",
            description="A test workflow",
            config={"trigger_type": "webhook", "actions": ["send_email"]},
            user_id="user-123"
        )
        mock_workflow_domain_service.validate_workflow_config.return_value = True
        
        # Act
        workflow = await handler.handle(command)
        
        # Assert
        assert isinstance(workflow, Workflow)
        assert workflow.name == "Test Workflow"
        assert workflow.description == "A test workflow"
        assert workflow.status == WorkflowStatus.INACTIVE
        assert workflow.config == command.config
        assert workflow.user_id == "user-123"
        mock_workflow_repository.save.assert_called_once_with(workflow)
    
    @pytest.mark.asyncio
    async def test_create_workflow_invalid_config(self, handler, mock_workflow_repository, mock_event_bus, mock_workflow_domain_service):
        """Test workflow creation with invalid config fails"""
        # Arrange
        command = CreateWorkflowCommand(
            name="Test Workflow",
            description="A test workflow",
            config={"invalid": "config"},
            user_id="user-123"
        )
        mock_workflow_domain_service.validate_workflow_config.return_value = False
        
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid workflow configuration"):
            await handler.handle(command)


class TestExecuteWorkflowHandler:
    """Test ExecuteWorkflowHandler command handler"""
    
    @pytest.fixture
    def mock_workflow_repository(self):
        return AsyncMock()
    
    @pytest.fixture
    def mock_event_bus(self):
        return AsyncMock()
    
    @pytest.fixture
    def handler(self, mock_workflow_repository, mock_event_bus):
        return ExecuteWorkflowHandler(mock_workflow_repository, mock_event_bus)
    
    @pytest.mark.asyncio
    async def test_execute_workflow_success(self, handler, mock_workflow_repository, mock_event_bus):
        """Test successful workflow execution"""
        # Arrange
        command = ExecuteWorkflowCommand(
            workflow_id="workflow-123",
            user_id="user-123",
            execution_data={"trigger_data": "test"}
        )
        existing_workflow = Workflow(
            id="workflow-123",
            name="Test Workflow",
            description="A test workflow",
            status=WorkflowStatus.ACTIVE,
            config={"trigger_type": "webhook", "actions": ["send_email"]},
            user_id="user-123"
        )
        mock_workflow_repository.get_by_id.return_value = existing_workflow
        
        # Act
        result = await handler.handle(command)
        
        # Assert
        assert result["workflow_id"] == "workflow-123"
        assert result["status"] == "executed"
        assert result["execution_data"] == command.execution_data
        mock_event_bus.publish.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_execute_workflow_not_found(self, handler, mock_workflow_repository, mock_event_bus):
        """Test workflow execution with non-existent workflow fails"""
        # Arrange
        command = ExecuteWorkflowCommand(
            workflow_id="nonexistent-workflow",
            user_id="user-123",
            execution_data={"trigger_data": "test"}
        )
        mock_workflow_repository.get_by_id.return_value = None
        
        # Act & Assert
        with pytest.raises(WorkflowNotFoundException):
            await handler.handle(command)
    
    @pytest.mark.asyncio
    async def test_execute_workflow_not_active(self, handler, mock_workflow_repository, mock_event_bus):
        """Test workflow execution with inactive workflow fails"""
        # Arrange
        command = ExecuteWorkflowCommand(
            workflow_id="workflow-123",
            user_id="user-123",
            execution_data={"trigger_data": "test"}
        )
        existing_workflow = Workflow(
            id="workflow-123",
            name="Test Workflow",
            description="A test workflow",
            status=WorkflowStatus.INACTIVE,
            config={"trigger_type": "webhook", "actions": ["send_email"]},
            user_id="user-123"
        )
        mock_workflow_repository.get_by_id.return_value = existing_workflow
        
        # Act & Assert
        with pytest.raises(ValueError, match="Workflow must be active to execute"):
            await handler.handle(command)
    
    @pytest.mark.asyncio
    async def test_execute_workflow_unauthorized_user(self, handler, mock_workflow_repository, mock_event_bus):
        """Test workflow execution with unauthorized user fails"""
        # Arrange
        command = ExecuteWorkflowCommand(
            workflow_id="workflow-123",
            user_id="unauthorized-user",
            execution_data={"trigger_data": "test"}
        )
        existing_workflow = Workflow(
            id="workflow-123",
            name="Test Workflow",
            description="A test workflow",
            status=WorkflowStatus.ACTIVE,
            config={"trigger_type": "webhook", "actions": ["send_email"]},
            user_id="user-123"
        )
        mock_workflow_repository.get_by_id.return_value = existing_workflow
        
        # Act & Assert
        with pytest.raises(ValueError, match="User not authorized to execute this workflow"):
            await handler.handle(command)
