---
tip_number: 29
tip_name: "Record and Replay"
categories: ["testing", "debugging", "evaluation"]
x_link: ""
linkedin_link: "https://www.linkedin.com/posts/skylarbpayne_3-hours-127-runs-2-half-empty-lattes-activity-7343337496522440705-Isb6?utm_source=share&utm_medium=member_desktop&rcm=ACoAABKpCf4BI_Yx2u7h66sgi5z1NF3aEYFHgps"
---

## Effective AI Engineering #29: Record and Replay

3 hours. 127 runs. 2 half empty lattes. And no progress.
Your most important customer got a strange response from your AI chat bot.
You followed best practices. You decomposed into multiple tasks. You added instrumentation.
But now you have a debugging nightmare: a complex AI workflows with multiple chained LLM calls.
How the hell can you debug something like this??

Take a deep breath; and follow along!

### The Problem

When failures occur deep in a pipeline, isolating the root cause requires reproducing exact conditions - model responses, context, and state that may be impossible to recreate.
Many developers try to debug AI pipelines by re-running them from scratch, hoping to recreate the failure. This creates challenges that aren't immediately obvious:

```python
# BEFORE: No replay capability
from mirascope import llm, prompt_template

@llm.call(provider="anthropic", model="claude-3-5-sonnet-20241022")
@prompt_template("Classify the sentiment of this message: {text}")
def classify_sentiment(text: str) -> str: ...


@llm.call(provider="anthropic", model="claude-3-5-sonnet-20241022")
@prompt_template("Generate a helpful response for a {sentiment} customer message: {text}")
def generate_response(sentiment: str, text: str) -> str: ...


def process_customer_message(message: str) -> str:
    sentiment = classify_sentiment(message)
    response = generate_response(sentiment, message)
    return response

# When this produces bad results, debugging requires expensive re-runs
result = process_customer_message("I can't access my billing information")
```

**Why this approach falls short:**

- **Non-Reproducible Failures:** LLM stochasticity means re-running rarely recreates the exact failure
- **Expensive Debugging:** Each debug attempt consumes tokens and may not hit the problematic path
- **Lost Context:** Intermediate states and responses that caused the failure are gone forever

### The Solution: Record / Replay Calls

A better approach is to record LLM interactions to "cassettes" that can be replayed exactly, similar to how VCRpy works for HTTP requests. This pattern captures problematic responses and lets you debug them repeatedly without making new API calls.
You can even manually _edit_ the saved "cassettes" to provide the exact output you're looking for!

```python
# AFTER: Simple cassette recording decorator
from mirascope import llm, prompt_template
import vcry

# First time this is run will record the HTTP requests; second time will replay them
@vcr.use_cassette()
@lilypad.trace()
@anthropic.call("claude-3-5-sonnet-20241022")
@prompt_template("Classify the sentiment of this message: {text}")
def classify_sentiment(text: str) -> str: ...


@lilypad.trace()
@anthropic.call("claude-3-5-sonnet-20241022")
@prompt_template("Generate a helpful response for a {sentiment} customer message: {text}")
def generate_response(sentiment: str, text: str) -> str: ...


def process_customer_message(message: str) -> str:
    sentiment = classify_sentiment(message)
    response = generate_response(sentiment, message)
    return response

# First run records to cassette
print("Processing problematic message...")
result = process_customer_message("I can't access my billing information")
print(f"Result: {result}")

# Subsequent runs replay identical sentiment classification for debuggin.
print("\nDebugging with identical responses...")
debug_result = process_customer_message("I can't access my billing information")
print(f"Debug result: {debug_result}")
```

**Why this approach works better:**

- **Perfect Reproduction:** Cassettes capture exact responses, making any failure reproducible indefinitely
- **Zero-Cost Debugging:** Replay from cassettes eliminates API costs during troubleshooting sessions
- **Simple Implementation:** One decorator provides VCRpy-style recording without complex infrastructure

### The Takeaway

Record/replay functionality can transform unpredictable AI debugging into systematic troubleshooting by capturing exact responses. This simple decorator pattern makes elusive bugs reproducible and eliminates the cost of repeated debugging attempts.

---
*Part of the "Effective AI Engineering" series - practical tips for building better applications with AI components.*