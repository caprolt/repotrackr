# Phase 2: Plan Parsing Engine - Implementation Guide

## Overview
Phase 2 implements the core plan parsing functionality that extracts tasks from GitHub repositories and calculates project progress. This is the heart of the RepoTrackr system.

## Architecture

### Core Services

#### 1. Repository Manager (`app/services/repository_manager.py`)
Handles repository cloning, file discovery, and cleanup operations.

**Key Features:**
- GitPython integration for repository operations
- Shallow clones for performance (<30 seconds)
- Plan file discovery in multiple locations:
  - `docs/plan.md` (primary)
  - `plan.md` (fallback)
  - `README.md` (with plan section detection)
- Automatic repository cleanup
- File content retrieval with encoding handling

**Usage:**
```python
from app.services.repository_manager import RepositoryManager

repo_manager = RepositoryManager()
repo_path = await repo_manager.clone_repository("https://github.com/user/repo")
plan_file = await repo_manager.discover_plan_file(repo_path)
content = await repo_manager.get_file_content(repo_path, plan_file)
await repo_manager.cleanup_repository(repo_path)
```

#### 2. Task Extractor (`app/services/task_extractor.py`)
Parses markdown content to extract tasks from checkboxes and tables.

**Supported Formats:**

**Checkbox Tasks:**
```markdown
- [ ] Implement user authentication
- [x] Set up database schema
- [~] Working on API endpoints
- [!] Blocked by external dependency
```

**Table Tasks:**
```markdown
| Task | Status | Priority |
|------|--------|----------|
| Setup project | Done | High |
| Implement API | In Progress | Medium |
| Write tests | Todo | Low |
```

**Usage:**
```python
from app.services.task_extractor import TaskExtractor

task_extractor = TaskExtractor()
tasks = await task_extractor.extract_tasks_from_markdown(content, "docs/plan.md")
```

#### 3. Progress Calculator (`app/services/progress_calculator.py`)
Calculates project progress and determines status based on task completion.

**Status Logic:**
- **Green**: ≥ 70% complete, no blocked items
- **Yellow**: 30-69% complete, ≤ 1 blocked task
- **Red**: < 30% complete, > 1 blocked task, or stale

**Usage:**
```python
from app.services.progress_calculator import ProgressCalculator

progress_calculator = ProgressCalculator()
snapshot = await progress_calculator.calculate_progress(tasks)
```

#### 4. Processing Pipeline (`app/services/processing_pipeline.py`)
Orchestrates the entire processing workflow.

**Pipeline Steps:**
1. Clone repository
2. Discover plan file
3. Parse tasks
4. Calculate progress
5. Store snapshot
6. Update project status

**Usage:**
```python
from app.services.processing_pipeline import PlanProcessingPipeline

pipeline = PlanProcessingPipeline()
result = await pipeline.process_project(project_id, db_session)
```

## API Endpoints

### New Endpoints Added:

#### `POST /projects/{id}/process`
Trigger manual processing of a project.

**Response:**
```json
{
  "message": "Project processed successfully",
  "tasks_count": 15,
  "progress_percentage": 65.5,
  "project_status": "yellow",
  "processing_time": 45.2
}
```

#### `GET /projects/{id}/processing-status`
Get the current processing status of a project.

**Response:**
```json
{
  "status": "completed",
  "last_processed": "2024-01-01T12:00:00Z",
  "tasks_count": 15,
  "progress_percentage": 65.5,
  "project_status": "yellow"
}
```

#### `GET /projects/{id}/tasks`
Get all tasks for a project.

**Response:**
```json
{
  "project_id": "uuid",
  "tasks": [
    {
      "id": "task-uuid",
      "title": "Implement authentication",
      "status": "done",
      "file_path": "docs/plan.md",
      "line_number": 5,
      "created_at": "2024-01-01T12:00:00Z"
    }
  ],
  "total": 15
}
```

#### `GET /projects/{id}/progress`
Get progress history for a project.

**Response:**
```json
{
  "project_id": "uuid",
  "progress_history": [
    {
      "id": "snapshot-uuid",
      "percentage_complete": 65.5,
      "tasks_total": 15,
      "tasks_done": 8,
      "tasks_doing": 2,
      "tasks_todo": 4,
      "tasks_blocked": 1,
      "created_at": "2024-01-01T12:00:00Z"
    }
  ],
  "total": 10
}
```

## Testing

### Running Tests
```bash
cd backend
python -m pytest tests/test_phase2.py -v
```

### Running Demo
```bash
cd backend
python demo_phase2.py
```

## Database Schema Updates

### New Status Values
The `Project.status` enum now includes:
- `green` - Project is on track (≥70% complete)
- `yellow` - Project needs attention (30-69% complete)
- `red` - Project has issues (<30% complete or blocked)
- `processing` - Currently being processed
- `failed` - Processing failed

### New Tables
- `tasks` - Stores extracted tasks
- `progress_snapshots` - Stores progress history

## Configuration

### Environment Variables
```bash
# Repository processing
REPO_TEMP_DIR=/tmp/repotrackr
REPO_CLEANUP_INTERVAL=3600

# Progress calculation
GREEN_THRESHOLD=70.0
YELLOW_THRESHOLD=30.0
STALE_THRESHOLD_DAYS=30
```

## Error Handling

### Common Error Scenarios
1. **Repository not found**: Returns 404 with clear error message
2. **Plan file not found**: Returns 404 with expected locations
3. **Git clone failure**: Returns 400 with git error details
4. **Parsing errors**: Logs warning and continues with partial results
5. **Database errors**: Returns 500 with error details

### Logging
All services include comprehensive logging:
- Repository operations
- Task extraction results
- Progress calculations
- Processing pipeline status
- Error conditions

## Performance Considerations

### Optimization Features
- Shallow repository clones (depth=1)
- Temporary file cleanup
- Task deduplication
- Efficient database queries
- Configurable processing timeouts

### Performance Metrics
- Repository cloning: <30 seconds
- Task extraction: <5 seconds
- Progress calculation: <1 second
- End-to-end processing: <60 seconds

## Next Steps

Phase 2 is now complete and ready for Phase 3: Frontend Foundation. The plan parsing engine provides:

1. ✅ Robust repository integration
2. ✅ Flexible task extraction
3. ✅ Accurate progress calculation
4. ✅ Comprehensive API endpoints
5. ✅ Error handling and logging
6. ✅ Performance optimization

The system can now process GitHub repositories, extract tasks from various markdown formats, calculate project progress, and provide real-time status updates through the API.
