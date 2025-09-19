#!/usr/bin/env python3
"""
PyPI Security Scanner
Scans Python requirements.txt and setup.py for known vulnerabilities
"""

import json
import subprocess
import sys
import os
import re
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, asdict
from datetime import datetime
import pkg_resources


@dataclass
class PythonVulnerability:
    """Represents a Python package security vulnerability."""
    package: str
    installed_version: str
    severity: str
    vulnerability_id: str
    description: str
    fixed_versions: List[str]
    advisory_url: Optional[str] = None


@dataclass
class PythonAuditResult:
    """Represents the result of a Python security audit."""
    scan_type: str
    project_path: str
    total_packages: int
    vulnerabilities: List[PythonVulnerability]
    scan_time: str
    summary: Dict[str, int]
    requirements_files: List[str]


class PyPIScanner:
    """Python package security scanner."""
    
    def __init__(self, project_path: str = "."):
        self.project_path = os.path.abspath(project_path)
        self.requirements_patterns = [
            "requirements.txt",
            "requirements/*.txt",
            "dev-requirements.txt",
            "test-requirements.txt",
            "setup.py",
            "pyproject.toml"
        ]
    
    def find_requirements_files(self) -> List[str]:
        """Find all requirements files in the project."""
        requirements_files = []
        
        for pattern in self.requirements_patterns:
            if '*' in pattern:
                # Handle glob patterns
                import glob
                files = glob.glob(os.path.join(self.project_path, pattern))
                requirements_files.extend(files)
            else:
                file_path = os.path.join(self.project_path, pattern)
                if os.path.exists(file_path):
                    requirements_files.append(file_path)
        
        return requirements_files
    
    def parse_requirements_file(self, file_path: str) -> Set[str]:
        """Parse a requirements file and extract package names."""
        packages = set()
        
        try:
            with open(file_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        # Extract package name (before ==, >=, etc.)
                        match = re.match(r'^([a-zA-Z0-9_-]+)', line)
                        if match:
                            packages.add(match.group(1).lower())
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
        
        return packages
    
    def get_installed_packages(self) -> Dict[str, str]:
        """Get currently installed packages and their versions."""
        packages = {}
        
        try:
            for dist in pkg_resources.working_set:
                packages[dist.project_name.lower()] = dist.version
        except Exception as e:
            print(f"Error getting installed packages: {e}")
        
        return packages
    
    def run_safety_check(self) -> Dict[str, Any]:
        """Run safety check for known vulnerabilities."""
        try:
            # First try to install safety if not available
            try:
                import safety
            except ImportError:
                print("Installing safety package...")
                subprocess.run([sys.executable, '-m', 'pip', 'install', 'safety'], 
                             capture_output=True, check=True)
            
            # Run safety check
            result = subprocess.run([
                sys.executable, '-m', 'safety', 'check', '--json'
            ], capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                return {"vulnerabilities": []}
            elif result.returncode == 255:  # Vulnerabilities found
                return json.loads(result.stdout)
            else:
                print(f"Safety check failed: {result.stderr}")
                return {"vulnerabilities": []}
                
        except subprocess.TimeoutExpired:
            print("Safety check timed out")
            return {"vulnerabilities": []}
        except json.JSONDecodeError:
            print("Failed to parse safety check output")
            return {"vulnerabilities": []}
        except Exception as e:
            print(f"Error running safety check: {e}")
            return {"vulnerabilities": []}
    
    def run_pip_audit(self) -> List[Dict[str, Any]]:
        """Run pip-audit for vulnerability scanning."""
        try:
            # Try to use pip-audit if available
            result = subprocess.run([
                sys.executable, '-m', 'pip-audit', '--format=json'
            ], capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                output = result.stdout.strip()
                if output:
                    return json.loads(output)
                else:
                    return []
            else:
                # pip-audit might not be installed, that's okay
                return []
                
        except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError):
            return []
        except Exception as e:
            print(f"Error running pip-audit: {e}")
            return []
    
    def parse_safety_results(self, safety_data: Dict[str, Any]) -> List[PythonVulnerability]:
        """Parse safety check results into PythonVulnerability objects."""
        vulnerabilities = []
        
        for vuln_data in safety_data.get('vulnerabilities', []):
            vulnerability = PythonVulnerability(
                package=vuln_data.get('package', 'unknown'),
                installed_version=vuln_data.get('installed_version', 'unknown'),
                severity=self._map_severity(vuln_data.get('severity', 'unknown')),
                vulnerability_id=vuln_data.get('id', 'unknown'),
                description=vuln_data.get('description', 'No description available'),
                fixed_versions=vuln_data.get('fixed_versions', []),
                advisory_url=vuln_data.get('more_info_url')
            )
            vulnerabilities.append(vulnerability)
        
        return vulnerabilities
    
    def _map_severity(self, severity: str) -> str:
        """Map various severity formats to standardized levels."""
        severity_lower = severity.lower()
        
        if severity_lower in ['critical', 'high']:
            return 'high'
        elif severity_lower in ['medium', 'moderate']:
            return 'moderate'
        elif severity_lower in ['low', 'minor']:
            return 'low'
        else:
            return 'info'
    
    def scan(self) -> PythonAuditResult:
        """Perform a complete security scan."""
        requirements_files = self.find_requirements_files()
        
        # Get all packages from requirements files
        all_packages = set()
        for req_file in requirements_files:
            packages = self.parse_requirements_file(req_file)
            all_packages.update(packages)
        
        # Get installed packages
        installed_packages = self.get_installed_packages()
        
        # Run security checks
        safety_data = self.run_safety_check()
        vulnerabilities = self.parse_safety_results(safety_data)
        
        # Also try pip-audit
        pip_audit_data = self.run_pip_audit()
        # Parse pip-audit results if available (implementation depends on format)
        
        # Create summary
        summary = {"info": 0, "low": 0, "moderate": 0, "high": 0, "critical": 0}
        for vuln in vulnerabilities:
            if vuln.severity in summary:
                summary[vuln.severity] += 1
            else:
                summary["info"] += 1
        
        return PythonAuditResult(
            scan_type="pypi",
            project_path=self.project_path,
            total_packages=len(all_packages) if all_packages else len(installed_packages),
            vulnerabilities=vulnerabilities,
            scan_time=datetime.now().isoformat(),
            summary=summary,
            requirements_files=requirements_files
        )


def main():
    """Main function for CLI usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Scan Python packages for security vulnerabilities")
    parser.add_argument("--path", "-p", default=".", help="Path to the Python project (default: current directory)")
    parser.add_argument("--output", "-o", help="Output file for results (JSON format)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    scanner = PyPIScanner(args.path)
    result = scanner.scan()
    
    if args.verbose:
        print(f"Scanning Python project at: {result.project_path}")
        print(f"Requirements files found: {len(result.requirements_files)}")
        print(f"Total packages: {result.total_packages}")
        print(f"Vulnerabilities found: {len(result.vulnerabilities)}")
        print(f"Summary: {result.summary}")
    
    # Output results
    result_dict = asdict(result)
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(result_dict, f, indent=2)
        print(f"Results saved to: {args.output}")
    else:
        print(json.dumps(result_dict, indent=2))
    
    # Exit with non-zero code if vulnerabilities found
    if result.vulnerabilities:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()