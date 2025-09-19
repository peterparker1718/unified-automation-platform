#!/usr/bin/env python3
"""
Docker Security Scanner
Scans Dockerfiles and Docker images for security vulnerabilities
"""

import json
import subprocess
import sys
import os
import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class DockerVulnerability:
    """Represents a Docker security vulnerability."""
    layer: str
    package: str
    installed_version: str
    severity: str
    vulnerability_id: str
    description: str
    fixed_version: Optional[str] = None


@dataclass
class DockerAuditResult:
    """Represents the result of a Docker security audit."""
    scan_type: str
    project_path: str
    dockerfile_path: str
    image_name: Optional[str]
    vulnerabilities: List[DockerVulnerability]
    scan_time: str
    summary: Dict[str, int]
    dockerfile_issues: List[str]


class DockerScanner:
    """Docker security scanner."""
    
    def __init__(self, project_path: str = "."):
        self.project_path = os.path.abspath(project_path)
        self.dockerfile_patterns = ["Dockerfile", "Dockerfile.*", "*.dockerfile"]
    
    def find_dockerfiles(self) -> List[str]:
        """Find all Dockerfiles in the project."""
        dockerfiles = []
        
        for root, dirs, files in os.walk(self.project_path):
            for file in files:
                if (file == "Dockerfile" or 
                    file.startswith("Dockerfile.") or 
                    file.endswith(".dockerfile")):
                    dockerfiles.append(os.path.join(root, file))
        
        return dockerfiles
    
    def analyze_dockerfile(self, dockerfile_path: str) -> List[str]:
        """Analyze Dockerfile for security issues."""
        issues = []
        
        try:
            with open(dockerfile_path, 'r') as f:
                lines = f.readlines()
            
            for i, line in enumerate(lines, 1):
                line = line.strip()
                
                # Check for common security issues
                if line.upper().startswith('USER '):
                    if 'root' in line.lower():
                        issues.append(f"Line {i}: Running as root user is not recommended")
                
                elif line.upper().startswith('RUN '):
                    if 'curl' in line and '|' in line and 'sh' in line:
                        issues.append(f"Line {i}: Piping curl to shell is dangerous")
                    if 'wget' in line and '|' in line and 'sh' in line:
                        issues.append(f"Line {i}: Piping wget to shell is dangerous")
                    if '--no-check-certificate' in line:
                        issues.append(f"Line {i}: Disabling certificate checks is insecure")
                
                elif line.upper().startswith('COPY ') or line.upper().startswith('ADD '):
                    if line.endswith(' /'):
                        issues.append(f"Line {i}: Copying to filesystem root can be problematic")
                
                elif line.upper().startswith('EXPOSE '):
                    ports = re.findall(r'\d+', line)
                    for port in ports:
                        if port in ['22', '23', '135', '445', '3389']:
                            issues.append(f"Line {i}: Exposing port {port} may be risky")
        
        except Exception as e:
            issues.append(f"Error analyzing Dockerfile: {e}")
        
        return issues
    
    def run_docker_scan(self, image_name: str) -> Dict[str, Any]:
        """Run docker scan command if available."""
        try:
            # Try to use docker scan (if available)
            result = subprocess.run([
                'docker', 'scan', '--json', image_name
            ], capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                return json.loads(result.stdout)
            else:
                print(f"Docker scan failed: {result.stderr}")
                return {}
                
        except subprocess.TimeoutExpired:
            print("Docker scan timed out")
            return {}
        except json.JSONDecodeError:
            print("Failed to parse docker scan output")
            return {}
        except FileNotFoundError:
            print("Docker command not found or docker scan not available")
            return {}
        except Exception as e:
            print(f"Error running docker scan: {e}")
            return {}
    
    def run_trivy_scan(self, dockerfile_path: str) -> Dict[str, Any]:
        """Run Trivy security scanner if available."""
        try:
            # Try to use Trivy
            result = subprocess.run([
                'trivy', 'fs', '--format', 'json', dockerfile_path
            ], capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                return json.loads(result.stdout)
            else:
                # Trivy might not be installed, that's okay
                return {}
                
        except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError):
            return {}
        except Exception as e:
            print(f"Error running Trivy scan: {e}")
            return {}
    
    def run_hadolint(self, dockerfile_path: str) -> List[str]:
        """Run Hadolint for Dockerfile best practices."""
        issues = []
        
        try:
            result = subprocess.run([
                'hadolint', '--format', 'json', dockerfile_path
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0 and result.stdout:
                hadolint_results = json.loads(result.stdout)
                for issue in hadolint_results:
                    message = f"Line {issue.get('line', '?')}: {issue.get('message', 'Unknown issue')}"
                    issues.append(message)
                    
        except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError):
            # Hadolint not available, skip
            pass
        except Exception as e:
            print(f"Error running Hadolint: {e}")
        
        return issues
    
    def parse_scan_results(self, scan_data: Dict[str, Any]) -> List[DockerVulnerability]:
        """Parse security scan results into DockerVulnerability objects."""
        vulnerabilities = []
        
        # This is a simplified parser - real implementation would depend on
        # the specific scanner output format (Docker scan, Trivy, etc.)
        
        if 'vulnerabilities' in scan_data:
            for vuln_data in scan_data['vulnerabilities']:
                vulnerability = DockerVulnerability(
                    layer=vuln_data.get('layer', 'unknown'),
                    package=vuln_data.get('package', 'unknown'),
                    installed_version=vuln_data.get('installedVersion', 'unknown'),
                    severity=vuln_data.get('severity', 'unknown').lower(),
                    vulnerability_id=vuln_data.get('vulnerabilityID', 'unknown'),
                    description=vuln_data.get('description', 'No description available'),
                    fixed_version=vuln_data.get('fixedVersion')
                )
                vulnerabilities.append(vulnerability)
        
        return vulnerabilities
    
    def scan(self) -> DockerAuditResult:
        """Perform a complete Docker security scan."""
        dockerfiles = self.find_dockerfiles()
        
        if not dockerfiles:
            return DockerAuditResult(
                scan_type="docker",
                project_path=self.project_path,
                dockerfile_path="",
                image_name=None,
                vulnerabilities=[],
                scan_time=datetime.now().isoformat(),
                summary={"info": 0, "low": 0, "moderate": 0, "high": 0, "critical": 0},
                dockerfile_issues=["No Dockerfile found in project"]
            )
        
        # Use the first Dockerfile found
        dockerfile_path = dockerfiles[0]
        
        # Analyze Dockerfile for static issues
        dockerfile_issues = self.analyze_dockerfile(dockerfile_path)
        
        # Add Hadolint results if available
        hadolint_issues = self.run_hadolint(dockerfile_path)
        dockerfile_issues.extend(hadolint_issues)
        
        # Try to scan with various tools
        vulnerabilities = []
        
        # Try Trivy scan
        trivy_data = self.run_trivy_scan(dockerfile_path)
        if trivy_data:
            vulnerabilities.extend(self.parse_scan_results(trivy_data))
        
        # Create summary
        summary = {"info": 0, "low": 0, "moderate": 0, "high": 0, "critical": 0}
        for vuln in vulnerabilities:
            if vuln.severity in summary:
                summary[vuln.severity] += 1
            else:
                summary["info"] += 1
        
        return DockerAuditResult(
            scan_type="docker",
            project_path=self.project_path,
            dockerfile_path=dockerfile_path,
            image_name=None,
            vulnerabilities=vulnerabilities,
            scan_time=datetime.now().isoformat(),
            summary=summary,
            dockerfile_issues=dockerfile_issues
        )


def main():
    """Main function for CLI usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Scan Docker containers for security vulnerabilities")
    parser.add_argument("--path", "-p", default=".", help="Path to the project (default: current directory)")
    parser.add_argument("--image", "-i", help="Docker image name to scan")
    parser.add_argument("--output", "-o", help="Output file for results (JSON format)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    scanner = DockerScanner(args.path)
    result = scanner.scan()
    
    if args.verbose:
        print(f"Scanning Docker project at: {result.project_path}")
        print(f"Dockerfile: {result.dockerfile_path}")
        print(f"Dockerfile issues: {len(result.dockerfile_issues)}")
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
    if result.vulnerabilities or result.dockerfile_issues:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()