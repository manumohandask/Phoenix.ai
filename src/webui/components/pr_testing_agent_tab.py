"""
PR Testing Agent Tab - Complete workflow for automated PR validation
Provides UI for Azure DevOps integration, PR selection, and automated testing
"""
import gradio as gr
import asyncio
import logging
import os
import re
import time
from typing import Dict, Any, AsyncGenerator
from gradio.components import Component
from datetime import datetime

from src.webui.webui_manager import WebuiManager
from src.utils.azure_devops_client import AzureDevOpsClient
from src.agent.pr_testing.code_analyzer import CodeAnalyzer
from src.agent.pr_testing.test_generator import TestGenerator
from src.agent.pr_testing.schemas import PRContext, FileChange, TestStepResult, TestExecutionResult
from src.agent.browser_use.browser_use_agent import BrowserUseAgent
from src.browser.custom_browser import CustomBrowser
from src.controller.custom_controller import CustomController
from browser_use.browser.browser import BrowserConfig
from src.utils import llm_provider

logger = logging.getLogger(__name__)


def create_pr_testing_agent_tab(webui_manager: WebuiManager):
    """Creates the PR Testing Agent tab following existing patterns"""
    
    with gr.Column():
        gr.Markdown("## 🔍 Pull Request Testing Automation")
        gr.Markdown("Connect to Azure DevOps, select a PR, and run automated validation tests")
        
        # ===== Phase 1: Connection Settings =====
        with gr.Group():
            gr.Markdown("### 📋 Step 1: Azure DevOps Configuration")
            
            with gr.Row():
                org_input = gr.Textbox(
                    label="Organization",
                    placeholder="hrblock-ca",
                    scale=1,
                    info="Your Azure DevOps organization name"
                )
                pat_input = gr.Textbox(
                    label="Personal Access Token (PAT)",
                    type="password",
                    placeholder="Enter your Azure DevOps PAT",
                    scale=2,
                    info="Generate from Azure DevOps User Settings"
                )
            
            load_projects_button = gr.Button(
                "🔄 Load Projects & Repositories",
                variant="secondary",
                size="sm"
            )
            
            with gr.Row():
                project_dropdown = gr.Dropdown(
                    label="Project",
                    choices=[],
                    interactive=True,
                    scale=1,
                    info="Select after loading"
                )
                repo_dropdown = gr.Dropdown(
                    label="Repository",
                    choices=[],
                    interactive=True,
                    scale=2,
                    info="Select after choosing project"
                )
            
            branch_input = gr.Textbox(
                label="Target Branch (optional)",
                placeholder="main",
                info="Leave empty for all branches"
            )
            
            fetch_button = gr.Button(
                "📥 Fetch Pull Requests",
                variant="primary",
                size="lg"
            )
        
        # ===== Phase 2: PR Selection =====
        with gr.Group():
            gr.Markdown("### 📝 Step 2: Select Pull Request")
            
            pr_dataframe = gr.DataFrame(
                headers=["PR ID", "Title", "Author", "Status", "Source", "Target", "Created"],
                datatype=["number", "str", "str", "str", "str", "str", "str"],
                interactive=False,
                wrap=True,
                label="Available Pull Requests"
            )
            
            pr_selector = gr.Dropdown(
                label="Select PR ID to Validate",
                choices=[],
                interactive=True,
                info="Choose a PR from the list above"
            )
        
        # ===== Phase 3: Test Configuration =====
        with gr.Group():
            gr.Markdown("### ⚙️ Step 3: Configure Test Generation")
            
            with gr.Row():
                llm_provider_dropdown = gr.Dropdown(
                    choices=["openai", "anthropic", "google", "deepseek", "ollama"],
                    value="openai",
                    label="LLM Provider",
                    scale=1
                )
                llm_model_dropdown = gr.Dropdown(
                    choices=[
                        "gpt-4o", "gpt-4", "gpt-3.5-turbo",
                        "claude-3-5-sonnet-20241022", "claude-3-opus-20240229",
                        "gemini-2.0-flash", "gemini-1.5-pro",
                        "deepseek-chat", "deepseek-reasoner"
                    ],
                    value="gpt-4o",
                    label="Model",
                    scale=1
                )
            
            llm_api_key_input = gr.Textbox(
                label="LLM API Key (optional)",
                placeholder="Leave empty to use environment variable",
                type="password",
                info="Provide API key here or set in .env file"
            )
            
            headless_checkbox = gr.Checkbox(
                label="Run browser in headless mode (faster, but can't watch execution)",
                value=True
            )
        
        # ===== Phase 4: Execution =====
        validate_button = gr.Button(
            "✅ Validate Pull Request",
            variant="primary",
            size="lg"
        )
        
        status_output = gr.Textbox(
            label="Status",
            lines=3,
            interactive=False,
            show_label=True
        )
        
        # ===== Results Display =====
        with gr.Tabs():
            with gr.TabItem("📊 PR Context"):
                context_display = gr.Markdown(value="")
            
            with gr.TabItem("📋 Test Plan"):
                test_plan_display = gr.Markdown(value="")
            
            with gr.TabItem("✅ Execution Results"):
                results_display = gr.Markdown(value="")
            
            with gr.TabItem("💬 PR Comment"):
                final_output = gr.Markdown(value="")
    
    # Register components
    components = {
        "org_input": org_input,
        "pat_input": pat_input,
        "load_projects_button": load_projects_button,
        "project_dropdown": project_dropdown,
        "repo_dropdown": repo_dropdown,
        "branch_input": branch_input,
        "fetch_button": fetch_button,
        "pr_dataframe": pr_dataframe,
        "pr_selector": pr_selector,
        "llm_provider_dropdown": llm_provider_dropdown,
        "llm_model_dropdown": llm_model_dropdown,
        "llm_api_key_input": llm_api_key_input,
        "headless_checkbox": headless_checkbox,
        "validate_button": validate_button,
        "status_output": status_output,
        "context_display": context_display,
        "test_plan_display": test_plan_display,
        "results_display": results_display,
        "final_output": final_output
    }
    
    webui_manager.add_components("pr_testing", components)
    
    # ===== Event Handlers =====
    
    async def load_projects_async(org, pat):
        """Load projects from Azure DevOps"""
        try:
            if not org or not pat:
                return (
                    gr.update(choices=[], value=None),
                    gr.update(choices=[], value=None),
                    "❌ Please enter Organization and PAT first"
                )
            
            logger.info(f"Loading projects from {org}")
            projects = await AzureDevOpsClient.list_projects(org, pat)
            
            project_choices = [proj["name"] for proj in projects]
            
            return (
                gr.update(choices=project_choices, value=None),
                gr.update(choices=[], value=None),
                f"✅ Loaded {len(project_choices)} project(s)"
            )
        except Exception as e:
            logger.error(f"Failed to load projects: {e}", exc_info=True)
            return (
                gr.update(choices=[], value=None),
                gr.update(choices=[], value=None),
                f"❌ Error: {str(e)}"
            )
    
    async def load_repositories_async(org, pat, project):
        """Load repositories when project is selected"""
        try:
            if not org or not pat or not project:
                return gr.update(choices=[], value=None)
            
            logger.info(f"Loading repositories from {org}/{project}")
            repos = await AzureDevOpsClient.list_repositories(org, project, pat)
            
            repo_choices = [repo["name"] for repo in repos]
            return gr.update(choices=repo_choices, value=None)
        except Exception as e:
            logger.error(f"Failed to load repositories: {e}", exc_info=True)
            return gr.update(choices=[], value=None)
    
    async def fetch_pull_requests_async(org, pat, proj, repo, branch):
        """Fetch PRs from Azure DevOps"""
        try:
            if not all([org, pat, proj, repo]):
                return (
                    gr.update(value=[]),
                    gr.update(choices=[], value=None),
                    "❌ Please select all fields"
                )
            
            logger.info(f"Fetching PRs from {org}/{proj}/{repo}")
            
            client = AzureDevOpsClient(org, proj, pat, repo)
            prs = await client.list_pull_requests(branch if branch.strip() else None)
            
            pr_list = []
            pr_choices = []
            for pr in prs:
                pr_id = pr["pullRequestId"]
                pr_title = pr["title"][:80]
                pr_list.append([
                    pr_id,
                    pr_title,
                    pr["createdBy"]["displayName"],
                    pr["status"],
                    pr["sourceRefName"].replace("refs/heads/", ""),
                    pr["targetRefName"].replace("refs/heads/", ""),
                    pr["creationDate"][:10]
                ])
                # Format: "PR #123: Title"
                pr_choices.append(f"PR #{pr_id}: {pr_title}")
            
            return (
                gr.update(value=pr_list),
                gr.update(choices=pr_choices, value=None),
                f"✅ Found {len(pr_list)} pull request(s)"
            )
            
        except Exception as e:
            logger.error(f"Failed to fetch PRs: {e}", exc_info=True)
            return (
                gr.update(value=[]),
                gr.update(choices=[], value=None),
                f"❌ Error fetching PRs: {str(e)}"
            )
    
    async def validate_pr_async(organization: str, pat: str, project: str, repository: str,
                                pr_selected: str, llm_prov: str, llm_model: str, 
                                llm_api_key: str, headless: bool):
        """Main validation workflow"""
        try:
            # Convert inputs to proper types
            organization = str(organization or "")
            pat = str(pat or "")
            project = str(project or "")
            repository = str(repository or "")
            llm_prov = str(llm_prov or "openai")
            llm_model = str(llm_model or "gpt-4o")
            llm_api_key = str(llm_api_key or "").strip()
            
            # Validate LLM API key before proceeding
            api_key_map = {
                "openai": "OPENAI_API_KEY",
                "anthropic": "ANTHROPIC_API_KEY",
                "google": "GOOGLE_API_KEY",
                "deepseek": "DEEPSEEK_API_KEY",
                "azure_openai": "AZURE_OPENAI_API_KEY",
                "mistral": "MISTRAL_API_KEY",
                "ollama": None,  # No API key needed for local Ollama
            }
            
            required_key = api_key_map.get(llm_prov)
            
            # Check if API key is provided via UI or environment variable
            has_api_key = bool(llm_api_key) or (required_key and os.getenv(required_key))
            
            if required_key and not has_api_key:
                error_msg = (
                    f"❌ Error: {llm_prov.upper()} API key not found!\n\n"
                    f"🔑 Please provide the API key in one of these ways:\n\n"
                    f"**Option 1: Via UI (Easiest)**\n"
                    f"- Enter your API key in the 'LLM API Key' field above\n\n"
                    f"**Option 2: Via Environment Variable**\n"
                    f"1. Create/edit `.env` file in project root\n"
                    f"2. Add: `{required_key}=your-api-key-here`\n"
                    f"3. Restart the WebUI server\n\n"
                    f"**Alternative:** Select a different LLM provider (e.g., Ollama for local usage)"
                )
                yield (error_msg, "", "", "", "")
                return
            
            # Extract PR ID from selected dropdown value (format: "PR #123: Title")
            if not pr_selected or not pr_selected.startswith("PR #"):
                yield (
                    "❌ Please select a PR from the dropdown list.\n\n" +
                    "Instructions:\n" +
                    "1. Click 'Fetch Pull Requests' to load PRs\n" +
                    "2. Select a PR from the dropdown menu\n" +
                    "3. Then click 'Validate Pull Request'",
                    "", "", "", ""
                )
                return
            
            # Parse PR ID from "PR #123: Title"
            pr_id = int(pr_selected.split(":")[0].replace("PR #", "").strip())
            logger.info(f"Starting validation for PR #{pr_id}")
            
            # Phase 1: Extract PR Context
            yield (f"🔄 Phase 1/4: Extracting PR #{pr_id} context...", "", "", "", "")
            
            client = AzureDevOpsClient(organization, project, pat, repository)
            pr_details = await client.get_pr_details(pr_id)
            
            # Fetch detailed work item information (in parallel, limit to 2 most recent)
            work_items_detailed = []
            workitems = pr_details.get("workitems", [])[:2]  # Limit to 2 work items for speed
            
            if workitems:
                # Fetch work items in parallel for speed
                async def fetch_work_item(wi):
                    try:
                        wi_id = wi.get("id")
                        if not wi_id and "url" in wi:
                            wi_id = int(wi["url"].split("/")[-1])
                        
                        if wi_id:
                            wi_details = await client.get_work_item_details(wi_id)
                            return wi_details
                    except Exception as e:
                        logger.warning(f"Failed to fetch work item details: {e}")
                    return None
                
                # Fetch all work items concurrently (should take ~1-2 seconds total)
                work_items_results = await asyncio.gather(*[fetch_work_item(wi) for wi in workitems])
                work_items_detailed = [wi for wi in work_items_results if wi]
            
            # Build PR context
            file_changes = []
            for change in pr_details.get("changes", []):
                try:
                    # Handle both item object and simple path
                    if isinstance(change.get("item"), dict):
                        file_path = change.get("item", {}).get("path", "")
                    else:
                        file_path = change.get("path", "")
                    
                    file_changes.append(FileChange(
                        path=file_path,
                        change_type=change.get("changeType", "edit").lower(),
                        additions=0,
                        deletions=0
                    ))
                except Exception as e:
                    logger.warning(f"Failed to parse file change: {e}")
            
            pr_context = PRContext(
                pr_id=pr_id,
                title=pr_details["pr"]["title"],
                description=pr_details["pr"].get("description"),
                author=pr_details["pr"]["createdBy"]["displayName"],
                reviewers=[r["displayName"] for r in pr_details["pr"].get("reviewers", [])],
                source_branch=pr_details["pr"]["sourceRefName"],
                target_branch=pr_details["pr"]["targetRefName"],
                linked_work_items=work_items_detailed,  # Use detailed work items
                commits=pr_details.get("commits", []),
                file_changes=file_changes
            )
            
            analyzer = CodeAnalyzer()
            pr_context = analyzer.analyze_pr_impact(pr_context)
            
            # Build work item details for display
            work_item_summary = ""
            if pr_context.linked_work_items:
                work_item_summary = "\n\n**Linked Work Items:**\n"
                for wi in pr_context.linked_work_items:
                    fields = wi.get("fields", {})
                    wi_id = wi.get("id", "N/A")
                    wi_type = fields.get("System.WorkItemType", "Unknown")
                    wi_title = fields.get("System.Title", "No title")
                    wi_state = fields.get("System.State", "Unknown")
                    wi_description = fields.get("System.Description", "")
                    wi_acceptance = fields.get("Microsoft.VSTS.Common.AcceptanceCriteria", "")
                    wi_repro_steps = fields.get("Microsoft.VSTS.TCM.ReproSteps", "")
                    
                    work_item_summary += f"\n**#{wi_id} - {wi_type}: {wi_title}**\n"
                    work_item_summary += f"- State: {wi_state}\n"
                    
                    if wi_description:
                        # Strip HTML tags for cleaner display (simplified)
                        clean_desc = re.sub(r'<[^>]+>', '', wi_description).strip()
                        work_item_summary += f"- Description: {clean_desc[:150]}{'...' if len(clean_desc) > 150 else ''}\n"
                    
                    if wi_acceptance:
                        clean_acceptance = re.sub(r'<[^>]+>', '', wi_acceptance).strip()
                        work_item_summary += f"- Acceptance: {clean_acceptance[:150]}{'...' if len(clean_acceptance) > 150 else ''}\n"
                    
                    if wi_repro_steps:
                        clean_repro = re.sub(r'<[^>]+>', '', wi_repro_steps).strip()
                        work_item_summary += f"- Repro: {clean_repro[:100]}{'...' if len(clean_repro) > 100 else ''}\n"
            
            context_md = f"""### PR Context
**Title:** {pr_context.title}
**Author:** {pr_context.author}
**Branch:** {pr_context.source_branch} → {pr_context.target_branch}

**Changed Files:** {len(pr_context.file_changes)}

**Impacted Areas:**
- Modules: {', '.join(pr_context.impacted_modules) or 'None detected'}
- APIs: {', '.join(pr_context.impacted_apis) or 'None detected'}
- UI Components: {', '.join(pr_context.impacted_ui_components) or 'None detected'}
{work_item_summary}
"""
            
            yield (
                f"✅ Phase 1 Complete: Analyzed {len(pr_context.file_changes)} file(s) + {len(pr_context.linked_work_items)} work item(s)",
                context_md,
                "",
                "",
                ""
            )
            
            # Phase 2: Generate Test Plan
            yield (f"🔄 Phase 2/4: Generating test plan with AI (this may take 15-30 seconds)...", context_md, "", "", "")
            
            # Use the LLM settings from parameters, pass API key if provided
            # Use lower temperature for faster, more consistent responses
            test_gen = TestGenerator(
                provider=llm_prov, 
                model_name=llm_model,
                temperature=0.3,  # Lower temperature for faster generation
                api_key=llm_api_key if llm_api_key else None
            )
            test_plan = await test_gen.generate_test_plan(pr_context)
            
            # Format test plan with full details
            test_plan_md = f"""### Test Plan
{test_plan.summary}

**Overview:** {len(test_plan.test_scenarios)} Scenarios | {len(test_plan.manual_steps)} Manual Steps | {len(test_plan.automated_steps)} Automated Steps

---

#### 📋 Test Scenarios
"""
            
            for i, scenario in enumerate(test_plan.test_scenarios, 1):
                test_plan_md += f"\n**{i}. {scenario.name}**\n"
                test_plan_md += f"   - Priority: {scenario.priority}\n"
                test_plan_md += f"   - Type: {scenario.test_type}\n"
                test_plan_md += f"   - Description: {scenario.description}\n"
            
            test_plan_md += f"\n\n#### 🖐️ Manual Test Steps\n"
            for i, step in enumerate(test_plan.manual_steps, 1):
                test_plan_md += f"\n**Step {i}:** {step.description}\n"
                test_plan_md += f"   - Action: {step.action_type}\n"
                if step.target:
                    test_plan_md += f"   - Target: `{step.target}`\n"
                if step.input_value:
                    test_plan_md += f"   - Input: `{step.input_value}`\n"
                test_plan_md += f"   - Expected: {step.expected_result}\n"
            
            test_plan_md += f"\n\n#### 🤖 Automated Test Steps\n"
            for i, step in enumerate(test_plan.automated_steps, 1):
                test_plan_md += f"\n**Step {i}:** {step.description}\n"
                test_plan_md += f"   - Action: {step.action_type}\n"
                if step.target:
                    test_plan_md += f"   - Target: `{step.target}`\n"
                if step.input_value:
                    test_plan_md += f"   - Input: `{step.input_value}`\n"
                test_plan_md += f"   - Expected: {step.expected_result}\n"
            
            if test_plan.prerequisites:
                test_plan_md += f"\n\n#### ⚙️ Prerequisites\n"
                for prereq in test_plan.prerequisites:
                    test_plan_md += f"- {prereq}\n"
            
            if test_plan.test_data_requirements:
                test_plan_md += f"\n\n#### 📊 Test Data Requirements\n"
                for data_req in test_plan.test_data_requirements:
                    test_plan_md += f"- {data_req}\n"
            
            yield (
                f"✅ Phase 2 Complete: Generated test plan",
                context_md,
                test_plan_md,
                "",
                ""
            )
            
            # Phase 3: Execute Tests (simplified for now)
            results_md = f"""### Test Results
**Status:** Validation workflow complete
**PR ID:** {pr_id}
**Generated Tests:** {len(test_plan.automated_steps)}

*Browser execution will be implemented in next iteration*
"""
            
            yield (
                f"✅ Phase 3 Complete: Test generation finished",
                context_md,
                test_plan_md,
                results_md,
                ""
            )
            
            # Phase 4: Generate Comment
            comment = f"""## 🤖 Automated Test Results

**PR #{pr_id}: {pr_context.title}**

### Test Plan Generated
{test_plan.summary}

- Generated {len(test_plan.test_scenarios)} test scenarios
- {len(test_plan.manual_steps)} manual test steps
- {len(test_plan.automated_steps)} automated test steps

*🔥 Generated by Phoenix AI - Intelligent Testing Platform*
"""
            
            yield (
                f"✅ All phases complete!",
                context_md,
                test_plan_md,
                results_md,
                comment
            )
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            logger.error(f"Validation error: {e}\n{error_details}")
            yield (
                f"❌ Error: {str(e)}\n\nCheck the console logs for more details.",
                "",
                "",
                "",
                ""
            )
    
    # Wire up events
    load_projects_button.click(
        load_projects_async,
        inputs=[org_input, pat_input],
        outputs=[project_dropdown, repo_dropdown, status_output]
    )
    
    project_dropdown.change(
        load_repositories_async,
        inputs=[org_input, pat_input, project_dropdown],
        outputs=[repo_dropdown]
    )
    
    fetch_button.click(
        fetch_pull_requests_async,
        inputs=[org_input, pat_input, project_dropdown, repo_dropdown, branch_input],
        outputs=[pr_dataframe, pr_selector, status_output]
    )
    
    validate_button.click(
        validate_pr_async,
        inputs=[org_input, pat_input, project_dropdown, repo_dropdown, pr_selector, 
                llm_provider_dropdown, llm_model_dropdown, llm_api_key_input, headless_checkbox],
        outputs=[status_output, context_display, test_plan_display, results_display, final_output]
    )
