## Effective AI #10: Refining RAG - Prioritize the Best Context with Reranking

In our RAG journey, we started with simple retrieval (Tip #5), explored improving it with chunking (Tip #8), and introduced embeddings and hybrid search (Tip #9) to cast a wider net and find semantically relevant documents (high *recall*).

**The Problem: Initial Retrieval Can Be Noisy**

However, optimizing for recall often means the initial set of retrieved documents (say, the top 20-50 candidates) can be noisy. It might contain highly relevant chunks mixed with others that are only tangentially related. Simply taking the top few from this initial set might not put the *absolute best* context at the top for the LLM.

**The Solution: Two-Stage Retrieval with Reranking**

Think of retrieval as a two-stage process:

1.  **Stage 1: Candidate Retrieval (Recall-Focused):** Use fast methods (BM25, vector search, hybrid) to retrieve a relatively large set of candidate documents.
2.  **Stage 2: Reranking (Precision-Focused):** Apply a more accurate model (like a cross-encoder via the `rerankers` library) to re-evaluate and re-order *only* this smaller candidate set, pushing the most relevant documents to the very top.

**Why Rerank?**

* **Optimize for Precision:** Ensures the top documents presented to the LLM are the most relevant.
* **Reduce Noise:** Filters out less relevant documents.
* **Improve LLM Focus:** Provides higher quality, more focused context.
* **Mitigate Hallucinations:** Less exposure to irrelevant context reduces unsupported statements.
* **Better Use of Context Window:** Ensures the most valuable information occupies the limited space.

**Common Reranking Techniques:**

The `rerankers` library provides easy access to several methods:

* **Cross-Encoders:** Models specifically trained to score (query, document) relevance accurately. Slower than initial retrieval but great for refining candidate sets. The library supports various cross-encoder models (needs installation/download) and API-based rerankers like Cohere.
* *(Other methods might be supported by the library or implemented custom)*

**Example (Reranking Flow with `rerankers` Library):**

This example integrates reranking using the `rerankers` library interface after an initial retrieval step (like the conceptual `hybrid_retrieve` from Tip #9).

```python
import os
from mirascope import llm, prompt_template, response_model
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Tuple

# Assume necessary libraries are installed:
# pip install mirascope pydantic python-dotenv openai rerankers
# pip install "rerankers[cohere]" # Example if using Cohere reranker
# pip install sentence-transformers # Example if using local cross-encoder
import lilypad # For tracing
from dotenv import load_dotenv

# Import from rerankers library based on screenshot/common usage
from rerankers import Reranker, Document as RerankerDocument

# --- Load Config & Initialize Clients ---
load_dotenv()
try:
    lilypad.configure() # Configure Lilypad (requires LILYPAD_API_KEY)
    print("Lilypad configured.")
except Exception as e: print(f"WARN: Failed to configure Lilypad: {e}")

# --- Initialize the Reranker ---
# Choose and initialize your reranker model via the library.
# This requires appropriate setup (API keys for Cohere, model download for local).
try:
    # Example: Using Cohere (Requires COHERE_API_KEY env var)
    # Check rerankers library docs for exact model names and initialization
    # ranker = Reranker("cohere", model_name="rerank-english-v3.0")

    # Example: Using a local Sentence Transformer cross-encoder
    # Needs `pip install sentence-transformers` and potentially model download
    ranker = Reranker("sentence-transformers", model_name="cross-encoder/ms-marco-MiniLM-L-6-v2") # Example model

    # Example: Using a different model available via the library
    # ranker = Reranker("flashrank", model_name="ms-marco-MiniLM-L-6-v2") # Needs flashrank[cpu] or flashrank[cuda]

    print(f"Reranker initialized with model: {ranker.model_name}") # Accessing assumed attribute
except Exception as e:
    print(f"WARN: Failed to initialize Reranker: {e}. Reranking will be skipped.")
    ranker = None

# --- Data Structures & Setup ---
class Chunk(BaseModel): # Your application's Chunk object
    id: str
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

# Assume hybrid_retrieve function exists (or any initial retrieval function)
# It should return a list of your application's Chunk objects
def initial_retrieve(query: str, k: int) -> List[Chunk]: # Stub for example
    print(f"CONCEPTUAL: Running initial retrieval for '{query}' (k={k})")
    # Placeholder implementation returning dummy Chunk objects
    return [
        Chunk(id="chunk_3", content="BM25 high score context for reranking test."),
        Chunk(id="chunk_1", content="Vector high score context, also relevant."),
        Chunk(id="chunk_5", content="Less relevant context A about unrelated projects."),
        Chunk(id="chunk_2", content="Highly relevant context about query but had lower initial score."),
        Chunk(id="chunk_4", content="Less relevant context B mentioning keywords tangentially."),
    ][:k]

# --- Reranking Function ---
@lilypad.trace(name="rerank_documents_library", versioning='automatic')
def rerank_documents(query: str, candidates: List[Chunk], reranker_model: Reranker | None) -> List[Chunk]:
    """Reranks candidate documents using the initialized rerankers library model."""
    print(f"Reranking {len(candidates)} candidates for query: '{query}'")
    if not candidates:
        return []
    if not reranker_model:
        print("WARN: Reranker model not available. Returning original candidates.")
        return candidates # Pass through if reranker isn't initialized

    try:
        # Prepare documents in the format expected by the rerankers library
        # Use the rerankers.Document class, preserving original IDs and metadata
        docs_for_reranker = [
            RerankerDocument(text=chunk.content, doc_id=chunk.id, metadata=chunk.metadata)
            for chunk in candidates
        ]

        # Use the ranker object initialized earlier
        # This call performs the actual reranking using the loaded model/API
        results = reranker_model.rank(query=query, docs=docs_for_reranker)
        # The result object `results` is of type RankedResults

        print(f"Reranker processed {len(results.results)} results.") # Accessing results attribute

        # Map the reranked results back to our application's Chunk objects
        # The results are already sorted by relevance score by the library
        original_chunks_map = {chunk.id: chunk for chunk in candidates}
        final_reranked_chunks = []
        for reranked_result in results.results: # Iterate through sorted results
            original_chunk = original_chunks_map.get(reranked_result.document.doc_id)
            if original_chunk:
                final_reranked_chunks.append(original_chunk)
                print(f"  - Reranked Score: {reranked_result.score:.4f}, Chunk ID: {original_chunk.id}")
            else:
                 print(f"WARN: Could not map reranked doc_id {reranked_result.document.doc_id} back to original chunk.")

        return final_reranked_chunks

    except Exception as e:
        print(f"Error during reranking using rerankers library: {e}")
        # Fallback: return original candidates? Or empty list?
        return candidates # Safest fallback might be original order


# --- Mirascope Prompt and Call Function (Same as Tip #5) ---
class RagResponse(BaseModel):
    answer: str = Field(description="The answer generated based on the provided context and query.")

RAG_PROMPT_TEMPLATE = """
SYSTEM: You are a helpful AI assistant... Answer based *only* on the context...

CONTEXT:
---
{context_str}
---

USER QUERY: {query}
ASSISTANT:
"""

@llm("openai", model="gpt-4o-mini", response_model=RagResponse)
@prompt_template(RAG_PROMPT_TEMPLATE)
def answer_with_rag(query: str, context_str: str):
    """Generates answer using Mirascope based on query and retrieved context."""
    pass

# --- Usage Flow ---
user_query = "Details about Project Phoenix timeline and tech stack?"
initial_k = 20 # Retrieve more candidates initially
final_k = 3  # Select the top N *after* reranking

# 1. Initial Retrieval (Recall-focused)
initial_candidates: List[Chunk] = initial_retrieve(query=user_query, k=initial_k)

# 2. Reranking (Precision-focused) - Instrumented by Lilypad
# Pass the initialized ranker object
reranked_candidates: List[Chunk] = rerank_documents(
    query=user_query,
    candidates=initial_candidates,
    reranker_model=ranker # Use the initialized reranker
)

# 3. Select Final Top-K Context after Reranking
final_context_chunks = reranked_candidates[:final_k]

# Prepare context string for the LLM
context_string = "\n\n---\n\n".join([chunk.content for chunk in final_context_chunks]) if final_context_chunks else "No relevant context found after reranking."

print(f"\n--- Final Context Provided to LLM (Reranked, Top {final_k}) ---")
print(context_string)
print("------------------------------------------------")

# 4. Call the LLM function (using Mirascope)
try:
    print("\nGenerating response with Mirascope...")
    response_object: RagResponse = answer_with_rag(
        query=user_query,
        context_str=context_string
    )
    print("\nFinal LLM Answer:", response_object.answer)
except Exception as e:
    print(f"Error generating Mirascope response: {e}")

```

**The Takeaway:**

Initial retrieval optimizes for recall. To ensure the *best* information reaches your LLM, **add a reranking step** using libraries like `rerankers` after initial retrieval. Use techniques like cross-encoders on the candidate set to improve *precision*, pushing the most relevant context to the top. This leads to more focused, accurate, and reliable RAG responses. Instrument your reranking step with Lilypad to monitor its performance too!