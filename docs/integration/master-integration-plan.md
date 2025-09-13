# NSF Master Integration Plan
## Supabase + n8n + Backend + Mobile + Web Integration

This document outlines the complete integration strategy for all components of the NSF template.

---

## 🎯 Integration Overview

### **Integration Goals**
- **Seamless Data Flow**: Real-time synchronization between all platforms
- **AI Automation**: Trigger workflows from any platform
- **Cross-Platform Consistency**: Shared business logic and data models
- **Event-Driven Architecture**: Asynchronous communication between services
- **Scalable Foundation**: Ready for microservices extraction

### **Integration Architecture**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Web     │    │  React Native   │    │   FastAPI       │
│   (Frontend)    │    │   (Mobile)      │    │   (Backend)    │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
                    ┌─────────────┴─────────────┐
                    │                           │
            ┌───────▼───────┐           ┌───────▼───────┐
            │   Supabase    │           │      n8n      │
            │  (Database +  │           │ (Automation +  │
            │   Auth +      │           │   Workflows)   │
            │  Real-time)   │           │                │
            └───────────────┘           └────────────────┘
```

---

## 🔄 Data Flow Integration

### **1. User Authentication Flow**
```
Mobile/Web → Supabase Auth → JWT Token → FastAPI Validation → User Context
```

**Implementation:**
- **Supabase Auth**: Handles user registration, login, password reset
- **JWT Validation**: FastAPI validates Supabase JWT tokens
- **User Context**: Shared user context across all platforms
- **Real-time Sync**: User profile changes sync in real-time

### **2. Content Management Flow**
```
Create Content → FastAPI → Supabase DB → Real-time Update → Mobile/Web
```

**Implementation:**
- **Content Creation**: FastAPI handles business logic and validation
- **Database Storage**: Supabase PostgreSQL for persistence
- **Real-time Updates**: Supabase Realtime for live updates
- **Cross-Platform**: Same content visible on web and mobile

### **3. AI Automation Flow**
```
Content Published → Domain Event → Event Bus → n8n Workflow → AI Generation → Update Content
```

**Implementation:**
- **Event Trigger**: Content publication triggers domain event
- **Event Bus**: Redis-based event publishing
- **n8n Workflow**: Visual workflow for AI content generation
- **AI Integration**: OpenAI/Anthropic for content generation
- **Content Update**: Generated content updates original content

---

## 🏗️ Component Integration Details

### **Supabase Integration**

#### **Database Schema**
```sql
-- Users table (extends Supabase auth.users)
CREATE TABLE public.users (
    id UUID REFERENCES auth.users(id) PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    avatar_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Content table
CREATE TABLE public.content (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    title TEXT NOT NULL,
    content_type TEXT NOT NULL CHECK (content_type IN ('social_media_post', 'blog_article', 'email_campaign', 'product_description')),
    content_body TEXT NOT NULL,
    user_id UUID REFERENCES public.users(id) NOT NULL,
    status TEXT NOT NULL DEFAULT 'draft' CHECK (status IN ('draft', 'ready', 'published', 'archived')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    published_at TIMESTAMP WITH TIME ZONE
);

-- Workflows table
CREATE TABLE public.workflows (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    status TEXT NOT NULL DEFAULT 'inactive' CHECK (status IN ('active', 'inactive', 'error', 'paused')),
    config JSONB NOT NULL,
    user_id UUID REFERENCES public.users(id) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Row Level Security (RLS)
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.content ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.workflows ENABLE ROW LEVEL SECURITY;

-- RLS Policies
CREATE POLICY "Users can view own profile" ON public.users FOR SELECT USING (auth.uid() = id);
CREATE POLICY "Users can update own profile" ON public.users FOR UPDATE USING (auth.uid() = id);

CREATE POLICY "Users can view own content" ON public.content FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can create own content" ON public.content FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own content" ON public.content FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can view own workflows" ON public.workflows FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can create own workflows" ON public.workflows FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own workflows" ON public.workflows FOR UPDATE USING (auth.uid() = user_id);
```

#### **Real-time Subscriptions**
```typescript
// Web Frontend
const { data, error } = await supabase
  .channel('content_changes')
  .on('postgres_changes', {
    event: '*',
    schema: 'public',
    table: 'content',
    filter: `user_id=eq.${userId}`
  }, (payload) => {
    console.log('Content changed:', payload);
    // Update UI in real-time
  })
  .subscribe();

// Mobile Frontend
const subscription = supabase
  .channel('content_changes')
  .on('postgres_changes', {
    event: '*',
    schema: 'public',
    table: 'content',
    filter: `user_id=eq.${userId}`
  }, (payload) => {
    // Update mobile UI in real-time
  })
  .subscribe();
```

### **n8n Integration**

#### **Workflow Templates**

**1. Content Publishing Workflow**
```json
{
  "name": "Content Publishing Workflow",
  "nodes": [
    {
      "name": "Webhook Trigger",
      "type": "n8n-nodes-base.webhook",
      "parameters": {
        "path": "content-published",
        "httpMethod": "POST"
      }
    },
    {
      "name": "Generate Social Media Posts",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "https://api.edcopo.info/ai/generate",
        "method": "POST",
        "body": {
          "prompt": "Create engaging social media posts for: {{ $json.title }}",
          "provider": "openai",
          "max_tokens": 500
        }
      }
    },
    {
      "name": "Update Content",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "https://api.edcopo.info/content/{{ $json.content_id }}",
        "method": "PUT",
        "body": {
          "title": "{{ $json.title }}",
          "content_body": "{{ $json.generated_content }}"
        }
      }
    }
  ]
}
```

**2. Welcome Email Workflow**
```json
{
  "name": "Welcome Email Workflow",
  "nodes": [
    {
      "name": "Webhook Trigger",
      "type": "n8n-nodes-base.webhook",
      "parameters": {
        "path": "user-registered",
        "httpMethod": "POST"
      }
    },
    {
      "name": "Generate Welcome Email",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "https://api.edcopo.info/ai/generate",
        "method": "POST",
        "body": {
          "prompt": "Create a personalized welcome email for {{ $json.name }}",
          "provider": "anthropic",
          "max_tokens": 300
        }
      }
    },
    {
      "name": "Send Email",
      "type": "n8n-nodes-base.emailSend",
      "parameters": {
        "to": "{{ $json.email }}",
        "subject": "Welcome to NSF AI Automation!",
        "text": "{{ $json.generated_content }}"
      }
    }
  ]
}
```

#### **API Integration**
```python
# FastAPI webhook endpoints
@app.post("/webhooks/content-published")
async def content_published_webhook(data: dict):
    """Trigger n8n workflow when content is published"""
    await n8n_client.trigger_workflow("content-publishing", data)
    return {"success": True}

@app.post("/webhooks/user-registered")
async def user_registered_webhook(data: dict):
    """Trigger n8n workflow when user registers"""
    await n8n_client.trigger_workflow("welcome-email", data)
    return {"success": True}
```

### **Backend Integration**

#### **Event-Driven Architecture**
```python
# Domain Events
@dataclass
class ContentPublishedEvent(DomainEvent):
    content_id: str
    user_id: str
    published_at: datetime

# Event Handler
class ContentPublishedEventHandler:
    def __init__(self, n8n_client: N8nClient):
        self.n8n_client = n8n_client
    
    async def handle(self, event: ContentPublishedEvent):
        await self.n8n_client.trigger_workflow("content-publishing", {
            "content_id": event.content_id,
            "user_id": event.user_id,
            "published_at": event.published_at.isoformat()
        })

# Event Bus
class RedisEventBus(EventBus):
    async def publish(self, event: DomainEvent):
        await self.redis.publish(f"events:{event.__class__.__name__}", event.to_dict())
```

#### **AI Integration**
```python
# Multi-provider AI service
class AIService:
    def __init__(self, openai_client: OpenAIClient, anthropic_client: AnthropicClient):
        self.openai_client = openai_client
        self.anthropic_client = anthropic_client
    
    async def generate_content(self, prompt: str, provider: str = "openai"):
        if provider == "openai":
            return await self.openai_client.generate_content(prompt)
        elif provider == "anthropic":
            return await self.anthropic_client.generate_content(prompt)
        else:
            raise ValueError("Invalid provider")
```

### **Frontend Integration**

#### **Web Frontend (React)**
```typescript
// API Service
class APIService {
  private supabase: SupabaseClient;
  private apiClient: AxiosInstance;

  constructor() {
    this.supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);
    this.apiClient = axios.create({
      baseURL: 'https://api.edcopo.info',
      headers: {
        'Authorization': `Bearer ${await this.supabase.auth.getSession().then(s => s.data.session?.access_token)}`
      }
    });
  }

  async createContent(content: CreateContentRequest): Promise<Content> {
    const response = await this.apiClient.post('/content', content);
    return response.data;
  }

  async publishContent(contentId: string): Promise<Content> {
    const response = await this.apiClient.post(`/content/${contentId}/publish`);
    return response.data;
  }

  // Real-time subscriptions
  subscribeToContentChanges(userId: string, callback: (payload: any) => void) {
    return this.supabase
      .channel('content_changes')
      .on('postgres_changes', {
        event: '*',
        schema: 'public',
        table: 'content',
        filter: `user_id=eq.${userId}`
      }, callback)
      .subscribe();
  }
}

// Redux Store
const store = configureStore({
  reducer: {
    auth: authSlice.reducer,
    content: contentSlice.reducer,
    workflows: workflowSlice.reducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      thunk: {
        extraArgument: { apiService: new APIService() }
      }
    })
});
```

#### **Mobile Frontend (React Native)**
```typescript
// API Service
class MobileAPIService {
  private supabase: SupabaseClient;
  private apiClient: AxiosInstance;

  constructor() {
    this.supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);
    this.apiClient = axios.create({
      baseURL: 'https://api.edcopo.info',
      headers: {
        'Authorization': `Bearer ${await this.supabase.auth.getSession().then(s => s.data.session?.access_token)}`
      }
    });
  }

  async createContent(content: CreateContentRequest): Promise<Content> {
    const response = await this.apiClient.post('/content', content);
    return response.data;
  }

  // Real-time subscriptions
  subscribeToContentChanges(userId: string, callback: (payload: any) => void) {
    return this.supabase
      .channel('content_changes')
      .on('postgres_changes', {
        event: '*',
        schema: 'public',
        table: 'content',
        filter: `user_id=eq.${userId}`
      }, callback)
      .subscribe();
  }
}

// Zustand Store
const useContentStore = create<ContentState>((set, get) => ({
  contents: [],
  loading: false,
  
  createContent: async (content: CreateContentRequest) => {
    set({ loading: true });
    try {
      const newContent = await apiService.createContent(content);
      set(state => ({ contents: [...state.contents, newContent] }));
    } finally {
      set({ loading: false });
    }
  },

  subscribeToChanges: (userId: string) => {
    return apiService.subscribeToContentChanges(userId, (payload) => {
      set(state => ({
        contents: state.contents.map(content => 
          content.id === payload.new.id ? payload.new : content
        )
      }));
    });
  }
}));
```

---

## 🔧 Integration Implementation Steps

### **Phase 1: Backend Foundation (Week 1)**
1. **Supabase Setup**
   - Create Supabase project
   - Run database migrations
   - Configure RLS policies
   - Set up authentication

2. **FastAPI Integration**
   - Implement Supabase repositories
   - Set up JWT validation
   - Create API endpoints
   - Implement event bus

3. **n8n Setup**
   - Deploy n8n instance
   - Create workflow templates
   - Set up webhook endpoints
   - Test workflow execution

### **Phase 2: Frontend Integration (Week 2)**
1. **Web Frontend**
   - Implement Supabase client
   - Create API service layer
   - Set up Redux store
   - Implement real-time subscriptions

2. **Mobile Frontend**
   - Implement Supabase client
   - Create API service layer
   - Set up Zustand store
   - Implement real-time subscriptions

### **Phase 3: AI Integration (Week 3)**
1. **AI Service Implementation**
   - Set up OpenAI client
   - Set up Anthropic client
   - Implement multi-provider service
   - Create AI generation endpoints

2. **Workflow Integration**
   - Create AI-powered workflows
   - Test content generation
   - Implement fallback strategies
   - Set up rate limiting

### **Phase 4: Testing & Optimization (Week 4)**
1. **Integration Testing**
   - Test complete data flow
   - Test real-time synchronization
   - Test AI automation workflows
   - Performance optimization

2. **Documentation & Deployment**
   - Complete documentation
   - Set up CI/CD pipeline
   - Deploy to production
   - Monitor and optimize

---

## 🎯 Success Metrics

### **Technical Metrics**
- **API Response Time**: < 200ms for all endpoints
- **Real-time Latency**: < 100ms for data synchronization
- **AI Generation Time**: < 5 seconds for content generation
- **Workflow Execution**: < 10 seconds for automation workflows
- **Uptime**: 99.9% availability

### **Business Metrics**
- **User Engagement**: Real-time updates increase user engagement
- **Content Quality**: AI-generated content improves quality
- **Automation Efficiency**: Workflows reduce manual work
- **Cross-Platform Consistency**: Same experience across platforms
- **Developer Productivity**: Template reduces development time

---

## 🚀 Next Steps

1. **Start with Backend**: Implement Supabase integration first
2. **Test Integration**: Use the test script to verify architecture
3. **Frontend Development**: Implement web and mobile frontends
4. **AI Integration**: Add AI-powered features
5. **Production Deployment**: Deploy and monitor the complete stack

This integration plan ensures **seamless communication** between all components while maintaining **scalability** and **maintainability** for future growth.
