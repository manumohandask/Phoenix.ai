# Changelog - API Testing Module

## [Version 2.0.0] - 2025-11-20

### 🎉 Major Feature: API Testing with Gherkin Generator

#### Added

##### New Module: API Testing Agent
- **Gherkin Scenario Generation**: AI-powered generation of BDD scenarios from natural language prompts
- **Comprehensive API Testing**: Full support for REST API testing with GET, POST, PUT, PATCH, DELETE methods
- **Value Extraction**: Extract values from API responses using JSONPath expressions
- **UI Validation**: Validate extracted API values in web UI for end-to-end consistency
- **Multiple Authentication Methods**: Support for Bearer Token, Basic Auth, and custom headers
- **AI-Powered Validation**: Intelligent response validation using LLM
- **Detailed Reporting**: Comprehensive test reports with execution metrics

##### Files Added
- `src/agent/api_testing/api_testing_agent.py` - Core API testing agent
- `src/agent/api_testing/__init__.py` - Module initialization
- `src/agent/api_testing/schemas.py` - Data models and enums
- `src/webui/components/api_testing_agent_tab.py` - UI component
- `examples/api_testing_examples.py` - Example scripts
- `docs/API_TESTING_MODULE_SUMMARY.md` - Implementation summary
- `docs/API_TESTING_QUICKSTART.md` - Quick start guide

##### Dependencies Added
- `requests>=2.31.0` - HTTP client for API requests
- `jsonpath-ng>=1.6.0` - JSONPath expression parsing
- `pytest-bdd>=7.0.0` - BDD/Gherkin support

#### Changed

##### Interface Updates
- Replaced "🧪 Testing Suite" tab with "🔌 API Testing" tab
- Moved "Deep Research" to standalone top-level tab
- Improved tab organization and navigation
- Updated interface imports to include API testing component

##### Documentation Updates
- **docs/API_TESTING.md**: Complete rewrite with:
  - Gherkin generator documentation
  - JSONPath expression guide
  - Three detailed workflow examples
  - Step-by-step configuration guide
  - Troubleshooting section
  - CI/CD integration examples
  - Best practices guide

- **README.md**: Updated to highlight:
  - Gherkin scenario generation
  - Value extraction capabilities
  - UI validation features

#### Features in Detail

##### 1. Gherkin Generator
```
Input: "Test user login API and verify profile page"
Output: 
  Feature: User Authentication
  Scenario: Successful login
    Given the API endpoint is available
    When I send login credentials
    Then I receive authentication token
    And profile page displays user name
```

##### 2. API Testing
- Configure base URL, endpoint, method
- Add headers, query params, request body
- Set authentication (Bearer, Basic)
- Define expected status code
- Validate response schema
- Extract values using JSONPath

##### 3. Value Extraction
```json
{
  "userId": "data.user.id",
  "userName": "data.user.name",
  "userEmail": "data.user.email"
}
```

##### 4. UI Validation
- Navigate to specified URL
- Replace placeholders with extracted values
- Validate elements contain expected data
- Report validation success/failure

##### 5. Reporting
- Execution time tracking
- Success/failure status
- API response details
- Extracted values display
- UI validation results
- Comprehensive error logging

#### Architecture

```
Phoenix AI
├── API Testing Module
│   ├── GherkinGenerator (LLM-powered)
│   ├── APIValidator (HTTP client)
│   ├── UIValidator (Browser automation)
│   └── TestResult (Reporter)
├── Web UI
│   ├── Step 1: Generate Gherkin
│   ├── Step 2: Configure API
│   ├── Step 3: Setup UI Validation (Optional)
│   └── Step 4: Execute & Report
└── Examples & Docs
```

#### Testing Workflow

1. **Generate**: Describe test in natural language
2. **Review**: Edit generated Gherkin scenario
3. **Configure**: Set API endpoint and parameters
4. **Extract**: Define JSONPath for value extraction
5. **Validate**: Optionally validate in UI
6. **Execute**: Run test with real-time feedback
7. **Report**: View detailed results and metrics

#### Use Cases

1. **API Regression Testing**: Ensure APIs maintain contracts
2. **End-to-End Validation**: Verify API data appears correctly in UI
3. **Authentication Flows**: Test login, token refresh, logout
4. **Data Consistency**: Validate API responses match UI displays
5. **Integration Testing**: Test multi-step API workflows
6. **CI/CD Integration**: Automated API testing in pipelines

#### Known Limitations

1. OAuth 2.0 flow not yet implemented (coming soon)
2. GraphQL support not included (future enhancement)
3. Load testing limited to sequential execution
4. WebSocket testing not supported yet

#### Future Enhancements

- [ ] OpenAPI/Swagger import for auto-test generation
- [ ] Load testing with concurrent requests
- [ ] Mock server for API simulation
- [ ] Data-driven testing with CSV/JSON
- [ ] Contract testing with schema evolution
- [ ] Performance monitoring with trends
- [ ] GraphQL query/mutation support
- [ ] WebSocket connection testing

#### Migration Notes

**If you were using "Testing Suite":**

The "Testing Suite" tab has been replaced with dedicated tabs:
- "🔌 API Testing" - New comprehensive API testing
- "🔬 Deep Research" - Moved to top-level tab

All existing Deep Research functionality remains unchanged.

#### Examples

##### Example 1: Simple GET Request
```python
agent = APITestingAgent(llm_provider="openai", ...)
gherkin = await agent.generate_gherkin_from_prompt(
    "Get user details from /users/1"
)
result = await agent.parse_and_execute_gherkin(gherkin, api_config)
```

##### Example 2: POST with UI Validation
```python
api_config = APITestConfig(
    base_url="https://api.example.com",
    endpoint="/auth/login",
    method="POST",
    body={"email": "test@test.com", "password": "pass"},
    extract_values={"userName": "data.user.name"}
)

ui_validation = UIValidationConfig(
    url="https://app.example.com/dashboard",
    validation_steps=["Verify {userName} is displayed"],
    expected_values={"userName": "should be visible"}
)

result = await agent.parse_and_execute_gherkin(
    gherkin, api_config, ui_validation
)
```

#### Credits

- Built on browser-use for UI automation
- Leverages LangChain for LLM integration
- Uses requests for HTTP client
- JSONPath implementation via jsonpath-ng

#### Breaking Changes

None. This is a new feature addition that replaces UI organization only.

#### Upgrade Instructions

1. Pull latest code
2. Install new dependencies: `pip install -r requirements.txt`
3. Restart Phoenix AI
4. Navigate to "🔌 API Testing" tab
5. Start testing!

---

For detailed documentation, see:
- [API Testing Guide](docs/API_TESTING.md)
- [Quick Start Guide](docs/API_TESTING_QUICKSTART.md)
- [Implementation Summary](docs/API_TESTING_MODULE_SUMMARY.md)

**Built with ❤️ by the Phoenix AI team**
