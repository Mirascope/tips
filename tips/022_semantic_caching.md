---
tip_number: 22
tip_name: "Semantic Caching"
categories: ["cost-control", "performance", "user-experience"]
x_link: ""
linkedin_link: ""
---

## Effective AI Engineering #22: Semantic Caching

**Is Your AI Quietly Burning Through Your Budget?** Imagine getting your cloud bill, and you see huge charges because your AI answered "How do I reset my password?" a thousand different ways.

Even though the answer was basically the same.  It's a frustrating surprise, and it happens more often than you'd think. You're paying top dollar for every single unique question, even when your system has already "learned" the answer. Think about it: a quick database lookup costs virtually nothing, but an LLM call can be 100 times more expensive. Yet, for some reason, we often treat every user query as if it's completely new.

### The Problem

Many developers approach caching by exact string matching or skip caching entirely. This creates challenges that aren't immediately obvious:

```python
# BEFORE: No caching
from mirascope.core import llm

@llm.call(provider="openai", model="gpt-4o-mini")
def answer_query(query: str) -> str:
    return f"Answer this customer question: {query}"

# Direct LLM call every time
def get_answer(query: str) -> str:
    return answer_query(query)
```

**Why this approach falls short:**

- **You're constantly overpaying:** Every slightly rephrased question triggers another expensive LLM call, even if the core meaning is identical. This quickly adds up on your cloud bill
- **Your users get different answers:** When similar questions get different responses, it's confusing and makes your AI feel inconsistent or unreliable
- **Time wasted:** You're spending money generating answers you already have, instead of investing in new, valuable AI features

### The Smarter Way: Semantic Answer Caching

What if your AI could understand the meaning of a question, not just the exact words? That's what semantic caching does. It intelligently checks if an incoming query is similar enough to something it's already answered, using the power of vector similarity.

```python
# AFTER: Semantic caching with similarity matching
from mirascope.core import llm
import lilypad
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import Optional

# Initialize cache as module-level variable for functional approach
encoder = SentenceTransformer('all-MiniLM-L6-v2')
cache = {}  # {query_embedding_hash: (query, answer, embedding)}
SIMILARITY_THRESHOLD = 0.85

def encode_query(query: str) -> np.ndarray:
    return encoder.encode([query])[0]

def get_cached_answer(query: str) -> Optional[str]:
    if not cache:
        return None
        
    query_embedding = encode_query(query)
    
    # Vectorized similarity computation against all cached embeddings
    cached_items = list(cache.values())
    cached_embeddings = np.array([item[2] for item in cached_items])
    
    similarities = cosine_similarity(
        query_embedding.reshape(1, -1),
        cached_embeddings
    )[0]
    
    # Find the most similar cached answer
    best_idx = np.argmax(similarities)
    best_similarity = similarities[best_idx]
    
    if best_similarity >= SIMILARITY_THRESHOLD:
        return cached_items[best_idx][1]  # Return the answer
    
    return None

def cache_answer(query: str, answer: str) -> None:
    query_embedding = encode_query(query)
    cache_key = hash(query_embedding.tobytes())
    cache[cache_key] = (query, answer, query_embedding)

@lilypad.trace()
@llm.call(provider="openai", model="gpt-4o-mini")
def answer_query(query: str) -> str:
    return f"Answer this customer question: {query}"

@lilypad.trace()
def get_answer(query: str) -> str:
    # Check semantic cache first
    cached_answer = get_cached_answer(query)
    if cached_answer:
        return cached_answer
    
    # Generate new answer and cache it
    answer = answer_query(query)
    cache_answer(query, answer)
    return answer
```

**Here's why this approach changes everything:**

- **Massive Cost Savings:** By intelligently reusing answers, you can slash your AI API costs by up to 80% on repetitive questions.  That's money back in your budget for innovation, not repetition
- **Rock-Solid Consistency:** Users get the same, high-quality answer for all semantically similar questions, building trust and improving their experience
- **Focus on What Matters:** You'll spend less time worrying about unexpected bills and more time building the next groundbreaking features that truly delight your users

### Stop Overpaying for Your AI

Semantic caching isn't just a technical tweak; it's a way to ensure your AI works smarter, not just harder. It transforms those frustrating, repetitive expenses into intelligent, consistent user experiences. It's how you build AI systems that are both powerful and cost-effective.

Ready to take control of your AI costs and deliver a more reliable experience? It's time to embrace semantic caching.

---
*Part of the "Effective AI Engineering" series - practical tips for building better applications with AI components.*