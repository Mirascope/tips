## Tip #5: Give Your LLM Context - Simple RAG with BM25

LLMs are incredibly powerful, but they have limitations. They don't know about events after their training cut-off date, and crucially, they don't have access to your private documents, internal knowledge bases, or specific company context. Relying solely on the model's pre-trained knowledge often leads to outdated or incomplete answers when dealing with specific, internal, or recent information.

**The Problem: LLMs Lack Your Context**

* **Knowledge Cut-offs:** Models can't answer questions about very recent developments.
* **No Private Data Access:** They can't answer questions based on your internal wikis, documents, codebases, or databases.
* **Context Window Limits:** While context windows are growing, stuffing massive amounts of raw text isn't always effective. Models can struggle to find the relevant "needle" in a giant contextual "haystack" ("lost in the middle" problem), and you often have far more internal knowledge than fits even in the largest windows.

**The Solution: Retrieval-Augmented Generation (RAG)**

The core idea is simple and powerful: **Retrieve relevant information first, then give that context to the LLM along with the user's query.** This grounds the LLM's response in factual, relevant, and up-to-date information specific to the query. Context is King!

**Getting Started Simply: BM25 Retrieval (No Embeddings Needed Yet!)**

Information Retrieval (IR) is a mature field, and you don't need complex vector embeddings to get started with RAG. A fantastic baseline technique is **Okapi BM25**, a keyword-based ranking algorithm that's efficient and often surprisingly effective.

* **Benefits of BM25:** It's fast, well-understood, doesn't require managing embedding models or vector databases, and works directly on text. It's a great way to build an initial RAG system quickly.

**Example (Simple RAG using `bm25s` and Mirascope - No Chunking):**

This example shows the basic flow: index whole documents, retrieve the most relevant one(s) with BM25, and pass them to Mirascope. **Note:** For simplicity, we are using entire documents here and skipping document *chunking* (splitting docs into smaller pieces), which is often a crucial step for better retrieval quality in real-world systems (we might cover chunking strategies in another tip!).

```python
import os
from mirascope import llm, prompt_template, response_model
from pydantic import BaseModel, Field
from typing import List

# Assume necessary libraries are installed:
# pip install mirascope bm25s python-dotenv openai
import bm25s # Using the bm25s library per user example
from dotenv import load_dotenv

# Load API keys from .env file (ensure OPENAI_API_KEY is set)
load_dotenv()

# --- RAG Setup ---

# 1. Your Documents (Using whole documents for simplicity here)
#    In practice, these could be loaded from files, databases, etc.
documents = [
    "Project Alpha: Focused on backend API improvements using Python and FastAPI. Key contact: alice@example.com. Status: On track.",
    "Project Beta: Developing a new user interface with React. UI mockups due next week. Key contact: bob@example.com. Status: Planning.",
    "Company Policy: Standard work hours are 9 AM to 5 PM local time. Remote work requires manager approval. Dress code is business casual.",
    "Onboarding Guide: New hires should complete IT setup and HR paperwork within the first week. Contact hr@example.com for questions.",
    "API Documentation: The /users endpoint returns user profiles. Requires authentication token. Use GET request.",
    "Project Alpha: Final testing phase begins next Monday. Deployment target is end of month.", # Update for Alpha
]

# 2. Build the BM25 Retriever Index
def build_bm25_retriever(docs: List[str]):
    """Builds and returns a bm25s retriever index."""
    print(f"Building BM25 index for {len(docs)} documents...")
    # Tokenize the documents (default whitespace tokenizer in bm25s)
    corpus_tokens = bm25s.tokenize(docs)
    # Create and index the retriever
    retriever = bm25s.BM25() # Default model is BM25L, often works well
    retriever.index(corpus_tokens)
    print("BM25 index built successfully.")
    return retriever

# Build the index once (or whenever documents update)
retriever = build_bm25_retriever(documents)

def retrieve_docs(retriever, query: str, k: int) -> list[str]:
    query_tokens = bm25s.tokenize(query)
    return retriever.retrieve(query_tokens, k=k)[0]


# --- Mirascope Prompt and Call Function ---
class RagResponse(BaseModel):
    answer: str = Field(description="The answer generated based on the provided context and query.")

# Define the prompt template incorporating retrieved context
RAG_PROMPT_TEMPLATE = """
SYSTEM: You are a helpful AI assistant. Answer the user's query based *only*
on the provided context below. If the answer is not in the context,
state that you don't have enough information.

CONTEXT:
---
{context_str}
---

USER QUERY: {query}
"""

@llm("openai", model="gpt-4o-mini", response_model=RagResponse) # Ensure OPENAI_API_KEY is set
@prompt_template(RAG_PROMPT_TEMPLATE)
def answer_with_rag(query: str, docs: list[str]):
    """Generates an answer using Mirascope based on query and retrieved context."""
    return {"computed_fields": {"context_string": "\n\n".join(docs)}}

# --- Usage Flow ---
user_query = "What is the status of Project Alpha and who is the contact?"
k = 2 # Number of documents to retrieve
# 4. Extract Content of Retrieved Documents
retrieved_docs = retrieve_docs(user_query, k=k)

response_object: RagResponse = answer_with_rag(
    query=user_query,
    context_str=context_string
)
print("\nFinal LLM Answer:", response_object.answer)
```

**Why this simple RAG approach is valuable:**

* **Provides Necessary Context:** Directly addresses the LLM's knowledge gaps with relevant information.
* **Leverages Mature IR:** Uses a well-established, efficient keyword-based retrieval method (BM25).
* **Easy Starting Point:** Creates a functional RAG system without the immediate complexity of setting up embedding models and vector stores. It establishes a strong baseline to compare against later.

**The Takeaway:**

Don't let your LLM operate in an information vacuum! **Start implementing RAG by retrieving relevant context before calling the LLM.** Using a simple, effective method like BM25 on your documents (even whole documents initially) is an excellent first step to ground your LLM responses in reality, providing immediate value with relatively low complexity. You can always add more sophisticated techniques like chunking and embeddings later.