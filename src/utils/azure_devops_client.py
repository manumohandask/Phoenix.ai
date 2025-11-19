"""
Azure DevOps REST API Client for PR Testing Automation
Handles authentication and API calls to Azure DevOps Services
"""
import aiohttp
import asyncio
import base64
import logging
from typing import List, Dict, Any, Optional
from urllib.parse import quote

logger = logging.getLogger(__name__)


class AzureDevOpsClient:
    """Async client for Azure DevOps REST API v7.0"""
    
    def __init__(self, organization: str, project: str, pat: str, repository: str):
        """
        Initialize Azure DevOps client
        
        Args:
            organization: Azure DevOps organization name
            project: Project name
            pat: Personal Access Token for authentication
            repository: Repository name or ID
        """
        self.organization = organization
        self.project = project
        self.repository = repository
        # URL encode project name to handle spaces (e.g., "TPS Cloud" -> "TPS%20Cloud")
        project_encoded = quote(project, safe='')
        self.base_url = f"https://dev.azure.com/{organization}/{project_encoded}/_apis"
        self.headers = {
            "Authorization": f"Basic {self._encode_pat(pat)}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    def _encode_pat(self, pat: str) -> str:
        """Encode PAT for Basic authentication"""
        return base64.b64encode(f":{pat}".encode()).decode()
    
    async def list_pull_requests(self, branch: Optional[str] = None, status: str = "all") -> List[Dict[str, Any]]:
        """
        Fetch all PRs for a repository
        
        Args:
            branch: Optional target branch filter (e.g., "main", "develop")
            status: PR status filter ("active", "completed", "abandoned", "all")
        
        Returns:
            List of pull request objects
        """
        try:
            url = f"{self.base_url}/git/repositories/{self.repository}/pullrequests"
            params = {
                "api-version": "7.0",
                "searchCriteria.status": status
            }
            
            if branch:
                params["searchCriteria.targetRefName"] = f"refs/heads/{branch}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers, params=params) as resp:
                    resp.raise_for_status()
                    data = await resp.json()
                    logger.info(f"Fetched {len(data.get('value', []))} pull requests")
                    return data.get("value", [])
        except aiohttp.ClientError as e:
            logger.error(f"Failed to fetch pull requests: {e}")
            raise Exception(f"Azure DevOps API error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error fetching PRs: {e}")
            raise
    
    async def get_pr_details(self, pr_id: int) -> Dict[str, Any]:
        """
        Get detailed PR information including commits, changes, and work items
        
        Args:
            pr_id: Pull request ID
        
        Returns:
            Dictionary containing PR details, commits, changes, and work items
        """
        try:
            pr_url = f"{self.base_url}/git/repositories/{self.repository}/pullrequests/{pr_id}"
            commits_url = f"{pr_url}/commits"
            iterations_url = f"{pr_url}/iterations"
            workitems_url = f"{pr_url}/workitems"
            
            async with aiohttp.ClientSession() as session:
                # Fetch all data in parallel
                pr_data, commits_data, iterations_data, workitems_data = await asyncio.gather(
                    self._fetch_json(session, pr_url),
                    self._fetch_json(session, commits_url),
                    self._fetch_json(session, iterations_url),
                    self._fetch_json(session, workitems_url),
                    return_exceptions=True
                )
                
                # Handle potential errors
                if isinstance(pr_data, Exception):
                    raise pr_data
                
                commits = commits_data.get("value", []) if not isinstance(commits_data, Exception) else []
                iterations = iterations_data.get("value", []) if not isinstance(iterations_data, Exception) else []
                workitems = workitems_data.get("value", []) if not isinstance(workitems_data, Exception) else []
                
                # Get file changes from latest iteration (must be inside session context)
                changes = []
                if iterations:
                    try:
                        latest_iteration_id = iterations[-1].get("id", 1)
                        changes_url = f"{pr_url}/iterations/{latest_iteration_id}/changes"
                        changes_data = await self._fetch_json(session, changes_url)
                        changes = changes_data.get("changeEntries", [])
                    except Exception as e:
                        logger.warning(f"Failed to fetch changes for PR #{pr_id}: {e}")
                        changes = []
                
                logger.info(f"Fetched PR #{pr_id} details: {len(commits)} commits, {len(changes)} changes")
                
                return {
                    "pr": pr_data,
                    "commits": commits,
                    "changes": changes,
                    "workitems": workitems
                }
        except Exception as e:
            logger.error(f"Failed to fetch PR details for #{pr_id}: {e}")
            raise Exception(f"Failed to fetch PR details: {str(e)}")
    
    async def get_file_content(self, file_path: str, commit_id: str) -> str:
        """
        Fetch file content at a specific commit
        
        Args:
            file_path: Path to file in repository
            commit_id: Commit SHA
        
        Returns:
            File content as string
        """
        try:
            url = f"{self.base_url}/git/repositories/{self.repository}/items"
            params = {
                "api-version": "7.0",
                "path": file_path,
                "versionDescriptor.version": commit_id,
                "versionDescriptor.versionType": "commit"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers, params=params) as resp:
                    resp.raise_for_status()
                    return await resp.text()
        except Exception as e:
            logger.error(f"Failed to fetch file content for {file_path}: {e}")
            return ""
    
    async def post_pr_comment(self, pr_id: int, comment: str, status: str = "active") -> Dict[str, Any]:
        """
        Post a comment thread to PR
        
        Args:
            pr_id: Pull request ID
            comment: Comment text (supports markdown)
            status: Thread status ("active", "fixed", "closed")
        
        Returns:
            Created comment thread object
        """
        try:
            url = f"{self.base_url}/git/repositories/{self.repository}/pullrequests/{pr_id}/threads"
            payload = {
                "comments": [
                    {
                        "parentCommentId": 0,
                        "content": comment,
                        "commentType": 1
                    }
                ],
                "status": status
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url + "?api-version=7.0", 
                    headers=self.headers, 
                    json=payload
                ) as resp:
                    resp.raise_for_status()
                    result = await resp.json()
                    logger.info(f"Posted comment to PR #{pr_id}")
                    return result
        except Exception as e:
            logger.error(f"Failed to post comment to PR #{pr_id}: {e}")
            raise Exception(f"Failed to post PR comment: {str(e)}")
    
    async def get_work_item_details(self, work_item_id: int) -> Dict[str, Any]:
        """
        Fetch detailed work item information (User Story, Bug, Task, etc.)
        Only fetches essential fields for faster performance
        
        Args:
            work_item_id: Work item ID
        
        Returns:
            Dictionary with work item details including fields, description, acceptance criteria
        """
        try:
            # Work items use a different base URL pattern
            work_item_url = f"https://dev.azure.com/{self.organization}/_apis/wit/workitems/{work_item_id}"
            
            # Only fetch essential fields for speed (instead of $expand=all)
            essential_fields = [
                "System.Id",
                "System.WorkItemType", 
                "System.Title",
                "System.State",
                "System.Description",
                "Microsoft.VSTS.Common.AcceptanceCriteria",
                "Microsoft.VSTS.TCM.ReproSteps"
            ]
            
            params = {
                "api-version": "7.0",
                "fields": ",".join(essential_fields)
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(work_item_url, headers=self.headers, params=params) as resp:
                    resp.raise_for_status()
                    data = await resp.json()
                    logger.info(f"Fetched work item #{work_item_id} details")
                    return data
        except Exception as e:
            logger.error(f"Failed to fetch work item #{work_item_id}: {e}")
            return {}
    
    async def _fetch_json(self, session: aiohttp.ClientSession, url: str) -> Dict[str, Any]:
        """Helper method to fetch JSON data"""
        try:
            async with session.get(url + "?api-version=7.0", headers=self.headers) as resp:
                resp.raise_for_status()
                return await resp.json()
        except Exception as e:
            logger.error(f"Failed to fetch {url}: {e}")
            raise
    
    @staticmethod
    async def list_projects(organization: str, pat: str) -> List[Dict[str, Any]]:
        """
        List all projects in an organization
        
        Args:
            organization: Azure DevOps organization name
            pat: Personal Access Token
        
        Returns:
            List of project objects
        """
        try:
            url = f"https://dev.azure.com/{organization}/_apis/projects?api-version=7.0"
            headers = {
                "Authorization": f"Basic {base64.b64encode(f':{pat}'.encode()).decode()}",
                "Content-Type": "application/json"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as resp:
                    resp.raise_for_status()
                    data = await resp.json()
                    projects = data.get("value", [])
                    logger.info(f"Fetched {len(projects)} projects from {organization}")
                    return projects
        except Exception as e:
            logger.error(f"Failed to fetch projects: {e}")
            raise Exception(f"Failed to fetch projects: {str(e)}")
    
    @staticmethod
    async def list_repositories(organization: str, project: str, pat: str) -> List[Dict[str, Any]]:
        """
        List all repositories in a project
        
        Args:
            organization: Azure DevOps organization name
            project: Project name
            pat: Personal Access Token
        
        Returns:
            List of repository objects
        """
        try:
            project_encoded = quote(project, safe='')
            url = f"https://dev.azure.com/{organization}/{project_encoded}/_apis/git/repositories?api-version=7.0"
            headers = {
                "Authorization": f"Basic {base64.b64encode(f':{pat}'.encode()).decode()}",
                "Content-Type": "application/json"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as resp:
                    resp.raise_for_status()
                    data = await resp.json()
                    repos = data.get("value", [])
                    logger.info(f"Fetched {len(repos)} repositories from {project}")
                    return repos
        except Exception as e:
            logger.error(f"Failed to fetch repositories: {e}")
            raise Exception(f"Failed to fetch repositories: {str(e)}")
