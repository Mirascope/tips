## Effective AI Engineering #14: Error Reinsertion for Smarter LLM Retries

**Tired of your LLM just repeating the same mistakes when retries fail?** Simple retry strategies just multiply costs without improving reliability when models fail in consistent ways.

You've built validation for structured LLM outputs, but when validation fails and you retry the exact same prompt, you're essentially asking the model to guess differently. Without feedback about what went wrong, you're wasting compute and adding latency while hoping for random success. A smarter approach feeds errors back to the model, creating a self-correcting loop.

### The Problem

Many developers implement basic retry mechanisms that blindly repeat the same prompt after a failure:

```python
# BEFORE: Naive Retry Without Error Feedback
from mirascope import llm
from tenacity import retry, stop_after_attempt
from typing import Annotated
from pydantic import AfterValidator

def is_upper(v: str) -> str:
    assert v.isupper(), "Must be uppercase"
    return v

@retry(stop=stop_after_attempt(3))
@llm.call(
    provider="openai",
    model="gpt-4o-mini",
    response_model=Annotated[str, AfterValidator(is_upper)],
)
def identify_author(book: str) -> str:
    return f"Who wrote {book}?"

try:
    # If the model returns "Patrick Rothfuss" instead of "PATRICK ROTHFUSS",
    # we'll retry with the EXACT SAME prompt 3 times
    author = identify_author("The Name of the Wind")
    print(f"Author: {author}")
except Exception as e:
    print(f"Failed after 3 attempts: {e}")
```

**Why this approach falls short:**

- **Wasteful Compute:** Repeatedly sending the same prompt when validation fails just multiplies costs without improving chances of success.
- **Same Mistakes:** LLMs tend to be consistent - if they misunderstand your requirements the first time, they'll likely make the same errors on retry.
- **Longer Latency:** Users wait through multiple failed attempts with no adaptation strategy.
- **No Learning Loop:** The model never receives feedback about what went wrong, missing the opportunity to improve.

### The Solution: Error Reinsertion for Adaptive Retries

A better approach is to reinsert error information into subsequent retry attempts, giving the model context to improve its response:

```python
# AFTER: Smart Retry with Error Reinsertion
from typing import Annotated
from mirascope import llm
from mirascope.retries.tenacity import collect_errors 
from pydantic import AfterValidator, ValidationError
from tenacity import retry, stop_after_attempt

def is_upper(v: str) -> str:
    assert v.isupper(), "Must be uppercase"
    return v

@retry(stop=stop_after_attempt(3), after=collect_errors(ValidationError))
@llm.call(
    provider="openai",
    model="gpt-4o-mini",
    response_model=Annotated[str, AfterValidator(is_upper)],
)
def identify_author(book: str, *, errors: list[ValidationError] | None = None) -> str: 
    if errors:
        return f"Previous Error: {errors}\n\nWho wrote {book}?"
    return f"Who wrote {book}?"

try:
    # First attempt might return "Patrick Rothfuss" (fails validation)
    # Second attempt with error info returns "PATRICK ROTHFUSS" (passes)
    author = identify_author("The Name of the Wind")
    print(f"Author: {author}")
except Exception as e:
    print(f"Failed after 3 attempts: {e}")
```

**Why this approach works better:**

- **Adaptive Learning:** The model receives feedback about specific validation failures, allowing it to correct its mistakes.
- **Higher Success Rate:** By feeding error context back to the model, retry attempts become increasingly likely to succeed.
- **Resource Efficiency:** Instead of hoping for random variation, each retry has a higher probability of success, reducing overall attempt count.
- **Improved User Experience:** Faster resolution of errors means less waiting for valid responses.

### The Takeaway

Stop treating LLM retries as mere repetition and implement error reinsertion to create a feedback loop. By telling the model exactly what went wrong, you create a self-correcting system that improves with each attempt. This approach makes your AI applications more reliable while reducing unnecessary compute and latency.

---
*Part of the "Effective AI Engineering" series - practical tips for building better applications with AI components.*