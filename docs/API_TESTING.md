# 🔌 API Testing Guide - Phoenix AI

Phoenix AI provides comprehensive API integration testing capabilities powered by AI. This guide will help you leverage Phoenix AI for automated API testing.

## Overview

Phoenix AI can automatically:
- Discover and test API endpoints
- Generate intelligent test cases based on OpenAPI/Swagger specifications
- Validate request/response patterns
- Perform load testing and performance monitoring
- Generate detailed API test reports

## Getting Started

### 1. Basic API Testing

The simplest way to test an API endpoint:

```python
# Example: Testing a REST API endpoint
task = """
Test the API endpoint at https://api.example.com/users
- Verify GET request returns 200 status
- Validate response structure
- Check data types and required fields
"""
```

### 2. OpenAPI/Swagger Integration

Phoenix AI can import and test from OpenAPI specifications:

```yaml
# Import your OpenAPI spec
openapi_url: "https://api.example.com/swagger.json"

# Phoenix AI will automatically:
# - Parse all endpoints
# - Generate test cases for each operation
# - Validate against schema definitions
# - Test authentication flows
```

### 3. Authentication Testing

Phoenix AI supports various authentication methods:

- **API Keys**: Header or query parameter based
- **OAuth 2.0**: Full OAuth flow testing
- **Bearer Tokens**: JWT and access token validation
- **Basic Auth**: Username/password authentication

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

## Example Workflows

### Testing a User Registration API

```python
# Phoenix AI task for user registration flow
task = """
Test user registration API flow:
1. POST to /api/register with valid user data
2. Verify 201 status and user ID returned
3. GET user details with returned ID
4. Verify all fields match registration data
5. Test duplicate registration (should fail)
6. Test invalid email format (should fail)
"""
```

### Testing Search Functionality

```python
# Phoenix AI task for search API
task = """
Test search API at /api/search:
1. Test with valid query parameters
2. Validate pagination works correctly
3. Test filter combinations
4. Verify sorting options
5. Test edge cases (empty query, special characters)
6. Measure response times for various query sizes
"""
```

## Configuration

### Setting Up API Tests

1. **Navigate to API Testing Tab** in Phoenix AI
2. **Configure Base URL** for your API
3. **Add Authentication** credentials if required
4. **Import OpenAPI Spec** (optional but recommended)
5. **Define Test Scenarios** using natural language

### Environment Variables

Add to your `.env` file:

```env
# API Testing Configuration
API_BASE_URL=https://api.example.com
API_AUTH_TOKEN=your-token-here
API_TIMEOUT=30
API_RETRY_COUNT=3

# For OpenAPI/Swagger
OPENAPI_SPEC_URL=https://api.example.com/swagger.json
```

## Advanced Features

### Data-Driven Testing

Phoenix AI can generate test data automatically:
- Valid test data based on schema
- Invalid data for negative testing
- Edge cases and boundary values
- Randomized data for comprehensive testing

### Contract Testing

Ensure API contracts are maintained:
- Compare responses against expected schema
- Detect breaking changes
- Validate backward compatibility
- Monitor API evolution

### Load Testing

Test API under load:
- Concurrent request simulation
- Stress testing
- Spike testing
- Endurance testing

## Best Practices

### 1. Use Descriptive Test Names

```python
# Good
task = "Test user login with valid credentials and verify JWT token generation"

# Avoid
task = "Test login"
```

### 2. Test Both Success and Failure Paths

Always include:
- Happy path scenarios
- Error handling tests
- Edge cases
- Security tests

### 3. Validate Response Thoroughly

Check:
- Status codes
- Response structure
- Data types
- Business logic
- Error messages

### 4. Use Environment-Specific Configurations

Separate configurations for:
- Development
- QA/Staging
- Production

### 5. Monitor Performance Trends

Track:
- Response time trends
- Error rates
- Success rates
- API availability

## Reporting

Phoenix AI generates comprehensive reports including:
- Test execution summary
- Pass/fail status for each test
- Response times and performance metrics
- Detailed error logs
- API coverage statistics
- Trend analysis

## Integration with CI/CD

Phoenix AI can be integrated into your CI/CD pipeline:

```yaml
# Example GitHub Actions workflow
name: API Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run Phoenix AI API Tests
        run: |
          python run_api_tests.py --config api_tests.yaml
```

## Troubleshooting

### Common Issues

**Authentication Failures**
- Verify API keys are correctly set
- Check token expiration
- Validate OAuth flow configuration

**Network Timeouts**
- Increase timeout values
- Check API availability
- Verify firewall rules

**Schema Validation Errors**
- Update OpenAPI specification
- Check for API version mismatches
- Verify response format

## Need Help?

- Check the [Quick Start Guide](QUICK_START_HRB.md)
- Review [PR Testing Documentation](PR_TESTING_TOOL.md)
- Visit our [GitHub Issues](https://github.com/manumohandask/Phoenix.ai/issues)

---

**Phoenix AI** - Making API testing intelligent and effortless 🔥
