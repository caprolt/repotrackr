import uuid
from typing import List, Optional
from pathlib import Path
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from app.db.models import Skill as DBSkill
from app.services.manifest_parser import ManifestParser, Package
from app.services.skill_mapper import SkillMapper, Skill
from app.services.repository_manager import RepositoryManager

logger = logging.getLogger(__name__)


class SkillsExtractionPipeline:
    """Pipeline for extracting skills from project repositories."""
    
    def __init__(self):
        self.manifest_parser = ManifestParser()
        self.skill_mapper = SkillMapper()
        self.repository_manager = RepositoryManager()
    
    async def extract_skills_from_project(self, project_id: str, repo_path: str, db: AsyncSession) -> List[Skill]:
        """
        Extract skills from a project repository.
        
        Args:
            project_id: The project ID
            repo_path: Path to the cloned repository
            db: Database session
            
        Returns:
            List of extracted skills
        """
        try:
            logger.info(f"Starting skills extraction for project {project_id}")
            
            # Discover and parse manifest files
            packages = await self.process_manifest_files(repo_path)
            
            # Map packages to skills
            skills = []
            for package in packages:
                skill = await self.skill_mapper.map_package_to_skill(package)
                if skill:
                    skills.append(skill)
            
            # Deduplicate skills
            skills = await self.skill_mapper.deduplicate_skills(skills)
            
            # Store skills in database
            await self.store_skills(project_id, skills, db)
            
            logger.info(f"Successfully extracted {len(skills)} skills for project {project_id}")
            return skills
            
        except Exception as e:
            logger.error(f"Failed to extract skills for project {project_id}: {e}")
            raise e
    
    async def process_manifest_files(self, repo_path: str) -> List[Package]:
        """
        Process all manifest files in the repository.
        
        Args:
            repo_path: Path to the repository
            
        Returns:
            List of extracted packages
        """
        packages = []
        repo_path_obj = Path(repo_path)
        
        # Define manifest file patterns
        manifest_patterns = {
            'requirements.txt': self.manifest_parser.parse_requirements_txt,
            'package.json': self.manifest_parser.parse_package_json,
            'pyproject.toml': self.manifest_parser.parse_pyproject_toml,
            'Cargo.toml': self.manifest_parser.parse_cargo_toml,
            'go.mod': self.manifest_parser.parse_go_mod,
        }
        
        # Find and parse manifest files
        for filename, parser_func in manifest_patterns.items():
            file_paths = list(repo_path_obj.rglob(filename))
            
            for file_path in file_paths:
                try:
                    # Read file content
                    content = await self.repository_manager.get_file_content(str(repo_path), str(file_path.relative_to(repo_path_obj)))
                    
                    # Parse file
                    file_packages = await parser_func(content)
                    packages.extend(file_packages)
                    
                    logger.debug(f"Parsed {filename}: {len(file_packages)} packages")
                    
                except Exception as e:
                    logger.warning(f"Failed to parse {file_path}: {e}")
        
        # Parse Dockerfiles
        dockerfile_paths = list(repo_path_obj.rglob('Dockerfile'))
        for dockerfile_path in dockerfile_paths:
            try:
                content = await self.repository_manager.get_file_content(str(repo_path), str(dockerfile_path.relative_to(repo_path_obj)))
                dockerfile_packages = await self.manifest_parser.parse_dockerfile(content)
                packages.extend(dockerfile_packages)
                
                logger.debug(f"Parsed Dockerfile: {len(dockerfile_packages)} packages")
                
            except Exception as e:
                logger.warning(f"Failed to parse Dockerfile {dockerfile_path}: {e}")
        
        return packages
    
    async def store_skills(self, project_id: str, skills: List[Skill], db: AsyncSession) -> None:
        """
        Store skills in the database.
        
        Args:
            project_id: The project ID
            skills: List of skills to store
            db: Database session
        """
        try:
            project_uuid = uuid.UUID(project_id)
        except ValueError:
            raise ValueError("Invalid project ID format")
        
        # Clear existing skills for this project
        await db.execute(
            delete(DBSkill).where(DBSkill.project_id == project_uuid)
        )
        
        # Store new skills
        for skill in skills:
            db_skill = DBSkill(
                project_id=project_uuid,
                name=skill.name,
                category=skill.category,
                source=skill.source,
                confidence=skill.confidence
            )
            db.add(db_skill)
        
        await db.commit()
        logger.info(f"Stored {len(skills)} skills for project {project_id}")
    
    async def get_project_skills(self, project_id: str, db: AsyncSession) -> List[Skill]:
        """
        Get skills for a project from the database.
        
        Args:
            project_id: The project ID
            db: Database session
            
        Returns:
            List of skills
        """
        try:
            project_uuid = uuid.UUID(project_id)
        except ValueError:
            raise ValueError("Invalid project ID format")
        
        result = await db.execute(
            select(DBSkill).where(DBSkill.project_id == project_uuid)
        )
        db_skills = result.scalars().all()
        
        skills = []
        for db_skill in db_skills:
            skill = Skill(
                name=db_skill.name,
                category=db_skill.category,
                confidence=float(db_skill.confidence) if db_skill.confidence else 0.5,
                source=db_skill.source,
                aliases=[]
            )
            skills.append(skill)
        
        return skills
    
    async def get_skills_by_category(self, db: AsyncSession) -> dict:
        """
        Get skills grouped by category across all projects.
        
        Args:
            db: Database session
            
        Returns:
            Dictionary with categories as keys and skill counts as values
        """
        result = await db.execute(
            select(DBSkill.category, DBSkill.name)
        )
        skills = result.all()
        
        categories = {}
        for category, name in skills:
            if category not in categories:
                categories[category] = {}
            if name not in categories[category]:
                categories[category][name] = 0
            categories[category][name] += 1
        
        return categories
    
    async def get_popular_skills(self, db: AsyncSession, limit: int = 20) -> List[dict]:
        """
        Get most popular skills across all projects.
        
        Args:
            db: Database session
            limit: Maximum number of skills to return
            
        Returns:
            List of popular skills with counts
        """
        result = await db.execute(
            select(DBSkill.name, DBSkill.category)
        )
        skills = result.all()
        
        skill_counts = {}
        for name, category in skills:
            if name not in skill_counts:
                skill_counts[name] = {'name': name, 'category': category, 'count': 0}
            skill_counts[name]['count'] += 1
        
        # Sort by count and return top skills
        popular_skills = sorted(
            skill_counts.values(),
            key=lambda x: x['count'],
            reverse=True
        )
        
        return popular_skills[:limit]
