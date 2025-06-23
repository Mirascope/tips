## Effective AI Engineering #32: PII Masking

**Ever accidentally paste a customer's credit card number into ChatGPT?** Copy-pasting customer support tickets, debugging with real user data, or testing with production examples can expose sensitive information to AI providers.

Personal data in AI inputs creates liability for data breaches, regulatory violations, and user trust issues. When you process customer messages through AI services, you're transmitting PII to external systems that may log and retain it indefinitely.

### The Problem

Many developers send user inputs directly to AI models without sanitizing personal information. This creates challenges that aren't immediately obvious:

```python
# BEFORE: Raw PII sent to AI models
from mirascope.core import anthropic, prompt_template

@anthropic.call("claude-3-5-sonnet-20241022")
@prompt_template("Help this customer with their request: {customer_message}")
def handle_customer_support(customer_message: str) -> str:
    pass

# Dangerous: PII gets sent to external AI service
message = "My email john.doe@company.com isn't receiving notifications and my phone 555-123-4567 needs to be updated"
response = handle_customer_support(message)
print(response)
```

**Why this approach falls short:**

- **Privacy Violations:** Customer PII gets transmitted to third-party AI providers
- **Compliance Risk:** GDPR, CCPA, and other regulations may be violated
- **Data Retention:** AI providers may log and store customer personal information

### The Solution: Presidio-Based PII Masking

A better approach is to use Microsoft Presidio to detect and anonymize PII before sending to AI services, then restore the original values in responses. This pattern preserves context while protecting sensitive data.

```python
# AFTER: PII masking with Presidio
from mirascope.core import anthropic, prompt_template
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig
import lilypad

# Initialize Presidio engines
analyzer = AnalyzerEngine()
anonymizer = AnonymizerEngine()

@lilypad.trace()
def mask_pii(text: str) -> tuple[str, dict]:
    """Detect and mask PII using Presidio"""
    # Analyze text for PII
    results = analyzer.analyze(text=text, language='en')
    
    # Create anonymization config with reversible placeholders
    operators = {}
    for result in results:
        operators[result.entity_type] = OperatorConfig("custom", {"lambda": lambda _: f"<{result.entity_type}>"})
    
    # Anonymize the text
    anonymized_result = anonymizer.anonymize(
        text=text,
        analyzer_results=results,
        operators=operators
    )
    
    # Create mapping to restore original values
    mapping = {}
    for item in anonymized_result.items:
        if item.operator == "custom":
            original_text = text[item.start:item.end]
            mapping[item.text] = original_text
    
    return anonymized_result.text, mapping

@lilypad.trace()
def restore_pii(text: str, mapping: dict) -> str:
    """Restore original PII values from anonymized text"""
    restored_text = text
    for placeholder, original in mapping.items():
        restored_text = restored_text.replace(placeholder, original)
    return restored_text

@lilypad.trace()
@anthropic.call("claude-3-5-sonnet-20241022")
@prompt_template("Help this customer with their request: {customer_message}")
def handle_masked_customer_support(customer_message: str) -> str:
    pass

@lilypad.trace()
def secure_customer_support(customer_message: str) -> str:
    # Step 1: Mask PII before sending to AI
    masked_message, pii_mapping = mask_pii(customer_message)
    
    # Step 2: Process with AI using masked data
    masked_response = handle_masked_customer_support(masked_message)
    
    # Step 3: Restore PII in the response
    final_response = restore_pii(masked_response, pii_mapping)
    
    return final_response

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