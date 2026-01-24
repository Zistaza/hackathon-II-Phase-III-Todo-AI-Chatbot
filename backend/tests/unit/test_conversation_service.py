import pytest
from unittest.mock import Mock, MagicMock
from sqlmodel import Session, select
from datetime import datetime
from uuid import uuid4

from backend.src.models.conversation_model import Conversation, ConversationCreate
from backend.src.models.message_model import Message, MessageCreate
from backend.src.services.conversation_service import ConversationService


class TestConversationService:
    """Unit tests for ConversationService"""

    def setup_method(self):
        """Setup test fixtures before each test method."""
        self.mock_session = Mock(spec=Session)
        self.conversation_service = ConversationService(self.mock_session)

    def test_create_conversation_success(self):
        """Test creating a conversation successfully"""
        # Arrange
        user_id = "test_user_123"
        conversation_data = ConversationCreate(title="Test Conversation")

        mock_conversation = Conversation(
            id="conv_123",
            user_id=user_id,
            title="Test Conversation",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        self.mock_session.add = Mock()
        self.mock_session.commit = Mock()
        self.mock_session.refresh = Mock(return_value=mock_conversation)

        # Act
        result = self.conversation_service.create_conversation(user_id, conversation_data)

        # Assert
        assert result.user_id == user_id
        assert result.title == "Test Conversation"
        self.mock_session.add.assert_called_once()
        self.mock_session.commit.assert_called_once()
        self.mock_session.refresh.assert_called_once()

    def test_get_user_conversations(self):
        """Test getting user's conversations"""
        # Arrange
        user_id = "test_user_123"
        mock_conversations = [
            Conversation(id="conv1", user_id=user_id, title="Conv 1", created_at=datetime.utcnow(), updated_at=datetime.utcnow()),
            Conversation(id="conv2", user_id=user_id, title="Conv 2", created_at=datetime.utcnow(), updated_at=datetime.utcnow())
        ]

        mock_exec_result = Mock()
        mock_exec_result.all = Mock(return_value=mock_conversations)
        self.mock_session.exec = Mock(return_value=mock_exec_result)

        # Act
        result = self.conversation_service.get_user_conversations(user_id)

        # Assert
        assert len(result) == 2
        assert result[0].user_id == user_id
        self.mock_session.exec.assert_called_once()

    def test_get_conversation_by_id_found(self):
        """Test getting a conversation by ID when it exists"""
        # Arrange
        user_id = "test_user_123"
        conversation_id = "conv_123"
        mock_conversation = Conversation(
            id=conversation_id,
            user_id=user_id,
            title="Test Conv",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        mock_exec_result = Mock()
        mock_exec_result.first = Mock(return_value=mock_conversation)
        self.mock_session.exec = Mock(return_value=mock_exec_result)

        # Act
        result = self.conversation_service.get_conversation_by_id(conversation_id, user_id)

        # Assert
        assert result.id == conversation_id
        assert result.user_id == user_id
        assert result.title == "Test Conv"

    def test_get_conversation_by_id_not_found(self):
        """Test getting a conversation by ID when it doesn't exist"""
        # Arrange
        user_id = "test_user_123"
        conversation_id = "nonexistent_conv"

        mock_exec_result = Mock()
        mock_exec_result.first = Mock(return_value=None)
        self.mock_session.exec = Mock(return_value=mock_exec_result)

        # Act
        result = self.conversation_service.get_conversation_by_id(conversation_id, user_id)

        # Assert
        assert result is None

    def test_add_message_to_conversation_success(self):
        """Test adding a message to a conversation successfully"""
        # Arrange
        user_id = "test_user_123"
        conversation_id = "conv_123"

        # Mock conversation exists
        mock_conversation = Conversation(
            id=conversation_id,
            user_id=user_id,
            title="Test Conv",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        exec_result_conv = Mock()
        exec_result_conv.first = Mock(return_value=mock_conversation)
        self.mock_session.exec = Mock(side_effect=[exec_result_conv])  # First call for conversation check

        message_data = MessageCreate(
            conversation_id=conversation_id,
            user_id=user_id,
            role="user",
            content="Test message content"
        )

        mock_message = Message(
            id="msg_123",
            conversation_id=conversation_id,
            user_id=user_id,
            role="user",
            content="Test message content",
            timestamp=datetime.utcnow()
        )

        self.mock_session.add = Mock()
        self.mock_session.commit = Mock()
        self.mock_session.refresh = Mock(return_value=mock_message)

        # Act
        result = self.conversation_service.add_message_to_conversation(user_id, conversation_id, message_data)

        # Assert
        assert result.user_id == user_id
        assert result.content == "Test message content"
        self.mock_session.add.assert_called_once()
        self.mock_session.commit.assert_called_once()

    def test_get_conversation_messages(self):
        """Test getting messages from a conversation"""
        # Arrange
        user_id = "test_user_123"
        conversation_id = "conv_123"

        # Mock conversation exists
        mock_conversation = Conversation(
            id=conversation_id,
            user_id=user_id,
            title="Test Conv",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        exec_result_conv = Mock()
        exec_result_conv.first = Mock(return_value=mock_conversation)
        exec_result_msgs = Mock()
        exec_result_msgs.all = Mock(return_value=[
            Message(
                id="msg1",
                conversation_id=conversation_id,
                user_id=user_id,
                role="user",
                content="Message 1",
                timestamp=datetime.utcnow()
            ),
            Message(
                id="msg2",
                conversation_id=conversation_id,
                user_id=user_id,
                role="assistant",
                content="Message 2",
                timestamp=datetime.utcnow()
            )
        ])

        self.mock_session.exec = Mock(side_effect=[exec_result_conv, exec_result_msgs])

        # Act
        result = self.conversation_service.get_conversation_messages(conversation_id, user_id)

        # Assert
        assert len(result) == 2
        assert result[0].content == "Message 1"
        assert result[1].content == "Message 2"

    def test_delete_conversation_success(self):
        """Test deleting a conversation successfully"""
        # Arrange
        user_id = "test_user_123"
        conversation_id = "conv_123"

        # Mock conversation exists
        mock_conversation = Conversation(
            id=conversation_id,
            user_id=user_id,
            title="Test Conv",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        exec_result = Mock()
        exec_result.first = Mock(return_value=mock_conversation)
        self.mock_session.exec = Mock(return_value=exec_result)

        self.mock_session.delete = Mock()
        self.mock_session.commit = Mock()

        # Act
        result = self.conversation_service.delete_conversation(conversation_id, user_id)

        # Assert
        assert result is True
        self.mock_session.delete.assert_called_once_with(mock_conversation)
        self.mock_session.commit.assert_called_once()

    def test_delete_conversation_not_found(self):
        """Test deleting a conversation that doesn't exist"""
        # Arrange
        user_id = "test_user_123"
        conversation_id = "nonexistent_conv"

        # Mock conversation doesn't exist
        exec_result = Mock()
        exec_result.first = Mock(return_value=None)
        self.mock_session.exec = Mock(return_value=exec_result)

        # Act
        result = self.conversation_service.delete_conversation(conversation_id, user_id)

        # Assert
        assert result is False