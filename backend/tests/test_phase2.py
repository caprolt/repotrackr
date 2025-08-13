import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from pathlib import Path
import tempfile
import shutil

from app.services.repository_manager import RepositoryManager
from app.services.task_extractor import TaskExtractor, Task
from app.services.progress_calculator import ProgressCalculator, ProgressSnapshot
from app.services.processing_pipeline import PlanProcessingPipeline


class TestRepositoryManager:
    """Test the repository management functionality."""
    
    @pytest.fixture
    def repo_manager(self):
        return RepositoryManager()
    
    @pytest.mark.asyncio
    async def test_discover_plan_file(self, repo_manager):
        """Test plan file discovery."""
        # Create a temporary directory structure
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create docs/plan.md
            docs_dir = temp_path / "docs"
            docs_dir.mkdir()
            plan_file = docs_dir / "plan.md"
            plan_file.write_text("# Test Plan\n- [ ] Task 1")
            
            # Test discovery
            discovered = await repo_manager.discover_plan_file(str(temp_path))
            assert discovered == str(plan_file)
    
    @pytest.mark.asyncio
    async def test_discover_plan_file_fallback(self, repo_manager):
        """Test plan file discovery with fallback locations."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create plan.md in root
            plan_file = temp_path / "plan.md"
            plan_file.write_text("# Test Plan\n- [ ] Task 1")
            
            # Test discovery
            discovered = await repo_manager.discover_plan_file(str(temp_path))
            assert discovered == str(plan_file)
    
    @pytest.mark.asyncio
    async def test_get_file_content(self, repo_manager):
        """Test file content retrieval."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            test_file = temp_path / "test.md"
            test_content = "# Test Content\nThis is a test file."
            test_file.write_text(test_content)
            
            content = await repo_manager.get_file_content(str(temp_path), "test.md")
            assert content == test_content


class TestTaskExtractor:
    """Test the task extraction functionality."""
    
    @pytest.fixture
    def task_extractor(self):
        return TaskExtractor()
    
    @pytest.mark.asyncio
    async def test_parse_checkbox_tasks(self, task_extractor):
        """Test parsing checkbox-style tasks."""
        content = """
# Project Plan

## Tasks
- [ ] Implement user authentication
- [x] Set up database schema
- [~] Working on API endpoints
- [!] Blocked by external dependency
        """
        
        tasks = await task_extractor.parse_checkbox_tasks(content)
        
        assert len(tasks) == 4
        assert tasks[0].title == "Implement user authentication"
        assert tasks[0].status == "todo"
        assert tasks[1].title == "Set up database schema"
        assert tasks[1].status == "done"
        assert tasks[2].title == "Working on API endpoints"
        assert tasks[2].status == "doing"
        assert tasks[3].title == "Blocked by external dependency"
        assert tasks[3].status == "blocked"
    
    @pytest.mark.asyncio
    async def test_parse_table_tasks(self, task_extractor):
        """Test parsing table-style tasks."""
        content = """
# Project Tasks

| Task | Status | Priority |
|------|--------|----------|
| Setup project | Done | High |
| Implement API | In Progress | Medium |
| Write tests | Todo | Low |
        """
        
        tasks = await task_extractor.parse_table_tasks(content)
        
        assert len(tasks) == 3
        assert tasks[0].title == "Setup project"
        assert tasks[0].status == "done"
        assert tasks[1].title == "Implement API"
        assert tasks[1].status == "doing"
        assert tasks[2].title == "Write tests"
        assert tasks[2].status == "todo"
    
    @pytest.mark.asyncio
    async def test_extract_tasks_from_markdown(self, task_extractor):
        """Test full markdown task extraction."""
        content = """
# Project Plan

## Checkbox Tasks
- [ ] Task 1
- [x] Task 2

## Table Tasks
| Task | Status |
|------|--------|
| Task 3 | Done |
| Task 4 | Todo |
        """
        
        tasks = await task_extractor.extract_tasks_from_markdown(content)
        
        assert len(tasks) == 4
        task_titles = [task.title for task in tasks]
        assert "Task 1" in task_titles
        assert "Task 2" in task_titles
        assert "Task 3" in task_titles
        assert "Task 4" in task_titles


class TestProgressCalculator:
    """Test the progress calculation functionality."""
    
    @pytest.fixture
    def progress_calculator(self):
        return ProgressCalculator()
    
    @pytest.mark.asyncio
    async def test_calculate_progress_empty(self, progress_calculator):
        """Test progress calculation with no tasks."""
        snapshot = await progress_calculator.calculate_progress([])
        
        assert snapshot.percentage_complete == 0.0
        assert snapshot.tasks_total == 0
        assert snapshot.project_status == "red"
    
    @pytest.mark.asyncio
    async def test_calculate_progress_green(self, progress_calculator):
        """Test progress calculation for green status."""
        tasks = [
            Task("Task 1", "done"),
            Task("Task 2", "done"),
            Task("Task 3", "done"),
            Task("Task 4", "todo"),
        ]
        
        snapshot = await progress_calculator.calculate_progress(tasks)
        
        assert snapshot.percentage_complete == 75.0  # 3/4 tasks done
        assert snapshot.tasks_total == 4
        assert snapshot.tasks_done == 3
        assert snapshot.tasks_todo == 1
        assert snapshot.project_status == "green"
    
    @pytest.mark.asyncio
    async def test_calculate_progress_yellow(self, progress_calculator):
        """Test progress calculation for yellow status."""
        tasks = [
            Task("Task 1", "done"),
            Task("Task 2", "doing"),
            Task("Task 3", "todo"),
            Task("Task 4", "todo"),
        ]
        
        snapshot = await progress_calculator.calculate_progress(tasks)
        
        assert snapshot.percentage_complete == 50.0  # 2/4 tasks in progress
        assert snapshot.project_status == "yellow"
    
    @pytest.mark.asyncio
    async def test_calculate_progress_red(self, progress_calculator):
        """Test progress calculation for red status."""
        tasks = [
            Task("Task 1", "todo"),
            Task("Task 2", "todo"),
            Task("Task 3", "blocked"),
            Task("Task 4", "blocked"),
        ]
        
        snapshot = await progress_calculator.calculate_progress(tasks)
        
        assert snapshot.percentage_complete == 0.0
        assert snapshot.tasks_blocked == 2
        assert snapshot.project_status == "red"
    
    @pytest.mark.asyncio
    async def test_is_stale(self, progress_calculator):
        """Test stale project detection."""
        from datetime import datetime, timedelta
        
        # Test stale project
        old_date = datetime.utcnow() - timedelta(days=35)
        assert await progress_calculator.is_stale(old_date) == True
        
        # Test fresh project
        recent_date = datetime.utcnow() - timedelta(days=5)
        assert await progress_calculator.is_stale(recent_date) == False


class TestProcessingPipeline:
    """Test the processing pipeline functionality."""
    
    @pytest.fixture
    def pipeline(self):
        return PlanProcessingPipeline()
    
    @pytest.mark.asyncio
    async def test_clone_and_parse_mock(self, pipeline):
        """Test clone and parse with mocked repository."""
        with patch.object(pipeline.repository_manager, 'clone_repository') as mock_clone, \
             patch.object(pipeline.repository_manager, 'discover_plan_file') as mock_discover, \
             patch.object(pipeline.repository_manager, 'get_file_content') as mock_content:
            
            mock_clone.return_value = "/tmp/test-repo"
            mock_discover.return_value = "/tmp/test-repo/docs/plan.md"
            mock_content.return_value = """
# Test Plan
- [ ] Task 1
- [x] Task 2
            """
            
            tasks = await pipeline.clone_and_parse("https://github.com/test/repo", "docs/plan.md")
            
            assert len(tasks) == 2
            assert tasks[0].title == "Task 1"
            assert tasks[0].status == "todo"
            assert tasks[1].title == "Task 2"
            assert tasks[1].status == "done"


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
