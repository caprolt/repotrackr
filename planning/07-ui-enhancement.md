# Phase 7: UI Enhancement & Polish (Weeks 13-14)

## Overview
This phase focuses on enhancing the user interface with advanced features, improved user experience, and polished visual design to create a professional and intuitive application.

## Dependencies
- Phase 1: Foundation & Core Infrastructure
- Phase 2: Plan Parsing Engine
- Phase 3: Frontend Foundation
- Phase 4: Skills Extraction System
- Phase 5: Background Processing & Automation
- Phase 6: GitHub Integration & Webhooks
- Frontend foundation must be complete
- All core functionality must be working

## Deliverables
- Project creation flow
- Progress timeline visualization
- Advanced dashboard features
- Stale project management
- Enhanced user experience

---

## Phase 7.1: Project Creation Flow

### Tasks
- [ ] Create project creation form component
- [ ] Add form validation and error handling
- [ ] Implement repository URL validation
- [ ] Add plan file path customization
- [ ] Create onboarding flow for new users

### Technical Details
- **Form Components**: React Hook Form for form management
- **Validation**: Real-time validation with error messages
- **Repository Validation**: Check repository accessibility
- **Customization Options**: Allow plan file path customization
- **Onboarding**: Step-by-step guide for new users

### Project Creation Form
```typescript
// ProjectCreationForm component
interface ProjectCreationFormProps {
  onSubmit: (data: CreateProjectData) => Promise<void>;
  onCancel: () => void;
}

interface CreateProjectData {
  name: string;
  repo_url: string;
  plan_path?: string;
  description?: string;
}

// Form validation schema
const projectSchema = z.object({
  name: z.string().min(1, "Project name is required").max(100),
  repo_url: z.string().url("Invalid repository URL").refine(
    (url) => url.includes("github.com"),
    "Only GitHub repositories are supported"
  ),
  plan_path: z.string().optional(),
  description: z.string().max(500).optional()
});
```

### Repository URL Validation
```typescript
// Repository validation hook
export function useRepositoryValidation() {
  const [isValidating, setIsValidating] = useState(false);
  const [validationResult, setValidationResult] = useState<ValidationResult | null>(null);
  
  const validateRepository = async (repoUrl: string) => {
    setIsValidating(true);
    try {
      const result = await api.validateRepository(repoUrl);
      setValidationResult(result);
      return result.isValid;
    } catch (error) {
      setValidationResult({ isValid: false, error: "Validation failed" });
      return false;
    } finally {
      setIsValidating(false);
    }
  };
  
  return { isValidating, validationResult, validateRepository };
}
```

### Onboarding Flow
```typescript
// Onboarding component
interface OnboardingStep {
  id: string;
  title: string;
  description: string;
  component: React.ComponentType;
  isComplete: boolean;
}

const onboardingSteps: OnboardingStep[] = [
  {
    id: "welcome",
    title: "Welcome to RepoTrackr",
    description: "Let's get you started with automated project tracking",
    component: WelcomeStep,
    isComplete: false
  },
  {
    id: "add-project",
    title: "Add Your First Project",
    description: "Connect a GitHub repository to start tracking",
    component: AddProjectStep,
    isComplete: false
  },
  {
    id: "configure",
    title: "Configure Settings",
    description: "Customize your tracking preferences",
    component: ConfigureStep,
    isComplete: false
  }
];
```

### Acceptance Criteria
- [ ] Project creation form functional
- [ ] Form validation working correctly
- [ ] Repository validation implemented
- [ ] Plan path customization working
- [ ] Onboarding flow complete

---

## Phase 7.2: Progress Timeline Visualization

### Tasks
- [ ] Implement progress timeline chart component
- [ ] Add sparkline charts for quick progress overview
- [ ] Create historical progress comparison
- [ ] Add trend analysis and predictions
- [ ] Implement interactive chart controls

### Technical Details
- **Chart Library**: Recharts or Chart.js for data visualization
- **Timeline Charts**: Line charts showing progress over time
- **Sparklines**: Mini charts for quick overview
- **Trend Analysis**: Simple trend calculations and predictions
- **Interactive Controls**: Zoom, pan, and filter capabilities

### Progress Timeline Component
```typescript
// ProgressTimeline component
interface ProgressTimelineProps {
  projectId: string;
  snapshots: ProgressSnapshot[];
  height?: number;
  showPredictions?: boolean;
}

// Timeline data structure
interface TimelineData {
  date: string;
  percentage: number;
  tasksTotal: number;
  tasksDone: number;
  status: string;
}

// Trend analysis
interface TrendAnalysis {
  trend: 'increasing' | 'decreasing' | 'stable';
  rate: number; // percentage change per day
  prediction: number; // predicted percentage in 7 days
  confidence: number; // confidence in prediction (0-1)
}
```

### Chart Components
```typescript
// ProgressChart component
const ProgressChart: React.FC<ProgressChartProps> = ({ data, height = 300 }) => {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="date" />
        <YAxis domain={[0, 100]} />
        <Tooltip />
        <Line 
          type="monotone" 
          dataKey="percentage" 
          stroke="#8884d8" 
          strokeWidth={2}
        />
      </LineChart>
    </ResponsiveContainer>
  );
};

// SparklineChart component
const SparklineChart: React.FC<SparklineProps> = ({ data, width = 100, height = 30 }) => {
  return (
    <ResponsiveContainer width={width} height={height}>
      <LineChart data={data}>
        <Line 
          type="monotone" 
          dataKey="percentage" 
          stroke="#8884d8" 
          strokeWidth={1}
          dot={false}
        />
      </LineChart>
    </ResponsiveContainer>
  );
};
```

### Trend Analysis
```typescript
// Trend calculation
function calculateTrend(snapshots: ProgressSnapshot[]): TrendAnalysis {
  if (snapshots.length < 2) {
    return { trend: 'stable', rate: 0, prediction: 0, confidence: 0 };
  }
  
  const recent = snapshots.slice(-7); // Last 7 snapshots
  const first = recent[0].percentage_complete;
  const last = recent[recent.length - 1].percentage_complete;
  const rate = (last - first) / recent.length;
  
  const trend = rate > 0.5 ? 'increasing' : rate < -0.5 ? 'decreasing' : 'stable';
  const prediction = Math.min(100, Math.max(0, last + (rate * 7)));
  const confidence = Math.min(1, recent.length / 7);
  
  return { trend, rate, prediction, confidence };
}
```

### Acceptance Criteria
- [ ] Timeline charts implemented
- [ ] Sparkline charts working
- [ ] Historical comparison functional
- [ ] Trend analysis accurate
- [ ] Interactive controls working

---

## Phase 7.3: Advanced Dashboard Features

### Tasks
- [ ] Add project search and filtering
- [ ] Implement project sorting options
- [ ] Create project status overview cards
- [ ] Add bulk operations for multiple projects
- [ ] Implement dashboard customization options

### Technical Details
- **Search & Filter**: Real-time search with multiple filter criteria
- **Sorting**: Multiple sorting options with persistence
- **Overview Cards**: Summary statistics and quick actions
- **Bulk Operations**: Select and operate on multiple projects
- **Customization**: User preferences for dashboard layout

### Search and Filter System
```typescript
// Search and filter hook
export function useProjectFilters() {
  const [filters, setFilters] = useState<ProjectFilters>({
    search: '',
    status: 'all',
    skills: [],
    dateRange: 'all'
  });
  
  const filteredProjects = useMemo(() => {
    return projects.filter(project => {
      // Search filter
      if (filters.search && !project.name.toLowerCase().includes(filters.search.toLowerCase())) {
        return false;
      }
      
      // Status filter
      if (filters.status !== 'all' && project.status !== filters.status) {
        return false;
      }
      
      // Skills filter
      if (filters.skills.length > 0) {
        const projectSkills = project.skills?.map(s => s.name) || [];
        if (!filters.skills.some(skill => projectSkills.includes(skill))) {
          return false;
        }
      }
      
      return true;
    });
  }, [projects, filters]);
  
  return { filters, setFilters, filteredProjects };
}
```

### Sorting System
```typescript
// Sort options
const sortOptions = [
  { value: 'name', label: 'Name (A-Z)' },
  { value: 'name-desc', label: 'Name (Z-A)' },
  { value: 'status', label: 'Status' },
  { value: 'progress', label: 'Progress' },
  { value: 'updated', label: 'Last Updated' },
  { value: 'created', label: 'Date Created' }
];

// Sort function
function sortProjects(projects: Project[], sortBy: string): Project[] {
  return [...projects].sort((a, b) => {
    switch (sortBy) {
      case 'name':
        return a.name.localeCompare(b.name);
      case 'name-desc':
        return b.name.localeCompare(a.name);
      case 'status':
        return a.status.localeCompare(b.status);
      case 'progress':
        return (b.progress_percentage || 0) - (a.progress_percentage || 0);
      case 'updated':
        return new Date(b.last_updated).getTime() - new Date(a.last_updated).getTime();
      case 'created':
        return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
      default:
        return 0;
    }
  });
}
```

### Bulk Operations
```typescript
// Bulk operations component
interface BulkOperationsProps {
  selectedProjects: string[];
  onRefresh: (projectIds: string[]) => void;
  onDelete: (projectIds: string[]) => void;
  onExport: (projectIds: string[]) => void;
}

// Bulk operations hook
export function useBulkOperations() {
  const [selectedProjects, setSelectedProjects] = useState<string[]>([]);
  
  const selectAll = () => {
    setSelectedProjects(projects.map(p => p.id));
  };
  
  const clearSelection = () => {
    setSelectedProjects([]);
  };
  
  const toggleProject = (projectId: string) => {
    setSelectedProjects(prev => 
      prev.includes(projectId) 
        ? prev.filter(id => id !== projectId)
        : [...prev, projectId]
    );
  };
  
  return {
    selectedProjects,
    selectAll,
    clearSelection,
    toggleProject,
    isSelected: (projectId: string) => selectedProjects.includes(projectId)
  };
}
```

### Acceptance Criteria
- [ ] Search and filtering functional
- [ ] Sorting options working
- [ ] Overview cards implemented
- [ ] Bulk operations working
- [ ] Customization options available

---

## Phase 7.4: Stale Project Management

### Tasks
- [ ] Add stale project detection and highlighting
- [ ] Implement stale project notifications
- [ ] Create project health indicators
- [ ] Add project archiving functionality
- [ ] Implement project activity tracking

### Technical Details
- **Stale Detection**: Configurable thresholds for stale projects
- **Notifications**: In-app and email notifications for stale projects
- **Health Indicators**: Visual indicators of project health
- **Archiving**: Soft delete with recovery options
- **Activity Tracking**: Track project activity over time

### Stale Project Detection
```typescript
// Stale project detection
interface StaleProjectConfig {
  daysThreshold: number;
  enableNotifications: boolean;
  autoArchive: boolean;
  archiveAfterDays: number;
}

function isProjectStale(project: Project, config: StaleProjectConfig): boolean {
  const lastUpdate = new Date(project.last_updated);
  const daysSinceUpdate = (Date.now() - lastUpdate.getTime()) / (1000 * 60 * 60 * 24);
  return daysSinceUpdate > config.daysThreshold;
}

function getProjectHealth(project: Project): 'healthy' | 'warning' | 'stale' | 'archived' {
  if (project.archived) return 'archived';
  
  const daysSinceUpdate = getDaysSinceUpdate(project.last_updated);
  
  if (daysSinceUpdate > 30) return 'stale';
  if (daysSinceUpdate > 7) return 'warning';
  return 'healthy';
}
```

### Health Indicators
```typescript
// Health indicator component
interface HealthIndicatorProps {
  health: 'healthy' | 'warning' | 'stale' | 'archived';
  daysSinceUpdate: number;
  showDetails?: boolean;
}

const HealthIndicator: React.FC<HealthIndicatorProps> = ({ 
  health, 
  daysSinceUpdate, 
  showDetails = false 
}) => {
  const getHealthColor = (health: string) => {
    switch (health) {
      case 'healthy': return 'text-green-500';
      case 'warning': return 'text-yellow-500';
      case 'stale': return 'text-red-500';
      case 'archived': return 'text-gray-500';
      default: return 'text-gray-500';
    }
  };
  
  const getHealthIcon = (health: string) => {
    switch (health) {
      case 'healthy': return '✓';
      case 'warning': return '⚠';
      case 'stale': return '⚠';
      case 'archived': return '📁';
      default: return '?';
    }
  };
  
  return (
    <div className={`flex items-center space-x-1 ${getHealthColor(health)}`}>
      <span className="text-sm">{getHealthIcon(health)}</span>
      {showDetails && (
        <span className="text-xs">
          {daysSinceUpdate} days ago
        </span>
      )}
    </div>
  );
};
```

### Project Archiving
```typescript
// Archive functionality
interface ArchiveProjectData {
  projectId: string;
  reason?: string;
  archiveDate: Date;
}

async function archiveProject(data: ArchiveProjectData): Promise<void> {
  await api.archiveProject(data.projectId, {
    reason: data.reason,
    archived_at: data.archiveDate.toISOString()
  });
}

async function restoreProject(projectId: string): Promise<void> {
  await api.restoreProject(projectId);
}

// Archive management component
const ArchiveManager: React.FC = () => {
  const [archivedProjects, setArchivedProjects] = useState<Project[]>([]);
  
  const handleRestore = async (projectId: string) => {
    await restoreProject(projectId);
    // Refresh archived projects list
    const updated = await api.getArchivedProjects();
    setArchivedProjects(updated);
  };
  
  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold">Archived Projects</h3>
      {archivedProjects.map(project => (
        <div key={project.id} className="flex items-center justify-between p-4 border rounded">
          <div>
            <h4 className="font-medium">{project.name}</h4>
            <p className="text-sm text-gray-500">
              Archived {formatDate(project.archived_at)}
            </p>
          </div>
          <button
            onClick={() => handleRestore(project.id)}
            className="px-3 py-1 text-sm bg-blue-500 text-white rounded hover:bg-blue-600"
          >
            Restore
          </button>
        </div>
      ))}
    </div>
  );
};
```

### Acceptance Criteria
- [ ] Stale detection working
- [ ] Notifications implemented
- [ ] Health indicators functional
- [ ] Archiving system complete
- [ ] Activity tracking working

---

## API Endpoints

### New Endpoints
- `POST /projects` - Create new project (enhanced)
- `GET /projects/search` - Search projects
- `GET /projects/archived` - Get archived projects
- `POST /projects/{id}/archive` - Archive project
- `POST /projects/{id}/restore` - Restore project
- `GET /dashboard/stats` - Get dashboard statistics
- `GET /dashboard/timeline/{project_id}` - Get project timeline

### Dashboard Statistics Response
```json
{
  "total_projects": 25,
  "active_projects": 20,
  "stale_projects": 3,
  "archived_projects": 2,
  "average_progress": 65.5,
  "recent_activity": [
    {
      "project_id": "uuid",
      "action": "updated",
      "timestamp": "2024-01-01T12:00:00Z"
    }
  ]
}
```

---

## Testing Strategy

### Unit Tests
- Form validation tests
- Chart component tests
- Filter and sort tests
- Health indicator tests

### Integration Tests
- End-to-end project creation
- Dashboard functionality tests
- Archive/restore tests

### User Testing
- Usability testing with real users
- Accessibility testing
- Performance testing

---

## Definition of Done
- [ ] All tasks completed and tested
- [ ] Project creation flow polished
- [ ] Timeline visualization working
- [ ] Advanced dashboard features complete
- [ ] Stale project management functional
- [ ] User experience enhanced
- [ ] Ready for Phase 8 development

---

## Next Phase Dependencies
- UI enhancement must be complete
- User experience must be polished
- All interactive features must work
- Performance must be optimized
