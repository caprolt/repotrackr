# Phase 5: Background Processing & Automation (Weeks 9-10)

## Overview
This phase implements background processing capabilities using FastAPI's built-in BackgroundTasks and database-based job tracking to handle time-consuming operations asynchronously, improving user experience without requiring additional infrastructure costs.

## Dependencies
- Phase 1: Foundation & Core Infrastructure
- Phase 2: Plan Parsing Engine
- Phase 3: Frontend Foundation
- Phase 4: Skills Extraction System
- All processing logic must be functional

## Deliverables
- Database-based job tracking system
- Background task processing system
- Asynchronous processing pipeline
- Manual refresh system
- Job monitoring and management

---

## Phase 5.1: Database-Based Job Tracking

### Tasks
- [ ] Create job tracking database schema
- [ ] Implement job status management
- [ ] Add job retry and failure handling
- [ ] Create job monitoring endpoints
- [ ] Implement job cleanup procedures

### Technical Details
- **Database**: PostgreSQL for job storage (Supabase cloud or local PostgreSQL)
- **Background Tasks**: FastAPI's built-in BackgroundTasks for immediate operations
- **Job Tracking**: Database table for job status and results
- **Status Updates**: Real-time job status updates via database
- **Cleanup**: Automatic cleanup of old job records

### Database Schema
```sql
-- Job tracking table
CREATE TABLE jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type VARCHAR(50) NOT NULL, -- 'project_processing', 'skills_extraction', 'refresh'
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    status VARCHAR(20) NOT NULL DEFAULT 'pending', -- pending, processing, completed, failed
    priority VARCHAR(20) DEFAULT 'normal', -- low, normal, high
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    result JSONB,
    error TEXT,
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3
);

-- Indexes for performance
CREATE INDEX idx_jobs_project_id ON jobs(project_id);
CREATE INDEX idx_jobs_status ON jobs(status);
CREATE INDEX idx_jobs_created_at ON jobs(created_at);
```

### Job Management System
```python
# job_manager.py
from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import BackgroundTasks
from app.models import Job

class JobManager:
    def __init__(self, db: Session):
        self.db = db
    
    async def create_job(
        self, 
        job_type: str, 
        project_id: UUID, 
        user_id: UUID,
        priority: str = 'normal'
    ) -> UUID:
        """Create a new job record"""
        job = Job(
            type=job_type,
            project_id=project_id,
            user_id=user_id,
            priority=priority,
            status='pending'
        )
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        return job.id
    
    async def update_job_status(
        self, 
        job_id: UUID, 
        status: str, 
        result: Optional[Dict] = None,
        error: Optional[str] = None
    ):
        """Update job status and results"""
        job = self.db.query(Job).filter(Job.id == job_id).first()
        if job:
            job.status = status
            if status == 'processing' and not job.started_at:
                job.started_at = datetime.utcnow()
            elif status in ['completed', 'failed']:
                job.completed_at = datetime.utcnow()
            
            if result:
                job.result = result
            if error:
                job.error = error
            
            self.db.commit()
    
    async def get_job_status(self, job_id: UUID) -> Optional[Dict]:
        """Get job status and details"""
        job = self.db.query(Job).filter(Job.id == job_id).first()
        if job:
            return {
                'id': str(job.id),
                'type': job.type,
                'status': job.status,
                'project_id': str(job.project_id),
                'created_at': job.created_at.isoformat(),
                'started_at': job.started_at.isoformat() if job.started_at else None,
                'completed_at': job.completed_at.isoformat() if job.completed_at else None,
                'result': job.result,
                'error': job.error,
                'retry_count': job.retry_count
            }
        return None
    
    async def get_project_jobs(self, project_id: UUID) -> List[Dict]:
        """Get all jobs for a project"""
        jobs = self.db.query(Job).filter(Job.project_id == project_id).order_by(Job.created_at.desc()).all()
        return [await self.get_job_status(job.id) for job in jobs]
```

### Acceptance Criteria
- [ ] Job tracking database schema created
- [ ] Job management system functional
- [ ] Status updates working
- [ ] Job retrieval endpoints working
- [ ] Cleanup procedures implemented

---

## Phase 5.2: Asynchronous Processing

### Tasks
- [ ] Implement background task processing
- [ ] Add project processing as background tasks
- [ ] Create skills extraction background jobs
- [ ] Implement job queue management
- [ ] Add progress tracking

### Technical Details
- **Background Tasks**: FastAPI's BackgroundTasks for immediate operations
- **Long-running Jobs**: Database-based job tracking with status polling
- **Progress Tracking**: Real-time progress updates via database
- **Error Handling**: Comprehensive error handling and retry logic
- **Resource Management**: Efficient resource usage and cleanup

### Background Processing Pipeline
```python
# background_processor.py
from fastapi import BackgroundTasks
from typing import Dict, Any
import asyncio
from datetime import datetime, timedelta
from uuid import UUID
from sqlalchemy.orm import Session
from app.models import Job
from app.database import get_db
from app.core.config import REDIS_CONFIG # Assuming REDIS_CONFIG is still needed for repository cloning
from app.utils.repository_utils import clone_repository, parse_plan_file, calculate_progress, store_project_data, extract_skills_from_repo, store_project_skills, cleanup_repository
from app.api.deps import get_current_user
from app.api.router import router
from fastapi import Depends, HTTPException

class BackgroundProcessor:
    def __init__(self, db: Session, job_manager: JobManager):
        self.db = db
        self.job_manager = job_manager
    
    async def process_project_background(
        self, 
        background_tasks: BackgroundTasks,
        project_id: UUID,
        user_id: UUID
    ) -> UUID:
        """Start project processing in background"""
        # Create job record
        job_id = await self.job_manager.create_job(
            'project_processing', 
            project_id, 
            user_id
        )
        
        # Add to background tasks
        background_tasks.add_task(
            self._execute_project_processing,
            job_id,
            project_id
        )
        
        return job_id
    
    async def _execute_project_processing(self, job_id: UUID, project_id: UUID):
        """Execute project processing in background"""
        try:
            # Update status to processing
            await self.job_manager.update_job_status(job_id, 'processing')
            
            # Clone repository
            repo_path = await clone_repository(project_id)
            
            # Parse plan file
            tasks = await parse_plan_file(repo_path)
            
            # Calculate progress
            progress = await calculate_progress(tasks)
            
            # Store results
            await store_project_data(project_id, tasks, progress)
            
            # Update job as completed
            result = {
                'status': 'success',
                'tasks_count': len(tasks),
                'progress_percentage': progress.percentage
            }
            await self.job_manager.update_job_status(job_id, 'completed', result)
            
        except Exception as e:
            # Update job as failed
            await self.job_manager.update_job_status(
                job_id, 
                'failed', 
                error=str(e)
            )
        finally:
            # Cleanup
            if 'repo_path' in locals():
                await cleanup_repository(repo_path)
    
    async def extract_skills_background(
        self,
        background_tasks: BackgroundTasks,
        project_id: UUID,
        user_id: UUID
    ) -> UUID:
        """Start skills extraction in background"""
        job_id = await self.job_manager.create_job(
            'skills_extraction',
            project_id,
            user_id
        )
        
        background_tasks.add_task(
            self._execute_skills_extraction,
            job_id,
            project_id
        )
        
        return job_id
    
    async def _execute_skills_extraction(self, job_id: UUID, project_id: UUID):
        """Execute skills extraction in background"""
        try:
            await self.job_manager.update_job_status(job_id, 'processing')
            
            repo_path = await clone_repository(project_id)
            skills = await extract_skills_from_repo(repo_path)
            await store_project_skills(project_id, skills)
            
            result = {
                'status': 'success',
                'skills_count': len(skills)
            }
            await self.job_manager.update_job_status(job_id, 'completed', result)
            
        except Exception as e:
            await self.job_manager.update_job_status(
                job_id,
                'failed',
                error=str(e)
            )
        finally:
            if 'repo_path' in locals():
                await cleanup_repository(repo_path)
```

### Job Queue Management
```python
class JobQueueManager:
    def __init__(self, db: Session):
        self.db = db
    
    async def get_queue_status(self) -> Dict[str, Any]:
        """Get overall queue status"""
        pending = self.db.query(Job).filter(Job.status == 'pending').count()
        processing = self.db.query(Job).filter(Job.status == 'processing').count()
        completed = self.db.query(Job).filter(Job.status == 'completed').count()
        failed = self.db.query(Job).filter(Job.status == 'failed').count()
        
        return {
            'pending': pending,
            'processing': processing,
            'completed': completed,
            'failed': failed,
            'total': pending + processing + completed + failed
        }
    
    async def retry_failed_job(self, job_id: UUID) -> bool:
        """Retry a failed job"""
        job = self.db.query(Job).filter(Job.id == job_id).first()
        if job and job.status == 'failed' and job.retry_count < job.max_retries:
            job.status = 'pending'
            job.retry_count += 1
            job.error = None
            job.completed_at = None
            self.db.commit()
            return True
        return False
    
    async def cleanup_old_jobs(self, days: int = 30):
        """Clean up old completed/failed jobs"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        self.db.query(Job).filter(
            Job.status.in_(['completed', 'failed']),
            Job.completed_at < cutoff_date
        ).delete()
        self.db.commit()
```

### Acceptance Criteria
- [ ] Background task processing working
- [ ] Project processing in background
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
- **Rate Limiting**: Database-based rate limiting
- **Status Indicators**: Real-time refresh status updates
- **History Tracking**: Track refresh operations over time
- **Priority Handling**: Manual refreshes get higher priority

### Manual Refresh API
```python
@router.post("/projects/{project_id}/refresh")
async def refresh_project(
    project_id: UUID,
    background_tasks: BackgroundTasks,
    current_user: Any = Depends(get_current_user), # Changed to Any as User model is removed
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Trigger manual refresh of project"""
    
    # Check rate limiting
    if not await check_rate_limit(db, current_user.id, "refresh"):
        raise HTTPException(429, "Rate limit exceeded")
    
    # Create refresh job with high priority
    job_manager = JobManager(db)
    job_id = await job_manager.create_job(
        'refresh',
        project_id,
        current_user.id,
        priority='high'
    )
    
    # Start background processing
    processor = BackgroundProcessor(db, job_manager)
    await processor.process_project_background(
        background_tasks,
        project_id,
        current_user.id
    )
    
    return {
        "job_id": str(job_id),
        "status": "queued",
        "message": "Project refresh queued successfully"
    }
```

### Rate Limiting
```python
class RateLimiter:
    def __init__(self, db: Session):
        self.db = db
    
    async def check_rate_limit(self, user_id: UUID, action: str) -> bool:
        """Check if user has exceeded rate limit for action"""
        window_seconds = RATE_LIMITS[action]['window_seconds']
        max_attempts = RATE_LIMITS[action]['max_attempts']
        
        cutoff_time = datetime.utcnow() - timedelta(seconds=window_seconds)
        
        # Count recent attempts
        recent_attempts = self.db.query(Job).filter(
            Job.user_id == user_id,
            Job.type == action,
            Job.created_at >= cutoff_time
        ).count()
        
        return recent_attempts < max_attempts

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
      const response = await api.refreshProject(projectId);
      // Poll for status updates
      pollJobStatus(response.job_id);
    } catch (error) {
      console.error('Refresh failed:', error);
    } finally {
      setIsRefreshing(false);
    }
  };
  
  const pollJobStatus = async (jobId: string) => {
    const interval = setInterval(async () => {
      const status = await api.getJobStatus(jobId);
      if (status.status === 'completed' || status.status === 'failed') {
        clearInterval(interval);
        setIsRefreshing(false);
        // Refresh project data
        window.location.reload();
      }
    }, 2000);
  };
  
  return { isRefreshing, triggerRefresh, refreshHistory };
}
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
- `GET /projects/{id}/jobs` - Get project jobs
- `GET /jobs/{id}/status` - Get job status
- `GET /jobs/queue-status` - Get queue status
- `POST /jobs/{id}/retry` - Retry failed job
- `DELETE /jobs/{id}` - Cancel job

### Job Status Response
```json
{
  "id": "uuid",
  "type": "project_processing",
  "status": "queued|processing|completed|failed",
  "project_id": "uuid",
  "created_at": "2024-01-01T12:00:00Z",
  "started_at": "2024-01-01T12:00:05Z",
  "completed_at": null,
  "result": {
    "tasks_count": 15,
    "progress_percentage": 65.5
  },
  "error": null,
  "retry_count": 0
}
```

---

## Monitoring and Observability

### Job Monitoring
- **Queue Metrics**: Job counts by status
- **Performance Metrics**: Job duration, success rate
- **Error Tracking**: Failed jobs, error patterns
- **User Activity**: Refresh patterns, usage statistics

### Health Checks
```python
@router.get("/health/jobs")
async def jobs_health_check(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Check job processing health"""
    try:
        # Get queue status
        queue_manager = JobQueueManager(db)
        queue_status = await queue_manager.get_queue_status()
        
        # Check for stuck jobs (processing for too long)
        stuck_jobs = db.query(Job).filter(
            Job.status == 'processing',
            Job.started_at < datetime.utcnow() - timedelta(hours=1)
        ).count()
        
        return {
            "status": "healthy",
            "queue_status": queue_status,
            "stuck_jobs": stuck_jobs,
            "database_connected": True
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
- Job management tests
- Background processing tests
- Rate limiting tests
- Error handling tests

### Integration Tests
- End-to-end job processing
- Database integration tests
- Background task tests

### Load Testing
- Concurrent job processing
- Database performance under load
- Rate limiting effectiveness

---

## Definition of Done
- [ ] All tasks completed and tested
- [ ] Database-based job tracking working
- [ ] Background processing functional
- [ ] Manual refresh system complete
- [ ] Job monitoring implemented
- [ ] Rate limiting functional
- [ ] Ready for Phase 6 development

---

## Next Phase Dependencies
- Background processing must be stable
- Job tracking must be functional
- Manual refresh must work correctly
- Monitoring must be in place

---

## Budget Benefits

### Cost Savings
- **No Redis infrastructure**: Eliminates Redis hosting costs
- **No additional services**: Uses existing PostgreSQL database (Supabase or local)
- **Simplified deployment**: Fewer moving parts to maintain
- **Reduced complexity**: Easier to debug and maintain
- **Cloud database benefits**: When using Supabase, no local database management needed

### Trade-offs
- **Less scalability**: No distributed queue processing
- **Database load**: Job tracking adds database queries
- **Limited concurrency**: No true parallel job processing
- **Manual cleanup**: Requires periodic cleanup of old jobs

### When to Upgrade
Consider upgrading to Redis/RQ when:
- Processing more than 100+ concurrent jobs
- Need true distributed processing
- Database becomes a bottleneck
- Require advanced queue features (priority, scheduling)
