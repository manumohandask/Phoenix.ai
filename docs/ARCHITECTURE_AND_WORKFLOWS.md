# Phoenix AI - Technical Architecture & Workflow Documentation

**Version:** 1.0  
**Date:** November 2025  
**Project:** Phoenix AI - Intelligent E2E Testing & Automation Platform

---

## Table of Contents

1. [High-Level System Overview](#1-high-level-system-overview)
2. [Configuration & Initialization Flow](#2-configuration--initialization-flow)
3. [PR Testing Lifecycle](#3-pr-testing-lifecycle)
4. [API Testing Lifecycle (Simplified Gherkin Flow)](#4-api-testing-lifecycle-simplified-gherkin-flow)
5. [Browser Autonomy Lifecycle](#5-browser-autonomy-lifecycle)
6. [Element Handling & Robustness](#6-element-handling--robustness)
7. [Data & Observability](#7-data--observability)
8. [Error Handling & Recovery Strategy](#8-error-handling--recovery-strategy)
9. [Extensibility Points](#9-extensibility-points)
10. [End-to-End Example Walkthrough](#10-end-to-end-example-walkthrough)
11. [Architecture Diagrams](#11-architecture-diagrams)
12. [Key Design Principles](#12-key-design-principles)
13. [Future Roadmap](#13-future-roadmap)
14. [Appendix A: Glossary](#appendix-a-glossary)
15. [Appendix B: Configuration Reference](#appendix-b-configuration-reference)

---

## 1. High-Level System Overview

Phoenix AI unifies three intelligent testing domains:

- **PR & Code Impact Analysis**
- **API Testing** (Natural Language → Gherkin → Execution)
- **Autonomous Browser Interaction** (UI validation & multi-step flows)

### Core Building Blocks

| Component | Purpose |
|-----------|---------|
| **WebUI (Gradio)** | Collects user intent via tabbed interface |
| **Agent Settings Tab** | Supplies LLM provider, model, API key, base URL |
| **Domain Agents** | Orchestrate workflows (PRTestingAgent, APITestingAgent, BrowserUseAgent) |
| **CustomBrowser** | Wraps Playwright launch & context creation |
| **CustomController** | Registers & executes actions (navigation, input, extraction, file upload, MCP tools) |
| **LLM** | Drives planning (goals → structured actions) |
| **Artifacts** | JSON results, GIF replay, screenshots, agent history for transparency |

### System Philosophy

Phoenix AI operates on the principle of **declarative intent → structured execution → verifiable artifacts**. Users describe what they want to validate, and the system translates that into concrete actions with full transparency.

---

## 2. Configuration & Initialization Flow

### Step-by-Step Initialization

#### Step 1: WebUI Launch

User opens WebUI → Gradio loads components for:
- Agent Settings
- Browser Settings  
- API Testing
- PR Testing
- Browser Use

#### Step 2: Configuration Entry

User enters:
- **LLM provider** (e.g., `openai`, `google`, `anthropic`, `ollama`)
- **Model name** (e.g., `gpt-4o`, `gemini-2.0-flash`, `claude-3-5-sonnet`)
- **API key** / **base URL** (optional for self-hosted or proxy endpoints)

These settings are stored in component registry (`webui_manager.id_to_component`), available to all tabs.

#### Step 3: Agent Invocation

When an agent is invoked:
1. Tab handler fetches current values from component registry
2. Calls `llm_provider.get_llm_model()` to initialize LLM object with correct kwargs:
   - `provider`
   - `model_name`
   - `api_key`
   - `temperature`
   - `base_url` (optional)
3. Browser-specific settings passed into `BrowserConfig`

#### Step 4: Browser Initialization

On first browser task:
1. **CustomBrowser** launches Playwright (chromium channel) with anti-detection flags:
   - Custom window size
   - Remote debugging port handling
   - Headless modes
   - Deterministic rendering (optional)
2. A **CustomBrowserContext** merges global and per-run overrides

**Result:** A shared stateful environment where each agent can reliably access the same LLM and browser primitives.

---

## 3. PR Testing Lifecycle

### Detailed Flow

#### Step 1: PR Selection
User selects organization/project/repository → System pulls PR list via Azure DevOps client or analogous API.

#### Step 2: Data Fetching
The PR Testing agent fetches:
- **PR metadata** (title, description, commits)
- **Changed files** and diffs
- **Associated work items** (if integrated)

#### Step 3: Impact Analysis
Code analyzer scans diff to classify changes:
- Modified modules
- Potential API endpoints
- UI components (basic heuristic or rule-based)

#### Step 4: Test Plan Generation

LLM prompt constructed with:
- Changed file paths & diff snippets
- Work item context
- Historical patterns (if memory enabled)

LLM outputs **structured test plan**:
- Risk-based scenarios
- Manual verification steps
- Potential automated test candidates

#### Step 5: Output & Artifacts

| Artifact | Purpose |
|----------|---------|
| Test plan JSON | Structured summary of PR metadata |
| Test plan text | Human-readable scenarios |
| Risk analysis logs | Indicate high-impact areas |

**End State:** Reviewers see targeted tests tied to actual changes, accelerating validation.

**Future Extension:** Agent could generate Gherkin for new API endpoints or trigger BrowserUse flows automatically.

---

## 4. API Testing Lifecycle (Simplified Gherkin Flow)

### Current Streamlined Implementation

#### Step 1: Natural Language Input

User provides scenario description:
```
Test GET https://jsonplaceholder.typicode.com/users and confirm Leanne Graham appears.
```

#### Step 2: Gherkin Generation

`APITestingAgent.generate_gherkin_from_prompt()`:
1. Constructs system + user prompt for LLM
2. LLM returns structured JSON or Gherkin-like text
3. Agent formats into canonical Gherkin:

```gherkin
Feature: Users API

Scenario: Validate users endpoint
  Given the API endpoint is "https://jsonplaceholder.typicode.com/users"
  When I send a GET request
  Then the response status code should be 200
  Then the response should be a JSON array
  Then the response should contain a user with name "Leanne Graham"
```

#### Step 3: Execution

User clicks **Execute** → `execute_gherkin_scenario()` performs:

**Parsing:**
- URL (from `Given` line)
- HTTP method (from `When` line: GET/POST/PUT/DELETE)
- Expected status code (`Then` with "status code should be …")
- Content assertions ("should contain" …)
- Array structure check ("should be a JSON array")

#### Step 4: HTTP Request

HTTP request performed with:
```python
requests.request(method, url, headers=..., timeout=...)
```

#### Step 5: Validation & Results

**Response post-processing:**
- Attempt JSON parse, fallback to raw text
- Validate status code match
- Search content for specified substrings (exact match presence)
- Record extracted boolean flags (e.g., `contains_Leanne_Graham: true`)

**Results assembled:**
```json
{
  "test_status": "passed",
  "message": "Test passed successfully",
  "execution_time": "0.62s",
  "api_endpoint": "https://jsonplaceholder.typicode.com/users",
  "status_code": 200,
  "response_time_ms": 622.135,
  "full_response": [ ... entire JSON array ... ],
  "extracted_values": { "contains_Leanne_Graham": true },
  "validation_errors": [],
  "timestamp": "2025-11-20T18:34:35.769096"
}
```

Displayed in **Test Results** (Gradio code component).

#### Step 6: Clear & Reset

User can **Clear All** to reset:
- Prompt
- Status
- Gherkin text
- Results

### Design Choices

- **Fast iteration:** Minimal config surface
- **Auto parse fundamentals:** URL, method, status extracted automatically
- **Extensible:** Future schema assertions or JSONPath reintroduction possible

---

## 5. Browser Autonomy Lifecycle

### End-to-End Loop

#### Step 1: Task Input
User enters a multi-step task or pastes Gherkin scenario into BrowserUse agent tab.

Example:
```
Log into demo site and verify dashboard message appears.
```

#### Step 2: Initialization

System performs:
- **LLM loaded** (if credentials present)
- **CustomBrowser** creates/gets context:
  - Viewport dimensions
  - Proxy settings
  - Headless options
- **CustomController** registers actions:
  - Baseline: `GoToUrl`, `ClickElement`, `InputText`, `ExtractPageContent`, `Scroll`, `OpenTab`, `SwitchTab`, `SearchGoogle`
  - Custom: `ask_for_assistant`, `upload_file`
  - External: MCP tools (if configured)

#### Step 3: Planning Cycle

Agent builds **current state snapshot**:
- Current URL
- DOM summary
- Memory excerpts from prior steps

**LLM receives:**
- Task goal
- Prior steps & their outcomes
- Extracted page content (when available)
- Optional memory summarization slice

**LLM outputs:**
- Next high-level objective
- Structured action JSON

Example:
```json
{
  "go_to_url": {
    "url": "https://example.com/login"
  }
}
```

#### Step 4: Action Dispatch

`CustomController.act()` process:
1. Iterates action JSON keys
2. Matches key to registered action in registry
3. Executes Playwright primitive

| Action Type | Playwright Operation |
|-------------|---------------------|
| **Navigation** | `page.goto()` |
| **Click** | Locate element by internal index → `element.click()` |
| **Input text** | `element.fill()` |
| **Extraction** | Fetch inner HTML or text; returns content to memory |
| **Upload** | Find `<input type="file">` via DOM index → `set_input_files()` |

#### Step 5: Post-Action Processing

After each action:
- **Screenshot captured** (base64) added to step history
- **ActionResult** includes:
  - `extracted_content`
  - `error` (if any)
  - `include_in_memory` flag
- **Memory summary updated** (LLM can compress long contexts)

#### Step 6: Iteration

Loop continues until:
- **Explicit DONE action** emitted: `{"done": {"text": "...", "success": true}}`
- **Failure repeated** (could escalate to `ask_for_assistant`)
- **Max steps/time budget** reached

#### Step 7: Finalization

On completion:
- **GIF assembled** from step screenshots
- **Agent history JSON** saved under `tmp/agent_history/<uuid>/`
- **WebUI shows:**
  - Task result
  - Memory summary
  - Screenshot progression

---

## 6. Element Handling & Robustness

### Mechanisms

#### DOM Indexing
- `browser_use` maps visible DOM elements to indices for stable referencing
- Actions target elements using numeric index, avoiding brittle CSS selectors in planning language
- Reduces selector fragility across dynamic pages

#### Locator Resolution
For file upload and interaction:
```
browser.get_dom_element_by_index(index) 
  → get structured DOM wrapper 
  → get_file_upload_element() or other locate functions 
  → underlying Playwright locator
```

#### Anti-Detection
Chrome launched with selective args:
- Remove automation flags that signal bot behavior
- Custom window position & size for realism
- Deterministic rendering timing

#### Fallback & Errors
- **Element not found:** `ActionResult(error="...")` returned
- LLM receives error text and re-plans next step
- **Upload file:** Path validation performed prior to action

#### Content Extraction
`ExtractPageContentAction` retrieves:
- Structured JSON
- Raw text for validation / memory enhancement

#### Memory Inclusion
Actions may set `include_in_memory=True` so extracted text appears in subsequent planning context, enabling:
- Context-aware decisions
- Multi-step reasoning
- Adaptive behavior

---

## 7. Data & Observability

### Collected Artifacts

| Artifact | Purpose | Location |
|----------|---------|----------|
| **Test Result JSON** | API test outcome | In-memory, displayed in UI |
| **Full API Response** | Debugging, evidence | Embedded in result JSON |
| **Agent History JSON** | Replay & audit | `tmp/agent_history/<uuid>/<uuid>.json` |
| **GIF Session Replay** | Visual narrative | Same folder as history JSON |
| **Screenshots (base64)** | Step-by-step state | Stored inside history JSON |
| **Logs (Python logging)** | Root cause analysis | Console / future file sink |
| **Gherkin Scenario Text** | Reproducible scenario representation | UI textbox / user editable |

### Observability Principles

- **Every meaningful action produces a structured record**
- **Human-reviewable evidence** (GIF + JSON) supports trust & reproducibility
- **Failures annotated** with error content for iterative AI correction
- **Transparent reasoning:** No black box AI decisions

### Artifact Cleanup

Runtime artifacts stored under `./tmp/` (git-ignored):
- `tmp/agent_history` (per-run JSON + GIF)
- `tmp/deep_research` (research tasks output)
- `tmp/downloads` (browser file downloads)

Safe to delete these between deployments to reduce storage footprint.

---

## 8. Error Handling & Recovery Strategy

### Error Categories & Handling

| Error Category | Handling Strategy |
|----------------|-------------------|
| **LLM Init Failure** | UI warns user to supply API key; agent proceeds with None for limited tasks |
| **Network/HTTP errors** | `requests.RequestException` → test result flagged with error status |
| **Element Not Found** | Action-level error → LLM receives context → may scroll/search/escalate |
| **Gherkin Parse Issues** | Missing `Feature:`/`Scenario:` triggers validation error; user corrects |
| **Browser Launch Conflict** | Remote debugging port conflict resolved by removing port arg dynamically |
| **Graceful Abort** | Repeated errors trigger `ask_for_assistant` action (future enhancement) |

### Recovery Patterns

1. **Retry with context:** Error message becomes input to next planning cycle
2. **Fallback actions:** Alternative selectors or navigation paths
3. **Human escalation:** `ask_for_assistant` bridges AI → human intervention
4. **Partial success capture:** Even failed runs preserve successful steps

---

## 9. Extensibility Points

### Extension Mechanisms

| Extension Point | How to Extend |
|----------------|---------------|
| **New Actions** | Add decorator to `CustomController._register_custom_actions()` |
| **MCP Tools** | Start MCP client → dynamic registration of external server tools |
| **API Assertions** | Enhance `execute_gherkin_scenario()` with schema validator (e.g., `jsonschema`) |
| **Bulk Test Generation** | Add OpenAPI importer → map endpoints → generate multi-scenario Gherkin |
| **CI Integration** | Serialize test results, add CLI runner for regression batch |
| **Visual Validation** | Extend BrowserUseAgent for DOM diffs / screenshot comparisons |
| **Auth Flows** | Augment Gherkin parser for tokens, sessions, reuse cookies across contexts |

### Adding a Custom Action Example

```python
# In CustomController
@register_action("scroll_to_bottom")
async def scroll_to_bottom_action(page: Page) -> ActionResult:
    """Scroll to bottom of page"""
    try:
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        return ActionResult(
            extracted_content="Scrolled to bottom",
            include_in_memory=False
        )
    except Exception as e:
        return ActionResult(error=str(e))
```

Update LLM prompt template to advertise new action type, and it becomes available automatically.

---

## 10. End-to-End Example Walkthrough

### Scenario
"Validate users API and confirm UI shows user 'Leanne Graham'."

### Step-by-Step Execution

#### Phase 1: API Validation

1. User enters API description → **Gherkin generated**
2. Click **Execute** → Response JSON captured (contains user list)
3. Result shows:
   ```json
   {
     "status": "passed",
     "contains_Leanne_Graham": true,
     "full_response": [...]
   }
   ```

#### Phase 2: UI Validation

4. User copies summary or reuses scenario in **BrowserUse tab**
5. **BrowserUse Agent plan:**
   - **Step 1:** Navigate to application URL
   - **Step 2:** Extract content from users list
   - **Step 3:** Confirm "Leanne Graham" present in DOM
   - **Done:** Success condition met

#### Phase 3: Consolidated Artifacts

6. **Collected artifacts:**
   - API Test JSON Result
   - Browser GIF & History JSON
   - Combined narrative for presentation

**Value:** Single workflow validates data layer (API) and presentation layer (UI) with full traceability.

---

## 11. Architecture Diagrams

### API Testing Flow

```
User Prompt
   │
   ▼
APITestingAgent.generate_gherkin_from_prompt()
   │  (LLM transforms intent → structured scenario)
   ▼
Gherkin Text (Feature/Scenario/Given/When/Then)
   │
   ▼
execute_gherkin_scenario()
   │  Parse URL/method/status/assertions
   │  Perform HTTP request
   │  Validate + assemble full_response
   ▼
Result JSON (test_status, full_response, extracted_values, timing)
```

### Browser Autonomy Flow

```
User Task / Scenario
   │
   ▼
LLM Planning Loop
   │  (Goal reasoning, memory summarization)
   ▼
Structured Action JSON
   │
   ▼
CustomController.act()
   │  (Lookup registered actions)
   ▼
Playwright Execution (navigation/input/extract/upload)
   │
   ├─ Screenshot capture
   ├─ ActionResult with extracted content
   └─ Update memory/context
   │
   └─ Repeat until DONE or failure
   ▼
Artifacts (GIF, history JSON, logs)
```

### Component Interaction Overview

```
┌─────────────────────────────────────────────────────────┐
│                      WebUI (Gradio)                     │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐   │
│  │ Agent Settings│ │Browser Settings│ │Domain Tabs  │   │
│  └──────┬───────┘ └──────┬───────┘ └──────┬───────┘   │
│         │                 │                 │           │
└─────────┼─────────────────┼─────────────────┼───────────┘
          │                 │                 │
          ▼                 ▼                 ▼
   ┌──────────────────────────────────────────────┐
   │         Phoenix Coordination Layer          │
   │  ┌────────────┐ ┌────────────┐ ┌──────────┐│
   │  │ LLM Provider│ │ BrowserConfig│ │Agent Mgr││
   │  └────────────┘ └────────────┘ └──────────┘│
   └──────────────────────────────────────────────┘
          │                 │                 │
          ▼                 ▼                 ▼
   ┌──────────────────────────────────────────────┐
   │            Domain Agents                     │
   │  ┌──────────┐ ┌──────────┐ ┌─────────────┐ │
   │  │PR Testing│ │API Testing│ │Browser Use  │ │
   │  └──────────┘ └──────────┘ └─────────────┘ │
   └──────────────────────────────────────────────┘
          │                 │                 │
          ▼                 ▼                 ▼
   ┌──────────────────────────────────────────────┐
   │         Core Execution Engines               │
   │  ┌──────────────┐ ┌──────────────────────┐  │
   │  │CustomBrowser│ │CustomController       │  │
   │  │(Playwright)  │ │(Action Registry)     │  │
   │  └──────────────┘ └──────────────────────┘  │
   └──────────────────────────────────────────────┘
          │                               │
          ▼                               ▼
   ┌──────────────────────────────────────────────┐
   │            Artifacts & Persistence           │
   │  JSON Results │ GIF Replay │ Screenshots     │
   └──────────────────────────────────────────────┘
```

---

## 12. Key Design Principles

Phoenix AI architecture follows these core principles:

1. **Declarative Prompts → Deterministic Structured Outputs**
   - Users describe intent, not implementation
   - System produces consistent, parseable results

2. **Separation of Concerns**
   - Agent orchestration separated from execution engines
   - Domain logic isolated from infrastructure

3. **Resilience & Transparency**
   - Artifacts generated before sophistication
   - Every action recorded for audit

4. **Extensibility over Monolithic Complexity**
   - Registry patterns enable dynamic capability addition
   - No core rewrites required for new features

5. **Minimal Configuration Friction**
   - Derive execution details from Gherkin
   - Central settings shared across all agents

6. **Human-in-the-Loop Ready**
   - Escalation mechanisms for ambiguous situations
   - Clear artifact presentation for validation

---

## 13. Future Roadmap

### Planned Enhancements

| Feature | Target | Description |
|---------|--------|-------------|
| **Schema Validation** | Q1 2026 | JSON Schema enforcement for API responses |
| **OpenAPI Import** | Q1 2026 | Bulk Gherkin generation from API specifications |
| **Performance Budgets** | Q2 2026 | Response time thresholds & alerts |
| **Flakiness Tracking** | Q2 2026 | Stability scoring for test reliability |
| **CI/CD Integration** | Q2 2026 | Export test results for pipeline gating |
| **Visual Regression** | Q3 2026 | Screenshot comparison & DOM diff analysis |
| **Knowledge Graph** | Q4 2026 | Link code changes to documentation automatically |
| **Multi-Language Support** | 2027 | Extend beyond Python to Java, TypeScript agents |

### Community Contributions Welcome

Areas seeking contributions:
- Additional LLM provider integrations
- Browser action library expansion
- Assertion library for complex validations
- Test result visualization dashboards

---

## Appendix A: Glossary

| Term | Definition |
|------|------------|
| **Gherkin** | Structured test description format using Given/When/Then syntax |
| **LLM** | Large Language Model (AI reasoning engine, e.g., GPT-4, Claude) |
| **Endpoint** | API URL for HTTP operations |
| **Action** | Single browser operation (Click, Navigate, Extract, etc.) |
| **Artifact** | Saved evidence file (JSON result, GIF replay, screenshot) |
| **DOM Index** | Numeric reference to page elements for stable targeting |
| **ActionResult** | Structured return object from executed actions |
| **CustomController** | Action registry and dispatcher for browser operations |
| **CustomBrowser** | Playwright wrapper with anti-detection and configuration |
| **MCP** | Model Context Protocol - external tool integration standard |
| **Agent** | Autonomous workflow orchestrator (PR/API/Browser) |
| **Memory** | Context carried across action steps for reasoning continuity |

---

## Appendix B: Configuration Reference

### LLM Settings

| Setting | Purpose | Example Values |
|---------|---------|----------------|
| **LLM Provider** | AI service selection | `openai`, `anthropic`, `google`, `ollama`, `azure` |
| **Model Name** | Specific model version | `gpt-4o`, `claude-3-5-sonnet`, `gemini-2.0-flash` |
| **API Key** | Authentication credential | `sk-...` (OpenAI), `sk-ant-...` (Anthropic) |
| **Base URL** | Custom endpoint (optional) | `https://api.custom.com/v1` |
| **Temperature** | Response randomness | `0.0` (deterministic) to `1.0` (creative) |

### Browser Settings

| Setting | Purpose | Example Values |
|---------|---------|----------------|
| **Headless** | Browser visibility | `true` (hidden), `false` (visible) |
| **Viewport** | Window dimensions | `1280x1100`, `1920x1080` |
| **User Data Dir** | Browser profile path | `C:/Users/.../Chrome/User Data` |
| **CDP URL** | Remote debugging endpoint | `http://localhost:9222` |
| **Recording Path** | Video capture location | `./tmp/recordings` |
| **Download Path** | File download destination | `./tmp/downloads` |

### Environment Variables

| Variable | Purpose | Default |
|----------|---------|---------|
| `LOG_LEVEL` | Logging verbosity | `INFO` |
| `OPENAI_API_KEY` | OpenAI authentication | (none) |
| `ANTHROPIC_API_KEY` | Anthropic authentication | (none) |
| `AZURE_DEVOPS_ORG` | PR analysis integration | (none) |
| `VNC_PASSWORD` | noVNC access control | `youvncpassword` |

---

## Document Maintenance

**Last Updated:** November 21, 2025  
**Maintainers:** Phoenix AI Team  
**Feedback:** Open issues on GitHub repository

For questions or clarifications, refer to:
- `README.md` - Quick start & installation
- `docs/TEAM_ONBOARDING_GUIDE.md` - Non-technical overview
- `docs/API_TESTING.md` - API testing deep dive
- `docs/PR_TESTING_TOOL.md` - PR analysis guide

---

**End of Document**
