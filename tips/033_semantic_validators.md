## Effective AI Engineering #33: Semantic Validators

**Your AI answers look professional and confident, but they're slowly destroying user trust.** Every hallucinated fact, unprofessional tone, or confidently wrong response chips away at your acquisition and retention rates.

Users can't easily distinguish between a well-formatted lie and a well-formatted truth. Traditional validation catches format issues, but can't detect when your AI sounds authoritative while being completely wrong about facts, tone, or context.

### The Problem

Many developers ship AI responses without any validation, trusting the model to get it right. This creates trust-eroding issues that hurt your business:

```python
# BEFORE: No validation at all
from mirascope.core import anthropic, prompt_template

@anthropic.call("claude-3-5-sonnet-20241022")
@prompt_template("Answer this customer question: {question}")
def answer_question(question: str) -> str:
    pass

# Ship whatever the AI says
result = answer_question("When was the War of 1812?")
print(result)  # Could be wrong, rude, or hallucinated
```

**Why this approach falls short:**

- **Hallucination Risk:** AI confidently states false information that sounds authoritative
- **Tone Problems:** Responses may be unprofessional, dismissive, or inappropriate for your brand
- **Trust Erosion:** Each wrong answer damages user confidence and long-term retention

### The Solution: Semantic Validators

A better approach is to use AI validators that catch fuzzy issues like hallucination, tone problems, and factual errors. This pattern uses AI to validate AI responses before they reach users.

```python
# AFTER: Simple semantic validation
from mirascope.core import anthropic, prompt_template
from pydantic import BaseModel
from typing import Annotated
from pydantic.functional_validators import AfterValidator

@anthropic.call("claude-3-5-sonnet-20241022", response_model=bool)
@prompt_template("Is this factual? Output only True or False:\n{content}")
def is_factual(content: str) -> bool:
    pass

@anthropic.call("claude-3-5-sonnet-20241022", response_model=bool)
@prompt_template("Is this professional and appropriate? Output only True or False:\n{content}")
def is_professional(content: str) -> bool:
    pass

def validate_response(content: str) -> str:
    if not is_factual(content):
        raise ValueError("Response contains factual errors")
    if not is_professional(content):
        raise ValueError("Response tone is unprofessional")
    return content

@anthropic.call("claude-3-5-sonnet-20241022", response_model=Annotated[str, AfterValidator(validate_response)])
@prompt_template("Answer this customer question: {question}")
def validated_answer(question: str) -> str:
    pass

# Now responses are validated before being returned
result = validated_answer("When was the War of 1812?")
print(result)  # Only factual, professional responses make it through
```

**Why this approach works better:**

- **Hallucination Detection:** Catches confident-sounding but false information before users see it
- **Tone Control:** Ensures responses match your brand voice and professionalism standards
- **Trust Protection:** Prevents trust-eroding responses that hurt long-term user retention

### The Takeaway

Semantic validators catch fuzzy issues like hallucination and tone problems that traditional validation misses. This pattern protects user trust by ensuring AI responses are both factually accurate and professionally appropriate.

---
*Part of the "Effective AI Engineering" series - practical tips for building better applications with AI components.*