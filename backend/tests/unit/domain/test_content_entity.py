# Test for Content Entity Domain Logic

import pytest
from datetime import datetime, timezone
from app.domain import (
    Content, ContentType, ContentStatus, ContentNotFoundException,
    ContentPublishedEvent, InvalidContentException
)


class TestContentEntity:
    """Test Content entity business logic"""
    
    def test_content_creation_with_valid_data(self):
        """Test Content entity creation with valid data"""
        # Arrange
        content_type = ContentType.BLOG_ARTICLE
        
        # Act
        content = Content(
            id="123",
            title="Test Blog Post",
            content_type=content_type,
            content_body="This is a test blog post content.",
            user_id="user-123"
        )
        
        # Assert
        assert content.id == "123"
        assert content.title == "Test Blog Post"
        assert content.content_type == ContentType.BLOG_ARTICLE
        assert content.content_body == "This is a test blog post content."
        assert content.user_id == "user-123"
        assert content.status == ContentStatus.DRAFT
        assert content.created_at is not None
        assert content.updated_at is not None
        assert content.published_at is None
    
    def test_content_update(self):
        """Test Content update functionality"""
        # Arrange
        content = Content(
            id="123",
            title="Original Title",
            content_type=ContentType.BLOG_ARTICLE,
            content_body="Original content",
            user_id="user-123"
        )
        original_updated_at = content.updated_at
        
        # Act
        content.update_content("Updated Title", "Updated content")
        
        # Assert
        assert content.title == "Updated Title"
        assert content.content_body == "Updated content"
        assert content.updated_at > original_updated_at
    
    def test_content_mark_ready_from_draft(self):
        """Test marking content as ready from draft status"""
        # Arrange
        content = Content(
            id="123",
            title="Test Content",
            content_type=ContentType.BLOG_ARTICLE,
            content_body="Test content",
            user_id="user-123",
            status=ContentStatus.DRAFT
        )
        
        # Act
        content.mark_ready()
        
        # Assert
        assert content.status == ContentStatus.READY
        assert content.updated_at is not None
    
    def test_content_mark_ready_from_non_draft_fails(self):
        """Test that marking non-draft content as ready fails"""
        # Arrange
        content = Content(
            id="123",
            title="Test Content",
            content_type=ContentType.BLOG_ARTICLE,
            content_body="Test content",
            user_id="user-123",
            status=ContentStatus.READY
        )
        
        # Act & Assert
        with pytest.raises(ValueError, match="Only draft content can be marked as ready"):
            content.mark_ready()
    
    def test_content_publish_from_ready(self):
        """Test publishing content from ready status"""
        # Arrange
        content = Content(
            id="123",
            title="Test Content",
            content_type=ContentType.BLOG_ARTICLE,
            content_body="Test content",
            user_id="user-123",
            status=ContentStatus.READY
        )
        
        # Act
        event = content.publish()
        
        # Assert
        assert content.status == ContentStatus.PUBLISHED
        assert content.published_at is not None
        assert content.updated_at is not None
        assert isinstance(event, ContentPublishedEvent)
        assert event.content_id == content.id
        assert event.user_id == content.user_id
        assert event.published_at == content.published_at
    
    def test_content_publish_from_non_ready_fails(self):
        """Test that publishing non-ready content fails"""
        # Arrange
        content = Content(
            id="123",
            title="Test Content",
            content_type=ContentType.BLOG_ARTICLE,
            content_body="Test content",
            user_id="user-123",
            status=ContentStatus.DRAFT
        )
        
        # Act & Assert
        with pytest.raises(ValueError, match="Only ready content can be published"):
            content.publish()
    
    def test_content_creation_with_different_types(self):
        """Test Content creation with different content types"""
        content_types = [
            ContentType.SOCIAL_MEDIA_POST,
            ContentType.BLOG_ARTICLE,
            ContentType.EMAIL_CAMPAIGN,
            ContentType.PRODUCT_DESCRIPTION
        ]
        
        for content_type in content_types:
            # Act
            content = Content(
                id=f"content-{content_type.value}",
                title=f"Test {content_type.value}",
                content_type=content_type,
                content_body=f"Content for {content_type.value}",
                user_id="user-123"
            )
            
            # Assert
            assert content.content_type == content_type
            assert content.status == ContentStatus.DRAFT


class TestContentTypeEnum:
    """Test ContentType enum values"""
    
    def test_content_type_values(self):
        """Test ContentType enum has correct values"""
        assert ContentType.SOCIAL_MEDIA_POST.value == "social_media_post"
        assert ContentType.BLOG_ARTICLE.value == "blog_article"
        assert ContentType.EMAIL_CAMPAIGN.value == "email_campaign"
        assert ContentType.PRODUCT_DESCRIPTION.value == "product_description"
    
    def test_content_type_from_string(self):
        """Test creating ContentType from string"""
        assert ContentType("social_media_post") == ContentType.SOCIAL_MEDIA_POST
        assert ContentType("blog_article") == ContentType.BLOG_ARTICLE
        assert ContentType("email_campaign") == ContentType.EMAIL_CAMPAIGN
        assert ContentType("product_description") == ContentType.PRODUCT_DESCRIPTION


class TestContentStatusEnum:
    """Test ContentStatus enum values"""
    
    def test_content_status_values(self):
        """Test ContentStatus enum has correct values"""
        assert ContentStatus.DRAFT.value == "draft"
        assert ContentStatus.READY.value == "ready"
        assert ContentStatus.PUBLISHED.value == "published"
        assert ContentStatus.ARCHIVED.value == "archived"
    
    def test_content_status_from_string(self):
        """Test creating ContentStatus from string"""
        assert ContentStatus("draft") == ContentStatus.DRAFT
        assert ContentStatus("ready") == ContentStatus.READY
        assert ContentStatus("published") == ContentStatus.PUBLISHED
        assert ContentStatus("archived") == ContentStatus.ARCHIVED


class TestContentDomainExceptions:
    """Test Content domain exceptions"""
    
    def test_content_not_found_exception(self):
        """Test ContentNotFoundException"""
        # Act & Assert
        with pytest.raises(ContentNotFoundException):
            raise ContentNotFoundException("Content 123 not found")
    
    def test_content_not_found_exception_message(self):
        """Test ContentNotFoundException message"""
        # Arrange
        content_id = "nonexistent-content"
        
        # Act
        exception = ContentNotFoundException(f"Content {content_id} not found")
        
        # Assert
        assert str(exception) == f"Content {content_id} not found"
        assert isinstance(exception, Exception)
    
    def test_invalid_content_exception(self):
        """Test InvalidContentException"""
        # Act & Assert
        with pytest.raises(InvalidContentException):
            raise InvalidContentException("Content validation failed")
    
    def test_invalid_content_exception_message(self):
        """Test InvalidContentException message"""
        # Arrange
        error_message = "Content title cannot be empty"
        
        # Act
        exception = InvalidContentException(error_message)
        
        # Assert
        assert str(exception) == error_message
        assert isinstance(exception, Exception)


class TestContentPublishedEvent:
    """Test ContentPublishedEvent domain event"""
    
    def test_content_published_event_creation(self):
        """Test ContentPublishedEvent creation"""
        # Arrange
        published_at = datetime.now(timezone.utc)
        
        # Act
        event = ContentPublishedEvent(
            content_id="content-123",
            user_id="user-123",
            published_at=published_at
        )
        
        # Assert
        assert event.content_id == "content-123"
        assert event.user_id == "user-123"
        assert event.published_at == published_at
        assert event.event_id is not None
        assert event.occurred_at is not None
    
    def test_content_published_event_auto_generated_fields(self):
        """Test ContentPublishedEvent auto-generated fields"""
        # Act
        event = ContentPublishedEvent(
            content_id="content-123",
            user_id="user-123",
            published_at=datetime.now(timezone.utc)
        )
        
        # Assert
        assert event.event_id is not None
        assert len(event.event_id) > 0
        assert event.occurred_at is not None
        assert isinstance(event.occurred_at, datetime)
