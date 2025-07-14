---
tip_number: 6
tip_name: "Isolate & Evaluate Your RAG Retriever"
categories: ["evaluation", "retrieval", "debugging"]
x_link: "https://x.com/skylar_b_payne/status/1920176661233811726"
linkedin_link: "https://www.linkedin.com/posts/skylarbpayne_are-your-rag-responses-inaccurate-despite-activity-7325941613128527875-h-jL?utm_source=share&utm_medium=member_desktop&rcm=ACoAABKpCf4BI_Yx2u7h66sgi5z1NF3aEYFHgps"
---

## Effective AI Engineering #6: Isolate & Evaluate Your RAG Retriever

**Are your RAG responses inaccurate despite a strong LLM?** When your retrieval system fails to find the right documents, even the most powerful language model can't generate correct answers.

You've instrumented your AI calls (Tip #2) and annotated your traces (Tip #3), but if you're only evaluating the final output, you can't pinpoint what's failing. RAG combines retrieval and generation - when answers are wrong, you need to know which part to fix. Without evaluating your retriever separately, you'll waste time optimizing the wrong component.

### The Problem

Many developers evaluate RAG systems by only examining if the final generated answer is correct:

```python
# BEFORE: Only Evaluating Final Answer Accuracy
from mirascope import llm, prompt_template
import lilypad
import os

# Compute metrics from traces with only final answer annotations
def compute_rag_metrics():
    client = lilypad.Client()
    project_id = os.environ.get("LILYPAD_PROJECT_ID")
    
    # Get all traces
    traces = client.projects.traces.list(project_uuid=project_id)
    
    # Filter to rag answer traces
    rag_traces = [t for t in traces if t.get('display_name') == 'rag_pipeline']
    
    # Count passes and fails from manual annotations
    labels = [t['annotations']['label'] for t in rag_traces if 'annotations' in t]
    passes = labels.count('pass')
    fails = labels.count('fail')
    total = passes + fails
    
    # Calculate success rate
    success_rate = passes / total if total > 0 else 0
    
    print(f"RAG Pipeline Success Rate: {success_rate:.2f}")
    print(f"Total evaluated: {total}, Passes: {passes}, Fails: {fails}")
    
    # Example output:
    # RAG Pipeline Success Rate: 0.67
    # Total evaluated: 100, Passes: 67, Fails: 33
    # (But this doesn't tell you WHY 33% of answers failed)
    
    return success_rate
```

**Why this approach falls short:**

- **Ambiguous Failures:** When an answer fails, you can't tell if your retriever failed to find relevant documents or if the LLM misused good context.
- **No Targeted Fixes:** Without knowing which component failed, you waste time optimizing the wrong part of your system.
- **Inefficient Iteration:** Each evaluation requires running the complete pipeline, making improvements slow and unfocused.
- **Hidden Patterns:** You miss systematic retrieval weaknesses that might affect only certain query types.

### The Solution: Isolate and Evaluate Retrieval

A better approach is to manually evaluate and annotate your retrieval quality separately from the final answer:

```python
# AFTER: Computing Metrics for Both Retriever and End-to-End
from mirascope import llm, prompt_template
import lilypad
import os

# Compute metrics from both retrieval and final answer annotations
def compute_component_metrics():
    client = lilypad.Client()
    project_id = os.environ.get("LILYPAD_PROJECT_ID")
    
    # Get all traces
    traces = client.projects.traces.list(project_uuid=project_id)
    
    # Filter to specific components
    retrieval_traces = [t for t in traces if t.get('display_name') == 'retrieve_documents']
    rag_traces = [t for t in traces if t.get('display_name') == 'rag_pipeline']
    
    # Count retrieval passes and fails
    retrieval_labels = [t['annotations']['label'] for t in retrieval_traces if 'annotations' in t]
    retrieval_passes = retrieval_labels.count('pass')
    retrieval_fails = retrieval_labels.count('fail')
    retrieval_total = retrieval_passes + retrieval_fails
    
    # Count RAG pipeline passes and fails
    rag_labels = [t['annotations']['label']  for t in rag_traces if 'annotations' in t]
    rag_passes = rag_labels.count('pass')
    rag_fails = rag_labels.count('fail')
    rag_total = rag_passes + rag_fails
    
    # Calculate success rates
    retrieval_success = retrieval_passes / retrieval_total if retrieval_total > 0 else 0
    rag_success = rag_passes / rag_total if rag_total > 0 else 0
    
    # Print component-specific metrics
    print(f"Retrieval Success Rate: {retrieval_success:.2f}")
    print(f"RAG Pipeline Success Rate: {rag_success:.2f}")
    
    # Count the four possible cases: retrieval label, rag label => count
    case_counts: dict[(bool, bool), int] = defaultdict(int)

    # Match traces by query to analyze component relationships
    # Get traces with both retrieval and end-to-end annotations
    retrieval_traces_by_query = {t['arg_values']['query']: t for t in retrieval_traces}
    rag_traces_by_query = {t['arg_values']['query']: t for t in rag_traces}
    for query, r_trace in retrieval_traces_by_query.items():
        r_label = r_trace['annotations']['label'] == 'pass'
        rag_label = rag_traces_by_query[query]['annotations']['label'] == 'pass'
        case_counts[(r_label, rag_label)] += 1
    
    # Print the diagnostic matrix
    total_matched = sum(case_counts.values())
    print("\nDiagnostic Matrix (% of total):")
    print(f"Retrieval PASS, RAG PASS: {cases[(True, True)]/total_matched:.2f}")
    print(f"Retrieval PASS, RAG FAIL: {cases[(True, False)]/total_matched:.2f}") 
    print(f"Retrieval FAIL, RAG PASS: {cases[(False, True)]/total_matched:.2f}")
    print(f"Retrieval FAIL, RAG FAIL: {cases[(False, False)]/total_matched:.2f}")
    
    # Example output:
    # Retrieval Success Rate: 0.75
    # RAG Pipeline Success Rate: 0.67
    # 
    # Diagnostic Matrix (% of total):
    # Retrieval PASS, RAG PASS: 0.65  ← Working as expected
    # Retrieval PASS, RAG FAIL: 0.10  ← Generation issue!
    # Retrieval FAIL, RAG PASS: 0.02  ← Lucky guesses
    # Retrieval FAIL, RAG FAIL: 0.23  ← Fix retrieval first
    
    return {
        'retrieval': retrieval_success,
        'rag': rag_success,
        'diagnostic': case_counts
    }
```

**Why this approach works better:**

- **Pinpoint Problems:** The diagnostic matrix clearly shows whether retrieval or generation is causing failures.
- **Targeted Improvements:** When retrieval fails predict RAG failures (~90% of time), you know to fix retrieval first.
- **Efficient Iteration:** Focus efforts on the component with the most impact on overall system quality.
- **Evidence-Based Decisions:** Make data-driven decisions about which retrieval approach works best for your use case.

### How to Implement Retrieval Evaluation

To start evaluating your retriever:

1. **Instrument Both Components:** Apply the Bulkhead pattern (Tip #1) to separate your RAG system into distinct retrieval and generation components. Instrument (Tip #2) and annotate (Tip #3) both separately.

2. **Annotate Retrieval Traces:** In your instrumentation UI, manually review and label each retrieval result:
   - `pass`: The retriever found the most relevant documents for the query
   - `fail`: The retriever missed important relevant documents or returned irrelevant ones

3. **Annotate Final Answer Traces:** Similarly, review and label the final RAG outputs:
   - `pass`: The answer is accurate and addresses the query appropriately
   - `fail`: The answer is inaccurate, incomplete, or off-topic

4. **Analyze Component Relationships:** Use the four-case diagnostic matrix to determine which component needs improvement first.

### The Takeaway

Don't waste time tweaking prompts when your retriever isn't finding the right documents. By isolating and specifically annotating your retrieval component, you can identify the true source of problems in your RAG system. This targeted approach allows you to systematically improve your system's foundation, leading to dramatically better end-to-end performance.

---
*Part of the "Effective AI Engineering" series - practical tips for building better applications with AI components.*