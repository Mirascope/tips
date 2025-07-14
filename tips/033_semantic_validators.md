---
tip_number: 33
tip_name: "Semantic Validators"
categories: ["output-validation", "quality-assurance", "error-handling"]
x_link: ""
linkedin_link: "https://www.linkedin.com/posts/skylarbpayne_users-no-feedback-just-churn-the-only-activity-7346598941485883392-RxzQ?utm_source=share&utm_medium=member_desktop&rcm=ACoAABKpCf4BI_Yx2u7h66sgi5z1NF3aEYFHgps"
---

## Effective AI Engineering #33: Semantic Validators

The only feedback on your AI? Pissed off users looking for a refund.
You thought you'd just ship your AI and iterate. Users would give holistic feedback. Right?
Instead they just churn. The problem? Your AI answers look correct, but have subtle problems.
Problems that a schema isn't going to validate for you.

Let's fix that.

### The Problem

Many developers ship AI responses without any validation, trusting the model to get it right. This creates trust-eroding issues that hurt your business:

```python
# BEFORE: No validation at all
from mirascope import llm, prompt_template

@llm.call("claude-3-5-sonnet-20241022")
@prompt_template("Answer this customer question: {question}")
def answer_question(question: str): ...

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
from mirascope import llm, prompt_template
from pydantic import BaseModel
from typing import Annotated
from pydantic import AfterValidator

@llm.call(provider="anthropic", model="claude-3-5-sonnet-20241022", response_model=bool)
@prompt_template("Is this factual? Output only True or False:\n{content}")
def is_factual(content: str): ...


@llm.call(provider="anthropic", model="claude-3-5-sonnet-20241022", response_model=bool)
@prompt_template("Is this professional and appropriate? Output only True or False:\n{content}")
def is_professional(content: str): ...


def validate_response(content: str) -> str:
    if not is_factual(content):
        raise ValueError("Response contains factual errors")
    if not is_professional(content):
        raise ValueError("Response tone is unprofessional")
    return content


@llm.call(provider="anthropic", model="claude-3-5-sonnet-20241022", response_model=Annotated[str, AfterValidator(validate_response)])
@prompt_template("Answer this customer question: {question}")
def validated_answer(question: str): ...


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