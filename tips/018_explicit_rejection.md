---
tip_number: 18
tip_name: "Use Explicit Rejection Types for Better Error Handling"
categories: ["output-validation", "error-handling", "user-experience"]
x_link: ""
linkedin_link: "https://www.linkedin.com/posts/skylarbpayne_are-your-ai-responses-giving-wrong-answers-activity-7332828238190186496-glCr?utm_source=share&utm_medium=member_desktop&rcm=ACoAABKpCf4BI_Yx2u7h66sgi5z1NF3aEYFHgps"
---

## Effective AI Engineering #18: Use Explicit Rejection Types for Better Error Handling

**Are your AI responses giving wrong answers when they should say "I don't know"?** A confident but incorrect response is often worse than an honest rejection.

Your AI system will encounter queries it can't or shouldn't answer - out-of-scope questions, insufficient context in RAG systems, or policy violations. Without explicit rejection handling, models often hallucinate plausible-sounding but incorrect responses rather than admitting uncertainty.

### The Problem

Many developers use simple response models that only handle successful answers, forcing the AI to always provide a response:

```python
# BEFORE: Response model only handles successful answers
from mirascope import llm, prompt_template
from pydantic import BaseModel, Field

class Answer(BaseModel):
    answer: str = Field(description="The answer to the question.")

@llm.call(provider="openai", model="gpt-4o-mini", response_model=Answer)
@prompt_template("""
SYSTEM: You are a helpful assistant. Answer the user's question.
USER: {query}
""")
def answer_question(query: str): ...

# Forces the model to always give an answer, even when it shouldn't
result = answer_question(query="What's the CEO's personal phone number?")
print(result.answer)  # Might hallucinate a phone number!
```

**Why this approach falls short:**

- **Forced Hallucination:** When the model can't provide a good answer, it's structurally forced to make something up rather than declining to answer.
- **No Policy Enforcement:** Questions that violate privacy, security, or business rules can't be explicitly rejected - they just get answered inappropriately.
- **Poor Analytics:** You can't distinguish between legitimate answers and cases where the model should have rejected the query, making it impossible to measure rejection rates or improve system boundaries.

### The Solution: Union Response Types with Explicit Rejection

A better approach is to use union types that allow the AI to explicitly reject queries with a clear reason. This gives the model a structured way to say "no" when appropriate.

```python
# AFTER: Union response type with explicit rejection handling
from mirascope import llm, prompt_template
from pydantic import BaseModel, Field

class Answer(BaseModel):
    answer: str = Field(description="The answer to the question.")

class Rejection(BaseModel):
    reason: str = Field(description="The reason to reject answering the question.")

class Response(BaseModel):
    response: Answer | Rejection

@llm.call(provider="openai", model="gpt-4o-mini", response_model=Response)
@prompt_template("""
SYSTEM: You are a helpful assistant that can answer many user questions. However, you always reject questions about hot dogs.
Your output should be a JSON object with a single top level "response" key. The value of the "response" key should be either an "answer" or "rejection" object.
USER: {query}
""")
def answer_question(query: str): ...

result = answer_question(query="What is the capital of the United States?")
print(result.response.answer)  # "Washington, D.C."

result = answer_question(query="What city has the best hot dogs?")
print(result.response.reason)  # "I don't provide opinions about hot dogs."
```

**Why this approach works better:**

- **Honest Uncertainty:** The model can explicitly reject queries when it lacks sufficient information or confidence, preventing hallucinated responses.
- **Policy Compliance:** Clear rejection paths allow enforcement of business rules, privacy policies, and content guidelines at the model level.
- **Better Analytics:** Track rejection rates to understand system boundaries and identify areas where your AI might need more training data or better prompting.

### The Takeaway

Don't force your AI to always provide an answer. Union response types with explicit rejection handling create more honest, policy-compliant systems that can gracefully decline inappropriate or uncertain queries, leading to better user trust and clearer system boundaries.

---
*Part of the "Effective AI Engineering" series - practical tips for building better applications with AI components.*