# Presentation Layer - API Routes and Middleware

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any
import os
import uuid

from ..domain import User, Content, Workflow, ContentType, ContentStatus, WorkflowStatus
from ..application import (
    CreateUserCommand, UpdateUserCommand, GetUserQuery, GetUserByEmailQuery, ListUsersQuery,
    CreateContentCommand, UpdateContentCommand, PublishContentCommand, GetContentQuery, ListContentQuery,
    CreateWorkflowCommand, ExecuteWorkflowCommand, GetWorkflowQuery, ListWorkflowsQuery,
    UserApplicationService, ContentApplicationService, WorkflowApplicationService
)
from ..infrastructure import (
    SupabaseUserRepository, SupabaseContentRepository, SupabaseWorkflowRepository,
    RedisEventBus, N8nClient, OpenAIClient, AnthropicClient,
    ContentPublishedEventHandler, UserCreatedEventHandler
)


# Pydantic Models for API
class UserCreateRequest(BaseModel):
    email: EmailStr
    name: str
    avatar_url: Optional[str] = None


class UserUpdateRequest(BaseModel):
    name: str
    avatar_url: Optional[str] = None


class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    avatar_url: Optional[str]
    created_at: str
    updated_at: str


class ContentCreateRequest(BaseModel):
    title: str
    content_type: str
    content_body: str


class ContentUpdateRequest(BaseModel):
    title: str
    content_body: str


class ContentResponse(BaseModel):
    id: str
    title: str
    content_type: str
    content_body: str
    user_id: str
    status: str
    created_at: str
    updated_at: str
    published_at: Optional[str]


class WorkflowCreateRequest(BaseModel):
    name: str
    description: Optional[str]
    config: Dict[str, Any]


class WorkflowExecuteRequest(BaseModel):
    execution_data: Dict[str, Any]


class WorkflowResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    status: str
    config: Dict[str, Any]
    user_id: str
    created_at: str
    updated_at: str


class AIGenerateRequest(BaseModel):
    prompt: str
    provider: str = "openai"
    model: Optional[str] = None
    max_tokens: int = 1000


class AIGenerateResponse(BaseModel):
    content: str
    provider: str
    model: str
    usage: Optional[Dict[str, Any]] = None


# Dependency Injection Setup
def get_supabase_client():
    from supabase import create_client
    return create_client(
        os.getenv("SUPABASE_URL", "https://db.edcopo.info"),
        os.getenv("SUPABASE_SERVICE_ROLE_KEY", "your_service_role_key")
    )


def get_redis_client():
    import redis.asyncio as redis
    return redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))


def get_n8n_client():
    return N8nClient(
        base_url=os.getenv("N8N_URL", "https://automation.edcopo.info"),
        api_key=os.getenv("N8N_API_KEY")
    )


def get_openai_client():
    return OpenAIClient(
        api_key=os.getenv("OPENAI_API_KEY", "your_openai_key")
    )


def get_anthropic_client():
    return AnthropicClient(
        api_key=os.getenv("ANTHROPIC_API_KEY", "your_anthropic_key")
    )


# Application Services Setup
def get_user_service(
    supabase_client=Depends(get_supabase_client),
    redis_client=Depends(get_redis_client),
    n8n_client=Depends(get_n8n_client)
):
    user_repository = SupabaseUserRepository(supabase_client)
    event_bus = RedisEventBus(redis_client)
    
    # Create handlers
    from ..application import CreateUserHandler, UpdateUserHandler, GetUserHandler, GetUserByEmailHandler, ListUsersHandler
    
    create_user_handler = CreateUserHandler(user_repository, event_bus)
    update_user_handler = UpdateUserHandler(user_repository, event_bus)
    get_user_handler = GetUserHandler(user_repository)
    get_user_by_email_handler = GetUserByEmailHandler(user_repository)
    list_users_handler = ListUsersHandler(user_repository)
    
    return UserApplicationService(
        create_user_handler, update_user_handler, get_user_handler,
        get_user_by_email_handler, list_users_handler
    )


def get_content_service(
    supabase_client=Depends(get_supabase_client),
    redis_client=Depends(get_redis_client)
):
    content_repository = SupabaseContentRepository(supabase_client)
    user_repository = SupabaseUserRepository(supabase_client)
    event_bus = RedisEventBus(redis_client)
    
    # Create handlers
    from ..application import CreateContentHandler, UpdateContentHandler, PublishContentHandler, GetContentHandler, ListContentHandler
    from ..domain import ContentDomainService
    
    content_domain_service = ContentDomainService()
    
    create_content_handler = CreateContentHandler(content_repository, user_repository, event_bus)
    update_content_handler = UpdateContentHandler(content_repository, event_bus)
    publish_content_handler = PublishContentHandler(content_repository, event_bus, content_domain_service)
    get_content_handler = GetContentHandler(content_repository)
    list_content_handler = ListContentHandler(content_repository)
    
    return ContentApplicationService(
        create_content_handler, update_content_handler, publish_content_handler,
        get_content_handler, list_content_handler
    )


def get_workflow_service(
    supabase_client=Depends(get_supabase_client),
    redis_client=Depends(get_redis_client)
):
    workflow_repository = SupabaseWorkflowRepository(supabase_client)
    event_bus = RedisEventBus(redis_client)
    
    # Create handlers
    from ..application import CreateWorkflowHandler, ExecuteWorkflowHandler, GetWorkflowHandler, ListWorkflowsHandler
    from ..domain import WorkflowDomainService
    
    workflow_domain_service = WorkflowDomainService()
    
    create_workflow_handler = CreateWorkflowHandler(workflow_repository, event_bus, workflow_domain_service)
    execute_workflow_handler = ExecuteWorkflowHandler(workflow_repository, event_bus)
    get_workflow_handler = GetWorkflowHandler(workflow_repository)
    list_workflows_handler = ListWorkflowsHandler(workflow_repository)
    
    return WorkflowApplicationService(
        create_workflow_handler, execute_workflow_handler,
        get_workflow_handler, list_workflows_handler
    )


# Authentication
security = HTTPBearer()


def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Extract user ID from JWT token"""
    # In a real implementation, you would validate the JWT token
    # and extract the user ID from it
    # For now, we'll use a simple approach
    token = credentials.credentials
    # TODO: Implement JWT validation with Supabase
    return "current_user_id"  # Placeholder


# FastAPI App
app = FastAPI(
    title="NSF AI Automation API",
    description="Multi-Platform AI Automation Template Backend",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "https://app.edcopo.info").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health Check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "nsf-api"}


# User Routes
@app.post("/users", response_model=UserResponse)
async def create_user(
    request: UserCreateRequest,
    user_service: UserApplicationService = Depends(get_user_service)
):
    command = CreateUserCommand(
        email=request.email,
        name=request.name,
        avatar_url=request.avatar_url
    )
    
    user = await user_service.create_user(command)
    
    return UserResponse(
        id=user.id,
        email=user.email.value,
        name=user.name,
        avatar_url=user.avatar_url,
        created_at=user.created_at.isoformat(),
        updated_at=user.updated_at.isoformat()
    )


@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    user_service: UserApplicationService = Depends(get_user_service)
):
    query = GetUserQuery(user_id=user_id)
    user = await user_service.get_user(query)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserResponse(
        id=user.id,
        email=user.email.value,
        name=user.name,
        avatar_url=user.avatar_url,
        created_at=user.created_at.isoformat(),
        updated_at=user.updated_at.isoformat()
    )


@app.get("/users", response_model=List[UserResponse])
async def list_users(
    limit: int = 20,
    offset: int = 0,
    user_service: UserApplicationService = Depends(get_user_service)
):
    query = ListUsersQuery(limit=limit, offset=offset)
    users = await user_service.list_users(query)
    
    return [
        UserResponse(
            id=user.id,
            email=user.email.value,
            name=user.name,
            avatar_url=user.avatar_url,
            created_at=user.created_at.isoformat(),
            updated_at=user.updated_at.isoformat()
        )
        for user in users
    ]


# Content Routes
@app.post("/content", response_model=ContentResponse)
async def create_content(
    request: ContentCreateRequest,
    current_user_id: str = Depends(get_current_user_id),
    content_service: ContentApplicationService = Depends(get_content_service)
):
    command = CreateContentCommand(
        title=request.title,
        content_type=request.content_type,
        content_body=request.content_body,
        user_id=current_user_id
    )
    
    content = await content_service.create_content(command)
    
    return ContentResponse(
        id=content.id,
        title=content.title,
        content_type=content.content_type.value,
        content_body=content.content_body,
        user_id=content.user_id,
        status=content.status.value,
        created_at=content.created_at.isoformat(),
        updated_at=content.updated_at.isoformat(),
        published_at=content.published_at.isoformat() if content.published_at else None
    )


@app.get("/content/{content_id}", response_model=ContentResponse)
async def get_content(
    content_id: str,
    content_service: ContentApplicationService = Depends(get_content_service)
):
    query = GetContentQuery(content_id=content_id)
    content = await content_service.get_content(query)
    
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    
    return ContentResponse(
        id=content.id,
        title=content.title,
        content_type=content.content_type.value,
        content_body=content.content_body,
        user_id=content.user_id,
        status=content.status.value,
        created_at=content.created_at.isoformat(),
        updated_at=content.updated_at.isoformat(),
        published_at=content.published_at.isoformat() if content.published_at else None
    )


@app.post("/content/{content_id}/publish", response_model=ContentResponse)
async def publish_content(
    content_id: str,
    current_user_id: str = Depends(get_current_user_id),
    content_service: ContentApplicationService = Depends(get_content_service)
):
    command = PublishContentCommand(
        content_id=content_id,
        user_id=current_user_id
    )
    
    content = await content_service.publish_content(command)
    
    return ContentResponse(
        id=content.id,
        title=content.title,
        content_type=content.content_type.value,
        content_body=content.content_body,
        user_id=content.user_id,
        status=content.status.value,
        created_at=content.created_at.isoformat(),
        updated_at=content.updated_at.isoformat(),
        published_at=content.published_at.isoformat() if content.published_at else None
    )


@app.get("/content", response_model=List[ContentResponse])
async def list_content(
    content_type: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    current_user_id: str = Depends(get_current_user_id),
    content_service: ContentApplicationService = Depends(get_content_service)
):
    query = ListContentQuery(
        user_id=current_user_id,
        content_type=content_type,
        status=status,
        limit=limit,
        offset=offset
    )
    
    contents = await content_service.list_content(query)
    
    return [
        ContentResponse(
            id=content.id,
            title=content.title,
            content_type=content.content_type.value,
            content_body=content.content_body,
            user_id=content.user_id,
            status=content.status.value,
            created_at=content.created_at.isoformat(),
            updated_at=content.updated_at.isoformat(),
            published_at=content.published_at.isoformat() if content.published_at else None
        )
        for content in contents
    ]


# Workflow Routes
@app.post("/workflows", response_model=WorkflowResponse)
async def create_workflow(
    request: WorkflowCreateRequest,
    current_user_id: str = Depends(get_current_user_id),
    workflow_service: WorkflowApplicationService = Depends(get_workflow_service)
):
    command = CreateWorkflowCommand(
        name=request.name,
        description=request.description,
        config=request.config,
        user_id=current_user_id
    )
    
    workflow = await workflow_service.create_workflow(command)
    
    return WorkflowResponse(
        id=workflow.id,
        name=workflow.name,
        description=workflow.description,
        status=workflow.status.value,
        config=workflow.config,
        user_id=workflow.user_id,
        created_at=workflow.created_at.isoformat(),
        updated_at=workflow.updated_at.isoformat()
    )


@app.get("/workflows/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(
    workflow_id: str,
    workflow_service: WorkflowApplicationService = Depends(get_workflow_service)
):
    query = GetWorkflowQuery(workflow_id=workflow_id)
    workflow = await workflow_service.get_workflow(query)
    
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    return WorkflowResponse(
        id=workflow.id,
        name=workflow.name,
        description=workflow.description,
        status=workflow.status.value,
        config=workflow.config,
        user_id=workflow.user_id,
        created_at=workflow.created_at.isoformat(),
        updated_at=workflow.updated_at.isoformat()
    )


@app.get("/workflows", response_model=List[WorkflowResponse])
async def list_workflows(
    status: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    current_user_id: str = Depends(get_current_user_id),
    workflow_service: WorkflowApplicationService = Depends(get_workflow_service)
):
    query = ListWorkflowsQuery(
        user_id=current_user_id,
        status=status,
        limit=limit,
        offset=offset
    )
    
    workflows = await workflow_service.list_workflows(query)
    
    return [
        WorkflowResponse(
            id=workflow.id,
            name=workflow.name,
            description=workflow.description,
            status=workflow.status.value,
            config=workflow.config,
            user_id=workflow.user_id,
            created_at=workflow.created_at.isoformat(),
            updated_at=workflow.updated_at.isoformat()
        )
        for workflow in workflows
    ]


# AI Routes
@app.post("/ai/generate", response_model=AIGenerateResponse)
async def generate_content(
    request: AIGenerateRequest,
    openai_client: OpenAIClient = Depends(get_openai_client),
    anthropic_client: AnthropicClient = Depends(get_anthropic_client)
):
    try:
        if request.provider == "openai":
            model = request.model or "gpt-4"
            content = await openai_client.generate_content(
                request.prompt, model, request.max_tokens
            )
            return AIGenerateResponse(
                content=content,
                provider="openai",
                model=model
            )
        elif request.provider == "anthropic":
            model = request.model or "claude-3-sonnet-20240229"
            content = await anthropic_client.generate_content(
                request.prompt, model, request.max_tokens
            )
            return AIGenerateResponse(
                content=content,
                provider="anthropic",
                model=model
            )
        else:
            raise HTTPException(status_code=400, detail="Invalid provider")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI generation failed: {str(e)}")


@app.get("/ai/models")
async def get_ai_models():
    return {
        "openai": ["gpt-4", "gpt-3.5-turbo"],
        "anthropic": ["claude-3-sonnet-20240229", "claude-3-haiku-20240307"]
    }


# n8n Webhook Routes
@app.post("/webhooks/content-published")
async def content_published_webhook(
    data: Dict[str, Any],
    n8n_client: N8nClient = Depends(get_n8n_client)
):
    """Webhook endpoint for n8n to trigger when content is published"""
    try:
        await n8n_client.trigger_workflow("social-media-posting", data)
        return {"success": True, "message": "Workflow triggered successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to trigger workflow: {str(e)}")


@app.post("/webhooks/user-registered")
async def user_registered_webhook(
    data: Dict[str, Any],
    n8n_client: N8nClient = Depends(get_n8n_client)
):
    """Webhook endpoint for n8n to trigger when user registers"""
    try:
        await n8n_client.trigger_workflow("welcome-email", data)
        return {"success": True, "message": "Welcome email workflow triggered"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to trigger welcome email: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=os.getenv("API_HOST", "0.0.0.0"),
        port=int(os.getenv("API_PORT", "8000")),
        reload=os.getenv("API_RELOAD", "true").lower() == "true",
        log_level=os.getenv("API_LOG_LEVEL", "info").lower()
    )
