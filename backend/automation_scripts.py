"""Automation workflow management system."""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
import uuid

from .openai_integration import openai_client
from .config import settings

logger = logging.getLogger(__name__)


class WorkflowStatus(Enum):
    """Workflow execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AutomationTask:
    """Represents an individual automation task."""
    
    def __init__(
        self, 
        task_id: str,
        name: str,
        description: str,
        task_type: str,
        parameters: Dict[str, Any]
    ):
        self.task_id = task_id
        self.name = name
        self.description = description
        self.task_type = task_type
        self.parameters = parameters
        self.status = WorkflowStatus.PENDING
        self.created_at = datetime.utcnow()
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self.result: Optional[Dict[str, Any]] = None
        self.error: Optional[str] = None


class WorkflowEngine:
    """Main workflow execution engine."""
    
    def __init__(self):
        self.tasks: Dict[str, AutomationTask] = {}
        self.running_tasks: Dict[str, asyncio.Task] = {}
        self.task_handlers: Dict[str, Callable] = {
            "code_generation": self._handle_code_generation,
            "code_review": self._handle_code_review,
            "github_automation": self._handle_github_automation,
            "dependency_audit": self._handle_dependency_audit,
        }
    
    async def create_task(
        self,
        name: str,
        description: str,
        task_type: str,
        parameters: Dict[str, Any]
    ) -> str:
        """Create a new automation task.
        
        Args:
            name: Human-readable task name
            description: Task description
            task_type: Type of automation task
            parameters: Task-specific parameters
            
        Returns:
            Task ID
        """
        task_id = str(uuid.uuid4())
        task = AutomationTask(task_id, name, description, task_type, parameters)
        self.tasks[task_id] = task
        
        logger.info(f"Created task {task_id}: {name}")
        return task_id
    
    async def execute_task(self, task_id: str) -> Dict[str, Any]:
        """Execute an automation task.
        
        Args:
            task_id: Task ID to execute
            
        Returns:
            Task execution result
        """
        if task_id not in self.tasks:
            raise ValueError(f"Task {task_id} not found")
        
        task = self.tasks[task_id]
        
        if task.status != WorkflowStatus.PENDING:
            raise ValueError(f"Task {task_id} is not in pending status")
        
        task.status = WorkflowStatus.RUNNING
        task.started_at = datetime.utcnow()
        
        try:
            # Execute the task based on its type
            handler = self.task_handlers.get(task.task_type)
            if not handler:
                raise ValueError(f"Unknown task type: {task.task_type}")
            
            # Create an asyncio task for execution
            execution_task = asyncio.create_task(handler(task))
            self.running_tasks[task_id] = execution_task
            
            # Wait for completion with timeout
            result = await asyncio.wait_for(
                execution_task,
                timeout=settings.job_timeout_seconds
            )
            
            task.result = result
            task.status = WorkflowStatus.COMPLETED
            task.completed_at = datetime.utcnow()
            
            logger.info(f"Task {task_id} completed successfully")
            return result
            
        except asyncio.TimeoutError:
            task.status = WorkflowStatus.FAILED
            task.error = "Task execution timed out"
            logger.error(f"Task {task_id} timed out")
            raise
        except Exception as e:
            task.status = WorkflowStatus.FAILED
            task.error = str(e)
            logger.error(f"Task {task_id} failed: {e}")
            raise
        finally:
            self.running_tasks.pop(task_id, None)
    
    async def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get task status and details.
        
        Args:
            task_id: Task ID
            
        Returns:
            Task status information
        """
        if task_id not in self.tasks:
            raise ValueError(f"Task {task_id} not found")
        
        task = self.tasks[task_id]
        return {
            "task_id": task.task_id,
            "name": task.name,
            "description": task.description,
            "task_type": task.task_type,
            "status": task.status.value,
            "created_at": task.created_at.isoformat(),
            "started_at": task.started_at.isoformat() if task.started_at else None,
            "completed_at": task.completed_at.isoformat() if task.completed_at else None,
            "result": task.result,
            "error": task.error
        }
    
    async def _handle_code_generation(self, task: AutomationTask) -> Dict[str, Any]:
        """Handle code generation tasks."""
        prompt = task.parameters.get("prompt", "")
        language = task.parameters.get("language", "python")
        
        generated_code = await openai_client.generate_code(prompt, language)
        
        return {
            "generated_code": generated_code,
            "language": language,
            "prompt": prompt
        }
    
    async def _handle_code_review(self, task: AutomationTask) -> Dict[str, Any]:
        """Handle code review tasks."""
        code = task.parameters.get("code", "")
        analysis_type = task.parameters.get("analysis_type", "review")
        
        analysis = await openai_client.analyze_code(code, analysis_type)
        
        return {
            "analysis": analysis,
            "code_length": len(code),
            "analysis_type": analysis_type
        }
    
    async def _handle_github_automation(self, task: AutomationTask) -> Dict[str, Any]:
        """Handle GitHub automation tasks."""
        action_type = task.parameters.get("action_type", "")
        
        # This is a stub implementation
        # In a real scenario, this would interact with GitHub API
        script = await openai_client.generate_automation_script(
            f"GitHub automation: {action_type}",
            platform="github"
        )
        
        return {
            "automation_script": script,
            "action_type": action_type,
            "platform": "github"
        }
    
    async def _handle_dependency_audit(self, task: AutomationTask) -> Dict[str, Any]:
        """Handle dependency audit tasks."""
        audit_type = task.parameters.get("audit_type", "npm")
        project_path = task.parameters.get("project_path", ".")
        
        # This is a stub implementation
        # In a real scenario, this would run actual dependency audits
        return {
            "audit_type": audit_type,
            "project_path": project_path,
            "vulnerabilities_found": 0,
            "recommendations": ["Keep dependencies up to date", "Review security advisories regularly"]
        }


# Global workflow engine instance
workflow_engine = WorkflowEngine()