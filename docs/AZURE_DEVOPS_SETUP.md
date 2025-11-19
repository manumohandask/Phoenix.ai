# Azure DevOps Setup Guide for PR Testing Tool

## Your Configuration

Based on your Azure DevOps repository, here are the connection details:

### Repository Details
- **Organization**: `hrblock-ca`
- **Project**: `TPS Cloud`
- **Repository**: `HRB-TPSC-QA-EnterpriseAutomation`
- **URL**: https://dev.azure.com/hrblock-ca/TPS%20Cloud/_git/HRB-TPSC-QA-EnterpriseAutomation

### How to Use in the PR Testing Agent Tab

1. **Organization**: Enter `hrblock-ca`
2. **Project**: Enter `TPS Cloud` (without URL encoding)
3. **Repository**: Enter `HRB-TPSC-QA-EnterpriseAutomation`
4. **Target Branch**: Optional - leave empty for all branches, or enter specific branch like `main` or `develop`
5. **Personal Access Token (PAT)**: You need to generate this

## Creating a Personal Access Token (PAT)

### Step 1: Generate PAT in Azure DevOps
1. Go to https://dev.azure.com/hrblock-ca
2. Click on your profile icon (top right) → **User settings** → **Personal access tokens**
3. Click **+ New Token**
4. Configure:
   - **Name**: `PR Testing Automation` (or any descriptive name)
   - **Organization**: Select `hrblock-ca`
   - **Expiration**: Choose appropriate duration (30 days, 90 days, custom, or full access)
   - **Scopes**: Select **Custom defined**, then enable:
     - ✅ **Code** → **Read** (to fetch PR details and file contents)
     - ✅ **Pull Request Threads** → **Read & write** (to post comments back to PRs)
5. Click **Create**
6. **IMPORTANT**: Copy the token immediately - you won't be able to see it again!

### Step 2: Required Permissions
Your Azure DevOps account needs these permissions:
- Read access to the repository
- Access to view pull requests
- Permission to comment on pull requests

If you don't have these permissions, contact your Azure DevOps administrator.

## Using the PR Testing Tool

### Step-by-Step Workflow

1. **Start the WebUI**
   ```powershell
   python webui.py --ip 127.0.0.1 --port 7788
   ```
   Access at: http://127.0.0.1:7788

2. **Navigate to PR Testing Agent Tab**
   Click on "🔍 PR Testing Agent" tab

3. **Configure Azure DevOps**
   - Organization: `hrblock-ca`
   - Project: `TPS Cloud`
   - Repository: `HRB-TPSC-QA-EnterpriseAutomation`
   - Target Branch: (optional - e.g., `main`)
   - PAT: Paste your personal access token

4. **Fetch Pull Requests**
   Click "📥 Fetch Pull Requests" button
   - The tool will connect to Azure DevOps
   - Display all PRs in a table with ID, Title, Author, Status, etc.

5. **Select a PR**
   Click on a row in the PR table to select it

6. **Configure Test Generation**
   - Choose LLM Provider (OpenAI, Anthropic, Google, DeepSeek, Ollama)
   - Select Model (gpt-4o, claude-3-5-sonnet, etc.)
   - Check/uncheck headless mode for browser automation

7. **Validate Pull Request**
   Click "✅ Validate Pull Request" button
   
   The tool will:
   - **Phase 1**: Extract PR context (files changed, commits, work items)
   - **Phase 2**: Generate test plan using AI (scenarios, manual steps, automated steps)
   - **Phase 3**: Execute automated browser tests (if configured)
   - **Phase 4**: Post results as a comment to the PR

## Environment Variables (Optional)

Instead of entering credentials in the UI each time, you can set environment variables:

Create a `.env` file in the project root:

```env
# Azure DevOps Configuration
AZURE_DEVOPS_ORG=hrblock-ca
AZURE_DEVOPS_PROJECT=TPS Cloud
AZURE_DEVOPS_REPO=HRB-TPSC-QA-EnterpriseAutomation
AZURE_DEVOPS_PAT=your_personal_access_token_here

# LLM Provider (for test generation)
OPENAI_API_KEY=your_openai_key_here
# or
ANTHROPIC_API_KEY=your_anthropic_key_here
```

## Troubleshooting

### Common Issues

**Error: "Failed to fetch PRs: 401 Unauthorized"**
- Your PAT is invalid or expired
- Generate a new PAT with correct permissions

**Error: "Failed to fetch PRs: 404 Not Found"**
- Check organization/project/repository names are correct
- Ensure no extra spaces in the fields
- Project name should be `TPS Cloud` not `TPS%20Cloud`

**Error: "Failed to fetch PRs: 403 Forbidden"**
- Your account doesn't have access to the repository
- Contact your Azure DevOps admin for permissions

**No PRs showing up**
- The repository might not have any active PRs
- Try removing the branch filter
- Check the status filter (defaults to "all")

**LLM errors during test generation**
- Ensure you have a valid API key for your chosen provider
- Set the API key in UI or environment variables
- Check your API usage limits

### Debug Mode

To see detailed logs:
1. Check the terminal/console where you started `webui.py`
2. Look for log messages starting with:
   - `INFO [azure_devops_client]`
   - `ERROR [azure_devops_client]`
   - `INFO [pr_testing]`

## API Rate Limits

**Azure DevOps:**
- Free tier: No specific limits published, but use reasonable polling intervals
- If you get 429 errors, wait before retrying

**LLM Providers:**
- OpenAI: Check your tier limits at https://platform.openai.com/settings/limits
- Anthropic: Check usage at https://console.anthropic.com/settings/usage
- Google: Check quotas at https://console.cloud.google.com/

## Security Best Practices

1. **Never commit PATs to git**
   - Add `.env` to `.gitignore`
   - Use environment variables or secure vaults

2. **Rotate PATs regularly**
   - Set expiration dates
   - Regenerate every 30-90 days

3. **Limit PAT permissions**
   - Only grant Read access to Code
   - Only grant Read & Write to Pull Request Threads
   - Don't grant full access unless necessary

4. **Revoke PATs when done**
   - If testing is complete, revoke the PAT
   - Go to User Settings → Personal Access Tokens → Revoke

## Support

If you encounter issues:
1. Check the console logs for detailed error messages
2. Verify your Azure DevOps permissions
3. Test your PAT using Azure DevOps REST API directly:
   ```powershell
   $pat = "your_pat_here"
   $base64Pat = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes(":$pat"))
   $headers = @{
       "Authorization" = "Basic $base64Pat"
       "Content-Type" = "application/json"
   }
   Invoke-RestMethod -Uri "https://dev.azure.com/hrblock-ca/TPS%20Cloud/_apis/git/repositories/HRB-TPSC-QA-EnterpriseAutomation/pullrequests?api-version=7.0" -Headers $headers
   ```
