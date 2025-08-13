import os
import tempfile
import shutil
from typing import Optional
from pathlib import Path
from git import Repo, GitCommandError
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)


class RepositoryManager:
    """Manages repository cloning, file discovery, and cleanup operations."""
    
    def __init__(self, temp_dir: Optional[str] = None):
        self.temp_dir = temp_dir or tempfile.gettempdir()
        self.repo_cache = {}  # Simple in-memory cache
    
    async def clone_repository(self, repo_url: str) -> str:
        """
        Clone a repository to a temporary directory.
        
        Args:
            repo_url: The repository URL to clone
            
        Returns:
            Path to the cloned repository
            
        Raises:
            HTTPException: If cloning fails
        """
        try:
            # Create a unique temporary directory for this clone
            repo_name = repo_url.split('/')[-1].replace('.git', '')
            temp_path = Path(self.temp_dir) / f"repotrackr_{repo_name}_{os.getpid()}"
            
            # Remove existing directory if it exists
            if temp_path.exists():
                shutil.rmtree(temp_path)
            
            temp_path.mkdir(parents=True, exist_ok=True)
            
            logger.info(f"Cloning repository: {repo_url} to {temp_path}")
            
            # Perform shallow clone for performance
            repo = Repo.clone_from(
                repo_url,
                temp_path,
                depth=1,  # Shallow clone
                single_branch=True
            )
            
            # Cache the repository path
            self.repo_cache[repo_url] = str(temp_path)
            
            logger.info(f"Successfully cloned repository to {temp_path}")
            return str(temp_path)
            
        except GitCommandError as e:
            logger.error(f"Failed to clone repository {repo_url}: {e}")
            raise HTTPException(
                status_code=400,
                detail=f"Failed to clone repository: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Unexpected error cloning repository {repo_url}: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Unexpected error cloning repository: {str(e)}"
            )
    
    async def discover_plan_file(self, repo_path: str) -> Optional[str]:
        """
        Discover the plan file in the repository.
        
        Args:
            repo_path: Path to the cloned repository
            
        Returns:
            Path to the plan file if found, None otherwise
        """
        repo_path = Path(repo_path)
        
        # Priority order for plan file locations
        plan_locations = [
            "docs/plan.md",
            "plan.md",
            "README.md"
        ]
        
        for location in plan_locations:
            file_path = repo_path / location
            if file_path.exists() and file_path.is_file():
                logger.info(f"Found plan file at: {file_path}")
                return str(file_path)
        
        logger.warning(f"No plan file found in repository: {repo_path}")
        return None
    
    async def get_file_content(self, repo_path: str, file_path: str) -> str:
        """
        Get the content of a file from the repository.
        
        Args:
            repo_path: Path to the cloned repository
            file_path: Path to the file relative to repo root
            
        Returns:
            File content as string
            
        Raises:
            HTTPException: If file cannot be read
        """
        try:
            full_path = Path(repo_path) / file_path
            if not full_path.exists():
                raise HTTPException(
                    status_code=404,
                    detail=f"File not found: {file_path}"
                )
            
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return content
            
        except UnicodeDecodeError:
            # Try with different encoding
            try:
                with open(full_path, 'r', encoding='latin-1') as f:
                    content = f.read()
                return content
            except Exception as e:
                logger.error(f"Failed to read file {file_path}: {e}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to read file: {str(e)}"
                )
        except Exception as e:
            logger.error(f"Failed to read file {file_path}: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to read file: {str(e)}"
            )
    
    async def cleanup_repository(self, repo_path: str) -> None:
        """
        Clean up a cloned repository.
        
        Args:
            repo_path: Path to the repository to clean up
        """
        try:
            if repo_path and Path(repo_path).exists():
                shutil.rmtree(repo_path)
                logger.info(f"Cleaned up repository: {repo_path}")
                
                # Remove from cache
                for url, path in list(self.repo_cache.items()):
                    if path == repo_path:
                        del self.repo_cache[url]
                        
        except Exception as e:
            logger.error(f"Failed to cleanup repository {repo_path}: {e}")
    
    async def cleanup_all(self) -> None:
        """Clean up all cached repositories."""
        for repo_path in list(self.repo_cache.values()):
            await self.cleanup_repository(repo_path)
        self.repo_cache.clear()
