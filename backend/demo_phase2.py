#!/usr/bin/env python3
"""
Demo script for Phase 2: Plan Parsing Engine
This script demonstrates the core functionality of the plan parsing system.
"""

import asyncio
import tempfile
from pathlib import Path
from app.services.repository_manager import RepositoryManager
from app.services.task_extractor import TaskExtractor
from app.services.progress_calculator import ProgressCalculator
from app.services.processing_pipeline import PlanProcessingPipeline


async def demo_repository_manager():
    """Demo the repository manager functionality."""
    print("=== Repository Manager Demo ===")
    
    repo_manager = RepositoryManager()
    
    # Create a temporary repository structure
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create docs/plan.md
        docs_dir = temp_path / "docs"
        docs_dir.mkdir()
        plan_file = docs_dir / "plan.md"
        plan_content = """
# Project Implementation Plan

## Phase 1: Foundation
- [x] Set up project structure
- [x] Configure database
- [ ] Implement basic API endpoints

## Phase 2: Core Features
- [~] Working on authentication system
- [ ] Add user management
- [!] Blocked: Waiting for design approval

## Phase 3: Polish
- [ ] Add comprehensive tests
- [ ] Optimize performance
- [ ] Deploy to production
        """
        plan_file.write_text(plan_content)
        
        print(f"Created test repository at: {temp_path}")
        
        # Test plan file discovery
        discovered = await repo_manager.discover_plan_file(str(temp_path))
        print(f"Discovered plan file: {discovered}")
        
        # Test file content retrieval
        content = await repo_manager.get_file_content(str(temp_path), "docs/plan.md")
        print(f"Retrieved content ({len(content)} characters)")
        
        return content


async def demo_task_extractor(content):
    """Demo the task extraction functionality."""
    print("\n=== Task Extractor Demo ===")
    
    task_extractor = TaskExtractor()
    
    # Extract tasks from markdown content
    tasks = await task_extractor.extract_tasks_from_markdown(content, "docs/plan.md")
    
    print(f"Extracted {len(tasks)} tasks:")
    for i, task in enumerate(tasks, 1):
        status_emoji = {
            'todo': '⏳',
            'doing': '🔄',
            'done': '✅',
            'blocked': '🚫'
        }.get(task.status, '❓')
        
        print(f"  {i}. {status_emoji} {task.title} ({task.status})")
        if task.file_path:
            print(f"     📁 {task.file_path}:{task.line_number}")
    
    return tasks


async def demo_progress_calculator(tasks):
    """Demo the progress calculation functionality."""
    print("\n=== Progress Calculator Demo ===")
    
    progress_calculator = ProgressCalculator()
    
    # Calculate progress
    snapshot = await progress_calculator.calculate_progress(tasks)
    
    print(f"Project Progress: {snapshot.percentage_complete}% complete")
    print(f"Status: {snapshot.project_status.upper()}")
    print(f"Task Breakdown:")
    print(f"  ✅ Done: {snapshot.tasks_done}")
    print(f"  🔄 Doing: {snapshot.tasks_doing}")
    print(f"  ⏳ Todo: {snapshot.tasks_todo}")
    print(f"  🚫 Blocked: {snapshot.tasks_blocked}")
    print(f"  📊 Total: {snapshot.tasks_total}")
    
    # Get status summary
    summary = await progress_calculator.get_status_summary(tasks)
    print(f"\nStatus Summary: {summary}")
    
    return snapshot


async def demo_processing_pipeline():
    """Demo the processing pipeline functionality."""
    print("\n=== Processing Pipeline Demo ===")
    
    pipeline = PlanProcessingPipeline()
    
    # Create sample markdown content
    sample_content = """
# Sample Project Plan

## Development Tasks
- [x] Initialize project
- [x] Set up development environment
- [~] Implementing core features
- [ ] Write documentation
- [!] Waiting for API keys

## Testing Tasks
| Task | Status | Priority |
|------|--------|----------|
| Unit tests | Done | High |
| Integration tests | In Progress | Medium |
| E2E tests | Todo | Low |
    """
    
    # Simulate the pipeline steps
    print("1. Extracting tasks from markdown...")
    tasks = await pipeline.task_extractor.extract_tasks_from_markdown(sample_content)
    
    print("2. Calculating progress...")
    progress = await pipeline.progress_calculator.calculate_progress(tasks)
    
    print("3. Pipeline result:")
    print(f"   - Tasks extracted: {len(tasks)}")
    print(f"   - Progress: {progress.percentage_complete}%")
    print(f"   - Status: {progress.project_status}")
    
    return tasks, progress


async def demo_table_parsing():
    """Demo table parsing functionality."""
    print("\n=== Table Parsing Demo ===")
    
    task_extractor = TaskExtractor()
    
    table_content = """
# Project Roadmap

## Sprint 1
| Feature | Status | Priority | Assignee |
|---------|--------|----------|----------|
| User Authentication | Done | High | Alice |
| Database Schema | In Progress | High | Bob |
| API Documentation | Todo | Medium | Charlie |
| Unit Tests | Blocked | Low | David |

## Sprint 2
| Feature | Status | Priority |
|---------|--------|----------|
| Dashboard UI | Todo | High |
| Data Export | Todo | Medium |
| Performance Optimization | Todo | Low |
    """
    
    tasks = await task_extractor.parse_table_tasks(table_content)
    
    print(f"Extracted {len(tasks)} tasks from tables:")
    for i, task in enumerate(tasks, 1):
        status_emoji = {
            'todo': '⏳',
            'doing': '🔄',
            'done': '✅',
            'blocked': '🚫'
        }.get(task.status, '❓')
        
        print(f"  {i}. {status_emoji} {task.title} ({task.status})")
        if task.priority:
            print(f"     🎯 Priority: {task.priority}")


async def main():
    """Run all demos."""
    print("🚀 RepoTrackr Phase 2: Plan Parsing Engine Demo")
    print("=" * 50)
    
    try:
        # Demo 1: Repository Manager
        content = await demo_repository_manager()
        
        # Demo 2: Task Extractor
        tasks = await demo_task_extractor(content)
        
        # Demo 3: Progress Calculator
        progress = await demo_progress_calculator(tasks)
        
        # Demo 4: Processing Pipeline
        await demo_processing_pipeline()
        
        # Demo 5: Table Parsing
        await demo_table_parsing()
        
        print("\n" + "=" * 50)
        print("✅ All Phase 2 demos completed successfully!")
        print("\nKey Features Demonstrated:")
        print("  • Repository cloning and file discovery")
        print("  • Markdown task extraction (checkboxes & tables)")
        print("  • Progress calculation and status determination")
        print("  • End-to-end processing pipeline")
        print("  • Error handling and validation")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
