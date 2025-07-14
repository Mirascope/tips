---
tip_number: 37
tip_name: "Sandboxed Code Agents"
categories: ["security", "testing", "architecture"]
x_link: "https://x.com/skylar_b_payne/status/1943007353424474204"
linkedin_link: "https://www.linkedin.com/posts/skylarbpayne_5-seconds-per-step-100-steps-this-agent-activity-7348773299218223105-rSpW?utm_source=share&utm_medium=member_desktop&rcm=ACoAABKpCf4BI_Yx2u7h66sgi5z1NF3aEYFHgps"
---

## Effective AI Engineering #37: Sandboxed Code Agents

**Why give your AI agent a single screwdriver when it could have an entire workshop?** Tool-calling agents are limited by the specific functions you've pre-defined, but a code agent can write custom logic to solve any problem.

The catch? A non-sandboxed code agent has the same risks as uncontrolled tool calling, except with a vastly larger attack surface. Instead of being constrained to your predefined tools, the AI can write code to do literally anything - access files, make network calls, modify system settings, or worse.

### The Problem

Many developers stick with tool-calling agents because they feel safer, but this severely limits what their AI can accomplish. This creates challenges that aren't immediately obvious:

```python
# BEFORE: Limited tool-calling agent
from mirascope import llm, prompt_template
from typing import List

def calculate_average(numbers: List[float]) -> float:
    """Calculate average of a list of numbers"""
    return sum(numbers) / len(numbers) if numbers else 0

def find_max_value(numbers: List[float]) -> float:
    """Find maximum value in a list"""
    return max(numbers) if numbers else 0

def calculate_growth_rate(old_value: float, new_value: float) -> float:
    """Calculate percentage growth rate"""
    if old_value == 0:
        return 0
    return ((new_value - old_value) / old_value) * 100

@llm.call(provider="anthropic", model="claude-3-5-sonnet-20241022", tools=[calculate_average, find_max_value, calculate_growth_rate])
@prompt_template("""
You are a data analysis assistant. Analyze this sales data: {sales_data}

Use the available tools to:
1. Calculate the average sales
2. Find the highest sales month  
3. Calculate month-over-month growth rates
4. Provide insights based on the analysis

Call the tools as needed and combine the results into a comprehensive analysis.
""")
def tool_calling_agent(sales_data: List[float]): ...

# Definition of `run_agent` is omitted for brevity - consult mirascope docs
run_agent(tool_calling_agent)("What is my MoM growth rate?")
```

**Why this approach falls short:**

- **Rigid Limitations:** Can only perform operations you've pre-defined as tools
- **Multiple Round Trips:** Complex analysis requires multiple LLM calls and tool orchestration
- **No Complex Logic:** Can't perform sophisticated data transformations or statistical analysis beyond basic tools

### The Solution: E2B Sandboxed Code Agents

A better approach is to let your AI generate complete code solutions and execute them safely in E2B's cloud sandboxes. This pattern provides the flexibility of code agents while maintaining security through proper isolation.

```python
# AFTER: Sandboxed code agent with E2B
from mirascope import llm, prompt_template
from e2b_code_interpreter import Sandbox
from typing import List

def run_sandboxed_code(code: str) -> str:
    """Run arbitrary python code in a sandbox"""
    sandbox = Sandbox()
    execution = sandbox.run_code(code)
    return execution.logs

@llm.call(provider="anthropic", model="claude-3-5-sonnet-20241022", tools=[run_sandboxed_code])
@prompt_template("""
Generate Python code to analyze this sales data: {sales_data}

Your code should:
1. Calculate comprehensive statistics (average, max, min, standard deviation)
2. Calculate month-over-month growth rates
3. Identify trends and patterns in the data
4. Print clear, formatted results

Write complete, executable Python code that handles all analysis in one script.
Run the code via the sandbox tool.
""")
def generate_analysis_code(sales_data: List[float]): ...

# Definition of `run_agent` omitted for brevity
run_agent(do_analysis)(sales_data)
```

**Why this approach works better:**

- **Complete Flexibility:** AI can write custom logic using the full Python ecosystem instead of being limited to predefined tools
- **Single Round Trip:** One LLM call generates complete analysis vs multiple calls for each tool operation  
- **Safe Execution:** E2B sandboxes isolate code execution from your host system while providing full programming capabilities

### The Takeaway

Sandboxed code agents with E2B give you the best of both worlds: the unlimited flexibility of letting AI write custom code and the safety of isolated execution. This pattern replaces rigid tool-calling workflows with intelligent code generation that can solve complex problems in one shot.

---
*Part of the "Effective AI Engineering" series - practical tips for building better applications with AI components.*