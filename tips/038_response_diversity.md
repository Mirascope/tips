---
tip_number: 38
tip_name: "Attribute-First Data Generation"
categories: ["prompt-engineering", "quality-assurance", "user-experience"]
x_link: "https://x.com/skylar_b_payne/status/1943369751545188453"
linkedin_link: "https://www.linkedin.com/posts/skylarbpayne_effective-ai-engineering-38-attribute-first-activity-7349135712916598786-efTH?utm_source=share&utm_medium=member_desktop&rcm=ACoAABKpCf4BI_Yx2u7h66sgi5z1NF3aEYFHgps"
---

## Effective AI Engineering #038: Attribute-First Data Generation

**Is your synthetic data generation stuck in a loop of sameness?** LLMs love to generate similar outputs when asked to create data, making your synthetic datasets predictably boring.

This becomes a major problem when you're trying to build robust evaluation datasets or train models that need to handle diverse real-world scenarios. Repetitive synthetic data leads to brittle AI systems that fail when they encounter actual user variety.

### The Problem

Many developers approach synthetic data generation by directly asking the LLM to create examples. This creates challenges that aren't immediately obvious:

```python
# BEFORE: Direct data generation
from mirascope import llm, prompt_template

@llm.call(provider='openai', model='gpt-4o-mini')
@prompt_template("Generate 10 customer support conversations about billing issues")
def generate_support_conversations(): ...

# Results in very similar conversations every time
conversations = []
for i in range(10):
    conversations.append(generate_support_conversations())
```

**Why this approach falls short:**

- **Repetitive Patterns:** LLMs gravitate toward the most common examples, creating homogeneous datasets
- **Missing Edge Cases:** Rare but important scenarios get overlooked in favor of typical interactions
- **Limited Diversity:** Without explicit guidance, the model defaults to safe, predictable outputs

### The Solution: Attribute-First Generation

A better approach is to generate diverse attributes first, then create data based on those attributes. This two-step pattern forces systematic coverage of your problem space.

```python
# AFTER: Attribute-first generation
from mirascope import llm, prompt_template
from pydantic import BaseModel
from typing import List, Literal

class CustomerProfile(BaseModel):
    user_type: Literal["new_customer", "long_term_customer", "enterprise_user", "free_tier_user"]
    technical_expertise: Literal["beginner", "intermediate", "expert"]
    urgency_level: Literal["low", "medium", "high", "critical"]
    communication_style: Literal["formal", "casual", "frustrated", "polite"]

@llm.call(provider='openai', model='gpt-4o-mini', response_model=CustomerProfile)
@prompt_template("Generate a diverse customer profile for a billing support scenario")
def generate_customer_profile(): ...

@llm.call(provider='openai', model='gpt-4o-mini')
@prompt_template("""
Generate a customer support conversation about billing issues with this customer profile:
- User type: {profile.user_type}
- Technical expertise: {profile.technical_expertise}  
- Urgency level: {profile.urgency_level}
- Communication style: {profile.communication_style}

Make sure the conversation reflects these specific attributes.
""")
def generate_conversation_for_profile(profile: CustomerProfile): ...

# Generate diverse profiles first, then create conversations
profiles = [generate_customer_profile() for _ in range(10)]
conversations = [generate_conversation_for_profile(profile) for profile in profiles]
```

**Why this approach works better:**

- **Systematic Coverage:** Attributes force the model to explore different dimensions of your problem space
- **Edge Case Discovery:** Explicit attribute combinations surface scenarios you might not have considered
- **Controllable Diversity:** You can target specific types of variation that matter for your use case

### The Takeaway

Generate attributes first, then generate data based on those attributes. This attribute-first pattern breaks LLMs out of their comfort zone and creates the diverse synthetic data your AI systems need to handle real-world complexity.

---
*Part of the "Effective AI Engineering" series - practical tips for building better applications with AI components.*