"""
Code analyzer for PR impact assessment
Identifies impacted modules, APIs, UI components, and database changes
"""
import re
import logging
from typing import List, Set
from .schemas import PRContext, FileChange

logger = logging.getLogger(__name__)


class CodeAnalyzer:
    """Analyzes PR changes to identify impacted areas"""
    
    # File patterns for different impact types
    API_PATTERNS = [
        r'api[/\\]', r'endpoint[/\\]', r'route[/\\]', r'controller[/\\]',
        r'service[/\\]', r'handler[/\\]', r'views?\.py$'
    ]
    
    UI_PATTERNS = [
        r'\.tsx?$', r'\.jsx$', r'\.vue$', r'\.html$', 
        r'\.css$', r'\.scss$', r'\.less$', r'component[/\\]'
    ]
    
    DATABASE_PATTERNS = [
        r'migration[/\\]', r'schema[/\\]', r'models?\.py$',
        r'\.sql$', r'database[/\\]', r'alembic[/\\]'
    ]
    
    CONFIG_PATTERNS = [
        r'config[/\\]', r'\.env', r'settings\.py$', 
        r'\.json$', r'\.yaml$', r'\.yml$'
    ]
    
    def analyze_pr_impact(self, pr_context: PRContext) -> PRContext:
        """
        Analyze file changes to identify impacted modules/APIs/UI/Database
        
        Args:
            pr_context: PR context with file changes
        
        Returns:
            Updated PR context with impact analysis
        """
        logger.info(f"Analyzing impact for PR #{pr_context.pr_id} with {len(pr_context.file_changes)} changes")
        
        modules: Set[str] = set()
        apis: Set[str] = set()
        ui_components: Set[str] = set()
        database_changes: Set[str] = set()
        
        for file_change in pr_context.file_changes:
            path = file_change.path
            path_lower = path.lower()
            
            # Extract module from path
            module = self._extract_module(path)
            if module:
                modules.add(module)
            
            # Check for API changes
            if self._matches_patterns(path_lower, self.API_PATTERNS):
                api_name = self._extract_api_name(path)
                if api_name:
                    apis.add(api_name)
            
            # Check for UI changes
            if self._matches_patterns(path_lower, self.UI_PATTERNS):
                component = self._extract_component_name(path)
                if component:
                    ui_components.add(component)
            
            # Check for database changes
            if self._matches_patterns(path_lower, self.DATABASE_PATTERNS):
                db_change = self._extract_database_change(path)
                if db_change:
                    database_changes.add(db_change)
        
        # Update context
        pr_context.impacted_modules = sorted(list(modules))
        pr_context.impacted_apis = sorted(list(apis))
        pr_context.impacted_ui_components = sorted(list(ui_components))
        pr_context.impacted_database = sorted(list(database_changes))
        
        logger.info(
            f"Impact analysis complete: {len(modules)} modules, "
            f"{len(apis)} APIs, {len(ui_components)} UI components, "
            f"{len(database_changes)} DB changes"
        )
        
        return pr_context
    
    def _extract_module(self, file_path: str) -> str:
        """Extract module name from file path"""
        # Remove leading/trailing slashes
        path = file_path.strip('/\\')
        
        # Look for src/ or app/ directories
        for prefix in ['src/', 'app/', 'lib/', 'packages/']:
            if prefix in path.lower():
                parts = path.split(prefix, 1)[1].split('/')[0].split('\\')[0]
                return parts
        
        # Fallback: get first directory
        parts = re.split(r'[/\\]', path)
        if len(parts) > 1:
            return parts[0]
        
        return ""
    
    def _extract_api_name(self, file_path: str) -> str:
        """Extract API endpoint name from file path"""
        # Try to find controller/route/handler name
        match = re.search(r'/([\w-]+)(?:Controller|Route|Handler|Api|Service|Endpoint)', file_path, re.IGNORECASE)
        if match:
            return match.group(1)
        
        # Fallback: use filename without extension
        filename = file_path.split('/')[-1].split('\\')[-1]
        name = re.sub(r'\.(py|js|ts|tsx|jsx)$', '', filename)
        
        # Clean up common suffixes
        name = re.sub(r'(Controller|Route|Handler|Api|Service|Endpoint)$', '', name, flags=re.IGNORECASE)
        
        return name if name else ""
    
    def _extract_component_name(self, file_path: str) -> str:
        """Extract UI component name from file path"""
        # Get filename without extension
        filename = file_path.split('/')[-1].split('\\')[-1]
        name = re.sub(r'\.(tsx?|jsx|vue|html|css|scss|less)$', '', filename)
        
        # Clean up common prefixes/suffixes
        name = re.sub(r'^(index|component|default)', '', name, flags=re.IGNORECASE)
        name = re.sub(r'(Component|View|Page)$', '', name, flags=re.IGNORECASE)
        
        return name.strip() if name.strip() else filename
    
    def _extract_database_change(self, file_path: str) -> str:
        """Extract database change description from file path"""
        path_lower = file_path.lower()
        
        # Check if it's a migration file
        if 'migration' in path_lower:
            filename = file_path.split('/')[-1].split('\\')[-1]
            # Try to extract migration name
            match = re.search(r'(\d+)_(.+)\.(py|sql)', filename)
            if match:
                return f"Migration: {match.group(2).replace('_', ' ')}"
            return f"Migration: {filename}"
        
        # Check if it's a model file
        if 'model' in path_lower:
            return f"Model: {self._extract_component_name(file_path)}"
        
        # Check if it's a schema file
        if 'schema' in path_lower:
            return f"Schema: {self._extract_component_name(file_path)}"
        
        return f"Database: {file_path.split('/')[-1]}"
    
    def _matches_patterns(self, path: str, patterns: List[str]) -> bool:
        """Check if path matches any of the given patterns"""
        return any(re.search(pattern, path) for pattern in patterns)
    
    def get_impact_summary(self, pr_context: PRContext) -> str:
        """Generate human-readable impact summary"""
        summary_parts = []
        
        if pr_context.impacted_modules:
            summary_parts.append(f"{len(pr_context.impacted_modules)} module(s)")
        
        if pr_context.impacted_apis:
            summary_parts.append(f"{len(pr_context.impacted_apis)} API(s)")
        
        if pr_context.impacted_ui_components:
            summary_parts.append(f"{len(pr_context.impacted_ui_components)} UI component(s)")
        
        if pr_context.impacted_database:
            summary_parts.append(f"{len(pr_context.impacted_database)} database change(s)")
        
        if not summary_parts:
            return "No significant impacts detected"
        
        return "Impacts: " + ", ".join(summary_parts)
