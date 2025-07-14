---
tip_number: 10
tip_name: "Refining RAG - Prioritize the Best Context with Reranking"
categories: ["retrieval", "quality-assurance", "performance"]
x_link: "https://x.com/skylar_b_payne/status/1922351237116125679"
linkedin_link: "https://www.linkedin.com/posts/skylarbpayne_worst-documents-coming-first-in-your-hybrid-activity-7328117170670899200-RLA5?utm_source=share&utm_medium=member_desktop&rcm=ACoAABKpCf4BI_Yx2u7h66sgi5z1NF3aEYFHgps"
---

## Effective AI Engineering #10: Refining RAG - Prioritize the Best Context with Reranking

**Are you struggling with merging results from different retrieval methods?** Hybrid search (Tip #9) improves recall by combining results from multiple retrievers, but simply averaging scores fails to properly rank the final list.

When combining BM25 and vector search as we saw in Tip #9, the naive approach of averaging scores is problematic. Different retrieval methods produce incomparable score distributions, making simple averaging mathematically unsound and potentially biasing your final results.

### The Problem

Many developers approach merging results from different retrievers with simple score averaging:

```python
# BEFORE: Problematic score merging approach
# Assume we have these helper functions already defined:
# - bm25_retrieve(query, k) -> Returns list of (chunk_id, score) tuples from BM25
# - vector_retrieve(query, k) -> Returns list of (chunk_id, score) tuples from vector DB
# - get_chunk_by_id(chunk_id) -> Returns the actual chunk object with content

def naive_hybrid_retrieve(query: str, k: int = 5):
    # Get results from both retrievers
    bm25_results = bm25_retrieve(query, k=k)
    vector_results = vector_retrieve(query, k=k)
    
    # Problematic: Direct averaging of incomparable scores
    combined_scores = {}
    for chunk_id, score in bm25_results:
        combined_scores[chunk_id] = combined_scores.get(chunk_id, 0) + score * 0.5
    for chunk_id, score in vector_results:
        combined_scores[chunk_id] = combined_scores.get(chunk_id, 0) + score * 0.5
    
    # Sort and return results based on flawed combined scores
    sorted_ids = sorted(combined_scores.keys(), 
                       key=lambda cid: combined_scores[cid], 
                       reverse=True)
    final_chunks = [get_chunk_by_id(chunk_id) for chunk_id in sorted_ids[:k]]
    
    return final_chunks
```

**Why this approach falls short:**

- **Different Score Ranges:** BM25 is generally unbounded, but vector similarity scores are generally between -1 and 1.
- **Different Distributions:** The statistical distribution of scores differs between methods
- **Loss of Information:** Simple averaging discards valuable relevance signals from each method
- **Arbitrary Weighting:** The 0.5 weight factor is arbitrary and may not reflect actual relevance

### The Solution: Two-Stage Retrieval with Reranking

A better approach is to implement a dedicated reranking step after your hybrid retrieval. This uses a more sophisticated model (like a cross-encoder) to re-score candidates from all retrieval methods, providing a unified, accurate ranking.

```python
# AFTER: Improved ranking with a dedicated reranker
from rerankers import Reranker, Document as RerankerDocument

# Initialize the reranker (once, at application startup)
ranker = Reranker("sentence-transformers", 
                 model_name="cross-encoder/ms-marco-MiniLM-L-6-v2")

def reranked_hybrid_retrieve(query: str, k_final: int = 5):
    # Stage 1: Get more candidates from each retriever to ensure good recall
    k_initial = 20  # Cast a wider net initially
    bm25_results = bm25_retrieve(query, k=k_initial)
    vector_results = vector_retrieve(query, k=k_initial)
    
    # Simply collect all unique chunks without trying to combine scores
    all_chunk_ids = set(id for id, _ in bm25_results).union(
        id for id, _ in vector_results
    )
    all_chunks = [get_chunk_by_id(chunk_id) for chunk_id in all_chunk_ids]
    
    # Stage 2: Rerank all candidates with a dedicated reranker
    def rerank_documents(query, chunks):
        # Prepare documents for reranking
        docs_for_reranker = [
            RerankerDocument(text=chunk.content, doc_id=chunk.id) 
            for chunk in chunks
        ]
        
        # Get unified relevance scores from reranker
        results = ranker.rank(query=query, docs=docs_for_reranker)
        
        # Map back to original chunks and return in ranked order
        chunk_map = {chunk.id: chunk for chunk in chunks}
        return [
            chunk_map[result.document.doc_id] 
            for result in results.results
        ]
    
    # Apply reranking and select final top-k candidates
    reranked_chunks = rerank_documents(query, all_chunks)
    final_chunks = reranked_chunks[:k_final]
    
    return final_chunks
```

**Why this approach works better:**

- **Unified Scoring Model:** The reranker applies consistent evaluation criteria across all candidates
- **Query-Document Interactions:** Cross-encoders analyze query and document together, not independently
- **Semantic Understanding:** Rerankers can recognize complex relationships between query and content
- **True Relevance Ranking:** Results are ordered by actual relevance, not arbitrary score combinations

### The Takeaway

Hybrid search improves recall, but properly ranking the combined results requires a dedicated reranking step. Instead of unsound score averaging, use a specialized reranker as a final stage to generate unified, accurate relevance scores. This approach gives you the best of both worlds: the broad recall of hybrid search with the precision focus of reranking.

---
*Part of the "Effective AI Engineering" series - practical tips for building better applications with AI components.*