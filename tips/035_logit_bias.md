## Effective AI Engineering #35: Logit Bias

**Does your AI writing sound robotic with telltale patterns?** Every response contains em-dashes, starts with "Certainly!" or uses the same transitional phrases that scream "AI-generated content."

AI models develop distinctive linguistic fingerprints - specific tokens, phrases, and structures they favor. These patterns make generated content easily identifiable and can undermine authenticity in applications where natural-sounding text matters.

### The Problem

Many developers accept default AI behavior without considering how token-level adjustments can improve output quality. This creates challenges that aren't immediately obvious:

```python
# BEFORE: Default model behavior with distinctive AI patterns
from mirascope.core import llm
import lilypad

@lilypad.trace()
@llm.call(provider="openai", model="gpt-4o-mini")
def generate_email_response(customer_message: str) -> str:
    return f"Write a professional email response to this customer inquiry: {customer_message}"

# Default responses often have AI tells
customer_messages = [
    "I'd like to return this product",
    "When will my order ship?",
    "I'm having trouble with setup"
]

for message in customer_messages:
    response = generate_email_response(message)
    print(f"Response: {response}")
    # Likely contains: "Certainly!", "I'd be happy to help", em-dashes, etc.
```

**Why this approach falls short:**

- **AI Fingerprints:** Distinctive patterns make content obviously machine-generated
- **Limited Stylistic Control:** Can't fine-tune specific linguistic preferences without prompt engineering
- **Repetitive Language:** Same phrases appear across different contexts, reducing authenticity

### The Solution: Strategic Logit Bias for Natural Language

A better approach is to use logit bias to suppress overused AI tokens and encourage more natural alternatives. This pattern gives you fine-grained control over language patterns at the token level.

```python
# AFTER: Logit bias for more natural language generation
from mirascope.core import anthropic, prompt_template
import lilypad
from typing import Dict

# Common AI tokens to discourage
ai_tells = {
            # Overly formal starts
            "Certainly": -0.5,
            "Absolutely": -0.3,
            "Indeed": -0.4,
            
            # Robotic transitions
            "However": -0.2,
            "Furthermore": -0.3,
            "Moreover": -0.3,
            "Additionally": -0.2,
            
            # AI-specific punctuation patterns
            "—": -0.8,  # Em-dash
            "–": -0.6,  # En-dash
            
            # Overly helpful language
            "happy": -0.2,  # "I'd be happy to"
            "assist": -0.3,
            "assistance": -0.3,
            
            # Generic closers
            "hesitate": -0.4,  # "don't hesitate to"
            "reach": -0.2,     # "feel free to reach out"
        }
        
        # Tokens to encourage for more natural speech
        self.natural_alternatives = {
            # More conversational starts
            "Thanks": 0.2,
            "Sure": 0.3,
            "Hi": 0.2,
            "Got": 0.2,  # "Got it"
            
            # Natural transitions
            "So": 0.3,
            "Also": 0.2,
            "Plus": 0.2,
            "And": 0.1,
            
            # Casual language
            "just": 0.2,
            "really": 0.1,
            "pretty": 0.1,
            "actually": 0.2,
        }
    
    def get_bias_config(self, style: str = "professional") -> Dict[str, float]:
        """Get logit bias configuration for different styles"""
        base_bias = {**self.ai_tells}  # Start with suppressions
        
        if style == "casual":
            # Encourage more conversational tokens
            base_bias.update(self.natural_alternatives)
            # Further suppress formal language
            base_bias.update({
                "sincerely": -0.5,
                "regards": -0.5,
                "formal": -0.3,
            })
        
        elif style == "professional":
            # Balanced approach - suppress AI tells but keep professional tone
            base_bias.update({
                k: v * 0.5 for k, v in self.natural_alternatives.items()
            })
        
        elif style == "creative":
            # Encourage varied vocabulary
            base_bias.update(self.natural_alternatives)
            base_bias.update({
                "unique": 0.2,
                "interesting": 0.2,
                "creative": 0.1,
            })
        
        return base_bias

generator = NaturalLanguageGenerator()

@lilypad.trace()
@llm.call(
    "claude-3-5-sonnet-20241022",
    call_params={"logit_bias": generator.get_bias_config("professional")}
)
def generate_natural_email_response(customer_message: str) -> str:
    return f"""
    Write a professional email response to this customer inquiry: {customer_message}
    Keep the tone helpful but natural, avoiding overly formal or robotic language.
    """

@lilypad.trace()
@llm.call(
    "claude-3-5-sonnet-20241022", 
    call_params={"logit_bias": generator.get_bias_config("casual")}
)
def generate_casual_response(message: str) -> str:
    return f"""
    Write a casual, friendly response to: {message}
    Sound like a real person, not a customer service bot.
    """

# Domain-specific bias configurations
class TechnicalWritingBias:
    @staticmethod
    def get_tech_bias() -> Dict[str, float]:
        return {
            # Suppress marketing language
            "amazing": -0.5,
            "incredible": -0.5,
            "revolutionary": -0.7,
            "game-changing": -0.8,
            
            # Encourage precision
            "specifically": 0.2,
            "exactly": 0.2,
            "precisely": 0.1,
            "typically": 0.2,
            
            # Technical clarity
            "implementation": 0.1,
            "configuration": 0.1,
            "documentation": 0.1,
        }

@lilypad.trace()
@llm.call(
    "claude-3-5-sonnet-20241022",
    call_params={"logit_bias": TechnicalWritingBias.get_tech_bias()}
)
def generate_technical_explanation(concept: str) -> str:
    return f"""
    Explain this technical concept clearly: {concept}
    Focus on accuracy and practical understanding.
    """

# Creative writing with enhanced variety
class CreativeWritingBias:
    @staticmethod
    def get_creative_bias() -> Dict[str, float]:
        return {
            # Suppress clichés
            "suddenly": -0.8,
            "amazing": -0.4,
            "incredible": -0.4,
            "breathtaking": -0.6,
            
            # Encourage varied sentence starts
            "As": -0.3,  # Overused sentence starter
            "The": -0.1, # Reduce definitive article starts
            "In": -0.2,  # Common opener
            
            # Promote vivid language
            "vivid": 0.3,
            "striking": 0.2,
            "compelling": 0.2,
            "nuanced": 0.3,
        }

def demo_logit_bias_comparison():
    """Compare outputs with and without logit bias"""
    test_message = "I need help setting up my new software"
    
    print("=== WITHOUT LOGIT BIAS ===")
    default_response = generate_email_response(test_message)
    print(f"Default: {default_response}")
    
    print("\n=== WITH PROFESSIONAL BIAS ===")
    natural_response = generate_natural_email_response(test_message)
    print(f"Natural: {natural_response}")
    
    print("\n=== WITH CASUAL BIAS ===")
    casual_response = generate_casual_response(test_message)
    print(f"Casual: {casual_response}")
    
    # Analyze differences
    ai_tells_found = []
    for tell in ["Certainly", "However", "I'd be happy", "—"]:
        if tell in default_response:
            ai_tells_found.append(tell)
    
    print(f"\nAI tells in default response: {ai_tells_found}")

# Advanced: Dynamic bias based on context
def context_aware_bias(content_type: str, audience: str) -> Dict[str, float]:
    """Generate logit bias based on content type and audience"""
    base_bias = generator.get_bias_config("professional")
    
    if audience == "technical":
        base_bias.update(TechnicalWritingBias.get_tech_bias())
    elif audience == "general":
        base_bias.update(generator.get_bias_config("casual"))
    
    if content_type == "marketing":
        # Allow some promotional language but keep it natural
        base_bias.update({
            "exciting": 0.1,
            "innovative": 0.1,
            "solution": 0.1,
        })
    
    return base_bias

if __name__ == "__main__":
    demo_logit_bias_comparison()
```

**Why this approach works better:**

- **Reduced AI Fingerprints:** Suppressing common AI tokens makes content less obviously machine-generated
- **Style Flexibility:** Different bias configurations adapt to various contexts and audiences
- **Token-Level Control:** Fine-grained adjustments that prompt engineering alone cannot achieve

### The Takeaway

Logit bias provides surgical control over AI language patterns, suppressing robotic tells while encouraging more natural alternatives. This pattern helps AI-generated content blend seamlessly with human writing styles.

---
*Part of the "Effective AI Engineering" series - practical tips for building better applications with AI components.*