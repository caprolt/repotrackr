'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { 
  ArrowLeft, 
  GitBranch, 
  Clock, 
  FileText, 
  RefreshCw,
  CheckCircle,
  Circle,
  AlertCircle,
  XCircle,
  Edit,
  Trash2
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { StatusBadge } from '@/components/ui/status-badge';
import { Progress } from '@/components/ui/progress';
import { api } from '@/lib/api';
import { ProjectDetail, Task } from '@/lib/types';
import { formatDate } from '@/lib/utils';

export default function ProjectDetailPage() {
  const params = useParams();
  const router = useRouter();
  const projectId = params.id as string;
  
  const [project, setProject] = useState<ProjectDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    if (projectId) {
      fetchProjectDetail();
    }
  }, [projectId]);

  const fetchProjectDetail = async () => {
    try {
      setLoading(true);
      const data = await api.getProjectDetail(projectId);
      setProject(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = async () => {
    try {
      setRefreshing(true);
      await api.refreshProject(projectId);
      await fetchProjectDetail();
    } catch (err) {
      console.error('Failed to refresh project:', err);
    } finally {
      setRefreshing(false);
    }
  };

  const handleDeleteProject = async () => {
    if (confirm('Are you sure you want to delete this project? This action cannot be undone.')) {
      try {
        await api.deleteProject(projectId);
        router.push('/dashboard');
      } catch (err) {
        console.error('Failed to delete project:', err);
        setError(err instanceof Error ? err.message : 'Failed to delete project');
      }
    }
  };

  const handleEditProject = () => {
    router.push(`/projects/${projectId}/edit`);
  };

  const getTaskStatusIcon = (status: string) => {
    switch (status) {
      case 'done':
        return <CheckCircle className="w-4 h-4 text-success-600" />;
      case 'doing':
        return <AlertCircle className="w-4 h-4 text-warning-600" />;
      case 'blocked':
        return <XCircle className="w-4 h-4 text-danger-600" />;
      case 'todo':
      default:
        return <Circle className="w-4 h-4 text-gray-400" />;
    }
  };

  const getTaskStatusColor = (status: string) => {
    switch (status) {
      case 'done':
        return 'text-success-600';
      case 'doing':
        return 'text-warning-600';
      case 'blocked':
        return 'text-danger-600';
      case 'todo':
      default:
        return 'text-gray-600';
    }
  };

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="flex items-center justify-center min-h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
        </div>
      </div>
    );
  }

  if (error || !project) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center">
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Error</h2>
          <p className="text-gray-600 mb-4">{error || 'Project not found'}</p>
          <Button variant="primary" onClick={() => router.push('/dashboard')}>
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Dashboard
          </Button>
        </div>
      </div>
    );
  }

  const latestProgress = project.progress_history[0];
  const progressPercentage = latestProgress ? latestProgress.percentage_complete : 0;

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <Button 
          variant="secondary" 
          size="sm" 
          onClick={() => router.push('/dashboard')}
          className="mb-4"
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back to Dashboard
        </Button>
        
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">{project.name}</h1>
            <div className="flex items-center gap-4 text-sm text-gray-600">
              <div className="flex items-center">
                <GitBranch className="w-4 h-4 mr-2" />
                <span className="truncate">{project.repo_url}</span>
              </div>
              <div className="flex items-center">
                <Clock className="w-4 h-4 mr-2" />
                <span>Updated {formatDate(project.last_updated)}</span>
              </div>
            </div>
          </div>
          
          <div className="flex items-center gap-3">
            <StatusBadge status={project.status}>
              <span className="capitalize">{project.status}</span>
            </StatusBadge>
            <Button 
              variant="primary" 
              size="sm"
              onClick={handleRefresh}
              disabled={refreshing}
            >
              <RefreshCw className={`w-4 h-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
            <Button 
              variant="outline" 
              size="sm"
              onClick={handleEditProject}
            >
              <Edit className="w-4 h-4 mr-2" />
              Edit
            </Button>
            <Button 
              variant="danger" 
              size="sm"
              onClick={handleDeleteProject}
            >
              <Trash2 className="w-4 h-4 mr-2" />
              Delete
            </Button>
          </div>
        </div>
      </div>

      {/* Progress Overview */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        <Card title="Progress Overview">
          <div className="flex items-center justify-center mb-4">
            <Progress 
              percentage={progressPercentage} 
              variant="circular" 
              size="lg"
              color={project.status === 'green' ? 'text-success-600' : 
                     project.status === 'yellow' ? 'text-warning-600' : 
                     'text-danger-600'}
            />
          </div>
          <div className="text-center">
            <p className="text-2xl font-bold text-gray-900">{Math.round(progressPercentage)}%</p>
            <p className="text-sm text-gray-600">Complete</p>
          </div>
        </Card>

        <Card title="Task Breakdown">
          {latestProgress && (
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Done</span>
                <span className="font-medium text-success-600">{latestProgress.tasks_done}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">In Progress</span>
                <span className="font-medium text-warning-600">{latestProgress.tasks_doing}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Todo</span>
                <span className="font-medium text-gray-600">{latestProgress.tasks_todo}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Blocked</span>
                <span className="font-medium text-danger-600">{latestProgress.tasks_blocked}</span>
              </div>
              <div className="border-t pt-3">
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium text-gray-900">Total</span>
                  <span className="font-bold text-gray-900">{latestProgress.tasks_total}</span>
                </div>
              </div>
            </div>
          )}
        </Card>

        <Card title="Project Info">
          <div className="space-y-3">
            <div>
              <label className="text-sm font-medium text-gray-700">Repository</label>
              <p className="text-sm text-gray-900 truncate">{project.repo_url}</p>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-700">Plan Path</label>
              <p className="text-sm text-gray-900">{project.plan_path}</p>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-700">Created</label>
              <p className="text-sm text-gray-900">{formatDate(project.created_at)}</p>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-700">Last Updated</label>
              <p className="text-sm text-gray-900">{formatDate(project.last_updated)}</p>
            </div>
          </div>
        </Card>
      </div>

      {/* Tasks List */}
      <Card title={`Tasks (${project.tasks.length})`}>
        {project.tasks.length === 0 ? (
          <div className="text-center py-8">
            <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600">No tasks found for this project.</p>
          </div>
        ) : (
          <div className="space-y-3">
            {project.tasks.map((task) => (
              <div 
                key={task.id} 
                className="flex items-start gap-3 p-3 border border-gray-200 rounded-lg hover:bg-gray-50"
              >
                <div className="flex-shrink-0 mt-0.5">
                  {getTaskStatusIcon(task.status)}
                </div>
                <div className="flex-1 min-w-0">
                  <h4 className={`text-sm font-medium ${getTaskStatusColor(task.status)}`}>
                    {task.title}
                  </h4>
                  {task.file_path && (
                    <p className="text-xs text-gray-500 mt-1">
                      {task.file_path}{task.line_number ? `:${task.line_number}` : ''}
                    </p>
                  )}
                </div>
                <div className="flex-shrink-0">
                  <StatusBadge status={task.status === 'done' ? 'green' : 
                                       task.status === 'doing' ? 'yellow' : 
                                       task.status === 'blocked' ? 'red' : 'gray'}>
                    <span className="capitalize">{task.status}</span>
                  </StatusBadge>
                </div>
              </div>
            ))}
          </div>
        )}
      </Card>
    </div>
  );
}
