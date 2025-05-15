## Effective AI Engineering #xxx: Model Escalation for Cost-Effective LLM Reliability

**Want to optimize both cost and reliability in your LLM applications?** Traditional retry approaches waste resources by repeatedly calling expensive models, but there's a smarter way.

Even with well-engineered prompts, LLMs sometimes fail to produce valid outputs. Instead of repeatedly retrying with the same costly model, model escalation starts with cheaper, smaller models and only escalates to more powerful ones when necessary.

### The Problem

Many developers implement retry strategies that use the same expensive model for every attempt:

```python
# BEFORE: Simple Retry with Expensive Model
from mirascope import anthropic, prompt_template
from tenacity import retry, stop_after_attempt
from pydantic import BaseModel, AfterValidator
from typing import Annotated

def is_upper(s: str) -> bool:
    return s.isupper()

@retry(stop=stop_after_attempt(3))
@anthropic.call(
    model="claude-3-opus-20240229",  # Always using the most powerful model
    response_model=Annotated[str, AfterValidator(is_upper)],
)
def identify_author(book: str) -> str:
    return f"Who wrote {book}?"
```

**Why this approach falls short:**

- **Cost Inefficiency:** Expensive models are used even for tasks that simpler models could handle.
- **Limited Resource Allocation:** Your budget gets consumed quickly, limiting the number of tasks you can process.
- **Overhead for Simple Tasks:** Using powerful models for straightforward queries is like using a sledgehammer to crack a nut.
- **Unnecessary Latency:** Larger models typically have higher latency, slowing down your application.

### The Solution: Model Escalation

A better approach implements model escalation: starting with smaller, cheaper models and only escalating to more powerful ones when necessary. Mirascope provides built-in fallback support for this exact use case.

```python
# AFTER: Model Escalation Strategy
from anthropic import RateLimitError as AnthropicRateLimitError
from mirascope import llm
from mirascope.retries import FallbackError, fallback
from openai import RateLimitError as OpenAIRateLimitError
from tenacity import (
    RetryError,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)
from pydantic import AfterValidator
from typing import Annotated

def is_upper(s: str) -> bool:
    return s.isupper()

# Try a cheaper model first, then fall back to more expensive model if needed
@fallback(
    RetryError,  # Trigger fallback on retry error
    [
        {
            "catch": RetryError,
            "provider": "openai",
            "model": "gpt-4o",
            "response_model": Annotated[str, AfterValidator(is_upper)],
        }
    ],
)
@retry(
    retry=retry_if_exception_type((OpenAIRateLimitError, AnthropicRateLimitError)),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
)
@llm.call(
    provider="openai", 
    model="gpt-4o-mini",
    response_model=Annotated[str, AfterValidator(is_upper)],
)
def identify_author(book: str) -> str:
    """First tries cheaper model, escalates to better model only when needed."""
    return f"Who wrote {book}?"
```

**Why this approach works better:**

- **Cost Optimization:** Starts with cheaper models, saving resources for when they're truly needed.
- **Appropriate Resource Allocation:** Matches model capabilities to task difficulty adaptively.
- **Faster Average Response Time:** Simpler models are generally faster, improving overall latency.
- **Graceful Degradation:** Provides multiple fallback options before giving up.

### The Takeaway

Model escalation provides a pragmatic strategy for balancing cost and reliability in LLM applications. By starting with smaller models and escalating only when necessary, you can achieve significant cost savings while maintaining high success rates.

> **Reference:** This approach is supported by research highlighted on [AI Snake Oil](https://www.aisnakeoil.com/p/ai-leaderboards-are-no-longer-useful), where smaller models were found to perform surprisingly well on many tasks, making exhaustive model benchmarking less useful than adaptive strategies.

---
*Part of the "Effective AI Engineering" series - practical tips for building better applications with AI components.*