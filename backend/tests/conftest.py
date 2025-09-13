# Test Configuration and Fixtures

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock
from datetime import datetime
import uuid

# Test fixtures for domain entities
@pytest.fixture
def sample_user():
    from app.domain import User, Email
    return User(
        id=str(uuid.uuid4()),
        email=Email("test@edcopo.info"),
        name="Test User",
        avatar_url="https://example.com/avatar.jpg"
    )

@pytest.fixture
def sample_content():
    from app.domain import Content, ContentType
    return Content(
        id=str(uuid.uuid4()),
        title="Test Content",
        content_type=ContentType.SOCIAL_MEDIA_POST,
        content_body="Test content body",
        user_id=str(uuid.uuid4())
    )

@pytest.fixture
def sample_workflow():
    from app.domain import Workflow, WorkflowStatus
    return Workflow(
        id=str(uuid.uuid4()),
        name="Test Workflow",
        description="Test workflow description",
        status=WorkflowStatus.ACTIVE,
        config={"trigger_type": "webhook", "actions": ["send_email"]},
        user_id=str(uuid.uuid4())
    )

# Mock fixtures for external services
@pytest.fixture
def mock_supabase_client():
    mock_client = Mock()
    mock_table = Mock()
    mock_table.upsert.return_value.execute.return_value.data = [{"id": "123"}]
    mock_table.select.return_value.eq.return_value.execute.return_value.data = [{"id": "123"}]
    mock_client.table.return_value = mock_table
    return mock_client

@pytest.fixture
def mock_redis_client():
    mock_client = AsyncMock()
    mock_client.publish.return_value = 1
    return mock_client

@pytest.fixture
def mock_n8n_client():
    mock_client = AsyncMock()
    mock_client.trigger_workflow.return_value = {"success": True}
    return mock_client

@pytest.fixture
def mock_openai_client():
    mock_client = AsyncMock()
    mock_client.generate_content.return_value = "Generated content"
    return mock_client

@pytest.fixture
def mock_anthropic_client():
    mock_client = AsyncMock()
    mock_client.generate_content.return_value = "Generated content"
    return mock_client

# Event loop fixture for async tests
@pytest.fixture
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

# Database fixtures
@pytest.fixture
def test_db():
    # Mock database for testing
    return Mock()

# Authentication fixtures
@pytest.fixture
def auth_headers():
    return {"Authorization": "Bearer test-jwt-token"}

@pytest.fixture
def test_user_id():
    return str(uuid.uuid4())

# API client fixture
@pytest.fixture
async def client():
    from fastapi.testclient import TestClient
    from main import app
    with TestClient(app) as test_client:
        yield test_client
