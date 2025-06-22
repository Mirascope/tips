## Effective AI Engineering #34: Gleaning

**Does your AI give up after one failed attempt?** Your validator catches an error in the response, but instead of learning from the feedback, you start over from scratch and likely repeat the same mistake.

Validation failures contain valuable information about what went wrong. Instead of discarding failed responses, you can feed the error details back to the AI and give it a chance to correct its mistakes iteratively.

### The Problem

Many developers treat validation failures as dead ends, regenerating responses from scratch without learning from errors. This creates challenges that aren't immediately obvious:

```python
# BEFORE: Discard failed responses and restart
from mirascope.core import llm
from pydantic import BaseModel
import lilypad

class ValidationResult(BaseModel):
    is_valid: bool
    errors: list[str]

@lilypad.trace()
@llm.call(provider="openai", model="gpt-4o-mini")
def generate_description(product_name: str) -> str:
    return f"Write a product description for: {product_name}"

@lilypad.trace()
@llm.call("claude-3-5-sonnet-20241022", response_model=ValidationResult)
def validate_description(product_name: str, description: str) -> ValidationResult:
    return f"""
    Validate this product description for accuracy and completeness:
    Product: {product_name}
    Description: {description}
    
    Check for missing key features, inaccurate claims, or poor structure.
    """

def create_validated_description(product_name: str, max_attempts: int = 3) -> str:
    for attempt in range(max_attempts):
        print(f"Attempt {attempt + 1}")
        
        # Generate fresh response each time
        description = generate_description(product_name)
        validation = validate_description(product_name, description)
        
        if validation.is_valid:
            return description
        else:
            print(f"Validation failed: {validation.errors}")
            # Discards response and starts over - waste of information
    
    return "Unable to generate valid description"

# Each attempt starts from zero - doesn't learn from previous failures
result = create_validated_description("Wireless Bluetooth Headphones")
```

**Why this approach falls short:**

- **Wasted Learning:** Validation feedback contains specific improvement guidance that gets ignored
- **Repeated Mistakes:** Starting fresh often reproduces the same errors that caused initial failures
- **Inefficient Iteration:** Each attempt burns full generation tokens instead of building on partial progress

### The Solution: Iterative Error-Driven Improvement (Gleaning)

A better approach is to use validation feedback to guide iterative improvements of the same response. This pattern turns validation failures into learning opportunities for progressive refinement.

```python
# AFTER: Iterative improvement using validation feedback
from mirascope.core import anthropic, prompt_template
from pydantic import BaseModel
import lilypad
from typing import Optional

class DetailedValidation(BaseModel):
    is_valid: bool
    errors: list[str]
    suggestions: list[str]

@lilypad.trace()
@llm.call(provider="openai", model="gpt-4o-mini")
def generate_initial_description(product_name: str) -> str:
    return f"Write a product description for: {product_name}"

@lilypad.trace()
@llm.call("claude-3-5-sonnet-20241022", response_model=DetailedValidation)
def detailed_validation(product_name: str, description: str) -> DetailedValidation:
    return f"""
    Validate this product description and provide specific improvement guidance:
    
    Product: {product_name}
    Description: {description}
    
    Evaluate:
    1. Accuracy of claims
    2. Completeness of key features
    3. Writing quality and structure
    4. Marketing effectiveness
    
    Provide specific suggestions for fixing identified issues.
    """

@lilypad.trace()
@llm.call(provider="openai", model="gpt-4o-mini")
def improve_description(
    current_description: str, 
    errors: list[str], 
    suggestions: list[str],
    primary_issues: str
) -> str:
    return f"""
    Improve this product description based on the validation feedback:
    
    Original Description: {current_description}
    Validation Issues: {errors}
    Specific Suggestions: {suggestions}
    
    Revise the description to address all identified issues while keeping the good parts.
    Focus on fixing: {primary_issues}
    """

@lilypad.trace()
def gleaning_process(product_name: str, max_iterations: int = 4) -> tuple[str, list[str]]:
    """Iteratively improve response using validation feedback"""
    
    # Generate initial response
    current_description = generate_initial_description(product_name)
    improvement_history = [f"Initial: {current_description[:100]}..."]
    
    for iteration in range(max_iterations):
        print(f"\n=== Iteration {iteration + 1} ===")
        print(f"Current description: {current_description}")
            
            # Validate current response
            validation = detailed_validation(product_name, current_description)
            
            print(f"Valid: {validation.is_valid}")
            print(f"Issues: {validation.errors}")
            print(f"Suggestions: {validation.suggestions}")
            
            # Check if we've reached acceptable quality
            if validation.is_valid:
                print(f"✅ Target quality reached after {iteration + 1} iterations")
                return current_description, improvement_history
            
            # Use feedback to improve
            if validation.errors:
                primary_issues = "; ".join(validation.errors[:2])  # Focus on top issues
                
                improved_description = improve_description(
                    current_description,
                    validation.errors,
                    validation.suggestions,
                    primary_issues
                )
                
                print(f"Improved to: {improved_description}")
                
                # Track improvement
                improvement_history.append(
                    f"Iteration {iteration + 1}: Fixed {len(validation.errors)} issues"
                )
                
                current_description = improved_description
            else:
                # No specific errors but score too low - general improvement
                current_description = improve_description(
                    current_description,
                    ["Overall quality needs enhancement"],
                    validation.suggestions,
                    "general quality improvement"
                )
        
        print(f"⚠️  Max iterations reached. Final valid: {validation.is_valid}")
        return current_description, improvement_history

# Advanced gleaning with focused improvements
class FocusedGleaning(GleaningProcessor):
    @lilypad.trace()
    def focused_improvement(self, product_name: str, focus_areas: list[str]) -> str:
        """Gleaning with specific focus areas for targeted improvement"""
        
        current_description = generate_initial_description(product_name)
        
        for focus_area in focus_areas:
            print(f"\n🎯 Focusing on: {focus_area}")
            
            # Validate with specific focus
            validation = detailed_validation(product_name, current_description)
            
            # Filter feedback for current focus area
            relevant_errors = [
                error for error in validation.errors 
                if focus_area.lower() in error.lower()
            ]
            
            relevant_suggestions = [
                suggestion for suggestion in validation.suggestions
                if focus_area.lower() in suggestion.lower()
            ]
            
            if relevant_errors or relevant_suggestions:
                current_description = improve_description(
                    current_description,
                    relevant_errors or ["General improvement needed"],
                    relevant_suggestions or ["Enhance this area"],
                    focus_area
                )
                print(f"Improved for {focus_area}: {current_description[:100]}...")
        
        return current_description

# Example usage showing progressive improvement
def demo_gleaning():
    product = "Wireless Bluetooth Headphones"
    final_description, history = gleaning_process(product, max_iterations=3)
    
    print(f"\n{'='*60}")
    print("FINAL RESULT")
    print('='*60)
    print(f"Product: {product}")
    print(f"Final Description: {final_description}")
    print(f"\nImprovement History:")
    for step in history:
        print(f"  • {step}")

# Focused gleaning example
def demo_focused_gleaning():
    focused_gleaner = FocusedGleaning()
    
    focus_areas = ["technical specifications", "user benefits", "competitive advantages"]
    result = focused_gleaner.focused_improvement("Gaming Laptop", focus_areas)
    
    print(f"Focused result: {result}")

if __name__ == "__main__":
    demo_gleaning()
    print("\n" + "="*60)
    demo_focused_gleaning()
```

**Why this approach works better:**

- **Learning from Failures:** Each validation failure provides specific guidance for targeted improvements
- **Progressive Quality:** Builds on partial progress instead of starting over, leading to better final results
- **Efficient Token Usage:** Improves existing content rather than generating completely new responses each time

### The Takeaway

Gleaning transforms validation failures into iterative improvement opportunities, using error feedback to refine responses progressively. This pattern achieves higher quality outputs with fewer token costs than regeneration approaches.

---
*Part of the "Effective AI Engineering" series - practical tips for building better applications with AI components.*