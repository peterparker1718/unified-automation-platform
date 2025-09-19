# Workflow Utilities

This folder contains utilities for managing and orchestrating automation workflows.

## Components

### GitHub Helpers (`github_helpers.py`)
Provides tools for GitHub API interactions and automation workflows.

**Features:**
- GitHub API client with authentication
- Repository operations (create issues, PRs, comments)
- File operations (read, create, update files)
- Workflow automation (trigger workflows, check status)
- Automated Dependabot PR merging
- Security issue creation from scan results
- Automated security scanning setup

**Usage:**
```python
from github_helpers import GitHubClient, GitHubAutomation

# Initialize client
client = GitHubClient(token="your_github_token")

# Create automation instance
automation = GitHubAutomation(client)

# Auto-merge Dependabot PRs
results = automation.auto_merge_dependabot_prs("owner", "repo")

# Create security issue from scan
issue = automation.create_security_issue_from_scan("owner", "repo", scan_results)
```

### Workflow Manager (`workflow_manager.py`)
Comprehensive workflow definition and execution system.

**Features:**
- YAML-based workflow definitions
- Asynchronous workflow execution
- Multiple step types (shell, HTTP, file operations, etc.)
- Conditional execution and error handling
- Workflow scheduling and dependencies
- Execution tracking and logging

**Workflow Definition Example:**
```yaml
name: "security-audit-workflow"
description: "Automated security audit and reporting"
version: "1.0.0"
trigger_type: "schedule"
schedule: "0 2 * * 1"  # Weekly on Monday at 2 AM

steps:
  - name: "Run Security Scan"
    action: "security_scan"
    parameters:
      scan_type: "unified"
      project_path: "."
    timeout: 600

  - name: "Create GitHub Issue"
    action: "github_action"
    parameters:
      action: "create_issue"
      title: "Weekly Security Audit Results"
    condition: "previous_step_success"
```

**Usage:**
```python
from workflow_manager import WorkflowManager

# Initialize manager
manager = WorkflowManager("./workflows")

# Create workflow
workflow_def = {
    "name": "my-workflow",
    "description": "My automation workflow",
    "steps": [
        {
            "name": "Hello World",
            "action": "shell",
            "parameters": {"command": "echo 'Hello World'"}
        }
    ]
}

workflow = manager.create_workflow(workflow_def)

# Execute workflow
execution = await manager.execute_workflow("my-workflow", "exec-123")
```

### Automation Scripts (`automation_scripts.py`)
Collection of common automation utilities and project management tools.

**Features:**
- Project analysis and technology detection
- Environment setup (Python, Node.js, Docker)
- Project metrics calculation
- Backup and restoration utilities
- Improvement recommendations

**Usage:**
```python
from automation_scripts import ProjectAnalyzer, EnvironmentManager, BackupManager

# Analyze project
analyzer = ProjectAnalyzer("/path/to/project")
analysis = analyzer.analyze_project()

# Setup environment
env_result = EnvironmentManager.setup_python_environment("/path/to/project")

# Create backup
backup_result = BackupManager.create_backup("/path/to/project")
```

## Step Types

The workflow manager supports various step types:

### Shell Command
```yaml
- name: "Run Tests"
  action: "shell"
  parameters:
    command: "npm test"
    working_dir: "./frontend"
```

### HTTP Request
```yaml
- name: "API Call"
  action: "http_request"
  parameters:
    url: "https://api.example.com/webhook"
    method: "POST"
    headers:
      Content-Type: "application/json"
    data:
      message: "Workflow completed"
```

### File Operations
```yaml
- name: "Update Config"
  action: "file_operation"
  parameters:
    operation: "write"
    filepath: "./config.json"
    content: '{"version": "1.0.0"}'
```

### GitHub Actions
```yaml
- name: "Create PR"
  action: "github_action"
  parameters:
    action: "create_pull_request"
    title: "Automated updates"
    head: "feature-branch"
    base: "main"
```

### Security Scan
```yaml
- name: "Security Audit"
  action: "security_scan"
  parameters:
    scan_type: "npm"
    project_path: "./frontend"
```

### Notifications
```yaml
- name: "Send Alert"
  action: "notification"
  parameters:
    channel: "slack"
    message: "Deployment completed successfully"
```

## Workflow Triggers

Workflows can be triggered in multiple ways:

### Manual Trigger
```yaml
trigger_type: "manual"
```

### Scheduled Trigger
```yaml
trigger_type: "schedule"
schedule: "0 2 * * 1"  # Cron expression
```

### Event Trigger
```yaml
trigger_type: "event"
# Triggered by external events
```

### Dependency Trigger
```yaml
trigger_type: "dependency"
dependencies: ["workflow1", "workflow2"]
```

## Error Handling

Workflows support comprehensive error handling:

- **Timeouts**: Each step can have a custom timeout
- **Retries**: Steps can be configured to retry on failure
- **Continue on Error**: Steps can be marked to continue even if they fail
- **Conditional Execution**: Steps can be executed based on conditions

## Integration with Backend

These utilities integrate with the backend automation system:

1. **Workflow Execution**: Backend can trigger and monitor workflows
2. **GitHub Integration**: Automated repository operations
3. **Security Integration**: Automated security scanning and reporting
4. **Environment Management**: Automated development environment setup

## Best Practices

1. **Modular Workflows**: Break complex processes into smaller, reusable workflows
2. **Error Handling**: Always include proper error handling and logging
3. **Security**: Never store sensitive data in workflow definitions
4. **Testing**: Test workflows in development before production deployment
5. **Documentation**: Document workflow purposes and parameters clearly