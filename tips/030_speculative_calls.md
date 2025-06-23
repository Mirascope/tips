## Effective AI Engineering #30: Speculative Calls

**You're running fraud detection on every transaction, but 99% of them are legitimate.** While your AI classifier determines if a payment is fraudulent, legitimate customers wait unnecessarily for their transactions to process.

Most fraud detection systems classify first, then process. But when the vast majority of transactions are legitimate, you can start processing the payment while classification runs in parallel, canceling only if fraud is detected.

### The Problem

Many developers implement fraud detection by classifying first, then processing the transaction. This creates challenges that aren't immediately obvious:

```python
# BEFORE: Sequential fraud detection blocks payment processing
from mirascope.core import anthropic, prompt_template
import lilypad
import time

@lilypad.trace()
@anthropic.call("claude-3-5-sonnet-20241022")
@prompt_template("Analyze this transaction for fraud: {transaction_data}")
def classify_transaction(transaction_data: str) -> str:
    pass

@lilypad.trace()
def process_payment(transaction_data: str) -> str:
    # Simulate payment processing
    time.sleep(0.5)  # API calls to payment processor
    return f"Payment processed for: {transaction_data}"

@lilypad.trace()
def handle_transaction(transaction_data: str) -> str:
    start_time = time.time()
    
    # Step 1: Check for fraud first (adds latency for all transactions)
    fraud_result = classify_transaction(transaction_data)
    print(f"Fraud classification took: {time.time() - start_time:.2f}s")
    
    # Step 2: Process payment only if not fraud
    if "fraud" not in fraud_result.lower():
        result = process_payment(transaction_data)
        print(f"Total time: {time.time() - start_time:.2f}s")
        return result
    else:
        return "Transaction blocked: fraud detected"

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
from mirascope.core import anthropic, prompt_template
import lilypad
import asyncio
import time

@lilypad.trace()
@anthropic.call("claude-3-5-sonnet-20241022")
@prompt_template("Analyze this transaction for fraud: {transaction_data}")
async def classify_transaction_async(transaction_data: str) -> str:
    pass

@lilypad.trace()
async def process_payment_async(transaction_data: str) -> str:
    # Simulate payment processing
    await asyncio.sleep(0.5)  # API calls to payment processor
    return f"Payment processed for: {transaction_data}"

@lilypad.trace()
async def handle_transaction_speculative(transaction_data: str) -> str:
    start_time = time.time()
    
    # Start both fraud detection AND payment processing in parallel
    fraud_task = asyncio.create_task(classify_transaction_async(transaction_data))
    payment_task = asyncio.create_task(process_payment_async(transaction_data))
    
    # Wait for fraud classification to complete first
    fraud_result = await fraud_task
    
    if "fraud" in fraud_result.lower():
        # Fraud detected - cancel the payment processing
        payment_task.cancel()
        print(f"Fraud detected, payment canceled: {time.time() - start_time:.2f}s")
        return "Transaction blocked: fraud detected"
    else:
        # Legitimate transaction - wait for payment to complete
        payment_result = await payment_task
        print(f"Total time: {time.time() - start_time:.2f}s")
        return payment_result

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