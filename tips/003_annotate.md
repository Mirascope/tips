---
tip_number: 3
tip_name: "Don't Just Log, Annotate! Turn Data into Understanding"
categories: ["evaluation", "monitoring", "iteration"]
x_link: "https://x.com/skylar_b_payne/status/1918364219847672165"
linkedin_link: "https://www.linkedin.com/posts/skylarbpayne_is-your-ai-system-generating-logs-without-activity-7324129427204812800-nDQz?utm_source=share&utm_medium=member_desktop&rcm=ACoAABKpCf4BI_Yx2u7h66sgi5z1NF3aEYFHgps"
---

## Effective AI Engineering #3: Don't Just Log, Annotate! Turn Data into Understanding

**Is your AI system generating logs without insights?** Traces and logs can quickly pile up without revealing why your AI fails or succeeds in specific scenarios.

When you instrument your AI calls (Tip #2), you collect valuable data about every interaction. But raw logs and traces, while essential, are just the starting point. To systematically improve your system, you need to transform this observability data into structured, actionable insights through annotation.

### The Problem

Many teams collect extensive logs but struggle to extract meaningful patterns from them:

```json
{
  "display_name": "example_llm_call",
  "uuid": "484d51bc-34f8-4e86-b452-1f4236cbc02f",
  "arg_values": {
    "user_attributes": {"name": "Jeffrey Wang", "title": "Senior Manager", "account_type": "admin"},
    "query": "What resources can I share with my reports about parental leave policies?"
  },
  "cost": 0.0054501,
  "duration_ms": 5919051711.0,
  "events": [],
  "function_uuid": "798c0f83-5dba-40ec-b019-a4e2180eecc7",
  "input_tokens": 35554.0,
  "output": "Please refer reports to documentation found on our [benefits page](acme.org/benefits)",
  "output_tokens": 195.0,
  ...
}
```

What do you even do with this?


**Why this approach falls short:**

- **Anecdotal Understanding:** You see individual failures but can't quantify how often specific issues occur.
- **Reactive Analysis:** You review traces only when something breaks, missing systematic patterns.
- **No Clear Quality Metrics:** You can't measure if changes actually improve your system.
- **Limited Dataset Creation:** You struggle to identify good examples for regression testing or few-shot learning.

### The Solution: Structured Annotation

A better approach is to implement a systematic annotation workflow that transforms raw traces into categorized, actionable insights. This process turns observability data into structured learning.

[PLACEHOLDER FOR LILYPAD SCREENSHOT]

**Why this approach works better:**

- **Systematic Understanding:** Quantify exactly why and how often your AI behaves correctly or incorrectly.
- **Targeted Improvements:** Identify specific failure modes (like "ignored newer context") that need attention.
- **Measurable Quality:** Track pass/fail rates based on consistent criteria as you make system changes.
- **Dataset Creation:** Easily identify traces to use for evaluation, regression testing, or few-shot examples.

### A Practical Annotation Workflow

Follow these steps to build an effective annotation system:

1. **Phase 1: Explore & Add Notes**
   - Review dozens of traces in your tracing UI
   - Add unstructured comments on what works/fails
   - Build qualitative understanding of patterns

2. **Phase 2: Define & Apply Tags**
   - Create structured tags based on recurring themes
   - Examples: `hallucination`, `bad_retrieval`, `contradicts_context`
   - Apply tags systematically to categorize issues

3. **Phase 3: Establish Pass/Fail Criteria**
   - Define clear acceptance criteria for your use case
   - Keep this definition stable to track progress over time
   - Apply consistently to measure system quality

### The Takeaway

Instrumentation gives you data; annotation turns that data into understanding. By following a structured workflow (Notes → Tags → Pass/Fail), you create the foundation for systematic improvement. This annotation process is what truly powers the AI improvement flywheel, turning raw observations into targeted enhancements.

---
*Part of the "Effective AI Engineering" series - practical tips for building better applications with AI components.*