# Quick Reference: Gherkin-Based API Testing

## One-Line Summary
Describe your API test in English → AI generates Gherkin → Click Execute → Get Results

## Workflow

```
┌─────────────────────────────────────────────────────────────┐
│  1. DESCRIBE TEST                                           │
│  "Test GET https://api.example.com/users and verify 200"   │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  2. AI GENERATES GHERKIN                                    │
│  Feature: Users API                                         │
│  Scenario: Get users                                        │
│    Given the API endpoint is "https://api.example.com/users"│
│    When I send a GET request                                │
│    Then the response status code should be 200              │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  3. EXECUTE TEST                                            │
│  Agent extracts: URL, Method, Expected Status               │
│  Makes API call and validates response                      │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  4. VIEW RESULTS                                            │
│  ✅ Test PASSED in 0.45s                                    │
│  Status: 200, Response Time: 234ms                          │
└─────────────────────────────────────────────────────────────┘
```

## Supported Gherkin Patterns

### API Endpoint
```gherkin
Given the API endpoint is "https://jsonplaceholder.typicode.com/users"
Given the URL is "https://api.example.com/data"
```
👉 Extracts the API URL to call

### HTTP Methods
```gherkin
When I send a GET request
When I send a POST request to the endpoint
When I send a PUT request
When I send a DELETE request
```
👉 Determines HTTP method (default: GET)

### Status Code Validation
```gherkin
Then the response status code should be 200
Then the status code should be 201
Then I should receive a 404 status
```
👉 Validates response status (default: 200)

### Response Structure
```gherkin
Then the response should be a JSON array
Then the response should be an array
Then the response body should be a JSON array
```
👉 Validates that response is an array

### Content Validation
```gherkin
Then the response should contain "Leanne Graham"
Then the response body should contain "success"
Then the response should contain a user with name "John"
```
👉 Checks if specific text exists in response

## Example Prompts

### Basic GET Test
```
Test https://jsonplaceholder.typicode.com/users 
with GET request and verify status 200
```

### Array Validation
```
Call the users endpoint at https://jsonplaceholder.typicode.com/users
Verify it returns a 200 status and the response is an array
```

### Content Checking
```
GET https://jsonplaceholder.typicode.com/users
Check status is 200 and response contains "Leanne Graham"
```

### POST Request
```
POST to https://jsonplaceholder.typicode.com/posts
Expect 201 status code
```

### Multiple Validations
```
Test GET https://jsonplaceholder.typicode.com/users endpoint
Verify:
- Status code is 200
- Response is a JSON array
- Contains user "Leanne Graham"
- Contains email "Sincere@april.biz"
```

## Result Fields Explained

```json
{
  "status": "passed",              // ← Overall test result
  "execution_time": "0.45s",       // ← How long test took
  "timestamp": "2024-11-20...",    // ← When test ran
  "api_endpoint": "https://...",   // ← URL that was tested
  "status_code": 200,              // ← Actual HTTP status
  "response_time_ms": 234.5,       // ← API response latency
  "extracted_values": {            // ← What was found
    "contains_Leanne_Graham": true
  },
  "validation_errors": [],         // ← Any failures
  "message": "Test passed..."      // ← Human-readable result
}
```

## Troubleshooting

### "❌ Please configure LLM settings"
→ Go to **Agent Settings** tab and set:
  - LLM Provider
  - Model Name  
  - API Key

### "❌ Could not extract API URL"
→ Make sure your Gherkin has:
```gherkin
Given the API endpoint is "https://your-url-here.com/path"
```

### "❌ Test FAILED: Expected status 200, got 404"
→ Check if the API URL is correct and accessible

### Empty Response
→ The API might not return JSON. Check `response_data.text` field

## Tips

✅ **Always include the full URL** in your description
```
Good: "Test https://jsonplaceholder.typicode.com/users"
Bad:  "Test the users endpoint"
```

✅ **Be specific about expected results**
```
Good: "Verify status 200 and response contains 'Leanne Graham'"
Bad:  "Test the API"
```

✅ **You can edit generated Gherkin** before executing
- Fix typos
- Add more validations
- Adjust expected values

✅ **Use the validate button** to check syntax before running

✅ **Start simple** - Test basic GET requests first, then add complexity

## Quick Test

Try this immediately after opening the app:

1. **Prompt**: 
```
Test GET https://jsonplaceholder.typicode.com/users, 
verify status 200 and check response contains "Leanne Graham"
```

2. **Click**: Generate Gherkin Scenario

3. **Click**: Execute Test

4. **Expected**: ✅ Test PASSED

## Need More Features?

If you need:
- Custom headers
- Authentication
- Request body
- Complex JSONPath extraction
- UI validation

Let me know and we can add them back in a modular way!

---

**Application URL**: http://127.0.0.1:7788
**Tab**: 🔌 API Testing
