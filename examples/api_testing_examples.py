"""
API Testing Agent - Quick Start Examples
Run these examples to test the API testing functionality
"""
import asyncio
import json
from src.agent.api_testing import APITestingAgent, APITestConfig, UIValidationConfig


async def example_1_simple_api_test():
    """Example 1: Simple API test without UI validation"""
    print("\n" + "="*60)
    print("Example 1: Simple API Test")
    print("="*60 + "\n")
    
    # Initialize agent
    agent = APITestingAgent(
        llm_provider="openai",
        model_name="gpt-4",
        api_key="your-api-key-here"
    )
    
    # Generate Gherkin from natural language
    prompt = """
    Test the JSONPlaceholder API to get user details.
    Send a GET request to /users/1 and verify the response contains user data.
    """
    
    gherkin = await agent.generate_gherkin_from_prompt(prompt)
    print("Generated Gherkin:")
    print(gherkin)
    print()
    
    # Configure API test
    api_config = APITestConfig(
        base_url="https://jsonplaceholder.typicode.com",
        endpoint="/users/1",
        method="GET",
        expected_status=200,
        extract_values={
            "userId": "id",
            "userName": "name",
            "userEmail": "email"
        }
    )
    
    # Execute test
    result = await agent.parse_and_execute_gherkin(gherkin, api_config)
    
    # Print results
    print("\nTest Results:")
    print(f"Success: {result.success}")
    print(f"Execution Time: {result.execution_time:.2f}s")
    print(f"Extracted Values: {json.dumps(result.extracted_values, indent=2)}")
    print(f"API Response Status: {result.api_response.get('status_code')}")


async def example_2_api_with_auth():
    """Example 2: API test with authentication"""
    print("\n" + "="*60)
    print("Example 2: API Test with Authentication")
    print("="*60 + "\n")
    
    agent = APITestingAgent(
        llm_provider="openai",
        model_name="gpt-4",
        api_key="your-api-key-here"
    )
    
    # Generate Gherkin
    prompt = """
    Test authenticated API endpoint to create a new post.
    Send POST request with title and body.
    Verify the response returns the created post with an ID.
    """
    
    gherkin = await agent.generate_gherkin_from_prompt(prompt)
    print("Generated Gherkin:")
    print(gherkin)
    print()
    
    # Configure API test with request body
    api_config = APITestConfig(
        base_url="https://jsonplaceholder.typicode.com",
        endpoint="/posts",
        method="POST",
        headers={
            "Content-Type": "application/json"
        },
        body={
            "title": "Test Post",
            "body": "This is a test post content",
            "userId": 1
        },
        expected_status=201,
        extract_values={
            "postId": "id",
            "postTitle": "title"
        }
    )
    
    # Execute test
    result = await agent.parse_and_execute_gherkin(gherkin, api_config)
    
    # Print results
    print("\nTest Results:")
    print(f"Success: {result.success}")
    print(f"Extracted Values: {json.dumps(result.extracted_values, indent=2)}")


async def example_3_api_with_ui_validation():
    """Example 3: API test with UI validation"""
    print("\n" + "="*60)
    print("Example 3: API Test with UI Validation")
    print("="*60 + "\n")
    
    agent = APITestingAgent(
        llm_provider="openai",
        model_name="gpt-4",
        api_key="your-api-key-here",
        browser_config={
            "headless": False,
            "disable_security": True
        }
    )
    
    # Generate Gherkin
    prompt = """
    Test user API to get user details, extract the name and email,
    then verify these details appear correctly on the user profile page.
    """
    
    gherkin = await agent.generate_gherkin_from_prompt(prompt)
    print("Generated Gherkin:")
    print(gherkin)
    print()
    
    # Configure API test
    api_config = APITestConfig(
        base_url="https://jsonplaceholder.typicode.com",
        endpoint="/users/1",
        method="GET",
        expected_status=200,
        extract_values={
            "userName": "name",
            "userEmail": "email",
            "userWebsite": "website"
        }
    )
    
    # Configure UI validation
    ui_validation = UIValidationConfig(
        url="https://jsonplaceholder.typicode.com/users/1",
        validation_steps=[
            "Verify the page displays user information",
            "Check that the name {userName} is present",
            "Verify email {userEmail} is shown"
        ],
        expected_values={
            "userName": "should be visible",
            "userEmail": "should be displayed"
        }
    )
    
    # Execute test
    result = await agent.parse_and_execute_gherkin(
        gherkin, 
        api_config, 
        ui_validation
    )
    
    # Print results
    print("\nTest Results:")
    print(f"Success: {result.success}")
    print(f"API Success: {result.api_response.get('status_code') == 200}")
    print(f"UI Validation: {result.ui_validation_result}")
    print(f"Extracted Values: {json.dumps(result.extracted_values, indent=2)}")
    
    # Generate report
    report = agent.generate_test_report()
    print("\n" + report)


async def example_4_batch_testing():
    """Example 4: Multiple API tests with reporting"""
    print("\n" + "="*60)
    print("Example 4: Batch API Testing")
    print("="*60 + "\n")
    
    agent = APITestingAgent(
        llm_provider="openai",
        model_name="gpt-4",
        api_key="your-api-key-here"
    )
    
    # Test multiple endpoints
    test_configs = [
        {
            "prompt": "Get user with ID 1",
            "api_config": APITestConfig(
                base_url="https://jsonplaceholder.typicode.com",
                endpoint="/users/1",
                method="GET",
                expected_status=200
            )
        },
        {
            "prompt": "Get all posts",
            "api_config": APITestConfig(
                base_url="https://jsonplaceholder.typicode.com",
                endpoint="/posts",
                method="GET",
                expected_status=200
            )
        },
        {
            "prompt": "Get comments for post 1",
            "api_config": APITestConfig(
                base_url="https://jsonplaceholder.typicode.com",
                endpoint="/posts/1/comments",
                method="GET",
                expected_status=200
            )
        }
    ]
    
    # Execute all tests
    for i, test_config in enumerate(test_configs, 1):
        print(f"\nExecuting Test {i}/{len(test_configs)}...")
        
        gherkin = await agent.generate_gherkin_from_prompt(test_config["prompt"])
        result = await agent.parse_and_execute_gherkin(
            gherkin,
            test_config["api_config"]
        )
        
        status = "✅ PASSED" if result.success else "❌ FAILED"
        print(f"Test {i}: {status} ({result.execution_time:.2f}s)")
    
    # Generate comprehensive report
    report = agent.generate_test_report()
    print("\n" + "="*60)
    print("FINAL REPORT")
    print("="*60)
    print(report)
    
    # Save results
    agent.save_test_results("tmp/batch_test_results.json")
    print("\n✅ Results saved to tmp/batch_test_results.json")


def main():
    """Run examples"""
    print("\n🔌 Phoenix AI - API Testing Examples\n")
    
    examples = {
        "1": ("Simple API Test", example_1_simple_api_test),
        "2": ("API Test with Authentication", example_2_api_with_auth),
        "3": ("API Test with UI Validation", example_3_api_with_ui_validation),
        "4": ("Batch API Testing", example_4_batch_testing),
    }
    
    print("Available Examples:")
    for key, (name, _) in examples.items():
        print(f"  {key}. {name}")
    print("  all. Run all examples")
    print("  q. Quit")
    
    choice = input("\nSelect an example to run (1-4, all, or q): ").strip().lower()
    
    if choice == "q":
        print("Goodbye!")
        return
    
    if choice == "all":
        for name, func in examples.values():
            asyncio.run(func())
    elif choice in examples:
        name, func = examples[choice]
        asyncio.run(func())
    else:
        print("Invalid choice!")


if __name__ == "__main__":
    main()
