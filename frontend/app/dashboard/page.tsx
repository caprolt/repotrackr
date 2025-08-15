'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { 
  Plus, 
  GitBranch, 
  Clock, 
  CheckCircle, 
  AlertCircle, 
  XCircle, 
  Edit, 
  Trash2,
  ExternalLink,
  ChevronDown,
  ChevronRight
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { StatusBadge } from '@/components/ui/status-badge';
import { Progress } from '@/components/ui/progress';
import { 
  Table, 
  TableHeader, 
  TableBody, 
  TableRow, 
  TableHead, 
  TableCell 
} from '@/components/ui/table';
import { Collapsible } from '@/components/ui/collapsible';
import { api } from '@/lib/api';
import { Project, Task } from '@/lib/types';
import { formatDate } from '@/lib/utils';

export default function Dashboard() {
  const router = useRouter();
  const [projects, setProjects] = useState<Project[]>([]);
  const [projectTasks, setProjectTasks] = useState<Record<string, Task[]>>({});
  const [expandedTasks, setExpandedTasks] = useState<Record<string, string | null>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchProjects();
  }, []);

  const fetchProjects = async () => {
    try {
      setLoading(true);
      const data = await api.getProjects();
      setProjects(data.projects);
      
      // Fetch tasks for each project
      const tasksData: Record<string, Task[]> = {};
      for (const project of data.projects) {
        try {
          const tasksResponse = await api.getProjectTasks(project.id);
          tasksData[project.id] = tasksResponse.tasks;
        } catch (err) {
          console.error(`Failed to fetch tasks for project ${project.id}:`, err);
          tasksData[project.id] = [];
        }
      }
      setProjectTasks(tasksData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'green':
        return <CheckCircle className="w-4 h-4 text-green-600" />;
      case 'yellow':
        return <AlertCircle className="w-4 h-4 text-yellow-600" />;
      case 'red':
        return <XCircle className="w-4 h-4 text-red-600" />;
      default:
        return <AlertCircle className="w-4 h-4 text-gray-600" />;
    }
  };

  const getTaskBreakdown = (projectId: string) => {
    const tasks = projectTasks[projectId] || [];
    return {
      todo: tasks.filter(t => t.status === 'todo').length,
      doing: tasks.filter(t => t.status === 'doing').length,
      done: tasks.filter(t => t.status === 'done').length,
      blocked: tasks.filter(t => t.status === 'blocked').length,
    };
  };

  const getProgressPercentage = (projectId: string) => {
    const breakdown = getTaskBreakdown(projectId);
    const total = breakdown.todo + breakdown.doing + breakdown.done + breakdown.blocked;
    if (total === 0) return 0;
    return Math.round((breakdown.done / total) * 100);
  };

  const handleRefreshProject = async (projectId: string) => {
    try {
      await api.refreshProject(projectId);
      await fetchProjects();
    } catch (err) {
      console.error('Failed to refresh project:', err);
    }
  };

  const handleDeleteProject = async (projectId: string) => {
    if (confirm('Are you sure you want to delete this project? This action cannot be undone.')) {
      try {
        await api.deleteProject(projectId);
        await fetchProjects();
      } catch (err) {
        console.error('Failed to delete project:', err);
        setError(err instanceof Error ? err.message : 'Failed to delete project');
      }
    }
  };

  const handleEditProject = (projectId: string) => {
    router.push(`/projects/${projectId}/edit`);
  };

  const toggleTaskBreakdown = (projectId: string, status: string) => {
    const currentExpanded = expandedTasks[projectId];
    const newStatus = currentExpanded === status ? null : status;
    setExpandedTasks(prev => ({
      ...prev,
      [projectId]: newStatus
    }));
  };

  const getTasksByStatus = (projectId: string, status: string) => {
    const tasks = projectTasks[projectId] || [];
    return tasks.filter(task => task.status === status);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'todo': return 'text-blue-600 bg-blue-50';
      case 'doing': return 'text-yellow-600 bg-yellow-50';
      case 'done': return 'text-green-600 bg-green-50';
      case 'blocked': return 'text-red-600 bg-red-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'todo': return 'To Do';
      case 'doing': return 'In Progress';
      case 'done': return 'Done';
      case 'blocked': return 'Blocked';
      default: return status;
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

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Dashboard</h1>
        <p className="text-gray-600">Track your project progress automatically</p>
      </div>

      {/* Add Project Button */}
      <div className="mb-6">
        <Button 
          variant="primary" 
          size="md"
          onClick={() => router.push('/projects/new')}
        >
          <Plus className="w-4 h-4 mr-2" />
          Add Project
        </Button>
      </div>

      {/* Error Display */}
      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-md">
          <p className="text-red-800">{error}</p>
        </div>
      )}

      {/* Projects Table */}
      {projects.length === 0 ? (
        <Card className="text-center py-12">
          <GitBranch className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No projects yet</h3>
          <p className="text-gray-600 mb-4">
            Get started by adding your first project to track its progress.
          </p>
          <Button 
            variant="primary" 
            size="md"
            onClick={() => router.push('/projects/new')}
          >
            <Plus className="w-4 h-4 mr-2" />
            Add Your First Project
          </Button>
        </Card>
      ) : (
        <Card className="overflow-hidden">
          <div className="overflow-x-auto">
            <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Project Name</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Progress</TableHead>
                <TableHead>Updated</TableHead>
                <TableHead>Task Breakdown</TableHead>
                <TableHead>Repo Link</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {projects.map((project) => {
                const breakdown = getTaskBreakdown(project.id);
                const progressPercentage = getProgressPercentage(project.id);
                const isExpanded = expandedTasks[project.id];
                
                return (
                  <>
                    <TableRow key={project.id} className="hover:bg-gray-50">
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <button
                            onClick={() => handleEditProject(project.id)}
                            className="font-medium text-gray-900 hover:text-blue-600 transition-colors"
                          >
                            {project.name}
                          </button>
                        </div>
                      </TableCell>
                      <TableCell>
                        <StatusBadge status={project.status}>
                          {getStatusIcon(project.status)}
                          <span className="ml-1 capitalize">{project.status}</span>
                        </StatusBadge>
                      </TableCell>
                      <TableCell>
                        <div className="w-24">
                          <Progress 
                            percentage={progressPercentage} 
                            size="sm" 
                            variant="linear"
                          />
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center text-sm text-gray-600">
                          <Clock className="w-4 h-4 mr-2" />
                          {formatDate(project.last_updated)}
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className="flex flex-wrap gap-1">
                          <button
                            onClick={() => toggleTaskBreakdown(project.id, 'todo')}
                            className={`px-2 py-1 rounded text-xs font-medium ${getStatusColor('todo')} hover:opacity-80 transition-opacity`}
                          >
                            {breakdown.todo} Todo
                          </button>
                          <button
                            onClick={() => toggleTaskBreakdown(project.id, 'doing')}
                            className={`px-2 py-1 rounded text-xs font-medium ${getStatusColor('doing')} hover:opacity-80 transition-opacity`}
                          >
                            {breakdown.doing} Doing
                          </button>
                          <button
                            onClick={() => toggleTaskBreakdown(project.id, 'done')}
                            className={`px-2 py-1 rounded text-xs font-medium ${getStatusColor('done')} hover:opacity-80 transition-opacity`}
                          >
                            {breakdown.done} Done
                          </button>
                          <button
                            onClick={() => toggleTaskBreakdown(project.id, 'blocked')}
                            className={`px-2 py-1 rounded text-xs font-medium ${getStatusColor('blocked')} hover:opacity-80 transition-opacity`}
                          >
                            {breakdown.blocked} Blocked
                          </button>
                        </div>
                      </TableCell>
                      <TableCell>
                        <a
                          href={project.repo_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="flex items-center text-sm text-gray-600 hover:text-blue-600 transition-colors"
                        >
                          <GitBranch className="w-4 h-4 mr-2" />
                          <span className="truncate max-w-32">View Repo</span>
                          <ExternalLink className="w-3 h-3 ml-1" />
                        </a>
                      </TableCell>
                      <TableCell>
                        <div className="flex gap-2">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleRefreshProject(project.id)}
                          >
                            Refresh
                          </Button>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleEditProject(project.id)}
                          >
                            <Edit className="w-4 h-4" />
                          </Button>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleDeleteProject(project.id)}
                          >
                            <Trash2 className="w-4 h-4" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                    
                    {/* Expanded Task Details */}
                    {isExpanded && (
                      <TableRow>
                        <TableCell colSpan={7} className="p-0">
                          <div className="bg-gray-50 border-t border-gray-200 p-4">
                            <div className="flex items-center gap-2 mb-3">
                              {isExpanded === 'todo' ? (
                                <ChevronDown className="w-4 h-4 text-blue-600" />
                              ) : (
                                <ChevronRight className="w-4 h-4 text-blue-600" />
                              )}
                              <h4 className="font-medium text-gray-900">
                                {getStatusLabel(isExpanded)} Tasks
                              </h4>
                              <button
                                onClick={() => toggleTaskBreakdown(project.id, isExpanded)}
                                className="text-sm text-gray-500 hover:text-gray-700"
                              >
                                (Click to collapse)
                              </button>
                            </div>
                            
                            <div className="space-y-2">
                              {getTasksByStatus(project.id, isExpanded).map((task) => (
                                <div
                                  key={task.id}
                                  className="flex items-center justify-between p-3 bg-white rounded-md border border-gray-200"
                                >
                                  <div className="flex-1">
                                    <h5 className="font-medium text-gray-900">{task.title}</h5>
                                    {task.file_path && (
                                      <p className="text-sm text-gray-600">
                                        {task.file_path}{task.line_number && `:${task.line_number}`}
                                      </p>
                                    )}
                                  </div>
                                  <div className="text-sm text-gray-500">
                                    {formatDate(task.created_at)}
                                  </div>
                                </div>
                              ))}
                              
                              {getTasksByStatus(project.id, isExpanded).length === 0 && (
                                <div className="text-center py-4 text-gray-500">
                                  No {isExpanded} tasks found for this project.
                                </div>
                              )}
                            </div>
                          </div>
                        </TableCell>
                      </TableRow>
                    )}
                  </>
                );
              })}
            </TableBody>
          </Table>
          </div>
        </Card>
      )}
    </div>
  );
}
