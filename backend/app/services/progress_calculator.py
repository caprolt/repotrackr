from datetime import datetime, timedelta
from typing import List, Optional
from dataclasses import dataclass
from decimal import Decimal
import logging

from app.services.task_extractor import Task

logger = logging.getLogger(__name__)


@dataclass
class ProgressSnapshot:
    """Represents a snapshot of project progress at a point in time."""
    percentage_complete: Decimal
    tasks_total: int
    tasks_done: int
    tasks_doing: int
    tasks_todo: int
    tasks_blocked: int
    project_status: str  # 'green', 'yellow', 'red'
    created_at: datetime


class ProgressCalculator:
    """Calculates project progress and determines status based on task completion."""
    
    def __init__(self, 
                 green_threshold: float = 70.0,
                 yellow_threshold: float = 30.0,
                 stale_threshold_days: int = 30):
        """
        Initialize the progress calculator.
        
        Args:
            green_threshold: Minimum percentage for green status
            yellow_threshold: Minimum percentage for yellow status
            stale_threshold_days: Days after which a project is considered stale
        """
        self.green_threshold = green_threshold
        self.yellow_threshold = yellow_threshold
        self.stale_threshold_days = stale_threshold_days
    
    async def calculate_progress(self, tasks: List[Task]) -> ProgressSnapshot:
        """
        Calculate progress from a list of tasks.
        
        Args:
            tasks: List of tasks to analyze
            
        Returns:
            Progress snapshot with calculated metrics
        """
        if not tasks:
            return ProgressSnapshot(
                percentage_complete=Decimal('0.0'),
                tasks_total=0,
                tasks_done=0,
                tasks_doing=0,
                tasks_todo=0,
                tasks_blocked=0,
                project_status='red',
                created_at=datetime.utcnow()
            )
        
        # Count tasks by status
        tasks_done = sum(1 for task in tasks if task.status == 'done')
        tasks_doing = sum(1 for task in tasks if task.status == 'doing')
        tasks_todo = sum(1 for task in tasks if task.status == 'todo')
        tasks_blocked = sum(1 for task in tasks if task.status == 'blocked')
        tasks_total = len(tasks)
        
        # Calculate percentage complete
        # Consider both done and doing tasks as progress
        completed_tasks = tasks_done + tasks_doing
        percentage_complete = Decimal(str((completed_tasks / tasks_total) * 100)).quantize(Decimal('0.01'))
        
        # Determine project status
        project_status = self._determine_status(percentage_complete, tasks_blocked)
        
        snapshot = ProgressSnapshot(
            percentage_complete=percentage_complete,
            tasks_total=tasks_total,
            tasks_done=tasks_done,
            tasks_doing=tasks_doing,
            tasks_todo=tasks_todo,
            tasks_blocked=tasks_blocked,
            project_status=project_status,
            created_at=datetime.utcnow()
        )
        
        logger.info(f"Calculated progress: {percentage_complete}% complete, status: {project_status}")
        return snapshot
    
    def _determine_status(self, percentage: Decimal, blocked_count: int) -> str:
        """
        Determine project status based on completion percentage and blocked tasks.
        
        Args:
            percentage: Completion percentage
            blocked_count: Number of blocked tasks
            
        Returns:
            Project status: 'green', 'yellow', or 'red'
        """
        percentage_float = float(percentage)
        
        # Green: ≥ 70% complete, no blocked items
        if percentage_float >= self.green_threshold and blocked_count == 0:
            return 'green'
        
        # Yellow: 30-69% complete, ≤ 1 blocked task
        elif percentage_float >= self.yellow_threshold and blocked_count <= 1:
            return 'yellow'
        
        # Red: < 30% complete, > 1 blocked task, or other issues
        else:
            return 'red'
    
    async def is_stale(self, last_updated: datetime) -> bool:
        """
        Check if a project is stale based on last update time.
        
        Args:
            last_updated: Last update timestamp
            
        Returns:
            True if project is stale, False otherwise
        """
        if not last_updated:
            return True
        
        stale_threshold = datetime.utcnow() - timedelta(days=self.stale_threshold_days)
        return last_updated < stale_threshold
    
    async def create_snapshot(self, project_id: str, tasks: List[Task]) -> ProgressSnapshot:
        """
        Create a progress snapshot for a project.
        
        Args:
            project_id: The project ID
            tasks: List of tasks for the project
            
        Returns:
            Progress snapshot
        """
        return await self.calculate_progress(tasks)
    
    async def get_status_summary(self, tasks: List[Task]) -> dict:
        """
        Get a summary of task statuses.
        
        Args:
            tasks: List of tasks to summarize
            
        Returns:
            Dictionary with status summary
        """
        if not tasks:
            return {
                'total': 0,
                'done': 0,
                'doing': 0,
                'todo': 0,
                'blocked': 0,
                'percentage': 0.0
            }
        
        tasks_done = sum(1 for task in tasks if task.status == 'done')
        tasks_doing = sum(1 for task in tasks if task.status == 'doing')
        tasks_todo = sum(1 for task in tasks if task.status == 'todo')
        tasks_blocked = sum(1 for task in tasks if task.status == 'blocked')
        tasks_total = len(tasks)
        
        completed_tasks = tasks_done + tasks_doing
        percentage = (completed_tasks / tasks_total) * 100 if tasks_total > 0 else 0
        
        return {
            'total': tasks_total,
            'done': tasks_done,
            'doing': tasks_doing,
            'todo': tasks_todo,
            'blocked': tasks_blocked,
            'percentage': round(percentage, 2)
        }
