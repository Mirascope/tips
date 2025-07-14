---
tip_number: 35
tip_name: "Logit Bias"
categories: ["prompt-engineering", "output-validation", "quality-assurance"]
x_link: "https://x.com/skylar_b_payne/status/1942282575797440704"
linkedin_link: "https://www.linkedin.com/posts/skylarbpayne_everyone-says-my-writing-sounds-like-ai-activity-7348048526045593601-TsHx?utm_source=share&utm_medium=member_desktop&rcm=ACoAABKpCf4BI_Yx2u7h66sgi5z1NF3aEYFHgps"
---

## Effective AI Engineering #35: Logit Bias

**"Everyone says my writing sounds like AI wrote it with all the em-dashes?"** That's because AI did write it—and those telltale punctuation patterns are dead giveaways.

AI models have distinctive linguistic fingerprints, especially around specific tokens like em-dashes and overly formal language. These patterns make generated content immediately recognizable as machine-generated, which can undermine authenticity in professional applications.

### The Problem

Many developers accept default AI behavior without considering how to suppress common AI tells. This creates challenges that aren't immediately obvious:

```python
# BEFORE: Default model behavior with distinctive AI patterns
from mirascope import llm, prompt_template

@llm.call(provider="openai", model="gpt-4o-mini")
@prompt_template("Write a comprehensive quarterly business report analyzing our Q3 performance, market trends, and strategic recommendations for Q4. Include sections on revenue, customer acquisition, and competitive positioning.")
def generate_quarterly_report(): ...

# Generate report
report = generate_quarterly_report()
print(report)
# Output likely contains: "However, our analysis shows—despite challenges—that revenue grew significantly..."
```

**Why this approach falls short:**

- **AI Fingerprints:** Em-dashes and formal transitions immediately signal AI authorship
- **Robotic Tone:** Overly structured language patterns that humans rarely use naturally
- **Obvious Tells:** Specific punctuation and phrasing that readers recognize as machine-generated

### The Solution: Strategic Logit Bias

A better approach is to use logit bias to suppress the most obvious AI tells like em-dashes and overly formal language. This technique gives you direct control over token-level generation patterns.

```python
# AFTER: Logit bias to suppress AI tells
from mirascope import llm, prompt_template

@llm.call(provider="openai", model="gpt-4o-mini", call_params={
    "logit_bias": {
        "—": -1.0,     # Suppress em-dashes completely
        "However": -0.5 # Reduce overly formal transitions
    }
})
@prompt_template("Write a comprehensive quarterly business report analyzing our Q3 performance, market trends, and strategic recommendations for Q4. Include sections on revenue, customer acquisition, and competitive positioning.")
def generate_natural_report(): ...

# Generate more natural-sounding report
report = generate_natural_report()
print(report)
# Output avoids em-dashes and reduces formal "However" transitions
```

**Why this approach works better:**

- **Eliminates Dead Giveaways:** Directly suppresses the most obvious AI writing patterns
- **Preserves Quality:** Maintains content quality while improving naturalness
- **Simple Implementation:** Just a few lines of bias configuration for immediate impact

### The Takeaway

Logit bias provides surgical control over AI language patterns by suppressing specific tokens that scream "AI-generated." This simple technique helps your AI writing blend seamlessly with human-authored content.

---
*Part of the "Effective AI Engineering" series - practical tips for building better applications with AI components.*