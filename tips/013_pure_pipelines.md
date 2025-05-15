## Effective AI Engineering #13: Pure Pipelines - Stop Your AI System From Traumatizing Real Users During Testing

**Every evaluation run emails a real customer. Every test fires a live notification. Surprise!** When your AI pipeline mixes external data and side effects, testing becomes a high-stakes game of Russian roulette with user experience as the casualty.

Your AI system needs constant evaluation to improve, but how can you evaluate when every test run might send gibberish to customers, update production databases, or trigger a cascade of real-world notifications? This isn't just an annoyance—it's a reliability crisis waiting to explode that makes meaningful evaluation nearly impossible.

### The Problem

Many developers build AI pipelines that directly mix external data fetching and side effects:

```python
# BEFORE: Tangled Pipeline With External Dependencies and Side Effects
def customer_support_pipeline(ticket_id: str):
    # External dependency - fetch latest ticket data
    ticket = database.get_ticket(ticket_id)
    customer = database.get_customer(ticket.customer_id)
    previous_tickets = database.get_customer_history(ticket.customer_id)
    
    # Generate response with external inputs
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
- **Impossible to Debug:** When errors occur, you can't replay the exact scenario that caused the failure.
- **Limited "What-If" Scenarios:** You can't easily explore alternative approaches by modifying inputs without rebuilding the entire context.

### The Solution: Pure and Idempotent Pipelines

A better approach is to separate your AI pipeline into three distinct phases: input collection, pure processing, and side effect execution. This creates a predictable, testable system that can be evaluated consistently.

```python
# AFTER: Pure Pipeline with Decoupled Dependencies and Side Effects
from pydantic import BaseModel
from typing import List, Optional

# Step 1: Define clear data models for inputs and outputs
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
    tickets: List[str]

class SupportPipelineInput(BaseModel):
    ticket: Ticket
    customer: Customer
    history: CustomerHistory

class SupportPipelineOutput(BaseModel):
    response: str
    ticket_id: str
    customer_email: str
    subject: str

# Step 2: Input collection function - responsibility is ONLY gathering inputs
def collect_support_inputs(ticket_id: str) -> SupportPipelineInput:
    ticket = database.get_ticket(ticket_id)
    customer = database.get_customer(ticket.customer_id)
    history = database.get_customer_history(ticket.customer_id)
    
    # Return structured input data
    return SupportPipelineInput(
        ticket=ticket,
        customer=customer,
        history=history
    )

# Step 3: Pure processing function - no external calls, only computation
def process_support_ticket(inputs: SupportPipelineInput) -> SupportPipelineOutput:
    # Generate response without external dependencies
    prompt = f"""
    Respond to this customer support ticket:
    Ticket: {inputs.ticket.description}
    Customer Name: {inputs.customer.name}
    Previous Issues: {inputs.history.tickets}
    """
    
    response = llm_client.generate(prompt=prompt)
    
    # Return structured output data
    return SupportPipelineOutput(
        response=response,
        ticket_id=inputs.ticket.id,
        customer_email=inputs.customer.email,
        subject=inputs.ticket.subject
    )

# Step 4: Side effect function - responsibility is ONLY executing side effects
def execute_support_actions(output: SupportPipelineOutput) -> None:
    database.update_ticket_status(output.ticket_id, "responded")
    slack.send_message(f"Ticket {output.ticket_id} handled")
    email.send(
        to=output.customer_email,
        subject=f"Re: {output.subject}",
        body=output.response
    )

# Step 5: Orchestrator function that connects the three phases
def customer_support_pipeline(ticket_id: str) -> str:
    inputs = collect_support_inputs(ticket_id)
    outputs = process_support_ticket(inputs)
    execute_support_actions(outputs)
    return outputs.response

# For evaluation - we can run just the pure processing part with saved inputs
def evaluate_support_pipeline(saved_inputs: List[SupportPipelineInput]):
    results = []
    for input_case in saved_inputs:
        output = process_support_ticket(input_case)
        results.append(output)
    return results
```

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