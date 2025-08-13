'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { ArrowLeft, Plus } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { api } from '@/lib/api';
import { CreateProjectData } from '@/lib/types';

export default function NewProjectPage() {
  const router = useRouter();
  const [formData, setFormData] = useState<CreateProjectData>({
    name: '',
    repo_url: '',
    plan_path: 'docs/plan.md',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const project = await api.createProject(formData);
      router.push(`/projects/${project.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create project');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value,
    }));
  };

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
        
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Add New Project</h1>
        <p className="text-gray-600">Track progress for a new repository</p>
      </div>

      {/* Form */}
      <div className="max-w-2xl">
        <Card title="Project Details">
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Error Display */}
            {error && (
              <div className="p-4 bg-danger-50 border border-danger-200 rounded-md">
                <p className="text-danger-800">{error}</p>
              </div>
            )}

            {/* Project Name */}
            <div>
              <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-2">
                Project Name *
              </label>
              <input
                type="text"
                id="name"
                name="name"
                value={formData.name}
                onChange={handleInputChange}
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                placeholder="Enter project name"
              />
            </div>

            {/* Repository URL */}
            <div>
              <label htmlFor="repo_url" className="block text-sm font-medium text-gray-700 mb-2">
                Repository URL *
              </label>
              <input
                type="url"
                id="repo_url"
                name="repo_url"
                value={formData.repo_url}
                onChange={handleInputChange}
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                placeholder="https://github.com/username/repository"
              />
              <p className="mt-1 text-sm text-gray-500">
                Must be a valid HTTP/HTTPS URL
              </p>
            </div>

            {/* Plan Path */}
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
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                placeholder="docs/plan.md"
              />
              <p className="mt-1 text-sm text-gray-500">
                Path to the plan file within the repository (default: docs/plan.md)
              </p>
            </div>

            {/* Submit Button */}
            <div className="flex gap-3">
              <Button
                type="submit"
                variant="primary"
                size="md"
                disabled={loading}
                className="flex-1"
              >
                <Plus className="w-4 h-4 mr-2" />
                {loading ? 'Creating...' : 'Create Project'}
              </Button>
              <Button
                type="button"
                variant="secondary"
                size="md"
                onClick={() => router.push('/dashboard')}
                disabled={loading}
              >
                Cancel
              </Button>
            </div>
          </form>
        </Card>
      </div>
    </div>
  );
}
