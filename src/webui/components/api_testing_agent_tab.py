"""
API Testing Agent Tab - Gherkin Generator & Validator Only
"""
import gradio as gr
import asyncio
import json
import logging
import re
from typing import Dict, Any, Optional
from datetime import datetime

from src.webui.webui_manager import WebuiManager
from src.agent.api_testing.api_testing_agent import APITestingAgent

logger = logging.getLogger(__name__)


def create_api_testing_agent_tab(webui_manager: WebuiManager):
    """Creates the simplified API Testing tab with only Gherkin generator and validator"""
    
    # Get references to Agent Settings components
    def get_agent_setting_component(key):
        """Helper to get agent settings component"""
        comp_id = f"agent_settings.{key}"
        return webui_manager.id_to_component.get(comp_id)
    
    with gr.Column():
        gr.Markdown("## 🔌 API Testing: Gherkin Generator & Validator")
        gr.Markdown("Generate BDD Gherkin scenarios from natural language and validate API responses automatically")
        
        # ===== Main Interface =====
        with gr.Group():
            gr.Markdown("### ✍️ Generate Gherkin Scenario")
            
            gherkin_prompt = gr.Textbox(
                label="Describe Your API Test",
                placeholder="Example: Test GET https://jsonplaceholder.typicode.com/users, verify status 200, and validate that user 'Leanne Graham' exists in the response",
                lines=4,
                info="Describe what you want to test in plain English - include API URL, method, and expected results"
            )
            
            context_input = gr.Textbox(
                label="Additional Context (Optional)",
                placeholder="API documentation, authentication details, expected response format, etc.",
                lines=2
            )
            
            generate_btn = gr.Button(
                "🤖 Generate Gherkin Scenario",
                variant="primary",
                size="lg"
            )
            
            generated_gherkin = gr.Textbox(
                label="Generated Gherkin Scenario",
                lines=15,
                interactive=True,
                info="AI-generated BDD scenario - you can edit this before execution"
            )
            
            gr.Markdown("---")
            gr.Markdown("### ✅ Validate & Execute")
            
            with gr.Row():
                validate_btn = gr.Button(
                    "🔍 Validate Gherkin Syntax",
                    variant="secondary"
                )
                execute_btn = gr.Button(
                    "🚀 Execute Test",
                    variant="primary",
                    size="lg"
                )
                clear_btn = gr.Button(
                    "🗑️ Clear All",
                    variant="stop"
                )
            
            status_output = gr.Textbox(
                label="Status",
                interactive=False,
                lines=2
            )
            
            test_results = gr.Code(
                label="Test Results",
                language="json",
                lines=20,
                interactive=False
            )
            
            gr.Markdown("""
            ---
            ### 📖 How It Works
            1. **Describe**: Write what you want to test in natural language (include API URL!)
            2. **Generate**: AI creates a proper Gherkin BDD scenario
            3. **Validate**: Check if the Gherkin syntax is correct (optional)
            4. **Execute**: Run the test - the agent extracts API details from Gherkin and validates the response
            
            #### Example Input:
            ```
            Test the JSONPlaceholder users API at https://jsonplaceholder.typicode.com/users
            Send a GET request and verify:
            - Status code is 200
            - Response is a JSON array
            - Contains a user named "Leanne Graham"
            ```
            
            #### Generated Gherkin Will Be:
            ```gherkin
            Feature: Users API Testing
            
            Scenario: Validate users endpoint
              Given the API endpoint is "https://jsonplaceholder.typicode.com/users"
              When I send a GET request
              Then the response status code should be 200
              Then the response should be a JSON array
              Then the response should contain a user with name "Leanne Graham"
            ```
            """)
        
        # ===== Event Handlers =====
        
        async def generate_gherkin_handler(prompt: str, context: str, 
                                          llm_provider: str, model_name: str,
                                          api_key: str, base_url: str):
            """Generate Gherkin scenario from natural language"""
            try:
                if not prompt or not prompt.strip():
                    return "❌ Please provide a test description"
                
                if not llm_provider or not model_name:
                    return "❌ Please configure LLM settings in Agent Settings tab first"
                
                if not api_key or not api_key.strip():
                    return "❌ Please set API key in Agent Settings tab"
                
                # Create agent with settings
                agent = APITestingAgent(
                    llm_provider=llm_provider,
                    model_name=model_name,
                    api_key=api_key,
                    base_url=base_url if base_url else None
                )
                
                # Generate Gherkin
                gherkin = await agent.generate_gherkin_from_prompt(
                    prompt=prompt,
                    context=context if context else None
                )
                
                return gherkin
                
            except Exception as e:
                logger.error(f"Error generating Gherkin: {e}")
                return f"❌ Error: {str(e)}"
        
        def validate_gherkin_handler(gherkin_text: str):
            """Validate Gherkin syntax"""
            try:
                if not gherkin_text or not gherkin_text.strip():
                    return "❌ No Gherkin scenario to validate"
                
                # Basic Gherkin validation
                errors = []
                
                # Check for Feature
                if not re.search(r'^\s*Feature:', gherkin_text, re.MULTILINE):
                    errors.append("Missing 'Feature:' declaration")
                
                # Check for Scenario
                if not re.search(r'^\s*Scenario:', gherkin_text, re.MULTILINE):
                    errors.append("Missing 'Scenario:' declaration")
                
                # Check for steps
                step_keywords = ['Given', 'When', 'Then', 'And', 'But']
                has_steps = any(re.search(rf'^\s*{kw}\s+', gherkin_text, re.MULTILINE) 
                               for kw in step_keywords)
                if not has_steps:
                    errors.append("No test steps found (Given/When/Then)")
                
                if errors:
                    return f"❌ Validation failed:\n" + "\n".join(f"  • {err}" for err in errors)
                else:
                    return "✅ Gherkin syntax is valid!"
                
            except Exception as e:
                logger.error(f"Error validating Gherkin: {e}")
                return f"❌ Validation error: {str(e)}"
        
        async def execute_test_handler(gherkin_text: str,
                                       llm_provider: str, model_name: str,
                                       api_key: str, base_url: str):
            """Execute the Gherkin test"""
            try:
                if not gherkin_text or not gherkin_text.strip():
                    return "❌ No Gherkin scenario to execute", "{}"
                
                if not llm_provider or not model_name:
                    return "❌ Please configure LLM settings in Agent Settings tab", "{}"
                
                if not api_key or not api_key.strip():
                    return "❌ Please set API key in Agent Settings tab", "{}"
                
                # Create agent
                agent = APITestingAgent(
                    llm_provider=llm_provider,
                    model_name=model_name,
                    api_key=api_key,
                    base_url=base_url if base_url else None
                )
                
                # Execute the Gherkin scenario
                # The agent will parse the Gherkin and extract API details automatically
                result = await agent.execute_gherkin_scenario(gherkin_text)
                
                # Format results with full response at the top
                result_dict = {
                    "test_status": result.status.value,
                    "message": result.message,
                    "execution_time": f"{result.execution_time:.2f}s",
                    "api_endpoint": result.api_endpoint or "N/A",
                    "status_code": result.status_code,
                    "response_time_ms": result.response_time_ms,
                    "full_response": result.response_data,  # Full API response prominently displayed
                    "extracted_values": result.extracted_values,
                    "validation_errors": result.validation_errors,
                    "timestamp": result.timestamp.isoformat()
                }
                
                if result.status.value == "passed":
                    status_msg = f"✅ Test PASSED in {result.execution_time:.2f}s"
                elif result.status.value == "failed":
                    status_msg = f"❌ Test FAILED: {result.message}"
                else:
                    status_msg = f"⚠️ Test SKIPPED: {result.message}"
                
                return status_msg, json.dumps(result_dict, indent=2)
                
            except Exception as e:
                logger.error(f"Error executing test: {e}", exc_info=True)
                error_result = {
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
                return f"❌ Execution error: {str(e)}", json.dumps(error_result, indent=2)
        
        # Wire up the event handlers
        generate_btn.click(
            fn=lambda prompt, context, llm_prov, llm_model, llm_key, llm_url: 
                asyncio.run(generate_gherkin_handler(prompt, context, llm_prov, llm_model, llm_key, llm_url)),
            inputs=[
                gherkin_prompt,
                context_input,
                get_agent_setting_component("llm_provider"),
                get_agent_setting_component("llm_model_name"),
                get_agent_setting_component("llm_api_key"),
                get_agent_setting_component("llm_base_url")
            ],
            outputs=[generated_gherkin]
        )
        
        validate_btn.click(
            fn=validate_gherkin_handler,
            inputs=[generated_gherkin],
            outputs=[status_output]
        )
        
        execute_btn.click(
            fn=lambda gherkin, llm_prov, llm_model, llm_key, llm_url:
                asyncio.run(execute_test_handler(gherkin, llm_prov, llm_model, llm_key, llm_url)),
            inputs=[
                generated_gherkin,
                get_agent_setting_component("llm_provider"),
                get_agent_setting_component("llm_model_name"),
                get_agent_setting_component("llm_api_key"),
                get_agent_setting_component("llm_base_url")
            ],
            outputs=[status_output, test_results]
        )
