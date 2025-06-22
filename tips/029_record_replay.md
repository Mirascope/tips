## Effective AI Engineering #29: Record and Replay

**Does debugging your AI pipeline feel like hunting ghosts?** A user reports a bad response, but by the time you investigate, the AI generates something completely different and you can't reproduce the issue.

Complex AI workflows with multiple chained LLM calls create debugging nightmares. When failures occur deep in a pipeline, isolating the root cause requires reproducing exact conditions - model responses, context, and state that may be impossible to recreate.

### The Problem

Many developers try to debug AI pipelines by re-running them from scratch, hoping to recreate the failure. This creates challenges that aren't immediately obvious:

```python
# BEFORE: No replay capability
from mirascope.core import llm
import lilypad

@lilypad.trace()
@llm.call(provider="openai", model="gpt-4o-mini")
def classify_sentiment(text: str) -> str:
    return f"Classify sentiment: {text}"

@lilypad.trace()
@llm.call(provider="openai", model="gpt-4o-mini")
def generate_response(sentiment: str, original_text: str) -> str:
    return f"Generate response for {sentiment} sentiment: {original_text}"

@lilypad.trace()
def process_message(user_message: str) -> str:
    # Step 1: Classify sentiment
    sentiment = classify_sentiment(user_message)
    
    # Step 2: Generate appropriate response
    response = generate_response(sentiment, user_message)
    
    return response

# When this fails, debugging is difficult
result = process_message("I hate this product!")
```

**Why this approach falls short:**

- **Non-Reproducible Failures:** LLM stochasticity means re-running rarely recreates the exact failure
- **Expensive Debugging:** Each debug attempt consumes tokens and may not hit the problematic path
- **Lost Context:** Intermediate states and responses that caused the failure are gone forever

### The Solution: Trace Recording and Selective Replay

A better approach is to record all LLM interactions and enable selective replay of specific steps. This pattern lets you freeze problematic scenarios and debug them systematically without re-generating responses.

```python
# AFTER: Record/replay debugging system
from mirascope.core import llm
import lilypad
import json
import uuid
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

@dataclass
class CallRecord:
    id: str
    function_name: str
    inputs: Dict[str, Any]
    output: Any
    timestamp: datetime
    model_used: str

# Global recording state
recordings: Dict[str, CallRecord] = {}
replay_mode = False
replay_data: Dict[str, CallRecord] = {}

def record_call(function_name: str, inputs: Dict[str, Any], output: Any, model: str) -> str:
    call_id = str(uuid.uuid4())
    record = CallRecord(
        id=call_id,
        function_name=function_name,
        inputs=inputs,
        output=output,
        timestamp=datetime.now(),
        model_used=model
    )
    recordings[call_id] = record
    return call_id

def save_session(session_name: str):
    with open(f"recordings/{session_name}.json", "w") as f:
        json.dump({k: asdict(v) for k, v in recordings.items()}, f, default=str)

def load_session(session_name: str):
    global replay_data
    with open(f"recordings/{session_name}.json", "r") as f:
        data = json.load(f)
        replay_data = {
            k: CallRecord(**v) for k, v in data.items()
        }

def enable_replay_mode(session_name: str):
    global replay_mode
    load_session(session_name)
    replay_mode = True

def get_replay_response(function_name: str, inputs: Dict[str, Any]) -> Optional[Any]:
    if not replay_mode:
        return None
    
    # Find matching call in replay data
    for record in replay_data.values():
        if (record.function_name == function_name and 
            record.inputs == inputs):
            print(f"Replaying {function_name} with recorded response")
            return record.output
    
    return None

def recorded_call(func_name: str, model: str):
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Check if we're in replay mode first
            inputs = {"args": args, "kwargs": kwargs}
            replay_response = get_replay_response(func_name, inputs)
            
            if replay_response is not None:
                return replay_response
            
            # Normal execution - record the call
            result = func(*args, **kwargs)
            record_call(func_name, inputs, result, model)
            return result
        return wrapper
    return decorator

@lilypad.trace()
@recorded_call("classify_sentiment", "gpt-4o-mini")
@llm.call(provider="openai", model="gpt-4o-mini")
def classify_sentiment(text: str) -> str:
    return f"Classify sentiment: {text}"

@lilypad.trace()
@recorded_call("generate_response", "gpt-4o-mini")
@llm.call(provider="openai", model="gpt-4o-mini")
def generate_response(sentiment: str, original_text: str) -> str:
    return f"Generate response for {sentiment} sentiment: {original_text}"

@lilypad.trace()
@recorded_call("validate_response", "gpt-4o-mini")
@llm.call(provider="openai", model="gpt-4o-mini")
def validate_response(response: str) -> str:
    return f"Is this response appropriate? {response}"

@lilypad.trace()
def process_message_pipeline(user_message: str, session_id: str) -> str:
    print(f"Processing in session: {session_id}")
    
    # Step 1: Classify sentiment
    sentiment = classify_sentiment(user_message)
    print(f"Classified sentiment: {sentiment}")
    
    # Step 2: Generate response
    response = generate_response(sentiment, user_message)
    print(f"Generated response: {response}")
    
    # Step 3: Validate response
    validation = validate_response(response)
    print(f"Validation result: {validation}")
    
    # Save recording for potential replay
    save_session(session_id)
    
    return response

# Normal execution - records everything
def test_normal_execution():
    result = process_message_pipeline("I hate this product!", "failed_session_001")
    return result

# Replay mode - uses recorded responses
def test_replay_debugging():
    # Enable replay mode with problematic session
    enable_replay_mode("failed_session_001")
    
    # Now we can debug step by step with identical responses
    print("=== REPLAY MODE ===")
    
    # Test just sentiment classification
    sentiment = classify_sentiment("I hate this product!")
    print(f"Recorded sentiment: {sentiment}")
    
    # Test response generation with recorded sentiment
    response = generate_response(sentiment, "I hate this product!")
    print(f"Recorded response: {response}")
    
    # Disable replay to test alternative flows
    global replay_mode
    replay_mode = False
    print("\n=== TESTING FIXES ===")
    
    # Try different prompt or logic
    new_response = generate_response("negative", "I hate this product!")
    print(f"New response: {new_response}")

# Usage example
if __name__ == "__main__":
    # First run - record the problematic session
    print("Recording session...")
    test_normal_execution()
    
    print("\nDebugging with replay...")
    test_replay_debugging()
```

**Why this approach works better:**

- **Perfect Reproduction:** Recorded sessions replay identical responses, making bugs reproducible
- **Isolated Testing:** Debug individual pipeline steps without re-running expensive upstream calls
- **Cost-Effective Debugging:** Replay mode eliminates token costs during troubleshooting

### The Takeaway

Record and replay transforms unpredictable AI debugging into systematic troubleshooting by preserving exact failure conditions. This pattern makes complex pipeline bugs reproducible and debuggable without burning tokens.

---
*Part of the "Effective AI Engineering" series - practical tips for building better applications with AI components.*