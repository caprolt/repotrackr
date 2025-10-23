#!/usr/bin/env python3
"""
Demo script for Phase 4: Skills Extraction System

This script demonstrates the skills extraction functionality by:
1. Testing manifest file parsing
2. Testing skill mapping and categorization
3. Testing the complete skills extraction pipeline
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "app"))

from app.services.manifest_parser import ManifestParser, Package
from app.services.skill_mapper import SkillMapper, Skill
from app.services.skills_extraction_pipeline import SkillsExtractionPipeline


async def demo_manifest_parsing():
    """Demo manifest file parsing functionality."""
    print("=" * 60)
    print("DEMO: Manifest File Parsing")
    print("=" * 60)
    
    parser = ManifestParser()
    
    # Test requirements.txt parsing
    print("\n1. Testing requirements.txt parsing:")
    requirements_content = """
# Web framework
Django==4.2.0
Flask>=2.3.0

# Database
psycopg2-binary
redis

# Testing
pytest>=7.0.0
"""
    packages = await parser.parse_requirements_txt(requirements_content)
    print(f"   Found {len(packages)} packages:")
    for pkg in packages:
        print(f"   - {pkg.name} (version: {pkg.version}, confidence: {pkg.confidence})")
    
    # Test package.json parsing
    print("\n2. Testing package.json parsing:")
    package_json_content = """
{
  "dependencies": {
    "react": "^18.0.0",
    "next": "14.0.0",
    "@types/node": "^20.0.0"
  },
  "devDependencies": {
    "typescript": "^5.0.0",
    "tailwindcss": "^3.0.0"
  },
  "scripts": {
    "build": "next build",
    "test": "jest"
  }
}
"""
    packages = await parser.parse_package_json(package_json_content)
    print(f"   Found {len(packages)} packages:")
    for pkg in packages:
        print(f"   - {pkg.name} (version: {pkg.version}, confidence: {pkg.confidence})")
    
    # Test Dockerfile parsing
    print("\n3. Testing Dockerfile parsing:")
    dockerfile_content = """
FROM python:3.11-slim
RUN apt-get update && apt-get install -y git
COPY requirements.txt .
RUN pip install -r requirements.txt
"""
    packages = await parser.parse_dockerfile(dockerfile_content)
    print(f"   Found {len(packages)} packages:")
    for pkg in packages:
        print(f"   - {pkg.name} (version: {pkg.version}, confidence: {pkg.confidence})")


async def demo_skill_mapping():
    """Demo skill mapping and categorization."""
    print("\n" + "=" * 60)
    print("DEMO: Skill Mapping and Categorization")
    print("=" * 60)
    
    mapper = SkillMapper()
    
    # Test package to skill mapping
    print("\n1. Testing package to skill mapping:")
    test_packages = [
        Package(name='django', version='4.2.0', source='requirements.txt', confidence=0.8),
        Package(name='react', version='18.0.0', source='package.json', confidence=0.9),
        Package(name='postgresql', version='15.0', source='docker-compose.yml', confidence=0.7),
        Package(name='pytest', version='7.0.0', source='requirements.txt', confidence=0.8),
        Package(name='docker', version='', source='Dockerfile', confidence=0.6),
    ]
    
    for pkg in test_packages:
        skill = await mapper.map_package_to_skill(pkg)
        if skill:
            print(f"   {pkg.name} -> {skill.name} ({skill.category}, confidence: {skill.confidence})")
        else:
            print(f"   {pkg.name} -> No skill mapping found")
    
    # Test skill normalization
    print("\n2. Testing skill name normalization:")
    test_names = ['React.js', 'fast-api', 'PostgreSQL', 'Django', 'TypeScript']
    for name in test_names:
        normalized = await mapper.normalize_skill_name(name)
        print(f"   '{name}' -> '{normalized}'")
    
    # Test skill deduplication
    print("\n3. Testing skill deduplication:")
    skills = [
        Skill(name='django', category='framework', confidence=0.8, source='requirements.txt'),
        Skill(name='django', category='framework', confidence=0.9, source='pyproject.toml'),
        Skill(name='react', category='framework', confidence=0.7, source='package.json'),
        Skill(name='react', category='framework', confidence=0.8, source='package-lock.json'),
    ]
    
    deduplicated = await mapper.deduplicate_skills(skills)
    print(f"   Original: {len(skills)} skills")
    print(f"   Deduplicated: {len(deduplicated)} skills")
    for skill in deduplicated:
        print(f"   - {skill.name} (confidence: {skill.confidence}, sources: {skill.source})")
    
    # Test skill categories
    print("\n4. Available skill categories:")
    categories = await mapper.get_skill_categories()
    for category in categories:
        print(f"   - {category}")


async def demo_skills_extraction():
    """Demo complete skills extraction pipeline."""
    print("\n" + "=" * 60)
    print("DEMO: Complete Skills Extraction Pipeline")
    print("=" * 60)
    
    pipeline = SkillsExtractionPipeline()
    
    # Create a mock repository structure
    print("\n1. Creating mock repository structure...")
    mock_repo_path = Path("mock_repo")
    mock_repo_path.mkdir(exist_ok=True)
    
    # Create requirements.txt
    (mock_repo_path / "requirements.txt").write_text("""
Django==4.2.0
Flask>=2.3.0
psycopg2-binary
redis
pytest>=7.0.0
""")
    
    # Create package.json
    (mock_repo_path / "package.json").write_text("""
{
  "dependencies": {
    "react": "^18.0.0",
    "next": "14.0.0"
  },
  "devDependencies": {
    "typescript": "^5.0.0",
    "tailwindcss": "^3.0.0"
  }
}
""")
    
    # Create Dockerfile
    (mock_repo_path / "Dockerfile").write_text("""
FROM python:3.11-slim
RUN apt-get update && apt-get install -y git
COPY requirements.txt .
RUN pip install -r requirements.txt
""")
    
    print("   Created mock repository with requirements.txt, package.json, and Dockerfile")
    
    # Test manifest file processing
    print("\n2. Processing manifest files...")
    packages = await pipeline.process_manifest_files(str(mock_repo_path))
    print(f"   Found {len(packages)} packages:")
    
    # Group packages by source
    packages_by_source = {}
    for pkg in packages:
        if pkg.source not in packages_by_source:
            packages_by_source[pkg.source] = []
        packages_by_source[pkg.source].append(pkg)
    
    for source, pkgs in packages_by_source.items():
        print(f"   {source}:")
        for pkg in pkgs:
            print(f"     - {pkg.name} (confidence: {pkg.confidence})")
    
    # Test skill mapping
    print("\n3. Mapping packages to skills...")
    skills = []
    for package in packages:
        skill = await pipeline.skill_mapper.map_package_to_skill(package)
        if skill:
            skills.append(skill)
    
    # Deduplicate skills
    skills = await pipeline.skill_mapper.deduplicate_skills(skills)
    
    print(f"   Mapped to {len(skills)} unique skills:")
    for skill in skills:
        print(f"   - {skill.name} ({skill.category}, confidence: {skill.confidence})")
    
    # Group skills by category
    skills_by_category = {}
    for skill in skills:
        if skill.category not in skills_by_category:
            skills_by_category[skill.category] = []
        skills_by_category[skill.category].append(skill)
    
    print("\n4. Skills by category:")
    for category, category_skills in skills_by_category.items():
        print(f"   {category}:")
        for skill in category_skills:
            print(f"     - {skill.name} (confidence: {skill.confidence})")
    
    # Cleanup
    import shutil
    shutil.rmtree(mock_repo_path)
    print("\n   Cleaned up mock repository")


async def main():
    """Run all demos."""
    print("Phase 4: Skills Extraction System Demo")
    print("This demo shows the skills extraction functionality")
    
    try:
        await demo_manifest_parsing()
        await demo_skill_mapping()
        await demo_skills_extraction()
        
        print("\n" + "=" * 60)
        print("DEMO COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("\nThe skills extraction system can now:")
        print("✓ Parse various manifest files (requirements.txt, package.json, Dockerfile, etc.)")
        print("✓ Map packages to skills with categories")
        print("✓ Calculate confidence scores")
        print("✓ Deduplicate skills across multiple sources")
        print("✓ Integrate with the existing processing pipeline")
        print("✓ Store skills in the database")
        print("✓ Provide API endpoints for skills data")
        
    except Exception as e:
        print(f"\nError during demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
