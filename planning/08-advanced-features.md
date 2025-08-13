# Phase 8: Advanced Features & Optimization (Weeks 15-16)

## Overview
This phase implements advanced features including multi-repo project support, GitHub Issues/Projects integration, performance optimizations, and analytics capabilities to enhance the system's functionality and scalability.

## Dependencies
- Phase 1: Foundation & Core Infrastructure
- Phase 2: Plan Parsing Engine
- Phase 3: Frontend Foundation
- Phase 4: Skills Extraction System
- Phase 5: Background Processing & Automation
- Phase 6: GitHub Integration & Webhooks
- Phase 7: UI Enhancement & Polish
- All previous phases must be complete and stable

## Deliverables
- Multi-repo project support
- GitHub Issues/Projects integration
- Performance optimizations
- Analytics and insights
- Advanced reporting features

---

## Phase 8.1: Multi-repo Project Support

### Tasks
- [ ] Extend project model for multiple repositories
- [ ] Implement cross-repo progress aggregation
- [ ] Create unified project view for multi-repo projects
- [ ] Add repository relationship management
- [ ] Implement cross-repo skill consolidation

### Technical Details
- **Multi-repo Projects**: Support projects spanning multiple repositories
- **Progress Aggregation**: Combine progress from multiple repos
- **Unified View**: Single interface for multi-repo projects
- **Relationship Management**: Define relationships between repositories
- **Skill Consolidation**: Merge skills from multiple repos

### Database Schema Extension
```sql
-- Add repository table for multi-repo support
CREATE TABLE repositories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    repo_url VARCHAR NOT NULL,
    repo_name VARCHAR NOT NULL,
    branch VARCHAR DEFAULT 'main',
    plan_path VARCHAR DEFAULT 'docs/plan.md',
    weight DECIMAL DEFAULT 1.0, -- Contribution weight to overall progress
    is_primary BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Add repository relationships
CREATE TABLE repository_relationships (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_repo_id UUID REFERENCES repositories(id) ON DELETE CASCADE,
    target_repo_id UUID REFERENCES repositories(id) ON DELETE CASCADE,
    relationship_type VARCHAR NOT NULL, -- 'depends_on', 'related_to', 'submodule'
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Multi-repo Project Model
```python
class MultiRepoProject:
    id: str
    name: str
    repositories: List[Repository]
    aggregated_progress: ProgressSnapshot
    cross_repo_skills: List[Skill]
    
class Repository:
    id: str
    project_id: str
    repo_url: str
    repo_name: str
    branch: str
    plan_path: str
    weight: float
    is_primary: bool
    progress: ProgressSnapshot
    skills: List[Skill]

class CrossRepoProgressAggregator:
    async def aggregate_progress(self, project_id: str) -> ProgressSnapshot:
        """Aggregate progress from multiple repositories"""
        repositories = await get_project_repositories(project_id)
        
        total_weight = sum(repo.weight for repo in repositories)
        weighted_progress = 0.0
        
        for repo in repositories:
            if repo.progress:
                weighted_progress += (repo.progress.percentage_complete * repo.weight)
        
        aggregated_percentage = weighted_progress / total_weight if total_weight > 0 else 0
        
        return ProgressSnapshot(
            percentage_complete=aggregated_percentage,
            # Aggregate other metrics...
        )
```

### Frontend Multi-repo Support
```typescript
// Multi-repo project interface
interface MultiRepoProject extends Project {
  repositories: Repository[];
  aggregatedProgress: ProgressSnapshot;
  crossRepoSkills: Skill[];
}

// Repository component
interface RepositoryCardProps {
  repository: Repository;
  onRefresh: (repoId: string) => void;
  onConfigure: (repoId: string) => void;
}

// Multi-repo project view
const MultiRepoProjectView: React.FC<{ project: MultiRepoProject }> = ({ project }) => {
  return (
    <div className="space-y-6">
      {/* Aggregated progress */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-semibold mb-4">Overall Progress</h3>
        <ProgressVisualization snapshot={project.aggregatedProgress} />
      </div>
      
      {/* Repository list */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold">Repositories</h3>
        {project.repositories.map(repo => (
          <RepositoryCard 
            key={repo.id} 
            repository={repo} 
            onRefresh={handleRefresh}
            onConfigure={handleConfigure}
          />
        ))}
      </div>
      
      {/* Cross-repo skills */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-semibold mb-4">Technologies Used</h3>
        <SkillsSection skills={project.crossRepoSkills} />
      </div>
    </div>
  );
};
```

### Acceptance Criteria
- [ ] Multi-repo projects supported
- [ ] Progress aggregation working
- [ ] Unified view functional
- [ ] Repository relationships managed
- [ ] Cross-repo skills consolidated

---

## Phase 8.2: GitHub Issues/Projects Integration

### Tasks
- [ ] Add GitHub Issues parser for task extraction
- [ ] Implement GitHub Projects board integration
- [ ] Create issue-to-task mapping logic
- [ ] Add issue status synchronization
- [ ] Implement issue-based progress tracking

### Technical Details
- **Issues Parser**: Extract tasks from GitHub Issues
- **Projects Integration**: Connect to GitHub Projects boards
- **Status Sync**: Synchronize issue status with task status
- **Progress Tracking**: Calculate progress based on issue completion
- **Mapping Logic**: Map issues to tasks with confidence scoring

### GitHub Issues Parser
```python
class GitHubIssuesParser:
    async def parse_issues_from_repo(self, repo_url: str, installation_token: str) -> List[Task]:
        """Parse GitHub Issues and convert to tasks"""
        
        # Get issues from GitHub API
        issues = await get_github_issues(repo_url, installation_token)
        
        tasks = []
        for issue in issues:
            task = await self.convert_issue_to_task(issue)
            tasks.append(task)
        
        return tasks
    
    async def convert_issue_to_task(self, issue: dict) -> Task:
        """Convert GitHub Issue to Task"""
        
        # Map issue state to task status
        status_mapping = {
            'open': 'todo',
            'closed': 'done',
            'in_progress': 'doing'
        }
        
        # Extract labels for additional context
        labels = [label['name'] for label in issue.get('labels', [])]
        
        # Determine status based on issue state and labels
        status = status_mapping.get(issue['state'], 'todo')
        if 'blocked' in labels:
            status = 'blocked'
        elif 'in-progress' in labels:
            status = 'doing'
        
        return Task(
            title=issue['title'],
            status=status,
            description=issue.get('body', ''),
            issue_number=issue['number'],
            issue_url=issue['html_url'],
            created_at=issue['created_at'],
            updated_at=issue['updated_at']
        )
```

### GitHub Projects Integration
```python
class GitHubProjectsIntegration:
    async def get_project_board(self, repo_url: str, board_name: str, installation_token: str) -> dict:
        """Get GitHub Projects board data"""
        
        # Get project board from GitHub API
        board = await get_github_project_board(repo_url, board_name, installation_token)
        
        # Get columns and cards
        columns = await get_project_columns(board['id'], installation_token)
        
        for column in columns:
            cards = await get_column_cards(column['id'], installation_token)
            column['cards'] = cards
        
        return {
            'board': board,
            'columns': columns
        }
    
    async def sync_project_board(self, project_id: str, board_data: dict) -> None:
        """Sync GitHub Projects board with local tasks"""
        
        # Map columns to task statuses
        column_mapping = {
            'To Do': 'todo',
            'In Progress': 'doing',
            'Done': 'done',
            'Blocked': 'blocked'
        }
        
        for column in board_data['columns']:
            status = column_mapping.get(column['name'], 'todo')
            
            for card in column['cards']:
                # Update task status based on card position
                await update_task_status_by_issue(
                    project_id, 
                    card['content_url'], 
                    status
                )
```

### Issue-to-Task Mapping
```python
class IssueTaskMapper:
    async def map_issues_to_tasks(self, issues: List[dict], existing_tasks: List[Task]) -> List[TaskMapping]:
        """Map GitHub Issues to existing tasks"""
        
        mappings = []
        
        for issue in issues:
            # Find best matching task
            best_match = await self.find_best_task_match(issue, existing_tasks)
            
            if best_match and best_match.confidence > 0.7:
                mappings.append(TaskMapping(
                    issue_id=issue['id'],
                    task_id=best_match.task_id,
                    confidence=best_match.confidence,
                    mapping_type='automatic'
                ))
            else:
                # Create new task from issue
                new_task = await self.create_task_from_issue(issue)
                mappings.append(TaskMapping(
                    issue_id=issue['id'],
                    task_id=new_task.id,
                    confidence=1.0,
                    mapping_type='new_task'
                ))
        
        return mappings
    
    async def find_best_task_match(self, issue: dict, tasks: List[Task]) -> Optional[TaskMatch]:
        """Find best matching task for an issue using fuzzy matching"""
        
        best_match = None
        best_score = 0
        
        for task in tasks:
            # Calculate similarity score
            title_similarity = calculate_similarity(issue['title'], task.title)
            
            if title_similarity > best_score and title_similarity > 0.7:
                best_score = title_similarity
                best_match = TaskMatch(
                    task_id=task.id,
                    confidence=title_similarity
                )
        
        return best_match
```

### Acceptance Criteria
- [ ] Issues parser functional
- [ ] Projects integration working
- [ ] Issue-to-task mapping accurate
- [ ] Status synchronization working
- [ ] Issue-based progress tracking complete

---

## Phase 8.3: Performance Optimization

### Tasks
- [ ] Implement database query optimization
- [ ] Add Redis caching for frequent queries
- [ ] Optimize frontend bundle size
- [ ] Implement lazy loading for large datasets
- [ ] Add database indexing for performance

### Technical Details
- **Query Optimization**: Optimize database queries for better performance
- **Caching Strategy**: Implement intelligent caching for frequently accessed data
- **Bundle Optimization**: Reduce frontend bundle size and improve loading times
- **Lazy Loading**: Load data on demand to improve initial page load
- **Database Indexing**: Add appropriate indexes for better query performance

### Database Query Optimization
```python
# Optimized queries with proper joins and indexing
class OptimizedProjectQueries:
    async def get_projects_with_progress(self, user_id: str, limit: int = 20, offset: int = 0) -> List[ProjectWithProgress]:
        """Get projects with latest progress in single query"""
        
        query = """
        SELECT 
            p.id,
            p.name,
            p.repo_url,
            p.status,
            p.last_updated,
            p.created_at,
            ps.percentage_complete,
            ps.tasks_total,
            ps.tasks_done,
            ps.tasks_doing,
            ps.tasks_todo,
            ps.tasks_blocked
        FROM projects p
        LEFT JOIN LATERAL (
            SELECT * FROM progress_snapshots ps2
            WHERE ps2.project_id = p.id
            ORDER BY ps2.created_at DESC
            LIMIT 1
        ) ps ON true
        WHERE p.user_id = :user_id
        ORDER BY p.last_updated DESC
        LIMIT :limit OFFSET :offset
        """
        
        return await db.fetch_all(query, {
            "user_id": user_id,
            "limit": limit,
            "offset": offset
        })

# Database indexes for performance
CREATE INDEX idx_projects_user_id ON projects(user_id);
CREATE INDEX idx_projects_last_updated ON projects(last_updated DESC);
CREATE INDEX idx_progress_snapshots_project_created ON progress_snapshots(project_id, created_at DESC);
CREATE INDEX idx_tasks_project_status ON tasks(project_id, status);
CREATE INDEX idx_skills_project_category ON skills(project_id, category);
```

### Redis Caching Strategy
```python
class CacheManager:
    def __init__(self, redis_client: Redis):
        self.redis = redis_client
        self.default_ttl = 300  # 5 minutes
    
    async def get_cached_projects(self, user_id: str) -> Optional[List[Project]]:
        """Get cached projects for user"""
        cache_key = f"projects:{user_id}"
        cached_data = await self.redis.get(cache_key)
        
        if cached_data:
            return json.loads(cached_data)
        return None
    
    async def cache_projects(self, user_id: str, projects: List[Project], ttl: int = None) -> None:
        """Cache projects for user"""
        cache_key = f"projects:{user_id}"
        ttl = ttl or self.default_ttl
        
        await self.redis.setex(
            cache_key,
            ttl,
            json.dumps([p.dict() for p in projects])
        )
    
    async def invalidate_user_cache(self, user_id: str) -> None:
        """Invalidate all cache for user"""
        pattern = f"projects:{user_id}"
        keys = await self.redis.keys(pattern)
        
        if keys:
            await self.redis.delete(*keys)

# Cache decorator for API endpoints
def cache_response(ttl: int = 300):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Try to get from cache
            cached_result = await cache_manager.redis.get(cache_key)
            if cached_result:
                return json.loads(cached_result)
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            await cache_manager.redis.setex(
                cache_key,
                ttl,
                json.dumps(result)
            )
            
            return result
        return wrapper
    return decorator
```

### Frontend Bundle Optimization
```typescript
// Dynamic imports for code splitting
const ProjectDetail = lazy(() => import('./pages/ProjectDetail'));
const Analytics = lazy(() => import('./pages/Analytics'));
const Settings = lazy(() => import('./pages/Settings'));

// Bundle analysis and optimization
// webpack.config.js
module.exports = {
  optimization: {
    splitChunks: {
      chunks: 'all',
      cacheGroups: {
        vendor: {
          test: /[\\/]node_modules[\\/]/,
          name: 'vendors',
          chunks: 'all',
        },
        common: {
          name: 'common',
          minChunks: 2,
          chunks: 'all',
          enforce: true,
        },
      },
    },
  },
};

// Lazy loading for large datasets
const useLazyProjects = (page: number, pageSize: number) => {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(false);
  const [hasMore, setHasMore] = useState(true);
  
  const loadMore = useCallback(async () => {
    if (loading || !hasMore) return;
    
    setLoading(true);
    try {
      const newProjects = await api.getProjects(page, pageSize);
      setProjects(prev => [...prev, ...newProjects]);
      setHasMore(newProjects.length === pageSize);
    } catch (error) {
      console.error('Failed to load projects:', error);
    } finally {
      setLoading(false);
    }
  }, [page, pageSize, loading, hasMore]);
  
  return { projects, loading, hasMore, loadMore };
};
```

### Acceptance Criteria
- [ ] Database queries optimized
- [ ] Redis caching implemented
- [ ] Frontend bundle optimized
- [ ] Lazy loading functional
- [ ] Database indexes added

---

## Phase 8.4: Analytics & Insights

### Tasks
- [ ] Create project analytics dashboard
- [ ] Implement skill usage analytics
- [ ] Add progress trend analysis
- [ ] Create project comparison features
- [ ] Implement export functionality

### Technical Details
- **Analytics Dashboard**: Comprehensive analytics and insights
- **Skill Analytics**: Track skill usage and trends
- **Progress Analysis**: Advanced progress trend analysis
- **Project Comparison**: Compare projects and performance
- **Export Features**: Export data in various formats

### Analytics Dashboard
```typescript
// Analytics dashboard component
interface AnalyticsDashboardProps {
  timeRange: '7d' | '30d' | '90d' | '1y';
  projects: Project[];
}

const AnalyticsDashboard: React.FC<AnalyticsDashboardProps> = ({ timeRange, projects }) => {
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);
  
  useEffect(() => {
    loadAnalytics(timeRange);
  }, [timeRange]);
  
  return (
    <div className="space-y-6">
      {/* Overview metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <MetricCard
          title="Total Projects"
          value={analytics?.totalProjects || 0}
          change={analytics?.projectGrowth || 0}
        />
        <MetricCard
          title="Average Progress"
          value={`${analytics?.averageProgress || 0}%`}
          change={analytics?.progressGrowth || 0}
        />
        <MetricCard
          title="Active Projects"
          value={analytics?.activeProjects || 0}
          change={analytics?.activityGrowth || 0}
        />
        <MetricCard
          title="Skills Used"
          value={analytics?.uniqueSkills || 0}
          change={analytics?.skillsGrowth || 0}
        />
      </div>
      
      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ProgressTrendChart data={analytics?.progressTrends} />
        <SkillsUsageChart data={analytics?.skillsUsage} />
      </div>
      
      {/* Project comparison */}
      <ProjectComparisonTable projects={projects} />
    </div>
  );
};
```

### Skill Usage Analytics
```python
class SkillAnalytics:
    async def get_skill_usage_stats(self, time_range: str) -> dict:
        """Get skill usage statistics"""
        
        query = """
        SELECT 
            s.name,
            s.category,
            COUNT(DISTINCT s.project_id) as project_count,
            AVG(s.confidence) as avg_confidence,
            MAX(s.created_at) as last_used
        FROM skills s
        JOIN projects p ON s.project_id = p.id
        WHERE s.created_at >= NOW() - INTERVAL :time_range
        GROUP BY s.name, s.category
        ORDER BY project_count DESC
        """
        
        results = await db.fetch_all(query, {"time_range": time_range})
        
        return {
            "skills": results,
            "categories": await self.get_category_stats(results),
            "trends": await self.get_skill_trends(time_range)
        }
    
    async def get_skill_trends(self, time_range: str) -> List[dict]:
        """Get skill usage trends over time"""
        
        query = """
        SELECT 
            DATE(s.created_at) as date,
            s.name,
            COUNT(*) as usage_count
        FROM skills s
        WHERE s.created_at >= NOW() - INTERVAL :time_range
        GROUP BY DATE(s.created_at), s.name
        ORDER BY date DESC, usage_count DESC
        """
        
        return await db.fetch_all(query, {"time_range": time_range})
```

### Progress Trend Analysis
```python
class ProgressAnalytics:
    async def analyze_progress_trends(self, project_id: str, days: int = 30) -> dict:
        """Analyze progress trends for a project"""
        
        snapshots = await self.get_project_snapshots(project_id, days)
        
        if not snapshots:
            return {"trend": "stable", "rate": 0, "prediction": 0}
        
        # Calculate trend
        trend = self.calculate_trend(snapshots)
        
        # Calculate velocity (progress per day)
        velocity = self.calculate_velocity(snapshots)
        
        # Predict completion
        prediction = self.predict_completion(snapshots, velocity)
        
        return {
            "trend": trend,
            "velocity": velocity,
            "prediction": prediction,
            "snapshots": snapshots
        }
    
    def calculate_trend(self, snapshots: List[ProgressSnapshot]) -> str:
        """Calculate progress trend"""
        
        if len(snapshots) < 2:
            return "stable"
        
        recent = snapshots[-7:]  # Last 7 snapshots
        first = recent[0].percentage_complete
        last = recent[-1].percentage_complete
        
        change = last - first
        if change > 5:
            return "increasing"
        elif change < -5:
            return "decreasing"
        else:
            return "stable"
```

### Export Functionality
```python
class DataExporter:
    async def export_project_data(self, project_id: str, format: str = 'json') -> bytes:
        """Export project data in specified format"""
        
        project_data = await self.get_project_export_data(project_id)
        
        if format == 'json':
            return json.dumps(project_data, indent=2).encode()
        elif format == 'csv':
            return self.convert_to_csv(project_data)
        elif format == 'excel':
            return self.convert_to_excel(project_data)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    async def export_analytics_report(self, time_range: str, format: str = 'pdf') -> bytes:
        """Export analytics report"""
        
        analytics_data = await self.get_analytics_data(time_range)
        
        if format == 'pdf':
            return self.generate_pdf_report(analytics_data)
        elif format == 'excel':
            return self.generate_excel_report(analytics_data)
        else:
            raise ValueError(f"Unsupported format: {format}")
```

### Acceptance Criteria
- [ ] Analytics dashboard functional
- [ ] Skill analytics working
- [ ] Progress analysis accurate
- [ ] Project comparison features complete
- [ ] Export functionality implemented

---

## API Endpoints

### New Endpoints
- `GET /analytics/overview` - Get analytics overview
- `GET /analytics/skills` - Get skill usage analytics
- `GET /analytics/progress/{project_id}` - Get progress analytics
- `GET /projects/compare` - Compare projects
- `POST /export/project/{project_id}` - Export project data
- `POST /export/analytics` - Export analytics report
- `GET /projects/multi-repo` - Get multi-repo projects
- `POST /projects/multi-repo` - Create multi-repo project
- `GET /github/issues/{project_id}` - Get GitHub issues
- `POST /github/issues/sync` - Sync GitHub issues

---

## Testing Strategy

### Unit Tests
- Analytics calculation tests
- Export functionality tests
- Multi-repo logic tests
- Performance optimization tests

### Integration Tests
- End-to-end analytics pipeline
- Multi-repo project workflows
- GitHub integration tests
- Export functionality tests

### Performance Tests
- Load testing with large datasets
- Cache performance tests
- Database query performance tests
- Frontend bundle size tests

---

## Definition of Done
- [ ] All tasks completed and tested
- [ ] Multi-repo support functional
- [ ] GitHub integration complete
- [ ] Performance optimizations implemented
- [ ] Analytics features working
- [ ] Export functionality complete
- [ ] Ready for Phase 9 development

---

## Next Phase Dependencies
- Advanced features must be stable
- Performance optimizations must be effective
- Analytics must be accurate
- Multi-repo support must be reliable
