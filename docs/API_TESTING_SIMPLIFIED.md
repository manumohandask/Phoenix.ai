# API Testing Module - Simplified Version

## ✅ Changes Completed

### What Was Removed
- ❌ Step 2: API Configuration (base URL, endpoint, method, headers, auth, etc.)
- ❌ Step 3: UI Validation (browser-based UI testing)
- ❌ Complex configuration forms with multiple accordions
- ❌ Value extraction with JSONPath
- ❌ UI validation with browser automation

### What Remains
- ✅ **Gherkin Generator**: AI-powered BDD scenario generation from natural language
- ✅ **Gherkin Validator**: Syntax validation for generated scenarios
- ✅ **Gherkin Executor**: Direct execution that extracts API details from Gherkin

## 🎯 New Workflow (3 Simple Steps)

### 1. Generate Gherkin
**Input a natural language description** like:
```
Test GET https://jsonplaceholder.typicode.com/users, verify status 200, 
and validate that user 'Leanne Graham' exists in the response
```

**AI generates a proper Gherkin scenario**:
```gherkin
Feature: Users API Testing

Scenario: Validate users endpoint
  Given the API endpoint is "https://jsonplaceholder.typicode.com/users"
  When I send a GET request
  Then the response status code should be 200
  Then the response should be a JSON array
  Then the response should contain a user with name "Leanne Graham"
```

### 2. Validate Syntax (Optional)
Click "🔍 Validate Gherkin Syntax" to check if the scenario is properly formatted.

### 3. Execute Test
Click "🚀 Execute Test" - the agent automatically:
- Extracts the API URL from Gherkin (`Given the API endpoint is "..."`)
- Determines the HTTP method (`When I send a GET request`)
- Identifies expected status code (`Then the response status code should be 200`)
- Validates array structure (`Then the response should be a JSON array`)
- Checks for specific content (`Then the response should contain...`)

## 📊 Test Results

Results are displayed in JSON format showing:
```json
{
  "status": "passed",
  "execution_time": "0.45s",
  "timestamp": "2024-11-20T10:30:00",
  "api_endpoint": "https://jsonplaceholder.typicode.com/users",
  "status_code": 200,
  "response_time_ms": 234.5,
  "extracted_values": {
    "contains_Leanne_Graham": true
  },
  "validation_errors": [],
  "message": "Test passed successfully"
}
```

## 🚀 How to Use

### Quick Start
1. Open Phoenix AI at http://127.0.0.1:7788
2. Go to "🔌 API Testing" tab
3. Make sure your LLM settings are configured in "Agent Settings" tab
4. Describe your API test in plain English
5. Click "Generate Gherkin Scenario"
6. Review/edit the generated Gherkin
7. Click "Execute Test"

### Example Test Cases

#### Example 1: Simple GET Request
```
Test the JSONPlaceholder users API at https://jsonplaceholder.typicode.com/users
Verify status is 200 and response is an array
```

#### Example 2: Checking Specific Content
```
Call GET https://jsonplaceholder.typicode.com/users/1
Verify status 200 and check that the response contains email "Sincere@april.biz"
```

#### Example 3: POST Request
```
Send a POST request to https://jsonplaceholder.typicode.com/posts
with title "Test Post" and body "Test content"
Verify status code is 201
```

## 🎨 UI Components

The simplified tab now has:

1. **Gherkin Prompt** - Natural language test description
2. **Context Input** - Optional additional context
3. **Generate Button** - Creates Gherkin from description
4. **Generated Gherkin** - Editable text area with the scenario
5. **Validate Button** - Checks Gherkin syntax
6. **Execute Button** - Runs the test
7. **Status Output** - Shows pass/fail with message
8. **Test Results** - Detailed JSON results

## 🔧 Technical Details

### Gherkin Parsing Logic

The executor automatically extracts:

| Gherkin Pattern | Extracted Detail |
|----------------|------------------|
| `Given the API endpoint is "URL"` | API URL |
| `When I send a GET/POST/PUT/DELETE request` | HTTP Method |
| `Then the response status code should be N` | Expected Status |
| `Then the response should be a JSON array` | Array validation |
| `Then the response should contain "text"` | Content validation |

### Configuration Required

Only needs configuration in **Agent Settings** tab:
- LLM Provider (OpenAI, Anthropic, Google, etc.)
- Model Name
- API Key
- Base URL (optional, for custom endpoints)

### Dependencies

All existing dependencies remain the same:
- `requests` - HTTP client
- `jsonpath-ng` - Not used in simplified version
- `pytest-bdd` - For Gherkin parsing
- LangChain - For AI generation

## 📝 Notes

- **No manual API configuration needed** - Everything is extracted from Gherkin
- **Smart parsing** - Understands natural language in Gherkin steps
- **Automatic validation** - Validates based on Gherkin assertions
- **Simple interface** - Just describe, generate, and execute
- **Agent Settings integration** - Uses centralized LLM configuration

## 🎉 Benefits

1. **Faster Testing** - No manual configuration forms
2. **Natural Language** - Write tests in plain English
3. **BDD Best Practices** - Generates proper Gherkin
4. **Self-Documenting** - Gherkin serves as documentation
5. **Flexible** - Can edit generated Gherkin before execution
6. **Automated** - Extracts everything from scenario

## 🔜 Future Enhancements (If Needed)

If you later need more features, we can add:
- Header configuration
- Authentication support
- Request body templates
- Response schema validation
- Batch test execution
- Test history and reports

---

**The application is now running at: http://127.0.0.1:7788**

Go to the **🔌 API Testing** tab to try it out!
