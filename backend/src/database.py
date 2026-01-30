from sqlmodel import create_engine, Session
from .config.settings import settings
from typing import Generator

# Export the database URL
DATABASE_URL = settings.DATABASE_URL

# Create the database engine
engine = create_engine(DATABASE_URL, echo=True)


def get_session() -> Generator[Session, None, None]:
    """
    Get a database session for dependency injection
    """
    with Session(engine) as session:
        yield session


def init_db():
    """
    Initialize the database by creating all tables
    """
    from .models.user_model import User  # Import models to register them
    from .models.task_model import Task  # Import Task model to register it
    from .models.conversation_model import Conversation  # Import new model
    from .models.message_model import Message  # Import new model
    from .models.mcp_tool import MCPToolMetadata  # Import existing model
    from sqlmodel import SQLModel

    # Create all tables
    SQLModel.metadata.create_all(engine)