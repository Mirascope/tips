---
tip_number: 2
tip_name: "Instrument Your AI Calls - You Can't Improve What You Don't Measure"
categories: ["monitoring", "debugging", "cost-control"]
x_link: "https://x.com/skylar_b_payne/status/1918002326310109549"
linkedin_link: "https://www.linkedin.com/posts/skylarbpayne_why-the-does-my-ai-system-return-that-activity-7323768517051256832-bmkx?utm_source=share&utm_medium=member_desktop&rcm=ACoAABKpCf4BI_Yx2u7h66sgi5z1NF3aEYFHgps"
---

## Effective AI Engineering: Instrument Your AI Calls - You Can't Improve What You Don't Measure

**Is your AI system a mysterious black box?** When your AI returns unexpected responses or errors, you need to know why – not just that something went wrong.

If you can't see what's happening inside your AI interactions, you'll struggle to debug issues, control costs, or systematically improve quality. Visibility into your AI calls isn't optional; it's essential for building reliable AI-powered applications that you can confidently maintain and evolve.

### The Problem

Many teams deploy AI services with minimal instrumentation, treating AI components differently from other parts of their system:

```python
# BEFORE: Uninstrumented AI Call
def generate_response(query: str) -> str:
  docs = search(query)
  
  # Black box AI call with no visibility
  response = ai_service.completion(
    prompt=make_prompt(query, docs), 
    temperature=0.7
  )
  
  # If something goes wrong, we have little insight into why
  return process_response(response)
```

**Why this approach falls short:**

- **Opaque Debugging:** When AI responses are incorrect or unexpected, you have no visibility into why – was it the prompt? The retrieved context? The parameter settings?
- **Uncontrolled Costs:** Without tracking token usage and costs per call, you risk budget overruns as usage scales.
- **No Quality Baselines:** Without systematic logging, you can't measure if changes to prompts or models actually improve outcomes.
- **Missing Optimization Opportunities:** You can't identify and fix slow or inefficient patterns without performance data.

### The Solution: Comprehensive Instrumentation

Building on the Bulkhead pattern (Tip #1), add instrumentation to your isolated AI components to capture rich data about every interaction. Think of it like a flight recorder for your AI calls – collecting the data you need for analysis, debugging, and improvement.

```python
# AFTER: Properly Instrumented AI Call
PROMPT_TEMPLATE = """
SYSTEM: You are a helpful assistant that generates concise, accurate responses to user queries.
Use only the provided document information. If you don't know, say so.

## CONTEXT
---
{docs}
---

USER: {query}
"""

# The "Bulkhead" Function (See Tip #1) - now with added instrumentation
@lilypad.trace() # <--- Added Instrumentation!
@llm.call(provider='openai', model='gpt-4o-mini')
@prompt_template(PROMPT_TEMPLATE)
def generate_response_llm(query: str, docs: list[Document]): ...

def generate_response(query: str) -> str:
  # Business logic
  docs = search(query)
  
  # Call the isolated, instrumented AI function
  structured_output = generate_response_llm(query, docs) # Now with tracing!
  
  # Business logic using validated, structured data
  return structured_output.content
```

**Why this approach works better:**

- **Comprehensive Visibility:** Every AI call logs prompt, response, metadata, latency, and tokens used. When something goes wrong, you have the data to understand why.
- **Cost Management:** Track exact token usage and costs per call, allowing for budget monitoring and optimization.
- **Actionable Analytics:** Collected data provides patterns of use, performance bottlenecks, and quality trends across your system.
- **Foundation for Evaluation:** Systematically collected examples become the raw material for measuring and improving AI quality over time.

### The Advanced Benefits

With properly instrumented AI calls, you unlock powerful capabilities:

- **Systematic Debugging:** Find patterns in failures (e.g., "fails on queries about topic X")
- **Evidence-Based Improvements:** Objectively measure if prompt or model changes actually improve results
- **Performance Optimization:** Identify which specific AI interactions are slow or expensive
- **Advanced Techniques:** Use your logged data to build semantic caching, dynamic few-shot learning, and even fine-tuning datasets

### The Takeaway

Instrumentation isn't a "nice-to-have" for AI systems; it's **fundamental**. It provides the visibility needed for cost control, debugging, reliability, and crucially, the data required for evaluation and continuous improvement. Building on the Bulkhead pattern (Tip #1), instrumentation can be surprisingly straightforward to add – but the benefits are profound.

---
*Part of the "Effective AI Engineering" series - practical tips for building better applications with AI components.*