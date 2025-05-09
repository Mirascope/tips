## Effective AI Engineering #11: Optimize Costs with Prompt Caching

**Are you struggling with high LLM API costs and latency?** Repeated LLM calls with similar prompts can quickly drain your budget and slow down your application.

Every call to an LLM API incurs costs and adds latency to your application. When your application makes multiple calls with similar prompts, you're paying repeatedly for processing the same tokens and waiting for unnecessary computation. This inefficiency compounds as your application scales.

### The Problem

Many developers approach prompt design by focusing solely on functionality, without considering how prompts might be reused:

```python
# BEFORE: Inefficient Prompt Organization
from mirascope import prompt_template, anthropic
from pydantic import BaseModel

class Response(BaseModel):
    answer: str

@anthropic.call(model="claude-3-sonnet-20240229", response_model=Response)
@prompt_template("""
SYSTEM: You are a helpful assistant that provides concise answers to questions about science topics.

Here are some example responses:
Q: How do solar panels work?
A: Solar panels contain photovoltaic cells that convert sunlight into electricity by knocking electrons loose.

Q: What causes rainbows?
A: Rainbows form when sunlight enters water droplets, bends, reflects off the back, and exits at different angles based on wavelength.

USER: {query}
""")
def generate_response(query: str):
    # Each call processes the entire prompt from scratch
    pass
```

**Why this approach falls short:**

- **Redundant Token Processing:** The system instructions and examples are reprocessed with every request, even though they never change.
- **Higher Costs:** Input tokens typically cost more than output tokens, and the static portion of your prompt is processed and charged repeatedly.
- **Increased Latency:** Processing the same static tokens adds unnecessary time to each request.
- **Limited Scale:** As request volume grows, inefficient prompt handling creates proportionally larger cost and performance issues.

### The Solution: Organize Prompts for Caching

A better approach is to structure your prompts to maximize cache hits with prompt caching. This technique separates static content from dynamic content, allowing providers to reuse processed portions of prompts.

```python
# AFTER: Prompt Structure Optimized for Caching
from mirascope import anthropic, prompt_template
from pydantic import BaseModel

class Response(BaseModel):
    answer: str

# Static part of the prompt placed first for better cache utilization
SYSTEM_PROMPT = """
SYSTEM: You are a helpful assistant that provides concise answers to questions about science topics.

Here are some example responses:
Q: How do solar panels work?
A: Solar panels contain photovoltaic cells that convert sunlight into electricity by knocking electrons loose.

Q: What causes rainbows?
A: Rainbows form when sunlight enters water droplets, bends, reflects off the back, and exits at different angles based on wavelength.
"""

@anthropic.call(
    model="claude-3-sonnet-20240229",
    response_model=Response,
    extra_headers={"anthropic-beta": "prompt-caching-v0"}
)
@prompt_template("{system}\n\nUSER: {query}")
def generate_cached_response(query: str):
    # The static system prompt is separate from the dynamic user query
    return {"computed_fields": {"system": SYSTEM_PROMPT}}

# Making a call that can leverage prompt caching
response = generate_cached_response(query="How do wind turbines generate electricity?")
```

**Why this approach works better:**

- **Reduced Processing Costs:** Static content only needs to be processed once, significantly cutting token costs.
- **Lower Latency:** Cached prompts are processed faster, improving response times.
- **Better Scalability:** Cost savings compound with increased usage volume.
- **Provider Optimization:** Works with various providers' caching mechanisms (Anthropic, OpenAI, etc.).

### The Takeaway

Organize your prompts with caching in mind by placing static content first and separating it from dynamic content. This simple architectural change can dramatically reduce costs and improve response times in LLM-powered applications, especially as you scale.

> **Note:** While in-context examples (as discussed in [Tip #7](007_in_context_learning.md)) make more of your prompt dynamic, our next tip (#12) will show you how to effectively combine dynamic few-shot learning with prompt caching.

> **Important:** Your mileage may vary as caching effectiveness depends on your query patterns and the specific provider's caching implementation. Some providers (like Gemini) are beginning to enable caching by default, while others require explicit configuration.

---
*Part of the "Effective AI Engineering" series - practical tips for building better applications with AI components.*