## Effective AI Engineering #25: Ranking Boosting

Your RAG gets documents like "API Documentation v1.2" before "Quick Start". Your ranker does not understand your data, but you can't train your own right now.

Off the shelf reranking models excel at semantic matching but often miss business context - recency preferences, user intent signals, or document importance. These nuances can make the difference between helpful and frustrating search results.

### The Problem

Many developers rely solely on ML model scores for ranking without incorporating business logic. This creates challenges that aren't immediately obvious:

```python
# BEFORE: Pure ML model ranking
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from typing import List
from dataclasses import dataclass

@dataclass
class Document:
    id: str
    content: str
    doc_type: str
    created_date: str

def rerank_documents(query: str, documents: List[Document]) -> List[Document]:
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    # Encode query and documents
    query_embedding = model.encode([query])
    doc_embeddings = model.encode([doc.content for doc in documents])
    
    # Calculate similarity scores
    similarities = cosine_similarity(query_embedding, doc_embeddings)[0]
    
    # Sort by ML score only
    scored_docs = list(zip(documents, similarities))
    scored_docs.sort(key=lambda x: x[1], reverse=True)
    
    return [doc for doc, score in scored_docs]
```

**Why this approach falls short:**

- **Ignores Context Signals:** Recent documents or beginner-friendly content might rank lower despite being more useful
- **No Business Logic:** Model doesn't understand that "Quick Start" docs should rank higher for "getting started" queries
- **Static Scoring:** Can't adapt to user personas, document freshness, or popularity signals

### The Solution: Signal-Aware Ranking Boost

A better approach is to combine ML model scores with targeted business logic boosts. This pattern enhances semantic ranking with contextual signals while keeping the system transparent and tunable.

```python
# AFTER: ML ranking enhanced with business logic boosting
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import lilypad
import numpy as np
from typing import List, Callable, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass


@dataclass
class BoostRule:
    name: str
    condition: Callable[[str, Document], bool]
    boost_factor: float

# Initialize model and rules at module level for functional approach
model = SentenceTransformer('all-MiniLM-L6-v2')

boost_rules = [
    BoostRule(
        name="recent_documentation",
        condition=lambda q, d: d.created_date > datetime.now() - timedelta(days=90),
        boost_factor=1.15
    ),
]

@lilypad.trace()
def calculate_boosted_score(query: str, document: Document, base_score: float) -> float:
    final_score = base_score
    applied_boosts = []
    
    for rule in boost_rules:
        if rule.condition(query, document):
            final_score *= rule.boost_factor
            applied_boosts.append(rule.name)
    
    # Log boost application for transparency
    if applied_boosts:
        print(f"Document {document.id}: Applied boosts {applied_boosts}")
    
    return final_score

@lilypad.trace()
def rerank_documents_with_boosting(query: str, documents: List[Document]) -> List[Document]:
    # Get base ML scores
    query_embedding = model.encode([query])
    doc_embeddings = model.encode([doc.content for doc in documents])
    base_similarities = cosine_similarity(query_embedding, doc_embeddings)[0]
    
    # Apply boosting to each document
    boosted_scores = []
    for doc, base_score in zip(documents, base_similarities):
        boosted_score = calculate_boosted_score(query, doc, base_score)
        boosted_scores.append((doc, boosted_score, base_score))
    
    # Sort by boosted scores
    boosted_scores.sort(key=lambda x: x[1], reverse=True)
    
    return [doc for doc, boosted_score, base_score in boosted_scores]
```

**Why this approach works better:**

- **Context-Aware Ranking:** Business rules ensure beginner content surfaces for "getting started" queries
- **Transparent Logic:** Boost application is logged, making ranking decisions explainable and debuggable  
- **Iterative Improvement:** Rules can be tuned based on user feedback without retraining ML models

### The Takeaway

Ranking boosts bridge the gap between semantic similarity and business context, ensuring your search results are both technically relevant and practically useful. This pattern provides immediate ranking improvements while building toward more sophisticated ML models.

---
*Part of the "Effective AI Engineering" series - practical tips for building better applications with AI components.*