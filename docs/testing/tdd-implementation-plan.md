# NSF Test-Driven Development Plan
## Comprehensive Testing Strategy for Clean Architecture

This document provides a complete TDD implementation plan for all components of the NSF template.

---

## 🎯 **TDD Strategy Overview**

### **Testing Philosophy**
- **Test-First Development**: Write tests before implementation
- **Red-Green-Refactor Cycle**: Fail → Pass → Improve
- **Architecture Compliance**: Validate Clean Architecture layers
- **Quality Assurance**: Ensure 80%+ test coverage
- **Continuous Integration**: Automated testing in CI/CD

### **Test Pyramid Structure**
```
        /\
       /  \     E2E Tests (10%)
      /____\    
     /      \   Integration Tests (20%)
    /________\  
   /          \ Unit Tests (70%)
  /____________\
```

---

## 🏗️ **Phase 1: Test Infrastructure Setup**

### **Backend Test Setup**
```bash
# Create test structure
mkdir -p backend/tests/{unit,integration,e2e,fixtures,mocks}

# Add test dependencies
echo "pytest-asyncio==0.21.1" >> backend/requirements.txt
echo "pytest-cov==4.1.0" >> backend/requirements.txt
echo "factory-boy==3.3.0" >> backend/requirements.txt
echo "faker==20.1.0" >> backend/requirements.txt
```

### **Web Test Setup**
```bash
# Add test dependencies
npm install --save-dev @testing-library/react @testing-library/jest-dom @testing-library/user-event
```

### **Mobile Test Setup**
```bash
# Add test dependencies
npm install --save-dev @testing-library/react-native react-native-testing-library detox
```

---

## 🧪 **Phase 2: Domain Layer Tests**

### **Entity Tests**
```python
# backend/tests/unit/domain/test_entities.py
class TestUserEntity:
    def test_user_creation(self):
        """Test User entity creation with valid data"""
        email = Email("test@edcopo.info")
        user = User(id="123", email=email, name="Test User")
        assert user.email.value == "test@edcopo.info"
        assert user.name == "Test User"
    
    def test_user_profile_update(self):
        """Test User profile update functionality"""
        user = User(id="123", email=Email("test@edcopo.info"), name="Test User")
        user.update_profile("Updated Name", "avatar.jpg")
        assert user.name == "Updated Name"
        assert user.avatar_url == "avatar.jpg"

class TestContentEntity:
    def test_content_creation(self):
        """Test Content entity creation"""
        content = Content(
            id="123",
            title="Test Content",
            content_type=ContentType.SOCIAL_MEDIA_POST,
            content_body="Test body",
            user_id="user123"
        )
        assert content.status == ContentStatus.DRAFT
    
    def test_content_publishing(self):
        """Test Content publishing workflow"""
        content = Content(...)
        content.mark_ready()
        event = content.publish()
        assert content.status == ContentStatus.PUBLISHED
        assert isinstance(event, ContentPublishedEvent)
```

### **Value Object Tests**
```python
# backend/tests/unit/domain/test_value_objects.py
class TestEmailValueObject:
    def test_valid_email(self):
        """Test valid email formats"""
        valid_emails = [
            "test@edcopo.info",
            "user.name@domain.com",
            "user+tag@domain.co.uk"
        ]
        for email in valid_emails:
            email_obj = Email(email)
            assert email_obj.value == email
    
    def test_invalid_email(self):
        """Test invalid email formats"""
        invalid_emails = [
            "invalid-email",
            "@domain.com",
            "user@",
            ""
        ]
        for email in invalid_emails:
            with pytest.raises(ValueError):
                Email(email)
```

---

## 🔄 **Phase 3: Application Layer Tests**

### **Command Handler Tests**
```python
# backend/tests/unit/application/test_command_handlers.py
class TestCreateUserHandler:
    @pytest.fixture
    def handler(self, mock_user_repo, mock_event_bus):
        return CreateUserHandler(mock_user_repo, mock_event_bus)
    
    async def test_create_user_success(self, handler):
        """Test successful user creation"""
        command = CreateUserCommand(
            email="test@edcopo.info",
            name="Test User"
        )
        user = await handler.handle(command)
        assert user.email.value == "test@edcopo.info"
        assert user.name == "Test User"
    
    async def test_create_user_duplicate_email(self, handler, mock_user_repo):
        """Test duplicate email handling"""
        mock_user_repo.get_by_email.return_value = User(...)
        command = CreateUserCommand(email="existing@edcopo.info", name="Test")
        with pytest.raises(ValueError, match="already exists"):
            await handler.handle(command)

class TestCreateContentHandler:
    async def test_create_content_success(self, handler):
        """Test successful content creation"""
        command = CreateContentCommand(
            title="Test Content",
            content_type="social_media_post",
            content_body="Test body",
            user_id="user123"
        )
        content = await handler.handle(command)
        assert content.title == "Test Content"
        assert content.content_type == ContentType.SOCIAL_MEDIA_POST
```

### **Query Handler Tests**
```python
# backend/tests/unit/application/test_query_handlers.py
class TestGetUserHandler:
    async def test_get_user_success(self, handler, mock_user_repo):
        """Test successful user retrieval"""
        mock_user = User(id="123", email=Email("test@edcopo.info"), name="Test")
        mock_user_repo.get_by_id.return_value = mock_user
        
        query = GetUserQuery(user_id="123")
        user = await handler.handle(query)
        assert user.id == "123"
        assert user.name == "Test"
    
    async def test_get_user_not_found(self, handler, mock_user_repo):
        """Test user not found handling"""
        mock_user_repo.get_by_id.return_value = None
        query = GetUserQuery(user_id="nonexistent")
        user = await handler.handle(query)
        assert user is None
```

---

## 🏗️ **Phase 4: Infrastructure Layer Tests**

### **Repository Tests**
```python
# backend/tests/unit/infrastructure/test_repositories.py
class TestSupabaseUserRepository:
    @pytest.fixture
    def repo(self, mock_supabase_client):
        return SupabaseUserRepository(mock_supabase_client)
    
    async def test_save_user(self, repo, mock_supabase_client):
        """Test user saving to Supabase"""
        user = User(id="123", email=Email("test@edcopo.info"), name="Test")
        await repo.save(user)
        mock_supabase_client.table.assert_called_with("users")
    
    async def test_get_user_by_id(self, repo, mock_supabase_client):
        """Test user retrieval by ID"""
        mock_data = {
            "id": "123",
            "email": "test@edcopo.info",
            "name": "Test User",
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z"
        }
        mock_supabase_client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [mock_data]
        
        user = await repo.get_by_id("123")
        assert user.id == "123"
        assert user.name == "Test User"
```

### **External Service Tests**
```python
# backend/tests/unit/infrastructure/test_external_services.py
class TestN8nClient:
    @pytest.fixture
    def client(self):
        return N8nClient("https://automation.edcopo.info")
    
    async def test_trigger_workflow(self, client, mock_httpx_client):
        """Test n8n workflow triggering"""
        mock_response = {"success": True}
        mock_httpx_client.post.return_value.json.return_value = mock_response
        
        result = await client.trigger_workflow("test-workflow", {"data": "test"})
        assert result["success"] is True

class TestOpenAIClient:
    async def test_generate_content(self, client, mock_httpx_client):
        """Test OpenAI content generation"""
        mock_response = {
            "choices": [{"message": {"content": "Generated content"}}]
        }
        mock_httpx_client.post.return_value.json.return_value = mock_response
        
        content = await client.generate_content("Test prompt")
        assert content == "Generated content"
```

---

## 🌐 **Phase 5: Presentation Layer Tests**

### **API Endpoint Tests**
```python
# backend/tests/integration/test_api_endpoints.py
class TestUserEndpoints:
    async def test_create_user(self, client):
        """Test user creation endpoint"""
        response = await client.post("/users", json={
            "email": "test@edcopo.info",
            "name": "Test User"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "test@edcopo.info"
        assert data["name"] == "Test User"
    
    async def test_get_user(self, client, test_user):
        """Test user retrieval endpoint"""
        response = await client.get(f"/users/{test_user.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_user.id

class TestContentEndpoints:
    async def test_create_content(self, client, auth_headers):
        """Test content creation endpoint"""
        response = await client.post("/content", json={
            "title": "Test Content",
            "content_type": "social_media_post",
            "content_body": "Test body"
        }, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Test Content"
    
    async def test_publish_content(self, client, auth_headers, test_content):
        """Test content publishing endpoint"""
        response = await client.post(f"/content/{test_content.id}/publish", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "published"
```

---

## 📱 **Phase 6: Frontend Tests**

### **Web Component Tests**
```typescript
// web/src/__tests__/components/Layout.test.tsx
import { render, screen } from '@testing-library/react';
import { Layout } from '../Layout';

describe('Layout Component', () => {
  it('renders navigation correctly', () => {
    render(<Layout />);
    expect(screen.getByRole('navigation')).toBeInTheDocument();
    expect(screen.getByText('Dashboard')).toBeInTheDocument();
    expect(screen.getByText('Automation')).toBeInTheDocument();
  });
  
  it('handles user authentication state', () => {
    const mockUser = { id: '123', name: 'Test User' };
    render(<Layout user={mockUser} />);
    expect(screen.getByText('Test User')).toBeInTheDocument();
  });
});
```

### **Web Store Tests**
```typescript
// web/src/__tests__/store/index.test.ts
import { configureStore } from '@reduxjs/toolkit';
import { userSlice } from '../store/userSlice';

describe('Redux Store', () => {
  let store: ReturnType<typeof configureStore>;
  
  beforeEach(() => {
    store = configureStore({
      reducer: {
        user: userSlice.reducer,
      },
    });
  });
  
  it('handles user login', () => {
    const action = userSlice.actions.login({ id: '123', name: 'Test User' });
    store.dispatch(action);
    
    const state = store.getState();
    expect(state.user.currentUser?.name).toBe('Test User');
  });
});
```

### **Web API Service Tests**
```typescript
// web/src/__tests__/services/api.test.ts
import { apiService } from '../services/api';
import { server } from '../../mocks/server';

describe('API Service', () => {
  beforeAll(() => server.listen());
  afterEach(() => server.resetHandlers());
  afterAll(() => server.close());
  
  it('creates content successfully', async () => {
    const contentData = {
      title: 'Test Content',
      content_type: 'social_media_post',
      content_body: 'Test body',
    };
    
    const result = await apiService.createContent(contentData);
    expect(result.title).toBe('Test Content');
    expect(result.status).toBe('draft');
  });
  
  it('handles API errors correctly', async () => {
    server.use(
      rest.post('/content', (req, res, ctx) => {
        return res(ctx.status(500), ctx.json({ error: 'Server error' }));
      })
    );
    
    await expect(apiService.createContent({})).rejects.toThrow('Server error');
  });
});
```

---

## 📱 **Phase 7: Mobile Tests**

### **Mobile Screen Tests**
```typescript
// mobile/src/__tests__/screens/DashboardScreen.test.tsx
import { render, screen } from '@testing-library/react-native';
import { DashboardScreen } from '../DashboardScreen';

describe('DashboardScreen', () => {
  it('renders dashboard correctly', () => {
    render(<DashboardScreen />);
    expect(screen.getByText('Dashboard')).toBeTruthy();
    expect(screen.getByText('Welcome to NSF')).toBeTruthy();
  });
  
  it('displays user content', () => {
    const mockContent = [
      { id: '1', title: 'Test Content', status: 'draft' }
    ];
    render(<DashboardScreen content={mockContent} />);
    expect(screen.getByText('Test Content')).toBeTruthy();
  });
});
```

### **Mobile Store Tests**
```typescript
// mobile/src/__tests__/services/store.test.ts
import { useContentStore } from '../services/store';

describe('Zustand Store', () => {
  beforeEach(() => {
    useContentStore.getState().reset();
  });
  
  it('manages content state correctly', () => {
    const { addContent, getContent } = useContentStore.getState();
    
    const content = { id: '1', title: 'Test', content_type: 'social_media_post' };
    addContent(content);
    
    const retrieved = getContent('1');
    expect(retrieved?.title).toBe('Test');
  });
});
```

---

## 🔗 **Phase 8: Integration Tests**

### **End-to-End Workflow Tests**
```python
# backend/tests/e2e/test_complete_workflow.py
class TestContentCreationWorkflow:
    async def test_complete_content_workflow(self, client, auth_headers):
        """Test complete content creation and publishing workflow"""
        # 1. Create content
        create_response = await client.post("/content", json={
            "title": "Test Content",
            "content_type": "social_media_post",
            "content_body": "Test body"
        }, headers=auth_headers)
        assert create_response.status_code == 200
        content_id = create_response.json()["id"]
        
        # 2. Mark content as ready
        update_response = await client.put(f"/content/{content_id}", json={
            "title": "Test Content",
            "content_body": "Updated body"
        }, headers=auth_headers)
        assert update_response.status_code == 200
        
        # 3. Publish content
        publish_response = await client.post(f"/content/{content_id}/publish", headers=auth_headers)
        assert publish_response.status_code == 200
        
        # 4. Verify content is published
        get_response = await client.get(f"/content/{content_id}")
        assert get_response.status_code == 200
        content = get_response.json()
        assert content["status"] == "published"
        assert content["published_at"] is not None
```

### **Cross-Platform Integration Tests**
```typescript
// tests/e2e/cross-platform.test.ts
describe('Cross-Platform Integration', () => {
  it('syncs data between web and mobile', async () => {
    // Create content on web
    const webContent = await webApi.createContent({
      title: 'Cross-platform test',
      content_type: 'social_media_post',
      content_body: 'Test body'
    });
    
    // Verify content appears on mobile
    const mobileContent = await mobileApi.getContent(webContent.id);
    expect(mobileContent.title).toBe('Cross-platform test');
    
    // Update content on mobile
    await mobileApi.updateContent(webContent.id, {
      title: 'Updated from mobile',
      content_body: 'Updated body'
    });
    
    // Verify update appears on web
    const updatedWebContent = await webApi.getContent(webContent.id);
    expect(updatedWebContent.title).toBe('Updated from mobile');
  });
});
```

---

## ⚡ **Phase 9: Performance Tests**

### **API Performance Tests**
```python
# backend/tests/performance/test_api_performance.py
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor

class TestAPIPerformance:
    async def test_concurrent_requests(self, client):
        """Test API performance under concurrent load"""
        async def make_request():
            response = await client.get("/health")
            return response.status_code
        
        start_time = time.time()
        tasks = [make_request() for _ in range(100)]
        results = await asyncio.gather(*tasks)
        end_time = time.time()
        
        assert all(status == 200 for status in results)
        assert (end_time - start_time) < 5.0  # Should complete within 5 seconds
    
    async def test_response_time(self, client):
        """Test API response time"""
        start_time = time.time()
        response = await client.get("/health")
        end_time = time.time()
        
        assert response.status_code == 200
        assert (end_time - start_time) < 0.2  # Should respond within 200ms
```

---

## 🔒 **Phase 10: Security Tests**

### **Authentication Security Tests**
```python
# backend/tests/security/test_security.py
class TestSecurity:
    async def test_jwt_validation(self, client):
        """Test JWT token validation"""
        # Test with invalid token
        response = await client.get("/users/me", headers={"Authorization": "Bearer invalid"})
        assert response.status_code == 401
        
        # Test with expired token
        expired_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
        response = await client.get("/users/me", headers={"Authorization": f"Bearer {expired_token}"})
        assert response.status_code == 401
    
    async def test_authorization(self, client, test_user, other_user):
        """Test user authorization"""
        # Test user can only access their own content
        response = await client.get(f"/content?user_id={other_user.id}")
        assert response.status_code == 403
        
        # Test user can access their own content
        response = await client.get(f"/content?user_id={test_user.id}")
        assert response.status_code == 200
```

---

## 🎯 **Test Coverage Goals**

### **Coverage Targets**
- **Domain Layer**: 100% (business logic must be fully tested)
- **Application Layer**: 95% (use cases are critical)
- **Infrastructure Layer**: 90% (external integrations)
- **Presentation Layer**: 85% (API endpoints)
- **Frontend Components**: 80% (UI components)
- **Overall Project**: 85% (comprehensive coverage)

### **Coverage Reporting**
```bash
# Backend coverage
pytest --cov=backend/app --cov-report=html --cov-report=term

# Web coverage
npm run test:coverage

# Mobile coverage
npm run test:coverage
```

---

## 🚀 **Implementation Timeline**

### **Week 1-2: Foundation**
- Set up test infrastructure
- Implement domain layer tests
- Create test fixtures and mocks

### **Week 3-4: Core Logic**
- Implement application layer tests
- Add infrastructure layer tests
- Create integration test framework

### **Week 5-6: API & Frontend**
- Implement presentation layer tests
- Add web frontend tests
- Create mobile frontend tests

### **Week 7-8: Integration**
- Implement end-to-end tests
- Add cross-platform tests
- Create performance tests

### **Week 9-10: Quality & Security**
- Implement security tests
- Add performance optimization tests
- Create comprehensive test reports

---

## 📊 **Success Metrics**

### **Quality Metrics**
- **Test Coverage**: >85% overall
- **Test Execution Time**: <5 minutes for full suite
- **Test Reliability**: >99% pass rate
- **Code Quality**: No critical issues

### **Development Metrics**
- **TDD Adoption**: 100% of new features
- **Bug Detection**: 90% caught by tests
- **Refactoring Safety**: 100% test coverage for changes
- **Documentation**: Tests serve as living documentation

This comprehensive TDD plan ensures **complete test coverage** and **architectural compliance** for the NSF template, following Clean Architecture principles and industry best practices.
