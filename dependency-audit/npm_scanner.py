#!/usr/bin/env python3
"""
NPM Security Scanner
Scans package.json and package-lock.json for known vulnerabilities
"""

import json
import subprocess
import sys
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class Vulnerability:
    """Represents a security vulnerability."""
    package: str
    version: str
    severity: str
    title: str
    url: str
    dependency_path: List[str]
    fixed_in: Optional[str] = None


@dataclass
class AuditResult:
    """Represents the result of a security audit."""
    scan_type: str
    project_path: str
    total_packages: int
    vulnerabilities: List[Vulnerability]
    scan_time: str
    summary: Dict[str, int]


class NPMScanner:
    """NPM package security scanner."""
    
    def __init__(self, project_path: str = "."):
        self.project_path = os.path.abspath(project_path)
        self.package_json_path = os.path.join(self.project_path, "package.json")
        self.package_lock_path = os.path.join(self.project_path, "package-lock.json")
    
    def is_npm_project(self) -> bool:
        """Check if the directory contains an NPM project."""
        return os.path.exists(self.package_json_path)
    
    def get_installed_packages(self) -> Dict[str, str]:
        """Get list of installed packages and their versions."""
        packages = {}
        
        try:
            with open(self.package_json_path, 'r') as f:
                package_data = json.load(f)
            
            # Get dependencies
            deps = package_data.get('dependencies', {})
            dev_deps = package_data.get('devDependencies', {})
            packages.update(deps)
            packages.update(dev_deps)
            
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error reading package.json: {e}")
        
        return packages
    
    def run_npm_audit(self) -> Dict[str, Any]:
        """Run npm audit command and return results."""
        try:
            # Change to project directory
            original_cwd = os.getcwd()
            os.chdir(self.project_path)
            
            # Run npm audit with JSON output
            result = subprocess.run(
                ['npm', 'audit', '--json'],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            os.chdir(original_cwd)
            
            if result.returncode in [0, 1]:  # 0 = no vulnerabilities, 1 = vulnerabilities found
                return json.loads(result.stdout)
            else:
                print(f"npm audit failed: {result.stderr}")
                return {}
                
        except subprocess.TimeoutExpired:
            print("npm audit timed out")
            return {}
        except json.JSONDecodeError:
            print("Failed to parse npm audit output")
            return {}
        except FileNotFoundError:
            print("npm command not found. Please install Node.js and npm.")
            return {}
        except Exception as e:
            print(f"Error running npm audit: {e}")
            return {}
    
    def parse_audit_results(self, audit_data: Dict[str, Any]) -> List[Vulnerability]:
        """Parse npm audit results into Vulnerability objects."""
        vulnerabilities = []
        
        # Handle different npm audit output formats
        if 'vulnerabilities' in audit_data:
            # npm v7+ format
            for vuln_id, vuln_data in audit_data['vulnerabilities'].items():
                vulnerability = Vulnerability(
                    package=vuln_data.get('name', 'unknown'),
                    version=vuln_data.get('version', 'unknown'),
                    severity=vuln_data.get('severity', 'unknown'),
                    title=vuln_data.get('title', 'No title available'),
                    url=vuln_data.get('url', ''),
                    dependency_path=vuln_data.get('via', []),
                    fixed_in=vuln_data.get('fixAvailable', {}).get('version') if vuln_data.get('fixAvailable') else None
                )
                vulnerabilities.append(vulnerability)
        
        elif 'advisories' in audit_data:
            # npm v6 format
            for advisory_id, advisory in audit_data['advisories'].items():
                vulnerability = Vulnerability(
                    package=advisory.get('module_name', 'unknown'),
                    version=advisory.get('vulnerable_versions', 'unknown'),
                    severity=advisory.get('severity', 'unknown'),
                    title=advisory.get('title', 'No title available'),
                    url=advisory.get('url', ''),
                    dependency_path=advisory.get('findings', [{}])[0].get('paths', []),
                    fixed_in=advisory.get('patched_versions') if advisory.get('patched_versions') != '<0.0.0' else None
                )
                vulnerabilities.append(vulnerability)
        
        return vulnerabilities
    
    def scan(self) -> AuditResult:
        """Perform a complete security scan."""
        if not self.is_npm_project():
            return AuditResult(
                scan_type="npm",
                project_path=self.project_path,
                total_packages=0,
                vulnerabilities=[],
                scan_time=datetime.now().isoformat(),
                summary={"info": 0, "low": 0, "moderate": 0, "high": 0, "critical": 0}
            )
        
        # Get package information
        packages = self.get_installed_packages()
        
        # Run npm audit
        audit_data = self.run_npm_audit()
        
        # Parse vulnerabilities
        vulnerabilities = self.parse_audit_results(audit_data)
        
        # Create summary
        summary = {"info": 0, "low": 0, "moderate": 0, "high": 0, "critical": 0}
        for vuln in vulnerabilities:
            if vuln.severity in summary:
                summary[vuln.severity] += 1
            else:
                summary["info"] += 1
        
        return AuditResult(
            scan_type="npm",
            project_path=self.project_path,
            total_packages=len(packages),
            vulnerabilities=vulnerabilities,
            scan_time=datetime.now().isoformat(),
            summary=summary
        )


def main():
    """Main function for CLI usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Scan NPM packages for security vulnerabilities")
    parser.add_argument("--path", "-p", default=".", help="Path to the NPM project (default: current directory)")
    parser.add_argument("--output", "-o", help="Output file for results (JSON format)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    scanner = NPMScanner(args.path)
    result = scanner.scan()
    
    if args.verbose:
        print(f"Scanning NPM project at: {result.project_path}")
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