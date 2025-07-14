---
tip_number: 13
tip_name: "Pure Pipelines - Stop Your AI System From Traumatizing Real Users During Testing"
categories: ["testing", "architecture", "evaluation"]
x_link: ""
linkedin_link: "https://www.linkedin.com/posts/skylarbpayne_youre-scared-to-test-your-ai-what-if-activity-7329204368811913218-P9gW?utm_source=share&utm_medium=member_desktop&rcm=ACoAABKpCf4BI_Yx2u7h66sgi5z1NF3aEYFHgps"
---

## Effective AI Engineering #13: Pure Pipelines - Stop Your AI System From Traumatizing Real Users During Testing

**Every evaluation run emails a real customer. Every test fires a live notification. Surprise!** When your AI pipeline mixes external data and side effects, testing becomes a high-stakes game of Russian roulette with user experience as the casualty.

Your AI system needs constant evaluation to improve, but how can you evaluate when every test run might send gibberish to customers, update production databases, or trigger a cascade of real-world notifications? This isn't just an annoyance—it's a reliability crisis waiting to explode that makes meaningful evaluation nearly impossible.

### The Problem

Many developers build AI pipelines that directly mix external data fetching and side effects:

```python
# BEFORE: Tangled Pipeline With External Dependencies and Side Effects
class Ticket(BaseModel):
    id: str
    description: str
    customer_id: str
    subject: str

class Customer(BaseModel):
    id: str
    name: str
    email: str

class CustomerHistory(BaseModel):
    tickets: list[str]

def customer_support_pipeline(ticket_id: str):
    # External dependency - fetch latest ticket data
    ticket: Ticket = database.get_ticket(ticket_id)
    customer: Customer = database.get_customer(ticket.customer_id)
    previous_tickets: CustomerHistory = database.get_customer_history(ticket.customer_id)
    
    # Notice how the prompt is kind of hidden in this function, making
    # it difficult to reproduce this LLM call in a pure manner
    prompt = f"""
    Respond to this customer support ticket:
    Ticket: {ticket.description}
    Customer Name: {customer.name}
    Previous Issues: {previous_tickets}
    """
    
    response = llm_client.generate(prompt=prompt)
    
    # Side effects intermingled with processing
    database.update_ticket_status(ticket_id, "responded")
    slack.send_message(f"Ticket {ticket_id} handled with response: {response[:100]}...")
    email.send(
        to=customer.email,
        subject=f"Re: {ticket.subject}",
        body=response
    )
    
    return response
```

**Why this approach falls short:**

- **Unreproducible Evaluations:** External data sources change, making it impossible to compare system outputs over time.
- **Testing Nightmares:** Unit tests become probabilistic as live data changes, and you can't test without triggering real-world side effects.
- **Unintended Consequences:** During development and testing, real users receive emails, Slack notifications fire, and database records change.
- **Hard to Debug:** When errors occur, you can't replay the exact scenario that caused the failure.
- **Limited "What-If" Scenarios:** You can't easily explore alternative approaches by modifying inputs without rebuilding the entire context.

### The Solution: Pure and Idempotent Pipelines

A better approach is to separate your AI pipeline into three distinct phases: input collection, pure processing, and side effect execution. This creates a predictable, testable system that can be evaluated consistently.

```python
# AFTER: Pure Pipeline with Decoupled Dependencies and Side Effects
from pydantic import BaseModel
from mirascope import llm, prompt_template



class SupportResponse(BaseModel):
    response: str

# Step 1: Define the pure LLM processing function -- this is a pure function we can run and evaluate without worry!
@llm.call(provider="openai", model="gpt-4o-mini", response_model=SupportResponse)
@prompt_template("""
SYSTEM: You are a helpful customer support assistant. Create a professional and helpful response.

USER: Respond to this customer support ticket:
Ticket: {description}
Customer Name: {customer_name}
Previous Issues: {previous_issues}
""")
def generate_support_response(description: str, customer_name: str, previous_issues: list[str]): 
    ...

# Step 2: Separate functions for the three pipeline phases
def customer_support_pipeline(ticket_id: str) -> str:
    # Phase 1: Input collection - gather external data
    ticket: Ticket = database.get_ticket(ticket_id)
    customer: Customer = database.get_customer(ticket.customer_id)
    history: CustomerHistory = database.get_customer_history(ticket.customer_id)
    
    # Phase 2: Pure processing - no side effects
    response = generate_support_response(
        description=ticket.description,
        customer_name=customer.name,
        previous_issues=history.tickets
    )
    
    # Phase 3: Side effects - all external actions grouped together
    database.update_ticket_status(ticket_id, "responded")
    slack.send_message(f"Ticket {ticket_id} handled")
    email.send(
        to=customer.email,
        subject=f"Re: {ticket.subject}",
        body=response.response
    )
    
    return response.response

# Evaluation is now simple - just call the pure function with saved inputs
def evaluate_support_pipeline(saved_inputs: list[tuple[str, str, list[str]]]):
    results = []
    for description, customer_name, previous_issues in saved_inputs:
        # Just call the pure function directly - no side effects
        response = generate_support_response(
            description=description,
            customer_name=customer_name,
            previous_issues=previous_issues
        )
        results.append(response)
    return results
```

And notice how using mirascope naturally guides us towards pure, idempotent functions!

**Why this approach works better:**

- **Reproducible Evaluations:** Input data can be saved and replayed for consistent comparisons over time.
- **Reliable Testing:** Each component can be tested in isolation without triggering real-world effects.
- **Development Safety:** You can develop and test without affecting real users or systems.
- **Powerful Debugging:** Issues can be precisely replicated by reusing the exact inputs that caused a failure.
- **"What-If" Analysis:** Easily modify saved inputs to evaluate different scenarios and approaches.
- **Clear Separation of Concerns:** Each function has a single responsibility, making the code more maintainable.

### The Takeaway

Design your AI systems with pure, idempotent pipelines by strictly separating input collection, computation, and side effects. This architecture pattern dramatically improves testing, evaluation, and debugging while reducing unexpected behavior. Your systems become more reliable, your evaluations more meaningful, and your users happier when they're not receiving test emails at 3 AM.

---
*Part of the "Effective AI Engineering" series - practical tips for building better applications with AI components.*