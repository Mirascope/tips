---
tip_number: 17
tip_name: "Quality Control Your RAG Chunks"
categories: ["retrieval", "debugging", "quality-assurance"]
x_link: "https://x.com/skylar_b_payne/status/1925975125272191139"
linkedin_link: "https://www.linkedin.com/posts/skylarbpayne_rag-built-answers-still-suck-now-what-activity-7331741067093934081-uqeI?utm_source=share&utm_medium=member_desktop&rcm=ACoAABKpCf4BI_Yx2u7h66sgi5z1NF3aEYFHgps"
---

## Effective AI Engineering #17: Quality Control Your RAG Chunks

RAG Built. Answers still suck. Now what?

Even with great retrieval strategies, your RAG system can still surface low-quality chunks that crowd out useful information.

No matter how sophisticated your chunking approach, the reality of document processing means you'll end up with problematic chunks: duplicates, empty content, overly long passages, or chunks that dominate retrieval.
Running systematic quality checks helps identify and fix these issues before they degrade your RAG performance.

### The Problem

Many developers implement chunking and immediately move to indexing without validating chunk quality:

```python
# BEFORE: Chunk and Index Without Quality Control
chunks = []
for doc in documents:
    doc_chunks = chunk_document(doc)
    chunks.extend(doc_chunks)

# Directly index all chunks
vector_store.add_documents(chunks)
return vector_store
```

**Why this approach falls short:**

- **Duplicate Noise:** Identical or near-identical chunks waste storage and confuse retrieval by returning multiple versions of the same information.
- **Garbage Retrieval:** Low-information chunks (punctuation, headers, whitespace) get retrieved instead of meaningful content, wasting context budget.
- **Size Extremes:** Overly long chunks dilute relevance while tiny chunks lack sufficient context for meaningful retrieval.

### The Solution: Systematic Chunk Quality Control

A better approach is to implement quality control checks that identify and address problematic chunks before indexing. This ensures your RAG system only works with high-quality, retrievable content.

```python
# AFTER: Simple Quality Checks for Chunks
import hashlib
import re
from typing import List

def filter_chunks(chunks: List[str]) -> List[str]:
    # 1. Remove duplicates
    seen_hashes = set()
    unique_chunks = []
    for chunk in chunks:
        normalized = re.sub(r'\s+', ' ', chunk.strip().lower())
        chunk_hash = hashlib.md5(normalized.encode()).hexdigest()
        if chunk_hash not in seen_hashes:
            seen_hashes.add(chunk_hash)
            unique_chunks.append(chunk)
    
    # 2. Check size extremes (top/bottom 5%)
    # Note: you should look at your own chunks to see whether there is more filtering
    # you should do
    lengths = [len(chunk) for chunk in unique_chunks]
    lengths.sort()
    p5 = lengths[int(0.05 * len(lengths))]
    p95 = lengths[int(0.95 * len(lengths))]
    
    print(f"Chunk lengths - 5th percentile: {p5}, 95th percentile: {p95}")
    print(f"Shortest chunks (bottom 5%): {[c[:50] for c in unique_chunks if len(c) <= p5][:3]}")
    print(f"Longest chunks (top 5%): {[c[:50] for c in unique_chunks if len(c) >= p95][:3]}")
    
    # 3. Filter low-information chunks
    quality_chunks = []
    for chunk in unique_chunks:
        # Skip chunks that are just punctuation or whitespace
        if (len(chunk.strip()) < 20 or
            re.match(r'^[\s\.\,\;\:\!\?\-\(\)]*$', chunk) or
            len(chunk.split()) < 3):
            continue
        quality_chunks.append(chunk)
    
    print(f"Removed {len(chunks) - len(quality_chunks)} problematic chunks")
    return quality_chunks

# Use in your pipeline
all_chunks = [chunk_document(doc) for doc in documents]
clean_chunks = filter_chunks(all_chunks)
vector_store.add_documents(clean_chunks)
```

**Why this approach works better:**

- **Cleaner Index:** Removing duplicates and low-information chunks reduces noise and improves retrieval precision.
- **Better Relevance:** Examining size extremes helps identify chunks that are too short (lack context) or too long (dilute relevance).
- **Resource Efficiency:** Quality control reduces index size and computational overhead while improving performance.

### The Takeaway

Quality control is as important as chunking strategy itself. By systematically checking for duplicates, low-information content, and size extremes, you ensure your RAG system works with clean, high-quality chunks that actually improve response quality.

---
*Part of the "Effective AI Engineering" series - practical tips for building better applications with AI components.*
