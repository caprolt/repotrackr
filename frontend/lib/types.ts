export interface Project {
  id: string;
  name: string;
  repo_url: string;
  plan_path: string;
  status: 'green' | 'yellow' | 'red';
  last_updated: string;
  created_at: string;
  progress_percentage?: number;
  task_breakdown?: {
    todo: number;
    doing: number;
    done: number;
    blocked: number;
  };
}

export interface ProjectListResponse {
  projects: Project[];
  total: number;
  limit: number;
  offset: number;
}

export interface Task {
  id: string;
  title: string;
  status: 'todo' | 'doing' | 'done' | 'blocked';
  file_path?: string;
  line_number?: number;
  created_at: string;
}

export interface ProgressSnapshot {
  id: string;
  percentage_complete: number;
  tasks_total: number;
  tasks_done: number;
  tasks_doing: number;
  tasks_todo: number;
  tasks_blocked: number;
  created_at: string;
}

export interface ProjectDetail extends Project {
  tasks: Task[];
  progress_history: ProgressSnapshot[];
}

export interface CreateProjectData {
  name: string;
  repo_url: string;
  plan_path?: string;
}

export interface ProcessingResult {
  success: boolean;
  tasks_count?: number;
  progress_percentage?: number;
  project_status?: string;
  processing_time?: number;
  error_message?: string;
}
