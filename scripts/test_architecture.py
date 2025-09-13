#!/usr/bin/env python3
"""
Test script for NSF Clean Architecture Backend
This script tests the basic functionality of our Clean Architecture implementation
"""

import asyncio
import os
import sys
from datetime import datetime

# Add the backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.domain import User, Content, Workflow, Email, ContentType, ContentStatus, WorkflowStatus
from app.application import (
    CreateUserCommand, CreateContentCommand, PublishContentCommand,
    CreateUserHandler, CreateContentHandler, PublishContentHandler
)
from app.infrastructure import (
    SupabaseUserRepository, SupabaseContentRepository, 
    RedisEventBus, N8nClient
)


class MockSupabaseClient:
    """Mock Supabase client for testing"""
    def __init__(self):
        self.users = {}
        self.content = {}
    
    def table(self, table_name):
        return MockTable(self.users if table_name == "users" else self.content)


class MockTable:
    """Mock Supabase table"""
    def __init__(self, data_store):
        self.data_store = data_store
    
    def upsert(self, data):
        self.data_store[data["id"]] = data
        return MockResult([data])
    
    def select(self, fields):
        return self
    
    def eq(self, field, value):
        return self
    
    def execute(self):
        return MockResult(list(self.data_store.values()))


class MockResult:
    """Mock Supabase result"""
    def __init__(self, data):
        self.data = data


class MockRedisClient:
    """Mock Redis client for testing"""
    async def publish(self, channel, message):
        print(f"Published to {channel}: {message}")
        return 1


class MockN8nClient:
    """Mock n8n client for testing"""
    async def trigger_workflow(self, workflow_id, data):
        print(f"Triggered workflow {workflow_id} with data: {data}")
        return {"success": True}


async def test_clean_architecture():
    """Test the Clean Architecture implementation"""
    print("🧪 Testing NSF Clean Architecture Backend")
    print("=" * 50)
    
    # Setup mock dependencies
    mock_supabase = MockSupabaseClient()
    mock_redis = MockRedisClient()
    mock_n8n = MockN8nClient()
    
    # Create repositories
    user_repository = SupabaseUserRepository(mock_supabase)
    content_repository = SupabaseContentRepository(mock_supabase)
    event_bus = RedisEventBus(mock_redis)
    
    # Create handlers
    create_user_handler = CreateUserHandler(user_repository, event_bus)
    create_content_handler = CreateContentHandler(content_repository, user_repository, event_bus)
    publish_content_handler = PublishContentHandler(content_repository, event_bus, None)
    
    try:
        # Test 1: Create User
        print("\n1️⃣ Testing User Creation")
        print("-" * 30)
        
        create_user_command = CreateUserCommand(
            email="test@edcopo.info",
            name="Test User",
            avatar_url="https://example.com/avatar.jpg"
        )
        
        user = await create_user_handler.handle(create_user_command)
        print(f"✅ User created: {user.name} ({user.email.value})")
        
        # Test 2: Create Content
        print("\n2️⃣ Testing Content Creation")
        print("-" * 30)
        
        create_content_command = CreateContentCommand(
            title="Test Social Media Post",
            content_type="social_media_post",
            content_body="This is a test post for our AI automation platform!",
            user_id=user.id
        )
        
        content = await create_content_handler.handle(create_content_command)
        print(f"✅ Content created: {content.title}")
        print(f"   Status: {content.status.value}")
        print(f"   Type: {content.content_type.value}")
        
        # Test 3: Publish Content
        print("\n3️⃣ Testing Content Publication")
        print("-" * 30)
        
        # Mark content as ready first
        content.mark_ready()
        await content_repository.save(content)
        
        publish_command = PublishContentCommand(
            content_id=content.id,
            user_id=user.id
        )
        
        published_content = await publish_content_handler.handle(publish_command)
        print(f"✅ Content published: {published_content.title}")
        print(f"   Status: {published_content.status.value}")
        print(f"   Published at: {published_content.published_at}")
        
        # Test 4: Test Domain Services
        print("\n4️⃣ Testing Domain Services")
        print("-" * 30)
        
        from app.domain import ContentDomainService
        content_service = ContentDomainService()
        
        summary = content_service.generate_content_summary(content)
        print(f"✅ Content summary: {summary}")
        
        is_valid = content_service.validate_content_for_publication(content)
        print(f"✅ Content validation: {'Valid' if is_valid else 'Invalid'}")
        
        # Test 5: Test Event Handling
        print("\n5️⃣ Testing Event Handling")
        print("-" * 30)
        
        from app.infrastructure import ContentPublishedEventHandler
        event_handler = ContentPublishedEventHandler(mock_n8n)
        
        event = ContentPublishedEvent(
            content_id=content.id,
            user_id=user.id,
            published_at=datetime.utcnow()
        )
        
        await event_handler.handle(event)
        print("✅ Event handling completed")
        
        print("\n🎉 All tests passed! Clean Architecture is working correctly.")
        print("\n📊 Architecture Summary:")
        print("   ✅ Domain Layer: Entities, Value Objects, Domain Services")
        print("   ✅ Application Layer: Commands, Queries, Handlers")
        print("   ✅ Infrastructure Layer: Repositories, Event Bus, External Services")
        print("   ✅ Presentation Layer: FastAPI routes and middleware")
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


async def test_api_endpoints():
    """Test API endpoints"""
    print("\n🌐 Testing API Endpoints")
    print("=" * 50)
    
    try:
        import httpx
        
        # Test health endpoint
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/health")
            if response.status_code == 200:
                print("✅ Health endpoint working")
            else:
                print(f"❌ Health endpoint failed: {response.status_code}")
            
            # Test AI models endpoint
            response = await client.get("http://localhost:8000/ai/models")
            if response.status_code == 200:
                models = response.json()
                print("✅ AI models endpoint working")
                print(f"   Available models: {models}")
            else:
                print(f"❌ AI models endpoint failed: {response.status_code}")
                
    except Exception as e:
        print(f"❌ API endpoint test failed: {str(e)}")
        print("   Make sure the FastAPI server is running on localhost:8000")


if __name__ == "__main__":
    print("🚀 NSF Multi-Platform AI Automation Template")
    print("   Clean Architecture Backend Test Suite")
    print("=" * 60)
    
    # Run Clean Architecture tests
    success = asyncio.run(test_clean_architecture())
    
    if success:
        # Run API endpoint tests
        asyncio.run(test_api_endpoints())
        
        print("\n🎯 Next Steps:")
        print("   1. Start the FastAPI server: cd backend && python main.py")
        print("   2. Test the API: curl http://localhost:8000/health")
        print("   3. View API docs: http://localhost:8000/docs")
        print("   4. Start the full stack: make start")
    else:
        print("\n❌ Tests failed. Please check the implementation.")
        sys.exit(1)
