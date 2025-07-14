---
tip_number: 31
tip_name: "Streaming Responses"
categories: ["user-experience", "performance", "integration"]
x_link: "https://x.com/skylar_b_payne/status/1940108268942069792"
linkedin_link: "https://www.linkedin.com/posts/skylarbpayne_users-leave-after-3-seconds-your-ai-takes-activity-7345874176194277377-FVpE?utm_source=share&utm_medium=member_desktop&rcm=ACoAABKpCf4BI_Yx2u7h66sgi5z1NF3aEYFHgps"
---

## Effective AI Engineering #31: Streaming Responses

Users love your report generation. That is if it loads in time.
After 1 second, users have gone to another tab.
And forget to come back. Your product seems impossible to produce without AI.
But why does it have to be so slow?

Let me show you a better way.

### The Problem

Many developers wait for complete LLM responses before showing anything to users. This creates challenges that aren't immediately obvious:

```python
# BEFORE: Blocking until complete response
from mirascope.core import llm

@llm.call(provider="openai", model="gpt-4o-mini")
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"

# User waits for entire response
response = recommend_book("fantasy")
print(response)  # Shows complete response only after the entire thing has been generated!
```

**Why this approach falls short:**

- **Poor Perceived Performance:** Users feel the system is slow even when generation time is reasonable
- **No Progressive Disclosure:** Long responses overwhelm users instead of building understanding incrementally
- **Higher Abandonment:** Users may leave before seeing any output from complex queries

### The Solution: Token-Level Streaming

A better approach is to stream tokens as they're generated and display partial responses immediately. This pattern dramatically improves perceived performance and user engagement.

```python
# AFTER: Streaming tokens as they arrive
from mirascope.core import llm

@llm.call(provider="openai", model="gpt-4o-mini", stream=True)
def recommend_book(genre: str):
    return f"Recommend a {genre} book"

# Stream tokens as they're generated
stream = recommend_book("fantasy")
for chunk, _ in stream:
    print(chunk.content, end="", flush=True)

# Access complete response after streaming
print(f"\n\nContent: {stream.content}")
```

**Why this approach works better:**

- **Instant Feedback:** Users see content within 200ms instead of waiting for complete responses
- **Progressive Understanding:** Complex topics build understanding incrementally rather than overwhelming users
- **Better Engagement:** Users stay engaged reading partial content instead of waiting on blank screens

### The Streaming vs. Validation Tension

Streaming creates a fundamental tension with output validation and guardrails. When you stream partial results, you're showing users content before it's complete—which means you can't validate the entire output or apply comprehensive guardrails.

**Key considerations:**

- **Partial Validation:** You can only validate chunks as they arrive, not the complete response
- **Guardrail Limitations:** Traditional content filters work on complete outputs, not streaming fragments
- **User Experience Trade-offs:** Users see faster responses but might encounter incomplete or invalidated content

```python
# Challenge: How do you validate this partial response?
for chunk, _ in stream:
    # You only have access to individual chunks
    # Cannot validate complete response until streaming finishes
    print(chunk.content, end="", flush=True)
    
# Validation must happen after streaming completes
if needs_validation:
    complete_content = stream.content
    validation_result = validate_output(complete_content)
    if not validation_result.is_valid:
        # Too late - user already saw the content
        handle_validation_failure()
```

This tension requires careful consideration of when streaming is appropriate versus when you need complete validation before showing results to users.

### The Takeaway

Streaming responses transform long AI outputs from blocking operations into engaging real-time experiences. This pattern dramatically improves perceived performance by showing partial results immediately while responses generate.

---
*Part of the "Effective AI Engineering" series - practical tips for building better applications with AI components.*