## Effective AI Engineering #34: Gleaning

**Ever copy a bad AI response into ChatGPT and ask "How would you fix this?"** Then you take that feedback, go back to your original prompt, and make the exact changes ChatGPT suggested. What if the AI just did that refinement loop itself?

Most developers treat AI responses as one-shot attempts—if it's wrong, start over from scratch. But the best responses often come from iterative refinement, where the AI learns from its own mistakes and progressively improves its output.

### The Problem

Many developers make single AI calls and hope for the best, starting over completely when responses don't meet requirements. This creates challenges that aren't immediately obvious:

```python
# BEFORE: Single attempt with no refinement
from mirascope.core import anthropic, prompt_template

@anthropic.call("claude-3-5-sonnet-20241022")
@prompt_template("Write a professional email to decline a job offer for: {position}")
def decline_job_offer(position: str) -> str:
    pass

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
from mirascope.core import anthropic, prompt_template

@anthropic.call("claude-3-5-sonnet-20241022")
@prompt_template("""
Answer: {query}

{% if prev_response %}
<previous>{prev_response}</previous>
{% endif %}

{% if feedback %}
<feedback>{feedback}</feedback>

Please revise your previous response based on this feedback.
{% endif %}
""")
def answer_with_refinement(
    query: str, 
    *, 
    prev_response: str | None = None, 
    feedback: str | None = None
) -> str:
    pass

@anthropic.call("claude-3-5-sonnet-20241022")
@prompt_template("""
Please provide feedback on whether this response adequately answers the question.

Question: {query}

Response: {response}

Identify specific areas for improvement and suggest concrete changes.
""")
def generate_feedback(query: str, response: str) -> str:
    pass

def gleaning_process(query: str, max_iterations: int = 3) -> str:
    """Iteratively refine response using self-generated feedback"""
    
    # Generate initial response
    current_response = answer_with_refinement(query)
    print(f"Initial response: {current_response[:100]}...")
    
    for iteration in range(max_iterations):
        # Generate feedback on current response
        feedback = generate_feedback(query, current_response)
        print(f"\nIteration {iteration + 1} feedback: {feedback[:100]}...")
        
        # Check if feedback indicates satisfaction
        if "excellent" in feedback.lower() or "no improvements" in feedback.lower():
            print(f"Refinement complete after {iteration + 1} iterations")
            return current_response
        
        # Refine response based on feedback
        refined_response = answer_with_refinement(
            query,
            prev_response=current_response,
            feedback=feedback
        )
        
        print(f"Refined response: {refined_response[:100]}...")
        current_response = refined_response
    
    return current_response

# Example usage
query = "Write a professional email declining a Senior Software Engineer position"
final_response = gleaning_process(query, max_iterations=2)

print(f"\nFinal response:\n{final_response}")
```

**Why this approach works better:**

- **Self-Improving Loop:** The AI learns from its own output and applies targeted improvements
- **Progressive Refinement:** Each iteration builds on the previous attempt rather than starting over  
- **Quality Convergence:** Multiple revision cycles typically produce higher-quality results than single attempts

### The Takeaway

Gleaning lets AI systems refine their own responses through iterative feedback loops, mimicking the natural revision process that produces better writing. This approach consistently generates higher-quality outputs than single-shot generation.

---
*Part of the "Effective AI Engineering" series - practical tips for building better applications with AI components.*