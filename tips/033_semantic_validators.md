## Effective AI Engineering #33: Semantic Validators

**Are your AI responses technically correct but completely missing the point?** Your model generates grammatically perfect text that doesn't answer the user's actual question or contradicts known facts.

Traditional validation catches syntax errors and format issues, but semantic correctness requires understanding meaning, context, and factual accuracy. Human reviewers can spot these issues instantly, but manual validation doesn't scale.

### The Problem

Many developers only validate AI outputs for format and basic safety without checking semantic accuracy. This creates challenges that aren't immediately obvious:

```python
# BEFORE: Only basic validation
from mirascope.core import llm
import lilypad
import re

@lilypad.trace()
@llm.call(provider="openai", model="gpt-4o-mini")
def generate_product_answer(question: str, product_info: str) -> str:
    return f"""
    Answer this customer question: {question}
    Base your answer on this product information: {product_info}
    """

def basic_validation(response: str) -> bool:
    """Basic format validation only"""
    # Check if response is not empty
    if not response or len(response.strip()) < 10:
        return False
    
    # Check for profanity or inappropriate content
    inappropriate_words = ["damn", "hell", "hate"]
    if any(word in response.lower() for word in inappropriate_words):
        return False
    
    # Check basic format
    if not re.search(r'[.!?]$', response.strip()):
        return False
    
    return True

def handle_product_question(question: str, product_info: str) -> str:
    response = generate_product_answer(question, product_info)
    
    if basic_validation(response):
        return response
    else:
        return "I apologize, I cannot provide a proper answer right now."

# Misses semantic issues like factual errors or irrelevant answers
product_info = "Our laptop has 16GB RAM, Intel i7 processor, runs Windows 11"
question = "How much storage does this laptop have?"
answer = handle_product_question(question, product_info)  # May give RAM info instead of storage
```

**Why this approach falls short:**

- **Semantic Drift:** Responses may be well-formed but address the wrong question
- **Factual Errors:** AI might contradict provided information or make up details
- **Context Misalignment:** Answers may be correct in general but inappropriate for the specific context

### The Solution: AI-Powered Semantic Validation

A better approach is to use AI validators that understand meaning, check factual consistency, and verify contextual appropriateness. This pattern catches semantic errors that rule-based systems miss.

```python
# AFTER: Comprehensive semantic validation
from mirascope.core import anthropic, prompt_template
from pydantic import BaseModel
import lilypad
from typing import List, Optional
from enum import Enum

class ValidationIssue(Enum):
    FACTUAL_ERROR = "factual_error"
    QUESTION_MISMATCH = "question_mismatch"
    CONTEXT_CONTRADICTION = "context_contradiction"
    INCOMPLETE_ANSWER = "incomplete_answer"
    HALLUCINATION = "hallucination"

class SemanticValidationResult(BaseModel):
    is_valid: bool
    issues: List[ValidationIssue]
    explanation: str
    suggested_improvements: Optional[str] = None

class FactualAccuracy(BaseModel):
    is_accurate: bool
    contradictions: List[str]
    unsupported_claims: List[str]

class QuestionAlignment(BaseModel):
    addresses_question: bool
    missing_aspects: List[str]

@lilypad.trace()
@llm.call("claude-3-5-sonnet-20241022", response_model=FactualAccuracy)
def validate_factual_accuracy(question: str, source_info: str, response: str) -> FactualAccuracy:
    return f"""
    Check if this response is factually accurate based on the provided information:
    
    Question: "{question}"
    Provided Information: "{source_info}"
    AI Response: "{response}"
    
    Verify:
    1. Does the response contradict any provided facts?
    2. Does it make claims not supported by the source?
    3. Are all factual statements accurate?
    """

@lilypad.trace()
@llm.call("claude-3-5-sonnet-20241022", response_model=QuestionAlignment)
def validate_question_alignment(question: str, response: str) -> QuestionAlignment:
    return f"""
    Evaluate how well this response addresses the original question:
    
    Question: "{question}"
    AI Response: "{response}"
    
    Check:
    1. Does the response directly answer what was asked?
    2. Are there important aspects of the question left unaddressed?
    3. Is the response relevant to the user's intent?
    """

@lilypad.trace()
@llm.call("claude-3-5-sonnet-20241022", response_model=SemanticValidationResult)
def comprehensive_semantic_validation(
    question: str, 
    source_info: str, 
    response: str,
    factual_result: str,
    alignment_result: str
) -> SemanticValidationResult:
    return f"""
    Perform comprehensive semantic validation of this AI response:
    
    Question: "{question}"
    Source Information: "{source_info}"
    AI Response: "{response}"
    
    Factual Check: {factual_result}
    Question Alignment: {alignment_result}
    
    Provide overall assessment considering:
    - Semantic correctness
    - Completeness of answer
    - Appropriateness for context
    - Risk of user confusion
    
    Determine if this response should be shown to users.
    """

@lilypad.trace()
async def semantic_validate_response(question: str, source_info: str, response: str) -> SemanticValidationResult:
    # Parallel validation checks
    factual_check = validate_factual_accuracy(question, source_info, response)
    alignment_check = validate_question_alignment(question, response)
    
    # Comprehensive semantic analysis
    validation_result = comprehensive_semantic_validation(
        question, 
        source_info, 
        response,
        str(factual_check),
        str(alignment_check)
    )
    
    # Apply validation thresholds
    if not factual_check.is_accurate:
        validation_result.is_valid = False
        validation_result.issues.append(ValidationIssue.FACTUAL_ERROR)
    
    if not alignment_check.addresses_question:
        validation_result.is_valid = False
        validation_result.issues.append(ValidationIssue.QUESTION_MISMATCH)
    
    return validation_result

@lilypad.trace()
@llm.call(provider="openai", model="gpt-4o-mini")
def generate_product_answer(question: str, product_info: str) -> str:
    return f"""
    Answer this customer question: {question}
    Base your answer on this product information: {product_info}
    
    Be specific, accurate, and directly address what was asked.
    """

@lilypad.trace()
async def validated_product_support(question: str, product_info: str, max_retries: int = 2) -> str:
    for attempt in range(max_retries + 1):
        # Generate response
        response = generate_product_answer(question, product_info)
        
        # Validate semantically
        validation = await semantic_validate_response(question, product_info, response)
        
        print(f"Attempt {attempt + 1}:")
        print(f"Response: {response}")
        print(f"Valid: {validation.is_valid}")
        print(f"Issues: {[issue.value for issue in validation.issues]}")
        print(f"Explanation: {validation.explanation}")
        
        if validation.is_valid:
            return response
        
        if attempt < max_retries:
            print(f"Retrying with improvements: {validation.suggested_improvements}")
            # Could modify prompt based on validation feedback
        else:
            print("Max retries reached. Escalating to human review.")
            return "I need to research this further. A specialist will follow up with you shortly."
    
    return response

# Example usage showing semantic validation in action
async def demo_semantic_validation():
    product_info = """
    Product: UltraBook Pro X1
    - RAM: 16GB DDR4
    - Processor: Intel Core i7-12700H
    - Storage: 512GB NVMe SSD
    - Display: 14" 4K OLED
    - OS: Windows 11 Pro
    - Battery: 8-hour typical usage
    - Weight: 2.8 lbs
    """
    
    test_questions = [
        "How much storage does this laptop have?",
        "What's the battery life?",
        "Can this run gaming applications?",
        "What's the screen size and resolution?"
    ]
    
    for question in test_questions:
        print(f"\n{'='*60}")
        print(f"Question: {question}")
        print('='*60)
        
        answer = await validated_product_support(question, product_info)
        print(f"Final Answer: {answer}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(demo_semantic_validation())
```

**Why this approach works better:**

- **Meaning-Aware Validation:** Catches responses that are grammatically correct but semantically wrong
- **Factual Consistency:** Prevents AI from contradicting provided information or hallucinating details
- **User Intent Alignment:** Ensures responses actually address what users asked rather than tangentially related topics

### The Takeaway

Semantic validators use AI to validate AI, checking meaning and factual accuracy beyond what rule-based systems can detect. This pattern prevents semantically incorrect responses from reaching users while maintaining natural language quality.

---
*Part of the "Effective AI Engineering" series - practical tips for building better applications with AI components.*