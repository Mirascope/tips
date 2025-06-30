## Effective AI Engineering #32: PII Masking

Just waiting for the other shoe to drop. LLMs have mad your customer support agents best in class.
But it's also created a huge risk: copy and pasted customer data into third-party AIs.
Emails, phone numbers, and addresses copy and pasted right into the LLM.
Sent off to third party providers without user consent.

One day your users will find out.
That'll be a bad day.

One easy trick to help below!

### The Problem

Many developers send user inputs directly to AI models without sanitizing personal information. This creates challenges that aren't immediately obvious:

```python
# BEFORE: Raw PII sent to AI models
from mirascope import llm, prompt_template

@llm.call(provider="anthropic", model="claude-3-5-sonnet-20241022")
@prompt_template("Help this customer with their request: {customer_message}")
def handle_customer_support(customer_message: str): ...

# Dangerous: PII gets sent to external AI service
message = "My email john.doe@company.com isn't receiving notifications and my phone 555-123-4567 needs to be updated"
response = handle_customer_support(message)
print(response)
```

**Why this approach falls short:**

- **Privacy Violations:** Customer PII gets transmitted to third-party AI providers
- **Compliance Risk:** GDPR, CCPA, and other regulations may be violated
- **Data Retention:** AI providers may log and store customer personal information

### The Solution: PII Masking

A better approach is to mask PII before sending to AI services, then restore the original values in responses. This pattern preserves context while protecting sensitive data.

```python
# AFTER: PII masking with Presidio
from mirascope import llm, prompt_template

from presidio_analyzer import AnalyzerEngine

def mask_pii(text: str) -> tuple[str, dict[str, str]]:
    """Detect and mask PII using Presidio"""
    analyzer = AnalyzerEngine()
    
    # Analyze text for PII
    results = analyzer.analyze(text=text, language='en')
    mapping = {f"<{result.entity_type}>": text[result.start:result.end] for result in results}
    inverse_mapping = {v: k for k, v in mapping.items()}
    return unmask_pii(text, inverse_mapping), mapping

def unmask_pii(text: str, mapping: dict[str, str]) -> str:
    for k, v in mapping.items():
        text = text.replace(k, v)
    return text


@llm.call(provider="anthropic", model="claude-3-5-sonnet-20241022")from presidio_analyzer import AnalyzerEngine
@prompt_template("Help this customer with their request: {customer_message}")
def handle_masked_customer_support(customer_message: str): ...

def secure_customer_support(customer_message: str) -> str:
    # Step 1: Mask PII before sending to AI
    masked_message, pii_mapping = mask_pii(customer_message)
    # Step 2: Process with AI using masked data
    masked_response = handle_masked_customer_support(masked_message)
    # Step 3: Restore PII in the response
    return restore_pii(masked_response, pii_mapping)

# Example usage
message = "My email john.doe@company.com isn't receiving notifications and my phone 555-123-4567 needs to be updated"
response = secure_customer_support(message)
print(f"Safe response: {response}")
```

**Why this approach works better:**

- **Privacy by Design:** PII never leaves your infrastructure in its original form
- **Production-Ready:** Presidio handles complex PII detection patterns reliably
- **Regulatory Compliance:** Reduces risk of GDPR, CCPA, and other privacy violations

### The Takeaway

PII masking with Presidio enables safe AI processing of customer data by automatically detecting, anonymizing, and restoring personal information. This pattern protects privacy while maintaining AI effectiveness for legitimate use cases.

---
*Part of the "Effective AI Engineering" series - practical tips for building better applications with AI components.*