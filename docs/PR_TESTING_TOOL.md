# PR Testing Automation Tool

Automated pull request validation tool integrated into Browser Use Web UI. Connects to Azure DevOps to fetch PRs, uses AI to generate test plans, and executes automated browser tests.

## Features

- 🔗 **Azure DevOps Integration**: Connect directly to your Azure DevOps organization
- 📋 **PR Context Extraction**: Automatically analyzes code changes, impacted modules, APIs, and UI components
- 🤖 **AI-Powered Test Generation**: Uses LLM to create comprehensive test plans with manual and automated steps
- 🌐 **Automated Browser Testing**: Executes tests using Browser-Use agent with Playwright
- 💬 **Automated Reporting**: Posts test results directly to PR comments

## Architecture

```
src/
├── utils/
│   └── azure_devops_client.py      # Azure DevOps REST API client
├── agent/
│   └── pr_testing/
│       ├── schemas.py              # Pydantic data models
│       ├── code_analyzer.py        # Code impact analysis
│       └── test_generator.py       # AI test plan generation
└── webui/
    └── components/
        └── pr_testing_agent_tab.py # Complete UI workflow
```

## Setup

### 1. Install Dependencies

```bash
# Activate your virtual environment first
.\.venv\Scripts\Activate.ps1  # Windows PowerShell

# Install new dependencies
uv pip install aiohttp==3.9.1
```

### 2. Azure DevOps Configuration

You need a Personal Access Token (PAT) with the following permissions:
- **Code**: Read
- **Pull Request Threads**: Read & Write
- **Work Items**: Read

Create a PAT at: `https://dev.azure.com/{organization}/_usersSettings/tokens`

### 3. LLM Configuration

Ensure you have at least one LLM provider configured in your `.env`:

```env
# Example: OpenAI
OPENAI_API_KEY=sk-...

# Or Anthropic
ANTHROPIC_API_KEY=sk-ant-...

# Or Google
GOOGLE_API_KEY=...
```

## Usage

### Step 1: Launch Web UI

```bash
python webui.py --ip 127.0.0.1 --port 7788
```

Navigate to: `http://127.0.0.1:7788`

### Step 2: Navigate to PR Testing Agent Tab

Click on **"🔍 PR Testing Agent"** tab

### Step 3: Configure Azure DevOps

Fill in:
- **Organization**: Your Azure DevOps org name (e.g., `mycompany`)
- **Project**: Project name (e.g., `MyProject`)
- **Repository**: Repository name (e.g., `my-web-app`)
- **Target Branch** (optional): Filter PRs by target branch (e.g., `main`)
- **PAT**: Your Personal Access Token

Click **"📥 Fetch Pull Requests"**

### Step 4: Select Pull Request

- Browse the list of fetched PRs in the table
- Click on a row to select it

### Step 5: Configure Test Generation

- **LLM Provider**: Choose your provider (openai, anthropic, google, etc.)
- **Model**: Select the model (gpt-4o, claude-3-5-sonnet, etc.)
- **Headless Mode**: Check to run browser tests in background

### Step 6: Run Validation

Click **"✅ Validate Pull Request"**

Watch the 4-phase execution:
1. **Phase 1**: Extract PR context (files, commits, work items)
2. **Phase 2**: Generate test plan with AI
3. **Phase 3**: Execute automated browser tests
4. **Phase 4**: Post results to PR as comment

### Step 7: Review Results

View results in tabs:
- **📊 PR Context**: Analyzed code changes and impacts
- **📋 Test Plan**: Generated test scenarios and steps
- **✅ Execution Results**: Test pass/fail status with details
- **💬 PR Comment**: Formatted comment posted to Azure DevOps

## Workflow Details

### Phase 1: Context Extraction

The tool fetches:
- PR metadata (title, description, author, reviewers)
- All commits and changed files
- Linked work items
- File diffs and change types

Then analyzes:
- **Impacted Modules**: Identifies affected code modules
- **Impacted APIs**: Detects API/endpoint changes
- **Impacted UI Components**: Finds modified UI elements
- **Database Changes**: Identifies migration or schema changes

### Phase 2: Test Generation

The LLM receives the PR context and generates:

1. **Test Scenarios**: High-level test cases covering all impacts
2. **Manual Steps**: Human-readable instructions for QA
3. **Automated Steps**: Browser actions for automation
4. **Prerequisites**: Required setup (test data, config)

Test types include:
- ✅ **Positive tests**: Happy path scenarios
- ❌ **Negative tests**: Error handling validation
- 🔍 **Edge cases**: Boundary conditions

### Phase 3: Browser Automation

For each automated test step:
1. Creates a new browser context
2. Initializes BrowserUseAgent with the step description
3. Executes the task (navigate, click, input, assert)
4. Captures results and screenshots
5. Marks as PASS/FAIL/ERROR

### Phase 4: Results Reporting

Generates markdown comment with:
- Overall pass rate and execution time
- Breakdown by test status
- Detailed step results table
- Test scenarios covered

Posts to Azure DevOps PR automatically.

## Example Output

### PR Context Display
```
📋 Pull Request Context
PR #123: Add user authentication feature
Author: John Doe
Branch: feature/auth → main
Files Changed: 12

Impact Analysis:
- Modules: auth, api, frontend
- APIs: LoginController, UserService
- UI Components: LoginForm, UserProfile
- Database: Migration: add_users_table
```

### Test Plan Display
```
📝 Generated Test Plan
Summary: Test user authentication flow including login, logout, and session management

Test Scenarios: 5
Manual Steps: 8
Automated Steps: 5

Scenarios:
- User Login with Valid Credentials (high): Verify successful login
- User Login with Invalid Credentials (high): Test error handling
- Session Expiration (medium): Verify timeout behavior
...
```

### Execution Results
```
✅ Test Execution Results
Pass Rate: 80.0% (4/5)
Execution Time: 45.2s

Breakdown:
- ✅ Passed: 4
- ❌ Failed: 1
- 🔥 Errors: 0

Step Details:
| Step | Status | Description | Time |
|------|--------|-------------|------|
| 1 | ✅ PASS | Navigate to login page | 5.2s |
| 2 | ✅ PASS | Enter valid credentials | 3.1s |
| 3 | ✅ PASS | Click login button | 2.8s |
| 4 | ❌ FAIL | Verify redirect to dashboard | 8.5s |
| 5 | ✅ PASS | Check session cookie | 1.2s |
```

## Troubleshooting

### "Failed to fetch PRs: Unauthorized"
- Verify your PAT is correct and not expired
- Ensure PAT has required permissions (Code: Read, PR Threads: Read & Write)

### "Failed to generate test plan"
- Check your LLM API key is set in `.env`
- Verify internet connectivity
- Try a different LLM provider

### "Browser test timeout"
- Increase timeout in code (default: 2 minutes per step)
- Check if application URL is accessible
- Run in non-headless mode to watch execution

### "Could not post comment"
- Verify PAT has "Pull Request Threads: Write" permission
- Check if PR is still active (not abandoned)

## Advanced Configuration

### Custom Test Generation Prompts

Edit `src/agent/pr_testing/test_generator.py` → `_get_system_prompt()` to customize how tests are generated.

### Browser Configuration

Modify browser settings in `src/webui/components/pr_testing_agent_tab.py`:

```python
browser_config = BrowserConfig(
    headless=True,
    disable_security=False,  # Set True for testing on local dev
    extra_browser_args=[]
)
```

### Timeout Adjustments

Change test step timeout in `_execute_browser_tests()`:

```python
history = await asyncio.wait_for(
    agent.run(max_steps=10),
    timeout=180  # 3 minutes instead of 2
)
```

## Integration with CI/CD

You can trigger PR validation programmatically:

```python
from src.utils.azure_devops_client import AzureDevOpsClient
from src.agent.pr_testing.test_generator import TestGenerator
from src.agent.pr_testing.code_analyzer import CodeAnalyzer

# Fetch PR
client = AzureDevOpsClient(org, project, pat, repo)
pr_details = await client.get_pr_details(pr_id)

# Generate tests
analyzer = CodeAnalyzer()
pr_context = analyzer.analyze_pr_impact(pr_context)
test_gen = TestGenerator(provider="openai", model_name="gpt-4o")
test_plan = await test_gen.generate_test_plan(pr_context)

# Execute and report
# ... (see pr_testing_agent_tab.py for full implementation)
```

## Team Responsibilities

- **Team 1 (Sachin & Lekshmi)**: Azure DevOps integration & context extraction
- **Team 2 (Gauri & Gayathri)**: AI test generation & prompt engineering
- **Team 3 (Sreeraj & Manu)**: Browser automation & UI integration

## Contributing

When adding new features:
1. Follow existing patterns in `src/agent/pr_testing/`
2. Add Pydantic models to `schemas.py` for type safety
3. Update UI in `pr_testing_agent_tab.py`
4. Add tests in `tests/test_pr_testing.py`

## License

Same as main Browser Use Web UI project.
