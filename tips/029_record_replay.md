## Effective AI Engineering #29: Record and Replay

**Last Tuesday at 2 AM, our support chatbot told a customer to "delete their account" instead of helping with a billing issue.** The logs showed the pipeline ran fine, but when I tried to reproduce it the next morning, the AI generated perfectly reasonable responses every single time.

Complex AI workflows with multiple chained LLM calls create debugging nightmares. When failures occur deep in a pipeline, isolating the root cause requires reproducing exact conditions - model responses, context, and state that may be impossible to recreate.

### The Problem

Many developers try to debug AI pipelines by re-running them from scratch, hoping to recreate the failure. This creates challenges that aren't immediately obvious:

```python
# BEFORE: No replay capability
from mirascope.core import anthropic, prompt_template
import lilypad

@lilypad.trace()
@anthropic.call("claude-3-5-sonnet-20241022")
@prompt_template("Classify the sentiment of this message: {text}")
def classify_sentiment(text: str) -> str:
    pass

@lilypad.trace()
@anthropic.call("claude-3-5-sonnet-20241022")
@prompt_template("Generate a helpful response for a {sentiment} customer message: {text}")
def generate_response(sentiment: str, text: str) -> str:
    pass

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

### The Solution: LLM Cassette Recording

A better approach is to record LLM interactions to "cassettes" that can be replayed exactly, similar to how VCRpy works for HTTP requests. This pattern captures problematic responses and lets you debug them repeatedly without making new API calls.

```python
# AFTER: Simple cassette recording decorator
from mirascope.core import anthropic, prompt_template
import lilypad
import json
import os
from functools import wraps
from typing import Any, Dict

def use_cassette(cassette_name: str):
    """Decorator that records/replays LLM calls to a cassette file"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cassette_path = f"cassettes/{cassette_name}.json"
            
            # Create cassettes directory if it doesn't exist
            os.makedirs("cassettes", exist_ok=True)
            
            # Create a key from function name and arguments
            call_key = f"{func.__name__}:{str(args)}:{str(sorted(kwargs.items()))}"
            
            # Try to load existing cassette
            cassette_data = {}
            if os.path.exists(cassette_path):
                with open(cassette_path, 'r') as f:
                    cassette_data = json.load(f)
            
            # Check if we have a recorded response
            if call_key in cassette_data:
                print(f"🎬 Replaying {func.__name__} from cassette")
                return cassette_data[call_key]
            
            # No recording found - make real call and record it
            print(f"🔴 Recording {func.__name__} to cassette")
            result = func(*args, **kwargs)
            
            # Save the result to cassette
            cassette_data[call_key] = result
            with open(cassette_path, 'w') as f:
                json.dump(cassette_data, f, indent=2)
            
            return result
        return wrapper
    return decorator

# Use the cassette decorator on your AI functions
@use_cassette('customer_support_debug')
@lilypad.trace()
@anthropic.call("claude-3-5-sonnet-20241022")
@prompt_template("Classify the sentiment of this message: {text}")
def classify_sentiment(text: str) -> str:
    pass

@use_cassette('customer_support_debug')
@lilypad.trace()
@anthropic.call("claude-3-5-sonnet-20241022")
@prompt_template("Generate a helpful response for a {sentiment} customer message: {text}")
def generate_response(sentiment: str, text: str) -> str:
    pass

def process_customer_message(message: str) -> str:
    sentiment = classify_sentiment(message)
    response = generate_response(sentiment, message)
    return response

# First run records to cassette
print("Processing problematic message...")
result = process_customer_message("I can't access my billing information")
print(f"Result: {result}")

# Subsequent runs replay identical responses for debugging
print("\nDebugging with identical responses...")
debug_result = process_customer_message("I can't access my billing information")
print(f"Debug result: {debug_result}")
```

**Why this approach works better:**

- **Perfect Reproduction:** Cassettes capture exact responses, making any failure reproducible indefinitely
- **Zero-Cost Debugging:** Replay from cassettes eliminates API costs during troubleshooting sessions
- **Simple Implementation:** One decorator provides VCRpy-style recording without complex infrastructure

### The Takeaway

Cassette recording transforms unpredictable AI debugging into systematic troubleshooting by capturing exact responses. This simple decorator pattern makes elusive bugs reproducible and eliminates the cost of repeated debugging attempts.

---
*Part of the "Effective AI Engineering" series - practical tips for building better applications with AI components.*