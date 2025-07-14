---
tip_number: 40
tip_name: "Graph-Based Agent Workflows"
categories: ["workflow", "architecture", "error-handling"]
x_link: ""
linkedin_link: ""
---

## Effective AI Engineering #040: Graph-Based Agent Workflows

**Are your agents making unpredictable decisions or getting stuck in loops?** Multi-step AI agents without structured workflows can spiral into unreliable behavior that breaks your application.

This becomes critical when your agents need to handle complex processes like customer support, data analysis, or document processing. Without clear workflow constraints, agents can make impossible transitions or repeat actions indefinitely.

### The Problem

Many developers build agents that can jump between any actions without constraints. This creates challenges that aren't immediately obvious:

```python
# BEFORE: Unconstrained agent decisions
from mirascope import llm, prompt_template

@llm.call(provider='openai', model='gpt-4o-mini')
@prompt_template("""
You are a support agent. You can:
1. Analyze the user's issue
2. Search for solutions
3. Provide recommendations
4. Escalate to human support

Handle this request: {user_request}
Choose your next action and execute it.
""")
def handle_support_request(user_request: str): ...

# Agent can jump between any actions unpredictably
# No guarantee of logical workflow progression
# Can get stuck repeating the same analysis
```

**Why this approach falls short:**

- **Unpredictable Flow:** Agents can transition between any actions, creating inconsistent behavior
- **Loop Vulnerabilities:** Without constraints, agents may repeat actions or get stuck
- **No Progress Tracking:** Difficult to monitor workflow progression or debug issues

### The Solution: PydanticAI Graph Workflows

A better approach is to use PydanticAI's graph functionality to create structured workflows with clear state transitions and progress tracking.

```python
# AFTER: Graph-based structured workflow
from pydantic_ai import Agent
from pydantic_ai.graph import Graph, BaseNode, GraphRunContext, End
from pydantic import BaseModel
from dataclasses import dataclass
from typing import Literal

class SupportState(BaseModel):
    user_request: str
    issue_analysis: str = ""
    solution_found: bool = False
    escalation_needed: bool = False

@dataclass
class AnalyzeIssue(BaseNode[SupportState]):
    async def run(self, ctx: GraphRunContext[SupportState]) -> 'SearchSolutions':
        agent = Agent(model='openai:gpt-4o-mini')
        
        analysis = await agent.run(
            f"Analyze this support request: {ctx.state.user_request}"
        )
        
        ctx.state.issue_analysis = analysis.data
        return SearchSolutions()

@dataclass
class SearchSolutions(BaseNode[SupportState]):
    async def run(self, ctx: GraphRunContext[SupportState]) -> 'ProvideRecommendation | EscalateToHuman':
        agent = Agent(model='openai:gpt-4o-mini')
        
        solution = await agent.run(
            f"Find solutions for: {ctx.state.issue_analysis}"
        )
        
        if "escalate" in solution.data.lower():
            ctx.state.escalation_needed = True
            return EscalateToHuman()
        else:
            ctx.state.solution_found = True
            return ProvideRecommendation(solution=solution.data)

@dataclass
class ProvideRecommendation(BaseNode[SupportState]):
    solution: str
    
    async def run(self, ctx: GraphRunContext[SupportState]) -> End[str]:
        return End(f"Solution: {self.solution}")

@dataclass
class EscalateToHuman(BaseNode[SupportState]):
    async def run(self, ctx: GraphRunContext[SupportState]) -> End[str]:
        return End("Escalated to human support team")

# Create the graph workflow
support_graph = Graph(
    nodes=[AnalyzeIssue, SearchSolutions, ProvideRecommendation, EscalateToHuman],
    start_node=AnalyzeIssue
)

async def handle_support_request_structured(user_request: str) -> str:
    state = SupportState(user_request=user_request)
    result = await support_graph.run(state)
    return result
```

**Why this approach works better:**

- **Structured Flow:** Graph defines clear progression from analysis to solution or escalation
- **State Tracking:** Workflow state is maintained and can be inspected at any point
- **Predictable Behavior:** Same inputs follow the same logical workflow path every time

### The Takeaway

Use graph-based workflows to structure agent decision-making into reliable, trackable processes. This approach ensures agents follow logical progressions and makes multi-step workflows debuggable and predictable.

---
*Part of the "Effective AI Engineering" series - practical tips for building better applications with AI components.*