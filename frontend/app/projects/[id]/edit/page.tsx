'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { ArrowLeft, Save, Trash2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { api } from '@/lib/api';
import { Project, CreateProjectData } from '@/lib/types';

export default function EditProjectPage() {
  const params = useParams();
  const router = useRouter();
  const projectId = params.id as string;
  
  const [project, setProject] = useState<Project | null>(null);
  const [formData, setFormData] = useState<CreateProjectData>({
    name: '',
    repo_url: '',
    plan_path: 'docs/plan.md',
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (projectId) {
      fetchProject();
    }
  }, [projectId]);

  const fetchProject = async () => {
    try {
      setLoading(true);
      const data = await api.getProject(projectId);
      setProject(data);
      setFormData({
        name: data.name,
        repo_url: data.repo_url,
        plan_path: data.plan_path,
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setError(null);

    try {
      await api.updateProject(projectId, formData);
      router.push(`/projects/${projectId}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update project');
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async () => {
    if (confirm('Are you sure you want to delete this project? This action cannot be undone.')) {
      try {
        await api.deleteProject(projectId);
        router.push('/dashboard');
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to delete project');
      }
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value,
    }));
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

  if (error && !project) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="mb-4">
          <Button 
            variant="secondary" 
            size="sm" 
            onClick={() => router.push('/dashboard')}
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Dashboard
          </Button>
        </div>
        <div className="p-4 bg-danger-50 border border-danger-200 rounded-md">
          <p className="text-danger-800">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <Button 
          variant="secondary" 
          size="sm" 
          onClick={() => router.push(`/projects/${projectId}`)}
          className="mb-4"
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back to Project
        </Button>
        
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Edit Project</h1>
        <p className="text-gray-600">Update your project details</p>
      </div>

      {/* Error Display */}
      {error && (
        <div className="mb-6 p-4 bg-danger-50 border border-danger-200 rounded-md">
          <p className="text-danger-800">{error}</p>
        </div>
      )}

      {/* Edit Form */}
      <Card className="max-w-2xl">
        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          <div>
            <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-2">
              Project Name
            </label>
            <input
              type="text"
              id="name"
              name="name"
              value={formData.name}
              onChange={handleInputChange}
              required
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              placeholder="Enter project name"
            />
          </div>

          <div>
            <label htmlFor="repo_url" className="block text-sm font-medium text-gray-700 mb-2">
              Repository URL
            </label>
            <input
              type="url"
              id="repo_url"
              name="repo_url"
              value={formData.repo_url}
              onChange={handleInputChange}
              required
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              placeholder="https://github.com/username/repository"
            />
            <p className="mt-1 text-sm text-gray-500">
              The URL of your Git repository
            </p>
          </div>

          <div>
            <label htmlFor="plan_path" className="block text-sm font-medium text-gray-700 mb-2">
              Plan File Path
            </label>
            <input
              type="text"
              id="plan_path"
              name="plan_path"
              value={formData.plan_path}
              onChange={handleInputChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              placeholder="docs/plan.md"
            />
            <p className="mt-1 text-sm text-gray-500">
              Path to your project plan file within the repository
            </p>
          </div>

          <div className="flex gap-4 pt-4">
            <Button 
              type="submit" 
              variant="primary" 
              size="md"
              disabled={saving}
              className="flex-1"
            >
              <Save className="w-4 h-4 mr-2" />
              {saving ? 'Saving...' : 'Save Changes'}
            </Button>
            
            <Button 
              type="button" 
              variant="danger" 
              size="md"
              onClick={handleDelete}
            >
              <Trash2 className="w-4 h-4 mr-2" />
              Delete Project
            </Button>
          </div>
        </form>
      </Card>
    </div>
  );
}
