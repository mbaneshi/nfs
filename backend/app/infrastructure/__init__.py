# Infrastructure Layer - External Concerns

import json
import uuid
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime

import httpx
from supabase import create_client, Client
from redis import Redis

from ..domain import (
    User, Content, Workflow, Email, ContentType, ContentStatus, WorkflowStatus,
    DomainEvent, UserCreatedEvent, ContentCreatedEvent, ContentPublishedEvent, WorkflowExecutedEvent
)


# Repository Interfaces
class UserRepository(ABC):
    @abstractmethod
    async def save(self, user: User) -> None:
        pass
    
    @abstractmethod
    async def get_by_id(self, user_id: str) -> Optional[User]:
        pass
    
    @abstractmethod
    async def get_by_email(self, email: Email) -> Optional[User]:
        pass
    
    @abstractmethod
    async def list(self, limit: int, offset: int) -> List[User]:
        pass


class ContentRepository(ABC):
    @abstractmethod
    async def save(self, content: Content) -> None:
        pass
    
    @abstractmethod
    async def get_by_id(self, content_id: str) -> Optional[Content]:
        pass
    
    @abstractmethod
    async def list_by_user(self, user_id: str, filters: Dict, limit: int, offset: int) -> List[Content]:
        pass


class WorkflowRepository(ABC):
    @abstractmethod
    async def save(self, workflow: Workflow) -> None:
        pass
    
    @abstractmethod
    async def get_by_id(self, workflow_id: str) -> Optional[Workflow]:
        pass
    
    @abstractmethod
    async def list_by_user(self, user_id: str, filters: Dict, limit: int, offset: int) -> List[Workflow]:
        pass


# Event Bus Interface
class EventBus(ABC):
    @abstractmethod
    async def publish(self, event: DomainEvent) -> None:
        pass


# Supabase Implementation
class SupabaseUserRepository(UserRepository):
    def __init__(self, supabase_client: Client):
        self.supabase = supabase_client
    
    async def save(self, user: User) -> None:
        user_data = {
            "id": user.id,
            "email": user.email.value,
            "name": user.name,
            "avatar_url": user.avatar_url,
            "created_at": user.created_at.isoformat(),
            "updated_at": user.updated_at.isoformat()
        }
        
        result = self.supabase.table("users").upsert(user_data).execute()
        if result.data is None:
            raise Exception("Failed to save user")
    
    async def get_by_id(self, user_id: str) -> Optional[User]:
        result = self.supabase.table("users").select("*").eq("id", user_id).execute()
        
        if not result.data:
            return None
        
        user_data = result.data[0]
        return User(
            id=user_data["id"],
            email=Email(user_data["email"]),
            name=user_data["name"],
            avatar_url=user_data.get("avatar_url"),
            created_at=datetime.fromisoformat(user_data["created_at"].replace('Z', '+00:00')),
            updated_at=datetime.fromisoformat(user_data["updated_at"].replace('Z', '+00:00'))
        )
    
    async def get_by_email(self, email: Email) -> Optional[User]:
        result = self.supabase.table("users").select("*").eq("email", email.value).execute()
        
        if not result.data:
            return None
        
        user_data = result.data[0]
        return User(
            id=user_data["id"],
            email=Email(user_data["email"]),
            name=user_data["name"],
            avatar_url=user_data.get("avatar_url"),
            created_at=datetime.fromisoformat(user_data["created_at"].replace('Z', '+00:00')),
            updated_at=datetime.fromisoformat(user_data["updated_at"].replace('Z', '+00:00'))
        )
    
    async def list(self, limit: int, offset: int) -> List[User]:
        result = self.supabase.table("users").select("*").range(offset, offset + limit - 1).execute()
        
        users = []
        for user_data in result.data:
            users.append(User(
                id=user_data["id"],
                email=Email(user_data["email"]),
                name=user_data["name"],
                avatar_url=user_data.get("avatar_url"),
                created_at=datetime.fromisoformat(user_data["created_at"].replace('Z', '+00:00')),
                updated_at=datetime.fromisoformat(user_data["updated_at"].replace('Z', '+00:00'))
            ))
        
        return users


class SupabaseContentRepository(ContentRepository):
    def __init__(self, supabase_client: Client):
        self.supabase = supabase_client
    
    async def save(self, content: Content) -> None:
        content_data = {
            "id": content.id,
            "title": content.title,
            "content_type": content.content_type.value,
            "content_body": content.content_body,
            "user_id": content.user_id,
            "status": content.status.value,
            "created_at": content.created_at.isoformat(),
            "updated_at": content.updated_at.isoformat(),
            "published_at": content.published_at.isoformat() if content.published_at else None
        }
        
        result = self.supabase.table("content").upsert(content_data).execute()
        if result.data is None:
            raise Exception("Failed to save content")
    
    async def get_by_id(self, content_id: str) -> Optional[Content]:
        result = self.supabase.table("content").select("*").eq("id", content_id).execute()
        
        if not result.data:
            return None
        
        content_data = result.data[0]
        return Content(
            id=content_data["id"],
            title=content_data["title"],
            content_type=ContentType(content_data["content_type"]),
            content_body=content_data["content_body"],
            user_id=content_data["user_id"],
            status=ContentStatus(content_data["status"]),
            created_at=datetime.fromisoformat(content_data["created_at"].replace('Z', '+00:00')),
            updated_at=datetime.fromisoformat(content_data["updated_at"].replace('Z', '+00:00')),
            published_at=datetime.fromisoformat(content_data["published_at"].replace('Z', '+00:00')) if content_data.get("published_at") else None
        )
    
    async def list_by_user(self, user_id: str, filters: Dict, limit: int, offset: int) -> List[Content]:
        query = self.supabase.table("content").select("*").eq("user_id", user_id)
        
        if "content_type" in filters:
            query = query.eq("content_type", filters["content_type"].value)
        if "status" in filters:
            query = query.eq("status", filters["status"].value)
        
        result = query.range(offset, offset + limit - 1).execute()
        
        contents = []
        for content_data in result.data:
            contents.append(Content(
                id=content_data["id"],
                title=content_data["title"],
                content_type=ContentType(content_data["content_type"]),
                content_body=content_data["content_body"],
                user_id=content_data["user_id"],
                status=ContentStatus(content_data["status"]),
                created_at=datetime.fromisoformat(content_data["created_at"].replace('Z', '+00:00')),
                updated_at=datetime.fromisoformat(content_data["updated_at"].replace('Z', '+00:00')),
                published_at=datetime.fromisoformat(content_data["published_at"].replace('Z', '+00:00')) if content_data.get("published_at") else None
            ))
        
        return contents


class SupabaseWorkflowRepository(WorkflowRepository):
    def __init__(self, supabase_client: Client):
        self.supabase = supabase_client
    
    async def save(self, workflow: Workflow) -> None:
        workflow_data = {
            "id": workflow.id,
            "name": workflow.name,
            "description": workflow.description,
            "status": workflow.status.value,
            "config": json.dumps(workflow.config),
            "user_id": workflow.user_id,
            "created_at": workflow.created_at.isoformat(),
            "updated_at": workflow.updated_at.isoformat()
        }
        
        result = self.supabase.table("workflows").upsert(workflow_data).execute()
        if result.data is None:
            raise Exception("Failed to save workflow")
    
    async def get_by_id(self, workflow_id: str) -> Optional[Workflow]:
        result = self.supabase.table("workflows").select("*").eq("id", workflow_id).execute()
        
        if not result.data:
            return None
        
        workflow_data = result.data[0]
        return Workflow(
            id=workflow_data["id"],
            name=workflow_data["name"],
            description=workflow_data.get("description"),
            status=WorkflowStatus(workflow_data["status"]),
            config=json.loads(workflow_data["config"]),
            user_id=workflow_data["user_id"],
            created_at=datetime.fromisoformat(workflow_data["created_at"].replace('Z', '+00:00')),
            updated_at=datetime.fromisoformat(workflow_data["updated_at"].replace('Z', '+00:00'))
        )
    
    async def list_by_user(self, user_id: str, filters: Dict, limit: int, offset: int) -> List[Workflow]:
        query = self.supabase.table("workflows").select("*").eq("user_id", user_id)
        
        if "status" in filters:
            query = query.eq("status", filters["status"].value)
        
        result = query.range(offset, offset + limit - 1).execute()
        
        workflows = []
        for workflow_data in result.data:
            workflows.append(Workflow(
                id=workflow_data["id"],
                name=workflow_data["name"],
                description=workflow_data.get("description"),
                status=WorkflowStatus(workflow_data["status"]),
                config=json.loads(workflow_data["config"]),
                user_id=workflow_data["user_id"],
                created_at=datetime.fromisoformat(workflow_data["created_at"].replace('Z', '+00:00')),
                updated_at=datetime.fromisoformat(workflow_data["updated_at"].replace('Z', '+00:00'))
            ))
        
        return workflows


# Redis Event Bus Implementation
class RedisEventBus(EventBus):
    def __init__(self, redis_client: Redis):
        self.redis = redis_client
    
    async def publish(self, event: DomainEvent) -> None:
        event_data = {
            "event_id": event.event_id,
            "event_type": event.__class__.__name__,
            "occurred_at": event.occurred_at.isoformat(),
            "data": self._serialize_event_data(event)
        }
        
        # Publish to Redis channel
        await self.redis.publish(f"events:{event.__class__.__name__}", json.dumps(event_data))
    
    def _serialize_event_data(self, event: DomainEvent) -> Dict[str, Any]:
        """Serialize event data to dictionary"""
        if isinstance(event, UserCreatedEvent):
            return {
                "user_id": event.user_id,
                "email": event.email,
                "name": event.name
            }
        elif isinstance(event, ContentCreatedEvent):
            return {
                "content_id": event.content_id,
                "user_id": event.user_id,
                "content_type": event.content_type
            }
        elif isinstance(event, ContentPublishedEvent):
            return {
                "content_id": event.content_id,
                "user_id": event.user_id,
                "published_at": event.published_at.isoformat()
            }
        elif isinstance(event, WorkflowExecutedEvent):
            return {
                "workflow_id": event.workflow_id,
                "user_id": event.user_id,
                "execution_data": event.execution_data
            }
        else:
            return {}


# n8n Integration
class N8nClient:
    def __init__(self, base_url: str, api_key: Optional[str] = None):
        self.base_url = base_url
        self.api_key = api_key
        self.client = httpx.AsyncClient()
    
    async def trigger_workflow(self, workflow_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Trigger n8n workflow via webhook"""
        url = f"{self.base_url}/webhook/{workflow_id}"
        
        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        response = await self.client.post(url, json=data, headers=headers)
        response.raise_for_status()
        return response.json()
    
    async def get_workflow_status(self, execution_id: str) -> Dict[str, Any]:
        """Get workflow execution status"""
        url = f"{self.base_url}/api/v1/executions/{execution_id}"
        
        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        response = await self.client.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()


# AI Service Integration
class OpenAIClient:
    def __init__(self, api_key: str, base_url: str = "https://api.openai.com/v1"):
        self.api_key = api_key
        self.base_url = base_url
        self.client = httpx.AsyncClient()
    
    async def generate_content(self, prompt: str, model: str = "gpt-4", max_tokens: int = 1000) -> str:
        """Generate content using OpenAI API"""
        url = f"{self.base_url}/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": model,
            "messages": [
                {"role": "system", "content": "You are a helpful AI assistant that generates high-quality content for social media and marketing purposes."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": max_tokens,
            "temperature": 0.7
        }
        
        response = await self.client.post(url, json=data, headers=headers)
        response.raise_for_status()
        
        result = response.json()
        return result["choices"][0]["message"]["content"]
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()


class AnthropicClient:
    def __init__(self, api_key: str, base_url: str = "https://api.anthropic.com/v1"):
        self.api_key = api_key
        self.base_url = base_url
        self.client = httpx.AsyncClient()
    
    async def generate_content(self, prompt: str, model: str = "claude-3-sonnet-20240229", max_tokens: int = 1000) -> str:
        """Generate content using Anthropic API"""
        url = f"{self.base_url}/messages"
        
        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        
        data = {
            "model": model,
            "max_tokens": max_tokens,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
        
        response = await self.client.post(url, json=data, headers=headers)
        response.raise_for_status()
        
        result = response.json()
        return result["content"][0]["text"]
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()


# Event Handlers
class ContentPublishedEventHandler:
    def __init__(self, n8n_client: N8nClient):
        self.n8n_client = n8n_client
    
    async def handle(self, event: ContentPublishedEvent) -> None:
        """Handle content published event by triggering social media workflow"""
        try:
            await self.n8n_client.trigger_workflow("social-media-posting", {
                "content_id": event.content_id,
                "user_id": event.user_id,
                "published_at": event.published_at.isoformat()
            })
        except Exception as e:
            print(f"Failed to trigger social media workflow: {e}")


class UserCreatedEventHandler:
    def __init__(self, n8n_client: N8nClient):
        self.n8n_client = n8n_client
    
    async def handle(self, event: UserCreatedEvent) -> None:
        """Handle user created event by sending welcome email"""
        try:
            await self.n8n_client.trigger_workflow("welcome-email", {
                "user_id": event.user_id,
                "email": event.email,
                "name": event.name
            })
        except Exception as e:
            print(f"Failed to send welcome email: {e}")
