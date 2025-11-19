"""
AI-powered test plan generator
Uses LLM to analyze PR context and generate comprehensive test plans
"""
import json
import logging
import re
from typing import List, Optional
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage

from src.utils import llm_provider
from .schemas import PRContext, TestPlan, TestInstruction, TestScenario, FileChange

logger = logging.getLogger(__name__)


class TestGenerator:
    """Generates test plans using LLM based on PR context"""
    
    def __init__(
        self, 
        provider: str = "openai", 
        model_name: str = "gpt-4o", 
        temperature: float = 0.7,
        api_key: Optional[str] = None
    ):
        """
        Initialize test generator with LLM
        
        Args:
            provider: LLM provider (openai, anthropic, google, etc.)
            model_name: Model name
            temperature: Temperature for generation
            api_key: Optional API key override
        """
        try:
            kwargs = {
                "provider": provider,
                "model_name": model_name,
                "temperature": temperature
            }
            if api_key:
                kwargs["api_key"] = api_key
            
            self.llm = llm_provider.get_llm_model(**kwargs)
            logger.info(f"Initialized TestGenerator with {provider}/{model_name}")
        except Exception as e:
            logger.error(f"Failed to initialize LLM: {e}")
            raise
    
    async def generate_test_plan(self, pr_context: PRContext) -> TestPlan:
        """
        Generate comprehensive test plan from PR context
        
        Args:
            pr_context: PR context with code changes
        
        Returns:
            Complete test plan with scenarios and steps
        """
        logger.info(f"Generating test plan for PR #{pr_context.pr_id}")
        
        try:
            # Create messages directly without template to avoid escaping issues
            messages = [
                SystemMessage(content=self._get_system_prompt()),
                HumanMessage(content=self._format_pr_context(pr_context))
            ]
            
            # Generate test plan
            response = await self.llm.ainvoke(messages)
            
            # Parse response - handle different content types
            content = response.content
            if isinstance(content, list):
                # For some LLMs, content is a list of content blocks
                content = " ".join([str(item) if not isinstance(item, dict) else item.get("text", str(item)) for item in content])
            elif not isinstance(content, str):
                content = str(content)
            
            test_plan = self._parse_llm_response(content, pr_context.pr_id)
            
            logger.info(
                f"Generated test plan: {len(test_plan.test_scenarios)} scenarios, "
                f"{len(test_plan.manual_steps)} manual steps, "
                f"{len(test_plan.automated_steps)} automated steps"
            )
            
            return test_plan
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            logger.error(f"Failed to generate test plan: {e}\n{error_details}")
            # Return minimal test plan on error
            return TestPlan(
                pr_id=pr_context.pr_id,
                summary=f"Failed to generate test plan: {str(e)}",
                test_scenarios=[],
                manual_steps=[],
                automated_steps=[],
                prerequisites=["Manual review required due to generation error"],
                test_data_requirements=[]
            )
    
    def _get_system_prompt(self) -> str:
        """Get system prompt for test generation"""
        return """You are an expert QA engineer and test automation specialist analyzing pull requests to generate comprehensive test plans.

Your task is to analyze the PR context (code changes, impacted areas, work items) and generate:
1. **Test Scenarios**: High-level test scenarios covering all impacted functionality
2. **Manual Testing Steps**: Detailed step-by-step instructions for manual QA
3. **Automated Testing Steps**: Browser automation steps that can be executed by Playwright/Browser-Use
4. **Prerequisites**: Required setup, test data, or configuration
5. **Test Data Requirements**: Specific test data needed

**Focus Areas:**
- **API Changes**: Test request/response formats, status codes, error handling, validation rules, authentication
- **UI Changes**: Test user interactions, form validations, button clicks, navigation, visual elements
- **Business Logic**: Test workflows, calculations, state management, data transformations
- **Database Changes**: Test data integrity, migrations, CRUD operations
- **Integration Points**: Test interactions between components/services

**Test Types to Include:**
- **Positive Tests**: Happy path scenarios with valid inputs
- **Negative Tests**: Error handling with invalid inputs, edge cases
- **Edge Cases**: Boundary values, empty states, concurrent operations

**Output Format:**
Return ONLY valid JSON (no markdown, no explanation) with this exact structure:
{{
  "summary": "Brief 1-2 sentence overview of what needs testing",
  "test_scenarios": [
    {{
      "name": "Scenario name",
      "description": "What this scenario tests",
      "priority": "high|medium|low",
      "test_type": "functional|integration|regression|smoke"
    }}
  ],
  "manual_steps": [
    {{
      "step_number": 1,
      "action_type": "navigate|click|input|assert|wait|extract",
      "description": "Clear description of what to do",
      "target": "Element description or CSS selector",
      "input_value": "Value to input (if applicable)",
      "expected_result": "What should happen",
      "test_type": "positive|negative|edge_case"
    }}
  ],
  "automated_steps": [
    {{
      "step_number": 1,
      "action_type": "navigate|click|input|assert|wait",
      "description": "Action description for automation",
      "target": "CSS selector or element identifier",
      "input_value": "Input value if needed",
      "expected_result": "Expected outcome to verify",
      "test_type": "positive|negative|edge_case"
    }}
  ],
  "prerequisites": ["Setup step 1", "Setup step 2"],
  "test_data_requirements": ["Data requirement 1", "Data requirement 2"]
}}

**Important Guidelines:**
- Generate at least 3-5 test scenarios covering different aspects
- Create 5-10 manual steps with clear instructions
- Create 3-7 automated steps that can be executed by browser automation
- Be specific about selectors and expected results for automated tests
- Include both positive and negative test cases
- Focus on changes mentioned in the PR context"""
    
    def _format_pr_context(self, pr_context: PRContext) -> str:
        """Format PR context for LLM consumption"""
        context_parts = [
            f"**Pull Request #{pr_context.pr_id}: {pr_context.title}**\n",
            f"**Author:** {pr_context.author}",
            f"**Branch:** {pr_context.source_branch} → {pr_context.target_branch}\n"
        ]
        
        # Add description if available
        if pr_context.description:
            context_parts.append(f"**Description:**\n{pr_context.description}\n")
        
        # Add file changes summary
        if pr_context.file_changes:
            context_parts.append(f"**Changed Files ({len(pr_context.file_changes)}):**")
            for change in pr_context.file_changes[:15]:  # Limit to first 15 files
                context_parts.append(
                    f"  - {change.change_type.upper()}: {change.path} "
                    f"(+{change.additions}/-{change.deletions})"
                )
            if len(pr_context.file_changes) > 15:
                context_parts.append(f"  ... and {len(pr_context.file_changes) - 15} more files\n")
        
        # Add impacted areas
        context_parts.append("\n**Impacted Areas:**")
        
        if pr_context.impacted_modules:
            context_parts.append(f"  - **Modules:** {', '.join(pr_context.impacted_modules)}")
        
        if pr_context.impacted_apis:
            context_parts.append(f"  - **APIs:** {', '.join(pr_context.impacted_apis)}")
        
        if pr_context.impacted_ui_components:
            context_parts.append(f"  - **UI Components:** {', '.join(pr_context.impacted_ui_components)}")
        
        if pr_context.impacted_database:
            context_parts.append(f"  - **Database:** {', '.join(pr_context.impacted_database)}")
        
        if not any([
            pr_context.impacted_modules,
            pr_context.impacted_apis,
            pr_context.impacted_ui_components,
            pr_context.impacted_database
        ]):
            context_parts.append("  - None identified (general code changes)")
        
        # Add linked work items with detailed information (optimized for speed)
        if pr_context.linked_work_items:
            context_parts.append("\n**Linked Work Items (CRITICAL - Use for test context):**")
            for item in pr_context.linked_work_items[:3]:  # Limit to first 3 for speed
                fields = item.get('fields', {})
                item_id = item.get('id', 'Unknown')
                item_type = fields.get('System.WorkItemType', 'WorkItem')
                item_title = fields.get('System.Title', 'No title')
                item_state = fields.get('System.State', 'Unknown')
                
                context_parts.append(f"\n  **#{item_id} - {item_type}: {item_title}**")
                context_parts.append(f"    - State: {item_state}")
                
                # Add description (reduced length)
                description = fields.get('System.Description', '')
                if description:
                    clean_desc = re.sub(r'<[^>]+>', '', description).strip()
                    if clean_desc:
                        context_parts.append(f"    - Description: {clean_desc[:200]}")
                
                # Add acceptance criteria (VERY IMPORTANT for testing, but reduced)
                acceptance = fields.get('Microsoft.VSTS.Common.AcceptanceCriteria', '')
                if acceptance:
                    clean_acceptance = re.sub(r'<[^>]+>', '', acceptance).strip()
                    if clean_acceptance:
                        context_parts.append(f"    - **Acceptance Criteria:** {clean_acceptance[:300]}")
                
                # Add reproduction steps (for bugs, reduced)
                repro_steps = fields.get('Microsoft.VSTS.TCM.ReproSteps', '')
                if repro_steps:
                    clean_repro = re.sub(r'<[^>]+>', '', repro_steps).strip()
                    if clean_repro:
                        context_parts.append(f"    - **Repro Steps:** {clean_repro[:200]}")
        
        # Add commit summary (reduced for speed)
        if pr_context.commits:
            context_parts.append(f"\n**Commits:** {len(pr_context.commits)} commit(s)")
            for commit in pr_context.commits[:2]:  # Show only first 2 commits
                commit_msg = commit.get('comment', 'No message')
                context_parts.append(f"  - {commit_msg[:60]}")
        
        context_parts.append("\n**Task:** Generate a comprehensive test plan for this PR.")
        
        return "\n".join(context_parts)
    
    def _parse_llm_response(self, response: str, pr_id: int) -> TestPlan:
        """
        Parse LLM JSON response into TestPlan model
        
        Args:
            response: LLM response text
            pr_id: Pull request ID
        
        Returns:
            Parsed TestPlan object
        """
        try:
            # Extract JSON from markdown code blocks if present
            json_str = response.strip()
            
            if "```json" in json_str:
                json_str = json_str.split("```json")[1].split("```")[0].strip()
            elif "```" in json_str:
                json_str = json_str.split("```")[1].split("```")[0].strip()
            
            # Parse JSON
            data = json.loads(json_str)
            
            # Convert to TestPlan with validation
            test_plan = TestPlan(
                pr_id=pr_id,
                summary=data.get("summary", "Test plan generated"),
                test_scenarios=[
                    TestScenario(**scenario) 
                    for scenario in data.get("test_scenarios", [])
                ],
                manual_steps=[
                    TestInstruction(**step)
                    for step in data.get("manual_steps", [])
                ],
                automated_steps=[
                    TestInstruction(**step)
                    for step in data.get("automated_steps", [])
                ],
                prerequisites=data.get("prerequisites", []),
                test_data_requirements=data.get("test_data_requirements", [])
            )
            
            return test_plan
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from LLM response: {e}")
            logger.debug(f"Response: {response[:500]}")
            
            # Try to extract partial information
            return self._create_fallback_test_plan(pr_id, response)
        
        except Exception as e:
            logger.error(f"Failed to create TestPlan from parsed data: {e}")
            return self._create_fallback_test_plan(pr_id, response)
    
    def _create_fallback_test_plan(self, pr_id: int, response: str) -> TestPlan:
        """Create a fallback test plan when parsing fails"""
        return TestPlan(
            pr_id=pr_id,
            summary="Test plan generation partially failed. Manual review required.",
            test_scenarios=[
                TestScenario(
                    name="Manual Review Required",
                    description="LLM response could not be fully parsed. Review changes manually.",
                    priority="high",
                    test_type="functional"
                )
            ],
            manual_steps=[
                TestInstruction(
                    step_number=1,
                    action_type="assert",
                    description="Review the PR changes manually and create test cases",
                    expected_result="All changes are tested appropriately",
                    test_type="positive"
                )
            ],
            automated_steps=[],
            prerequisites=["Manual review of LLM response", "Check application logs"],
            test_data_requirements=[]
        )
