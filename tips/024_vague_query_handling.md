---
tip_number: 24
tip_name: "Handle Vague Queries"
categories: ["user-experience", "prompt-engineering", "quality-assurance"]
x_link: "https://x.com/skylar_b_payne/status/1934672461695521000"
linkedin_link: "https://www.linkedin.com/posts/skylarbpayne_is-your-ai-spitting-out-nonsense-and-costing-activity-7340438380037455873-QAW4?utm_source=share&utm_medium=member_desktop&rcm=ACoAABKpCf4BI_Yx2u7h66sgi5z1NF3aEYFHgps"
---

## Effective AI Engineering #24: Handle Vague Queries

**Is Your AI Burning Through Precious Compute Budget Answering Vague User Questions?**

You built that new AI feature to revolutionize how users interact with your product. But when someone types "something is wrong," does your AI confidently spout generic advice, or worse, hallucinate details about problems it knows nothing about?

This isn't just annoying; it's a drain on your resources and, more importantly, on user trust. Vague queries force powerful LLMs into a guessing game, leading to responses that miss the mark entirely. Users get frustrated, abandon the feature, and that early excitement fades fast.

### The Hidden Cost of Blindly Answering

Many engineers, especially in fast-paced startups, try to make their AI handle every user input, no matter how unclear. It feels flexible, right? But this approach has hidden costs that aren't immediately obvious.

Take a look at how this often plays out:

```python
# BEFORE: No query filtering
from mirascope.core import llm

@llm.call(provider="openai", model="gpt-4o-mini")
def handle_user_request(user_query: str) -> str:
    return f"""
    Help the user with their request: {user_query}
    If the request is unclear, do your best to provide general advice.
    """

handle_user_request("something is wrong")
```

**Why this quickly becomes a problem:**

- **Hallucinated Specifics:** Your AI invents details about problems it literally knows nothing about. This can lead to wrong advice and erode user confidence.
- **Generic Responses:** Vague questions get equally vague, unhelpful answers. It's like asking for directions and being told "go somewhere."
- **Wasted Resources:** Every unclear query you process still burns tokens and compute. It's like paying for a consultant to say "I don't know what you want."

### The Smarter Way: Clarity-First AI

Imagine your AI actually *guides* users to ask better questions. That's the power of clarity-first query processing. Instead of guessing, your AI detects vague inputs and smartly asks for more information before trying to solve anything. This ensures you only process queries when you can actually deliver a valuable, specific response.

Here’s how it works:

```python
# AFTER: Vague query detection and clarification requests
from mirascope.core import llm
from pydantic import BaseModel
import lilypad
from typing import List

class QueryAnalysis(BaseModel):
    is_specific: bool
    missing_context: List[str]

class ClarificationRequest(BaseModel):
    message: str
    suggested_questions: List[str]

@lilypad.trace()
@llm.call(provider="openai", model="gpt-4o-mini", response_model=QueryAnalysis)
def analyze_query_clarity(query: str) -> QueryAnalysis:
    return f"""
    Analyze if this user query contains enough specific information to provide a helpful response:
    Query: "{query}"
    
    Consider:
    - Does it specify the problem domain (code, data, specific tool)?
    - Does it include relevant context or error details?
    - Can you provide a specific, actionable answer?
    
    Determine if query is specific and list what context is missing.
    """

@lilypad.trace()
@llm.call(provider="openai", model="gpt-4o-mini", response_model=ClarificationRequest)
def generate_clarification(query: str, missing_context: List[str]) -> ClarificationRequest:
    return f"""
    Create a helpful clarification request for this vague query: "{query}"
    Missing context: {missing_context}
    
    Guide the user to provide specific details needed for a helpful response.
    Include 2-3 example questions they could ask instead.
    """

@lilypad.trace()
@llm.call(provider="openai", model="gpt-4o-mini")
def handle_specific_query(query: str) -> str:
    return f"Provide a specific, helpful response to: {query}"

@lilypad.trace()
def smart_query_handler(user_query: str) -> str:
    # Analyze query clarity first
    analysis = analyze_query_clarity(user_query)
    
    if analysis.is_specific:
        # Query is specific enough - process it
        return handle_specific_query(user_query)
    else:
        # Query is too vague - request clarification
        clarification = generate_clarification(user_query, analysis.missing_context)
        
        suggested_questions = "\n".join([f"• {q}" for q in clarification.suggested_questions])
        
        return f"""{clarification.message}

For example, you could ask:
{suggested_questions}"""

smart_query_handler("something is wrong")
```

**Why this approach is a game-changer:**

- **Guided Specificity:** Users learn to ask better questions through targeted, helpful prompts. They feel understood, not dismissed.
- **Reduced Hallucination:** Your AI only attempts to answer when it has enough context. No more inventing details\!
- **Higher Success Rate:** Specific questions lead to specific, actionable solutions. This means more "aha\!" moments for your users and less wasted effort for your AI.
- **Efficient Resource Use:** Stop spending valuable tokens on unanswerable questions. Direct your compute power to problems your AI can genuinely solve.

### Empower Your AI, Delight Your Users

Don't let vague queries turn your innovative AI feature into a frustrating guessing game. By implementing a clarity-first approach, you'll build more reliable, efficient, and user-pleasing AI applications. It's about working smarter, not just harder, and ensuring every interaction delivers real value.

-----

*Part of the "Effective AI Engineering" series - practical tips for building better applications with AI components.*