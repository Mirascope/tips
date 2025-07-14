---
tip_number: 9
tip_name: "Hybrid Search for Better RAG"
categories: ["retrieval", "performance", "quality-assurance"]
x_link: ""
linkedin_link: "https://www.linkedin.com/posts/skylarbpayne_are-you-struggling-with-rag-systems-that-activity-7327754797317566465-_1F2?utm_source=share&utm_medium=member_desktop&rcm=ACoAABKpCf4BI_Yx2u7h66sgi5z1NF3aEYFHgps"
---

## Effective AI Engineering #9: Hybrid Search for Better RAG

**Are you struggling with RAG systems that miss relevant information?** Keyword-based search often fails to find conceptually similar content when users phrase queries differently.

When users ask about "reducing UI lag" but your documents mention "improving application responsiveness," traditional search can fail to make the connection. This creates a frustrating experience where your AI assistant misses relevant information despite it being in your knowledge base.

### The Problem

Many developers approach retrieval by relying solely on either lexical search like BM25 or semantic search with embeddings. This creates challenges that aren't immediately obvious:

```python
# BEFORE: Keyword-only retrieval
from bm25s import BM25
from typing import List

# Initialize BM25 with document chunks
bm25_retriever = BM25([chunk.content for chunk in all_chunks])
query_tokens = bm25s.tokenize(user_query)

# Retrieve documents using only keyword matching
indices, scores = bm25_retriever.retrieve(query_tokens, k=5)
retrieved_chunks = [all_chunks[idx] for idx in indices[0]]

# Provide context to LLM based only on keyword matches
context_string = "\n\n".join([chunk.content for chunk in retrieved_chunks])
```

**Why this approach falls short:**

- **Synonym Blindness:** Can't match "UI lag" with "application responsiveness" when words don't overlap
- **Conceptual Gaps:** Misses documents that discuss the same concept using different terminology
- **Literal Matching:** Focuses on exact word matches rather than semantic meaning
- **Relevance Ambiguity:** May retrieve documents with keyword matches that aren't conceptually relevant

### The Solution: Hybrid Search

A better approach is to combine keyword search with semantic embeddings. This hybrid retrieval strategy uses both methods to find documents that match either the exact keywords or the conceptual meaning of the query.

```python
# AFTER: Hybrid search combining keywords and embeddings
def hybrid_retrieve(query: str, k: int = 5):
    # 1. Keyword-based retrieval with BM25
    query_tokens = bm25s.tokenize(query)
    indices, bm25_scores = bm25_retriever.retrieve(query_tokens, k=k)
    bm25_results = [(all_chunks_map[idx].id, score) 
                    for idx, score in zip(indices[0], bm25_scores[0])]
    
    # 2. Semantic retrieval using embeddings
    query_embedding = embedding_model.embed_query(query)
    vector_results = vector_store.similarity_search_with_score(
        query_embedding, k=k
    )
    
    # 3. Combine & re-rank results
    combined_scores = {}
    for chunk_id, score in bm25_results:
        combined_scores[chunk_id] = combined_scores.get(chunk_id, 0) + score * 0.5
    for chunk_id, score in vector_results:
        combined_scores[chunk_id] = combined_scores.get(chunk_id, 0) + score * 0.5
    
    # 4. Get final chunks based on combined scores
    sorted_ids = sorted(combined_scores.keys(), 
                        key=lambda cid: combined_scores[cid], 
                        reverse=True)
    return [all_chunks_map[cid] for cid in sorted_ids[:k]]
```

**Why this approach works better:**

- **Semantic Understanding:** Captures related concepts even when different terminology is used
- **Complementary Strengths:** BM25 excels at finding exact matches while embeddings capture meaning
- **Improved Recall:** Retrieves relevant documents that would be missed by either method alone
- **Better Ranking:** Prioritizes documents that score well in both keyword and semantic relevance

But even this example has a subtle issue! Can you see what it is? Check out Tip #10 to find out!

### The Takeaway

When building RAG systems, don't rely solely on keyword matching or embeddings—combine both for optimal results. This hybrid approach creates more robust information retrieval that understands both exact matches and semantic relationships, addressing the common problem of missed relevant information.

---
*Part of the "Effective AI Engineering" series - practical tips for building better applications with AI components.*