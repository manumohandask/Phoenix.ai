# 🚀 API Testing Module - Quick Start Guide

## Prerequisites

1. Phoenix AI installed and configured
2. LLM API key (OpenAI, Anthropic, etc.)
3. Python 3.11+

## Installation

If you haven't already, install the new dependencies:

```bash
pip install requests jsonpath-ng pytest-bdd
```

Or reinstall from requirements.txt:

```bash
pip install -r requirements.txt
```

## Getting Started

### Step 1: Launch Phoenix AI

```bash
python phoenix.py
```

### Step 2: Navigate to API Testing Tab

In the web interface, click on the **"🔌 API Testing"** tab.

### Step 3: Generate Your First Gherkin Scenario

**In the "Describe Your Test Scenario" field, enter:**

```
Test the JSONPlaceholder API to get user details. 
Send a GET request to /users/1. 
Verify the response contains user name and email.
Extract the user ID and name for later use.
```

**Click:** `🤖 Generate Gherkin Scenario`

**Result:** You'll see a Gherkin scenario like:

```gherkin
Feature: User Data Retrieval
Scenario: Get user details by ID
  Given the API endpoint "/users/1" is available
  When I send a GET request
  Then the response status code should be 200
  And the response should contain user name
  And the response should contain user email
```

### Step 4: Configure API Details

**Fill in the configuration:**

- **Base URL:** `https://jsonplaceholder.typicode.com`
- **Endpoint:** `/users/1`
- **HTTP Method:** `GET`
- **Expected Status:** `200`

**Expand "Response Validation" and set:**

```json
{
  "userId": "id",
  "userName": "name",
  "userEmail": "email"
}
```

### Step 5: Run the Test

**Click:** `🚀 Run API Test`

**You'll see:**
- ✅ Test PASSED
- Execution Time: ~1.5s
- Extracted Values with actual data

### Step 6: View Results

The results will show:

```json
{
  "success": true,
  "scenario": "Get user details by ID",
  "execution_time": 1.23,
  "api_response": {
    "status_code": 200,
    "body": {
      "id": 1,
      "name": "Leanne Graham",
      "email": "Sincere@april.biz"
    }
  },
  "extracted_values": {
    "userId": 1,
    "userName": "Leanne Graham",
    "userEmail": "Sincere@april.biz"
  }
}
```

## Example 2: POST Request with Authentication

### Generate Gherkin

**Prompt:**
```
Test creating a new post via API. 
Send POST request with title and body. 
Use bearer token authentication. 
Verify the response returns the created post with an ID.
```

### Configure

- **Base URL:** `https://api.example.com`
- **Endpoint:** `/api/posts`
- **Method:** `POST`
- **Expected Status:** `201`

**Headers:**
```json
{
  "Content-Type": "application/json"
}
```

**Request Body:**
```json
{
  "title": "My Test Post",
  "body": "This is the content of my test post",
  "userId": 1
}
```

**Authentication:**
- Select: `Bearer Token`
- Token: `your-bearer-token-here`

**Extract Values:**
```json
{
  "postId": "data.id",
  "postTitle": "data.title"
}
```

### Run and Verify

Click `🚀 Run API Test` and check the results!

## Example 3: API + UI Validation

### Generate Gherkin

**Prompt:**
```
Test user login API. 
Post email and password to /auth/login. 
Extract the user name and ID from response. 
Then verify the user name appears on the dashboard page.
```

### Configure API

- **Base URL:** `https://api.example.com`
- **Endpoint:** `/auth/login`
- **Method:** `POST`

**Body:**
```json
{
  "email": "test@example.com",
  "password": "password123"
}
```

**Extract Values:**
```json
{
  "userId": "data.user.id",
  "userName": "data.user.name",
  "authToken": "data.token"
}
```

### Configure UI Validation

**Check:** `Enable UI Validation`

**UI URL:** `https://app.example.com/dashboard`

**Validation Steps:**
```
Navigate to the dashboard
Verify the welcome message contains {userName}
Check that the user menu shows {userName}
Confirm the profile link includes user ID {userId}
```

**Expected Values:**
```json
{
  "userName": "should be visible in header",
  "userId": "should be in profile URL"
}
```

### Run Complete Test

Click `🚀 Run API Test` and watch as Phoenix AI:
1. Executes the API call
2. Extracts the values
3. Opens the browser
4. Navigates to the dashboard
5. Validates the extracted values in the UI
6. Reports success or failure

## Tips for Success

### Writing Good Prompts

✅ **Good:**
```
Test the user registration API at /api/register. 
Send POST with email, password, and name. 
Expect 201 status and a user ID in response. 
Extract the user ID and verify it appears in the welcome email.
```

❌ **Avoid:**
```
test register
```

### JSONPath Tips

| Want to Extract | JSONPath | Example Response |
|----------------|----------|------------------|
| Top-level field | `fieldName` | `{"fieldName": "value"}` |
| Nested field | `data.user.id` | `{"data": {"user": {"id": 123}}}` |
| Array first item | `items[0].name` | `{"items": [{"name": "John"}]}` |
| Array all items | `items[*].name` | `{"items": [{"name": "John"}, {"name": "Jane"}]}` |

### Authentication

**Bearer Token:**
- Used for JWT tokens
- Common in modern APIs
- Format: `Authorization: Bearer <token>`

**Basic Auth:**
- Username and password
- Base64 encoded
- Format: `Authorization: Basic <encoded>`

## Troubleshooting

### "API test failed: Connection refused"
- ✅ Check base URL is correct
- ✅ Verify API is accessible from your network
- ✅ Test with curl first: `curl https://api.example.com/endpoint`

### "Schema validation failed"
- ✅ Check expected schema matches actual response
- ✅ Use AI-powered validation (it's more flexible)
- ✅ Start without schema validation, add it later

### "UI validation failed"
- ✅ Verify browser configuration allows automation
- ✅ Check UI URL is accessible
- ✅ Test variables were extracted correctly
- ✅ Add waits for slow-loading pages

### "JSONPath extraction error"
- ✅ Verify path syntax: `data.user.id` not `data->user->id`
- ✅ Check response structure matches path
- ✅ Use simple paths first: `id` before `data.users[0].profile.id`

## Next Steps

1. **Try the Examples:** Run `python examples/api_testing_examples.py`
2. **Read Full Documentation:** Check `docs/API_TESTING.md`
3. **Integrate with CI/CD:** See CI/CD examples in documentation
4. **Create Test Suites:** Save multiple test configurations
5. **Monitor Results:** Track success rates over time

## Advanced Features

### Batch Testing

Create multiple test configs and run them sequentially to test complete workflows:

1. Login → Get Token
2. Create Resource → Get ID
3. Update Resource → Verify Changes
4. Delete Resource → Confirm Deletion

### Parameterized Testing

Use variables in your configs for data-driven testing:

```json
{
  "scenarios": [
    {"email": "user1@test.com", "expected": "success"},
    {"email": "invalid-email", "expected": "failure"},
    {"email": "", "expected": "validation_error"}
  ]
}
```

### Reporting

Generate comprehensive reports:

```python
from src.agent.api_testing import APITestingAgent

agent = APITestingAgent(...)
# ... run tests ...
report = agent.generate_test_report()
print(report)

# Save results
agent.save_test_results("tmp/my_tests.json")
```

## Need Help?

- 📚 [Full API Testing Documentation](../docs/API_TESTING.md)
- 📝 [Implementation Summary](../docs/API_TESTING_MODULE_SUMMARY.md)
- 🐛 [Report Issues](https://github.com/manumohandask/Phoenix.ai/issues)
- 💬 Community discussions

---

**Happy Testing! 🔥**

Phoenix AI makes API testing intelligent, comprehensive, and effortless.
