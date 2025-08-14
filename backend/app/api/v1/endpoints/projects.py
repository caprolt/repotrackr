from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.db.base import get_db
from app.db.models import Project, Task, ProgressSnapshot
from app.schemas.project import (
    ProjectCreate,
    ProjectResponse,
    ProjectListResponse,
    ProjectUpdate
)
from app.services.processing_pipeline import PlanProcessingPipeline

router = APIRouter()


@router.post("/", response_model=ProjectResponse)
async def create_project(
    project: ProjectCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new project"""
    # Check if project with same repo_url already exists
    existing_project = await db.execute(
        select(Project).where(Project.repo_url == project.repo_url)
    )
    if existing_project.scalar_one_or_none():
        raise HTTPException(
            status_code=400,
            detail="A project with this repository URL already exists"
        )
    
    # Create new project
    db_project = Project(
        name=project.name,
        repo_url=project.repo_url,
        plan_path=project.plan_path
    )
    db.add(db_project)
    await db.commit()
    await db.refresh(db_project)
    
    return db_project


@router.get("/", response_model=ProjectListResponse)
async def list_projects(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    status: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """List all projects with pagination"""
    # Build query
    query = select(Project)
    count_query = select(func.count(Project.id))
    
    # Add status filter if provided
    if status:
        if status not in ["green", "yellow", "red"]:
            raise HTTPException(
                status_code=400,
                detail="Status must be one of: green, yellow, red"
            )
        query = query.where(Project.status == status)
        count_query = count_query.where(Project.status == status)
    
    # Get total count
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Get paginated results
    query = query.offset(offset).limit(limit).order_by(Project.created_at.desc())
    result = await db.execute(query)
    projects = result.scalars().all()
    
    return ProjectListResponse(
        projects=projects,
        total=total,
        limit=limit,
        offset=offset
    )


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get project details by ID"""
    try:
        import uuid
        project_uuid = uuid.UUID(project_id)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid project ID format"
        )
    
    result = await db.execute(
        select(Project).where(Project.id == project_uuid)
    )
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )
    
    return project


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: str,
    project_update: ProjectUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a project"""
    try:
        import uuid
        project_uuid = uuid.UUID(project_id)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid project ID format"
        )
    
    # Get existing project
    result = await db.execute(
        select(Project).where(Project.id == project_uuid)
    )
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )
    
    # Check if repo_url is being updated and if it conflicts with existing project
    if project_update.repo_url and project_update.repo_url != project.repo_url:
        existing_project = await db.execute(
            select(Project).where(Project.repo_url == project_update.repo_url)
        )
        if existing_project.scalar_one_or_none():
            raise HTTPException(
                status_code=400,
                detail="A project with this repository URL already exists"
            )
    
    # Update project fields
    update_data = {}
    if project_update.name is not None:
        update_data["name"] = project_update.name
    if project_update.repo_url is not None:
        update_data["repo_url"] = project_update.repo_url
    if project_update.plan_path is not None:
        update_data["plan_path"] = project_update.plan_path
    
    # Update the project
    for field, value in update_data.items():
        setattr(project, field, value)
    
    project.last_updated = datetime.utcnow()
    await db.commit()
    await db.refresh(project)
    
    return project


@router.delete("/{project_id}")
async def delete_project(
    project_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Delete a project"""
    try:
        import uuid
        project_uuid = uuid.UUID(project_id)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid project ID format"
        )
    
    result = await db.execute(
        select(Project).where(Project.id == project_uuid)
    )
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )
    
    await db.delete(project)
    await db.commit()
    
    return {"message": "Project deleted successfully"}


@router.post("/{project_id}/process")
async def process_project(
    project_id: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Trigger manual processing of a project"""
    try:
        import uuid
        project_uuid = uuid.UUID(project_id)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid project ID format"
        )
    
    # Check if project exists
    result = await db.execute(
        select(Project).where(Project.id == project_uuid)
    )
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )
    
    # Process the project
    pipeline = PlanProcessingPipeline()
    result = await pipeline.process_project(project_id, db)
    
    if result.success:
        return {
            "message": "Project processed successfully",
            "tasks_count": result.tasks_count,
            "progress_percentage": result.progress_percentage,
            "project_status": result.project_status,
            "processing_time": result.processing_time
        }
    else:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process project: {result.error_message}"
        )


@router.get("/{project_id}/processing-status")
async def get_processing_status(
    project_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get the current processing status of a project"""
    try:
        import uuid
        project_uuid = uuid.UUID(project_id)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid project ID format"
        )
    
    # Check if project exists
    result = await db.execute(
        select(Project).where(Project.id == project_uuid)
    )
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )
    
    # Get processing status
    pipeline = PlanProcessingPipeline()
    status = await pipeline.get_processing_status(project_id, db)
    
    return status


@router.get("/{project_id}/tasks")
async def get_project_tasks(
    project_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get all tasks for a project"""
    try:
        import uuid
        project_uuid = uuid.UUID(project_id)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid project ID format"
        )
    
    # Check if project exists
    result = await db.execute(
        select(Project).where(Project.id == project_uuid)
    )
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )
    
    # Get tasks
    task_result = await db.execute(
        select(Task).where(Task.project_id == project_uuid).order_by(Task.created_at)
    )
    tasks = task_result.scalars().all()
    
    return {
        "project_id": project_id,
        "tasks": [
            {
                "id": str(task.id),
                "title": task.title,
                "status": task.status,
                "file_path": task.file_path,
                "line_number": task.line_number,
                "created_at": task.created_at.isoformat() if task.created_at else None
            }
            for task in tasks
        ],
        "total": len(tasks)
    }


@router.get("/{project_id}/progress")
async def get_project_progress(
    project_id: str,
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    """Get progress history for a project"""
    try:
        import uuid
        project_uuid = uuid.UUID(project_id)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid project ID format"
        )
    
    # Check if project exists
    result = await db.execute(
        select(Project).where(Project.id == project_uuid)
    )
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )
    
    # Get progress snapshots
    snapshot_result = await db.execute(
        select(ProgressSnapshot)
        .where(ProgressSnapshot.project_id == project_uuid)
        .order_by(ProgressSnapshot.created_at.desc())
        .limit(limit)
    )
    snapshots = snapshot_result.scalars().all()
    
    return {
        "project_id": project_id,
        "progress_history": [
            {
                "id": str(snapshot.id),
                "percentage_complete": float(snapshot.percentage_complete),
                "tasks_total": snapshot.tasks_total,
                "tasks_done": snapshot.tasks_done,
                "tasks_doing": snapshot.tasks_doing,
                "tasks_todo": snapshot.tasks_todo,
                "tasks_blocked": snapshot.tasks_blocked,
                "created_at": snapshot.created_at.isoformat() if snapshot.created_at else None
            }
            for snapshot in snapshots
        ],
        "total": len(snapshots)
    }
