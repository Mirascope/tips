## Effective AI Engineering #30: Speculative Calls

Your fraud and abuse detection just got a whole lot better.
The catch? Also much slower. It takes almost as much time as your core logic now!

"Will users wait around that long?" You think to yourself.
You'd rather not find out.

How can we avoid potential churn and keep our platform safe from fraud?
Simple: Keep Reading.

### The Problem

Many developers implement fraud detection by classifying first, then processing the transaction. This creates challenges that aren't immediately obvious:

```python
# BEFORE: Sequential fraud detection blocks payment processing
from mirascope import llm, prompt_template
from pydantic import BaseModel

class FraudClassification(BaseModel):
    reasoning: str
    is_fraud: bool

@llm.call(provider="anthropic", model="claude-3-5-sonnet-20241022", response_model=FraudClassification)
@prompt_template("Analyze this transaction for fraud: {transaction_data}")
def classify_transaction(transaction_data: str): ...


def handle_transaction(transaction_data: str) -> str:
    # Step 1: Check for fraud first (adds latency for all transactions)
    fraud_result = classify_transaction(transaction_data)
    
    # Step 2: Process payment only if not fraud
    if fraud_result.is_fraud:
        return "Transaction blocked: fraud detected"
    return process_payment(transaction_data)

# Every legitimate transaction waits for fraud classification
result = handle_transaction("$50 coffee purchase from regular merchant")
```

**Why this approach falls short:**

- **Sequential Latency:** Every legitimate transaction waits for fraud detection before processing
- **Underutilized Resources:** Payment systems idle during classification instead of doing useful work
- **Poor Customer Experience:** Simple purchases feel slow despite being completely legitimate

### The Solution: Parallel Speculative Execution

A better approach is to start payment processing in parallel with fraud detection, since most transactions are legitimate. This pattern optimizes for the common case while canceling work if fraud is detected.

```python
# AFTER: Parallel fraud detection with speculative processing
from mirascope import llm, prompt_template
from pydantic import BaseModel

class FraudClassification(BaseModel):
    reasoning: str
    is_fraud: bool

@llm.call(provider="anthropic", model="claude-3-5-sonnet-20241022", response_model=FraudClassification)
@prompt_template("Analyze this transaction for fraud: {transaction_data}")
async def classify_transaction(transaction_data: str): ...


async def handle_transaction_speculative(transaction_data: str) -> str:    
    # Start both fraud detection AND payment processing in parallel
    fraud_task = asyncio.create_task(classify_transaction(transaction_data))
    payment_task = asyncio.create_task(process_payment(transaction_data))
    
    # Wait for fraud classification to complete first
    fraud_result = await fraud_task
    
    if fraud_result.is_fraud:
        # Fraud detected - cancel the payment processing
        payment_task.cancel()
        await cancel_transaction(transaction_data)
        return "Transaction blocked: fraud detected"

    # Legitimate transaction - wait for payment to complete
    return await payment_task

# Legitimate transactions get faster processing
result = asyncio.run(handle_transaction_speculative("$50 coffee purchase from regular merchant"))
```

**Why this approach works better:**

- **Reduced Latency:** Legitimate transactions complete faster since payment processing starts immediately
- **Optimized for Common Case:** Since 99% of transactions are valid, speculation pays off almost always
- **Increased Costs:** You'll run payment processing for fraudulent transactions too, increasing computational costs

### The Takeaway

Speculative calls eliminate classification bottlenecks by starting likely work in parallel, dramatically reducing latency when most cases follow the happy path. This pattern trades slightly higher costs for significantly better user experience on legitimate transactions.

---
*Part of the "Effective AI Engineering" series - practical tips for building better applications with AI components.*