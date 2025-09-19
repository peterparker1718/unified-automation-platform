"""
Common Automation Scripts
Collection of frequently used automation scripts and utilities
"""

import os
import json
import yaml
import subprocess
import shutil
from typing import Dict, List, Any, Optional
from datetime import datetime
import tempfile
import zipfile
import requests


class ProjectAnalyzer:
    """Analyzes project structure and technology stack."""
    
    def __init__(self, project_path: str = "."):
        self.project_path = os.path.abspath(project_path)
    
    def analyze_project(self) -> Dict[str, Any]:
        """Perform comprehensive project analysis."""
        analysis = {
            'project_path': self.project_path,
            'analysis_time': datetime.now().isoformat(),
            'technologies': self._detect_technologies(),
            'structure': self._analyze_structure(),
            'dependencies': self._analyze_dependencies(),
            'metrics': self._calculate_metrics(),
            'recommendations': self._generate_recommendations()
        }
        
        return analysis
    
    def _detect_technologies(self) -> List[str]:
        """Detect technologies used in the project."""
        technologies = []
        
        # Check for various technology indicators
        files_to_check = {
            'package.json': 'nodejs',
            'requirements.txt': 'python',
            'setup.py': 'python',
            'pyproject.toml': 'python',
            'Cargo.toml': 'rust',
            'go.mod': 'go',
            'pom.xml': 'java',
            'build.gradle': 'java',
            'Dockerfile': 'docker',
            'docker-compose.yml': 'docker-compose',
            '.github/workflows': 'github-actions',
            'terraform': 'terraform',
            'ansible': 'ansible'
        }
        
        for file_indicator, tech in files_to_check.items():
            if os.path.exists(os.path.join(self.project_path, file_indicator)):
                technologies.append(tech)
        
        # Check for programming languages by file extensions
        language_extensions = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.java': 'java',
            '.go': 'go',
            '.rs': 'rust',
            '.cpp': 'cpp',
            '.c': 'c',
            '.cs': 'csharp',
            '.php': 'php',
            '.rb': 'ruby'
        }
        
        for root, dirs, files in os.walk(self.project_path):
            for file in files:
                ext = os.path.splitext(file)[1]
                if ext in language_extensions:
                    lang = language_extensions[ext]
                    if lang not in technologies:
                        technologies.append(lang)
        
        return technologies
    
    def _analyze_structure(self) -> Dict[str, Any]:
        """Analyze project directory structure."""
        structure = {
            'total_files': 0,
            'total_directories': 0,
            'file_types': {},
            'large_files': [],
            'empty_directories': []
        }
        
        for root, dirs, files in os.walk(self.project_path):
            structure['total_directories'] += len(dirs)
            structure['total_files'] += len(files)
            
            for file in files:
                filepath = os.path.join(root, file)
                ext = os.path.splitext(file)[1] or 'no_extension'
                
                if ext not in structure['file_types']:
                    structure['file_types'][ext] = 0
                structure['file_types'][ext] += 1
                
                # Check for large files (>10MB)
                try:
                    size = os.path.getsize(filepath)
                    if size > 10 * 1024 * 1024:  # 10MB
                        structure['large_files'].append({
                            'path': os.path.relpath(filepath, self.project_path),
                            'size_mb': round(size / (1024 * 1024), 2)
                        })
                except OSError:
                    pass
            
            # Check for empty directories
            if not files and not dirs:
                structure['empty_directories'].append(
                    os.path.relpath(root, self.project_path)
                )
        
        return structure
    
    def _analyze_dependencies(self) -> Dict[str, Any]:
        """Analyze project dependencies."""
        dependencies = {
            'npm': {},
            'python': {},
            'docker': {}
        }
        
        # NPM dependencies
        package_json_path = os.path.join(self.project_path, 'package.json')
        if os.path.exists(package_json_path):
            try:
                with open(package_json_path, 'r') as f:
                    package_data = json.load(f)
                dependencies['npm'] = {
                    'dependencies': package_data.get('dependencies', {}),
                    'dev_dependencies': package_data.get('devDependencies', {}),
                    'total': len(package_data.get('dependencies', {})) + len(package_data.get('devDependencies', {}))
                }
            except (json.JSONDecodeError, IOError):
                pass
        
        # Python dependencies
        requirements_path = os.path.join(self.project_path, 'requirements.txt')
        if os.path.exists(requirements_path):
            try:
                with open(requirements_path, 'r') as f:
                    lines = f.readlines()
                reqs = [line.strip() for line in lines if line.strip() and not line.startswith('#')]
                dependencies['python'] = {
                    'requirements': reqs,
                    'total': len(reqs)
                }
            except IOError:
                pass
        
        # Docker base images
        dockerfile_path = os.path.join(self.project_path, 'Dockerfile')
        if os.path.exists(dockerfile_path):
            try:
                with open(dockerfile_path, 'r') as f:
                    content = f.read()
                
                base_images = []
                for line in content.split('\n'):
                    if line.strip().upper().startswith('FROM '):
                        image = line.strip()[5:].strip()
                        base_images.append(image)
                
                dependencies['docker'] = {
                    'base_images': base_images,
                    'total': len(base_images)
                }
            except IOError:
                pass
        
        return dependencies
    
    def _calculate_metrics(self) -> Dict[str, Any]:
        """Calculate project metrics."""
        metrics = {
            'lines_of_code': 0,
            'code_files': 0,
            'test_files': 0,
            'config_files': 0,
            'documentation_files': 0
        }
        
        code_extensions = {'.py', '.js', '.ts', '.java', '.go', '.rs', '.cpp', '.c', '.cs', '.php', '.rb'}
        test_patterns = {'test_', '_test', '.test.', '.spec.'}
        config_extensions = {'.json', '.yml', '.yaml', '.toml', '.ini', '.cfg', '.conf'}
        doc_extensions = {'.md', '.rst', '.txt', '.doc', '.docx'}
        
        for root, dirs, files in os.walk(self.project_path):
            for file in files:
                filepath = os.path.join(root, file)
                ext = os.path.splitext(file)[1]
                
                if ext in code_extensions:
                    metrics['code_files'] += 1
                    
                    # Check if it's a test file
                    if any(pattern in file.lower() for pattern in test_patterns):
                        metrics['test_files'] += 1
                    
                    # Count lines of code
                    try:
                        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                            lines = f.readlines()
                            metrics['lines_of_code'] += len([line for line in lines if line.strip()])
                    except (IOError, UnicodeDecodeError):
                        pass
                
                elif ext in config_extensions:
                    metrics['config_files'] += 1
                
                elif ext in doc_extensions:
                    metrics['documentation_files'] += 1
        
        return metrics
    
    def _generate_recommendations(self) -> List[str]:
        """Generate improvement recommendations."""
        recommendations = []
        
        # Check for common files
        common_files = {
            'README.md': 'Add a README.md file to document your project',
            '.gitignore': 'Add a .gitignore file to exclude unnecessary files',
            'LICENSE': 'Consider adding a LICENSE file',
            '.github/workflows': 'Consider adding GitHub Actions for CI/CD'
        }
        
        for file, recommendation in common_files.items():
            if not os.path.exists(os.path.join(self.project_path, file)):
                recommendations.append(recommendation)
        
        # Check for security files
        security_files = {
            'SECURITY.md': 'Add a SECURITY.md file to document security policies',
            '.github/dependabot.yml': 'Configure Dependabot for automated dependency updates'
        }
        
        for file, recommendation in security_files.items():
            if not os.path.exists(os.path.join(self.project_path, file)):
                recommendations.append(recommendation)
        
        return recommendations


class EnvironmentManager:
    """Manages development environment setup and configuration."""
    
    @staticmethod
    def setup_python_environment(project_path: str, python_version: str = "3.9") -> Dict[str, Any]:
        """Set up Python virtual environment."""
        venv_path = os.path.join(project_path, 'venv')
        
        try:
            # Create virtual environment
            subprocess.run([
                'python', '-m', 'venv', venv_path
            ], check=True, cwd=project_path)
            
            # Install requirements if they exist
            requirements_path = os.path.join(project_path, 'requirements.txt')
            if os.path.exists(requirements_path):
                pip_path = os.path.join(venv_path, 'bin', 'pip')
                if os.name == 'nt':  # Windows
                    pip_path = os.path.join(venv_path, 'Scripts', 'pip.exe')
                
                subprocess.run([
                    pip_path, 'install', '-r', requirements_path
                ], check=True)
            
            return {
                'status': 'success',
                'venv_path': venv_path,
                'python_version': python_version
            }
            
        except subprocess.CalledProcessError as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    @staticmethod
    def setup_node_environment(project_path: str) -> Dict[str, Any]:
        """Set up Node.js environment."""
        try:
            # Install dependencies
            subprocess.run([
                'npm', 'install'
            ], check=True, cwd=project_path)
            
            return {
                'status': 'success',
                'package_manager': 'npm'
            }
            
        except subprocess.CalledProcessError as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    @staticmethod
    def setup_docker_environment(project_path: str) -> Dict[str, Any]:
        """Set up Docker environment."""
        dockerfile_path = os.path.join(project_path, 'Dockerfile')
        
        if not os.path.exists(dockerfile_path):
            return {
                'status': 'error',
                'error': 'No Dockerfile found'
            }
        
        try:
            # Build Docker image
            subprocess.run([
                'docker', 'build', '-t', f'{os.path.basename(project_path)}:latest', '.'
            ], check=True, cwd=project_path)
            
            return {
                'status': 'success',
                'image_name': f'{os.path.basename(project_path)}:latest'
            }
            
        except subprocess.CalledProcessError as e:
            return {
                'status': 'error',
                'error': str(e)
            }


class BackupManager:
    """Manages project backups and restoration."""
    
    @staticmethod
    def create_backup(project_path: str, backup_dir: str = None) -> Dict[str, Any]:
        """Create a backup of the project."""
        if backup_dir is None:
            backup_dir = os.path.join(os.path.dirname(project_path), 'backups')
        
        os.makedirs(backup_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        project_name = os.path.basename(project_path)
        backup_name = f"{project_name}_{timestamp}.zip"
        backup_path = os.path.join(backup_dir, backup_name)
        
        try:
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(project_path):
                    # Skip common directories that shouldn't be backed up
                    dirs[:] = [d for d in dirs if d not in {'.git', 'node_modules', '__pycache__', '.venv', 'venv'}]
                    
                    for file in files:
                        file_path = os.path.join(root, file)
                        arc_path = os.path.relpath(file_path, project_path)
                        zipf.write(file_path, arc_path)
            
            return {
                'status': 'success',
                'backup_path': backup_path,
                'backup_size_mb': round(os.path.getsize(backup_path) / (1024 * 1024), 2)
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    @staticmethod
    def restore_backup(backup_path: str, restore_dir: str) -> Dict[str, Any]:
        """Restore a project from backup."""
        try:
            os.makedirs(restore_dir, exist_ok=True)
            
            with zipfile.ZipFile(backup_path, 'r') as zipf:
                zipf.extractall(restore_dir)
            
            return {
                'status': 'success',
                'restore_path': restore_dir
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }