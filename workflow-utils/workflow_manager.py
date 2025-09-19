"""
Workflow Management Utilities
Provides tools for managing and orchestrating automation workflows
"""

import json
import yaml
import os
import subprocess
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import asyncio


class WorkflowStatus(Enum):
    """Workflow execution status."""
    PENDING = "pending"
    RUNNING = "running" 
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


class TriggerType(Enum):
    """Workflow trigger types."""
    MANUAL = "manual"
    SCHEDULE = "schedule"
    EVENT = "event"
    DEPENDENCY = "dependency"


@dataclass
class WorkflowStep:
    """Represents a single step in a workflow."""
    name: str
    action: str
    parameters: Dict[str, Any]
    timeout: int = 300
    retry_count: int = 0
    continue_on_error: bool = False
    condition: Optional[str] = None


@dataclass
class WorkflowDefinition:
    """Represents a complete workflow definition."""
    name: str
    description: str
    version: str
    trigger_type: TriggerType
    schedule: Optional[str] = None  # Cron expression for scheduled workflows
    dependencies: List[str] = None  # List of dependency workflow names
    environment: Dict[str, str] = None
    steps: List[WorkflowStep] = None
    timeout: int = 3600
    created_at: str = ""
    updated_at: str = ""


@dataclass
class WorkflowExecution:
    """Represents a workflow execution instance."""
    execution_id: str
    workflow_name: str
    status: WorkflowStatus
    started_at: str
    completed_at: Optional[str] = None
    trigger_type: TriggerType = TriggerType.MANUAL
    input_parameters: Dict[str, Any] = None
    current_step: int = 0
    step_results: List[Dict[str, Any]] = None
    error_message: Optional[str] = None
    logs: List[str] = None


class WorkflowManager:
    """Manages workflow definitions and executions."""
    
    def __init__(self, workflows_dir: str = "./workflows"):
        self.workflows_dir = workflows_dir
        self.workflows: Dict[str, WorkflowDefinition] = {}
        self.executions: Dict[str, WorkflowExecution] = {}
        self.step_handlers: Dict[str, Callable] = {
            'shell': self._execute_shell_command,
            'http_request': self._execute_http_request,
            'file_operation': self._execute_file_operation,
            'github_action': self._execute_github_action,
            'security_scan': self._execute_security_scan,
            'notification': self._send_notification,
            'wait': self._wait_step,
            'condition': self._evaluate_condition
        }
        
        # Load existing workflows
        self._load_workflows()
    
    def _load_workflows(self):
        """Load workflow definitions from files."""
        if not os.path.exists(self.workflows_dir):
            os.makedirs(self.workflows_dir)
            return
        
        for filename in os.listdir(self.workflows_dir):
            if filename.endswith('.yml') or filename.endswith('.yaml'):
                try:
                    workflow = self.load_workflow_from_file(
                        os.path.join(self.workflows_dir, filename)
                    )
                    self.workflows[workflow.name] = workflow
                except Exception as e:
                    print(f"Error loading workflow {filename}: {e}")
    
    def load_workflow_from_file(self, filepath: str) -> WorkflowDefinition:
        """Load a workflow definition from a YAML file."""
        with open(filepath, 'r') as f:
            data = yaml.safe_load(f)
        
        # Convert steps
        steps = []
        for step_data in data.get('steps', []):
            step = WorkflowStep(**step_data)
            steps.append(step)
        
        # Create workflow definition
        workflow = WorkflowDefinition(
            name=data['name'],
            description=data.get('description', ''),
            version=data.get('version', '1.0.0'),
            trigger_type=TriggerType(data.get('trigger_type', 'manual')),
            schedule=data.get('schedule'),
            dependencies=data.get('dependencies', []),
            environment=data.get('environment', {}),
            steps=steps,
            timeout=data.get('timeout', 3600),
            created_at=data.get('created_at', datetime.now().isoformat()),
            updated_at=data.get('updated_at', datetime.now().isoformat())
        )
        
        return workflow
    
    def save_workflow_to_file(self, workflow: WorkflowDefinition, filepath: str):
        """Save a workflow definition to a YAML file."""
        data = asdict(workflow)
        
        # Convert enums back to strings
        data['trigger_type'] = workflow.trigger_type.value
        
        with open(filepath, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, indent=2)
    
    def create_workflow(self, workflow_def: Dict[str, Any]) -> WorkflowDefinition:
        """Create a new workflow from definition."""
        # Convert steps
        steps = []
        for step_data in workflow_def.get('steps', []):
            step = WorkflowStep(**step_data)
            steps.append(step)
        
        workflow = WorkflowDefinition(
            name=workflow_def['name'],
            description=workflow_def.get('description', ''),
            version=workflow_def.get('version', '1.0.0'),
            trigger_type=TriggerType(workflow_def.get('trigger_type', 'manual')),
            schedule=workflow_def.get('schedule'),
            dependencies=workflow_def.get('dependencies', []),
            environment=workflow_def.get('environment', {}),
            steps=steps,
            timeout=workflow_def.get('timeout', 3600),
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )
        
        # Save workflow
        self.workflows[workflow.name] = workflow
        workflow_file = os.path.join(self.workflows_dir, f"{workflow.name}.yml")
        self.save_workflow_to_file(workflow, workflow_file)
        
        return workflow
    
    async def execute_workflow(
        self, 
        workflow_name: str, 
        execution_id: str,
        input_parameters: Dict[str, Any] = None
    ) -> WorkflowExecution:
        """Execute a workflow."""
        if workflow_name not in self.workflows:
            raise ValueError(f"Workflow '{workflow_name}' not found")
        
        workflow = self.workflows[workflow_name]
        
        # Create execution instance
        execution = WorkflowExecution(
            execution_id=execution_id,
            workflow_name=workflow_name,
            status=WorkflowStatus.RUNNING,
            started_at=datetime.now().isoformat(),
            input_parameters=input_parameters or {},
            step_results=[],
            logs=[]
        )
        
        self.executions[execution_id] = execution
        
        try:
            # Set environment variables
            env = os.environ.copy()
            if workflow.environment:
                env.update(workflow.environment)
            
            # Execute steps
            for i, step in enumerate(workflow.steps):
                execution.current_step = i
                execution.logs.append(f"Starting step {i + 1}: {step.name}")
                
                try:
                    # Check step condition
                    if step.condition and not self._evaluate_step_condition(step.condition, execution):
                        execution.logs.append(f"Step {i + 1} skipped due to condition")
                        continue
                    
                    # Execute step with timeout
                    result = await asyncio.wait_for(
                        self._execute_step(step, execution, env),
                        timeout=step.timeout
                    )
                    
                    execution.step_results.append({
                        'step': i,
                        'name': step.name,
                        'status': 'completed',
                        'result': result
                    })
                    
                    execution.logs.append(f"Step {i + 1} completed successfully")
                    
                except asyncio.TimeoutError:
                    error_msg = f"Step {i + 1} timed out after {step.timeout} seconds"
                    execution.logs.append(error_msg)
                    
                    if not step.continue_on_error:
                        execution.status = WorkflowStatus.FAILED
                        execution.error_message = error_msg
                        break
                
                except Exception as e:
                    error_msg = f"Step {i + 1} failed: {str(e)}"
                    execution.logs.append(error_msg)
                    
                    execution.step_results.append({
                        'step': i,
                        'name': step.name,
                        'status': 'failed',
                        'error': str(e)
                    })
                    
                    if not step.continue_on_error:
                        execution.status = WorkflowStatus.FAILED
                        execution.error_message = error_msg
                        break
            
            # Mark as completed if no failures
            if execution.status == WorkflowStatus.RUNNING:
                execution.status = WorkflowStatus.COMPLETED
            
        except Exception as e:
            execution.status = WorkflowStatus.FAILED
            execution.error_message = str(e)
            execution.logs.append(f"Workflow failed: {str(e)}")
        
        finally:
            execution.completed_at = datetime.now().isoformat()
        
        return execution
    
    async def _execute_step(
        self, 
        step: WorkflowStep, 
        execution: WorkflowExecution, 
        env: Dict[str, str]
    ) -> Any:
        """Execute a single workflow step."""
        handler = self.step_handlers.get(step.action)
        if not handler:
            raise ValueError(f"Unknown step action: {step.action}")
        
        return await handler(step, execution, env)
    
    def _evaluate_step_condition(self, condition: str, execution: WorkflowExecution) -> bool:
        """Evaluate a step condition."""
        # Simple condition evaluation (can be extended)
        # Example conditions: "previous_step_success", "input.param == 'value'"
        
        if condition == "previous_step_success":
            if not execution.step_results:
                return True
            last_result = execution.step_results[-1]
            return last_result.get('status') == 'completed'
        
        # Add more condition logic as needed
        return True
    
    # Step handler implementations
    async def _execute_shell_command(self, step: WorkflowStep, execution: WorkflowExecution, env: Dict[str, str]) -> Dict[str, Any]:
        """Execute a shell command."""
        command = step.parameters.get('command', '')
        working_dir = step.parameters.get('working_dir', '.')
        
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=working_dir,
            env=env
        )
        
        stdout, stderr = await process.communicate()
        
        return {
            'command': command,
            'return_code': process.returncode,
            'stdout': stdout.decode('utf-8'),
            'stderr': stderr.decode('utf-8')
        }
    
    async def _execute_http_request(self, step: WorkflowStep, execution: WorkflowExecution, env: Dict[str, str]) -> Dict[str, Any]:
        """Execute an HTTP request."""
        import aiohttp
        
        url = step.parameters.get('url', '')
        method = step.parameters.get('method', 'GET').upper()
        headers = step.parameters.get('headers', {})
        data = step.parameters.get('data')
        
        async with aiohttp.ClientSession() as session:
            async with session.request(method, url, headers=headers, json=data) as response:
                response_text = await response.text()
                
                return {
                    'url': url,
                    'method': method,
                    'status_code': response.status,
                    'response': response_text,
                    'headers': dict(response.headers)
                }
    
    async def _execute_file_operation(self, step: WorkflowStep, execution: WorkflowExecution, env: Dict[str, str]) -> Dict[str, Any]:
        """Execute a file operation."""
        operation = step.parameters.get('operation', 'read')
        filepath = step.parameters.get('filepath', '')
        
        if operation == 'read':
            with open(filepath, 'r') as f:
                content = f.read()
            return {'operation': 'read', 'filepath': filepath, 'content': content}
        
        elif operation == 'write':
            content = step.parameters.get('content', '')
            with open(filepath, 'w') as f:
                f.write(content)
            return {'operation': 'write', 'filepath': filepath, 'bytes_written': len(content)}
        
        elif operation == 'delete':
            os.remove(filepath)
            return {'operation': 'delete', 'filepath': filepath}
        
        else:
            raise ValueError(f"Unknown file operation: {operation}")
    
    async def _execute_github_action(self, step: WorkflowStep, execution: WorkflowExecution, env: Dict[str, str]) -> Dict[str, Any]:
        """Execute a GitHub action."""
        # This would integrate with the GitHub helpers
        action = step.parameters.get('action', '')
        return {'action': action, 'status': 'not_implemented'}
    
    async def _execute_security_scan(self, step: WorkflowStep, execution: WorkflowExecution, env: Dict[str, str]) -> Dict[str, Any]:
        """Execute a security scan."""
        scan_type = step.parameters.get('scan_type', 'unified')
        project_path = step.parameters.get('project_path', '.')
        
        # This would integrate with the dependency audit tools
        return {'scan_type': scan_type, 'project_path': project_path, 'status': 'not_implemented'}
    
    async def _send_notification(self, step: WorkflowStep, execution: WorkflowExecution, env: Dict[str, str]) -> Dict[str, Any]:
        """Send a notification."""
        channel = step.parameters.get('channel', 'email')
        message = step.parameters.get('message', '')
        
        # Implementation would depend on notification channel
        return {'channel': channel, 'message': message, 'status': 'sent'}
    
    async def _wait_step(self, step: WorkflowStep, execution: WorkflowExecution, env: Dict[str, str]) -> Dict[str, Any]:
        """Wait for a specified amount of time."""
        duration = step.parameters.get('duration', 1)
        await asyncio.sleep(duration)
        return {'waited_seconds': duration}
    
    async def _evaluate_condition(self, step: WorkflowStep, execution: WorkflowExecution, env: Dict[str, str]) -> Dict[str, Any]:
        """Evaluate a condition and return the result."""
        condition = step.parameters.get('condition', 'true')
        # Simple condition evaluation - can be extended
        result = condition.lower() == 'true'
        return {'condition': condition, 'result': result}