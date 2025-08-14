from typing import List, Dict, Optional, Set
from dataclasses import dataclass
import logging
from .manifest_parser import Package

logger = logging.getLogger(__name__)


@dataclass
class Skill:
    """Represents a skill extracted from packages."""
    name: str
    category: str  # language, framework, tool, database, etc.
    confidence: float
    source: str
    aliases: List[str] = None
    
    def __post_init__(self):
        if self.aliases is None:
            self.aliases = []


class SkillMapper:
    """Maps packages to skills and handles categorization."""
    
    def __init__(self):
        # Comprehensive skill mapping database
        self.skill_mappings = {
            # Languages
            'python': {'category': 'language', 'aliases': ['py', 'python3']},
            'javascript': {'category': 'language', 'aliases': ['js', 'node']},
            'typescript': {'category': 'language', 'aliases': ['ts']},
            'rust': {'category': 'language', 'aliases': ['rs']},
            'go': {'category': 'language', 'aliases': ['golang']},
            'java': {'category': 'language', 'aliases': []},
            'c#': {'category': 'language', 'aliases': ['csharp', 'dotnet']},
            'php': {'category': 'language', 'aliases': []},
            'ruby': {'category': 'language', 'aliases': ['rb']},
            'swift': {'category': 'language', 'aliases': []},
            'kotlin': {'category': 'language', 'aliases': ['kt']},
            'scala': {'category': 'language', 'aliases': []},
            
            # Python Frameworks
            'django': {'category': 'framework', 'aliases': ['djangoproject']},
            'flask': {'category': 'framework', 'aliases': ['flask-app']},
            'fastapi': {'category': 'framework', 'aliases': ['fast-api']},
            'uvicorn': {'category': 'framework', 'aliases': ['asgi']},
            'gunicorn': {'category': 'framework', 'aliases': ['wsgi']},
            'tornado': {'category': 'framework', 'aliases': []},
            'aiohttp': {'category': 'framework', 'aliases': ['async-http']},
            'starlette': {'category': 'framework', 'aliases': []},
            'bottle': {'category': 'framework', 'aliases': []},
            'pyramid': {'category': 'framework', 'aliases': []},
            
            # JavaScript/TypeScript Frameworks
            'react': {'category': 'framework', 'aliases': ['reactjs', 'react.js']},
            'vue': {'category': 'framework', 'aliases': ['vuejs', 'vue.js']},
            'angular': {'category': 'framework', 'aliases': ['angularjs']},
            'next': {'category': 'framework', 'aliases': ['nextjs', 'next.js']},
            'nuxt': {'category': 'framework', 'aliases': ['nuxtjs', 'nuxt.js']},
            'express': {'category': 'framework', 'aliases': ['expressjs', 'express.js']},
            'koa': {'category': 'framework', 'aliases': ['koajs']},
            'nest': {'category': 'framework', 'aliases': ['nestjs']},
            'svelte': {'category': 'framework', 'aliases': ['sveltejs']},
            'ember': {'category': 'framework', 'aliases': ['emberjs']},
            'backbone': {'category': 'framework', 'aliases': ['backbonejs']},
            
            # Rust Frameworks
            'actix-web': {'category': 'framework', 'aliases': ['actix']},
            'rocket': {'category': 'framework', 'aliases': ['rocket-rs']},
            'warp': {'category': 'framework', 'aliases': ['warp-rs']},
            'axum': {'category': 'framework', 'aliases': ['axum-rs']},
            'tonic': {'category': 'framework', 'aliases': ['grpc-rs']},
            
            # Go Frameworks
            'gin': {'category': 'framework', 'aliases': ['gin-gonic']},
            'echo': {'category': 'framework', 'aliases': ['echo-framework']},
            'gorilla': {'category': 'framework', 'aliases': ['gorilla-mux']},
            'fiber': {'category': 'framework', 'aliases': ['fiber-go']},
            'chi': {'category': 'framework', 'aliases': ['chi-router']},
            
            # Databases
            'postgresql': {'category': 'database', 'aliases': ['postgres', 'psql']},
            'mysql': {'category': 'database', 'aliases': ['mariadb']},
            'sqlite': {'category': 'database', 'aliases': ['sqlite3']},
            'mongodb': {'category': 'database', 'aliases': ['mongo']},
            'redis': {'category': 'database', 'aliases': ['redis-py']},
            'cassandra': {'category': 'database', 'aliases': ['cassandra-db']},
            'elasticsearch': {'category': 'database', 'aliases': ['elastic', 'es']},
            'influxdb': {'category': 'database', 'aliases': ['influx']},
            'neo4j': {'category': 'database', 'aliases': ['neo4j-db']},
            'dynamodb': {'category': 'database', 'aliases': ['aws-dynamodb']},
            
            # ORMs and Database Tools
            'sqlalchemy': {'category': 'orm', 'aliases': ['sql-alchemy']},
            'alembic': {'category': 'orm', 'aliases': ['db-migration']},
            'prisma': {'category': 'orm', 'aliases': ['prisma-client']},
            'sequelize': {'category': 'orm', 'aliases': ['sequelize-orm']},
            'typeorm': {'category': 'orm', 'aliases': ['type-orm']},
            'gorm': {'category': 'orm', 'aliases': ['gorm-go']},
            'sqlx': {'category': 'orm', 'aliases': ['sqlx-rs']},
            'diesel': {'category': 'orm', 'aliases': ['diesel-rs']},
            
            # Testing Frameworks
            'pytest': {'category': 'testing', 'aliases': ['py-test']},
            'unittest': {'category': 'testing', 'aliases': ['python-testing']},
            'jest': {'category': 'testing', 'aliases': ['jest-testing']},
            'mocha': {'category': 'testing', 'aliases': ['mocha-testing']},
            'cypress': {'category': 'testing', 'aliases': ['cypress-testing']},
            'playwright': {'category': 'testing', 'aliases': ['playwright-testing']},
            'selenium': {'category': 'testing', 'aliases': ['selenium-testing']},
            'testify': {'category': 'testing', 'aliases': ['testify-go']},
            'criterion': {'category': 'testing', 'aliases': ['criterion-rs']},
            
            # Build Tools
            'webpack': {'category': 'build', 'aliases': ['webpack-bundler']},
            'vite': {'category': 'build', 'aliases': ['vite-bundler']},
            'rollup': {'category': 'build', 'aliases': ['rollup-bundler']},
            'parcel': {'category': 'build', 'aliases': ['parcel-bundler']},
            'esbuild': {'category': 'build', 'aliases': ['es-build']},
            'babel': {'category': 'build', 'aliases': ['babel-transpiler']},
            'typescript': {'category': 'build', 'aliases': ['ts-compiler']},
            'swc': {'category': 'build', 'aliases': ['swc-compiler']},
            
            # Package Managers
            'npm': {'category': 'package_manager', 'aliases': ['node-package-manager']},
            'yarn': {'category': 'package_manager', 'aliases': ['yarn-pkg']},
            'pnpm': {'category': 'package_manager', 'aliases': ['pnpm-pkg']},
            'pip': {'category': 'package_manager', 'aliases': ['python-pip']},
            'poetry': {'category': 'package_manager', 'aliases': ['poetry-python']},
            'cargo': {'category': 'package_manager', 'aliases': ['rust-cargo']},
            'go': {'category': 'package_manager', 'aliases': ['golang-mod']},
            
            # Cloud Platforms
            'aws': {'category': 'cloud', 'aliases': ['amazon-web-services']},
            'azure': {'category': 'cloud', 'aliases': ['microsoft-azure']},
            'gcp': {'category': 'cloud', 'aliases': ['google-cloud', 'google-cloud-platform']},
            'heroku': {'category': 'cloud', 'aliases': ['heroku-platform']},
            'vercel': {'category': 'cloud', 'aliases': ['vercel-platform']},
            'netlify': {'category': 'cloud', 'aliases': ['netlify-platform']},
            'digitalocean': {'category': 'cloud', 'aliases': ['do', 'digital-ocean']},
            
            # DevOps Tools
            'docker': {'category': 'devops', 'aliases': ['docker-container']},
            'kubernetes': {'category': 'devops', 'aliases': ['k8s', 'kube']},
            'terraform': {'category': 'devops', 'aliases': ['terraform-iac']},
            'ansible': {'category': 'devops', 'aliases': ['ansible-automation']},
            'jenkins': {'category': 'devops', 'aliases': ['jenkins-ci']},
            'github-actions': {'category': 'devops', 'aliases': ['github-ci']},
            'gitlab-ci': {'category': 'devops', 'aliases': ['gitlab-pipeline']},
            'circleci': {'category': 'devops', 'aliases': ['circle-ci']},
            'travis': {'category': 'devops', 'aliases': ['travis-ci']},
            
            # Monitoring and Logging
            'prometheus': {'category': 'monitoring', 'aliases': ['prometheus-metrics']},
            'grafana': {'category': 'monitoring', 'aliases': ['grafana-dashboard']},
            'datadog': {'category': 'monitoring', 'aliases': ['datadog-apm']},
            'newrelic': {'category': 'monitoring', 'aliases': ['new-relic']},
            'sentry': {'category': 'monitoring', 'aliases': ['sentry-error-tracking']},
            'logstash': {'category': 'monitoring', 'aliases': ['elastic-logstash']},
            'fluentd': {'category': 'monitoring', 'aliases': ['fluent-d']},
            
            # Utilities and Libraries
            'requests': {'category': 'utility', 'aliases': ['python-requests']},
            'axios': {'category': 'utility', 'aliases': ['axios-http']},
            'lodash': {'category': 'utility', 'aliases': ['lodash-js']},
            'moment': {'category': 'utility', 'aliases': ['moment-js']},
            'pandas': {'category': 'utility', 'aliases': ['pandas-data']},
            'numpy': {'category': 'utility', 'aliases': ['numpy-array']},
            'matplotlib': {'category': 'utility', 'aliases': ['matplotlib-plot']},
            'seaborn': {'category': 'utility', 'aliases': ['seaborn-viz']},
            'scikit-learn': {'category': 'utility', 'aliases': ['sklearn', 'scikit']},
            'tensorflow': {'category': 'utility', 'aliases': ['tf', 'tensor-flow']},
            'pytorch': {'category': 'utility', 'aliases': ['torch', 'py-torch']},
        }
        
        # Create reverse mapping for aliases
        self.alias_mappings = {}
        for skill_name, skill_info in self.skill_mappings.items():
            self.alias_mappings[skill_name] = skill_name
            for alias in skill_info['aliases']:
                self.alias_mappings[alias] = skill_name
    
    async def map_package_to_skill(self, package: Package) -> Optional[Skill]:
        """Map a package to a skill."""
        normalized_name = await self.normalize_skill_name(package.name)
        
        if normalized_name in self.skill_mappings:
            skill_info = self.skill_mappings[normalized_name]
            return Skill(
                name=normalized_name,
                category=skill_info['category'],
                confidence=package.confidence,
                source=package.source,
                aliases=skill_info['aliases']
            )
        
        # If not found, try to infer category based on package name patterns
        inferred_category = self._infer_category(package.name)
        if inferred_category:
            return Skill(
                name=normalized_name,
                category=inferred_category,
                confidence=package.confidence * 0.7,  # Lower confidence for inferred
                source=package.source,
                aliases=[]
            )
        
        return None
    
    async def normalize_skill_name(self, name: str) -> str:
        """Normalize skill name for consistent matching."""
        # Convert to lowercase
        normalized = name.lower()
        
        # Remove common prefixes/suffixes
        normalized = normalized.replace('-', '').replace('_', '').replace('.', '')
        
        # Check if it's an alias
        if normalized in self.alias_mappings:
            return self.alias_mappings[normalized]
        
        return normalized
    
    async def deduplicate_skills(self, skills: List[Skill]) -> List[Skill]:
        """Remove duplicate skills and merge confidence scores."""
        skill_map: Dict[str, Skill] = {}
        
        for skill in skills:
            if skill.name in skill_map:
                # Merge skills with same name
                existing = skill_map[skill.name]
                # Take the highest confidence
                existing.confidence = max(existing.confidence, skill.confidence)
                # Merge sources
                if skill.source not in existing.source:
                    existing.source += f", {skill.source}"
            else:
                skill_map[skill.name] = skill
        
        return list(skill_map.values())
    
    def _infer_category(self, package_name: str) -> Optional[str]:
        """Infer category based on package name patterns."""
        name_lower = package_name.lower()
        
        # Language patterns
        if any(lang in name_lower for lang in ['python', 'py-', '-py', 'js-', '-js', 'ts-', '-ts']):
            return 'language'
        
        # Framework patterns
        if any(fw in name_lower for fw in ['framework', 'web', 'api', 'server', 'app']):
            return 'framework'
        
        # Database patterns
        if any(db in name_lower for db in ['db', 'database', 'sql', 'nosql', 'orm', 'model']):
            return 'database'
        
        # Testing patterns
        if any(test in name_lower for test in ['test', 'spec', 'mock', 'stub', 'fixture']):
            return 'testing'
        
        # Build patterns
        if any(build in name_lower for build in ['build', 'bundle', 'compile', 'transpile']):
            return 'build'
        
        # Cloud patterns
        if any(cloud in name_lower for cloud in ['aws', 'azure', 'gcp', 'cloud', 'serverless']):
            return 'cloud'
        
        # DevOps patterns
        if any(devops in name_lower for devops in ['deploy', 'ci', 'cd', 'pipeline', 'docker', 'k8s']):
            return 'devops'
        
        # Monitoring patterns
        if any(monitor in name_lower for monitor in ['log', 'metric', 'monitor', 'trace', 'alert']):
            return 'monitoring'
        
        return 'utility'  # Default category
    
    async def get_skill_categories(self) -> List[str]:
        """Get all available skill categories."""
        categories = set()
        for skill_info in self.skill_mappings.values():
            categories.add(skill_info['category'])
        return sorted(list(categories))
    
    async def get_popular_skills(self, limit: int = 20) -> List[str]:
        """Get list of popular skills."""
        # This could be enhanced with actual usage statistics
        popular_skills = [
            'python', 'javascript', 'react', 'django', 'docker', 'postgresql',
            'typescript', 'fastapi', 'vue', 'express', 'redis', 'pytest',
            'next', 'flask', 'mongodb', 'jest', 'webpack', 'kubernetes',
            'aws', 'terraform', 'prometheus', 'grafana'
        ]
        return popular_skills[:limit]
