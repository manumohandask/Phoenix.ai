# Quick Start Guide - PR Testing Tool for HRB TPSC

## Your Repository Configuration

**Azure DevOps URL**: https://dev.azure.com/hrblock-ca/TPS%20Cloud/_git/HRB-TPSC-QA-EnterpriseAutomation

**Connection Details**:
- Organization: `hrblock-ca`
- Project: `TPS Cloud`
- Repository: `HRB-TPSC-QA-EnterpriseAutomation`

## Step 1: Generate Personal Access Token (PAT)

1. Go to: https://dev.azure.com/hrblock-ca/_usersSettings/tokens
2. Click **+ New Token**
3. Configure:
   - Name: `PR Testing Automation`
   - Organization: `hrblock-ca`
   - Expiration: 30 days (or your preference)
   - Scopes: **Custom defined**
     - ✅ Code → **Read**
     - ✅ Pull Request Threads → **Read & Write**
4. Click **Create** and **COPY THE TOKEN** (you won't see it again!)

## Step 2: Test Your Connection

Run this to verify everything works:

```powershell
python tests/test_azure_devops_connection.py
```

Enter your details when prompted:
- Organization: `hrblock-ca`
- Project: `TPS Cloud`
- Repository: `HRB-TPSC-QA-EnterpriseAutomation`
- PAT: [paste your token]

If successful, you'll see:
```
✅ ALL TESTS PASSED!
Found X pull requests
```

## Step 3: Start the WebUI

```powershell
python webui.py --ip 127.0.0.1 --port 7788
```

Open in browser: http://127.0.0.1:7788

## Step 4: Use the PR Testing Agent

1. Click on **🔍 PR Testing Agent** tab
2. Enter connection details:
   - Organization: `hrblock-ca`
   - Project: `TPS Cloud`
   - Repository: `HRB-TPSC-QA-EnterpriseAutomation`
   - Target Branch: _(optional, leave empty for all)_
   - PAT: _(paste your token)_
3. Click **📥 Fetch Pull Requests**
4. Select a PR from the table
5. Configure test generation:
   - LLM Provider: OpenAI (or Anthropic, Google, etc.)
   - Model: gpt-4o (or your preference)
   - Headless: ✅ (faster) or ❌ (watch execution)
6. Click **✅ Validate Pull Request**

The tool will:
- ✅ Extract PR context (files, commits, work items)
- ✅ Generate test plan using AI
- ✅ Execute automated tests (coming soon)
- ✅ Post results to PR

## Troubleshooting

**401 Unauthorized**: PAT is invalid or expired
**403 Forbidden**: You don't have access to the repository
**404 Not Found**: Organization/project/repository name is incorrect

For detailed help: See `docs/AZURE_DEVOPS_SETUP.md`

## Required API Keys

For test generation, you need an LLM API key:
- **OpenAI**: Get from https://platform.openai.com/api-keys
- **Anthropic**: Get from https://console.anthropic.com/settings/keys
- **Google**: Get from https://console.cloud.google.com/

Set in WebUI or add to `.env`:
```env
OPENAI_API_KEY=sk-...
# or
ANTHROPIC_API_KEY=sk-ant-...
```

## Security Reminder

🔐 **Never commit your PAT or API keys to git!**
- Add `.env` to `.gitignore`
- Revoke PATs when no longer needed
- Rotate keys regularly
