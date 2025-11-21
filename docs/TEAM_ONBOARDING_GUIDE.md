# Phoenix AI – Team Onboarding & Working Principles

This guide explains how Phoenix AI works so that every team member (technical or not-so-technical) can understand what happens from the moment you open the app to the point you see test results. It avoids deep code details while still showing the moving parts.

---
## 1. What Problem Are We Solving?
Modern software teams struggle with:
- Writing and maintaining lots of manual tests.
- Checking whether new code (a Pull Request) breaks something.
- Validating both the API (data) and the UI (what users see) in one flow.

Phoenix AI turns natural language instructions (plain English) into real automated checks across code changes, APIs, and the browser.

---
## 2. Core Idea (In One Sentence)
You describe what you want to verify; Phoenix AI plans and performs the steps (API calls, browser actions) and gives you clear, structured results you can trust.

---
## 3. Main Building Blocks
| Block | What It Does | Example |
|-------|--------------|---------|
| Web UI (Gradio) | Where you type prompts and see results | Tabs for API Testing, Browser Use, PR Testing |
| Agent Settings | Central place where we set AI model & API key | Choose provider (OpenAI, Anthropic, etc.) |
| API Testing Agent | Turns a sentence into a Gherkin scenario & runs it | "Test users API" → structured steps |
| Browser Use Agent | Autonomously clicks, types, navigates like a tester | "Log in and verify dashboard" |
| PR Testing (Concept) | Looks at code changes to suggest tests | Changed file → propose scenarios |
| Controller | Dispatches structured actions to the browser | Action: Click button #login |
| Browser (Playwright) | Automates real web pages safely | Opens pages, extracts text, takes screenshots |
| Artifacts | Saved history of what happened | JSON results, screenshots, GIF replay |

---
## 4. Typical Workflow Scenarios
### A. API Test
1. You describe a test in plain English.
2. Phoenix generates a Gherkin scenario (Given / When / Then lines) automatically.
3. You click Execute; it extracts the URL, method (GET/POST), and expectations from the scenario.
4. It calls the API and checks: Did we get the right status? Does the response include expected text/data?
5. You see a result JSON with pass/fail and full response.

### B. Browser Autonomy
1. You set a goal like: "Go to the login page and sign in, then confirm greeting appears."
2. Phoenix asks the AI to break this into actions (open page, fill fields, click login).
3. Each action is executed in a real browser window (you can watch via screenshots or VNC).
4. After each step, Phoenix saves what happened and decides the next step until goal complete.
5. A GIF and a JSON history show everything for review or audit.

### C. PR Impact (Conceptual)
1. Phoenix looks at which files changed.
2. It groups the changes into risk areas (e.g., “Authentication code modified”).
3. It suggests tests you might run immediately (API or UI scenarios).

---
## 5. How an API Scenario Is Built
Input (your words):
```
Test GET https://jsonplaceholder.typicode.com/users and make sure the status is 200 and the name "Leanne Graham" appears.
```
Generated Gherkin:
```gherkin
Feature: Users API Testing
Scenario: Validate users endpoint
  Given the API endpoint is "https://jsonplaceholder.typicode.com/users"
  When I send a GET request
  Then the response status code should be 200
  Then the response should contain "Leanne Graham"
```
Execution Outcome (simplified JSON):
```json
{
  "status": "passed",
  "api_endpoint": "https://jsonplaceholder.typicode.com/users",
  "status_code": 200,
  "contains_Leanne_Graham": true,
  "full_response_excerpt": "[ ... trimmed ... ]"
}
```

---
## 6. How the Browser Agent Thinks
It repeats a loop:
1. Look at goal and what happened so far.
2. Decide next action (e.g., GoToUrl, Click, InputText, ExtractContent).
3. Perform the action in the browser.
4. Record screenshot + any extracted text.
5. Decide next step until success or it says DONE.

This means you do NOT script every click manually; Phoenix figures out steps based on your goal.

---
## 7. What You Need to Configure First
| Setting | Why It Matters |
|---------|----------------|
| LLM Provider & API Key | The AI brain Phoenix uses to plan/generate steps |
| Browser Settings (optional) | Whether to run headless, window size, custom Chrome profile |
| Environment File (.env) | Secure place for keys so they aren’t hardcoded |

If something is missing (like an API key), Phoenix will show an error before running a test.

---
## 8. What Gets Saved
- API test results: response and validation outcome.
- Browser session: screenshots + GIF + history of steps.
- These are stored under `tmp/` folders and can be deleted safely when not needed.

None of these runtime artifacts are committed to the repository.

---
## 9. Reading the Artifacts
| Artifact | What to Look For |
|----------|------------------|
| Test Result JSON | status (passed/failed), errors, timing |
| Browser History JSON | sequence of actions, any errors encountered |
| GIF Replay | Visual confirmation the journey made sense |
| Full API Response | Verify returned fields (IDs, names, etc.) |

If a test fails, start with the JSON errors, then check the GIF for visual clues.

---
## 10. Common Questions
| Question | Short Answer |
|----------|--------------|
| Do I need to know Gherkin syntax? | Not really; Phoenix generates it. You can edit it if you want. |
| Can I re-run a test with small changes? | Yes—edit the scenario box or prompt and click Execute again. |
| Does it work with private APIs? | Yes—add auth tokens in `.env` and mention them in your prompt if needed (future enhancement may automate). |
| How do I clean old runs? | Delete folders under `tmp/` (they’re safe). |
| Can I watch the browser live? | Yes—using the provided VNC view if using Docker setup. |

---
## 11. Mental Model Summary
Think of Phoenix AI as three cooperating helpers:
1. **Translator** – Turns your intent into structured steps (Gherkin / actions).
2. **Executor** – Performs the web/API steps in the real world.
3. **Recorder** – Captures everything so you can verify or share it.

---
## 12. Light Glossary
| Term | Simple Meaning |
|------|----------------|
| Gherkin | A structured way to describe tests (Given / When / Then). |
| Endpoint | URL of an API we call. |
| LLM | The AI model that understands and plans (Large Language Model). |
| Action | A single browser operation like Click or Navigate. |
| Artifact | A saved file showing what happened. |

---
## 13. Quick Start (Non-Technical)
1. Open Phoenix AI in your browser.
2. Go to Agent Settings → fill AI provider + key.
3. Go to API Testing → describe a test → click Generate → Execute.
4. Review result JSON (status + response).
5. (Optional) Try a browser goal in the Browser Use tab.

You’ve now performed full automated validation without writing code.

---
## 14. When to Ask for Help
Ask a developer teammate if:
- Scenario keeps failing and JSON shows strange errors.
- Browser actions stop mid-way repeatedly.
- You need to integrate with secure internal systems or new providers.

---
## 15. What’s Coming Next (Roadmap Highlights)
- Smarter response checks (schemas instead of only text).
- Bulk generation of tests from API specs.
- Performance timing alerts.
- Flakiness tracking (mark unstable tests).

---
## 16. Elevator Pitch You Can Share
“Phoenix AI lets us describe what we want to verify, and it automatically tests both our APIs and web app. It saves us time, reduces manual scripting, and gives us clear evidence of what happened.”

---
## 17. One Page Summary (Copy/Paste Friendly)
Phoenix AI converts plain English instructions into automated API and browser tests. You set up an AI provider once, type what you want to check, and Phoenix handles planning, execution, and evidence collection. Results come back as easy-to-read JSON plus visual GIFs. It helps us validate changes faster and more reliably without requiring everyone to be a test automation expert.

---
If you need a shorter version for slides or onboarding emails, let us know—we can auto-generate one.
