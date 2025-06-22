## Effective AI Engineering #30: Speculative Calls

**Are your users waiting seconds for simple yes/no decisions?** Your AI classifies user intent, then routes to the appropriate handler, but that sequential flow adds unnecessary latency to your hot path.

When AI workflows involve classification followed by specialized processing, the linear approach forces users to wait for each step. But if you can predict the likely outcome, you can start expensive work early and provide instant responses.

### The Problem

Many developers implement AI workflows as strict sequences, waiting for each step before starting the next. This creates challenges that aren't immediately obvious:

```python
# BEFORE: Sequential processing with classification bottleneck
from mirascope.core import llm
import lilypad
import time

@lilypad.trace()
@llm.call(provider="openai", model="gpt-4o-mini")
def classify_request(user_request: str) -> str:
    return f"Classify this request as 'simple' or 'complex': {user_request}"

@lilypad.trace()
@llm.call(provider="openai", model="gpt-4o-mini")
def handle_simple_request(user_request: str) -> str:
    return f"Handle this simple request: {user_request}"

@lilypad.trace()
@llm.call(provider="openai", model="gpt-4o-mini")
def handle_complex_request(user_request: str) -> str:
    return f"Handle this complex request with detailed analysis: {user_request}"

@lilypad.trace()
def process_user_request(user_request: str) -> str:
    start_time = time.time()
    
    # Step 1: Classify (adds latency)
    classification = classify_request(user_request)
    print(f"Classification took: {time.time() - start_time:.2f}s")
    
    # Step 2: Route based on classification
    if classification == "simple":
        result = handle_simple_request(user_request)
    else:
        result = handle_complex_request(user_request)
    
    print(f"Total time: {time.time() - start_time:.2f}s")
    return result

# Sequential approach - classification blocks processing
result = process_user_request("What's the weather like?")
```

**Why this approach falls short:**

- **Sequential Latency:** Users wait for classification before any real work begins
- **Underutilized Resources:** System idles during classification instead of doing useful work
- **Poor User Experience:** Simple requests feel slow despite having fast answers

### The Solution: Parallel Speculative Execution

A better approach is to predict likely outcomes and start work speculatively in parallel with classification. This pattern optimizes for the common case while gracefully handling mispredictions.

```python
# AFTER: Speculative parallel processing
from mirascope.core import llm
import lilypad
import asyncio
import time
from typing import Tuple

# Simple heuristics for quick prediction
simple_patterns = [
    "what's the weather",
    "what time is it",
    "hello",
    "how are you",
    "thank you"
]

def predict_classification(request: str) -> Tuple[str, float]:
    """Quick prediction based on patterns - no LLM call"""
    request_lower = request.lower()
    
    for pattern in simple_patterns:
        if pattern in request_lower:
            return "simple", 0.85  # High confidence
    
    # Default to complex for unknown patterns
    return "complex", 0.6  # Lower confidence for unknown patterns

@lilypad.trace()
@llm.call(provider="openai", model="gpt-4o-mini")
async def classify_request_async(user_request: str) -> str:
    return f"Classify this request as 'simple' or 'complex': {user_request}"

@lilypad.trace()
@llm.call(provider="openai", model="gpt-4o-mini")
async def handle_simple_request_async(user_request: str) -> str:
    return f"Handle this simple request: {user_request}"

@lilypad.trace()
@llm.call(provider="openai", model="gpt-4o-mini")
async def handle_complex_request_async(user_request: str) -> str:
    return f"Handle this complex request with detailed analysis: {user_request}"

@lilypad.trace()
async def speculative_request_processor(user_request: str, confidence_threshold: float = 0.8) -> str:
    start_time = time.time()
    
    # Quick prediction without LLM
    predicted_type, confidence = predict_classification(user_request)
    print(f"Predicted: {predicted_type} (confidence: {confidence:.2f})")
    
    if confidence >= confidence_threshold:
        # High confidence - start speculative processing immediately
        print(f"Starting speculative {predicted_type} processing...")
        
        if predicted_type == "simple":
            # Start simple processing immediately, verify classification in parallel
            simple_task = asyncio.create_task(handle_simple_request_async(user_request))
            classification_task = asyncio.create_task(classify_request_async(user_request))
            
            # Wait for whichever finishes first
            done, pending = await asyncio.wait(
                [simple_task, classification_task],
                return_when=asyncio.FIRST_COMPLETED
            )
            
            if simple_task in done:
                # Speculative execution won - return result immediately
                result = simple_task.result()
                print(f"Speculative hit! Time: {time.time() - start_time:.2f}s")
                
                # Cancel classification if still running
                if classification_task in pending:
                    classification_task.cancel()
                
                return result
            else:
                # Classification finished first - check if prediction was correct
                actual_classification = classification_task.result()
                if actual_classification == "simple":
                    # Prediction was correct - wait for simple processing
                    result = await simple_task
                    print(f"Speculative hit (verified)! Time: {time.time() - start_time:.2f}s")
                    return result
                else:
                    # Prediction was wrong - cancel and do complex processing
                    simple_task.cancel()
                    print("Speculative miss - switching to complex processing")
                    result = await handle_complex_request_async(user_request)
                    print(f"Corrected result time: {time.time() - start_time:.2f}s")
                    return result
        else:
            # Predicted complex - still speculate but verify
            complex_task = asyncio.create_task(handle_complex_request_async(user_request))
            classification_task = asyncio.create_task(classify_request_async(user_request))
            
            # Wait for classification to verify prediction
            actual_classification = await classification_task
            
            if actual_classification == "complex":
                # Prediction correct - wait for complex result
                result = await complex_task
                print(f"Complex speculative hit! Time: {time.time() - start_time:.2f}s")
                return result
            else:
                # Prediction wrong - cancel and do simple processing
                complex_task.cancel()
                print("Speculative miss - switching to simple processing")
                result = await handle_simple_request_async(user_request)
                print(f"Corrected result time: {time.time() - start_time:.2f}s")
                return result
    else:
        # Low confidence - fall back to sequential processing
        print("Low confidence - using sequential processing")
        classification = await classify_request_async(user_request)
        
        if classification == "simple":
            result = await handle_simple_request_async(user_request)
        else:
            result = await handle_complex_request_async(user_request)
        
        print(f"Sequential fallback time: {time.time() - start_time:.2f}s")
        return result

# Example usage showing latency improvements
async def test_speculative_processing():
    test_requests = [
        "What's the weather like?",  # Predicted simple - should be fast
        "Hello there!",              # Predicted simple - should be fast  
        "Analyze the market trends for Q4", # Predicted complex
        "Can you help me debug this complex algorithm?" # Predicted complex
    ]
    
    for request in test_requests:
        print(f"\n=== Processing: {request} ===")
        result = await speculative_request_processor(request)
        print(f"Result: {result[:50]}...")

# Run the test
if __name__ == "__main__":
    asyncio.run(test_speculative_processing())
```

**Why this approach works better:**

- **Reduced Latency:** Common cases get instant responses without waiting for classification
- **Cost-Optimized Speculation:** Only speculate when confidence is high, avoiding wasteful parallel calls
- **Graceful Fallback:** Mispredictions are detected and corrected without user impact

### The Takeaway

Speculative calls eliminate classification bottlenecks by starting likely work in parallel, dramatically reducing latency for predictable requests. This pattern optimizes user experience for common cases while maintaining correctness.

---
*Part of the "Effective AI Engineering" series - practical tips for building better applications with AI components.*