## Effective AI Engineering #36: Human Approval for Risky Tools

**Did your AI agent just delete your production database?** Tool-enabled AI can execute powerful actions, but without proper guardrails, one hallucination or misinterpretation can cause irreversible damage.

AI agents with tool access can perform incredibly useful automation, but they lack human judgment about risk and context. A simple file cleanup task could become data loss if the AI misunderstands scope or encounters unexpected edge cases.

### The Problem

Many developers give AI agents direct access to powerful tools without human oversight. This creates challenges that aren't immediately obvious:

```python
# BEFORE: Unrestricted tool access
from mirascope.core import llm
import lilypad
import os
import subprocess
from typing import List

@llm.call(provider="openai", model="gpt-4o-mini")
def ai_system_agent(user_request: str) -> str:
    return f"""
    You have access to these system tools:
    - file_delete(path): Delete files or directories
    - run_command(cmd): Execute shell commands
    - database_query(sql): Run SQL queries
    
    User request: {user_request}
    
    Use the appropriate tools to complete this task.
    """

def file_delete(path: str) -> str:
    """Delete files - no safety checks"""
    try:
        if os.path.isdir(path):
            os.rmdir(path)
        else:
            os.remove(path)
        return f"Deleted: {path}"
    except Exception as e:
        return f"Error: {e}"

def run_command(cmd: str) -> str:
    """Execute shell commands - dangerous without limits"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return f"Output: {result.stdout}\nError: {result.stderr}"
    except Exception as e:
        return f"Error: {e}"

def database_query(sql: str) -> str:
    """Execute SQL - could be destructive"""
    # Simulated database operation
    return f"Would execute: {sql}"

# AI has unrestricted access to dangerous operations
user_requests = [
    "Clean up old files in /tmp",
    "Free up disk space",
    "Remove unused data",
    "Optimize the database"
]

for request in user_requests:
    # No human oversight - AI could misinterpret and cause damage
    response = ai_system_agent(request)
    print(f"AI Response: {response}")
```

**Why this approach falls short:**

- **No Risk Assessment:** AI can't distinguish between safe operations and potentially destructive ones
- **Context Blindness:** Lacks understanding of business impact, data importance, or operational timing
- **Irreversible Actions:** Once executed, destructive operations can't be undone

### The Solution: Risk-Based Human Approval Gates

A better approach is to classify tool operations by risk level and require human approval for dangerous actions. This pattern maintains AI efficiency for safe operations while protecting against catastrophic mistakes.

```python
# AFTER: Human approval gates for risky operations
from mirascope.core import anthropic, prompt_template
from pydantic import BaseModel
import lilypad
import os
import subprocess
from typing import List, Optional
from enum import Enum
from dataclasses import dataclass

class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class ToolCall:
    tool_name: str
    parameters: dict
    risk_level: RiskLevel
    risk_explanation: str
    estimated_impact: str

class RiskAssessment(BaseModel):
    risk_level: RiskLevel
    reasoning: str
    potential_impacts: List[str]
    mitigation_suggestions: List[str]

class HumanApprovalRequired(Exception):
    def __init__(self, tool_call: ToolCall, assessment: RiskAssessment):
        self.tool_call = tool_call
        self.assessment = assessment
        super().__init__(f"Human approval required for {tool_call.tool_name}")

class ApprovalGate:
    def __init__(self):
        # Define risk levels for different tools and patterns
        self.tool_risk_rules = {
            "file_delete": self._assess_file_delete_risk,
            "run_command": self._assess_command_risk,
            "database_query": self._assess_database_risk,
        }
        
        # High-risk patterns
        self.critical_patterns = [
            r"rm -rf",
            r"DROP TABLE",
            r"DELETE FROM.*WHERE.*",
            r"FORMAT",
            r"mkfs",
        ]
        
        self.high_risk_patterns = [
            r"sudo",
            r"chmod 777",
            r"*.sh",
            r"UPDATE.*SET",
            r"DELETE",
        ]
    
    @lilypad.trace()
    @llm.call("claude-3-5-sonnet-20241022", response_model=RiskAssessment)
    def ai_risk_assessment(self, tool_name: str, parameters: dict, context: str) -> RiskAssessment:
        return f"""
        Assess the risk level of this tool operation:
        
        Tool: {tool_name}
        Parameters: {parameters}
        Context: {context}
        
        Consider:
        1. Potential for data loss or system damage
        2. Reversibility of the operation
        3. Scope and impact of changes
        4. Business-critical systems affected
        
        Classify risk as: LOW, MEDIUM, HIGH, or CRITICAL
        """
    
    def _assess_file_delete_risk(self, parameters: dict) -> RiskLevel:
        path = parameters.get("path", "")
        
        # Critical paths that should never be deleted
        critical_paths = ["/", "/usr", "/etc", "/var", "/home"]
        if any(path.startswith(critical) for critical in critical_paths):
            return RiskLevel.CRITICAL
        
        # Production or important directories
        high_risk_paths = ["prod", "production", "main", "master", "backup"]
        if any(term in path.lower() for term in high_risk_paths):
            return RiskLevel.HIGH
        
        # Temporary or cache directories
        if any(term in path.lower() for term in ["tmp", "temp", "cache", "log"]):
            return RiskLevel.LOW
        
        return RiskLevel.MEDIUM
    
    def _assess_command_risk(self, parameters: dict) -> RiskLevel:
        cmd = parameters.get("cmd", "").lower()
        
        # Check for critical patterns
        for pattern in self.critical_patterns:
            if pattern.lower() in cmd:
                return RiskLevel.CRITICAL
        
        # Check for high-risk patterns  
        for pattern in self.high_risk_patterns:
            if pattern.lower() in cmd:
                return RiskLevel.HIGH
        
        # Safe read-only commands
        safe_commands = ["ls", "cat", "grep", "find", "ps", "top", "df"]
        if any(cmd.startswith(safe) for safe in safe_commands):
            return RiskLevel.LOW
        
        return RiskLevel.MEDIUM
    
    def _assess_database_risk(self, parameters: dict) -> RiskLevel:
        sql = parameters.get("sql", "").upper()
        
        # Destructive operations
        if any(op in sql for op in ["DROP", "DELETE", "TRUNCATE", "ALTER"]):
            return RiskLevel.HIGH
        
        # Data modification
        if any(op in sql for op in ["UPDATE", "INSERT"]):
            return RiskLevel.MEDIUM
        
        # Read-only queries
        if sql.strip().startswith("SELECT"):
            return RiskLevel.LOW
        
        return RiskLevel.MEDIUM
    
    @lilypad.trace()
    def evaluate_tool_call(self, tool_name: str, parameters: dict, context: str = "") -> ToolCall:
        # Get rule-based assessment
        rule_based_risk = RiskLevel.MEDIUM
        if tool_name in self.tool_risk_rules:
            rule_based_risk = self.tool_risk_rules[tool_name](parameters)
        
        # Get AI assessment for nuanced evaluation
        ai_assessment = self.ai_risk_assessment(tool_name, parameters, context)
        
        # Take the higher risk level
        final_risk = max(rule_based_risk, ai_assessment.risk_level, key=lambda x: list(RiskLevel).index(x))
        
        return ToolCall(
            tool_name=tool_name,
            parameters=parameters,
            risk_level=final_risk,
            risk_explanation=ai_assessment.reasoning,
            estimated_impact="; ".join(ai_assessment.potential_impacts)
        )

class SafeToolExecutor:
    def __init__(self):
        self.approval_gate = ApprovalGate()
        self.pending_approvals = {}
    
    def request_human_approval(self, tool_call: ToolCall, assessment: RiskAssessment) -> bool:
        """Simulate human approval process"""
        print(f"\n🚨 HUMAN APPROVAL REQUIRED 🚨")
        print(f"Tool: {tool_call.tool_name}")
        print(f"Parameters: {tool_call.parameters}")
        print(f"Risk Level: {tool_call.risk_level.value.upper()}")
        print(f"Reasoning: {tool_call.risk_explanation}")
        print(f"Potential Impacts: {tool_call.estimated_impact}")
        print(f"Mitigation: {assessment.mitigation_suggestions}")
        
        # In real implementation, this would:
        # - Send notification to human operators
        # - Create approval ticket in workflow system
        # - Wait for human decision
        
        approval = input("Approve this operation? (yes/no): ").lower().strip()
        return approval in ["yes", "y"]
    
    @lilypad.trace()
    def safe_execute_tool(self, tool_name: str, parameters: dict, context: str = "") -> str:
        # Assess risk level
        tool_call = self.approval_gate.evaluate_tool_call(tool_name, parameters, context)
        
        # Check if human approval is needed
        if tool_call.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            assessment = self.approval_gate.ai_risk_assessment(tool_name, parameters, context)
            
            if not self.request_human_approval(tool_call, assessment):
                return f"❌ Operation denied by human operator: {tool_name}"
            
            print("✅ Operation approved by human operator")
        
        # Execute the tool (simulated)
        print(f"🔧 Executing {tool_name} with parameters: {parameters}")
        
        # Simulate actual tool execution
        if tool_name == "file_delete":
            return f"Deleted: {parameters['path']}"
        elif tool_name == "run_command":
            return f"Executed: {parameters['cmd']}"
        elif tool_name == "database_query":
            return f"Query result: {parameters['sql']}"
        
        return "Operation completed"

@lilypad.trace()
@llm.call(provider="openai", model="gpt-4o-mini")
def plan_system_task(user_request: str) -> str:
    return f"""
    You are a system administrator AI with access to tools.
    For the user request: {user_request}
    
    Available tools:
    - file_delete(path): Delete files/directories  
    - run_command(cmd): Execute shell commands
    - database_query(sql): Run SQL queries
    
    Plan your approach and specify which tools to use with exact parameters.
    """

def demo_approval_gates():
    executor = SafeToolExecutor()
    
    # Test different risk levels
    test_operations = [
        ("file_delete", {"path": "/tmp/cache.log"}, "Cleaning temporary files"),
        ("file_delete", {"path": "/home/user/important.db"}, "User requested cleanup"),
        ("run_command", {"cmd": "ls -la"}, "List directory contents"),
        ("run_command", {"cmd": "rm -rf /var/log/*"}, "Free up disk space"),
        ("database_query", {"sql": "SELECT * FROM users LIMIT 10"}, "Check user data"),
        ("database_query", {"sql": "DELETE FROM old_logs WHERE date < '2023-01-01'"}, "Cleanup old data"),
    ]
    
    for tool_name, params, context in test_operations:
        print(f"\n{'='*60}")
        print(f"Testing: {tool_name} - {context}")
        print('='*60)
        
        result = executor.safe_execute_tool(tool_name, params, context)
        print(f"Result: {result}")

if __name__ == "__main__":
    demo_approval_gates()
```

**Why this approach works better:**

- **Risk-Proportionate Control:** Low-risk operations execute immediately while dangerous ones require approval
- **Human Context:** Operators can consider business impact, timing, and circumstances AI cannot evaluate
- **Audit Trail:** All high-risk operations have documented human approval for compliance

### The Takeaway

Human approval gates for risky tool operations prevent AI agents from causing irreversible damage while maintaining automation efficiency for safe tasks. This pattern balances AI capability with human oversight where it matters most.

---
*Part of the "Effective AI Engineering" series - practical tips for building better applications with AI components.*