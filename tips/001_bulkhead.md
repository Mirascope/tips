## Effective AI Tip #1: Build Bulkheads Around Your AI Calls!

AI components (especially LLMs) have unique failure modes and operational needs (retries, specific logging, structured output handling) compared to typical application code. Mixing them directly creates brittle systems that are hard to manage.

**The Common Anti-Pattern:**

We often see code like this:

Python

```python
# <<< BEFORE: Direct Call within Business Logic >>>
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

**Why this is problematic:**

- **Reliability:** Where do you add retries just for `ai_service.completion` without cluttering `generate_response`? How do you handle specific AI errors gracefully?
- **Logging/Observability:** Need to log the exact prompt, raw response, latency, token counts? You have to manually add that logging *here*, and potentially everywhere else `ai_service` is called.
- **Structured Output:** What if you need JSON, not just a string? You parse the `response_text` *after* the call, mixing parsing logic with core application flow. Validation becomes an afterthought.
- **Maintenance:** Changing the underlying AI model, adding Chain-of-Thought prompting, or needing different parsing logic requires modifying `generate_response` directly, increasing the risk of breaking unrelated business logic.

**The Better Way: The Bulkhead Pattern**

Isolate the AI call behind a dedicated function or class. This acts as a "bulkhead," containing the AI's specific needs and protecting the rest of your application. [Bulkheads are named after sectioned partitions of a ship's hull](https://learn.microsoft.com/en-us/azure/architecture/patterns/bulkhead), which prevents damage from one section causing water
leakage to another.

Here's the *principle* demonstrated using `mirascope` (but you can implement this pattern yourself!):

Python

```python
# <<< AFTER: Isolated AI Call >>>
PROMPT_TEMPLATE = """
SYSTEM: You are a helpful assistant that generates concise, accurate responses to user queries.
Use only the provided document information. If you don't know, say so.

CONTEXT:
---
{docs}
---

USER QUERY: {query}
""" # Keep prompts separate

class GenResponse(BaseModel): # Define desired structure
  response: str
  # Add Pydantic validators here for output checking!

# The "Bulkhead" Function - dedicated to the AI interaction
@llm.call(provider='openai', model='gpt-4o-mini', response_model=GenResponse) # Handles call, parsing, retries (via decorators)
@prompt_template(PROMPT_TEMPLATE)
def generate_response_llm(query: str, docs: list[Document]): ... # Definition focuses purely on inputs/outputs

# Main business logic - cleaner and decoupled
def generate_response(query: str) -> str:
  # Business logic
  docs = search(query)

  # Call the isolated AI function (the bulkhead)
  structured_output = generate_response_llm(query, docs) # Handles retries, parsing, validation internally!

  # Business logic using reliable, structured data
  return structured_output.response # Access the validated field

```

**Why this "Bulkhead" is better**

- **Targeted Reliability:** Need retries? Add a retry decorator (`@retry(...)`) to `generate_response_llm` – it doesn't touch `generate_response`.
- **Clean Structured Output:** Define the `GenResponse` model. The framework (or your custom wrapper) handles parsing and validation *within the bulkhead*. `generate_response` receives clean, validated data.
- **Centralized Control:** Want to add Chain-of-Thought? Update the `PROMPT_TEMPLATE` and maybe `GenResponse`. Need better parsing? Add a parsing decorator to `generate_response_llm`. Changes are localized.
- **Simplified Observability:** Instrument `generate_response_llm` once (e.g., using tracing tools like `lilypad` or manual logging) to capture all AI interaction details (prompt, raw/parsed response, latency, cost) consistently.

**The Takeaway**

Don't let AI calls bleed into your core logic. **Wrap them in dedicated functions/classes (Bulkheads)** to handle their unique reliability, input/output, and observability needs. This isolation makes your system more robust, maintainable, and easier to evolve.