# Dependency Audit Tools

This folder contains security scanning tools for different package managers and containerization technologies.

## Scanners

### NPM Scanner (`npm_scanner.py`)
Scans Node.js projects for security vulnerabilities in NPM packages.

**Features:**
- Parses `package.json` and `package-lock.json`
- Uses `npm audit` command for vulnerability detection
- Supports both npm v6 and v7+ output formats
- Provides detailed vulnerability information

**Usage:**
```bash
python npm_scanner.py --path /path/to/npm/project --output results.json
```

### PyPI Scanner (`pypi_scanner.py`)
Scans Python projects for security vulnerabilities in PyPI packages.

**Features:**
- Scans `requirements.txt`, `setup.py`, and `pyproject.toml`
- Uses Safety and pip-audit tools for vulnerability detection
- Analyzes both declared and installed packages
- Provides fix recommendations

**Usage:**
```bash
python pypi_scanner.py --path /path/to/python/project --output results.json
```

### Docker Scanner (`docker_scanner.py`)
Scans Dockerfiles and Docker images for security issues.

**Features:**
- Static analysis of Dockerfile best practices
- Integration with Trivy and Hadolint scanners
- Detects common security anti-patterns
- Scans for vulnerable base images and packages

**Usage:**
```bash
python docker_scanner.py --path /path/to/docker/project --output results.json
```

### Unified Scanner (`unified_scanner.py`)
Combines all scanners for comprehensive project security analysis.

**Features:**
- Runs all scanners in a single command
- Provides unified reporting across all package managers
- Generates both JSON and text reports
- Aggregates vulnerability statistics

**Usage:**
```bash
python unified_scanner.py --path /path/to/project --format text --output report.txt
```

## Requirements

### Python Dependencies
```bash
pip install safety pip-audit requests
```

### External Tools (Optional)
- **npm**: For NPM scanning
- **Trivy**: For enhanced Docker scanning
- **Hadolint**: For Dockerfile linting

## Output Format

All scanners produce JSON output with the following structure:

```json
{
  "scan_type": "npm|pypi|docker",
  "project_path": "/path/to/project",
  "total_packages": 42,
  "vulnerabilities": [
    {
      "package": "package-name",
      "version": "1.0.0",
      "severity": "high",
      "description": "Vulnerability description",
      "fixed_in": "1.0.1"
    }
  ],
  "scan_time": "2024-01-01T12:00:00Z",
  "summary": {
    "critical": 0,
    "high": 1,
    "moderate": 2,
    "low": 3,
    "info": 0
  }
}
```

## Integration with Backend

These scanners can be integrated with the backend automation system by:

1. Creating automation tasks that trigger scans
2. Scheduling regular security audits
3. Integrating with CI/CD pipelines
4. Sending alerts for critical vulnerabilities

## Security Best Practices

1. **Regular Scanning**: Run scans frequently, especially before releases
2. **Automated Monitoring**: Set up automated scans in CI/CD pipelines
3. **Severity-Based Actions**: Define different responses based on vulnerability severity
4. **Documentation**: Maintain records of scan results and remediation actions
5. **Tool Updates**: Keep scanning tools updated for latest vulnerability databases