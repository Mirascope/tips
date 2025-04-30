from mirascope import llm, prompt_template

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

def search(query: str) -> list[str]:
  return ["doc1", "doc2", "doc3"]

# The "Bulkhead" Function - dedicated to the AI interaction
@llm.call(provider='openai', model='gpt-4o-mini') # Handles call, parsing, retries (via decorators)
@prompt_template(PROMPT_TEMPLATE)
def generate_response_llm(query: str, docs: list[str]): ... # Definition focuses purely on inputs/outputs

# Main business logic - cleaner and decoupled
def generate_response(query: str) -> str:
  # Business logic
  docs = search(query)

  # Call the isolated AI function (the bulkhead)
  return generate_response_llm(query, docs).content # Handles retries, parsing, validation internally!

print(generate_response('example query'))

