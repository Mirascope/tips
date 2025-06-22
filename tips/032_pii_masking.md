## Effective AI Engineering #32: PII Masking

**Are you sending customer emails and phone numbers to third-party AI models?** Every user query containing personal information gets transmitted to external services, creating compliance risks and privacy violations.

Personal data in AI inputs creates liability for data breaches, regulatory violations, and user trust issues. But completely blocking PII often breaks legitimate use cases where personal context improves AI responses.

### The Problem

Many developers send user inputs directly to AI models without sanitizing personal information. This creates challenges that aren't immediately obvious:

```python
# BEFORE: Raw PII sent to AI models
from mirascope.core import llm
import lilypad

@lilypad.trace()
@llm.call(provider="openai", model="gpt-4o-mini")
def handle_customer_support(customer_message: str) -> str:
    return f"Help this customer with their request: {customer_message}"

# Dangerous: PII gets sent to external AI service
customer_inputs = [
    "My email john.doe@company.com isn't receiving notifications",
    "Call me at 555-123-4567 about my order #12345",
    "My credit card 4532-1234-5678-9012 was charged twice",
    "I live at 123 Main St, Boston MA 02101"
]

for message in customer_inputs:
    # PII transmitted to AI provider
    response = handle_customer_support(message)
    print(f"Response: {response}")
```

**Why this approach falls short:**

- **Privacy Violations:** Customer PII gets transmitted to third-party AI providers
- **Compliance Risk:** GDPR, CCPA, and other regulations may be violated
- **Data Retention:** AI providers may log and store customer personal information

### The Solution: PII Detection and Placeholder Substitution

A better approach is to detect PII, replace it with semantic placeholders, and restore the original values in responses. This pattern preserves context for AI processing while protecting sensitive data.

```python
# AFTER: PII masking with semantic placeholders
from mirascope.core import anthropic, prompt_template
from pydantic import BaseModel
import lilypad
import re
from typing import Dict, List, Tuple
from dataclasses import dataclass

@dataclass
class PIIMatch:
    original_text: str
    placeholder: str
    pii_type: str
    start_pos: int
    end_pos: int

# PII detection patterns
pii_patterns = {
    'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
    'phone': r'\b(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b',
    'ssn': r'\b\d{3}-?\d{2}-?\d{4}\b',
    'credit_card': r'\b(?:\d{4}[-\s]?){3}\d{4}\b',
    'address': r'\d+\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr|Court|Ct|Place|Pl)(?:\s+\w+)*(?:\s+[A-Z]{2}\s+\d{5})?',
}

# Counter for unique placeholders
pii_counters = {pii_type: 0 for pii_type in pii_patterns.keys()}

def detect_and_mask_pii(text: str) -> Tuple[str, Dict[str, str]]:
    """Detect PII and replace with semantic placeholders"""
    global pii_counters
    masked_text = text
    replacement_map = {}
    
    for pii_type, pattern in pii_patterns.items():
        matches = list(re.finditer(pattern, text, re.IGNORECASE))
        
        # Process matches in reverse order to maintain string positions
        for match in reversed(matches):
            original_value = match.group()
            
            # Generate semantic placeholder
            pii_counters[pii_type] += 1
            placeholder = f"[{pii_type.upper()}_{pii_counters[pii_type]}]"
            
            # Replace in text
            masked_text = (
                masked_text[:match.start()] + 
                placeholder + 
                masked_text[match.end():]
            )
            
            # Store replacement mapping
            replacement_map[placeholder] = original_value
    
    return masked_text, replacement_map

def restore_pii(text: str, replacement_map: Dict[str, str]) -> str:
    """Restore original PII values from placeholders"""
    restored_text = text
    
    for placeholder, original_value in replacement_map.items():
        restored_text = restored_text.replace(placeholder, original_value)
    
    return restored_text

class PIIValidationResult(BaseModel):
    contains_pii: bool
    detected_types: List[str]
    risk_level: str
    recommendation: str

@lilypad.trace()
@llm.call(provider="openai", model="gpt-4o-mini", response_model=PIIValidationResult)
def advanced_pii_detection(text: str, detected_types: List[str]) -> PIIValidationResult:
    return f"""
    Analyze this text for potential PII that might not be caught by regex patterns:
    
    Text: "{text}"
    
    Already detected: {detected_types}
    
    Look for:
    - Names that might be personal
    - Sensitive personal details
    - Account numbers or IDs
    - Other identifying information
    
    Assess the overall privacy risk and provide recommendations.
    """

@lilypad.trace()
@llm.call(provider="openai", model="gpt-4o-mini")
def handle_masked_customer_support(customer_message: str) -> str:
    return f"""
    Help this customer with their request: {customer_message}
    
    Note: Any values in [BRACKETS] are placeholder values for privacy protection.
    Provide helpful responses that reference these placeholders when needed.
    """

@lilypad.trace()
def secure_customer_support(customer_message: str) -> str:
    # Step 1: Detect and mask PII
    masked_message, replacement_map = detect_and_mask_pii(customer_message)
    
    print(f"Original: {customer_message}")
    print(f"Masked: {masked_message}")
    print(f"Detected PII types: {list(set([k.split('_')[0] for k in replacement_map.keys()]))}")
    
    # Step 2: Advanced PII detection for missed patterns
    detected_types = list(set([k.split('_')[0] for k in replacement_map.keys()]))
    validation = advanced_pii_detection(masked_message, detected_types)
    
    if validation.risk_level == "HIGH":
        print(f"Warning: {validation.recommendation}")
        # Could block processing or request user confirmation
    
    # Step 3: Process with AI using masked data
    masked_response = handle_masked_customer_support(masked_message)
    
    # Step 4: Restore PII in response
    final_response = restore_pii(masked_response, replacement_map)
    
    print(f"AI Response (masked): {masked_response}")
    print(f"Final Response: {final_response}")
    
    return final_response

# Example usage showing privacy protection
def demo_pii_protection():
    test_messages = [
        "My email john.doe@company.com isn't receiving notifications",
        "Call me at 555-123-4567 about my order #12345", 
        "My card 4532-1234-5678-9012 was charged twice",
        "I live at 123 Main St, Boston MA 02101 and need help"
    ]
    
    for message in test_messages:
        print("\n" + "="*60)
        print("SECURE PROCESSING")
        print("="*60)
        
        response = secure_customer_support(message)
        
        print(f"\nFinal secure response: {response}")

# Advanced PII detection for specific domains
def mask_with_context_preservation(text: str, domain_specific_patterns: Dict[str, str] = None) -> Tuple[str, Dict[str, str]]:
    """Enhanced masking that preserves semantic context"""
    # Temporarily add domain-specific patterns if provided
    original_patterns = pii_patterns.copy()
    if domain_specific_patterns:
        pii_patterns.update(domain_specific_patterns)
    
    try:
        masked_text, replacement_map = detect_and_mask_pii(text)
        
        # Add context hints to placeholders
        enhanced_replacements = {}
        for placeholder, original in replacement_map.items():
            if 'EMAIL' in placeholder:
                enhanced_replacements[placeholder] = f"[USER_EMAIL_ADDRESS]"
            elif 'PHONE' in placeholder:
                enhanced_replacements[placeholder] = f"[USER_PHONE_NUMBER]"
            elif 'CREDIT_CARD' in placeholder:
                enhanced_replacements[placeholder] = f"[USER_PAYMENT_METHOD]"
            else:
                enhanced_replacements[placeholder] = placeholder
        
        # Apply enhanced placeholders
        for old_placeholder, new_placeholder in enhanced_replacements.items():
            if old_placeholder in masked_text:
                masked_text = masked_text.replace(old_placeholder, new_placeholder)
        
        return masked_text, replacement_map
    finally:
        # Restore original patterns
        pii_patterns.clear()
        pii_patterns.update(original_patterns)

if __name__ == "__main__":
    demo_pii_protection()
```

**Why this approach works better:**

- **Privacy by Design:** PII never leaves your infrastructure in its original form
- **Context Preservation:** Semantic placeholders maintain meaning for AI processing
- **Regulatory Compliance:** Reduces risk of GDPR, CCPA, and other privacy violations

### The Takeaway

PII masking enables AI processing of personal data without privacy risks by using semantic placeholders that preserve context while protecting sensitive information. This pattern ensures compliance while maintaining AI effectiveness.

---
*Part of the "Effective AI Engineering" series - practical tips for building better applications with AI components.*