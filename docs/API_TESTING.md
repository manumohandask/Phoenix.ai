# 🔌 API Testing with Gherkin Generator - Phoenix AI

Phoenix AI provides comprehensive API integration testing capabilities powered by AI with Gherkin BDD scenario generation. This guide will help you leverage Phoenix AI for automated API testing with natural language test definitions.

## Overview

Phoenix AI can automatically:
- **Generate Gherkin scenarios** from natural language prompts
- Discover and test API endpoints with intelligent validation
- **Extract values from API responses** for cross-validation
- **Validate API data in UI** to ensure end-to-end consistency
- Generate intelligent test cases based on OpenAPI/Swagger specifications
- Validate request/response patterns with AI-powered assertions
- Perform load testing and performance monitoring
- Generate detailed API test reports with execution history

## 🚀 Getting Started

### 1. Gherkin Scenario Generation

Phoenix AI's most powerful feature - generate BDD scenarios from natural language:

**Step 1: Describe Your Test in Natural Language**
```
I want to test the user login API. 
When a user logs in with valid credentials, 
the API should return a JWT token and user details. 
Then I want to verify the user's name appears correctly on the profile page.
```

**Step 2: Phoenix AI Generates Gherkin**
```gherkin
Feature: User Authentication
Scenario: Successful login with valid credentials
  Given the API endpoint "/api/auth/login" is available
  And I have valid user credentials
  When I send a POST request with username and password
  Then the response status code should be 200
  And the response should contain a JWT token
  And the response should contain user details
  And I can verify the user name on the profile page
```

**Step 3: Configure and Execute**
- Set up API endpoint details
- Configure authentication
- Define response extraction (get userId, userName from response)
- Enable UI validation to check the extracted values
- Run the test and get detailed results

### 2. API Testing with Value Extraction

Extract values from API responses and use them in subsequent validations:

```json
{
  "extract_values": {
    "userId": "data.user.id",
    "userName": "data.user.name",
    "userEmail": "data.user.email"
  }
}
```

These values can then be validated in the UI or used in subsequent API calls.

### 3. UI Validation After API Calls

After extracting values from API, validate them in the UI:

```
Validation Steps:
- Navigate to profile page at https://app.example.com/profile
- Check that the user name {userName} is displayed in the header
- Verify user email {userEmail} appears in the profile section
- Confirm user ID {userId} is present in the URL
```

Phoenix AI's browser agent will automatically:
1. Navigate to the specified URL
2. Replace placeholders with extracted API values
3. Validate each element on the page
4. Report success/failure with detailed logs

### 4. Authentication Testing

Phoenix AI supports various authentication methods:

- **Bearer Tokens**: JWT and access token validation
- **Basic Auth**: Username/password authentication
- **API Keys**: Header or query parameter based
- **OAuth 2.0**: Full OAuth flow testing (coming soon)

## Features

### Intelligent Test Generation

Phoenix AI analyzes your API structure and generates:
- Happy path test cases
- Edge case scenarios
- Error handling tests
- Data validation tests
- Security tests

### Response Validation

Automatic validation of:
- Status codes
- Response headers
- JSON/XML schema
- Data types
- Required fields
- Business logic rules

### Performance Testing

Monitor API performance:
- Response time tracking
- Throughput measurement
- Concurrent request handling
- Rate limiting validation

### Integration Testing

Test complex workflows:
- Multi-step API sequences
- Data dependencies between requests
- State management
- Transaction flows

## 📋 Example Workflows

### Example 1: User Login with UI Validation

**Natural Language Prompt:**
```
Test user login API at /api/auth/login. 
Post username and password, expect 200 status with JWT token. 
Extract the user's name and ID from response. 
Then verify the name appears on the dashboard page.
```

**Configuration:**
```json
{
  "base_url": "https://api.example.com",
  "endpoint": "/api/auth/login",
  "method": "POST",
  "body": {
    "username": "testuser@example.com",
    "password": "SecurePass123"
  },
  "expected_status": 200,
  "extract_values": {
    "userName": "data.user.name",
    "userId": "data.user.id",
    "token": "data.token"
  }
}
```

**UI Validation:**
```
URL: https://app.example.com/dashboard
Steps:
- Verify {userName} is displayed in the welcome message
- Check user profile link contains {userId}
```

### Example 2: E-commerce Order Creation

**Natural Language Prompt:**
```
Test the order creation API. 
Create a new order with product details, 
get the order ID from response, 
then verify the order appears in the orders page with correct details.
```

**Configuration:**
```json
{
  "base_url": "https://api.shop.example.com",
  "endpoint": "/api/orders",
  "method": "POST",
  "headers": {
    "Authorization": "Bearer YOUR_TOKEN",
    "Content-Type": "application/json"
  },
  "body": {
    "productId": "PROD-123",
    "quantity": 2,
    "shippingAddress": "123 Main St"
  },
  "expected_status": 201,
  "extract_values": {
    "orderId": "data.order.id",
    "orderTotal": "data.order.total",
    "orderStatus": "data.order.status"
  }
}
```

**UI Validation:**
```
URL: https://shop.example.com/orders
Steps:
- Search for order {orderId}
- Verify order status shows {orderStatus}
- Check order total matches {orderTotal}
```

### Example 3: User Profile Update

**Natural Language Prompt:**
```
Update user profile via API, 
then verify the updated information is correctly displayed on the profile page.
```

**Configuration:**
```json
{
  "base_url": "https://api.example.com",
  "endpoint": "/api/users/profile",
  "method": "PATCH",
  "headers": {
    "Authorization": "Bearer YOUR_TOKEN"
  },
  "body": {
    "name": "John Updated",
    "bio": "New bio text"
  },
  "expected_status": 200,
  "extract_values": {
    "updatedName": "data.name",
    "updatedBio": "data.bio"
  }
}
```

**UI Validation:**
```
URL: https://app.example.com/profile
Steps:
- Verify profile name shows {updatedName}
- Check bio section contains {updatedBio}
```

## ⚙️ Configuration

### Setting Up API Tests in Phoenix AI

**Step-by-Step Guide:**

1. **Launch Phoenix AI**
   ```bash
   python phoenix.py
   ```

2. **Navigate to API Testing Tab**
   - Click on "🔌 API Testing" in the main interface

3. **Generate Gherkin Scenario**
   - Enter your test description in natural language
   - Click "🤖 Generate Gherkin Scenario"
   - Review and edit the generated Gherkin if needed

4. **Configure API Details**
   - **Base URL**: Your API's base URL (e.g., https://api.example.com)
   - **Endpoint**: The specific endpoint path (e.g., /api/users)
   - **HTTP Method**: GET, POST, PUT, PATCH, or DELETE
   - **Expected Status**: Expected HTTP status code (default: 200)

5. **Add Headers** (Optional)
   ```json
   {
     "Content-Type": "application/json",
     "X-Custom-Header": "value"
   }
   ```

6. **Configure Authentication**
   - Select authentication type: None, Bearer Token, or Basic Auth
   - Enter credentials as required

7. **Set Up Response Validation**
   - Define expected response schema
   - Configure value extraction with JSONPath expressions:
   ```json
   {
     "userId": "data.user.id",
     "userName": "data.user.name",
     "email": "data.user.email"
   }
   ```

8. **Enable UI Validation** (Optional)
   - Check "Enable UI Validation"
   - Enter the UI URL to validate
   - Define validation steps using `{variableName}` placeholders
   - Specify expected values

9. **Execute Test**
   - Click "🚀 Run API Test"
   - Monitor execution in real-time
   - Review detailed results

10. **Save and Report**
    - Save results to JSON file
    - Generate formatted test report

### JSONPath Expression Guide

Extract values from API responses using JSONPath:

| Expression | Description | Example |
|------------|-------------|---------|
| `data.user.id` | Nested object access | `{"data": {"user": {"id": 123}}}` |
| `users[0].name` | Array access | `{"users": [{"name": "John"}]}` |
| `items[0].price` | First array element | `{"items": [{"price": 29.99}]}` |
| `response.token` | Direct property | `{"response": {"token": "abc123"}}` |

### Environment Variables

Add to your `.env` file for easy configuration:

```env
# API Testing Configuration
API_BASE_URL=https://api.example.com
API_AUTH_TOKEN=your-token-here
API_TIMEOUT=30

# LLM Configuration for Gherkin Generation
LLM_PROVIDER=openai
MODEL_NAME=gpt-4
API_KEY=your-api-key

# UI Testing (if needed)
UI_BASE_URL=https://app.example.com
BROWSER_HEADLESS=false
```

## 🎯 Key Features

### 1. Gherkin Scenario Generation
Generate BDD scenarios from natural language descriptions using AI:
- Automatic Given-When-Then structure
- Context-aware scenario creation
- Support for complex multi-step workflows
- Editable generated scenarios

### 2. API Response Validation
Intelligent validation powered by AI:
- Status code verification
- Response schema validation
- Custom validation rules
- AI-powered semantic validation

### 3. Value Extraction
Extract data from API responses using JSONPath:
- Nested object access
- Array element extraction
- Multiple value extraction
- Type-safe extraction

### 4. Cross-Platform Validation
Validate API data in the UI:
- Extract values from API responses
- Navigate to specified UI pages
- Verify extracted values appear correctly
- End-to-end consistency validation

### 5. Comprehensive Reporting
Detailed test execution reports:
- Execution time tracking
- Success/failure status
- Extracted values display
- Error logs with context
- API response details
- UI validation results

### 6. Multiple Authentication Methods
Flexible authentication support:
- Bearer Token authentication
- Basic HTTP authentication
- Custom header authentication
- Future: OAuth 2.0 support

## 💡 Best Practices

### 1. Write Clear Natural Language Prompts

**Good Examples:**
```
✅ Test user login API with valid credentials, extract the user ID and token, 
   then verify the user's profile page displays the correct name
   
✅ Create a new order via API, get the order ID, 
   and validate it appears in the orders list with correct status
```

**Avoid:**
```
❌ Test login
❌ Check API
```

### 2. Use Meaningful JSONPath Expressions

**Clear and Maintainable:**
```json
{
  "userId": "data.user.id",
  "userName": "data.user.fullName",
  "userEmail": "data.user.email"
}
```

**Avoid:**
```json
{
  "val1": "data[0]",
  "val2": "data[1]"
}
```

### 3. Test Both Success and Failure Paths

Include in your Gherkin scenarios:
- ✅ Happy path scenarios (valid inputs)
- ✅ Error handling tests (invalid inputs)
- ✅ Edge cases (boundary values)
- ✅ Authentication failures
- ✅ Rate limiting scenarios

### 4. Validate Response Thoroughly

Always verify:
- ✅ Status codes (200, 201, 400, 401, etc.)
- ✅ Response structure (schema validation)
- ✅ Data types (string, number, boolean)
- ✅ Required fields presence
- ✅ Business logic rules
- ✅ Error messages format

### 5. Use UI Validation Wisely

Enable UI validation when:
- ✅ You need end-to-end verification
- ✅ Data must be visible to users
- ✅ Testing critical user flows
- ✅ Verifying data consistency

Skip UI validation when:
- ❌ Testing internal APIs only
- ❌ Performance testing (adds overhead)
- ❌ No UI representation exists

### 6. Organize Test Scenarios

Structure your tests logically:
```
Feature: User Management
  Scenario: User Registration
  Scenario: User Login
  Scenario: User Profile Update
  Scenario: User Deletion

Feature: Order Management
  Scenario: Create Order
  Scenario: View Order
  Scenario: Cancel Order
```

### 7. Use Environment-Specific Configurations

Maintain separate configurations:
- 🔵 Development: Local/dev APIs
- 🟡 QA/Staging: Test environment
- 🔴 Production: Live APIs (read-only tests)

### 8. Monitor and Track Results

Keep track of:
- 📊 Execution time trends
- 📈 Success/failure rates
- 🐛 Common error patterns
- ⚡ API performance metrics

## Reporting

Phoenix AI generates comprehensive reports including:
- Test execution summary
- Pass/fail status for each test
- Response times and performance metrics
- Detailed error logs
- API coverage statistics
- Trend analysis

## 🔗 Integration with CI/CD

Phoenix AI API tests can be integrated into your CI/CD pipeline:

### GitHub Actions Example

```yaml
name: API Tests
on: [push, pull_request]

jobs:
  api-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      
      - name: Run Phoenix AI API Tests
        env:
          API_KEY: ${{ secrets.API_KEY }}
          LLM_API_KEY: ${{ secrets.LLM_API_KEY }}
        run: |
          python -c "from src.agent.api_testing import APITestingAgent; 
                     import asyncio;
                     # Your test execution code here"
      
      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v2
        with:
          name: api-test-results
          path: tmp/api_test_results_*.json
```

### Azure DevOps Pipeline Example

```yaml
trigger:
  - main
  - develop

pool:
  vmImage: 'ubuntu-latest'

steps:
- task: UsePythonVersion@0
  inputs:
    versionSpec: '3.11'
  
- script: |
    pip install -r requirements.txt
  displayName: 'Install dependencies'

- script: |
    python run_api_tests.py
  displayName: 'Run Phoenix AI API Tests'
  env:
    API_KEY: $(API_KEY)
    LLM_API_KEY: $(LLM_API_KEY)

- task: PublishTestResults@2
  inputs:
    testResultsFiles: 'tmp/api_test_results_*.json'
    testRunTitle: 'Phoenix AI API Tests'
```

## 🔧 Troubleshooting

### Common Issues and Solutions

#### Gherkin Generation Issues

**Problem:** Generated Gherkin is too generic
- **Solution:** Provide more context in your prompt
- **Example:** Instead of "test login", use "test login API at /auth/login with email and password, expect JWT token and user profile data"

**Problem:** Gherkin doesn't match my API structure
- **Solution:** Edit the generated Gherkin manually
- **Tip:** The generated text is fully editable before execution

#### API Testing Issues

**Problem:** Authentication Failures
- ✅ Verify Bearer token is not expired
- ✅ Check token format (should start with "Bearer " if using headers)
- ✅ Validate API key permissions
- ✅ Ensure correct authentication type is selected

**Problem:** Network Timeouts
- ✅ Check API endpoint is accessible
- ✅ Verify base URL and endpoint are correct
- ✅ Test API directly with curl/Postman first
- ✅ Check firewall/proxy settings

**Problem:** Schema Validation Errors
- ✅ Verify expected schema matches actual response
- ✅ Check for API version mismatches
- ✅ Use AI-powered validation for flexible schema checking
- ✅ Test with actual API response first

**Problem:** Value Extraction Failures
- ✅ Verify JSONPath expression is correct
- ✅ Check response structure matches expected format
- ✅ Test JSONPath expressions separately
- ✅ Use simple paths first (e.g., `data.id` before `data.users[0].profile.id`)

#### UI Validation Issues

**Problem:** UI validation always fails
- ✅ Ensure browser settings allow headless/headed mode
- ✅ Check UI URL is accessible
- ✅ Verify extracted values are correct
- ✅ Test UI validation steps manually first
- ✅ Add delays if page loads slowly

**Problem:** Variables not replaced in UI steps
- ✅ Use correct placeholder format: `{variableName}`
- ✅ Ensure variable names match extraction config
- ✅ Check variables were actually extracted from API response

**Problem:** Browser crashes during UI validation
- ✅ Check browser configuration settings
- ✅ Ensure sufficient system resources
- ✅ Try disabling headless mode for debugging
- ✅ Update Playwright dependencies

### Debug Tips

1. **Test API Separately First**
   ```bash
   curl -X GET "https://api.example.com/users" \
        -H "Authorization: Bearer YOUR_TOKEN"
   ```

2. **Validate JSONPath Expressions**
   Use online JSONPath testers with your actual API response

3. **Enable Verbose Logging**
   Check execution logs for detailed error messages

4. **Test in Stages**
   - ✅ First: Test API only (disable UI validation)
   - ✅ Second: Verify value extraction works
   - ✅ Third: Enable UI validation

5. **Check Test Results JSON**
   Review the detailed results for specific error messages

### Getting Help

- 📚 Check the [README](../README.md) for general setup
- 🔍 Review [PR Testing Documentation](PR_TESTING_TOOL.md)
- 🐛 Report issues on [GitHub Issues](https://github.com/manumohandask/Phoenix.ai/issues)
- 💬 Join our community discussions

## 📊 Sample Test Report

```markdown
# API Testing Report

Generated: 2025-11-20 10:30:00

## Summary
- Total Tests: 5
- Passed: 4
- Failed: 1
- Success Rate: 80.0%

## Test Results

### Test 1: User Login ✅ PASSED
- Execution Time: 1.23s
- Timestamp: 2025-11-20T10:28:30
- API Status: 200
- Extracted Values: {"userId": 123, "userName": "John Doe", "token": "eyJ..."}

### Test 2: Profile Validation ✅ PASSED
- Execution Time: 3.45s
- API Status: 200
- UI Validation: Success
- All extracted values validated in UI

### Test 3: Order Creation ✅ PASSED
- Execution Time: 2.10s
- API Status: 201
- Extracted Values: {"orderId": "ORD-456", "total": 99.99}
```

---

**Phoenix AI** - Making API testing intelligent, comprehensive, and effortless 🔥

## 🎯 Next Steps

1. **Try the Examples**: Start with the user login example above
2. **Generate Your First Gherkin**: Use natural language to describe your test
3. **Configure Your API**: Set up base URL and authentication
4. **Run Your First Test**: Execute and review results
5. **Enable UI Validation**: Add end-to-end validation for critical flows

**Happy Testing! 🚀**
