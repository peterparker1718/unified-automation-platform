#!/usr/bin/env python3
"""
Unified Security Scanner
Combines NPM, PyPI, and Docker security scanning
"""

import json
import sys
import os
from typing import Dict, List, Any
from dataclasses import dataclass, asdict
from datetime import datetime

from npm_scanner import NPMScanner
from pypi_scanner import PyPIScanner
from docker_scanner import DockerScanner


@dataclass
class UnifiedScanResult:
    """Represents the result of a unified security scan."""
    scan_time: str
    project_path: str
    npm_result: Any
    pypi_result: Any
    docker_result: Any
    total_vulnerabilities: int
    summary: Dict[str, Dict[str, int]]


class UnifiedScanner:
    """Unified security scanner for multiple package managers."""
    
    def __init__(self, project_path: str = "."):
        self.project_path = os.path.abspath(project_path)
        self.npm_scanner = NPMScanner(project_path)
        self.pypi_scanner = PyPIScanner(project_path)
        self.docker_scanner = DockerScanner(project_path)
    
    def scan_all(self) -> UnifiedScanResult:
        """Perform security scans for all supported package managers."""
        print("Starting unified security scan...")
        
        # Run individual scans
        print("Scanning NPM packages...")
        npm_result = self.npm_scanner.scan()
        
        print("Scanning Python packages...")
        pypi_result = self.pypi_scanner.scan()
        
        print("Scanning Docker configuration...")
        docker_result = self.docker_scanner.scan()
        
        # Calculate totals
        total_vulnerabilities = (
            len(npm_result.vulnerabilities) +
            len(pypi_result.vulnerabilities) +
            len(docker_result.vulnerabilities)
        )
        
        # Create unified summary
        summary = {
            "npm": npm_result.summary,
            "pypi": pypi_result.summary,
            "docker": docker_result.summary,
            "total": {
                "info": sum(result.summary.get("info", 0) for result in [npm_result, pypi_result, docker_result]),
                "low": sum(result.summary.get("low", 0) for result in [npm_result, pypi_result, docker_result]),
                "moderate": sum(result.summary.get("moderate", 0) for result in [npm_result, pypi_result, docker_result]),
                "high": sum(result.summary.get("high", 0) for result in [npm_result, pypi_result, docker_result]),
                "critical": sum(result.summary.get("critical", 0) for result in [npm_result, pypi_result, docker_result])
            }
        }
        
        return UnifiedScanResult(
            scan_time=datetime.now().isoformat(),
            project_path=self.project_path,
            npm_result=asdict(npm_result),
            pypi_result=asdict(pypi_result),
            docker_result=asdict(docker_result),
            total_vulnerabilities=total_vulnerabilities,
            summary=summary
        )
    
    def generate_report(self, result: UnifiedScanResult, output_format: str = "json") -> str:
        """Generate a formatted report from scan results."""
        if output_format == "json":
            return json.dumps(asdict(result), indent=2)
        
        elif output_format == "text":
            report = []
            report.append("=== UNIFIED SECURITY SCAN REPORT ===")
            report.append(f"Scan Time: {result.scan_time}")
            report.append(f"Project Path: {result.project_path}")
            report.append(f"Total Vulnerabilities: {result.total_vulnerabilities}")
            report.append("")
            
            # Summary table
            report.append("SUMMARY BY SEVERITY:")
            report.append("-" * 40)
            for severity in ["critical", "high", "moderate", "low", "info"]:
                count = result.summary["total"].get(severity, 0)
                report.append(f"{severity.upper():10} : {count:3d}")
            report.append("")
            
            # NPM Results
            if result.npm_result["vulnerabilities"]:
                report.append("NPM VULNERABILITIES:")
                report.append("-" * 20)
                for vuln in result.npm_result["vulnerabilities"]:
                    report.append(f"• {vuln['package']}@{vuln['version']} - {vuln['severity']}")
                    report.append(f"  {vuln['title']}")
                report.append("")
            
            # Python Results
            if result.pypi_result["vulnerabilities"]:
                report.append("PYTHON VULNERABILITIES:")
                report.append("-" * 23)
                for vuln in result.pypi_result["vulnerabilities"]:
                    report.append(f"• {vuln['package']}@{vuln['installed_version']} - {vuln['severity']}")
                    report.append(f"  {vuln['description']}")
                report.append("")
            
            # Docker Results
            if result.docker_result["dockerfile_issues"]:
                report.append("DOCKER ISSUES:")
                report.append("-" * 14)
                for issue in result.docker_result["dockerfile_issues"]:
                    report.append(f"• {issue}")
                report.append("")
            
            return "\n".join(report)
        
        else:
            raise ValueError(f"Unsupported output format: {output_format}")


def main():
    """Main function for CLI usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Unified security scanner for NPM, PyPI, and Docker")
    parser.add_argument("--path", "-p", default=".", help="Path to the project (default: current directory)")
    parser.add_argument("--output", "-o", help="Output file for results")
    parser.add_argument("--format", "-f", choices=["json", "text"], default="json", help="Output format")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    scanner = UnifiedScanner(args.path)
    result = scanner.scan_all()
    
    if args.verbose:
        print(f"\nScan completed!")
        print(f"Total vulnerabilities found: {result.total_vulnerabilities}")
        print(f"Summary: {result.summary['total']}")
    
    # Generate report
    report = scanner.generate_report(result, args.format)
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(report)
        print(f"Report saved to: {args.output}")
    else:
        print(report)
    
    # Exit with non-zero code if vulnerabilities found
    if result.total_vulnerabilities > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()