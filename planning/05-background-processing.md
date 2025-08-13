# Phase 5: Background Processing & Automation (Weeks 9-10)

## Overview
This phase implements background processing capabilities using Redis and RQ (Redis Queue) to handle time-consuming operations asynchronously, improving user experience and system scalability.

## Dependencies
- Phase 1: Foundation & Core Infrastructure
- Phase 2: Plan Parsing Engine
- Phase 3: Frontend Foundation
- Phase 4: Skills Extraction System
- Redis must be configured and running
- All processing logic must be functional

## Deliverables
- Redis queue integration
- Background job processing system
- Asynchronous processing pipeline
- Manual refresh system
- Job monitoring and management

---

## Phase 5.1: Redis Queue Integration

### Tasks
- [ ] Set up Redis with RQ (Redis Queue)
- [ ] Create worker process configuration
- [ ] Implement job serialization/deserialization
- [ ] Add job status tracking and monitoring
- [ ] Create job retry and failure handling

### Technical Details
- **Redis**: Redis 7+ for job queue storage
- **RQ**: Python Redis Queue for job processing
- **Worker Processes**: Multiple worker processes for scalability
- **Job Serialization**: JSON serialization for job data
- **Status Tracking**: Real-time job status updates

### Redis Configuration
```python
# redis_config.py
REDIS_CONFIG = {
    'host': 'localhost',
    'port': 6379,
    'db': 0,
    'password': None,
    'ssl': False,
    'connection_pool': {
        'max_connections': 20,
        'retry_on_timeout': True
    }
}

# Queue configuration
QUEUE_CONFIG = {
    'default': 'repotrackr',
    'high': 'repotrackr_high',
    'low': 'repotrackr_low'
}
```

### Worker Configuration
```python
# worker.py
from rq import Worker, Queue, Connection
from redis import Redis

def start_worker():
    redis_conn = Redis(**REDIS_CONFIG)
    with Connection(redis_conn):
        worker = Worker([Queue('repotrackr')])
        worker.work()

# Job functions
def process_project_job(project_id: str) -> dict:
    """Background job to process a project"""
    pass

def extract_skills_job(project_id: str) -> dict:
    """Background job to extract skills"""
    pass
```

### Job Status Tracking
```python
class JobTracker:
    async def create_job(self, job_type: str, project_id: str) -> str
    async def get_job_status(self, job_id: str) -> JobStatus
    async def update_job_status(self, job_id: str, status: str, result: dict)
    async def get_project_jobs(self, project_id: str) -> List[JobStatus]

class JobStatus:
    id: str
    type: str
    status: str  # pending, processing, completed, failed
    project_id: str
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    result: Optional[dict]
    error: Optional[str]
```

### Acceptance Criteria
- [ ] Redis connection established
- [ ] RQ worker processes running
- [ ] Job serialization working
- [ ] Status tracking functional
- [ ] Retry logic implemented

---

## Phase 5.2: Asynchronous Processing

### Tasks
- [ ] Move repository cloning to background jobs
- [ ] Implement plan parsing as async tasks
- [ ] Add skills extraction to background pipeline
- [ ] Create job queue management endpoints
- [ ] Add job progress tracking

### Technical Details
- **Job Types**: Different job types for different operations
- **Priority Queues**: High priority for user-triggered jobs
- **Progress Tracking**: Real-time progress updates
- **Error Handling**: Comprehensive error handling and recovery
- **Resource Management**: Efficient resource usage

### Asynchronous Pipeline
```python
class AsyncProcessingPipeline:
    async def enqueue_project_processing(self, project_id: str, priority: str = 'normal') -> str
    async def enqueue_skills_extraction(self, project_id: str) -> str
    async def process_project_async(self, project_id: str) -> dict
    async def extract_skills_async(self, project_id: str) -> dict

# Job execution functions
def execute_project_processing(project_id: str) -> dict:
    """Execute project processing in background"""
    try:
        # Clone repository
        repo_path = clone_repository(project_id)
        
        # Parse plan file
        tasks = parse_plan_file(repo_path)
        
        # Calculate progress
        progress = calculate_progress(tasks)
        
        # Store results
        store_project_data(project_id, tasks, progress)
        
        return {
            'status': 'success',
            'tasks_count': len(tasks),
            'progress_percentage': progress.percentage
        }
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e)
        }
    finally:
        cleanup_repository(repo_path)

def execute_skills_extraction(project_id: str) -> dict:
    """Execute skills extraction in background"""
    try:
        # Clone repository
        repo_path = clone_repository(project_id)
        
        # Extract skills
        skills = extract_skills_from_repo(repo_path)
        
        # Store skills
        store_project_skills(project_id, skills)
        
        return {
            'status': 'success',
            'skills_count': len(skills)
        }
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e)
        }
    finally:
        cleanup_repository(repo_path)
```

### Job Queue Management
```python
class JobQueueManager:
    async def get_queue_status(self) -> dict
    async def get_worker_status(self) -> List[dict]
    async def clear_failed_jobs(self)
    async def retry_failed_job(self, job_id: str)
    async def cancel_job(self, job_id: str)
```

### Acceptance Criteria
- [ ] Repository cloning moved to background
- [ ] Plan parsing works asynchronously
- [ ] Skills extraction in background
- [ ] Queue management functional
- [ ] Progress tracking working

---

## Phase 5.3: Manual Refresh System

### Tasks
- [ ] Implement `/projects/{id}/refresh` endpoint
- [ ] Add refresh button to frontend
- [ ] Create refresh status indicators
- [ ] Implement refresh rate limiting
- [ ] Add refresh history tracking

### Technical Details
- **Manual Triggers**: User-initiated refresh operations
- **Rate Limiting**: Prevent abuse of refresh endpoints
- **Status Indicators**: Real-time refresh status updates
- **History Tracking**: Track refresh operations over time
- **Priority Handling**: Manual refreshes get higher priority

### Manual Refresh API
```python
@router.post("/projects/{project_id}/refresh")
async def refresh_project(
    project_id: str,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
) -> dict:
    """Trigger manual refresh of project"""
    
    # Check rate limiting
    if not check_rate_limit(current_user.id, "refresh"):
        raise HTTPException(429, "Rate limit exceeded")
    
    # Enqueue refresh job with high priority
    job_id = await enqueue_project_processing(project_id, priority="high")
    
    # Track refresh operation
    await track_refresh_operation(project_id, current_user.id, job_id)
    
    return {
        "job_id": job_id,
        "status": "queued",
        "message": "Project refresh queued successfully"
    }
```

### Frontend Integration
```typescript
// Refresh button component
interface RefreshButtonProps {
  projectId: string;
  onRefresh?: () => void;
  disabled?: boolean;
}

// Refresh status hook
export function useRefreshStatus(projectId: string) {
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [refreshHistory, setRefreshHistory] = useState<RefreshOperation[]>([]);
  
  const triggerRefresh = async () => {
    setIsRefreshing(true);
    try {
      await api.refreshProject(projectId);
      // Poll for status updates
      pollRefreshStatus(projectId);
    } catch (error) {
      console.error('Refresh failed:', error);
    } finally {
      setIsRefreshing(false);
    }
  };
  
  return { isRefreshing, triggerRefresh, refreshHistory };
}
```

### Rate Limiting
```python
class RateLimiter:
    async def check_rate_limit(self, user_id: str, action: str) -> bool
    async def increment_counter(self, user_id: str, action: str)
    async def get_remaining_attempts(self, user_id: str, action: str) -> int

# Rate limit configuration
RATE_LIMITS = {
    "refresh": {
        "max_attempts": 5,
        "window_seconds": 300  # 5 minutes
    },
    "create_project": {
        "max_attempts": 10,
        "window_seconds": 3600  # 1 hour
    }
}
```

### Refresh History Tracking
```python
class RefreshHistory:
    id: str
    project_id: str
    user_id: str
    job_id: str
    status: str
    created_at: datetime
    completed_at: Optional[datetime]
    duration_seconds: Optional[int]
    result: Optional[dict]
```

### Acceptance Criteria
- [ ] Refresh endpoint functional
- [ ] Frontend refresh button working
- [ ] Status indicators implemented
- [ ] Rate limiting working
- [ ] History tracking complete

---

## API Endpoints

### New Endpoints
- `POST /projects/{id}/refresh` - Trigger manual refresh
- `GET /projects/{id}/refresh-status` - Get refresh status
- `GET /projects/{id}/refresh-history` - Get refresh history
- `GET /jobs/{id}/status` - Get job status
- `GET /jobs/queue-status` - Get queue status
- `POST /jobs/{id}/retry` - Retry failed job
- `DELETE /jobs/{id}` - Cancel job

### Job Status Response
```json
{
  "job_id": "uuid",
  "status": "queued|processing|completed|failed",
  "progress": 0.75,
  "result": {
    "tasks_count": 15,
    "progress_percentage": 65.5
  },
  "error": null,
  "created_at": "2024-01-01T12:00:00Z",
  "started_at": "2024-01-01T12:00:05Z",
  "completed_at": null
}
```

---

## Monitoring and Observability

### Job Monitoring
- **Queue Metrics**: Queue length, processing rate
- **Worker Metrics**: Worker count, job success rate
- **Performance Metrics**: Job duration, resource usage
- **Error Tracking**: Failed jobs, error patterns

### Health Checks
```python
@router.get("/health/queue")
async def queue_health_check() -> dict:
    """Check queue health"""
    try:
        redis_conn = Redis(**REDIS_CONFIG)
        redis_conn.ping()
        
        # Check worker status
        workers = Worker.all(connection=redis_conn)
        
        return {
            "status": "healthy",
            "redis_connected": True,
            "worker_count": len(workers),
            "queue_length": len(Queue('repotrackr'))
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }
```

---

## Testing Strategy

### Unit Tests
- Job function tests
- Queue management tests
- Rate limiting tests
- Error handling tests

### Integration Tests
- End-to-end job processing
- Redis integration tests
- Worker process tests

### Load Testing
- Concurrent job processing
- Queue performance under load
- Worker scaling tests

---

## Definition of Done
- [ ] All tasks completed and tested
- [ ] Redis queue integration working
- [ ] Asynchronous processing functional
- [ ] Manual refresh system complete
- [ ] Job monitoring implemented
- [ ] Rate limiting functional
- [ ] Ready for Phase 6 development

---

## Next Phase Dependencies
- Background processing must be stable
- Job queue must be functional
- Manual refresh must work correctly
- Monitoring must be in place
