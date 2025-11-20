# 🔥 Phoenix AI - Intelligent E2E Testing & Automation Platform

<div align="center">

[![License](https://img.shields.io/badge/License-MIT-orange.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![AI Powered](https://img.shields.io/badge/AI-Powered-ff6b35.svg)](https://github.com/manumohandask/Phoenix.ai)

**Phoenix AI** is an advanced AI-powered end-to-end testing and automation platform that revolutionizes software quality assurance through intelligent automation.

</div>

## 🚀 What is Phoenix AI?

Phoenix AI is a next-generation testing platform that combines the power of AI with comprehensive testing capabilities. Unlike traditional testing tools, Phoenix AI understands your application context and autonomously performs complex testing scenarios.

### 🎯 Core Capabilities

**🔍 PR Testing & Code Review**
- Automated pull request validation and testing
- Intelligent code change analysis
- Integration with Azure DevOps and GitHub
- Automated regression testing on code changes
- Smart test case generation based on PR content

**🔌 API Integration Testing**
- Comprehensive REST API testing
- Automated API endpoint discovery and validation
- Request/response validation with AI-powered assertions
- Load testing and performance monitoring
- Integration with OpenAPI/Swagger specifications

**🌐 E2E Browser Automation**
- Intelligent web application testing
- Cross-browser compatibility testing
- Visual regression detection
- Session persistence for complex workflows
- Custom browser integration with existing profiles

**🤖 AI-Powered Intelligence**
- Support for multiple LLMs: OpenAI (GPT-4, GPT-4o), Google (Gemini), Anthropic (Claude), Azure OpenAI, DeepSeek, Ollama, and more
- Context-aware test execution
- Self-healing test scripts that adapt to UI changes
- Natural language test case definition
- Intelligent error detection and reporting

**📊 Advanced Features**
- Real-time test execution monitoring
- Comprehensive test reports with screenshots and videos
- Integration with CI/CD pipelines
- Parallel test execution
- Custom test data generation
- Memory-enhanced agents for complex scenarios

## 🎨 Why Phoenix AI?

- **Intelligent Automation**: AI understands your application and writes tests for you
- **Comprehensive Coverage**: From UI to API to PR validation - all in one platform
- **Developer-Friendly**: Natural language test definitions, no complex scripting
- **Enterprise-Ready**: Integrates with Azure DevOps, GitHub, and major CI/CD tools
- **Cost-Effective**: Reduce manual testing time by up to 80%
- **Scalable**: Run tests in parallel across multiple environments

---

**Built on the foundation of browser-use and enhanced with enterprise-grade testing capabilities.**

## 📦 Installation Guide

### Option 1: Local Installation

#### Step 1: Clone the Repository
```bash
git clone https://github.com/manumohandask/Phoenix.ai.git
cd Phoenix.ai
```

#### Step 2: Set Up Python Environment
We recommend using Python 3.11 or higher. You can use [uv](https://docs.astral.sh/uv/) or standard virtual environments.

Using venv:
```bash
python -m venv .venv
```

Using uv (recommended):
```bash
uv venv --python 3.11
```

Activate the virtual environment:
- Windows (Command Prompt):
```cmd
.venv\Scripts\activate
```
- Windows (PowerShell):
```powershell
.\.venv\Scripts\Activate.ps1
```
- macOS/Linux:
```bash
source .venv/bin/activate
```

#### Step 3: Install Dependencies
Install Python packages:
```bash
uv pip install -r requirements.txt
```

Install Browsers in playwright. 
```bash
playwright install --with-deps
```
Or you can install specific browsers by running:
```bash
playwright install chromium --with-deps
```

#### Step 4: Configure Environment
1. Create a copy of the example environment file:
- Windows (Command Prompt):
```bash
copy .env.example .env
```
- macOS/Linux/Windows (PowerShell):
```bash
cp .env.example .env
```
2. Open `.env` in your preferred text editor and add your API keys and other settings

#### Step 5: Launch Phoenix AI
1.  **Run Phoenix AI:**
    ```bash
    python webui.py --ip 127.0.0.1 --port 7788
    ```
2. **Access the Platform:** Open your web browser and navigate to `http://127.0.0.1:7788`.

3. **Configure for PR Testing (Optional):**
   - Set up Azure DevOps credentials in `.env` file
   - Configure your organization and project details
   - See [Azure DevOps Setup Guide](docs/AZURE_DEVOPS_SETUP.md) for detailed instructions

4. **Configure for API Testing (Optional):**
   - Add your API endpoints in the API Testing tab
   - Configure authentication tokens and headers
   - Import OpenAPI/Swagger specifications

5. **Using Your Own Browser (Optional):**
    - Set `BROWSER_PATH` to the executable path of your browser and `BROWSER_USER_DATA` to the user data directory of your browser. Leave `BROWSER_USER_DATA` empty if you want to use local user data.
      - Windows
        ```env
         BROWSER_PATH="C:\Program Files\Google\Chrome\Application\chrome.exe"
         BROWSER_USER_DATA="C:\Users\YourUsername\AppData\Local\Google\Chrome\User Data"
        ```
        > Note: Replace `YourUsername` with your actual Windows username for Windows systems.
      - Mac
        ```env
         BROWSER_PATH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
         BROWSER_USER_DATA="/Users/YourUsername/Library/Application Support/Google/Chrome"
        ```
    - Close all Chrome windows
    - Open Phoenix AI in a non-Chrome browser, such as Firefox or Edge. This is important because the persistent browser context will use the Chrome data when running the agent.
    - Check the "Use Own Browser" option within the Browser Settings.

### Option 2: Docker Installation

#### Prerequisites
- Docker and Docker Compose installed
  - [Docker Desktop](https://www.docker.com/products/docker-desktop/) (For Windows/macOS)
  - [Docker Engine](https://docs.docker.com/engine/install/) and [Docker Compose](https://docs.docker.com/compose/install/) (For Linux)

#### Step 1: Clone the Repository
```bash
git clone https://github.com/manumohandask/Phoenix.ai.git
cd Phoenix.ai
```

#### Step 2: Configure Environment
1. Create a copy of the example environment file:
- Windows (Command Prompt):
```bash
copy .env.example .env
```
- macOS/Linux/Windows (PowerShell):
```bash
cp .env.example .env
```
2. Open `.env` in your preferred text editor and add your API keys and other settings

#### Step 3: Docker Build and Run
```bash
docker compose up --build
```
For ARM64 systems (e.g., Apple Silicon Macs), please run follow command:
```bash
TARGETPLATFORM=linux/arm64 docker compose up --build
```

#### Step 4: Access Phoenix AI
- Phoenix AI Platform: Open `http://localhost:7788` in your browser
- VNC Viewer (for watching browser interactions): Open `http://localhost:6080/vnc.html`
  - Default VNC password: "youvncpassword"
  - Can be changed by setting `VNC_PASSWORD` in your `.env` file

## 📚 Feature Documentation

- **[PR Testing Guide](docs/PR_TESTING_TOOL.md)** - Learn how to automate pull request testing with Azure DevOps integration
- **[API Testing Guide](docs/API_TESTING.md)** - Comprehensive guide to API integration testing
- **[Azure DevOps Setup](docs/AZURE_DEVOPS_SETUP.md)** - Configure Azure DevOps for PR automation
- **[Quick Start Guide](docs/QUICK_START_HRB.md)** - Get started with Phoenix AI in minutes

## 🎯 Use Cases

### PR Testing & Validation
Automatically test pull requests before merging. Phoenix AI analyzes code changes, generates relevant test cases, and validates functionality.

### API Integration Testing
Test your REST APIs with intelligent assertions. Phoenix AI understands your API structure and validates responses automatically.

### E2E Web Testing
Create comprehensive end-to-end tests using natural language. Phoenix AI navigates your application like a human tester.

### Regression Testing
Catch bugs before they reach production. Phoenix AI maintains test suites that adapt to your application changes.

## 🛠️ Technology Stack

- **AI Models**: OpenAI GPT-4, Google Gemini, Anthropic Claude, Azure OpenAI, DeepSeek, Ollama
- **Web Automation**: Playwright, Selenium WebDriver
- **UI Framework**: Gradio
- **API Testing**: httpx, requests
- **Integration**: Azure DevOps API, GitHub API
- **Language**: Python 3.11+

## 📊 Roadmap

- [x] **2025/01:** PR Testing with Azure DevOps integration
- [x] **2025/01:** API Testing module with OpenAPI support
- [x] **2025/01:** Enhanced E2E browser automation
- [ ] **2025/02:** GitHub Actions integration
- [ ] **2025/02:** Advanced visual regression testing
- [ ] **2025/03:** Mobile app testing (iOS/Android)
- [ ] **2025/03:** Performance testing and monitoring
- [ ] **2025/04:** AI-powered test case generation
- [ ] **2025/04:** Team collaboration features

## 🤝 Contributing

We welcome contributions! Phoenix AI is built to be extensible and community-driven.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

Phoenix AI builds upon the excellent foundation of [browser-use](https://github.com/browser-use/browser-use) and extends it with enterprise testing capabilities. We thank the browser-use team and all contributors.

---

<div align="center">

**Made with ❤️ by the Phoenix AI Team**

[Report Bug](https://github.com/manumohandask/Phoenix.ai/issues) · [Request Feature](https://github.com/manumohandask/Phoenix.ai/issues) · [Documentation](docs/)

</div>
