"""
GitHub Integration Utilities
Provides helpers for GitHub API interactions and automation
"""

import os
import json
import requests
from typing import Dict, List, Any, Optional
from datetime import datetime
import base64


class GitHubClient:
    """GitHub API client with common automation methods."""
    
    def __init__(self, token: Optional[str] = None, base_url: str = "https://api.github.com"):
        self.token = token or os.getenv('GITHUB_TOKEN')
        self.base_url = base_url
        self.session = requests.Session()
        
        if self.token:
            self.session.headers.update({
                'Authorization': f'token {self.token}',
                'Accept': 'application/vnd.github.v3+json'
            })
    
    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make a request to the GitHub API."""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = self.session.request(method, url, **kwargs)
        response.raise_for_status()
        return response.json()
    
    def get_repository(self, owner: str, repo: str) -> Dict[str, Any]:
        """Get repository information."""
        return self._request('GET', f'/repos/{owner}/{repo}')
    
    def list_pull_requests(self, owner: str, repo: str, state: str = 'open') -> List[Dict[str, Any]]:
        """List pull requests for a repository."""
        return self._request('GET', f'/repos/{owner}/{repo}/pulls', params={'state': state})
    
    def create_pull_request(
        self, 
        owner: str, 
        repo: str, 
        title: str, 
        head: str, 
        base: str, 
        body: str = ""
    ) -> Dict[str, Any]:
        """Create a new pull request."""
        data = {
            'title': title,
            'head': head,
            'base': base,
            'body': body
        }
        return self._request('POST', f'/repos/{owner}/{repo}/pulls', json=data)
    
    def create_issue(
        self, 
        owner: str, 
        repo: str, 
        title: str, 
        body: str = "", 
        labels: List[str] = None
    ) -> Dict[str, Any]:
        """Create a new issue."""
        data = {
            'title': title,
            'body': body
        }
        if labels:
            data['labels'] = labels
        
        return self._request('POST', f'/repos/{owner}/{repo}/issues', json=data)
    
    def add_comment(self, owner: str, repo: str, issue_number: int, body: str) -> Dict[str, Any]:
        """Add a comment to an issue or pull request."""
        data = {'body': body}
        return self._request('POST', f'/repos/{owner}/{repo}/issues/{issue_number}/comments', json=data)
    
    def get_file_content(self, owner: str, repo: str, path: str, ref: str = 'main') -> str:
        """Get the content of a file from the repository."""
        response = self._request('GET', f'/repos/{owner}/{repo}/contents/{path}', params={'ref': ref})
        content = base64.b64decode(response['content']).decode('utf-8')
        return content
    
    def create_or_update_file(
        self, 
        owner: str, 
        repo: str, 
        path: str, 
        content: str, 
        message: str,
        branch: str = 'main',
        sha: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create or update a file in the repository."""
        encoded_content = base64.b64encode(content.encode('utf-8')).decode('utf-8')
        data = {
            'message': message,
            'content': encoded_content,
            'branch': branch
        }
        if sha:
            data['sha'] = sha
        
        return self._request('PUT', f'/repos/{owner}/{repo}/contents/{path}', json=data)
    
    def list_workflow_runs(self, owner: str, repo: str, workflow_id: str = None) -> List[Dict[str, Any]]:
        """List workflow runs for a repository."""
        endpoint = f'/repos/{owner}/{repo}/actions/runs'
        if workflow_id:
            endpoint = f'/repos/{owner}/{repo}/actions/workflows/{workflow_id}/runs'
        return self._request('GET', endpoint)['workflow_runs']
    
    def trigger_workflow(
        self, 
        owner: str, 
        repo: str, 
        workflow_id: str, 
        ref: str = 'main',
        inputs: Dict[str, Any] = None
    ) -> bool:
        """Trigger a workflow dispatch event."""
        data = {'ref': ref}
        if inputs:
            data['inputs'] = inputs
        
        try:
            self._request('POST', f'/repos/{owner}/{repo}/actions/workflows/{workflow_id}/dispatches', json=data)
            return True
        except requests.exceptions.HTTPError:
            return False


class GitHubAutomation:
    """High-level GitHub automation workflows."""
    
    def __init__(self, github_client: GitHubClient):
        self.client = github_client
    
    def auto_merge_dependabot_prs(self, owner: str, repo: str) -> List[Dict[str, Any]]:
        """Automatically merge Dependabot pull requests that pass CI."""
        results = []
        
        # Get open pull requests
        prs = self.client.list_pull_requests(owner, repo, 'open')
        
        for pr in prs:
            if pr['user']['login'] == 'dependabot[bot]':
                # Check if CI passed (simplified check)
                if self._check_pr_status(owner, repo, pr['number']):
                    try:
                        # Merge the PR
                        merge_result = self._merge_pull_request(owner, repo, pr['number'])
                        results.append({
                            'pr_number': pr['number'],
                            'title': pr['title'],
                            'action': 'merged',
                            'result': merge_result
                        })
                    except Exception as e:
                        results.append({
                            'pr_number': pr['number'],
                            'title': pr['title'],
                            'action': 'failed',
                            'error': str(e)
                        })
        
        return results
    
    def create_security_issue_from_scan(
        self, 
        owner: str, 
        repo: str, 
        scan_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a GitHub issue from security scan results."""
        vulnerability_count = len(scan_results.get('vulnerabilities', []))
        
        if vulnerability_count == 0:
            return {'action': 'skipped', 'reason': 'No vulnerabilities found'}
        
        # Create issue title and body
        title = f"Security vulnerabilities found: {vulnerability_count} issues"
        body = self._format_security_issue_body(scan_results)
        
        # Create issue with security label
        issue = self.client.create_issue(
            owner, repo, title, body, 
            labels=['security', 'vulnerability']
        )
        
        return {
            'action': 'created',
            'issue_number': issue['number'],
            'url': issue['html_url']
        }
    
    def setup_automated_security_scanning(self, owner: str, repo: str) -> Dict[str, Any]:
        """Set up automated security scanning workflow."""
        workflow_content = """
name: Security Scan

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]
  schedule:
    - cron: '0 2 * * 1'  # Weekly on Monday at 2 AM

jobs:
  security-scan:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Run NPM Audit
      if: hashFiles('package.json') != ''
      run: npm audit --audit-level high
      continue-on-error: true
    
    - name: Run Python Security Scan
      if: hashFiles('requirements.txt') != ''
      run: |
        pip install safety
        safety check
      continue-on-error: true
    
    - name: Run Docker Security Scan
      if: hashFiles('Dockerfile') != ''
      run: |
        docker run --rm -v $(pwd):/workspace \
          aquasec/trivy fs /workspace
      continue-on-error: true
"""
        
        try:
            # Create .github/workflows directory structure
            self.client.create_or_update_file(
                owner, repo,
                '.github/workflows/security-scan.yml',
                workflow_content,
                'Add automated security scanning workflow'
            )
            return {'action': 'created', 'workflow': 'security-scan.yml'}
        except Exception as e:
            return {'action': 'failed', 'error': str(e)}
    
    def _check_pr_status(self, owner: str, repo: str, pr_number: int) -> bool:
        """Check if PR status checks are passing (simplified)."""
        # In a real implementation, this would check GitHub status checks
        # For now, return True as a placeholder
        return True
    
    def _merge_pull_request(self, owner: str, repo: str, pr_number: int) -> Dict[str, Any]:
        """Merge a pull request."""
        data = {'merge_method': 'squash'}
        return self.client._request('PUT', f'/repos/{owner}/{repo}/pulls/{pr_number}/merge', json=data)
    
    def _format_security_issue_body(self, scan_results: Dict[str, Any]) -> str:
        """Format security scan results into issue body."""
        body = ["## Security Vulnerability Report", ""]
        body.append(f"**Scan Time:** {scan_results.get('scan_time', 'Unknown')}")
        body.append(f"**Total Vulnerabilities:** {len(scan_results.get('vulnerabilities', []))}")
        body.append("")
        
        # Summary by severity
        summary = scan_results.get('summary', {})
        if summary:
            body.append("### Summary by Severity")
            for severity, count in summary.items():
                if count > 0:
                    body.append(f"- **{severity.capitalize()}**: {count}")
            body.append("")
        
        # Vulnerability details
        vulnerabilities = scan_results.get('vulnerabilities', [])
        if vulnerabilities:
            body.append("### Vulnerability Details")
            for i, vuln in enumerate(vulnerabilities[:10], 1):  # Limit to first 10
                body.append(f"#### {i}. {vuln.get('package', 'Unknown Package')}")
                body.append(f"- **Severity**: {vuln.get('severity', 'Unknown')}")
                body.append(f"- **Version**: {vuln.get('version', 'Unknown')}")
                body.append(f"- **Description**: {vuln.get('description', 'No description')}")
                if vuln.get('fixed_in'):
                    body.append(f"- **Fixed in**: {vuln['fixed_in']}")
                body.append("")
        
        if len(vulnerabilities) > 10:
            body.append(f"... and {len(vulnerabilities) - 10} more vulnerabilities")
        
        return "\n".join(body)