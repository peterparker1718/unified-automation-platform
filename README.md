# Unified Automation Platform

End-to-end OpenAI API + Codex/GitHub connector automation platform with dependency auditing, workflow management, and CI/CD integration.

## 🚀 Features

- **OpenAI Integration**: Generate and analyze code using OpenAI's GPT models
- **Interactive Dashboard**: React-based frontend with Material-UI components
- **Dependency Security Scanning**: Automated vulnerability detection for NPM, PyPI, and Docker
- **Workflow Automation**: YAML-based workflow definitions with GitHub integration
- **CI/CD Pipeline**: Comprehensive automated testing, linting, and security scanning
- **Task Management**: Queue and execute automation tasks asynchronously

## 📁 Project Structure

```
unified-automation-platform/
├── backend/                    # Python FastAPI backend
│   ├── server.py              # Main API server
│   ├── openai_integration.py  # OpenAI API client
│   ├── automation_scripts.py  # Workflow engine
│   ├── config.py             # Configuration management
│   └── requirements.txt      # Python dependencies
├── frontend/                  # React TypeScript frontend
│   ├── src/
│   │   ├── components/       # Reusable React components
│   │   ├── pages/           # Main application pages
│   │   └── services/        # API service layer
│   └── package.json         # Node.js dependencies
├── dependency-audit/          # Security scanning tools
│   ├── npm_scanner.py        # NPM vulnerability scanner
│   ├── pypi_scanner.py       # Python package scanner
│   ├── docker_scanner.py     # Docker security scanner
│   └── unified_scanner.py    # Combined security scanner
├── workflow-utils/            # Automation utilities
│   ├── github_helpers.py     # GitHub API integration
│   ├── workflow_manager.py   # Workflow execution engine
│   └── automation_scripts.py # Common automation scripts
└── .github/workflows/         # CI/CD pipeline definitions
    ├── backend-ci.yml        # Backend testing and linting
    ├── frontend-ci.yml       # Frontend testing and linting
    ├── dependency-audit.yml  # Security scanning automation
    ├── code-quality.yml      # Code quality checks
    └── integration-tests.yml # End-to-end integration tests
```

## 🛠️ Setup and Installation

### Prerequisites

- Python 3.9+
- Node.js 16+
- Docker (optional)
- Git

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create environment configuration:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and configuration
   ```

5. Start the development server:
   ```bash
   python -m uvicorn server:app --reload --host 0.0.0.0 --port 8000
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm start
   ```

The frontend will be available at http://localhost:3000 and will proxy API requests to the backend at http://localhost:8000.

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the backend directory with the following variables:

```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4
OPENAI_MAX_TOKENS=2000

# GitHub Configuration  
GITHUB_TOKEN=your_github_token_here
GITHUB_API_BASE=https://api.github.com

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=false

# Database Configuration
DATABASE_URL=sqlite:///./automation_platform.db

# Automation Configuration
MAX_CONCURRENT_JOBS=5
JOB_TIMEOUT_SECONDS=300
```

## 🎯 Usage

### Dashboard Overview

Access the main dashboard at http://localhost:3000 to:

- View task execution statistics
- Monitor recent automation activities
- Access different platform modules

### Code Generation (Codex Trigger)

1. Navigate to the "Codex Trigger" tab
2. Enter your code generation prompt
3. Select the target programming language
4. Click "Generate Code" to get AI-generated code
5. Use "Analyze Code" to get security and quality insights

### Task Management

1. Go to the "Task Management" tab
2. Create new automation tasks with custom parameters
3. Execute tasks and monitor their progress
4. View detailed execution results and logs

### Dependency Auditing

1. Visit the "Dependency Audit" tab
2. Select scan type (NPM, PyPI, Docker, or All)
3. Specify project path
4. Run security scans and review vulnerability reports

## 🔍 Security Scanning

The platform includes comprehensive security scanning capabilities:

### Supported Scan Types

- **NPM**: Scans `package.json` and `package-lock.json` for Node.js vulnerabilities
- **PyPI**: Analyzes Python dependencies in `requirements.txt` and `setup.py`
- **Docker**: Checks Dockerfiles and container images for security issues

### Running Scans

#### Manual Scanning
```bash
# NPM scan
cd dependency-audit
python npm_scanner.py --path ../frontend --output results.json

# Python scan
python pypi_scanner.py --path ../backend --output results.json

# Docker scan
python docker_scanner.py --path .. --output results.json

# Unified scan
python unified_scanner.py --path .. --format json --output unified-results.json
```

#### Automated CI/CD Scanning

Security scans run automatically on:
- Every push to main/develop branches
- Pull request creation
- Weekly scheduled runs (Mondays at 2 AM)

## 🤖 Workflow Automation

### Creating Workflows

Create YAML workflow definitions in the `workflow-utils/workflows/` directory:

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

### GitHub Integration

The platform can automatically:
- Create issues from security scan results
- Merge Dependabot pull requests
- Trigger workflow runs
- Update repository files

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest tests/ --cov=. --cov-report=term-missing
```

### Frontend Tests
```bash
cd frontend
npm test
```

### Integration Tests
```bash
# Start both backend and frontend servers
# Then run integration tests
npm run test:integration
```

## 🚀 Deployment

### Docker Deployment

1. Build the containers:
   ```bash
   docker build -t unified-automation-backend ./backend
   docker build -t unified-automation-frontend ./frontend
   ```

2. Run with Docker Compose:
   ```bash
   docker-compose up -d
   ```

### Production Deployment

1. Set production environment variables
2. Build the frontend for production:
   ```bash
   cd frontend
   npm run build
   ```

3. Deploy backend with a production ASGI server:
   ```bash
   cd backend
   gunicorn -w 4 -k uvicorn.workers.UvicornWorker server:app
   ```

## 📊 Monitoring and Logging

- Backend logs are structured JSON format
- Frontend errors are captured and reported
- Security scan results are stored as artifacts
- Workflow execution logs are available in the dashboard

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and add tests
4. Run the linting and tests: `npm run lint && npm test`
5. Commit your changes: `git commit -am 'Add feature'`
6. Push to the branch: `git push origin feature-name`
7. Create a Pull Request

### Code Quality Standards

- Python code follows PEP 8 with Black formatting
- TypeScript/React code follows ESLint and Prettier rules
- All functions include type hints and docstrings
- Tests are required for new features
- Security scans must pass before merging

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenAI for the GPT API
- GitHub for the automation platform
- React and Material-UI communities
- FastAPI and Python ecosystem
- Security scanning tools: Safety, npm audit, Trivy, Hadolint

## 📞 Support

For support and questions:
- Create an issue in this repository
- Check the documentation in each module's README
- Review the CI/CD workflow logs for deployment issues

---

Built with ❤️ for automation and security-first development.
