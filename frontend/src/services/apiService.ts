import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for adding auth tokens (if needed)
apiClient.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for handling errors
apiClient.interceptors.response.use(
  (response) => {
    return response.data;
  },
  (error) => {
    const message = error.response?.data?.detail || error.message || 'An error occurred';
    return Promise.reject(new Error(message));
  }
);

export interface CodeGenerationRequest {
  prompt: string;
  language: string;
  max_tokens?: number;
}

export interface CodeAnalysisRequest {
  code: string;
  analysis_type: string;
}

export interface TaskCreateRequest {
  name: string;
  description: string;
  task_type: string;
  parameters: Record<string, any>;
}

export interface AutomationScriptRequest {
  task_description: string;
  platform: string;
}

class ApiService {
  // Health check
  async healthCheck() {
    return apiClient.get('/health');
  }

  // OpenAI endpoints
  async generateCode(request: CodeGenerationRequest) {
    return apiClient.post('/api/generate-code', request);
  }

  async analyzeCode(request: CodeAnalysisRequest) {
    return apiClient.post('/api/analyze-code', request);
  }

  async generateAutomationScript(request: AutomationScriptRequest) {
    return apiClient.post('/api/generate-automation-script', request);
  }

  // Task management endpoints
  async createTask(request: TaskCreateRequest) {
    return apiClient.post('/api/tasks', request);
  }

  async executeTask(taskId: string) {
    return apiClient.post(`/api/tasks/${taskId}/execute`);
  }

  async getTaskStatus(taskId: string) {
    return apiClient.get(`/api/tasks/${taskId}`);
  }

  async listTasks() {
    return apiClient.get('/api/tasks');
  }

  // Configuration endpoint
  async getConfig() {
    return apiClient.get('/api/config');
  }

  // Dependency audit endpoints (mock for now)
  async runDependencyAudit(auditType: string, projectPath: string) {
    // This would be a real endpoint in the backend
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          success: true,
          audit_type: auditType,
          project_path: projectPath,
          vulnerabilities_found: Math.floor(Math.random() * 10),
          recommendations: [
            'Update dependencies to latest versions',
            'Review security advisories regularly',
            'Use automated dependency monitoring'
          ]
        });
      }, 2000);
    });
  }
}

export const apiService = new ApiService();