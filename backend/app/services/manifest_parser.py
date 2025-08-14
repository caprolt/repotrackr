import re
import json
import tomli
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


@dataclass
class Package:
    """Represents a package extracted from a manifest file."""
    name: str
    version: Optional[str] = None
    source: str = ""  # filename
    category: Optional[str] = None
    confidence: float = 0.5


class ManifestParser:
    """Parser for various manifest files to extract package dependencies."""
    
    def __init__(self):
        # Popular packages for confidence scoring
        self.popular_packages = {
            # Python packages
            'django', 'flask', 'fastapi', 'requests', 'pandas', 'numpy', 'pytest',
            'sqlalchemy', 'alembic', 'psycopg2', 'redis', 'celery', 'uvicorn',
            # Node.js packages
            'react', 'vue', 'angular', 'express', 'next', 'typescript', 'jest',
            'tailwindcss', 'axios', 'lodash', 'moment', 'webpack', 'vite',
            # Rust packages
            'tokio', 'serde', 'actix-web', 'sqlx', 'clap', 'reqwest',
            # Go packages
            'gin', 'echo', 'gorilla', 'gorm', 'testify',
            # Tools
            'docker', 'git', 'npm', 'pip', 'cargo', 'go'
        }
        
        # Reliable source files for confidence scoring
        self.reliable_sources = {
            'requirements.txt', 'package.json', 'pyproject.toml', 'Cargo.toml',
            'go.mod', 'Dockerfile', 'docker-compose.yml'
        }
    
    async def parse_requirements_txt(self, content: str) -> List[Package]:
        """Parse Python requirements.txt file."""
        packages = []
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Skip comments and empty lines
            if not line or line.startswith('#'):
                continue
            
            # Parse package specification
            # Format: package==version, package>=version, package, etc.
            match = re.match(r'^([a-zA-Z0-9_-]+)(.*)$', line)
            if match:
                name = match.group(1).lower()
                version_spec = match.group(2).strip()
                
                # Extract version if present
                version = None
                if version_spec:
                    # Remove version specifiers like ==, >=, <=, ~=, etc.
                    version_match = re.match(r'^[=<>~!]+(.+)$', version_spec)
                    if version_match:
                        version = version_match.group(1)
                
                confidence = self._calculate_confidence(name, 'requirements.txt')
                packages.append(Package(
                    name=name,
                    version=version,
                    source='requirements.txt',
                    confidence=confidence
                ))
        
        return packages
    
    async def parse_package_json(self, content: str) -> List[Package]:
        """Parse Node.js package.json file."""
        packages = []
        
        try:
            data = json.loads(content)
            
            # Parse dependencies
            for dep_type in ['dependencies', 'devDependencies', 'peerDependencies']:
                if dep_type in data:
                    for name, version_spec in data[dep_type].items():
                        name = name.lower()
                        
                        # Extract version from spec
                        version = None
                        if version_spec and version_spec != '*':
                            # Remove ^, ~, >, <, etc.
                            version_match = re.match(r'^[^0-9]*([0-9].*)$', version_spec)
                            if version_match:
                                version = version_match.group(1)
                        
                        confidence = self._calculate_confidence(name, 'package.json')
                        packages.append(Package(
                            name=name,
                            version=version,
                            source='package.json',
                            confidence=confidence
                        ))
            
            # Parse scripts for tool detection
            if 'scripts' in data:
                scripts = data['scripts']
                script_content = ' '.join(scripts.values()).lower()
                
                # Detect tools from scripts
                tools = self._detect_tools_from_scripts(script_content)
                for tool in tools:
                    confidence = self._calculate_confidence(tool, 'package.json')
                    packages.append(Package(
                        name=tool,
                        source='package.json',
                        confidence=confidence
                    ))
                    
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse package.json: {e}")
        
        return packages
    
    async def parse_dockerfile(self, content: str) -> List[Package]:
        """Parse Dockerfile to extract base images and tools."""
        packages = []
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Skip comments and empty lines
            if not line or line.startswith('#'):
                continue
            
            # Parse FROM instruction
            if line.upper().startswith('FROM '):
                image_spec = line[5:].strip()
                # Extract base image name
                image_name = image_spec.split(':')[0].split('/')[-1].lower()
                
                confidence = self._calculate_confidence(image_name, 'Dockerfile')
                packages.append(Package(
                    name=image_name,
                    source='Dockerfile',
                    confidence=confidence
                ))
            
            # Parse RUN instructions for tool detection
            elif line.upper().startswith('RUN '):
                run_command = line[4:].strip()
                tools = self._detect_tools_from_command(run_command)
                for tool in tools:
                    confidence = self._calculate_confidence(tool, 'Dockerfile')
                    packages.append(Package(
                        name=tool,
                        source='Dockerfile',
                        confidence=confidence
                    ))
        
        return packages
    
    async def parse_pyproject_toml(self, content: str) -> List[Package]:
        """Parse Python pyproject.toml file."""
        packages = []
        
        try:
            data = tomli.loads(content)
            
            # Parse dependencies from [project] section
            if 'project' in data and 'dependencies' in data['project']:
                for dep in data['project']['dependencies']:
                    name = dep.split('>=')[0].split('<=')[0].split('==')[0].split('~=')[0].strip().lower()
                    confidence = self._calculate_confidence(name, 'pyproject.toml')
                    packages.append(Package(
                        name=name,
                        source='pyproject.toml',
                        confidence=confidence
                    ))
            
            # Parse optional dependencies
            if 'project' in data and 'optional-dependencies' in data['project']:
                for group, deps in data['project']['optional-dependencies'].items():
                    for dep in deps:
                        name = dep.split('>=')[0].split('<=')[0].split('==')[0].split('~=')[0].strip().lower()
                        confidence = self._calculate_confidence(name, 'pyproject.toml')
                        packages.append(Package(
                            name=name,
                            source='pyproject.toml',
                            confidence=confidence
                        ))
            
            # Parse build-system dependencies
            if 'build-system' in data and 'requires' in data['build-system']:
                for dep in data['build-system']['requires']:
                    name = dep.split('>=')[0].split('<=')[0].split('==')[0].split('~=')[0].strip().lower()
                    confidence = self._calculate_confidence(name, 'pyproject.toml')
                    packages.append(Package(
                        name=name,
                        source='pyproject.toml',
                        confidence=confidence
                    ))
                    
        except Exception as e:
            logger.warning(f"Failed to parse pyproject.toml: {e}")
        
        return packages
    
    async def parse_cargo_toml(self, content: str) -> List[Package]:
        """Parse Rust Cargo.toml file."""
        packages = []
        
        try:
            data = tomli.loads(content)
            
            # Parse dependencies
            if 'dependencies' in data:
                for name, spec in data['dependencies'].items():
                    name = name.lower()
                    confidence = self._calculate_confidence(name, 'Cargo.toml')
                    packages.append(Package(
                        name=name,
                        source='Cargo.toml',
                        confidence=confidence
                    ))
            
            # Parse dev-dependencies
            if 'dev-dependencies' in data:
                for name, spec in data['dev-dependencies'].items():
                    name = name.lower()
                    confidence = self._calculate_confidence(name, 'Cargo.toml')
                    packages.append(Package(
                        name=name,
                        source='Cargo.toml',
                        confidence=confidence
                    ))
                    
        except Exception as e:
            logger.warning(f"Failed to parse Cargo.toml: {e}")
        
        return packages
    
    async def parse_go_mod(self, content: str) -> List[Package]:
        """Parse Go go.mod file."""
        packages = []
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Skip comments and empty lines
            if not line or line.startswith('//'):
                continue
            
            # Parse require statements
            if line.startswith('require '):
                # Format: require module/path v1.2.3
                parts = line.split()
                if len(parts) >= 3:
                    module_path = parts[1]
                    # Extract module name from path
                    module_name = module_path.split('/')[-1].lower()
                    confidence = self._calculate_confidence(module_name, 'go.mod')
                    packages.append(Package(
                        name=module_name,
                        source='go.mod',
                        confidence=confidence
                    ))
        
        return packages
    
    def _calculate_confidence(self, package_name: str, source: str) -> float:
        """Calculate confidence score for a package."""
        base_confidence = 0.5
        
        # Popularity boost
        if package_name in self.popular_packages:
            base_confidence += 0.3
        
        # Source file reliability
        if source in self.reliable_sources:
            base_confidence += 0.1
        
        # Version specificity (handled in individual parsers)
        
        return min(base_confidence, 1.0)
    
    def _detect_tools_from_scripts(self, script_content: str) -> List[str]:
        """Detect tools from npm scripts content."""
        tools = []
        
        # Common tools in scripts
        script_tools = {
            'webpack', 'vite', 'rollup', 'jest', 'mocha', 'cypress', 'eslint',
            'prettier', 'typescript', 'babel', 'postcss', 'tailwindcss'
        }
        
        for tool in script_tools:
            if tool in script_content:
                tools.append(tool)
        
        return tools
    
    def _detect_tools_from_command(self, command: str) -> List[str]:
        """Detect tools from shell commands."""
        tools = []
        
        # Common tools in commands
        command_tools = {
            'apt-get', 'yum', 'dnf', 'pip', 'npm', 'yarn', 'cargo', 'go',
            'git', 'curl', 'wget', 'tar', 'unzip', 'make', 'cmake'
        }
        
        for tool in command_tools:
            if tool in command.lower():
                tools.append(tool)
        
        return tools
