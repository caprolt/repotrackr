import uuid
from typing import List, Optional
from dataclasses import dataclass
from datetime import datetime
import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from fastapi import HTTPException

from app.db.models import Project, Task as DBTask, ProgressSnapshot as DBProgressSnapshot
from app.services.repository_manager import RepositoryManager
from app.services.task_extractor import TaskExtractor, Task
from app.services.progress_calculator import ProgressCalculator, ProgressSnapshot

logger = logging.getLogger(__name__)


@dataclass
class ProcessingResult:
    """Result of processing a project."""
    success: bool
    tasks_count: int
    progress_percentage: float
    project_status: str
    error_message: Optional[str] = None
    processing_time: Optional[float] = None


class PlanProcessingPipeline:
    """Main pipeline for processing project plans."""
    
    def __init__(self):
        self.repository_manager = RepositoryManager()
        self.task_extractor = TaskExtractor()
        self.progress_calculator = ProgressCalculator()
    
    async def process_project(self, project_id: str, db: AsyncSession) -> ProcessingResult:
        """
        Process a project end-to-end.
        
        Args:
            project_id: The project ID to process
            db: Database session
            
        Returns:
            Processing result with success status and metrics
        """
        start_time = datetime.utcnow()
        repo_path = None
        
        try:
            # Get project from database
            project = await self._get_project(project_id, db)
            if not project:
                raise HTTPException(status_code=404, detail="Project not found")
            
            logger.info(f"Starting processing for project: {project.name}")
            
            # Update project status to processing
            await self._update_project_status(project_id, "processing", db)
            
            # Clone repository and extract tasks
            tasks = await self.clone_and_parse(project.repo_url, project.plan_path)
            
            # Calculate progress
            progress_snapshot = await self.progress_calculator.calculate_progress(tasks)
            
            # Store tasks and progress in database
            await self._store_tasks_and_progress(project_id, tasks, progress_snapshot, db)
            
            # Update project status
            await self._update_project_status(project_id, progress_snapshot.project_status, db)
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            result = ProcessingResult(
                success=True,
                tasks_count=len(tasks),
                progress_percentage=float(progress_snapshot.percentage_complete),
                project_status=progress_snapshot.project_status,
                processing_time=processing_time
            )
            
            logger.info(f"Successfully processed project {project.name}: {len(tasks)} tasks, {progress_snapshot.percentage_complete}% complete")
            return result
            
        except Exception as e:
            logger.error(f"Failed to process project {project_id}: {e}")
            
            # Update project status to failed
            await self._update_project_status(project_id, "failed", db)
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            result = ProcessingResult(
                success=False,
                tasks_count=0,
                progress_percentage=0.0,
                project_status="red",
                error_message=str(e),
                processing_time=processing_time
            )
            
            return result
            
        finally:
            # Clean up repository
            if repo_path:
                await self.repository_manager.cleanup_repository(repo_path)
    
    async def clone_and_parse(self, repo_url: str, plan_path: str) -> List[Task]:
        """
        Clone repository and parse tasks from plan file.
        
        Args:
            repo_url: Repository URL to clone
            plan_path: Expected path to plan file
            
        Returns:
            List of extracted tasks
        """
        # Clone repository
        repo_path = await self.repository_manager.clone_repository(repo_url)
        
        try:
            # Discover plan file
            discovered_plan_path = await self.repository_manager.discover_plan_file(repo_path)
            
            if not discovered_plan_path:
                raise HTTPException(
                    status_code=404,
                    detail=f"No plan file found in repository. Expected locations: docs/plan.md, plan.md, README.md"
                )
            
            # Get plan file content
            content = await self.repository_manager.get_file_content(repo_path, discovered_plan_path)
            
            # Extract tasks
            tasks = await self.task_extractor.extract_tasks_from_markdown(content, discovered_plan_path)
            
            return tasks
            
        except Exception as e:
            # Clean up on error
            await self.repository_manager.cleanup_repository(repo_path)
            raise e
    
    async def _get_project(self, project_id: str, db: AsyncSession) -> Optional[Project]:
        """Get project from database."""
        try:
            project_uuid = uuid.UUID(project_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid project ID format")
        
        result = await db.execute(
            select(Project).where(Project.id == project_uuid)
        )
        return result.scalar_one_or_none()
    
    async def _update_project_status(self, project_id: str, status: str, db: AsyncSession) -> None:
        """Update project status in database."""
        try:
            project_uuid = uuid.UUID(project_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid project ID format")
        
        await db.execute(
            update(Project)
            .where(Project.id == project_uuid)
            .values(
                status=status,
                last_updated=datetime.utcnow()
            )
        )
        await db.commit()
    
    async def _store_tasks_and_progress(self, project_id: str, tasks: List[Task], 
                                      progress_snapshot: ProgressSnapshot, db: AsyncSession) -> None:
        """Store tasks and progress snapshot in database."""
        try:
            project_uuid = uuid.UUID(project_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid project ID format")
        
        # Clear existing tasks
        await db.execute(
            select(DBTask).where(DBTask.project_id == project_uuid)
        )
        existing_tasks = await db.execute(
            select(DBTask).where(DBTask.project_id == project_uuid)
        )
        for task in existing_tasks.scalars().all():
            await db.delete(task)
        
        # Store new tasks
        for task in tasks:
            db_task = DBTask(
                project_id=project_uuid,
                title=task.title,
                status=task.status,
                file_path=task.file_path,
                line_number=task.line_number
            )
            db.add(db_task)
        
        # Store progress snapshot
        db_snapshot = DBProgressSnapshot(
            project_id=project_uuid,
            percentage_complete=progress_snapshot.percentage_complete,
            tasks_total=progress_snapshot.tasks_total,
            tasks_done=progress_snapshot.tasks_done,
            tasks_doing=progress_snapshot.tasks_doing,
            tasks_todo=progress_snapshot.tasks_todo,
            tasks_blocked=progress_snapshot.tasks_blocked,
            created_at=progress_snapshot.created_at
        )
        db.add(db_snapshot)
        
        await db.commit()
    
    async def handle_processing_error(self, error: Exception, project_id: str, db: AsyncSession) -> None:
        """Handle processing errors and update project status."""
        logger.error(f"Processing error for project {project_id}: {error}")
        
        try:
            await self._update_project_status(project_id, "failed", db)
        except Exception as e:
            logger.error(f"Failed to update project status after error: {e}")
    
    async def get_processing_status(self, project_id: str, db: AsyncSession) -> dict:
        """Get the current processing status of a project."""
        project = await self._get_project(project_id, db)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Get latest progress snapshot
        result = await db.execute(
            select(DBProgressSnapshot)
            .where(DBProgressSnapshot.project_id == project.id)
            .order_by(DBProgressSnapshot.created_at.desc())
            .limit(1)
        )
        latest_snapshot = result.scalar_one_or_none()
        
        # Get task count
        task_result = await db.execute(
            select(DBTask).where(DBTask.project_id == project.id)
        )
        tasks = task_result.scalars().all()
        
        return {
            "status": project.status,
            "last_processed": project.last_updated.isoformat() if project.last_updated else None,
            "tasks_count": len(tasks),
            "progress_percentage": float(latest_snapshot.percentage_complete) if latest_snapshot else 0.0,
            "project_status": project.status
        }
