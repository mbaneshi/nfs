# NSF Architecture Overview
## Clean Architecture + Domain-Driven Design Implementation

This document provides a comprehensive overview of the NSF template's architecture, patterns, and implementation details.

---

## 🏗️ **Architecture Overview**

### **Clean Architecture Layers**
```
┌─────────────────────────────────────────────────────────────┐
│                    Presentation Layer                       │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │   React Web     │  │  React Native   │  │   FastAPI   │ │
│  │   (Frontend)    │  │   (Mobile)       │  │   (API)     │ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│                   Application Layer                         │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │    Commands     │  │     Queries     │  │   Handlers  │ │
│  │   (Write Ops)   │  │   (Read Ops)    │  │ (CQRS)      │ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│                     Domain Layer                            │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │    Entities     │  │  Value Objects  │  │   Services  │ │
│  │  (Business)     │  │   (Types)       │  │ (Logic)     │ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│                 Infrastructure Layer                        │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │  Repositories   │  │   Event Bus     │  │  External   │ │
│  │  (Data Access)  │  │  (Redis)        │  │ Services    │ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 **Domain Layer**

### **Core Entities**

#### **User Entity**
```python
@dataclass
class User:
    id: str
    email: Email
    name: str
    avatar_url: Optional[str] = None
    created_at: datetime = None
    updated_at: datetime = None
    
    def update_profile(self, name: str, avatar_url: Optional[str] = None):
        self.name = name
        if avatar_url:
            self.avatar_url = avatar_url
        self.updated_at = datetime.utcnow()
```

#### **Content Entity**
```python
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
    
    def publish(self):
        if self.status != ContentStatus.READY:
            raise ValueError("Only ready content can be published")
        self.status = ContentStatus.PUBLISHED
        self.published_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        return ContentPublishedEvent(
            content_id=self.id,
            user_id=self.user_id,
            published_at=self.published_at
        )
```

#### **Workflow Entity**
```python
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
    
    def activate(self):
        self.status = WorkflowStatus.ACTIVE
        self.updated_at = datetime.utcnow()
```

### **Value Objects**

#### **Email Value Object**
```python
class Email:
    def __init__(self, value: str):
        if not self._is_valid_email(value):
            raise ValueError("Invalid email format")
        self.value = value
    
    def _is_valid_email(self, email: str) -> bool:
        import re
        pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
        return re.match(pattern, email) is not None
    
    def __eq__(self, other):
        return isinstance(other, Email) and self.value == other.value
```

#### **Content Type Enum**
```python
class ContentType(Enum):
    SOCIAL_MEDIA_POST = "social_media_post"
    BLOG_ARTICLE = "blog_article"
    EMAIL_CAMPAIGN = "email_campaign"
    PRODUCT_DESCRIPTION = "product_description"
```

### **Domain Services**

#### **Content Domain Service**
```python
class ContentDomainService:
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
```

### **Domain Events**

#### **Content Published Event**
```python
@dataclass
class ContentPublishedEvent(DomainEvent):
    content_id: str
    user_id: str
    published_at: datetime
```

---

## 🔄 **Application Layer**

### **CQRS Pattern Implementation**

#### **Commands (Write Operations)**
```python
@dataclass
class CreateContentCommand:
    title: str
    content_type: str
    content_body: str
    user_id: str

@dataclass
class PublishContentCommand:
    content_id: str
    user_id: str
```

#### **Queries (Read Operations)**
```python
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
```

#### **Command Handlers**
```python
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
            content_type=content.content_type.value
        )
        await self.event_bus.publish(event)
        
        return content
```

#### **Query Handlers**
```python
class GetContentHandler(QueryHandler):
    def __init__(self, content_repository):
        self.content_repository = content_repository
    
    async def handle(self, query: GetContentQuery) -> Optional[Content]:
        return await self.content_repository.get_by_id(query.content_id)
```

### **Application Services**
```python
class ContentApplicationService:
    def __init__(self, create_content_handler, update_content_handler, publish_content_handler, get_content_handler, list_content_handler):
        self.create_content_handler = create_content_handler
        self.update_content_handler = update_content_handler
        self.publish_content_handler = publish_content_handler
        self.get_content_handler = get_content_handler
        self.list_content_handler = list_content_handler
    
    async def create_content(self, command: CreateContentCommand) -> Content:
        return await self.create_content_handler.handle(command)
    
    async def get_content(self, query: GetContentQuery) -> Optional[Content]:
        return await self.get_content_handler.handle(query)
```

---

## 🏗️ **Infrastructure Layer**

### **Repository Pattern**

#### **Supabase User Repository**
```python
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
```

### **Event Bus Implementation**

#### **Redis Event Bus**
```python
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
```

### **External Service Integration**

#### **n8n Client**
```python
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
```

#### **AI Service Integration**
```python
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
```

---

## 🌐 **Presentation Layer**

### **FastAPI Routes**

#### **Content Routes**
```python
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
```

#### **AI Routes**
```python
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
```

### **Dependency Injection**
```python
def get_content_service(
    supabase_client=Depends(get_supabase_client),
    redis_client=Depends(get_redis_client)
):
    content_repository = SupabaseContentRepository(supabase_client)
    user_repository = SupabaseUserRepository(supabase_client)
    event_bus = RedisEventBus(redis_client)
    
    # Create handlers
    create_content_handler = CreateContentHandler(content_repository, user_repository, event_bus)
    update_content_handler = UpdateContentHandler(content_repository, event_bus)
    publish_content_handler = PublishContentHandler(content_repository, event_bus, content_domain_service)
    get_content_handler = GetContentHandler(content_repository)
    list_content_handler = ListContentHandler(content_repository)
    
    return ContentApplicationService(
        create_content_handler, update_content_handler, publish_content_handler,
        get_content_handler, list_content_handler
    )
```

---

## 🔄 **Event-Driven Architecture**

### **Event Flow**
```
1. User Action → Command → Command Handler
2. Command Handler → Domain Entity → Domain Event
3. Domain Event → Event Bus → Event Handlers
4. Event Handlers → External Services (n8n, AI, etc.)
5. External Services → Update Data → Real-time Sync
```

### **Event Handlers**
```python
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
```

---

## 🎯 **Architecture Benefits**

### **Scalability**
- **Independent Scaling**: Each layer can scale independently
- **Event-Driven**: Asynchronous communication for high performance
- **Microservices Ready**: Easy to extract services when needed
- **Database Optimization**: Optimized read and write operations

### **Maintainability**
- **Separation of Concerns**: Each layer has specific responsibilities
- **Testability**: Easy to unit test business logic in isolation
- **Business Logic Isolation**: Independent of frameworks
- **Clear Boundaries**: Easy to understand and modify

### **Flexibility**
- **Technology Agnostic**: Can swap any technology without breaking business logic
- **Provider Diversity**: Multiple AI providers and external services
- **Cross-Platform**: Shared business logic across web and mobile
- **Event-Driven**: Easy to add new integrations

### **Team Productivity**
- **Domain-Driven**: Code reflects business domain
- **Clean Interfaces**: Easy to understand and modify
- **Documentation**: Self-documenting code structure
- **Standards**: Consistent patterns across the codebase

---

## 🚀 **Next Steps**

### **Implementation Priority**
1. **Domain Layer**: Complete all entities and value objects
2. **Application Layer**: Implement all commands, queries, and handlers
3. **Infrastructure Layer**: Complete all repositories and external services
4. **Presentation Layer**: Implement all API endpoints
5. **Testing**: Comprehensive testing at all layers
6. **Documentation**: Complete API and integration documentation

### **Integration Points**
1. **Supabase**: Database, authentication, real-time features
2. **n8n**: Workflow automation and webhook triggers
3. **AI Services**: OpenAI and Anthropic integration
4. **Redis**: Event bus and caching
5. **Frontend**: React web and React Native mobile integration

This architecture provides a **solid foundation** for building scalable, maintainable, and AI-powered applications that can grow from startup to enterprise without major refactoring.
