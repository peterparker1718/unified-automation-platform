"""FastAPI server for the automation platform backend."""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import uvicorn
import logging

from .config import settings
from .automation_scripts import workflow_engine
from .openai_integration import openai_client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Unified Automation Platform API",
    description="Backend API for OpenAI integration and automation workflows",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models for request/response
class TaskCreateRequest(BaseModel):
    name: str
    description: str
    task_type: str
    parameters: Dict[str, Any]


class CodeGenerationRequest(BaseModel):
    prompt: str
    language: str = "python"
    max_tokens: Optional[int] = None


class CodeAnalysisRequest(BaseModel):
    code: str
    analysis_type: str = "review"


class AutomationScriptRequest(BaseModel):
    task_description: str
    platform: str = "github"


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "1.0.0"}


# OpenAI endpoints
@app.post("/api/generate-code")
async def generate_code(request: CodeGenerationRequest):
    """Generate code using OpenAI."""
    try:
        generated_code = await openai_client.generate_code(
            request.prompt,
            request.language,
            request.max_tokens
        )
        return {
            "success": True,
            "generated_code": generated_code,
            "language": request.language,
            "prompt": request.prompt
        }
    except Exception as e:
        logger.error(f"Error generating code: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/analyze-code")
async def analyze_code(request: CodeAnalysisRequest):
    """Analyze code using OpenAI."""
    try:
        analysis = await openai_client.analyze_code(request.code, request.analysis_type)
        return {
            "success": True,
            "analysis": analysis,
            "analysis_type": request.analysis_type
        }
    except Exception as e:
        logger.error(f"Error analyzing code: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/generate-automation-script")
async def generate_automation_script(request: AutomationScriptRequest):
    """Generate automation scripts."""
    try:
        script = await openai_client.generate_automation_script(
            request.task_description,
            request.platform
        )
        return {
            "success": True,
            "automation_script": script,
            "platform": request.platform,
            "task_description": request.task_description
        }
    except Exception as e:
        logger.error(f"Error generating automation script: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Workflow management endpoints
@app.post("/api/tasks")
async def create_task(request: TaskCreateRequest):
    """Create a new automation task."""
    try:
        task_id = await workflow_engine.create_task(
            request.name,
            request.description,
            request.task_type,
            request.parameters
        )
        return {
            "success": True,
            "task_id": task_id,
            "message": "Task created successfully"
        }
    except Exception as e:
        logger.error(f"Error creating task: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/tasks/{task_id}/execute")
async def execute_task(task_id: str, background_tasks: BackgroundTasks):
    """Execute an automation task."""
    try:
        # Execute task in background
        background_tasks.add_task(workflow_engine.execute_task, task_id)
        return {
            "success": True,
            "task_id": task_id,
            "message": "Task execution started"
        }
    except Exception as e:
        logger.error(f"Error executing task {task_id}: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/tasks/{task_id}")
async def get_task_status(task_id: str):
    """Get task status and details."""
    try:
        task_info = await workflow_engine.get_task_status(task_id)
        return {
            "success": True,
            "task": task_info
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting task status {task_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/tasks")
async def list_tasks():
    """List all tasks."""
    try:
        tasks = []
        for task_id in workflow_engine.tasks.keys():
            task_info = await workflow_engine.get_task_status(task_id)
            tasks.append(task_info)
        
        return {
            "success": True,
            "tasks": tasks,
            "total": len(tasks)
        }
    except Exception as e:
        logger.error(f"Error listing tasks: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Configuration endpoint
@app.get("/api/config")
async def get_config():
    """Get public configuration information."""
    return {
        "success": True,
        "config": {
            "openai_model": settings.openai_model,
            "max_tokens": settings.openai_max_tokens,
            "max_concurrent_jobs": settings.max_concurrent_jobs,
            "job_timeout_seconds": settings.job_timeout_seconds
        }
    }


if __name__ == "__main__":
    uvicorn.run(
        "server:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )