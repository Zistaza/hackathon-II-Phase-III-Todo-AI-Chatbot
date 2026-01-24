from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
from sqlmodel import SQLModel, Field
import uuid


class MCPToolType(str, Enum):
    """
    Enumeration of MCP tool types
    """
    CODE_GENERATOR = "code_generator"
    DATA_ANALYZER = "data_analyzer"
    FILE_MANAGER = "file_manager"
    DEPLOYMENT_TOOL = "deployment_tool"
    SECURITY_SCANNER = "security_scanner"
    TEST_RUNNER = "test_runner"


class MCPToolAccessType(str, Enum):
    """
    Enumeration of access levels for MCP tools
    """
    READ_ONLY = "read_only"
    READ_WRITE = "read_write"
    ADMIN = "admin"


class MCPToolResource(BaseModel):
    """
    Model representing a resource that can be accessed by MCP tools

    Fields:
    - resource_id: Unique identifier for the resource
    - resource_type: Type of the resource
    - owner_id: ID of the user who owns the resource
    - permissions: Access permissions for the tool
    """
    resource_id: str
    resource_type: str
    owner_id: str
    permissions: List[MCPToolAccessType]


class MCPToolRequest(BaseModel):
    """
    Model representing an MCP tool access request

    Fields:
    - tool_id: Unique identifier for the MCP tool
    - user_id: ID of the user making the request
    - action: Action the tool wants to perform
    - resources: Resources the tool needs access to
    - parameters: Additional parameters for the tool
    """
    tool_id: str
    user_id: str
    action: str
    resources: List[MCPToolResource]
    parameters: Dict[str, Any]


class MCPToolResponse(BaseModel):
    """
    Model representing an MCP tool response

    Fields:
    - success: Whether the operation was successful
    - message: Result message
    - data: Additional data from the tool
    - timestamp: When the response was generated
    """
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    timestamp: datetime = datetime.now()


class MCPToolMetadata(SQLModel, table=True):
    """
    Database model for storing MCP tool metadata

    Fields:
    - id: Unique identifier for the tool entry
    - tool_id: ID of the MCP tool
    - user_id: ID of the user who owns/created the tool
    - name: Name of the tool
    - description: Description of the tool
    - created_at: When the tool was registered
    - updated_at: When the tool was last updated
    - is_active: Whether the tool is currently active
    """
    __tablename__ = "mcp_tools"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    tool_id: str = Field(nullable=False)
    user_id: str = Field(nullable=False)  # User who registered the tool
    name: str = Field(nullable=False, max_length=255)
    description: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)
    allowed_resources: Optional[str] = Field(default=None)  # JSON string of allowed resources


class MCPToolAccessLog(SQLModel, table=True):
    """
    Database model for logging MCP tool access

    Fields:
    - id: Unique identifier for the log entry
    - tool_id: ID of the MCP tool that was accessed
    - user_id: ID of the user who accessed the tool
    - action: Action that was performed
    - resource_id: ID of the resource that was accessed
    - success: Whether the access was successful
    - timestamp: When the access occurred
    - ip_address: IP address of the requester
    """
    __tablename__ = "mcp_tool_access_logs"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    tool_id: str = Field(nullable=False)
    user_id: str = Field(nullable=False)
    action: str = Field(nullable=False, max_length=100)
    resource_id: Optional[str] = Field(default=None)
    success: bool = Field(default=False)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    ip_address: Optional[str] = Field(default=None, max_length=45)  # Support IPv6