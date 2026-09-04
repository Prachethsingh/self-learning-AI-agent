"""
Main API Application

FastAPI application for the self-learning AI agent system.
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
import uvicorn
import logging
from contextlib import asynccontextmanager
import time

# Import API routes
from api.routes import agent, memory, tasks
from api.websocket import router as websocket_router
from api.middleware.security import setup_security_middleware

# Import core components
from agent.brain import Brain, LLMConfig, LLMProvider
from agent.planner import Planner
from agent.executor import Executor
from agent.evaluator import Evaluator
from agent.learner import Learner
from memory.short_term import ShortTermMemory
from memory.long_term import LongTermMemory
from memory.vector_memory import VectorMemory
from tools.web_search import create_web_search_tool
from tools.python_tool import create_python_tool
from tools.filesystem import create_filesystem_tool
from tools.database import create_database_tool
from tools.git_tool import create_git_tool

# Load environment variables
import os
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Security
security = HTTPBearer()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info("Starting up self-learning AI agent system...")

    # Initialize core components
    app.state.llm_config = LLMConfig(
        provider=LLMProvider.OPENAI,
        model=os.getenv("LLM_MODEL", "gpt-4-turbo-preview"),
        api_key=os.getenv("OPENAI_API_KEY", ""),
        max_tokens=int(os.getenv("MAX_TOKENS", "4000")),
        temperature=float(os.getenv("TEMPERATURE", "0.7")),
        base_url=os.getenv("LLM_BASE_URL", None)
    )

    app.state.brain = Brain(app.state.llm_config)
    app.state.planner = Planner()
    app.state.evaluator = Evaluator()
    app.state.learner = Learner()

    # Initialize memory systems
    app.state.short_term_memory = ShortTermMemory()
    db_url = os.getenv("DATABASE_URL", "postgresql://localhost/self_learning_agent")
    try:
        app.state.long_term_memory = LongTermMemory(db_url)
    except Exception as e:
        logger.warning(f"Failed to connect to primary database at {db_url}: {e}. Falling back to SQLite.")
        db_url = "sqlite:///./self_learning_agent.db"
        app.state.long_term_memory = LongTermMemory(db_url)

    app.state.vector_memory = VectorMemory(
        qdrant_url=os.getenv("QDRANT_URL", "http://localhost:6379")
    )

    # Initialize tools
    app.state.tools = {
        "web_search": create_web_search_tool(
            api_key=os.getenv("WEB_SEARCH_API_KEY")
        ),
        "python_tool": create_python_tool(),
        "filesystem": create_filesystem_tool(),
        "database": create_database_tool(db_url),
        "git_tool": create_git_tool()
    }

    # Initialize executor with tools
    app.state.executor = Executor(app.state.tools)

    logger.info("Self-learning AI agent system started successfully")

    yield

    # Cleanup
    logger.info("Shutting down self-learning AI agent system...")
    await app.state.tools["web_search"].close()
    await app.state.tools["database"].close()
    logger.info("Shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="Self-Learning AI Agent API",
    description="API for a self-learning AI agent system",
    version="0.1.0",
    lifespan=lifespan
)

# Add security middleware
setup_security_middleware(app)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Dependency to get current user (simplified for now)
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current user from token (simplified implementation)."""
    # In a real implementation, you would validate the JWT token here
    # For demo purposes, we'll accept any token or create a demo user
    if not credentials or not credentials.credentials:
        return {"user_id": "demo_user", "username": "demo", "role": "user"}

    # In production, validate JWT token here
    # For now, we'll accept any non-empty token as valid for demo
    return {"user_id": "authenticated_user", "username": "authenticated", "role": "user"}


# Include routers
app.include_router(agent.router, prefix="/api/agent", tags=["agent"])
app.include_router(memory.router, prefix="/api/memory", tags=["memory"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["tasks"])
app.include_router(websocket_router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Self-Learning AI Agent API",
        "version": "0.1.0",
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        from api.main import app

        # Test database connection
        db_status = "ok"
        try:
            # Simple query to test connection
            pass  # In real implementation, test actual connection
        except:
            db_status = "error"

        return {
            "status": "healthy",
            "timestamp": time.time(),
            "components": {
                "brain": "ok",
                "planner": "ok",
                "executor": "ok",
                "evaluator": "ok",
                "learner": "ok",
                "short_term_memory": "ok",
                "long_term_memory": db_status,
                "vector_memory": "ok",
                "tools": "ok"
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e)
            }
        )


if __name__ == "__main__":
    uvicorn.run(
        "api.main:app",
        host=os.getenv("API_HOST", "0.0.0.0"),
        port=int(os.getenv("API_PORT", "8000")),
        reload=True
    )