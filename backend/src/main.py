from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.auth import router as auth_router
from .api.tasks import router as tasks_router
from .api.chat import router as chat_router
from .api.mcp_tools import router as mcp_tools_router
from .api.conversations import router as conversations_router
from .config.settings import settings
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Create FastAPI app instance
app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include authentication routes
app.include_router(auth_router)

# Include tasks routes (will be protected by authentication)
app.include_router(tasks_router, prefix="/api")

# Include chat routes (will be protected by authentication)
app.include_router(chat_router, prefix="/api")

# Include MCP tools routes (will be protected by authentication)
app.include_router(mcp_tools_router, prefix="/api")

# Include conversations routes (will be protected by authentication)
app.include_router(conversations_router, prefix="/api")

@app.get("/")
async def root():
    """
    Root endpoint for health check
    """
    return {"message": "Todo API is running"}

@app.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {"status": "healthy", "app": settings.APP_NAME}


@app.get("/auth-health")
async def auth_health_check():
    """
    Authentication-specific health check endpoint
    """
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "features": {
            "jwt": "enabled",
            "authentication": "ready",
            "multi_tenant": "enforced",
            "rate_limiting": "active"
        }
    }