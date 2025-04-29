Okay, let's create Tip #6 focusing on evaluating the retrieval component of your RAG system separately, leveraging the patterns established in previous tips.

---

**Tip #6: Isolate & Evaluate Your RAG Retriever**

**Subject: Effective AI #6: Debugging RAG? Check Your Retrieval First!**

Hey team,

You've set up a Retrieval-Augmented Generation (RAG) system (Tip #5) to give your LLM relevant context. But sometimes, the final answers are still wrong, irrelevant, or incomplete. When this happens, how do you know where the problem lies? Did the retriever fail to find the right information, or did the LLM misunderstand or misuse the context it was given?

**The Anti-Pattern: End-to-End Evaluation Only**

Trying to diagnose RAG issues solely by looking at the final LLM-generated answer is like trying to fix a car engine just by listening to the exhaust. You might know something's wrong, but you can't pinpoint the faulty part. If the context fed *into* the LLM was garbage, you can't expect a good answer, no matter how much you tweak the final prompt.

**Why this fails:**

* **Ambiguous Failures:** You don't know if you need to fix your retrieval logic (indexing, chunking, search algorithm) or your generation prompt/logic.
* **Wasted Effort:** You might spend hours optimizing the LLM prompt when the root cause is consistently poor context retrieval.
* **Hidden Problems:** You might have a retriever that *usually* works but fails badly on certain query types, and this gets masked if you only look at average end-to-end performance.

**The Better Way: Isolate, Instrument, and Evaluate the Retrieval Step**

Treat your retrieval mechanism as a distinct component and evaluate its performance independently.

1.  **Isolate Retrieval Logic:** Encapsulate your document retrieval logic (whether it's BM25, vector search, or something else) within its own dedicated function. This creates a testable unit, similar to the Bulkhead pattern for LLM calls (Tip #1).
2.  **Instrument the Retriever:** Apply instrumentation to *this specific retrieval function* using tools like Lilypad. This logs the inputs (the query) and outputs (the retrieved documents) for every retrieval attempt.
3.  **Annotate Retrieval Traces:** Use your instrumentation platform (like the Lilypad UI) to examine the traces from your retrieval function. For a given query trace, you can see exactly which documents were retrieved *before* they were sent to the LLM. You can then annotate these specific traces – was the retrieved context relevant? Complete? Sufficient? (e.g., 'pass'/'fail', 'good_context'/'bad_context').

**Example (Isolating and Instrumenting Retrieval with Lilypad):**

Let's adapt the RAG flow from Tip #5. We'll put the BM25 retrieval into its own function and instrument it.

```python
import os
from mirascope import llm, prompt_template, response_model
from pydantic import BaseModel, Field
from typing import List
import bm25s # Assuming BM25 from Tip #5
import lilypad # For instrumentation


lilypad.configure()

# --- Data Structures ---
class Document(BaseModel): # Simple representation
    content: str
    id: str # Give docs an ID

class RagResponse(BaseModel):
    answer: str = Field(description="The answer generated based on context and query.")

# --- RAG Setup (Assume documents and BM25 index exist) ---
# Dummy data for illustration
documents_store: List[Document] = [
    Document(id="doc1", content="Project Alpha: Focused on backend API improvements... Status: On track."),
    Document(id="doc2", content="Project Beta: Developing a new user interface... Status: Planning."),
    # ... more documents ...
    Document(id="doc6", content="Project Alpha: Final testing phase begins next Monday...")
]


# --- Step 1 & 2: Isolate and Instrument Retrieval Logic ---
@lilypad.trace(versioning='automatic') # Instrument this function
def retrieve_documents(query: str, k: int) -> List[Document]:
    """
    Retrieves the top k documents for a query using BM25.
    This function is now traced independently by Lilypad.
    """
    print(f"Retrieving top {k} docs for query: '{query}'")
    if not retriever or not bm25s: # Check if retriever/library is available
        print("ERROR: BM25 retriever not available.")
        return []

    try:
        query_tokens = bm25s.tokenize(query)
        # Retrieve indices using the BM25 retriever
        results_indices, _ = retriever.retrieve(query_tokens, k=k)

        # Map indices back to Document objects (ensure indices are valid)
        retrieved_docs = []
        if results_indices and len(results_indices) > 0:
             # Assumes results_indices[0] contains the list of indices
             valid_indices = [idx for idx in results_indices[0] if 0 <= idx < len(documents_store)]
             retrieved_docs = [documents_store[i] for i in valid_indices]

        print(f"Retrieved {len(retrieved_docs)} documents.")
        # Lilypad automatically logs 'query', 'k' as inputs and the returned list of docs as output
        return retrieved_docs
    except Exception as e:
        print(f"Error during retrieval: {e}")
        # Log the exception to Lilypad trace using lilypad.get_current_span().record_exception(e)
        return [] # Return empty on error


# --- Mirascope Prompt and Call Function (Similar to Tip #5) ---
RAG_PROMPT_TEMPLATE = """
SYSTEM: You are a helpful AI assistant... Answer based *only* on the context...

CONTEXT:
---
{context_str}
---

USER QUERY: {query}
"""

@llm("openai", model="gpt-4o-mini", response_model=RagResponse)
@prompt_template(RAG_PROMPT_TEMPLATE)
def answer_with_rag(query: str, docs: list[Document]):
    """Generates answer using Mirascope based on query and retrieved context."""
    return {"computed_fields": {"context_str": "\n\n".join([doc.content for doc in docs])}}

# --- Usage Flow ---
user_query = "What is the status of Project Alpha?"

# Call the ISOLATED and INSTRUMENTED retrieval function
retrieved_docs: List[Document] = retrieve_documents(query=user_query, k=2)

# Call the LLM function (this call will also be traced by Lilypad if instrumented)
response_object: RagResponse = answer_with_rag(
    query=user_query,
    context_str=context_string
)
print("\nFinal LLM Answer:", response_object.answer)
```

**Why This is Powerful:**

* **Pinpoint Failures:** By annotating the `retrieve_documents` traces in Lilypad, you can directly see if bad retrieval correlates with bad final answers. Is the retriever consistently failing for certain types of queries?
* **Targeted Improvement:** If retrieval traces are often marked 'fail', you know to focus on improving that specific component (e.g., try different chunking (Tip coming soon!), use embeddings (Tip coming soon!), tune BM25 parameters).
* **Calculate Retrieval Metrics:** Once you have annotated retrieval traces ('pass'/'fail' based on relevance), you can calculate metrics like Retrieval Precision ("How often was the retrieved context actually relevant?").
* **Regression Testing:** Use your annotated retrieval examples as a test set to ensure changes don't break retrieval performance for queries that previously worked.

**The Takeaway:**

Don't treat your RAG system as an un-debuggable black box. **Isolate your retrieval logic into a separate function, instrument it using tools like Lilypad, and evaluate its performance independently by annotating retrieval traces.** This targeted approach is key to efficiently diagnosing problems and systematically improving the quality of your RAG system.