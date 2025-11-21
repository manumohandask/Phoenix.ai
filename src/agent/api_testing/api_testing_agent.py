"""
API Testing Agent with Gherkin Generator and Validation Capabilities
"""
import json
import re
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
import asyncio
from datetime import datetime
import requests
from pathlib import Path

from langchain_core.messages import HumanMessage, SystemMessage
from browser_use import Agent, Controller
from pydantic import BaseModel

from src.utils.llm_provider import get_llm_model
from src.browser.custom_browser import CustomBrowser


@dataclass
class GherkinScenario:
    """Represents a Gherkin scenario"""
    feature: str
    scenario: str
    given: List[str]
    when: List[str]
    then: List[str]
    background: Optional[List[str]] = None


@dataclass
class APITestConfig:
    """Configuration for API testing"""
    base_url: str
    endpoint: str
    method: str
    headers: Optional[Dict[str, str]] = None
    query_params: Optional[Dict[str, str]] = None
    body: Optional[Dict[str, Any]] = None
    auth: Optional[Dict[str, str]] = None
    expected_status: int = 200
    expected_response_schema: Optional[Dict[str, Any]] = None
    extract_values: Optional[Dict[str, str]] = None  # JSONPath expressions to extract values


@dataclass
class UIValidationConfig:
    """Configuration for UI validation after API call"""
    url: str
    validation_steps: List[str]
    expected_values: Dict[str, Any]  # Values extracted from API to validate in UI


@dataclass
class TestResult:
    """Test execution result"""
    success: bool
    scenario_name: str
    timestamp: str
    api_response: Optional[Dict[str, Any]] = None
    ui_validation_result: Optional[Dict[str, Any]] = None
    extracted_values: Optional[Dict[str, Any]] = None
    errors: Optional[List[str]] = None
    execution_time: float = 0.0


class GherkinGenerator:
    """Generates Gherkin scenarios from natural language descriptions"""
    
    def __init__(self, llm_provider: str, model_name: str, api_key: str, base_url: Optional[str] = None):
        self.llm = get_llm_model(
            llm_provider,
            model_name=model_name,
            api_key=api_key,
            base_url=base_url,
            temperature=0.0
        )
    
    async def generate_gherkin(self, description: str, context: Optional[str] = None) -> GherkinScenario:
        """Generate Gherkin scenario from natural language description"""
        system_prompt = """You are an expert at writing Gherkin BDD scenarios for API testing.
Generate a well-structured Gherkin scenario based on the user's description.

Format:
Feature: <Feature name>
Scenario: <Scenario name>
  Given <precondition>
  When <action>
  Then <expected result>

Be specific and include:
- API endpoints and methods
- Request parameters and body
- Expected response status and structure
- Data validation rules
- Any UI validation if mentioned

Return the scenario in a structured JSON format with fields:
{
    "feature": "Feature name",
    "scenario": "Scenario name",
    "given": ["step1", "step2"],
    "when": ["action1", "action2"],
    "then": ["assertion1", "assertion2"]
}"""
        
        user_message = f"Generate a Gherkin scenario for:\n{description}"
        if context:
            user_message += f"\n\nAdditional context:\n{context}"
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_message)
        ]
        
        response = await self.llm.ainvoke(messages)
        
        # Parse the response
        try:
            # Extract JSON from response
            content = response.content
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                scenario_data = json.loads(json_match.group())
                return GherkinScenario(**scenario_data)
            else:
                # Fallback: parse manually
                return self._parse_gherkin_text(content)
        except Exception as e:
            raise ValueError(f"Failed to parse Gherkin scenario: {str(e)}")
    
    def _parse_gherkin_text(self, text: str) -> GherkinScenario:
        """Parse Gherkin text format into structured data"""
        lines = text.strip().split('\n')
        feature = ""
        scenario = ""
        given = []
        when = []
        then = []
        
        current_section = None
        
        for line in lines:
            line = line.strip()
            if line.startswith('Feature:'):
                feature = line.replace('Feature:', '').strip()
            elif line.startswith('Scenario:'):
                scenario = line.replace('Scenario:', '').strip()
            elif line.startswith('Given'):
                current_section = 'given'
                given.append(line.replace('Given', '').strip())
            elif line.startswith('When'):
                current_section = 'when'
                when.append(line.replace('When', '').strip())
            elif line.startswith('Then'):
                current_section = 'then'
                then.append(line.replace('Then', '').strip())
            elif line.startswith('And') and current_section:
                step = line.replace('And', '').strip()
                if current_section == 'given':
                    given.append(step)
                elif current_section == 'when':
                    when.append(step)
                elif current_section == 'then':
                    then.append(step)
        
        return GherkinScenario(
            feature=feature,
            scenario=scenario,
            given=given,
            when=when,
            then=then
        )


class APIValidator:
    """Validates API responses against expected criteria"""
    
    def __init__(self, llm_provider: str, model_name: str, api_key: str, base_url: Optional[str] = None):
        self.llm = get_llm_model(
            llm_provider,
            model_name=model_name,
            api_key=api_key,
            base_url=base_url,
            temperature=0.0
        )
    
    async def execute_api_test(self, config: APITestConfig) -> Tuple[bool, Dict[str, Any], Optional[Dict[str, Any]]]:
        """Execute API test and return success status, response, and extracted values"""
        try:
            url = f"{config.base_url}{config.endpoint}"
            
            # Prepare request
            kwargs = {
                'method': config.method.upper(),
                'url': url,
                'headers': config.headers or {},
                'timeout': 30
            }
            
            if config.query_params:
                kwargs['params'] = config.query_params
            
            if config.body:
                kwargs['json'] = config.body
            
            if config.auth:
                if 'bearer' in config.auth:
                    kwargs['headers']['Authorization'] = f"Bearer {config.auth['bearer']}"
                elif 'basic' in config.auth:
                    kwargs['auth'] = (config.auth['basic']['username'], config.auth['basic']['password'])
            
            # Execute request
            response = requests.request(**kwargs)
            
            # Validate status code
            if response.status_code != config.expected_status:
                return False, {
                    'status_code': response.status_code,
                    'body': response.text,
                    'error': f"Expected status {config.expected_status}, got {response.status_code}"
                }, None
            
            # Parse response
            try:
                response_data = response.json()
            except:
                response_data = {'text': response.text}
            
            # Extract values if specified
            extracted_values = None
            if config.extract_values:
                extracted_values = self._extract_values(response_data, config.extract_values)
            
            # Validate response schema if specified
            if config.expected_response_schema:
                schema_valid = await self._validate_schema(response_data, config.expected_response_schema)
                if not schema_valid:
                    return False, {
                        'status_code': response.status_code,
                        'body': response_data,
                        'error': 'Response schema validation failed'
                    }, extracted_values
            
            return True, {
                'status_code': response.status_code,
                'body': response_data,
                'headers': dict(response.headers)
            }, extracted_values
            
        except Exception as e:
            return False, {'error': str(e)}, None
    
    def _extract_values(self, response_data: Dict[str, Any], extractors: Dict[str, str]) -> Dict[str, Any]:
        """Extract values from response using JSONPath-like expressions"""
        extracted = {}
        
        for key, path in extractors.items():
            try:
                # Simple JSONPath implementation
                value = self._get_nested_value(response_data, path)
                extracted[key] = value
            except Exception as e:
                extracted[key] = f"Error extracting: {str(e)}"
        
        return extracted
    
    def _get_nested_value(self, data: Any, path: str) -> Any:
        """Get nested value from data using dot notation"""
        keys = path.split('.')
        current = data
        
        for key in keys:
            # Handle array indexing
            if '[' in key and ']' in key:
                key_name = key.split('[')[0]
                index = int(key.split('[')[1].split(']')[0])
                current = current[key_name][index]
            else:
                current = current[key]
        
        return current
    
    async def _validate_schema(self, response_data: Dict[str, Any], schema: Dict[str, Any]) -> bool:
        """Use LLM to validate response schema"""
        system_prompt = """You are validating API response against expected schema.
Check if the response data matches the schema requirements.
Return only 'VALID' or 'INVALID' followed by a brief explanation."""
        
        user_message = f"""
Response Data:
{json.dumps(response_data, indent=2)}

Expected Schema:
{json.dumps(schema, indent=2)}

Is the response valid according to the schema?"""
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_message)
        ]
        
        response = await self.llm.ainvoke(messages)
        return 'VALID' in response.content.upper()


class APITestingAgent:
    """Main agent for API testing with Gherkin support"""
    
    def __init__(
        self,
        llm_provider: str,
        model_name: str,
        api_key: str,
        base_url: Optional[str] = None,
        browser_config: Optional[Dict[str, Any]] = None
    ):
        self.llm_provider = llm_provider
        self.model_name = model_name
        self.api_key = api_key
        self.base_url = base_url
        self.browser_config = browser_config or {}
        
        self.gherkin_generator = GherkinGenerator(llm_provider, model_name, api_key, base_url)
        self.api_validator = APIValidator(llm_provider, model_name, api_key, base_url)
        
        self.test_results: List[TestResult] = []
    
    async def generate_gherkin_from_prompt(self, prompt: str, context: Optional[str] = None) -> str:
        """Generate Gherkin scenario from natural language prompt"""
        scenario = await self.gherkin_generator.generate_gherkin(prompt, context)
        
        # Format as Gherkin text
        gherkin_text = f"Feature: {scenario.feature}\n\n"
        gherkin_text += f"Scenario: {scenario.scenario}\n"
        
        for step in scenario.given:
            gherkin_text += f"  Given {step}\n"
        for step in scenario.when:
            gherkin_text += f"  When {step}\n"
        for step in scenario.then:
            gherkin_text += f"  Then {step}\n"
        
        return gherkin_text
    
    async def parse_and_execute_gherkin(
        self,
        gherkin_text: str,
        api_config: APITestConfig,
        ui_validation: Optional[UIValidationConfig] = None
    ) -> TestResult:
        """Parse Gherkin scenario and execute tests"""
        start_time = asyncio.get_event_loop().time()
        
        # Parse Gherkin
        scenario = self._parse_gherkin_scenario(gherkin_text)
        
        # Execute API test
        api_success, api_response, extracted_values = await self.api_validator.execute_api_test(api_config)
        
        errors = []
        ui_result = None
        
        if not api_success:
            errors.append(f"API test failed: {api_response.get('error', 'Unknown error')}")
        
        # Execute UI validation if specified and API test passed
        if api_success and ui_validation and extracted_values:
            ui_result = await self._execute_ui_validation(ui_validation, extracted_values)
            if not ui_result['success']:
                errors.extend(ui_result.get('errors', []))
        
        end_time = asyncio.get_event_loop().time()
        
        result = TestResult(
            success=api_success and (not ui_validation or (ui_result and ui_result['success'])),
            scenario_name=scenario.scenario,
            timestamp=datetime.now().isoformat(),
            api_response=api_response,
            ui_validation_result=ui_result,
            extracted_values=extracted_values,
            errors=errors if errors else None,
            execution_time=end_time - start_time
        )
        
        self.test_results.append(result)
        return result
    
    def _parse_gherkin_scenario(self, gherkin_text: str) -> GherkinScenario:
        """Parse Gherkin text into structured scenario"""
        return self.gherkin_generator._parse_gherkin_text(gherkin_text)
    
    async def _execute_ui_validation(
        self,
        config: UIValidationConfig,
        extracted_values: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute UI validation using browser agent"""
        try:
            # Create browser and controller
            browser = CustomBrowser(config=self.browser_config)
            controller = Controller()
            
            # Create agent
            llm = get_llm_model(
                self.llm_provider,
                model_name=self.model_name,
                api_key=self.api_key,
                base_url=self.base_url,
                temperature=0.0
            )
            agent = Agent(
                task="",
                llm=llm,
                browser=browser,
                controller=controller
            )
            
            # Build validation task
            task = f"Navigate to {config.url} and validate the following:\n"
            for step in config.validation_steps:
                # Replace placeholders with extracted values
                formatted_step = step
                for key, value in extracted_values.items():
                    formatted_step = formatted_step.replace(f"{{{key}}}", str(value))
                task += f"- {formatted_step}\n"
            
            agent.task = task
            
            # Execute validation
            history = await agent.run()
            
            # Analyze results using LLM
            validation_result = await self._analyze_ui_validation(history, config.expected_values, extracted_values)
            
            return validation_result
            
        except Exception as e:
            return {
                'success': False,
                'errors': [f"UI validation failed: {str(e)}"]
            }
    
    async def _analyze_ui_validation(
        self,
        history: Any,
        expected_values: Dict[str, Any],
        extracted_values: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze UI validation results using LLM"""
        llm = get_llm_model(
            self.llm_provider,
            model_name=self.model_name,
            api_key=self.api_key,
            base_url=self.base_url,
            temperature=0.0
        )
        
        system_prompt = """You are analyzing UI validation results.
Determine if the UI validation was successful by checking if the extracted API values
match what was displayed/validated in the UI.
Return a JSON with: {"success": true/false, "details": "explanation", "errors": []}"""
        
        user_message = f"""
API Extracted Values:
{json.dumps(extracted_values, indent=2)}

Expected Values in UI:
{json.dumps(expected_values, indent=2)}

Agent Execution History:
{str(history)[-2000:]}  # Last 2000 chars

Did the UI validation succeed?"""
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_message)
        ]
        
        response = await llm.ainvoke(messages)
        
        try:
            # Extract JSON from response
            content = response.content
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return {
                    'success': 'success' in content.lower(),
                    'details': content,
                    'errors': []
                }
        except:
            return {
                'success': False,
                'details': 'Failed to parse validation result',
                'errors': ['Failed to parse LLM response']
            }
    
    def get_test_results(self) -> List[Dict[str, Any]]:
        """Get all test results"""
        return [asdict(result) for result in self.test_results]
    
    def save_test_results(self, output_path: str):
        """Save test results to file"""
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(self.get_test_results(), f, indent=2)
    
    def generate_test_report(self) -> str:
        """Generate a formatted test report"""
        report = "# API Testing Report\n\n"
        report += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r.success)
        failed_tests = total_tests - passed_tests
        
        report += f"## Summary\n"
        report += f"- Total Tests: {total_tests}\n"
        report += f"- Passed: {passed_tests}\n"
        report += f"- Failed: {failed_tests}\n"
        report += f"- Success Rate: {(passed_tests/total_tests*100) if total_tests > 0 else 0:.1f}%\n\n"
        
        report += "## Test Results\n\n"
        
        for i, result in enumerate(self.test_results, 1):
            status = "✅ PASSED" if result.success else "❌ FAILED"
            report += f"### Test {i}: {result.scenario_name} {status}\n"
            report += f"- Execution Time: {result.execution_time:.2f}s\n"
            report += f"- Timestamp: {result.timestamp}\n"
            
            if result.api_response:
                report += f"- API Status: {result.api_response.get('status_code', 'N/A')}\n"
            
            if result.extracted_values:
                report += f"- Extracted Values: {json.dumps(result.extracted_values, indent=2)}\n"
            
            if result.errors:
                report += f"- Errors:\n"
                for error in result.errors:
                    report += f"  - {error}\n"
            
            report += "\n"
        
        return report
    
    async def execute_gherkin_scenario(self, gherkin_text: str) -> TestResult:
        """
        Execute a Gherkin scenario by parsing it and making the appropriate API call.
        This is a simplified version that extracts API details from Gherkin steps.
        """
        import time
        from enum import Enum
        
        class TestStatus(Enum):
            PASSED = "passed"
            FAILED = "failed"
            SKIPPED = "skipped"
        
        start_time = time.time()
        
        try:
            # Extract API details from Gherkin
            api_url = None
            method = "GET"
            expected_status = 200
            
            # Parse Gherkin text
            lines = gherkin_text.strip().split('\n')
            scenario_name = "API Test"
            
            for line in lines:
                line = line.strip()
                
                # Extract scenario name
                if line.startswith('Scenario:'):
                    scenario_name = line.replace('Scenario:', '').strip()
                
                # Extract API endpoint URL
                if 'endpoint is' in line.lower() or 'url is' in line.lower():
                    # Extract URL from quotes
                    url_match = re.search(r'"([^"]+)"', line)
                    if url_match:
                        api_url = url_match.group(1)
                
                # Extract HTTP method
                if 'GET request' in line:
                    method = 'GET'
                elif 'POST request' in line:
                    method = 'POST'
                elif 'PUT request' in line:
                    method = 'PUT'
                elif 'DELETE request' in line:
                    method = 'DELETE'
                
                # Extract expected status code
                if 'status code should be' in line.lower():
                    status_match = re.search(r'\d+', line)
                    if status_match:
                        expected_status = int(status_match.group())
            
            if not api_url:
                return TestResult(
                    success=False,
                    scenario_name=scenario_name,
                    timestamp=datetime.now().isoformat(),
                    errors=["Could not extract API URL from Gherkin scenario"],
                    execution_time=time.time() - start_time
                )
            
            # Make the API call
            try:
                response = requests.request(
                    method=method,
                    url=api_url,
                    headers={'Content-Type': 'application/json'},
                    timeout=30
                )
                
                response_time_ms = response.elapsed.total_seconds() * 1000
                
                # Parse response
                try:
                    response_data = response.json()
                except:
                    response_data = {"text": response.text}
                
                # Validate status code
                status_ok = response.status_code == expected_status
                
                # Check validations from Gherkin
                validation_errors = []
                extracted_values = {}
                
                if not status_ok:
                    validation_errors.append(
                        f"Expected status {expected_status}, got {response.status_code}"
                    )
                
                # Check for specific validations mentioned in Gherkin
                for line in lines:
                    line_lower = line.lower()
                    
                    if 'should be a json array' in line_lower or 'should be an array' in line_lower:
                        if not isinstance(response_data, list):
                            validation_errors.append("Response is not a JSON array")
                    
                    if 'should contain' in line_lower:
                        # Extract what should be contained
                        content_match = re.search(r'should contain.*?"([^"]+)"', line, re.IGNORECASE)
                        if content_match:
                            search_value = content_match.group(1)
                            response_str = json.dumps(response_data)
                            if search_value not in response_str:
                                validation_errors.append(f"Response does not contain '{search_value}'")
                            else:
                                extracted_values[f"contains_{search_value.replace(' ', '_')}"] = True
                
                success = len(validation_errors) == 0 and status_ok
                
                # Create result with the correct TestResult structure
                result = TestResult(
                    success=success,
                    scenario_name=scenario_name,
                    timestamp=datetime.now().isoformat(),
                    api_response={
                        'status_code': response.status_code,
                        'response_time_ms': response_time_ms,
                        'data': response_data
                    },
                    extracted_values=extracted_values,
                    errors=validation_errors if validation_errors else None,
                    execution_time=time.time() - start_time
                )
                
                # Store result
                self.test_results.append(result)
                
                # Convert to the expected format with all fields
                from dataclasses import dataclass
                from enum import Enum
                
                @dataclass
                class FormattedTestResult:
                    status: Any
                    execution_time: float
                    timestamp: datetime
                    api_endpoint: str
                    status_code: int
                    response_time_ms: float
                    extracted_values: Dict[str, Any]
                    validation_errors: List[str]
                    message: str
                    response_data: Any  # Full response data
                
                class Status(Enum):
                    PASSED = "passed"
                    FAILED = "failed"
                    SKIPPED = "skipped"
                
                formatted_result = FormattedTestResult(
                    status=Status.PASSED if success else Status.FAILED,
                    execution_time=time.time() - start_time,
                    timestamp=datetime.now(),
                    api_endpoint=api_url,
                    status_code=response.status_code,
                    response_time_ms=response_time_ms,
                    extracted_values=extracted_values,
                    validation_errors=validation_errors,
                    message="Test passed successfully" if success else f"Test failed: {', '.join(validation_errors)}",
                    response_data=response_data  # Include full response
                )
                
                return formatted_result
                
            except requests.RequestException as e:
                return TestResult(
                    success=False,
                    scenario_name=scenario_name,
                    timestamp=datetime.now().isoformat(),
                    errors=[f"API request failed: {str(e)}"],
                    execution_time=time.time() - start_time
                )
        
        except Exception as e:
            return TestResult(
                success=False,
                scenario_name="Error",
                timestamp=datetime.now().isoformat(),
                errors=[f"Execution error: {str(e)}"],
                execution_time=time.time() - start_time
            )
