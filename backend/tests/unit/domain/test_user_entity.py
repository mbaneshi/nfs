# Test for User Entity Domain Logic

import pytest
from app.domain import User, Email, UserNotFoundException


class TestUserEntity:
    """Test User entity business logic"""
    
    def test_user_creation_with_valid_data(self):
        """Test User entity creation with valid data"""
        # Arrange
        email = Email("test@edcopo.info")
        
        # Act
        user = User(
            id="123",
            email=email,
            name="Test User",
            avatar_url="https://example.com/avatar.jpg"
        )
        
        # Assert
        assert user.id == "123"
        assert user.email.value == "test@edcopo.info"
        assert user.name == "Test User"
        assert user.avatar_url == "https://example.com/avatar.jpg"
        assert user.created_at is not None
        assert user.updated_at is not None
    
    def test_user_profile_update(self):
        """Test User profile update functionality"""
        # Arrange
        user = User(
            id="123",
            email=Email("test@edcopo.info"),
            name="Test User"
        )
        original_updated_at = user.updated_at
        
        # Act
        user.update_profile("Updated Name", "new-avatar.jpg")
        
        # Assert
        assert user.name == "Updated Name"
        assert user.avatar_url == "new-avatar.jpg"
        assert user.updated_at > original_updated_at
    
    def test_user_profile_update_without_avatar(self):
        """Test User profile update without changing avatar"""
        # Arrange
        user = User(
            id="123",
            email=Email("test@edcopo.info"),
            name="Test User",
            avatar_url="original-avatar.jpg"
        )
        
        # Act
        user.update_profile("Updated Name")
        
        # Assert
        assert user.name == "Updated Name"
        assert user.avatar_url == "original-avatar.jpg"  # Should remain unchanged
    
    def test_user_creation_without_optional_fields(self):
        """Test User creation with minimal required fields"""
        # Arrange
        email = Email("minimal@edcopo.info")
        
        # Act
        user = User(
            id="456",
            email=email,
            name="Minimal User"
        )
        
        # Assert
        assert user.id == "456"
        assert user.email.value == "minimal@edcopo.info"
        assert user.name == "Minimal User"
        assert user.avatar_url is None
        assert user.created_at is not None
        assert user.updated_at is not None


class TestEmailValueObject:
    """Test Email value object validation"""
    
    def test_valid_email_formats(self):
        """Test valid email formats"""
        valid_emails = [
            "test@edcopo.info",
            "user.name@domain.com",
            "user+tag@domain.co.uk",
            "user123@subdomain.example.org"
        ]
        
        for email_str in valid_emails:
            # Act
            email = Email(email_str)
            
            # Assert
            assert email.value == email_str
    
    def test_invalid_email_formats(self):
        """Test invalid email formats raise ValueError"""
        invalid_emails = [
            "invalid-email",
            "@domain.com",
            "user@",
            "",
            "user@domain",
            "user..name@domain.com",
            "user@domain..com"
        ]
        
        for email_str in invalid_emails:
            # Act & Assert
            with pytest.raises(ValueError, match="Invalid email format"):
                Email(email_str)
    
    def test_email_equality(self):
        """Test Email value object equality"""
        # Arrange
        email1 = Email("test@edcopo.info")
        email2 = Email("test@edcopo.info")
        email3 = Email("different@edcopo.info")
        
        # Assert
        assert email1 == email2
        assert email1 != email3
        assert hash(email1) == hash(email2)
        assert hash(email1) != hash(email3)
    
    def test_email_string_representation(self):
        """Test Email string representation"""
        # Arrange
        email = Email("test@edcopo.info")
        
        # Act
        email_str = str(email)
        
        # Assert
        assert email_str == "test@edcopo.info"


class TestUserDomainExceptions:
    """Test User domain exceptions"""
    
    def test_user_not_found_exception(self):
        """Test UserNotFoundException"""
        # Act & Assert
        with pytest.raises(UserNotFoundException):
            raise UserNotFoundException("User 123 not found")
    
    def test_user_not_found_exception_message(self):
        """Test UserNotFoundException message"""
        # Arrange
        user_id = "nonexistent-user"
        
        # Act
        exception = UserNotFoundException(f"User {user_id} not found")
        
        # Assert
        assert str(exception) == f"User {user_id} not found"
        assert isinstance(exception, Exception)
