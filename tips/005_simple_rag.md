## Effective AI Engineering #5: Give Your LLM Context - Simple RAG with BM25

**Is your LLM giving irrelevant or outdated answers?** When your AI assistant can't access your internal documents or recent information, it's severely limited in its ability to help.

LLMs are incredibly powerful, but they don't know about events after their training cut-off date, and crucially, they don't have access to your private documents, internal knowledge bases, or specific company context. Relying solely on the model's pre-trained knowledge often leads to outdated or incomplete answers when dealing with specific, internal, or recent information.

### The Problem

Many developers pass questions directly to LLMs without providing relevant context:

```python
# BEFORE: Asking Without Context
from mirascope import llm, prompt_template
from pydantic import BaseModel, Field

class Response(BaseModel):
    answer: str = Field(description="The answer to the user's question.")

PROMPT_TEMPLATE = """
SYSTEM: You are a helpful AI assistant.

USER: {query}
"""

@llm("openai", model="gpt-4o-mini", response_model=Response)
@prompt_template(PROMPT_TEMPLATE)
def answer_question(query: str): ...

def get_answer(user_query: str) -> str:
    # Direct call to LLM with no context
    response = answer_question(query=user_query)
    return response.answer
```

**Why this approach falls short:**

- **Knowledge Cut-offs:** Models can't answer questions about very recent developments.
- **No Private Data Access:** They can't answer questions based on your internal wikis, documents, codebases, or databases.
- **Context Window Limits:** While context windows are growing, stuffing massive amounts of raw text isn't always effective. Models can struggle to find the relevant "needle" in a giant contextual "haystack."
- **Consistency Issues:** Without specific reference material, answers can vary dramatically between calls or model versions.

### The Solution: Retrieval-Augmented Generation (RAG)

A better approach is to retrieve relevant information first, then give that context to the LLM along with the user's query. This grounds the LLM's response in factual, relevant, and up-to-date information specific to the query. Starting with BM25 (a classic keyword-based algorithm) is a simple yet powerful way to begin without the complexity of embeddings.

```python
# AFTER: Simple BM25-based RAG
import bm25s
from mirascope import llm, prompt_template
from pydantic import BaseModel, Field
from typing import List

# 1. Build the BM25 Retriever Index
def build_bm25_retriever(docs: List[str]):
    """Builds and returns a bm25s retriever index."""
    corpus_tokens = bm25s.tokenize(docs)
    retriever = bm25s.BM25()  # Default model is BM25L
    retriever.index(corpus_tokens)
    return retriever

# Sample documents (in practice, load from files/database)
documents = [
    "Project Alpha: Focused on backend API improvements. Contact: alice@example.com. Status: On track.",
    "Project Beta: Developing a new user interface with React. Contact: bob@example.com. Status: Planning.",
    "Company Policy: Remote work requires manager approval. Dress code is business casual.",
    "Onboarding Guide: New hires should complete IT setup within the first week. Contact hr@example.com.",
]

# Build the index once
retriever = build_bm25_retriever(documents)

def retrieve_docs(query: str, k: int = 2) -> list[str]:
    """Retrieves the k most relevant documents for a query."""
    query_tokens = bm25s.tokenize(query)
    return retriever.retrieve(query_tokens, k=k)[0]

# Define structured output - same as before
class Response(BaseModel):
    answer: str = Field(description="The answer based on the provided context and query.")

# Define the RAG prompt template
RAG_PROMPT_TEMPLATE = """
SYSTEM: You are a helpful AI assistant. Answer the user's query based *only*
on the provided context below. If the answer is not in the context,
state that you don't have enough information.

<context>
{context_str}
</context>

USER: {query}
"""

# Render each document in XML -- works best with most modern LLMs
def render_document(document: str) -> str:
    return f'<document>\n{document}\n</document>'

# The RAG function that puts it all together
@llm("openai", model="gpt-4o-mini", response_model=Response)
@prompt_template(RAG_PROMPT_TEMPLATE)
def answer_with_rag(query: str, documents: list[str]):
    return {'computed_fields': {'context_str': '\n'.join([render_document(doc) for doc in documents])}}

# Usage flow
def get_answer(user_query: str) -> str:
    # 1. Retrieve relevant documents
    retrieved_docs = retrieve_docs(user_query, k=2)
    
    # 2. Pass documents and query to the LLM
    response = answer_with_rag(query=user_query, documents=retrieved_docs)
    return response.answer
```

**Why this approach works better:**

- **Grounded in Facts:** Responses incorporate specific, relevant information that wasn't in the LLM's training data.
- **Simple Implementation:** BM25 is a mature, keyword-based retrieval algorithm that works directly on text without embeddings.
- **Reliability:** When answers come from your own documents, they're more consistent and accurate for your domain.
- **Minimal Setup:** This approach requires no vector databases or embedding models to get started - perfect for initial RAG implementations.

### The Takeaway

Don't let your LLM operate in an information vacuum! Start implementing RAG by retrieving relevant context before calling the LLM. Using a simple, effective method like BM25 is an excellent first step to ground your LLM responses in reality, providing immediate value with relatively low complexity. You can always add more sophisticated techniques like embeddings and vector search later, once you've proven the basic RAG concept.

---
*Part of the "Effective AI Engineering" series - practical tips for building better applications with AI components.*