## Effective AI Engineering #37: Sandboxed Code Agents

**Why give your AI agent a single screwdriver when it could have an entire workshop?** Tool-calling agents are limited by the specific functions you've pre-defined, but a code agent can write custom logic to solve any problem.

The catch? A non-sandboxed code agent has the same risks as uncontrolled tool calling, except with a vastly larger attack surface. Instead of being constrained to your predefined tools, the AI can write code to do literally anything - access files, make network calls, modify system settings, or worse.

### The Problem

Many developers stick with tool-calling agents because they feel safer, but this severely limits what their AI can accomplish. This creates challenges that aren't immediately obvious:

```python
# BEFORE: Limited tool-calling agent
from mirascope.core import anthropic, prompt_template
import lilypad
from typing import List

class DataAnalysisTools:
    @staticmethod
    def calculate_average(numbers: List[float]) -> float:
        """Calculate average of a list of numbers"""
        return sum(numbers) / len(numbers) if numbers else 0
    
    @staticmethod
    def find_max_value(numbers: List[float]) -> float:
        """Find maximum value in a list"""
        return max(numbers) if numbers else 0
    
    @staticmethod
    def calculate_growth_rate(old_value: float, new_value: float) -> float:
        """Calculate percentage growth rate"""
        if old_value == 0:
            return 0
        return ((new_value - old_value) / old_value) * 100

@lilypad.trace()
@anthropic.call("claude-3-5-sonnet-20241022")
@prompt_template("""
You are a data analysis assistant. You have access to these tools:
- calculate_average(numbers): Calculate average of numbers
- find_max_value(numbers): Find maximum value
- calculate_growth_rate(old_value, new_value): Calculate growth rate

Analyze this sales data: {sales_data}

Use the available tools to:
1. Calculate the average sales
2. Find the highest sales month
3. Calculate month-over-month growth rates

You must call each tool separately and combine the results.
""")
def tool_calling_agent(sales_data: List[float]) -> str:
    pass

# This requires multiple LLM calls and tool orchestration
def analyze_with_tools(sales_data: List[float]):
    tools = DataAnalysisTools()
    
    # Step 1: Calculate average (LLM call + tool call)
    avg = tools.calculate_average(sales_data)
    
    # Step 2: Find max (another LLM call + tool call)  
    max_val = tools.find_max_value(sales_data)
    
    # Step 3: Calculate growth rates (multiple LLM calls)
    growth_rates = []
    for i in range(1, len(sales_data)):
        rate = tools.calculate_growth_rate(sales_data[i-1], sales_data[i])
        growth_rates.append(rate)
    
    # Step 4: Final analysis (another LLM call)
    return f"Average: {avg}, Max: {max_val}, Growth rates: {growth_rates}"
```

**Why this approach falls short:**

- **Rigid Limitations:** Can only perform operations you've pre-defined as tools
- **Multiple Round Trips:** Each analysis step requires separate LLM calls and tool orchestration
- **No Complex Logic:** Can't perform sophisticated data transformations or statistical analysis beyond basic tools

### The Solution: E2B Sandboxed Code Agents

A better approach is to let your AI generate complete code solutions and execute them safely in E2B's cloud sandboxes. This pattern provides the flexibility of code agents while maintaining security through proper isolation.

```python
# AFTER: Sandboxed code agent with E2B
from mirascope.core import anthropic, prompt_template
from e2b_code_interpreter import Sandbox
import lilypad
from typing import List, Dict, Any
import json

@lilypad.trace()
@anthropic.call("claude-3-5-sonnet-20241022")
@prompt_template("""
Generate Python code to analyze this sales data: {sales_data}

Your code should:
1. Calculate comprehensive statistics (average, max, min, standard deviation)
2. Identify trends and patterns in the data
3. Calculate month-over-month growth rates
4. Provide insights and recommendations
5. Print clear, formatted results

Write complete, executable Python code that handles all analysis in one script.
""")
def generate_analysis_code(sales_data: List[float]) -> str:
    pass

class SandboxedCodeAgent:
    def __init__(self):
        # E2B sandbox automatically handles isolation and cleanup
        self.sandbox = None
    
    @lilypad.trace()
    def analyze_data(self, sales_data: List[float]) -> str:
        """Execute complete data analysis using sandboxed code generation"""
        
        # Generate comprehensive analysis code
        analysis_code = generate_analysis_code(sales_data)
        
        # Execute safely in E2B sandbox
        with Sandbox() as sbx:  # Automatically manages sandbox lifecycle
            # Provide data to the sandbox
            data_setup = f"""
import json
sales_data = {sales_data}
months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul']
print("Data loaded successfully")
print(f"Sales data: {{sales_data}}")
"""
            
            # Set up the data
            setup_result = sbx.run_code(data_setup)
            print(f"Setup: {setup_result.logs}")
            
            # Run the analysis
            execution_result = sbx.run_code(analysis_code)
            
            if execution_result.error:
                return f"Analysis failed: {execution_result.error}"
            
            return execution_result.logs

# Comparison with tool-calling approach
def compare_analysis_approaches():
    """Compare tool-calling agent vs sandboxed code agent"""
    
    sample_data = [100, 150, 200, 180, 220, 190, 250]
    
    print("=== TOOL-CALLING AGENT ===")
    print("Multiple LLM calls required:")
    print("1. Call LLM to decide which tool to use first")
    print("2. Call calculate_average() tool")
    print("3. Call LLM to decide next step")
    print("4. Call find_max_value() tool")
    print("5. Call LLM for growth rate calculation strategy")
    print("6. Multiple calls to calculate_growth_rate() tool")
    print("7. Call LLM to synthesize final analysis")
    print("Result: 7+ LLM calls, limited by predefined tools")
    
    print("\n=== SANDBOXED CODE AGENT ===")
    agent = SandboxedCodeAgent()
    
    print("Single LLM call generates complete analysis:")
    result = agent.analyze_data(sample_data)
    print("Analysis Result:")
    print(result)

# Advanced: Multi-step workflow with persistent state
class PersistentSandboxAgent:
    def __init__(self):
        self.sandbox = Sandbox()  # Keep sandbox alive for session
    
    @lilypad.trace()
    def execute_workflow(self, tasks: List[str], initial_data: Dict[str, Any]) -> List[str]:
        """Execute multiple related tasks maintaining state between steps"""
        
        # Set up initial data in sandbox
        setup_code = f"""
import pandas as pd
import numpy as np
import json
from typing import Dict, Any

# Load initial data
data = {json.dumps(initial_data)}
print("Workflow initialized with data:", list(data.keys()))

# Helper functions for workflow
def save_result(step_name: str, result: Any):
    globals()[f'step_{step_name}_result'] = result
    print(f"Saved result for step: {step_name}")

def get_previous_result(step_name: str):
    return globals().get(f'step_{step_name}_result', None)
"""
        
        setup_result = self.sandbox.run_code(setup_code)
        print(f"Workflow setup: {setup_result.logs}")
        
        results = []
        
        for i, task in enumerate(tasks):
            # Generate code for this specific task
            task_code = self._generate_task_code(task, i)
            
            # Execute in persistent sandbox (maintains state)
            execution = self.sandbox.run_code(task_code)
            
            if execution.error:
                results.append(f"Task {i+1} failed: {execution.error}")
            else:
                results.append(execution.logs)
        
        return results
    
    @anthropic.call("claude-3-5-sonnet-20241022")
    @prompt_template("""
    Generate Python code for step {step_number} of a multi-step analysis workflow.
    
    Task: {task}
    
    You can use:
    - The 'data' variable (contains initial dataset)
    - save_result(step_name, result) to save results for later steps
    - get_previous_result(step_name) to access results from previous steps
    
    Generate complete code that:
    1. Performs the requested analysis
    2. Saves key results for future steps
    3. Prints clear output
    """)
    def _generate_task_code(self, task: str, step_number: int) -> str:
        pass
    
    def cleanup(self):
        """Clean up the sandbox when done"""
        if self.sandbox:
            # E2B handles cleanup automatically, but you can explicitly close
            pass

# Example usage
def demo_persistent_workflow():
    agent = PersistentSandboxAgent()
    
    sample_data = {
        "sales_data": [100, 150, 200, 180, 220, 190, 250, 280, 300],
        "months": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep"],
        "regions": ["North", "South", "East", "West", "Central"]
    }
    
    workflow_tasks = [
        "Perform comprehensive statistical analysis of sales data",
        "Identify seasonal patterns and trends using the statistical results",
        "Create forecasting model based on identified patterns",
        "Generate executive summary with actionable recommendations"
    ]
    
    print("=== MULTI-STEP SANDBOXED WORKFLOW ===")
    results = agent.execute_workflow(workflow_tasks, sample_data)
    
    for i, result in enumerate(results):
        print(f"\n--- Step {i+1} Result ---")
        print(result)
    
    agent.cleanup()

if __name__ == "__main__":
    print("🔒 Using E2B sandboxed execution - safe and secure!")
    
    # Simple comparison
    compare_analysis_approaches()
    
    # Advanced workflow
    print("\n" + "="*60)
    demo_persistent_workflow()
```

**Why this approach works better:**

- **Complete Flexibility:** AI can write custom logic using the full Python ecosystem instead of being limited to predefined tools
- **Single Round Trip:** One LLM call generates complete analysis vs multiple calls for each tool operation
- **Safe Execution:** E2B sandboxes isolate code execution from your host system while providing full programming capabilities

### The Takeaway

Sandboxed code agents with E2B give you the best of both worlds: the unlimited flexibility of letting AI write custom code and the safety of isolated execution. This pattern replaces rigid tool-calling workflows with intelligent code generation that can solve complex problems in one shot.

---
*Part of the "Effective AI Engineering" series - practical tips for building better applications with AI components.*