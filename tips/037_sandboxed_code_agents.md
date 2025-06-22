## Effective AI Engineering #37: Sandboxed Code Agents

**Are you tired of slow tool-calling loops for complex multi-step tasks?** Your AI agent calls one tool, waits for your response, calls another tool, waits again - turning a 30-second script into a 5-minute conversation.

Code agents can generate and execute complete workflows in one shot, dramatically reducing latency and token costs. But running AI-generated code on your system without isolation is like giving a stranger root access to your servers.

### The Problem

Many developers either avoid code agents due to security concerns or run them without proper isolation. This creates challenges that aren't immediately obvious:

```python
# BEFORE: Slow tool-calling loops or unsafe code execution
from mirascope.core import llm
import lilypad
import subprocess
import os

@llm.call(provider="openai", model="gpt-4o-mini")
def tool_based_agent(user_request: str) -> str:
    return f"""
    You have access to these tools:
    - run_shell_command(cmd): Execute shell commands
    - read_file(path): Read file contents  
    - write_file(path, content): Write content to file
    
    User request: {user_request}
    
    Complete this task step by step using the available tools.
    """

def run_shell_command(cmd: str) -> str:
    """Dangerous: executes directly on host system"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return f"Output: {result.stdout}\nError: {result.stderr}"
    except Exception as e:
        return f"Error: {e}"

# Alternative: Multi-turn tool calling (slow and expensive)
@llm.call(provider="openai", model="gpt-4o-mini")
def unsafe_code_agent(user_request: str) -> str:
    return f"""
    Generate Python code to complete this task: {user_request}
    
    The code should be complete and executable.
    """

def execute_ai_code_unsafely(code: str) -> str:
    """Extremely dangerous: executes AI code directly"""
    try:
        exec(code)  # Never do this!
        return "Code executed"
    except Exception as e:
        return f"Error: {e}"

# Both approaches have major issues:
# 1. Tool calling: Slow, expensive, lots of round trips
# 2. Direct exec: Fast but completely unsafe
```

**Why this approach falls short:**

- **Security Risks:** AI-generated code could access sensitive files, make network calls, or damage the system
- **Latency Issues:** Tool-calling loops require multiple LLM round trips for complex tasks
- **Limited Capability:** Tool-based agents can't perform complex logic or state management

### The Solution: Docker-Sandboxed Code Agents

A better approach is to execute AI-generated code in isolated Docker containers with restricted capabilities. This pattern provides the speed and flexibility of code agents while maintaining security through containerization.

```python
# AFTER: Secure code agents with Docker sandboxing
from mirascope.core import anthropic, prompt_template
import lilypad
import docker
import tempfile
import os
import json
from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class SandboxResult:
    success: bool
    output: str
    error: Optional[str] = None
    execution_time: float = 0.0
    resource_usage: Dict[str, Any] = None

class SecureCodeSandbox:
    def __init__(self):
        self.client = docker.from_env()
        self.base_image = "python:3.11-slim"
        self.container_limits = {
            "mem_limit": "128m",  # Limit memory
            "cpu_period": 100000,
            "cpu_quota": 50000,   # Limit CPU to 50%
            "network_mode": "none",  # No network access
        }
    
    def create_restricted_dockerfile(self) -> str:
        """Create a minimal Python environment with restricted capabilities"""
        return """
FROM python:3.11-slim

# Remove potentially dangerous tools
RUN apt-get update && apt-get remove -y --purge curl wget && \
    apt-get autoremove -y && apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -s /bin/bash sandbox
USER sandbox
WORKDIR /home/sandbox

# Install allowed packages only
RUN pip install --user pandas numpy matplotlib requests-cache

# Set up restricted environment
ENV PATH="/home/sandbox/.local/bin:$PATH"
"""

    @lilypad.trace()
    def execute_code_safely(self, code: str, timeout: int = 30) -> SandboxResult:
        """Execute Python code in a secure Docker container"""
        
        # Create temporary directory for code
        with tempfile.TemporaryDirectory() as temp_dir:
            code_file = os.path.join(temp_dir, "agent_code.py")
            
            # Write code to file
            with open(code_file, "w") as f:
                f.write(code)
            
            try:
                # Create and run container
                container = self.client.containers.run(
                    self.base_image,
                    command=f"python /code/agent_code.py",
                    volumes={temp_dir: {"bind": "/code", "mode": "ro"}},
                    remove=True,
                    detach=False,
                    stdout=True,
                    stderr=True,
                    timeout=timeout,
                    **self.container_limits
                )
                
                output = container.decode('utf-8')
                
                return SandboxResult(
                    success=True,
                    output=output,
                    execution_time=timeout  # Simplified
                )
                
            except docker.errors.ContainerError as e:
                return SandboxResult(
                    success=False,
                    output="",
                    error=f"Container error: {e.stderr.decode('utf-8')}"
                )
            except Exception as e:
                return SandboxResult(
                    success=False,
                    output="",
                    error=f"Execution error: {str(e)}"
                )

@lilypad.trace()
@llm.call(provider="openai", model="gpt-4o-mini")
def generate_sandbox_code(task_description: str, available_data: str = "None") -> str:
    return f"""
    Generate Python code to complete this task: {task_description}
    
    Requirements:
    - Complete, executable Python script
    - Use only standard library and: pandas, numpy, matplotlib
    - No file system access outside current directory
    - No network requests
    - Include error handling
    - Print results clearly
    
    Task: {task_description}
    Available data: {available_data}
    """

class CodeAgentWorkflow:
    def __init__(self):
        self.sandbox = SecureCodeSandbox()
        self.max_retries = 2
    
    @lilypad.trace()
    def execute_task(self, task_description: str, context: Dict[str, Any] = None) -> str:
        """Execute a task using sandboxed code generation"""
        
        # Prepare context information
        available_data = json.dumps(context) if context else "None"
        
        for attempt in range(self.max_retries + 1):
            print(f"\n=== Attempt {attempt + 1} ===")
            
            # Generate code
            code = generate_sandbox_code(task_description, available_data)
            print(f"Generated code:\n{code}")
            
            # Execute safely in sandbox
            result = self.sandbox.execute_code_safely(code)
            
            if result.success:
                print(f"✅ Execution successful")
                print(f"Output: {result.output}")
                return result.output
            else:
                print(f"❌ Execution failed: {result.error}")
                
                if attempt < self.max_retries:
                    # Could use error feedback to improve code generation
                    print("Retrying with error feedback...")
                else:
                    return f"Failed to complete task after {self.max_retries + 1} attempts. Last error: {result.error}"
        
        return "Task execution failed"

# Advanced: Persistent sandbox with state management
class StatefulCodeSandbox(SecureCodeSandbox):
    def __init__(self):
        super().__init__()
        self.persistent_container = None
        self.session_state = {}
    
    def start_session(self) -> str:
        """Start a persistent container for multi-step workflows"""
        try:
            self.persistent_container = self.client.containers.run(
                self.base_image,
                command="tail -f /dev/null",  # Keep container running
                detach=True,
                **self.container_limits
            )
            return f"Session started: {self.persistent_container.id[:12]}"
        except Exception as e:
            return f"Failed to start session: {e}"
    
    def execute_in_session(self, code: str) -> SandboxResult:
        """Execute code in persistent container maintaining state"""
        if not self.persistent_container:
            return SandboxResult(False, "", "No active session")
        
        try:
            # Execute code in running container
            exec_result = self.persistent_container.exec_run(
                f"python -c '{code}'",
                stdout=True,
                stderr=True
            )
            
            output = exec_result.output.decode('utf-8')
            
            return SandboxResult(
                success=exec_result.exit_code == 0,
                output=output,
                error=None if exec_result.exit_code == 0 else output
            )
            
        except Exception as e:
            return SandboxResult(False, "", f"Session execution error: {e}")
    
    def end_session(self):
        """Clean up persistent container"""
        if self.persistent_container:
            self.persistent_container.stop()
            self.persistent_container.remove()
            self.persistent_container = None

# Example usage demonstrating secure code agents
def demo_sandboxed_code_agents():
    agent = CodeAgentWorkflow()
    
    # Example: Data analysis task
    sample_data = {
        "sales_data": [100, 150, 200, 180, 220, 190, 250],
        "months": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul"]
    }
    
    tasks = [
        "Calculate the average sales and identify the month with highest sales",
        "Create a simple trend analysis showing growth rate month-over-month",
        "Generate a basic statistical summary of the sales data"
    ]
    
    for task in tasks:
        print(f"\n{'='*60}")
        print(f"Task: {task}")
        print('='*60)
        
        result = agent.execute_task(task, sample_data)
        print(f"Final Result: {result}")

# Performance comparison
def compare_approaches():
    """Compare tool-calling vs code agent approaches"""
    print("=== PERFORMANCE COMPARISON ===")
    print("Tool-calling approach:")
    print("  - 5+ LLM calls for complex tasks")
    print("  - High latency (multiple round trips)")
    print("  - Limited by available tools")
    print("  - Expensive token usage")
    
    print("\nSandboxed code agent:")
    print("  - 1 LLM call for code generation")
    print("  - Low latency (single round trip)")
    print("  - Full programming language flexibility")
    print("  - Secure execution environment")
    print("  - Cost-effective for complex workflows")

if __name__ == "__main__":
    print("🚨 Note: This demo requires Docker to be installed and running")
    print("Simulating sandboxed execution...")
    
    # Simulate the demo without actual Docker
    compare_approaches()
    
    # In real usage with Docker:
    # demo_sandboxed_code_agents()
```

**Why this approach works better:**

- **Security Through Isolation:** Docker containers prevent AI code from accessing host system resources
- **Performance Advantage:** Single code generation call replaces multiple tool-calling round trips
- **Enhanced Capability:** Full programming language access enables complex logic and state management

### The Takeaway

Sandboxed code agents combine the flexibility of full programming environments with security through containerization, enabling fast and capable AI automation without system risks. This pattern unlocks advanced AI workflows while maintaining safety.

---
*Part of the "Effective AI Engineering" series - practical tips for building better applications with AI components.*