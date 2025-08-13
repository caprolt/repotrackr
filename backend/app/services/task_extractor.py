import re
from typing import List, Optional
from dataclasses import dataclass
from markdown_it import MarkdownIt
from markdown_it.tree import SyntaxTreeNode
import logging

logger = logging.getLogger(__name__)


@dataclass
class Task:
    """Represents a task extracted from markdown content."""
    title: str
    status: str  # 'todo', 'doing', 'done', 'blocked'
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    priority: Optional[str] = None
    description: Optional[str] = None


class TaskExtractor:
    """Extracts tasks from markdown content using various parsing strategies."""
    
    def __init__(self):
        self.md = MarkdownIt()
        self.checkbox_patterns = {
            r'- \[ \] (.+)': 'todo',
            r'- \[x\] (.+)': 'done',
            r'- \[~\] (.+)': 'doing',
            r'- \[!\] (.+)': 'blocked',
            r'- \[X\] (.+)': 'done',  # Alternative uppercase
            r'- \[-\] (.+)': 'doing',  # Alternative doing
        }
    
    async def extract_tasks_from_markdown(self, content: str, file_path: Optional[str] = None) -> List[Task]:
        """
        Extract tasks from markdown content using multiple parsing strategies.
        
        Args:
            content: The markdown content to parse
            file_path: Optional file path for task context
            
        Returns:
            List of extracted tasks
        """
        tasks = []
        
        # Parse checkbox tasks
        checkbox_tasks = await self.parse_checkbox_tasks(content, file_path)
        tasks.extend(checkbox_tasks)
        
        # Parse table tasks
        table_tasks = await self.parse_table_tasks(content, file_path)
        tasks.extend(table_tasks)
        
        # Validate and deduplicate tasks
        valid_tasks = []
        seen_titles = set()
        
        for task in tasks:
            if await self.validate_task(task) and task.title not in seen_titles:
                valid_tasks.append(task)
                seen_titles.add(task.title)
        
        logger.info(f"Extracted {len(valid_tasks)} tasks from {file_path or 'content'}")
        return valid_tasks
    
    async def parse_checkbox_tasks(self, content: str, file_path: Optional[str] = None) -> List[Task]:
        """
        Parse checkbox-style tasks from markdown content.
        
        Args:
            content: The markdown content to parse
            file_path: Optional file path for task context
            
        Returns:
            List of checkbox tasks
        """
        tasks = []
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            
            for pattern, status in self.checkbox_patterns.items():
                match = re.match(pattern, line)
                if match:
                    title = match.group(1).strip()
                    
                    # Extract additional information from the title
                    priority = self._extract_priority(title)
                    description = self._extract_description(title)
                    
                    # Clean up the title
                    clean_title = self._clean_title(title)
                    
                    task = Task(
                        title=clean_title,
                        status=status,
                        file_path=file_path,
                        line_number=line_num,
                        priority=priority,
                        description=description
                    )
                    
                    tasks.append(task)
                    break
        
        return tasks
    
    async def parse_table_tasks(self, content: str, file_path: Optional[str] = None) -> List[Task]:
        """
        Parse table-style tasks from markdown content.
        
        Args:
            content: The markdown content to parse
            file_path: Optional file path for task context
            
        Returns:
            List of table tasks
        """
        tasks = []
        
        try:
            # Parse markdown to get table structure
            tokens = self.md.parse(content)
            
            for token in tokens:
                if token.type == 'table_open':
                    # Find the table content
                    table_tasks = self._extract_tasks_from_table(token, file_path)
                    tasks.extend(table_tasks)
        
        except Exception as e:
            logger.warning(f"Failed to parse table tasks: {e}")
        
        return tasks
    
    def _extract_tasks_from_table(self, table_token, file_path: Optional[str] = None) -> List[Task]:
        """Extract tasks from a markdown table token."""
        tasks = []
        
        try:
            # Find table rows
            rows = []
            for child in table_token.children:
                if child.type == 'tr_open':
                    row = []
                    for cell in child.children:
                        if cell.type == 'td_open':
                            # Get cell content
                            content = cell.content if hasattr(cell, 'content') else ''
                            row.append(content.strip())
                    if row:
                        rows.append(row)
            
            if len(rows) < 2:  # Need header + at least one data row
                return tasks
            
            # Parse header to find column indices
            header = rows[0]
            task_col = self._find_column_index(header, ['task', 'title', 'description', 'item'])
            status_col = self._find_column_index(header, ['status', 'state', 'progress'])
            priority_col = self._find_column_index(header, ['priority', 'importance'])
            
            # Process data rows
            for row in rows[1:]:
                if len(row) <= max(task_col, status_col, priority_col):
                    continue
                
                title = row[task_col] if task_col < len(row) else ''
                status_text = row[status_col] if status_col < len(row) else ''
                priority = row[priority_col] if priority_col < len(row) else ''
                
                if not title:
                    continue
                
                # Map status text to our status enum
                status = self._map_status_text(status_text)
                
                task = Task(
                    title=title.strip(),
                    status=status,
                    file_path=file_path,
                    priority=priority.strip() if priority else None
                )
                
                tasks.append(task)
        
        except Exception as e:
            logger.warning(f"Failed to extract tasks from table: {e}")
        
        return tasks
    
    def _find_column_index(self, header: List[str], possible_names: List[str]) -> int:
        """Find the index of a column by matching possible header names."""
        for i, col in enumerate(header):
            if any(name.lower() in col.lower() for name in possible_names):
                return i
        return 0  # Default to first column
    
    def _map_status_text(self, status_text: str) -> str:
        """Map status text to our status enum."""
        status_text = status_text.lower().strip()
        
        status_mapping = {
            'done': 'done',
            'completed': 'done',
            'finished': 'done',
            'complete': 'done',
            'todo': 'todo',
            'pending': 'todo',
            'not started': 'todo',
            'doing': 'doing',
            'in progress': 'doing',
            'working': 'doing',
            'blocked': 'blocked',
            'stuck': 'blocked',
            'waiting': 'blocked'
        }
        
        return status_mapping.get(status_text, 'todo')
    
    def _extract_priority(self, title: str) -> Optional[str]:
        """Extract priority information from task title."""
        priority_patterns = [
            r'\[(high|medium|low|urgent|critical)\]',
            r'\((high|medium|low|urgent|critical)\)',
            r'#(high|medium|low|urgent|critical)'
        ]
        
        for pattern in priority_patterns:
            match = re.search(pattern, title, re.IGNORECASE)
            if match:
                return match.group(1).lower()
        
        return None
    
    def _extract_description(self, title: str) -> Optional[str]:
        """Extract description from task title (text after colon or dash)."""
        # Look for descriptions after colons or dashes
        patterns = [
            r'^[^:]+:\s*(.+)',
            r'^[^-]+-\s*(.+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, title)
            if match:
                desc = match.group(1).strip()
                # Remove priority tags from description
                desc = re.sub(r'\[(high|medium|low|urgent|critical)\]', '', desc, flags=re.IGNORECASE)
                desc = re.sub(r'\((high|medium|low|urgent|critical)\)', '', desc, flags=re.IGNORECASE)
                desc = re.sub(r'#(high|medium|low|urgent|critical)', '', desc, flags=re.IGNORECASE)
                return desc.strip()
        
        return None
    
    def _clean_title(self, title: str) -> str:
        """Clean up task title by removing priority tags and descriptions."""
        # Remove priority tags
        title = re.sub(r'\[(high|medium|low|urgent|critical)\]', '', title, flags=re.IGNORECASE)
        title = re.sub(r'\((high|medium|low|urgent|critical)\)', '', title, flags=re.IGNORECASE)
        title = re.sub(r'#(high|medium|low|urgent|critical)', '', title, flags=re.IGNORECASE)
        
        # Remove description part (after colon or dash)
        title = re.sub(r':\s*.*$', '', title)
        title = re.sub(r'-\s*.*$', '', title)
        
        return title.strip()
    
    async def validate_task(self, task: Task) -> bool:
        """
        Validate a task to ensure it meets our requirements.
        
        Args:
            task: The task to validate
            
        Returns:
            True if task is valid, False otherwise
        """
        # Check required fields
        if not task.title or not task.title.strip():
            return False
        
        # Check status is valid
        valid_statuses = ['todo', 'doing', 'done', 'blocked']
        if task.status not in valid_statuses:
            return False
        
        # Check title length
        if len(task.title) > 500:  # Reasonable limit
            return False
        
        return True
