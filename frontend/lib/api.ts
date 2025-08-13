import { 
  Project, 
  ProjectListResponse, 
  ProjectDetail, 
  CreateProjectData, 
  ProcessingResult 
} from './types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public statusText: string
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const errorText = await response.text();
    throw new ApiError(
      errorText || `HTTP error! status: ${response.status}`,
      response.status,
      response.statusText
    );
  }
  
  return response.json();
}

export class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  async getProjects(limit: number = 20, offset: number = 0): Promise<ProjectListResponse> {
    const response = await fetch(
      `${this.baseUrl}/api/v1/projects/?limit=${limit}&offset=${offset}`
    );
    return handleResponse<ProjectListResponse>(response);
  }

  async getProject(id: string): Promise<Project> {
    const response = await fetch(`${this.baseUrl}/api/v1/projects/${id}`);
    return handleResponse<Project>(response);
  }

  async createProject(data: CreateProjectData): Promise<Project> {
    const response = await fetch(`${this.baseUrl}/api/v1/projects/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    return handleResponse<Project>(response);
  }

  async deleteProject(id: string): Promise<void> {
    const response = await fetch(`${this.baseUrl}/api/v1/projects/${id}`, {
      method: 'DELETE',
    });
    await handleResponse(response);
  }

  async refreshProject(id: string): Promise<ProcessingResult> {
    const response = await fetch(`${this.baseUrl}/api/v1/projects/${id}/process`, {
      method: 'POST',
    });
    return handleResponse<ProcessingResult>(response);
  }

  async getProjectTasks(id: string): Promise<{ project_id: string; tasks: any[]; total: number }> {
    const response = await fetch(`${this.baseUrl}/api/v1/projects/${id}/tasks`);
    return handleResponse(response);
  }

  async getProjectProgress(id: string, limit: number = 10): Promise<{ project_id: string; progress_history: any[]; total: number }> {
    const response = await fetch(`${this.baseUrl}/api/v1/projects/${id}/progress?limit=${limit}`);
    return handleResponse(response);
  }

  async getProjectDetail(id: string): Promise<ProjectDetail> {
    const [project, tasksData, progressData] = await Promise.all([
      this.getProject(id),
      this.getProjectTasks(id),
      this.getProjectProgress(id),
    ]);

    return {
      ...project,
      tasks: tasksData.tasks,
      progress_history: progressData.progress_history,
    };
  }
}

// Export a default instance
export const apiClient = new ApiClient();

// Export individual functions for convenience
export const api = {
  getProjects: (limit?: number, offset?: number) => apiClient.getProjects(limit, offset),
  getProject: (id: string) => apiClient.getProject(id),
  createProject: (data: CreateProjectData) => apiClient.createProject(data),
  deleteProject: (id: string) => apiClient.deleteProject(id),
  refreshProject: (id: string) => apiClient.refreshProject(id),
  getProjectDetail: (id: string) => apiClient.getProjectDetail(id),
};
