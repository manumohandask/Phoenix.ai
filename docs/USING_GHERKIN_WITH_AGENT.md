# Using Generated Gherkin with Phoenix AI API Testing

## Example: Testing JSONPlaceholder Users API

### Generated Gherkin Scenario

```gherkin
Feature: Users API

Scenario: Retrieve users and validate Leanne Graham's presence
  Given the API endpoint is "https://jsonplaceholder.typicode.com/users"
  When I send a GET request to the endpoint
  Then the response status code should be 200
  Then the response body should be a JSON array
  Then the response body should contain an object with the name "Leanne Graham"
```

## How to Execute This Gherkin

### Step 1: Copy the Generated Gherkin
The Gherkin above is already in the "Generated Gherkin Scenario" field after generation.

### Step 2: Configure API Details

Based on the Gherkin scenario, configure the following:

**API Configuration:**
- **Base URL:** `https://jsonplaceholder.typicode.com`
- **Endpoint:** `/users`
- **HTTP Method:** `GET`
- **Expected Status:** `200`

**Response Validation:**
In the "Expected Response Schema" section (optional but recommended):
```json
{
  "type": "array",
  "items": {
    "type": "object",
    "properties": {
      "id": {"type": "number"},
      "name": {"type": "string"},
      "username": {"type": "string"},
      "email": {"type": "string"}
    }
  }
}
```

**Extract Values:**
To validate "Leanne Graham" appears in the response:
```json
{
  "firstUserName": "[0].name",
  "firstUserId": "[0].id"
}
```

### Step 3: Run the Test

Click "🚀 Run API Test"

### Expected Results

```json
{
  "success": true,
  "scenario": "Retrieve users and validate Leanne Graham's presence",
  "execution_time": 1.23,
  "api_response": {
    "status_code": 200,
    "body": [
      {
        "id": 1,
        "name": "Leanne Graham",
        "username": "Bret",
        "email": "Sincere@april.biz",
        ...
      },
      ...
    ]
  },
  "extracted_values": {
    "firstUserName": "Leanne Graham",
    "firstUserId": 1
  }
}
```

## How the Agent Uses Gherkin

The API Testing Agent uses the Gherkin scenario in the following way:

1. **Parses the Gherkin** - Extracts Feature, Scenario, Given/When/Then steps
2. **Maps to API Configuration** - Uses your configured API settings
3. **Executes API Call** - Makes the HTTP request based on config
4. **Validates Response** - Checks status code, schema, and extracted values
5. **Reports Results** - Shows success/failure with detailed information

## Validation Logic

The agent validates based on your Gherkin "Then" statements:

| Gherkin Statement | Agent Validation |
|-------------------|------------------|
| `response status code should be 200` | Checks `api_response.status_code == 200` |
| `response body should be a JSON array` | Validates response is an array type |
| `should contain an object with the name "Leanne Graham"` | Checks extracted values or searches in response body |

## Advanced: Adding Custom Validation

You can enhance validation by:

### Option 1: Use Response Schema
Define the expected structure in "Expected Response Schema"

### Option 2: Extract Specific Values
Use JSONPath to extract and validate specific data:
```json
{
  "allUserNames": "[*].name",
  "leanneEmail": "[?(@.name=='Leanne Graham')].email"
}
```

### Option 3: Enable UI Validation
If you want to verify the API data appears in a UI:

1. Check "Enable UI Validation"
2. Enter UI URL (e.g., `https://example.com/users`)
3. Add validation steps:
   ```
   Navigate to the users page
   Verify {firstUserName} is displayed in the user list
   Check that user ID {firstUserId} appears
   ```

## Complete Working Example

Here's the complete configuration for your Gherkin:

```yaml
Gherkin Scenario: |
  Feature: Users API
  Scenario: Retrieve users and validate Leanne Graham's presence
    Given the API endpoint is "https://jsonplaceholder.typicode.com/users"
    When I send a GET request to the endpoint
    Then the response status code should be 200
    Then the response body should be a JSON array
    Then the response body should contain an object with the name "Leanne Graham"

API Configuration:
  base_url: "https://jsonplaceholder.typicode.com"
  endpoint: "/users"
  method: "GET"
  expected_status: 200
  
Response Validation:
  extract_values:
    firstUserName: "[0].name"
    firstUserId: "[0].id"
    allNames: "[*].name"
  
  expected_schema:
    type: "array"
    minItems: 1
```

## Running From Code

You can also execute this programmatically:

```python
from src.agent.api_testing import APITestingAgent, APITestConfig

# Initialize agent
agent = APITestingAgent(
    llm_provider="openai",
    model_name="gpt-4",
    api_key="your-api-key"
)

# Your Gherkin
gherkin = """
Feature: Users API

Scenario: Retrieve users and validate Leanne Graham's presence
  Given the API endpoint is "https://jsonplaceholder.typicode.com/users"
  When I send a GET request to the endpoint
  Then the response status code should be 200
  Then the response body should be a JSON array
  Then the response body should contain an object with the name "Leanne Graham"
"""

# Configure API
api_config = APITestConfig(
    base_url="https://jsonplaceholder.typicode.com",
    endpoint="/users",
    method="GET",
    expected_status=200,
    extract_values={
        "firstUserName": "[0].name"
    }
)

# Execute
import asyncio
result = asyncio.run(agent.parse_and_execute_gherkin(gherkin, api_config))

print(f"Success: {result.success}")
print(f"Extracted: {result.extracted_values}")
```

## Troubleshooting

### Issue: "Leanne Graham not found in response"
- **Solution:** Check the JSONPath expression in extract_values
- Try: `"userName": "[?(@.name=='Leanne Graham')].name"`

### Issue: "Response schema validation failed"
- **Solution:** Make the schema less strict or remove it for initial testing
- The API call will still succeed, just without schema validation

### Issue: "API test failed with status 404"
- **Solution:** Verify Base URL and Endpoint are correct
- Test manually: `curl https://jsonplaceholder.typicode.com/users`

## Summary

✅ **YES** - You can use the generated Gherkin with the agent!

The workflow is:
1. Generate Gherkin (or write it manually)
2. Configure API details to match the Gherkin
3. Optionally configure value extraction
4. Run the test
5. Review results

The agent will parse your Gherkin and use it to guide the test execution and reporting! 🚀
