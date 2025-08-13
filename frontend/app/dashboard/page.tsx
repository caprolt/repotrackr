'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Plus, GitBranch, Clock, CheckCircle, AlertCircle, XCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { StatusBadge } from '@/components/ui/status-badge';
import { api } from '@/lib/api';
import { Project } from '@/lib/types';
import { formatDate } from '@/lib/utils';

export default function Dashboard() {
  const router = useRouter();
  const [projects, setProjects] = useState<Project[]>([]);
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
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'green':
        return <CheckCircle className="w-4 h-4 text-success-600" />;
      case 'yellow':
        return <AlertCircle className="w-4 h-4 text-warning-600" />;
      case 'red':
        return <XCircle className="w-4 h-4 text-danger-600" />;
      default:
        return <AlertCircle className="w-4 h-4 text-gray-600" />;
    }
  };

  const handleRefreshProject = async (projectId: string) => {
    try {
      await api.refreshProject(projectId);
      // Refresh the projects list to get updated data
      await fetchProjects();
    } catch (err) {
      console.error('Failed to refresh project:', err);
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
        <div className="mb-6 p-4 bg-danger-50 border border-danger-200 rounded-md">
          <p className="text-danger-800">{error}</p>
        </div>
      )}

      {/* Projects Grid */}
      {projects.length === 0 ? (
        <div className="text-center py-12">
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
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {projects.map((project) => (
            <Card key={project.id} className="hover:shadow-lg transition-shadow">
              <div className="flex items-start justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900 truncate">
                  {project.name}
                </h3>
                <StatusBadge status={project.status}>
                  {getStatusIcon(project.status)}
                  <span className="ml-1 capitalize">{project.status}</span>
                </StatusBadge>
              </div>
              
              <div className="space-y-2 mb-4">
                <div className="flex items-center text-sm text-gray-600">
                  <GitBranch className="w-4 h-4 mr-2" />
                  <span className="truncate">{project.repo_url}</span>
                </div>
                <div className="flex items-center text-sm text-gray-600">
                  <Clock className="w-4 h-4 mr-2" />
                  <span>Updated {formatDate(project.last_updated)}</span>
                </div>
              </div>
              
              <div className="flex gap-2">
                <Button 
                  variant="secondary" 
                  size="sm" 
                  className="flex-1"
                  onClick={() => router.push(`/projects/${project.id}`)}
                >
                  View Details
                </Button>
                <Button 
                  variant="primary" 
                  size="sm"
                  onClick={() => handleRefreshProject(project.id)}
                >
                  Refresh
                </Button>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
