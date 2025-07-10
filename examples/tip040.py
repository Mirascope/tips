#!/usr/bin/env python3
"""
Example for Tip 040: Graph-Based Agent Workflows

This example demonstrates how to use PydanticAI's graph functionality to create
structured, reliable agent workflows.
"""

import asyncio
from pydantic_ai import Agent
from pydantic import BaseModel
from dataclasses import dataclass

# Mock classes for demonstration (would be imported from pydantic_ai.graph in real usage)
class GraphRunContext:
    def __init__(self, state):
        self.state = state

class BaseNode:
    pass

class End:
    def __init__(self, result):
        self.result = result

class Graph:
    def __init__(self, nodes, start_node):
        self.nodes = nodes
        self.start_node = start_node
    
    async def run(self, state):
        # Mock implementation for demonstration
        print(f"Running graph workflow with state: {state.model_dump()}")
        
        # Simulate workflow execution
        print("1. Analyzing issue...")
        await asyncio.sleep(0.1)  # Simulate async work
        
        print("2. Searching for solutions...")
        await asyncio.sleep(0.1)
        
        print("3. Providing recommendation...")
        await asyncio.sleep(0.1)
        
        return "Workflow completed successfully"

# Real implementation starts here
class SupportState(BaseModel):
    user_request: str
    issue_analysis: str = ""
    solution_found: bool = False
    escalation_needed: bool = False

@dataclass
class AnalyzeIssue(BaseNode):
    async def run(self, ctx: GraphRunContext) -> 'SearchSolutions':
        # In real implementation, would use PydanticAI Agent
        print(f"Analyzing request: {ctx.state.user_request}")
        
        # Mock analysis
        ctx.state.issue_analysis = "Issue identified: User experiencing login problems"
        print(f"Analysis complete: {ctx.state.issue_analysis}")
        
        return SearchSolutions()

@dataclass
class SearchSolutions(BaseNode):
    async def run(self, ctx: GraphRunContext):
        print(f"Searching solutions for: {ctx.state.issue_analysis}")
        
        # Mock solution search
        if "login" in ctx.state.issue_analysis.lower():
            ctx.state.solution_found = True
            return ProvideRecommendation(solution="Clear browser cache and try again")
        else:
            ctx.state.escalation_needed = True
            return EscalateToHuman()

@dataclass
class ProvideRecommendation(BaseNode):
    solution: str
    
    async def run(self, ctx: GraphRunContext) -> End:
        print(f"Providing solution: {self.solution}")
        return End(f"Solution: {self.solution}")

@dataclass
class EscalateToHuman(BaseNode):
    async def run(self, ctx: GraphRunContext) -> End:
        print("Escalating to human support team")
        return End("Escalated to human support team")

# Create the graph workflow
support_graph = Graph(
    nodes=[AnalyzeIssue, SearchSolutions, ProvideRecommendation, EscalateToHuman],
    start_node=AnalyzeIssue
)

async def handle_support_request_structured(user_request: str) -> str:
    print(f"\n=== Processing Support Request ===")
    print(f"Request: {user_request}")
    
    state = SupportState(user_request=user_request)
    result = await support_graph.run(state)
    
    print(f"Final state: {state.model_dump()}")
    print(f"Result: {result}")
    
    return result

async def main():
    print("=== Graph-Based Agent Workflow Example ===\n")
    
    # Test different support requests
    test_requests = [
        "I can't log into my account",
        "The website is really slow",
        "My data was deleted"
    ]
    
    for request in test_requests:
        print(f"\n{'='*60}")
        await handle_support_request_structured(request)
        print('='*60)

if __name__ == "__main__":
    asyncio.run(main())