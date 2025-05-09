## Effective AI Engineering #12: Balance Caching and Relevance with Clustered Few-Shot Examples

**Are you struggling to balance prompt caching benefits with dynamic few-shot learning?** Dynamic in-context examples improve quality but reduce cache hits, forcing a tradeoff between performance and cost.

When you use dynamic few-shot prompting, each query potentially gets different examples, which breaks prompt caching. This means you either sacrifice the benefits of prompt caching (lower costs and latency) or the benefits of dynamically selected examples (higher relevance and quality). This tradeoff significantly impacts applications that need both cost efficiency and high-quality, context-aware responses.

### The Problem

Many developers implement dynamic few-shot prompting without considering the impact on prompt caching:

```python
# BEFORE: Dynamic Few-Shot Selection Breaking Cache Hits
from mirascope import anthropic, prompt_template
from pydantic import BaseModel
import bm25s

class Example(BaseModel):
    query: str
    answer: str

class Response(BaseModel):
    answer: str

# Load a large corpus of examples
examples = load_examples_from_database()  # Hundreds of potential examples

def retrieve_examples(query: str, k: int = 3) -> list[Example]:
    # Tokenize all examples
    corpus_tokens = bm25s.tokenize([ex.query for ex in examples])
    retriever = bm25s.BM25()
    retriever.index(corpus_tokens)
    
    # Find most similar examples for each query
    query_tokens = bm25s.tokenize(query)
    results = retriever.retrieve(query_tokens, k=k)[0]
    return [examples[idx] for idx, _ in results]

@anthropic.call(
    model="claude-3-sonnet-20240229", 
    response_model=Response,
    extra_headers={"anthropic-beta": "prompt-caching-v0"}
)
@prompt_template("""
SYSTEM: You are a helpful assistant that answers questions based on examples.

<examples>
{examples_block}
</examples>

USER: {query}
""")
def generate_response(query: str):
    # Each query gets different examples, breaking prompt caching
    selected_examples = retrieve_examples(query)
    examples_block = "\n".join([
        f"QUERY: {ex.query}\nANSWER: {ex.answer}" 
        for ex in selected_examples
    ])
    return {"computed_fields": {"examples_block": examples_block}}

# Every call has a unique prompt, resulting in 0% cache hits
response = generate_response(query="How do wind turbines work?")
```

**Why this approach falls short:**

- **Zero Cache Utilization:** Every unique combination of examples creates a distinct prompt, eliminating cache benefits.
- **Higher Costs:** Processing the full prompt from scratch for every request increases token costs.
- **Increased Latency:** Each request requires full prompt processing, slowing response times.
- **Diminishing Returns:** Beyond a certain point, more specific examples yield minimal quality improvements but continue to break caching.

### The Solution: Clustered Few-Shot Examples

A better approach is to cluster your examples and select entire clusters rather than individual examples. This creates a finite set of possible example combinations that can be effectively cached.

```python
# AFTER: Clustered Few-Shot Examples for Better Cache Utilization
from mirascope import anthropic, prompt_template
from pydantic import BaseModel
from sklearn.cluster import KMeans

class Example(BaseModel):
    query: str
    answer: str

class Response(BaseModel):
    answer: str

# Pre-define a small number of example clusters at initialization time
def create_example_clusters(examples: list[Example], num_clusters: int = 5):
    """Group examples into a small number of semantically similar clusters"""
    # Simple clustering based on word overlap (in production, use embeddings)
    from sklearn.feature_extraction.text import CountVectorizer
    
    # Convert queries to feature vectors (word counts)
    vectorizer = CountVectorizer(stop_words='english')
    vectors = vectorizer.fit_transform([ex.query for ex in examples])
    
    # Cluster the examples
    kmeans = KMeans(n_clusters=num_clusters)
    clusters = kmeans.fit_predict(vectors)
    
    # Group examples by cluster
    clustered_examples = {i: [] for i in range(num_clusters)}
    for i, cluster_id in enumerate(clusters):
        clustered_examples[cluster_id].append(examples[i])
    
    return vectorizer, kmeans, clustered_examples

# Load examples and create clusters (done once at startup)
all_examples = load_examples_from_database()
vectorizer, kmeans, example_clusters = create_example_clusters(all_examples, num_clusters=5)

# Function to find the right cluster for a query
def get_cluster_for_query(query: str) -> list[Example]:
    """Return all examples from the most relevant cluster"""
    # Convert query to vector using same vectorizer
    query_vector = vectorizer.transform([query])
    
    # Find nearest cluster
    cluster_id = kmeans.predict(query_vector)[0]
    
    # Return all examples from that cluster
    return example_clusters[cluster_id]

@anthropic.call(
    model="claude-3-sonnet-20240229", 
    response_model=Response,
    extra_headers={"anthropic-beta": "prompt-caching-v0"}
)
@prompt_template("""
SYSTEM: You are a helpful assistant that answers questions based on examples.

<examples>
{examples_block}
</examples>

USER: {query}
""")
def generate_response(query: str, cluster_examples: list[Example]):
    # Format examples for insertion into prompt
    examples_block = "\n".join([
        f"QUERY: {ex.query}\nANSWER: {ex.answer}" 
        for ex in cluster_examples
    ])
    return {"computed_fields": {"examples_block": examples_block}}

# Main function to answer queries
def answer_query(query: str) -> Response:
    # Get examples from the relevant cluster
    cluster_examples = get_cluster_for_query(query)
    
    # With only 5 clusters, you'll have at most 5 different prompts
    # This provides ~20% cache hit rate even with uniform query distribution
    return generate_response(query=query, cluster_examples=cluster_examples)
```

**Why this approach works better:**

- **Balanced Caching:** Limits the total number of unique prompts to the number of clusters, enabling effective caching.
- **Contextual Relevance:** Still uses query-relevant examples, maintaining most quality benefits of dynamic selection.
- **Cost Optimization:** With N clusters, you can achieve approximately 1/N of the caching benefit compared to static prompts.
- **Adjustable Tradeoff:** You can tune the number of clusters to balance between caching benefits and example specificity.

### Alternative Clustering Approaches

The core idea of clustering examples works with various clustering techniques. Here are some effective alternatives:

1. **Embedding-Based Clustering**: Instead of word counts, use vector embeddings for better semantic understanding. This captures meaning, not just lexical similarity.
2. **Domain-Based Classification**: Group examples into predefined categories based on topics or domains (e.g., science, finance, technology).
3. **Hybrid Approaches**: Combine automatic clustering with manual curation for the best balance of automation and quality.


### The Takeaway

Cluster your few-shot examples to find the sweet spot between caching efficiency and example relevance. By grouping similar examples and selecting entire clusters, you can maintain most of the quality benefits of dynamic few-shot examples while still getting substantial prompt caching benefits. This approach is especially valuable for high-volume AI applications where both cost efficiency and response quality are critical.

---
*Part of the "Effective AI Engineering" series - practical tips for building better applications with AI components.*