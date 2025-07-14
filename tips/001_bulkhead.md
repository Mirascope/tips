---
tip_number: 1
tip_name: "Build Bulkheads Around Your AI Calls"
categories: ["architecture", "error-handling", "integration"]
x_link: "https://x.com/skylar_b_payne/status/1917639950633255072"
linkedin_link: "https://www.linkedin.com/posts/skylarbpayne_effective-ai-tip-1-build-bulkheads-around-activity-7323404898300010496-pxTL?utm_source=share&utm_medium=member_desktop&rcm=ACoAABKpCf4BI_Yx2u7h66sgi5z1NF3aEYFHgps"
---

## Effective AI Engineering: Build Bulkheads Around Your AI Calls

**Is your AI service making your entire codebase fragile?** Random AI errors shouldn't crash your application or force you to litter retry logic throughout your code.

AI components (especially LLMs) have unique failure modes and operational requirements unlike typical application dependencies. Without proper isolation, they create brittle systems where AI-specific needs (retries, logging, parsing) contaminate your business logic, making the whole system harder to maintain and evolve.

### The Problem

Many developers integrate AI directly into their business logic, mixing concerns that should remain separate:

```python
# BEFORE: Direct Call within Business Logic
def generate_response(query: str) -> str:
  # Business logic: preparing data
  docs = search(query)
  prompt = make_generate_prompt(query, docs)

  # Direct, tightly-coupled AI call
  response_text = ai_service.completion(prompt) # What if this fails? Needs retries? Returns garbage?

  # More business logic potentially using the raw text
  # ... process response_text ...
  return processed_response
```

**Why this approach falls short:**

- **Reliability Issues:** Adding retries just for `ai_service.completion` clutters `generate_response`. AI-specific error handling becomes difficult to isolate.
- **Poor Observability:** Need to log prompts, responses, latency, and token counts? You'll add this logic everywhere the AI service is called, creating duplication and inconsistency.
- **Unstructured Outputs:** Parsing raw text responses and validating their structure happens after the call, mixing validation logic with core application flow.
- **Maintenance Challenges:** Changing the underlying AI model, modifying prompting techniques, or updating parsing logic requires modifying business functions directly, increasing the risk of breaking unrelated code.

### The Solution: The Bulkhead Pattern

A better approach is to isolate AI calls behind dedicated functions or classes. This "bulkhead" contains the AI's specific needs and protects the rest of your application from its unique behaviors. The pattern is named after ship hull partitions that prevent water damage in one section from spreading to others.

```python
# AFTER: Isolated AI Call with Clear Boundaries
PROMPT_TEMPLATE = """
SYSTEM: You are a helpful assistant that generates concise, accurate responses to user queries.
Use only the provided document information. If you don't know, say so.

## CONTEXT:
---
{docs}
---

USER: {query}
""" # Keep prompts separate

# The "Bulkhead" Function - dedicated to the AI interaction
@llm.call(provider='openai', model='gpt-4o-mini') # Handles call, parsing, retries (via decorators)
@prompt_template(PROMPT_TEMPLATE)
def generate_response_llm(query: str, docs: list[str]): ... # Definition focuses purely on inputs/outputs

# Main business logic - cleaner and decoupled
def generate_response(query: str) -> str:
  # Business logic
  docs = search(query)

  # Call the isolated AI function (the bulkhead)
  response = generate_response_llm(query, docs) # Handles retries, parsing, validation internally!
  
  # Business logic using reliable, structured data
  return response.content
```

**Why this approach works better:**

- **Targeted Reliability:** Need retries? Add a retry decorator (`@retry(...)`) to `generate_response_llm` – it won't affect your business logic. AI-specific errors are handled in one place.
- **Consistent Observability:** Instrument `generate_response_llm` once to capture all AI interaction details (prompt, response, latency, cost) consistently across your application.
- **Clean Structured Output:** Define a response model with validation. The bulkhead handles parsing and validation internally, so business logic receives clean, validated data every time.
- **Simplified Maintenance:** Need to update the prompt? Change the model? Add Chain-of-Thought? All these changes happen within the bulkhead, isolated from your business logic.

### The Takeaway

Don't let AI calls bleed into your core business logic. When you isolate AI interactions using the Bulkhead pattern, you gain better reliability, observability, and maintainability. This targeted isolation makes your AI integrations more robust against failures and easier to evolve as AI capabilities change.

---
*Part of the "Effective AI Engineering" series - practical tips for building better applications with AI components.*