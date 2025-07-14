---
tip_number: 34
tip_name: "Gleaning"
categories: ["quality-assurance", "iteration", "prompt-engineering"]
x_link: ""
linkedin_link: "https://www.linkedin.com/posts/skylarbpayne_going-back-and-forth-with-ai-is-time-consuming-activity-7346961348242685953-rP9a?utm_source=share&utm_medium=member_desktop&rcm=ACoAABKpCf4BI_Yx2u7h66sgi5z1NF3aEYFHgps"
---

## Effective AI Engineering #34: Gleaning

You’ve seen it before: your AI delivers that 'almost there' draft.
That sinking feeling when you realize you're still on cleanup duty, manually tweaking and re-prompting, just to get it production-ready. It's frustrating, right?
You got into AI to build amazing things, not to babysit endless 'first drafts.'  Many engineers find themselves stuck in this loop, making single AI calls and crossing their fingers. But when responses don't hit the mark, you're back to square one, manually refining what the AI couldn't quite nail. This isn't just inefficient; it means your AI isn't truly learning or improving, and you're missing out on real innovation.

Imagine an AI that learns from its mistakes.
An AI that doesn’t just generate a response, but refines it. Iteratively. Until it meets your exact standards.

### The Problem

Many developers make single AI calls and hope for the best, starting over completely when responses don't meet requirements. This creates challenges that aren't immediately obvious:

```python
# BEFORE: Single attempt with no refinement
from mirascope import llm, prompt_template

@llm.call(provider="anthropic", model="claude-3-5-sonnet-20241022")
@prompt_template("Write a professional email to decline a job offer for: {position}")
def decline_job_offer(position): ...

# One shot, no refinement opportunity
response = decline_job_offer("Senior Software Engineer")
print(response)
```

**Why this approach falls short:**

- **No Learning from Context:** The AI can't learn from what didn't work in its initial attempt
- **Missed Refinement Opportunities:** Human-quality writing often requires multiple drafts and revisions
- **Binary Success:** Either the response works perfectly or you start completely over

### The Solution: Gleaning

A better approach is to let the AI refine its own responses iteratively. This gleaning technique creates a feedback loop where the AI critiques and improves its own output until it meets your standards.

```python
# AFTER: Iterative refinement through gleaning
from mirascope import llm, prompt_template
from pydantic import BaseModel

class FeedbackResult(BaseModel):
    feedback: str
    needs_improvement: bool

@llm.call(provider="anthropic", model="claude-3-5-sonnet-20241022")
@prompt_template("Write a professional email to decline a job offer for: {position}")
def generate_response(position: str): ...

@llm.call(
    provider="anthropic", 
    model="claude-3-5-sonnet-20241022",
    response_model=FeedbackResult
)
@prompt_template("""
Evaluate this response and provide feedback:

Query: {query}
Response: {response}

Return your assessment with specific improvement suggestions.
""")
def evaluate_response(query: str, response: str): ...

@llm.call(provider="anthropic", model="claude-3-5-sonnet-20241022")
@prompt_template("""
Improve this response based on the feedback:

Original query: {query}
Previous response: {response}
Feedback: {feedback}

Provide a revised version.
""")
def refine_response(query: str, response: str, feedback: str): ...

def gleaning_query(position: str, max_iterations: int = 3):
    """Higher-order function that adds gleaning to any AI function"""
    current_response = generate_response(position)
    
    for i in range(max_iterations):
        evaluation = evaluate_response(position, current_response.content)
        
        if not evaluation.needs_improvement:
            return current_response
            
        current_response = refine_response(
            position, current_response.content, evaluation.feedback
        )
    
    return current_response

# Example usage
position = "Senior Software Engineer"
final_response = gleaning(generate_response, position, max_iterations=2)

print(f"Final response:\n{final_response}")
```

**Why this approach works better:**

- **Self-Improving Loop:** The AI learns from its own output and applies targeted improvements
- **Progressive Refinement:** Each iteration builds on the previous attempt rather than starting over  
- **Quality Convergence:** Multiple revision cycles typically produce higher-quality results than single attempts

### The Takeaway

Gleaning lets AI systems refine their own responses through iterative feedback loops, mimicking the natural revision process that produces better writing. This approach consistently generates higher-quality outputs than single-shot generation.

---
*Part of the "Effective AI Engineering" series - practical tips for building better applications with AI components.*