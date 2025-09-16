# Domain Layer - Core Business Logic

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional
import uuid


# Value Objects
class Email:
    def __init__(self, value: str):
        if not self._is_valid_email(value):
            raise ValueError("Invalid email format")
        self.value = value
    
    def _is_valid_email(self, email: str) -> bool:
        import re
        # More strict email validation pattern
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        # Additional checks for common invalid patterns
        if not email or email.count('@') != 1:
            return False
        if email.startswith('.') or email.endswith('.'):
            return False
        if '..' in email:
            return False
        return re.match(pattern, email) is not None
    
    def __eq__(self, other):
        return isinstance(other, Email) and self.value == other.value
    
    def __hash__(self):
        return hash(self.value)
    
    def __str__(self):
        return self.value


class ContentType(Enum):
    SOCIAL_MEDIA_POST = "social_media_post"
    BLOG_ARTICLE = "blog_article"
    EMAIL_CAMPAIGN = "email_campaign"
    PRODUCT_DESCRIPTION = "product_description"


class ContentStatus(Enum):
    DRAFT = "draft"
    READY = "ready"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class WorkflowStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    PAUSED = "paused"


# Domain Entities
@dataclass
class User:
    id: str
    email: Email
    name: str
    avatar_url: Optional[str] = None
    created_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc)
        if self.updated_at is None:
            self.updated_at = datetime.now(timezone.utc)
    
    def update_profile(self, name: str, avatar_url: Optional[str] = None):
        self.name = name
        if avatar_url:
            self.avatar_url = avatar_url
        self.updated_at = datetime.now(timezone.utc)


@dataclass
class Content:
    id: str
    title: str
    content_type: ContentType
    content_body: str
    user_id: str
    status: ContentStatus = ContentStatus.DRAFT
    created_at: datetime = None
    updated_at: datetime = None
    published_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc)
        if self.updated_at is None:
            self.updated_at = datetime.now(timezone.utc)
    
    def update_content(self, title: str, content_body: str):
        self.title = title
        self.content_body = content_body
        self.updated_at = datetime.now(timezone.utc)
    
    def mark_ready(self):
        if self.status != ContentStatus.DRAFT:
            raise ValueError("Only draft content can be marked as ready")
        self.status = ContentStatus.READY
        self.updated_at = datetime.now(timezone.utc)
    
    def publish(self):
        if self.status != ContentStatus.READY:
            raise ValueError("Only ready content can be published")
        self.status = ContentStatus.PUBLISHED
        self.published_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)
        return ContentPublishedEvent(
            content_id=self.id,
            user_id=self.user_id,
            published_at=self.published_at
        )


@dataclass
class Workflow:
    id: str
    name: str
    description: Optional[str]
    status: WorkflowStatus
    config: dict
    user_id: str
    created_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc)
        if self.updated_at is None:
            self.updated_at = datetime.now(timezone.utc)
    
    def activate(self):
        self.status = WorkflowStatus.ACTIVE
        self.updated_at = datetime.now(timezone.utc)
    
    def deactivate(self):
        self.status = WorkflowStatus.INACTIVE
        self.updated_at = datetime.now(timezone.utc)
    
    def pause(self):
        if self.status != WorkflowStatus.ACTIVE:
            raise ValueError("Only active workflows can be paused")
        self.status = WorkflowStatus.PAUSED
        self.updated_at = datetime.now(timezone.utc)


# Domain Events
@dataclass
class DomainEvent:
    event_id: str
    occurred_at: datetime
    
    def __post_init__(self):
        if not self.event_id:
            self.event_id = str(uuid.uuid4())
        if not self.occurred_at:
            self.occurred_at = datetime.now(timezone.utc)


@dataclass
class UserCreatedEvent(DomainEvent):
    user_id: str
    email: str
    name: str


@dataclass
class ContentCreatedEvent(DomainEvent):
    content_id: str
    user_id: str
    content_type: str


@dataclass
class ContentPublishedEvent(DomainEvent):
    content_id: str
    user_id: str
    published_at: datetime
    
    def __init__(self, content_id: str, user_id: str, published_at: datetime, event_id: str = None, occurred_at: datetime = None):
        super().__init__(event_id=event_id or str(uuid.uuid4()), occurred_at=occurred_at or datetime.now(timezone.utc))
        self.content_id = content_id
        self.user_id = user_id
        self.published_at = published_at


@dataclass
class WorkflowExecutedEvent(DomainEvent):
    workflow_id: str
    user_id: str
    execution_data: dict
    
    def __init__(self, workflow_id: str, user_id: str, execution_data: dict, event_id: str = None, occurred_at: datetime = None):
        super().__init__(event_id=event_id or str(uuid.uuid4()), occurred_at=occurred_at or datetime.now(timezone.utc))
        self.workflow_id = workflow_id
        self.user_id = user_id
        self.execution_data = execution_data


# Domain Services
class ContentDomainService:
    def __init__(self):
        pass
    
    def generate_content_summary(self, content: Content) -> str:
        """Generate a summary of the content"""
        if len(content.content_body) <= 100:
            return content.content_body
        return content.content_body[:100] + "..."
    
    def validate_content_for_publication(self, content: Content) -> bool:
        """Validate if content is ready for publication"""
        return (
            content.status == ContentStatus.READY and
            len(content.title.strip()) > 0 and
            len(content.content_body.strip()) > 0
        )


class WorkflowDomainService:
    def __init__(self):
        pass
    
    def validate_workflow_config(self, config: dict) -> bool:
        """Validate workflow configuration"""
        required_fields = ["trigger_type", "actions"]
        return all(field in config for field in required_fields)
    
    def can_execute_workflow(self, workflow: Workflow) -> bool:
        """Check if workflow can be executed"""
        return workflow.status == WorkflowStatus.ACTIVE


# Domain Exceptions
class DomainException(Exception):
    """Base domain exception"""
    pass


class InvalidContentException(DomainException):
    """Raised when content validation fails"""
    pass


class WorkflowExecutionException(DomainException):
    """Raised when workflow execution fails"""
    pass


class UserNotFoundException(DomainException):
    """Raised when user is not found"""
    pass


class ContentNotFoundException(DomainException):
    """Raised when content is not found"""
    pass


class WorkflowNotFoundException(DomainException):
    """Raised when workflow is not found"""
    pass
