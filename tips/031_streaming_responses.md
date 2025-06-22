## Effective AI Engineering #31: Streaming Responses

**Are your users staring at blank screens while your AI thinks?** They wait 10 seconds for a complete response when they could be reading the first sentence in under 2 seconds.

Long AI responses create perceived latency that frustrates users, even when the total generation time is reasonable. Users prefer to start reading immediately rather than waiting for complete responses, especially for explanations, summaries, or step-by-step instructions.

### The Problem

Many developers wait for complete LLM responses before showing anything to users. This creates challenges that aren't immediately obvious:

```python
# BEFORE: Waiting for complete responses
from mirascope.core import llm
import lilypad
import time

@lilypad.trace()
@llm.call(provider="openai", model="gpt-4o-mini")
def explain_concept(concept: str) -> str:
    return f"""
    Explain this concept in detail: {concept}
    Provide a comprehensive explanation with examples and practical applications.
    """

def handle_explanation_request(concept: str) -> str:
    print(f"Generating explanation for: {concept}")
    start_time = time.time()
    
    # User sees nothing until complete response is ready
    response = explain_concept(concept)
    
    end_time = time.time()
    print(f"Response ready after {end_time - start_time:.2f} seconds")
    print(f"Full response: {response}")
    
    return response

# User experience: 8+ seconds of blank screen, then wall of text
result = handle_explanation_request("machine learning")
```

**Why this approach falls short:**

- **Poor Perceived Performance:** Users feel the system is slow even when generation time is reasonable
- **No Progressive Disclosure:** Long responses overwhelm users instead of building understanding incrementally
- **Higher Abandonment:** Users may leave before seeing any output from complex queries

### The Solution: Token-Level Streaming

A better approach is to stream tokens as they're generated and display partial responses immediately. This pattern dramatically improves perceived performance and user engagement.

```python
# AFTER: Real-time streaming responses
from mirascope.core import llm
import lilypad
import asyncio
import time
from typing import AsyncGenerator

@lilypad.trace()
@llm.call(provider="openai", model="gpt-4o-mini", stream=True)
async def explain_concept_streaming(concept: str) -> AsyncGenerator[str, None]:
    return f"""
    Explain this concept in detail: {concept}
    Provide a comprehensive explanation with examples and practical applications.
    """

# Streaming state for functional approach
buffer = ""
sentence_markers = ['.', '!', '?', '\n']

async def render_progressive(token_stream: AsyncGenerator[str, None]):
    """Render tokens as they arrive, with smart sentence boundaries"""
    global buffer
    start_time = time.time()
    first_token_time = None
    
    async for token in token_stream:
        if first_token_time is None:
            first_token_time = time.time()
            print(f"First token arrived after: {first_token_time - start_time:.2f}s")
            print("=== STREAMING RESPONSE ===")
        
        buffer += token
        
        # Show complete sentences immediately
        if any(marker in token for marker in sentence_markers):
            # Find last complete sentence
            last_marker_idx = max([
                buffer.rfind(marker) for marker in sentence_markers
            ])
            
            if last_marker_idx > 0:
                complete_text = buffer[:last_marker_idx + 1]
                remaining = buffer[last_marker_idx + 1:]
                
                # Render complete sentences
                print(f"\rCurrent output: {complete_text.strip()}", flush=True)
                
                buffer = remaining
        
        # Small delay to simulate real streaming
        await asyncio.sleep(0.05)
    
    # Render any remaining content
    if buffer.strip():
        print(f"\rFinal output: {buffer.strip()}")
    
    end_time = time.time()
    print(f"\n=== STREAMING COMPLETE ===")
    print(f"Total time: {end_time - start_time:.2f}s")
    print(f"Time to first token: {first_token_time - start_time:.2f}s")

@lilypad.trace()
async def handle_streaming_explanation(concept: str) -> str:
    print(f"Starting streaming explanation for: {concept}")
    
    # Get streaming response
    token_stream = explain_concept_streaming(concept)
    
    # Render progressively
    await render_progressive(token_stream)
    
    return "Streaming complete"

async def render_structured_response(concept: str):
    """Advanced renderer that streams structured content"""
    # Define sections to stream
    sections = [
        f"# Understanding {concept}\n",
        "## Overview\n",
        "## Key Concepts\n", 
        "## Examples\n",
        "## Practical Applications\n"
    ]
    
    section_content = {}
    current_section = None
    
    async for token in explain_concept_streaming(concept):
        # Detect section headers
        for section in sections:
            if section.strip() in token:
                current_section = section.strip()
                print(f"\n{section}")
                section_content[current_section] = ""
                continue
        
        # Accumulate content for current section
        if current_section:
            section_content[current_section] += token
            
            # Stream content as it builds
            if any(marker in token for marker in ['.', '\n']):
                print(f"{section_content[current_section]}", end='', flush=True)
                section_content[current_section] = ""
        
        await asyncio.sleep(0.03)

# Example usage showing improved user experience
async def demo_streaming_vs_blocking():
    concept = "neural networks"
    
    print("=== BLOCKING APPROACH ===")
    start = time.time()
    
    # Simulate what user sees with blocking
    print("🤔 Thinking...")
    await asyncio.sleep(3)  # Simulated generation time
    print("✅ Here's your complete explanation!")
    print("Neural networks are computational models inspired by biological neural networks...")
    
    blocking_time = time.time() - start
    print(f"User waited {blocking_time:.1f}s before seeing anything\n")
    
    print("=== STREAMING APPROACH ===")
    start = time.time()
    
    # Show streaming experience
    await asyncio.sleep(0.2)  # Minimal latency to first token
    first_token_time = time.time() - start
    
    print("Neural networks are...")
    await asyncio.sleep(0.5)
    print("Neural networks are computational models...")
    await asyncio.sleep(0.5) 
    print("Neural networks are computational models inspired by biological neural networks...")
    
    streaming_time = time.time() - start
    print(f"\nUser saw content after {first_token_time:.1f}s")
    print(f"Complete response after {streaming_time:.1f}s")
    print(f"Perceived performance improvement: {(blocking_time - first_token_time) / blocking_time * 100:.0f}%")

# Run demonstration
if __name__ == "__main__":
    asyncio.run(demo_streaming_vs_blocking())
    
    print("\n" + "="*50)
    print("REAL STREAMING EXAMPLE")
    print("="*50)
    
    asyncio.run(handle_streaming_explanation("machine learning"))
```

**Why this approach works better:**

- **Instant Feedback:** Users see content within 200ms instead of waiting for complete responses
- **Progressive Understanding:** Complex topics build understanding incrementally rather than overwhelming users
- **Better Engagement:** Users stay engaged reading partial content instead of waiting on blank screens

### The Takeaway

Streaming responses transform long AI outputs from blocking operations into engaging real-time experiences. This pattern dramatically improves perceived performance by showing partial results immediately while responses generate.

---
*Part of the "Effective AI Engineering" series - practical tips for building better applications with AI components.*