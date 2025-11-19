"""
PR Testing Agent Tab - Complete workflow for automated PR validation
Provides UI for Azure DevOps integration, PR selection, and automated testing
"""
import gradio as gr
import asyncio
import logging
import os
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

logger = logging.getLogger(__name__)


# ===== Helper Functions =====

async def fetch_pull_requests_handler(
    organization: str,
    project: str, 
    repository: str,
    branch: str,
    pat: str
):
    """Fetch all PRs from Azure DevOps and display in table"""
    try:
        if not all([organization, project, repository, pat]):
            return (
                gr.update(value=[]),
                "❌ Please fill in all required fields (Organization, Project, Repository, PAT)"
            )
        
        logger.info(f"Fetching PRs from {organization}/{project}/{repository}")
        
        # Create client and fetch PRs
        client = AzureDevOpsClient(organization, project, pat, repository)
        prs = await client.list_pull_requests(branch if branch.strip() else None)
        
        # Format as table rows
        pr_list = []
        for pr in prs:
            pr_list.append([
                pr["pullRequestId"],
                pr["title"][:80],  # Truncate long titles
                pr["createdBy"]["displayName"],
                pr["status"],
                pr["sourceRefName"].replace("refs/heads/", ""),
                pr["targetRefName"].replace("refs/heads/", ""),
                pr["creationDate"][:10]  # Show only date
            ])
        
        return (
            gr.update(value=pr_list),
            f"✅ Found {len(pr_list)} pull request(s)"
        )
        
    except Exception as e:
        logger.error(f"Failed to fetch PRs: {e}", exc_info=True)
        return (
            gr.update(value=[]),
            f"❌ Error fetching PRs: {str(e)}"
        )


async def validate_pr_handler(
    webui_manager: WebuiManager,
    components: Dict[Component, Any]
) -> AsyncGenerator[Dict[Component, Any], None]:
    """Main validation workflow: Extract → Generate → Execute → Report"""
    
    start_time = time.time()
    
    try:
        # Get all inputs
        organization = components.get("org_input", "")
        project = components.get("project_input", "")
        repository = components.get("repo_input", "")
        pat = components.get("pat_input", "")
        pr_dataframe_data = components.get("pr_dataframe", {})
        
        # Get selected row
        if isinstance(pr_dataframe_data, dict):
            selected_data = pr_dataframe_data.get("data", [])
            selected_index = pr_dataframe_data.get("selected_rows", [])
        else:
            selected_data = []
            selected_index = []
        
        if not selected_index or not selected_data:
            yield {
                "status_output": "❌ Please select a PR from the list",
                "context_display": "",
                "test_plan_display": "",
                "results_display": "",
                "final_output": ""
            }
            return
        
        # Get PR ID from selected row
        pr_id = int(selected_data[selected_index[0]][0])
        
        # ===== PHASE 1: Extract PR Context =====
        yield {
            "status_output": f"🔄 Phase 1/4: Extracting PR #{pr_id} context...",
            "context_display": "",
            "test_plan_display": "",
            "results_display": "",
            "final_output": ""
        }
        
        client = AzureDevOpsClient(organization, project, pat, repository)
        pr_details = await client.get_pr_details(pr_id)
        
        # Build PRContext
        pr_data = pr_details["pr"]
        file_changes = []
        
        for change in pr_details["changes"]:
            change_type = change.get("changeType", "edit").lower()
            item = change.get("item", {})
            
            file_changes.append(FileChange(
                path=item.get("path", "unknown"),
                change_type=change_type,
                additions=0,  # Azure DevOps doesn't provide this in iterations API
                deletions=0
            ))
        
        pr_context = PRContext(
            pr_id=pr_id,
            title=pr_data["title"],
            description=pr_data.get("description", ""),
            author=pr_data["createdBy"]["displayName"],
            reviewers=[r["displayName"] for r in pr_data.get("reviewers", [])],
            source_branch=pr_data["sourceRefName"],
            target_branch=pr_data["targetRefName"],
            linked_work_items=pr_details["workitems"],
            commits=pr_details["commits"],
            file_changes=file_changes
        )
        
        # Analyze code impact
        analyzer = CodeAnalyzer()
        pr_context = analyzer.analyze_pr_impact(pr_context)
        
        context_md = _format_context(pr_context)
        
        yield {
            "status_output": (
                f"✅ Phase 1 Complete: Analyzed {len(pr_context.file_changes)} file(s)\n"
                f"   Impacted: {len(pr_context.impacted_modules)} module(s), "
                f"{len(pr_context.impacted_apis)} API(s), "
                f"{len(pr_context.impacted_ui_components)} UI component(s), "
                f"{len(pr_context.impacted_database)} DB change(s)"
            ),
            "context_display": context_md,
            "test_plan_display": "",
            "results_display": "",
            "final_output": ""
        }
        
        await asyncio.sleep(0.5)  # Brief pause for UI update
        
        # ===== PHASE 2: Generate Test Plan =====
        yield {
            "status_output": f"🔄 Phase 2/4: Generating test plan with AI...",
            "context_display": context_md,
            "test_plan_display": "",
            "results_display": "",
            "final_output": ""
        }
        
        llm_provider = components.get("llm_provider_dropdown", "openai")
        llm_model = components.get("llm_model_dropdown", "gpt-4o")
        
        test_gen = TestGenerator(provider=llm_provider, model_name=llm_model)
        test_plan = await test_gen.generate_test_plan(pr_context)
        
        test_plan_md = _format_test_plan(test_plan)
        
        yield {
            "status_output": (
                f"✅ Phase 2 Complete: Generated test plan\n"
                f"   {len(test_plan.test_scenarios)} scenario(s), "
                f"{len(test_plan.manual_steps)} manual step(s), "
                f"{len(test_plan.automated_steps)} automated step(s)"
            ),
            "context_display": context_md,
            "test_plan_display": test_plan_md,
            "results_display": "",
            "final_output": ""
        }
        
        await asyncio.sleep(0.5)
        
        # ===== PHASE 3: Execute Browser Tests =====
        if test_plan.automated_steps:
            yield {
                "status_output": f"🔄 Phase 3/4: Executing {len(test_plan.automated_steps)} automated test(s)...",
                "context_display": context_md,
                "test_plan_display": test_plan_md,
                "results_display": "",
                "final_output": ""
            }
            
            results = await _execute_browser_tests(webui_manager, test_plan, components)
            results_md = _format_results(results)
            
            yield {
                "status_output": (
                    f"✅ Phase 3 Complete: {results.passed}/{results.total_tests} test(s) passed\n"
                    f"   Pass Rate: {results.pass_rate:.1f}%"
                ),
                "context_display": context_md,
                "test_plan_display": test_plan_md,
                "results_display": results_md,
                "final_output": ""
            }
        else:
            results = TestExecutionResult(
                pr_id=pr_id,
                total_tests=0,
                passed=0,
                failed=0,
                errors=0,
                skipped=0,
                pass_rate=0.0,
                execution_time=0.0,
                summary="No automated tests generated"
            )
            
            yield {
                "status_output": "⚠️ Phase 3 Skipped: No automated tests to execute",
                "context_display": context_md,
                "test_plan_display": test_plan_md,
                "results_display": "No automated tests were generated for this PR.",
                "final_output": ""
            }
        
        await asyncio.sleep(0.5)
        
        # ===== PHASE 4: Post Results to PR =====
        yield {
            "status_output": f"🔄 Phase 4/4: Posting results to PR #{pr_id}...",
            "context_display": context_md,
            "test_plan_display": test_plan_md,
            "results_display": results_md if test_plan.automated_steps else "No automated tests executed.",
            "final_output": ""
        }
        
        comment = _generate_pr_comment(test_plan, results, time.time() - start_time)
        
        try:
            await client.post_pr_comment(pr_id, comment)
            comment_status = "✅ Results posted to PR"
        except Exception as e:
            logger.error(f"Failed to post comment: {e}")
            comment_status = f"⚠️ Could not post comment: {str(e)}"
        
        final_status = (
            f"✅ All phases complete! ({time.time() - start_time:.1f}s)\n"
            f"   {comment_status}"
        )
        
        yield {
            "status_output": final_status,
            "context_display": context_md,
            "test_plan_display": test_plan_md,
            "results_display": results_md if test_plan.automated_steps else "No automated tests executed.",
            "final_output": comment
        }
        
    except Exception as e:
        logger.error(f"Validation error: {e}", exc_info=True)
        yield {
            "status_output": f"❌ Error: {str(e)}",
            "context_display": "",
            "test_plan_display": "",
            "results_display": "",
            "final_output": f"Validation failed: {str(e)}"
        }


async def _execute_browser_tests(
    webui_manager: WebuiManager,
    test_plan,
    components: Dict[Component, Any]
) -> TestExecutionResult:
    """Execute automated test steps using BrowserUseAgent"""
    
    start_time = time.time()
    step_results = []
    passed = 0
    failed = 0
    errors = 0
    
    try:
        # Initialize browser if needed
        headless = components.get("headless_checkbox", True)
        
        if not webui_manager.bu_browser:
            browser_config = BrowserConfig(
                headless=headless,
                disable_security=False
            )
            webui_manager.bu_browser = CustomBrowser(config=browser_config)
        
        # Execute each automated test step
        for step in test_plan.automated_steps:
            step_start = time.time()
            
            try:
                # Create task description for browser agent
                task_description = (
                    f"{step.description}. "
                    f"Expected result: {step.expected_result}"
                )
                
                if step.target:
                    task_description += f" Target element: {step.target}"
                
                if step.input_value:
                    task_description += f" Input value: {step.input_value}"
                
                # Create controller and context
                controller = CustomController()
                context = await webui_manager.bu_browser.new_context()
                
                # Get LLM (reuse from webui_manager if available)
                if webui_manager.bu_agent and hasattr(webui_manager.bu_agent, 'llm'):
                    llm = webui_manager.bu_agent.llm
                else:
                    # Create new LLM instance
                    from src.utils import llm_provider
                    llm = llm_provider.get_llm_model(
                        provider=components.get("llm_provider_dropdown", "openai"),
                        model_name=components.get("llm_model_dropdown", "gpt-4o")
                    )
                
                # Create agent for this step
                agent = BrowserUseAgent(
                    task=task_description,
                    llm=llm,
                    controller=controller,
                    browser_context=context
                )
                
                # Execute with timeout
                try:
                    history = await asyncio.wait_for(
                        agent.run(max_steps=10),
                        timeout=120  # 2 minute timeout per step
                    )
                    
                    # Check if successful
                    if history and history[-1].result.done:
                        passed += 1
                        step_results.append(TestStepResult(
                            step_number=step.step_number,
                            status="PASS",
                            description=step.description,
                            execution_time=time.time() - step_start
                        ))
                    else:
                        failed += 1
                        error_msg = history[-1].result.error if history else "Unknown error"
                        step_results.append(TestStepResult(
                            step_number=step.step_number,
                            status="FAIL",
                            description=step.description,
                            error_message=error_msg,
                            execution_time=time.time() - step_start
                        ))
                
                except asyncio.TimeoutError:
                    failed += 1
                    step_results.append(TestStepResult(
                        step_number=step.step_number,
                        status="FAIL",
                        description=step.description,
                        error_message="Timeout: Step took longer than 2 minutes",
                        execution_time=time.time() - step_start
                    ))
                
                finally:
                    # Clean up context
                    try:
                        await context.close()
                    except:
                        pass
                
            except Exception as e:
                errors += 1
                logger.error(f"Error executing step {step.step_number}: {e}")
                step_results.append(TestStepResult(
                    step_number=step.step_number,
                    status="ERROR",
                    description=step.description,
                    error_message=str(e),
                    execution_time=time.time() - step_start
                ))
        
        # Calculate results
        total = len(test_plan.automated_steps)
        pass_rate = (passed / total * 100) if total > 0 else 0.0
        
        return TestExecutionResult(
            pr_id=test_plan.pr_id,
            total_tests=total,
            passed=passed,
            failed=failed,
            errors=errors,
            skipped=0,
            pass_rate=pass_rate,
            execution_time=time.time() - start_time,
            step_results=step_results,
            summary=f"{passed}/{total} tests passed ({pass_rate:.1f}%)"
        )
        
    except Exception as e:
        logger.error(f"Browser test execution failed: {e}")
        return TestExecutionResult(
            pr_id=test_plan.pr_id,
            total_tests=len(test_plan.automated_steps),
            passed=0,
            failed=0,
            errors=len(test_plan.automated_steps),
            skipped=0,
            pass_rate=0.0,
            execution_time=time.time() - start_time,
            step_results=[],
            summary=f"Execution failed: {str(e)}"
        )


def _format_context(pr_context: PRContext) -> str:
    """Format PR context for display"""
    lines = [
        "### 📋 Pull Request Context\n",
        f"**PR #{pr_context.pr_id}: {pr_context.title}**\n",
        f"**Author:** {pr_context.author}",
        f"**Branch:** `{pr_context.source_branch}` → `{pr_context.target_branch}`",
        f"**Files Changed:** {len(pr_context.file_changes)}\n"
    ]
    
    if pr_context.description:
        lines.append(f"**Description:**\n{pr_context.description[:200]}{'...' if len(pr_context.description) > 200 else ''}\n")
    
    lines.append("**Impact Analysis:**")
    
    if pr_context.impacted_modules:
        lines.append(f"- **Modules:** {', '.join(pr_context.impacted_modules)}")
    
    if pr_context.impacted_apis:
        lines.append(f"- **APIs:** {', '.join(pr_context.impacted_apis)}")
    
    if pr_context.impacted_ui_components:
        lines.append(f"- **UI Components:** {', '.join(pr_context.impacted_ui_components)}")
    
    if pr_context.impacted_database:
        lines.append(f"- **Database:** {', '.join(pr_context.impacted_database)}")
    
    if not any([pr_context.impacted_modules, pr_context.impacted_apis, 
                pr_context.impacted_ui_components, pr_context.impacted_database]):
        lines.append("- No specific impacts identified")
    
    return "\n".join(lines)


def _format_test_plan(test_plan) -> str:
    """Format test plan for display"""
    lines = [
        "### 📝 Generated Test Plan\n",
        f"**Summary:** {test_plan.summary}\n",
        f"**Test Scenarios:** {len(test_plan.test_scenarios)}",
        f"**Manual Steps:** {len(test_plan.manual_steps)}",
        f"**Automated Steps:** {len(test_plan.automated_steps)}\n"
    ]
    
    if test_plan.prerequisites:
        lines.append("**Prerequisites:**")
        for prereq in test_plan.prerequisites:
            lines.append(f"- {prereq}")
        lines.append("")
    
    if test_plan.test_scenarios:
        lines.append("**Scenarios:**")
        for scenario in test_plan.test_scenarios[:5]:  # Show first 5
            lines.append(f"- **{scenario.name}** ({scenario.priority}): {scenario.description}")
        if len(test_plan.test_scenarios) > 5:
            lines.append(f"  ... and {len(test_plan.test_scenarios) - 5} more")
    
    return "\n".join(lines)


def _format_results(results: TestExecutionResult) -> str:
    """Format test results for display"""
    lines = [
        "### ✅ Test Execution Results\n",
        f"**Pass Rate:** {results.pass_rate:.1f}% ({results.passed}/{results.total_tests})",
        f"**Execution Time:** {results.execution_time:.1f}s\n",
        f"**Breakdown:**",
        f"- ✅ Passed: {results.passed}",
        f"- ❌ Failed: {results.failed}",
        f"- 🔥 Errors: {results.errors}",
        f"- ⏭️ Skipped: {results.skipped}\n"
    ]
    
    if results.step_results:
        lines.append("**Step Details:**\n")
        lines.append("| Step | Status | Description | Time |")
        lines.append("|------|--------|-------------|------|")
        
        for step in results.step_results:
            status_icon = {
                "PASS": "✅",
                "FAIL": "❌",
                "ERROR": "🔥",
                "SKIP": "⏭️"
            }.get(step.status, "❓")
            
            lines.append(
                f"| {step.step_number} | {status_icon} {step.status} | "
                f"{step.description[:50]}... | {step.execution_time:.1f}s |"
            )
            
            if step.error_message:
                lines.append(f"|   | | *Error: {step.error_message[:80]}...* | |")
    
    return "\n".join(lines)


def _generate_pr_comment(test_plan, results: TestExecutionResult, total_time: float) -> str:
    """Generate markdown comment for Azure DevOps PR"""
    lines = [
        "## 🤖 Automated Test Results\n",
        f"**Overall Pass Rate:** {results.pass_rate:.1f}% ({results.passed}/{results.total_tests} tests)",
        f"**Total Execution Time:** {total_time:.1f}s",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
        "---\n",
        "### 📊 Test Summary",
        f"{test_plan.summary}\n",
        "### 📈 Results Breakdown",
        f"- ✅ **Passed:** {results.passed}",
        f"- ❌ **Failed:** {results.failed}",
        f"- 🔥 **Errors:** {results.errors}",
        f"- ⏭️ **Skipped:** {results.skipped}\n"
    ]
    
    if results.step_results:
        lines.append("### 📝 Test Step Results\n")
        lines.append("| # | Status | Description | Result |")
        lines.append("|---|--------|-------------|--------|")
        
        for step in results.step_results:
            status_icon = {"PASS": "✅", "FAIL": "❌", "ERROR": "🔥", "SKIP": "⏭️"}.get(step.status, "❓")
            desc = step.description[:60] + "..." if len(step.description) > 60 else step.description
            result = "OK" if step.status == "PASS" else (step.error_message or "Failed")[:40]
            lines.append(f"| {step.step_number} | {status_icon} | {desc} | {result} |")
    
    if test_plan.test_scenarios:
        lines.append("\n### 🎯 Test Scenarios Covered\n")
        for scenario in test_plan.test_scenarios:
            lines.append(f"- **{scenario.name}** ({scenario.priority}): {scenario.description}")
    
    lines.append("\n---")
    lines.append("*Generated by Browser-Use PR Testing Agent*")
    
    return "\n".join(lines)


# ===== Main Tab Creation =====

def create_pr_testing_agent_tab(webui_manager: WebuiManager):
    """Creates the PR Testing Agent tab with complete workflow"""
    
    components = {}
    
    with gr.Column():
        gr.Markdown("## 🔍 Pull Request Testing Automation")
        gr.Markdown(
            "Automated PR validation: Connect to Azure DevOps → Select PR → "
            "Generate test plan with AI → Execute automated tests → Post results"
        )
        
        # ===== Phase 1: Azure DevOps Configuration =====
        with gr.Group():
            gr.Markdown("### 📋 Step 1: Azure DevOps Configuration")
            
            with gr.Row():
                org_input = gr.Textbox(
                    label="Organization",
                    placeholder="myorg",
                    scale=1
                )
                project_input = gr.Textbox(
                    label="Project",
                    placeholder="MyProject",
                    scale=1
                )
            
            with gr.Row():
                repo_input = gr.Textbox(
                    label="Repository",
                    placeholder="my-repo",
                    scale=2
                )
                branch_input = gr.Textbox(
                    label="Target Branch (optional)",
                    placeholder="main",
                    scale=1
                )
            
            pat_input = gr.Textbox(
                label="Personal Access Token (PAT)",
                type="password",
                placeholder="Enter your Azure DevOps PAT"
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
        "project_input": project_input,
        "repo_input": repo_input,
        "branch_input": branch_input,
        "pat_input": pat_input,
        "fetch_button": fetch_button,
        "pr_dataframe": pr_dataframe,
        "llm_provider_dropdown": llm_provider_dropdown,
        "llm_model_dropdown": llm_model_dropdown,
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
    
    async def fetch_wrapper(org, proj, repo, branch, pat):
        async for update in fetch_pull_requests_handler(org, proj, repo, branch, pat):
            yield (
                update.get("pr_dataframe", gr.update()),
                update.get("status_output", "")
            )
    
    async def validate_wrapper(comps: Dict[Component, Any]):
        async for update in validate_pr_handler(webui_manager, comps):
            yield (
                update.get("status_output", ""),
                update.get("context_display", ""),
                update.get("test_plan_display", ""),
                update.get("results_display", ""),
                update.get("final_output", "")
            )
    
    # Wire up events
    fetch_button.click(
        fetch_wrapper,
        inputs=[org_input, project_input, repo_input, branch_input, pat_input],
        outputs=[pr_dataframe, status_output]
    )
    
    validate_button.click(
        validate_wrapper,
        inputs=webui_manager.get_components(),
        outputs=[status_output, context_display, test_plan_display, results_display, final_output]
    )
