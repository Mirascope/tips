---
tip_number: 11
tip_name: "Optimize Costs with Prompt Caching"
categories: ["cost-control", "performance", "prompt-engineering"]
x_link: "https://x.com/skylar_b_payne/status/1922713662583628249"
linkedin_link: "https://www.linkedin.com/posts/skylarbpayne_input-tokens-are-expensive-so-why-are-activity-7328479589507252224-HyGy?utm_source=share&utm_medium=member_desktop&rcm=ACoAABKpCf4BI_Yx2u7h66sgi5z1NF3aEYFHgps"
---

## Effective AI Engineering #11: Optimize Costs with Prompt Caching

Input tokens are EXPENSIVE, so why are you paying for the same tokens again and again?
Repeated LLM calls with similar prompts can quickly drain your budget and slow down your application.

Every call to an LLM API incurs costs and adds latency to your application. When your application makes multiple calls with similar prompts, you're paying repeatedly for processing the same tokens and waiting for unnecessary computation. This inefficiency compounds as your application scales.

The landscape is evolving rapidly, with Google recently releasing implicit caching for Gemini that automatically caches prompt prefixes without additional configuration, offering significant performance improvements. Despite these advancements, understanding prompt caching principles remains valuable across all LLM providers.

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
def generate_response(query: str): ...
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

@anthropic.call(model="claude-3-sonnet-20240229", response_model=Response)
@prompt_template("""
SYSTEM: You are a helpful assistant that provides concise answers to questions about science topics.

Here are some example responses:
Q: How do solar panels work?
A: Solar panels contain photovoltaic cells that convert sunlight into electricity by knocking electrons loose.

Q: What causes rainbows?
A: Rainbows form when sunlight enters water droplets, bends, reflects off the back, and exits at different angles based on wavelength.

{:cache_control}

USER: {query}
""")
def generate_response(query: str): ...
```

**Why this approach works better:**

- **Reduced Processing Costs:** Static content only needs to be processed once, significantly cutting token costs.
- **Lower Latency:** Cached prompts are processed faster, improving response times.
- **Better Scalability:** Cost savings compound with increased usage volume.
- **Provider Optimization:** Works with various providers' caching mechanisms (Anthropic, OpenAI, etc.).

### The Takeaway

Organize your prompts with caching in mind by placing static content first and separating it from dynamic content. This simple architectural change can dramatically reduce costs and improve response times in LLM-powered applications, especially as you scale.

> **Note:** While in-context examples (as discussed in [Tip #7](007_in_context_learning.md)) make more of your prompt dynamic, our next tip (#12) will show you how to effectively combine dynamic few-shot learning with prompt caching.

> **Important:** Your mileage may vary as caching effectiveness depends on your query patterns and the specific provider's implementation. Provider approaches differ significantly:
> - Google's Gemini now enables implicit caching by default with automatic detection of cacheable content
> - OpenAI offers implicit caching with static content at the beginning of prompts
> - Anthropic requires explicit `{:cache_control}` markers to designate cacheable content
>
> Always consult your provider's latest documentation for the most current caching implementation details.

---
*Part of the "Effective AI Engineering" series - practical tips for building better applications with AI components.*