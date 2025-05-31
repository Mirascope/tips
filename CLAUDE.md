# CLAUDE.md - Guide for Generating Effective AI Engineering Tips

This guide provides instructions for generating high-quality tips in the "Effective AI Engineering" series. Follow these patterns and principles to maintain consistency and quality across all tips.

## Core Writing Principles

### 1. Hook Crafting (Opening Line)
Create compelling, attention-grabbing hooks that immediately identify with developer pain points:

**Effective Hook Patterns:**
- **Direct Pain Questions:** "Is your AI service making your entire codebase fragile?"
- **Shocking Statements:** "Every evaluation run emails a real customer. Every test fires a live notification. Surprise!"
- **Impossibility/Contradiction:** "Bigger models are expensive. Smaller models don't always work. But you can have the best of both worlds."

**Hook Formula:** Bold question + one sentence expanding the pain point that resonates with engineers

### 2. Article Structure (Required)
Every tip must follow this exact structure:

```markdown
## Effective AI Engineering #[Number]: [Action-Oriented Title]

**[Punchy hook question]?** [One sentence expanding the pain point]

[2-3 sentences explaining why this matters and its impact on AI applications]

### The Problem

Many developers approach this by [describe common approach]. This creates challenges that aren't immediately obvious:

```python
# BEFORE: [Brief descriptive label]
[Problematic code example]
```

**Why this approach falls short:**

- **[Issue Category 1]:** [Specific problem explanation]
- **[Issue Category 2]:** [Specific problem explanation]  
- **[Issue Category 3]:** [Specific problem explanation]

### The Solution: [Name of Pattern/Approach]

A better approach is to [1-2 sentences introducing solution]. This [pattern/technique] [explain how it addresses core issues].

```python
# AFTER: [Brief descriptive label]
[Improved code example]
```

**Why this approach works better:**

- **[Benefit 1]:** [Specific improvement explanation]
- **[Benefit 2]:** [Specific improvement explanation]
- **[Benefit 3]:** [Specific improvement explanation]

### The Takeaway

[1-2 sentence summary of core principle]. This [approach/pattern] makes your AI-powered applications more [robust/maintainable/reliable] and addresses [reiterate key pain point].

---
*Part of the "Effective AI Engineering" series - practical tips for building better applications with AI components.*
```

## Code Example Requirements

### 1. BEFORE/AFTER Pattern (Mandatory)
- Always show problematic approach first with "BEFORE:" label
- Always show improved approach with "AFTER:" label
- Code must be production-ready, not toy examples
- Include comments explaining key differences

### 2. Mirascope Integration (When Applicable)
Use mirascope consistently for AI function definitions:

```python
from mirascope.core import anthropic, prompt_template
from pydantic import BaseModel

@anthropic.call("claude-3-5-sonnet-20241022")
@prompt_template("Your prompt here")
def ai_function() -> str:
    pass

# For structured outputs:
class OutputModel(BaseModel):
    field: str

@anthropic.call("claude-3-5-sonnet-20241022", response_model=OutputModel)
@prompt_template("Your prompt here")
def structured_ai_function() -> OutputModel:
    pass
```

### 3. Lilypad Integration (When Tracing Matters)
Use lilypad for observability and evaluation:

```python
import lilypad

@lilypad.trace()
@anthropic.call("claude-3-5-sonnet-20241022")
@prompt_template("Your prompt here")
def traced_function() -> str:
    pass

# For evaluation workflows:
@lilypad.trace()
def evaluate_responses():
    # Show annotation and metric computation
    pass
```

## Technical Guidelines

### 1. Framework Usage
- **Primary:** Use mirascope for AI function definitions
- **Observability:** Use lilypad when tracing/evaluation is relevant to the tip
- **Models:** Default to Claude 3.5 Sonnet unless specific model requirements exist
- **Validation:** Use Pydantic models for structured outputs

### 2. Code Quality Standards
- Production-ready examples with proper error handling
- Complete workflows, not isolated snippets
- Real-world complexity, not oversimplified demos
- Include imports and necessary setup code

### 3. Problem-Solution Focus
- Start with genuine developer pain points
- Show concrete, actionable solutions
- Explain the "why" behind recommendations
- Reference real-world experience and battle-tested approaches

## Writing Tone and Voice

### 1. Authoritative Yet Approachable
- Use "we" and "you" to create partnership
- Reference "decades of experience" for credibility
- Acknowledge complexity while providing practical solutions

### 2. Problem-First Approach
- Lead with pain points developers actually face
- Avoid abstract theoretical discussions
- Focus on immediate practical value

### 3. Battle-Tested Emphasis
- Draw from real production experience
- Reference specific tools used in practice
- Emphasize proven patterns over experimental approaches

## Content Themes and Progression

### 1. Foundation Patterns (Early Tips)
- Bulkhead patterns for service isolation
- Instrumentation and observability
- Annotation workflows for evaluation
- Structured outputs for reliability

### 2. Advanced Optimization (Later Tips)
- Cost optimization techniques
- Performance and caching strategies
- Model escalation patterns
- Complex retrieval and reranking

### 3. Cross-Tip Connections
- Build on previous tips ("Building on Tip #X...")
- Reference established patterns
- Create coherent narrative progression

## Quality Checklist

Before finalizing a tip, verify:

- [ ] Hook immediately identifies with developer pain point
- [ ] Structure follows exact template format
- [ ] BEFORE/AFTER code examples are complete and runnable
- [ ] Mirascope patterns used correctly for AI functions
- [ ] Lilypad integration shown when relevant for observability
- [ ] Three specific problems and three specific benefits listed
- [ ] Takeaway summarizes core principle clearly
- [ ] Code examples are production-ready with proper imports
- [ ] Writing tone is authoritative yet approachable
- [ ] Content builds logically on existing tip foundation

## Common Pitfalls to Avoid

- **Generic hooks:** Avoid vague statements that don't resonate with specific pain points
- **Over sensationalized hooks:** Avoid hooks which make the problem seem grandiose, more so than it really is
- **Toy examples:** Never use oversimplified code that doesn't work in practice
- **Missing context:** Always explain why the problem matters to AI applications
- **Incomplete solutions:** Ensure code examples are runnable and complete
- **Abstract advice:** Focus on concrete, actionable recommendations
- **Inconsistent structure:** Follow the template format exactly for each tip