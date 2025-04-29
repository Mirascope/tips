Okay, Tip #9 will introduce embeddings for semantic search and the concept of hybrid search, building upon the BM25 baseline from Tip #5 and the chunking discussion from Tip #8.

---

**Tip #9: Better RAG - Embeddings & Hybrid Search for Relevance**

**Subject: Effective AI #9: Beyond Keywords - Semantic & Hybrid Search for RAG**

Hey team,

In Tip #5, we saw how BM25 provides a strong keyword-based baseline for RAG retrieval. It's fast and effective when users search using terms directly present in your documents. But what happens when users ask questions using synonyms, related concepts, or just different phrasing? Keyword search might miss relevant chunks entirely.

**The Limitation of Keywords:**

Imagine a document mentions "improving application responsiveness," but the user asks about "reducing UI lag." BM25 might struggle to connect these if the exact words don't overlap sufficiently.

**Enter Embeddings: Searching for Meaning**

This is where **embeddings** shine. An embedding model converts text (your query, your document chunks) into numerical vectors that capture semantic meaning. Similar concepts end up closer together in this vector space.

* **Semantic Search:** Instead of matching keywords, you embed the user's query and search for document chunks with the *closest embedding vectors*. This allows you to find chunks that are *conceptually similar*, even if they use different words. This is incredibly powerful for understanding user intent.

**The Limitation of (Pure) Semantics:**

While powerful, pure semantic search isn't perfect either. Sometimes, specific keywords, product codes, acronyms, or exact phrases *are* critical, and embedding models might occasionally retrieve chunks that are conceptually related but factually incorrect or miss the precise keyword match needed.

**The Best of Both Worlds: Hybrid Search**

Often, the most robust approach is **Hybrid Search**, which combines the strengths of keyword-based retrieval (like BM25) and semantic search (embeddings).

* **How it Works:** You typically run both searches independently for a given query. Then, you combine and re-rank the results. A common and effective re-ranking method is **Reciprocal Rank Fusion (RRF)**, which prioritizes documents that appear highly ranked in *both* result sets. Many modern vector databases and search platforms offer built-in hybrid search capabilities.

**Choosing an Embedding Model:**

Not all embedding models are created equal. Consider:

* **Performance:** Check benchmarks like MTEB (Massive Text Embedding Benchmark) for performance on tasks relevant to you (retrieval, clustering, etc.).
* **Domain:** Was the model trained on data similar to yours (e.g., general text, code, scientific papers)?
* **Dimensionality:** Higher dimensions can sometimes capture more nuance but require more storage/computation.
* **Cost & Speed:** Consider inference latency and cost if using API-based models.

**Example (Conceptual Hybrid Search Flow):**

This example shows the *structure* of performing hybrid search. It assumes you have a BM25 index (Tip #5/#8) and have indexed your chunk embeddings in a conceptual `vector_store`. The focus is on the flow, not the specific vector store implementation.

```python
import os
from mirascope import llm, prompt_template, response_model
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Tuple, Set

# Assume necessary libraries:
# pip install mirascope bm25s pydantic python-dotenv openai
import bm25s
from dotenv import load_dotenv
import lilypad # For tracing the retrieval function
# Conceptual imports for embedding and vector store interaction
# from openai import OpenAI # Or your embedding client
# from your_vector_db_client import VectorStoreClient # Replace with actual client

# --- Load Config & Initialize Clients ---
load_dotenv()
# Configure Lilypad
try:
    lilypad.configure()
    print("Lilypad configured.")
except Exception as e:
    print(f"WARN: Failed to configure Lilypad: {e}")

# Conceptual: Configure clients needed for embeddings & vector search
# client_openai = OpenAI()
# vector_store = VectorStoreClient(api_key=..., environment=...)
print("WARN: Vector store and embedding clients are conceptual placeholders.")
vector_store = None # Placeholder
client_openai = None # Placeholder

# --- Data Structures & Setup ---
# Assume Chunk model from Tip #8 exists
class Chunk(BaseModel):
    id: str # Unique ID for each chunk
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

# Assume you have a list of Chunk objects indexed in both BM25 and vector store
# all_chunks: List[Chunk] = load_and_chunk_documents(...) # From Tip #8 logic
# bm25_retriever = build_bm25_retriever([c.content for c in all_chunks]) # From Tip #5 logic
# index_chunks_in_vector_store(all_chunks) # Conceptual function
print("WARN: Chunk loading, BM25 index, and vector store indexing are placeholders.")
all_chunks_map: Dict[str, Chunk] = {} # Placeholder map from chunk ID to Chunk object
bm25_retriever = None # Placeholder

# --- Conceptual Embedding Function ---
def get_query_embedding(query: str) -> List[float]:
    """Gets embedding for the user query."""
    print(f"CONCEPTUAL: Getting embedding for query: '{query[:50]}...'")
    # Replace with actual call to embedding model API
    # if client_openai:
    #    response = client_openai.embeddings.create(...)
    #    return response.data[0].embedding
    return [0.0] * 1536 # Return dummy vector of appropriate dimension

# --- Hybrid Retrieval Function ---
@lilypad.trace(name="hybrid_rag_retrieval", versioning='automatic')
def hybrid_retrieve(
    query: str,
    k: int = 5,
    bm25_weight: float = 0.5, # Example weights for simple combination
    vector_weight: float = 0.5 # Often requires tuning or RRF
) -> List[Chunk]:
    """Performs hybrid search using BM25 and conceptual vector search."""
    print(f"\nPerforming hybrid retrieval for query: '{query}'")
    final_results: List[Chunk] = []
    retrieved_ids: Set[str] = set()

    # 1. BM25 Retrieval (Keyword)
    bm25_results: List[Tuple[str, float]] = [] # List of (chunk_id, score)
    if bm25_retriever and bm25s:
        try:
            query_tokens = bm25s.tokenize(query)
            indices, scores = bm25_retriever.retrieve(query_tokens, k=k)
            # Assuming indices map back correctly to chunk IDs in all_chunks_map
            # This mapping needs careful implementation based on how bm25 index was built
            # bm25_results = [(all_chunks_map[list(all_chunks_map.keys())[idx]].id, score)
            #                 for idx, score in zip(indices[0], scores[0])]
            print(f"BM25 retrieved {len(indices[0] if indices else 0)} candidates (conceptual mapping).")
            # Placeholder result IDs for flow:
            bm25_results = [("chunk_1", 0.9), ("chunk_3", 0.7)] # Dummy Data
        except Exception as e:
            print(f"Error during BM25 retrieval: {e}")

    # 2. Vector Retrieval (Semantic)
    vector_results: List[Tuple[str, float]] = [] # List of (chunk_id, score)
    try:
        query_embedding = get_query_embedding(query)
        if query_embedding and vector_store:
            # Conceptual call to vector store similarity search
            # results = vector_store.similarity_search_with_score(query_embedding, k=k)
            # vector_results = [(res.metadata['id'], res.score) for res in results]
            print(f"Vector search retrieved candidates (conceptual).")
            # Placeholder result IDs for flow:
            vector_results = [("chunk_2", 0.85), ("chunk_1", 0.8)] # Dummy Data
        else:
            print("Skipping vector search (client unavailable or embedding failed).")
    except Exception as e:
        print(f"Error during vector retrieval: {e}")

    # 3. Combine & Re-rank Results (Simple weighted score / placeholder for RRF)
    # In a real implementation, use RRF or a more robust method.
    # This simple example just combines, normalizes roughly, and sorts.
    combined_scores: Dict[str, float] = {}
    for chunk_id, score in bm25_results:
        combined_scores[chunk_id] = combined_scores.get(chunk_id, 0) + score * bm25_weight
    for chunk_id, score in vector_results:
        # Assuming vector score is similarity (higher is better)
        combined_scores[chunk_id] = combined_scores.get(chunk_id, 0) + score * vector_weight

    # Sort by combined score
    sorted_ids = sorted(combined_scores.keys(), key=lambda cid: combined_scores[cid], reverse=True)

    # 4. Retrieve final chunks (limit to k)
    final_chunk_ids = sorted_ids[:k]
    final_results = [all_chunks_map[cid] for cid in final_chunk_ids if cid in all_chunks_map] # Fetch from map
    retrieved_ids = {chunk.id for chunk in final_results}
    print(f"Hybrid search selected {len(final_results)} chunks: {retrieved_ids}")

    # Lilypad trace will capture input 'query', 'k' and output 'final_results'
    return final_results


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
user_query = "How can we improve UI responsiveness for Project Phoenix?"

# Call the HYBRID retrieval function (instrumented by Lilypad)
retrieved_chunks: List[Chunk] = hybrid_retrieve(query=user_query, k=3)

# Prepare context string for the LLM
context_string = "\n\n---\n\n".join([chunk.content for chunk in retrieved_chunks]) if retrieved_chunks else "No relevant context found."

print(f"\n--- Context Provided to LLM (Hybrid) ---")
print(context_string)
print("---------------------------------------")

# Call the LLM function (using Mirascope)
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

While keyword search (BM25) is a great starting point, **leverage embeddings for semantic search** to understand user intent better, especially with varied phrasing. For the most robust RAG retrieval, consider implementing **hybrid search** to combine the strengths of both keyword and semantic matching. Choose your embedding model wisely based on your data and performance needs. Instrument your retrieval function (whether keyword, semantic, or hybrid) with Lilypad to monitor and evaluate its effectiveness (Tip #6).