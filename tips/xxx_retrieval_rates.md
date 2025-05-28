## Effective AI Engineering #xxx: Monitor Chunk Retrieval Rates - Find the Overused and the Forgotten

**Are some chunks in your RAG system carrying all the weight while others sit unused?** Uneven retrieval patterns reveal critical insights about your knowledge base that most teams completely miss.

When certain chunks get retrieved for 80% of queries while others never see the light of day, you're looking at optimization opportunities hiding in plain sight. If a chunk is pulled for most queries, ask yourself whether it should be in the system prompt. If a chunk never gets retrieved, ask why - is it irrelevant, uninformative, corrupted, or poorly formatted?

### The Solution: Simple Retrieval Rate Analysis

The key is having chunk and document IDs in all your traces (Tip #2). With proper tracking, you can query your lilypad traces to understand which chunks are overused or forgotten:

```python
# Analyze chunk retrieval patterns from production traces
import os
from lilypad import Lilypad
from collections import defaultdict

def analyze_chunk_retrieval_rates():
    """Get retrieval rates for all chunks from traces"""
    client = Lilypad()
    
    # Get all RAG traces with chunk information
    traces = client.projects.traces.list(
        project_uuid=os.environ.get("PROJECT_ID"),
        function_name="answer_with_rag"  # Your instrumented RAG function
    )
    
    chunk_retrievals = defaultdict(int)
    total_queries = len(traces)
    
    # Count how often each chunk was retrieved
    for trace in traces:
        chunk_ids = trace.get('arg_values', {}).get('retrieved_chunk_ids', [])
        for chunk_id in chunk_ids:
            chunk_retrievals[chunk_id] += 1
    
    # Calculate retrieval rates
    chunk_rates = {
        chunk_id: count / total_queries 
        for chunk_id, count in chunk_retrievals.items()
    }
    
    return chunk_rates, total_queries

def show_retrieval_extremes():
    """Show the most and least retrieved chunks"""
    chunk_rates, total_queries = analyze_chunk_retrieval_rates()
    
    # Sort chunks by retrieval rate
    sorted_chunks = sorted(chunk_rates.items(), key=lambda x: x[1], reverse=True)
    
    # Get top and bottom 5%
    num_chunks = len(sorted_chunks)
    top_5_percent = max(1, num_chunks // 20)
    
    print(f"Analyzed {total_queries} queries across {num_chunks} chunks\n")
    
    print("TOP 5% - Most Retrieved Chunks:")
    for chunk_id, rate in sorted_chunks[:top_5_percent]:
        print(f"  {chunk_id}: {rate:.1%}")
    
    print("\nBOTTOM 5% - Least Retrieved Chunks:")
    for chunk_id, rate in sorted_chunks[-top_5_percent:]:
        print(f"  {chunk_id}: {rate:.1%}")
```

**What to do with these insights:**

- **High retrieval rate chunks (>80%):** Consider moving to your system prompt instead of retrieval
- **Never retrieved chunks (0%):** Investigate for removal - likely irrelevant, corrupted, or poorly formatted
- **Pattern analysis:** Look for document-level patterns to improve your chunking strategy

### The Takeaway

Monitor your chunk retrieval patterns to find optimization opportunities. Overused chunks might belong in your system prompt, while never-retrieved chunks are dead weight. This simple analysis requires chunk IDs in your traces but reveals powerful insights for improving your RAG system.

---
*Part of the "Effective AI Engineering" series - practical tips for building better applications with AI components.*