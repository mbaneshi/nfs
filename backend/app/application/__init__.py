# Application Layer - Use Cases and Application Services

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional, Any
from datetime import datetime, timezone

import uuid
from ..domain import (
    User, Content, Workflow, Email, ContentType, ContentStatus, WorkflowStatus,
    UserCreatedEvent, ContentCreatedEvent, ContentPublishedEvent, WorkflowExecutedEvent,
    ContentDomainService, WorkflowDomainService,
    UserNotFoundException, ContentNotFoundException, WorkflowNotFoundException
)


# Commands (Write Operations)
@dataclass
class CreateUserCommand:
    email: str
    name: str
    avatar_url: Optional[str] = None


@dataclass
class UpdateUserCommand:
    user_id: str
    name: str
    avatar_url: Optional[str] = None


@dataclass
class CreateContentCommand:
    title: str
    content_type: str
    content_body: str
    user_id: str


@dataclass
class UpdateContentCommand:
    content_id: str
    title: str
    content_body: str
    user_id: str


@dataclass
class PublishContentCommand:
    content_id: str
    user_id: str


@dataclass
class CreateWorkflowCommand:
    name: str
    description: Optional[str]
    config: dict
    user_id: str


@dataclass
class ExecuteWorkflowCommand:
    workflow_id: str
    user_id: str
    execution_data: dict


# Queries (Read Operations)
@dataclass
class GetUserQuery:
    user_id: str


@dataclass
class GetUserByEmailQuery:
    email: str


@dataclass
class ListUsersQuery:
    limit: int = 20
    offset: int = 0


@dataclass
class GetContentQuery:
    content_id: str


@dataclass
class ListContentQuery:
    user_id: str
    content_type: Optional[str] = None
    status: Optional[str] = None
    limit: int = 20
    offset: int = 0


@dataclass
class GetWorkflowQuery:
    workflow_id: str


@dataclass
class ListWorkflowsQuery:
    user_id: str
    status: Optional[str] = None
    limit: int = 20
    offset: int = 0


# Command Handlers
class CommandHandler(ABC):
    @abstractmethod
    async def handle(self, command: Any) -> Any:
        pass


class CreateUserHandler(CommandHandler):
    def __init__(self, user_repository, event_bus):
        self.user_repository = user_repository
        self.event_bus = event_bus
    
    async def handle(self, command: CreateUserCommand) -> User:
        email = Email(command.email)
        
        # Check if user already exists
        existing_user = await self.user_repository.get_by_email(email)
        if existing_user:
            raise ValueError("User with this email already exists")
        
        user = User(
            id=str(uuid.uuid4()),
            email=email,
            name=command.name,
            avatar_url=command.avatar_url
        )
        
        await self.user_repository.save(user)
        
        # Publish domain event
        event = UserCreatedEvent(
            user_id=user.id,
            email=user.email.value,
            name=user.name,
            event_id=str(uuid.uuid4()),
            occurred_at=datetime.now(timezone.utc)
        )
        await self.event_bus.publish(event)
        
        return user


class CreateContentHandler(CommandHandler):
    def __init__(self, content_repository, user_repository, event_bus):
        self.content_repository = content_repository
        self.user_repository = user_repository
        self.event_bus = event_bus
    
    async def handle(self, command: CreateContentCommand) -> Content:
        # Verify user exists
        user = await self.user_repository.get_by_id(command.user_id)
        if not user:
            raise UserNotFoundException(f"User {command.user_id} not found")
        
        content = Content(
            id=str(uuid.uuid4()),
            title=command.title,
            content_type=ContentType(command.content_type),
            content_body=command.content_body,
            user_id=command.user_id
        )
        
        await self.content_repository.save(content)
        
        # Publish domain event
        event = ContentCreatedEvent(
            content_id=content.id,
            user_id=content.user_id,
            content_type=content.content_type.value,
            event_id=str(uuid.uuid4()),
            occurred_at=datetime.now(timezone.utc)
        )
        await self.event_bus.publish(event)
        
        return content


class PublishContentHandler(CommandHandler):
    def __init__(self, content_repository, event_bus, content_domain_service):
        self.content_repository = content_repository
        self.event_bus = event_bus
        self.content_domain_service = content_domain_service
    
    async def handle(self, command: PublishContentCommand) -> Content:
        content = await self.content_repository.get_by_id(command.content_id)
        if not content:
            raise ContentNotFoundException(f"Content {command.content_id} not found")
        
        if content.user_id != command.user_id:
            raise ValueError("User not authorized to publish this content")
        
        # Validate content for publication
        if not self.content_domain_service.validate_content_for_publication(content):
            raise ValueError("Content is not ready for publication")
        
        # Publish content (this triggers domain event)
        event = content.publish()
        await self.content_repository.save(content)
        
        # Publish domain event
        await self.event_bus.publish(event)
        
        return content


class CreateWorkflowHandler(CommandHandler):
    def __init__(self, workflow_repository, event_bus, workflow_domain_service):
        self.workflow_repository = workflow_repository
        self.event_bus = event_bus
        self.workflow_domain_service = workflow_domain_service
    
    async def handle(self, command: CreateWorkflowCommand) -> Workflow:
        # Validate workflow configuration
        if not self.workflow_domain_service.validate_workflow_config(command.config):
            raise ValueError("Invalid workflow configuration")
        
        workflow = Workflow(
            id=str(uuid.uuid4()),
            name=command.name,
            description=command.description,
            status=WorkflowStatus.INACTIVE,
            config=command.config,
            user_id=command.user_id
        )
        
        await self.workflow_repository.save(workflow)
        return workflow


class UpdateUserHandler(CommandHandler):
    def __init__(self, user_repository, event_bus):
        self.user_repository = user_repository
        self.event_bus = event_bus
    
    async def handle(self, command: UpdateUserCommand) -> User:
        # Get existing user
        user = await self.user_repository.get_by_id(command.user_id)
        if not user:
            raise UserNotFoundException(f"User {command.user_id} not found")
        
        # Update user profile
        user.update_profile(command.name, command.avatar_url)
        
        # Save updated user
        await self.user_repository.save(user)
        
        return user


class UpdateContentHandler(CommandHandler):
    def __init__(self, content_repository, event_bus):
        self.content_repository = content_repository
        self.event_bus = event_bus
    
    async def handle(self, command: UpdateContentCommand) -> Content:
        # Get existing content
        content = await self.content_repository.get_by_id(command.content_id)
        if not content:
            raise ContentNotFoundException(f"Content {command.content_id} not found")
        
        # Verify user ownership
        if content.user_id != command.user_id:
            raise ValueError("User not authorized to update this content")
        
        # Update content
        content.update_content(command.title, command.content_body)
        
        # Save updated content
        await self.content_repository.save(content)
        
        return content


class ExecuteWorkflowHandler(CommandHandler):
    def __init__(self, workflow_repository, event_bus):
        self.workflow_repository = workflow_repository
        self.event_bus = event_bus
    
    async def handle(self, command: ExecuteWorkflowCommand) -> dict:
        # Get workflow
        workflow = await self.workflow_repository.get_by_id(command.workflow_id)
        if not workflow:
            raise WorkflowNotFoundException(f"Workflow {command.workflow_id} not found")
        
        # Verify user ownership
        if workflow.user_id != command.user_id:
            raise ValueError("User not authorized to execute this workflow")
        
        # Check if workflow can be executed
        if workflow.status != WorkflowStatus.ACTIVE:
            raise ValueError("Workflow must be active to execute")
        
        # Create execution event
        event = WorkflowExecutedEvent(
            workflow_id=workflow.id,
            user_id=workflow.user_id,
            execution_data=command.execution_data
        )
        
        # Publish event
        await self.event_bus.publish(event)
        
        return {
            "workflow_id": workflow.id,
            "status": "executed",
            "execution_data": command.execution_data
        }


# Query Handlers
class QueryHandler(ABC):
    @abstractmethod
    async def handle(self, query: Any) -> Any:
        pass


class GetUserHandler(QueryHandler):
    def __init__(self, user_repository):
        self.user_repository = user_repository
    
    async def handle(self, query: GetUserQuery) -> Optional[User]:
        return await self.user_repository.get_by_id(query.user_id)


class GetUserByEmailHandler(QueryHandler):
    def __init__(self, user_repository):
        self.user_repository = user_repository
    
    async def handle(self, query: GetUserByEmailQuery) -> Optional[User]:
        email = Email(query.email)
        return await self.user_repository.get_by_email(email)


class ListUsersHandler(QueryHandler):
    def __init__(self, user_repository):
        self.user_repository = user_repository
    
    async def handle(self, query: ListUsersQuery) -> List[User]:
        return await self.user_repository.list(query.limit, query.offset)


class GetContentHandler(QueryHandler):
    def __init__(self, content_repository):
        self.content_repository = content_repository
    
    async def handle(self, query: GetContentQuery) -> Optional[Content]:
        return await self.content_repository.get_by_id(query.content_id)


class ListContentHandler(QueryHandler):
    def __init__(self, content_repository):
        self.content_repository = content_repository
    
    async def handle(self, query: ListContentQuery) -> List[Content]:
        filters = {}
        if query.content_type:
            filters['content_type'] = ContentType(query.content_type)
        if query.status:
            filters['status'] = ContentStatus(query.status)
        
        return await self.content_repository.list_by_user(
            query.user_id, 
            filters, 
            query.limit, 
            query.offset
        )


class GetWorkflowHandler(QueryHandler):
    def __init__(self, workflow_repository):
        self.workflow_repository = workflow_repository
    
    async def handle(self, query: GetWorkflowQuery) -> Optional[Workflow]:
        return await self.workflow_repository.get_by_id(query.workflow_id)


class ListWorkflowsHandler(QueryHandler):
    def __init__(self, workflow_repository):
        self.workflow_repository = workflow_repository
    
    async def handle(self, query: ListWorkflowsQuery) -> List[Workflow]:
        filters = {}
        if query.status:
            filters['status'] = WorkflowStatus(query.status)
        
        return await self.workflow_repository.list_by_user(
            query.user_id, 
            filters, 
            query.limit, 
            query.offset
        )


# Application Services
class UserApplicationService:
    def __init__(self, create_user_handler, update_user_handler, get_user_handler, get_user_by_email_handler, list_users_handler):
        self.create_user_handler = create_user_handler
        self.update_user_handler = update_user_handler
        self.get_user_handler = get_user_handler
        self.get_user_by_email_handler = get_user_by_email_handler
        self.list_users_handler = list_users_handler
    
    async def create_user(self, command: CreateUserCommand) -> User:
        return await self.create_user_handler.handle(command)
    
    async def update_user(self, command: UpdateUserCommand) -> User:
        return await self.update_user_handler.handle(command)
    
    async def get_user(self, query: GetUserQuery) -> Optional[User]:
        return await self.get_user_handler.handle(query)
    
    async def get_user_by_email(self, query: GetUserByEmailQuery) -> Optional[User]:
        return await self.get_user_by_email_handler.handle(query)
    
    async def list_users(self, query: ListUsersQuery) -> List[User]:
        return await self.list_users_handler.handle(query)


class ContentApplicationService:
    def __init__(self, create_content_handler, update_content_handler, publish_content_handler, get_content_handler, list_content_handler):
        self.create_content_handler = create_content_handler
        self.update_content_handler = update_content_handler
        self.publish_content_handler = publish_content_handler
        self.get_content_handler = get_content_handler
        self.list_content_handler = list_content_handler
    
    async def create_content(self, command: CreateContentCommand) -> Content:
        return await self.create_content_handler.handle(command)
    
    async def update_content(self, command: UpdateContentCommand) -> Content:
        return await self.update_content_handler.handle(command)
    
    async def publish_content(self, command: PublishContentCommand) -> Content:
        return await self.publish_content_handler.handle(command)
    
    async def get_content(self, query: GetContentQuery) -> Optional[Content]:
        return await self.get_content_handler.handle(query)
    
    async def list_content(self, query: ListContentQuery) -> List[Content]:
        return await self.list_content_handler.handle(query)


class WorkflowApplicationService:
    def __init__(self, create_workflow_handler, execute_workflow_handler, get_workflow_handler, list_workflows_handler):
        self.create_workflow_handler = create_workflow_handler
        self.execute_workflow_handler = execute_workflow_handler
        self.get_workflow_handler = get_workflow_handler
        self.list_workflows_handler = list_workflows_handler
    
    async def create_workflow(self, command: CreateWorkflowCommand) -> Workflow:
        return await self.create_workflow_handler.handle(command)
    
    async def execute_workflow(self, command: ExecuteWorkflowCommand) -> dict:
        return await self.execute_workflow_handler.handle(command)
    
    async def get_workflow(self, query: GetWorkflowQuery) -> Optional[Workflow]:
        return await self.get_workflow_handler.handle(query)
    
    async def list_workflows(self, query: ListWorkflowsQuery) -> List[Workflow]:
        return await self.list_workflows_handler.handle(query)
