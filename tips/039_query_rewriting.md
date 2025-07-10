## Effective AI Engineering #039: Query Rewriting for RAG

**Why does your RAG system return docs about "database optimization" when users ask about "my app is slow"?** Embedding similarity search breaks down when user language doesn't match your documentation's technical vocabulary.

This creates a frustrating user experience where your RAG system works great for precise technical queries but falls apart when users ask natural, conversational questions. The gap between how users think and how embeddings search becomes your system's biggest weakness.

### The Problem

Many developers rely entirely on embedding similarity to retrieve relevant documents. This creates challenges that aren't immediately obvious:

```python
# BEFORE: Direct embedding search
from mirascope import llm, prompt_template
import numpy as np

def search_documents(query: str, documents: list[str], embeddings: list) -> list[str]:
    query_embedding = get_embedding(query)
    similarities = [
        np.dot(query_embedding, doc_embedding) 
        for doc_embedding in embeddings
    ]
    top_indices = np.argsort(similarities)[-3:][::-1]
    return [documents[i] for i in top_indices]

def get_embedding(text: str):
    # Placeholder for embedding generation
    ...

# User asks: "How do I troubleshoot when my app is slow?"
# Embedding search might miss documents about "performance optimization" or "latency debugging"
```

**Why this approach falls short:**

- **Vocabulary Mismatch:** User language differs from document language, causing embedding misses
- **Context Loss:** Vague queries lack the specific terms that would match relevant documents
- **Intent Ambiguity:** Broad questions don't surface the most relevant subset of information

### The Solution: LLM Query Rewriting

A better approach is to use an LLM to rewrite queries before embedding search. This preprocessing step extracts key information and adds context that improves retrieval.

```python
# AFTER: Query rewriting before embedding search
from mirascope import llm, prompt_template
from typing import List

@llm.call(provider='openai', model='gpt-4o-mini')
@prompt_template("""
Rewrite this user query to improve document retrieval: {original_query}

Generate 3 alternative search queries that use specific technical terms likely to appear in documentation.
Return as a comma-separated list.
""")
def rewrite_query(original_query: str) -> str: ...

def search_documents_with_rewriting(query: str, documents: list[str], embeddings: list) -> list[str]:
    # Rewrite query first
    rewritten_queries = rewrite_query(query).split(',')
    rewritten_queries = [q.strip() for q in rewritten_queries]
    
    # Search with multiple query variants
    all_results = []
    search_queries = [query] + rewritten_queries
    
    for search_query in search_queries:
        query_embedding = get_embedding(search_query)
        similarities = [
            np.dot(query_embedding, doc_embedding) 
            for doc_embedding in embeddings
        ]
        top_indices = np.argsort(similarities)[-2:][::-1]
        all_results.extend([documents[i] for i in top_indices])
    
    # Deduplicate and return top results
    unique_results = list(dict.fromkeys(all_results))
    return unique_results[:5]

# User asks: "How do I troubleshoot when my app is slow?"
# Rewritten to: "application performance troubleshooting, latency debugging, slow response optimization"
```

**Why this approach works better:**

- **Vocabulary Bridging:** LLM translates user language into document-specific terminology
- **Context Enrichment:** Vague queries get expanded with likely relevant concepts
- **Multiple Perspectives:** Alternative phrasings increase chances of finding relevant content

### The Takeaway

Rewrite queries before embedding search to bridge the gap between user language and document terminology. This preprocessing step dramatically improves retrieval quality for natural, conversational queries.

---
*Part of the "Effective AI Engineering" series - practical tips for building better applications with AI components.*