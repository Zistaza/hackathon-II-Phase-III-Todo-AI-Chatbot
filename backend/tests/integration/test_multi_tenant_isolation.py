import pytest
from sqlmodel import Session, create_engine, SQLModel
from sqlmodel.pool import StaticPool
from backend.src.database import init_db
from backend.src.models.conversation_model import Conversation
from backend.src.models.message_model import Message
from backend.src.models.user_model import User
from backend.src.services.conversation_service import ConversationService
from backend.src.models.conversation_model import ConversationCreate
from backend.src.models.message_model import MessageCreate


@pytest.fixture
def session():
    """Create an in-memory database session for testing."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel = Conversation.__table__.metadata
    SQLModel.bind = engine
    SQLModel.create_all(engine)

    with Session(engine) as session:
        yield session


class TestMultiTenantIsolation:
    """Integration tests for multi-tenant isolation"""

    def test_user_cannot_access_other_users_conversations(self, session):
        """Test that users cannot access each other's conversations"""
        # Arrange: Create two users
        user1_id = "user_123"
        user2_id = "user_456"

        # Create conversations for user 1
        conversation_service = ConversationService(session)

        conv1_data = ConversationCreate(title="User 1's Conversation")
        user1_conv = conversation_service.create_conversation(user1_id, conv1_data)

        # Create conversations for user 2
        conv2_data = ConversationCreate(title="User 2's Conversation")
        user2_conv = conversation_service.create_conversation(user2_id, conv2_data)

        # Act: Try to access user 2's conversation as user 1
        result = conversation_service.get_conversation_by_id(user2_conv.id, user1_id)

        # Assert: User 1 should not be able to access user 2's conversation
        assert result is None

        # Act: Try to access user 1's conversation as user 2
        result2 = conversation_service.get_conversation_by_id(user1_conv.id, user2_id)

        # Assert: User 2 should not be able to access user 1's conversation
        assert result2 is None

        # Verify: Each user can access their own conversation
        user1_own_conv = conversation_service.get_conversation_by_id(user1_conv.id, user1_id)
        user2_own_conv = conversation_service.get_conversation_by_id(user2_conv.id, user2_id)

        assert user1_own_conv is not None
        assert user2_own_conv is not None
        assert user1_own_conv.id == user1_conv.id
        assert user2_own_conv.id == user2_conv.id

    def test_user_cannot_access_other_users_messages(self, session):
        """Test that users cannot access each other's messages in conversations"""
        # Arrange: Create two users and a shared conversation
        user1_id = "user_abc"
        user2_id = "user_def"

        conversation_service = ConversationService(session)

        # Create a conversation for user 1
        conv_data = ConversationCreate(title="Shared Conversation?")
        conversation = conversation_service.create_conversation(user1_id, conv_data)

        # Add a message from user 1 to the conversation
        msg_data = MessageCreate(
            conversation_id=conversation.id,
            user_id=user1_id,
            role="user",
            content="User 1's private message"
        )
        conversation_service.add_message_to_conversation(user1_id, conversation.id, msg_data)

        # Act: Try to get messages from user 1's conversation as user 2
        # This should raise a ValueError since user 2 doesn't own the conversation
        from backend.src.services.conversation_service import ConversationService
        try:
            conversation_service.get_conversation_messages(conversation.id, user2_id)
            # If we reach here, the test should fail
            assert False, "Expected ValueError was not raised"
        except ValueError:
            # This is expected behavior
            pass

    def test_user_can_only_see_their_own_conversations(self, session):
        """Test that users can only see their own conversations"""
        # Arrange: Create two users with conversations
        user1_id = "user_xyz"
        user2_id = "user_abc"

        conversation_service = ConversationService(session)

        # Create conversations for user 1
        conv1_data = ConversationCreate(title="User 1's First Conversation")
        conversation_service.create_conversation(user1_id, conv1_data)

        conv2_data = ConversationCreate(title="User 1's Second Conversation")
        conversation_service.create_conversation(user1_id, conv2_data)

        # Create conversations for user 2
        conv3_data = ConversationCreate(title="User 2's First Conversation")
        conversation_service.create_conversation(user2_id, conv3_data)

        conv4_data = ConversationCreate(title="User 2's Second Conversation")
        conversation_service.create_conversation(user2_id, conv4_data)

        # Act: Get conversations for each user
        user1_conversations = conversation_service.get_user_conversations(user1_id)
        user2_conversations = conversation_service.get_user_conversations(user2_id)

        # Assert: Each user should only see their own conversations
        assert len(user1_conversations) == 2
        assert len(user2_conversations) == 2

        for conv in user1_conversations:
            assert conv.user_id == user1_id

        for conv in user2_conversations:
            assert conv.user_id == user2_id