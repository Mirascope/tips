## Tip #3: Structure Your Outputs for Reliable Systems

Often, the output from an LLM isn't the final product; it needs to feed into other parts of your software – updating a database, calling another API, displaying data in a UI. Just getting raw text back from the LLM makes this integration process surprisingly fragile.

**The Anti-Pattern: Parsing Text Downstream**

A common approach is to get a natural language response and then write separate code to parse it using string searching, regex, or complex conditional logic:

```python
# <<< CONCEPTUAL BEFORE: Parsing Raw Text >>>

raw_llm_output = llm.generate("Summarize the meeting and list action items.")
# raw_llm_output might be:
# "The meeting was about Project Phoenix. Key decisions were X and Y.
# Action Items:
# - John Doe to update slides by Friday.
# - Jane Smith to schedule follow-up."

# Fragile downstream parsing logic:
summary = raw_llm_output.split("Action Items:")[0].strip()
action_items_text = raw_llm_output.split("Action Items:")[1]
items = []
for line in action_items_text.strip().split('\n'):
    if line.startswith('-'):
        # ... complex logic to extract task, assignee, due date ...
        # What if the format changes slightly? This breaks!
        pass

# What if you need to validate the extracted data? More custom code needed here.
# What if you want the LLM's reasoning? Where does that fit?
```

**Why this fails:**

* **Brittle Integrations:** The slightest change in the LLM's output phrasing, formatting, or even capitalization can break your downstream parsing logic. This leads to constant maintenance headaches.
* **Difficult Validation:** How do you reliably check if the extracted "due date" is actually a date? Or if an "assignee" is a valid user? You have to build complex validation logic *after* fragile parsing.
* **Hard to Extend:** Want to add Chain-of-Thought reasoning? Or extract more nuanced data? You have to significantly complicate both the prompt *and* the already brittle parsing code.
* **Inconsistent Handling:** Parsing and validation logic often gets scattered across different parts of your application.

**The Better Way: Design for Structure Upfront with `response_model`**

Instead of asking for raw text, define the *structure* you need using a schema (like a Pydantic model) and use tools that help the LLM conform to it. This makes the interaction predictable and robust.

**Example (using Mirascope's `response_model`):**

```python
import os
from mirascope import llm, prompt_template, response_model
from pydantic import BaseModel, Field, field_validator, EmailStr
from typing import List, Optional

# Assume OPENAI_API_KEY is set
# from dotenv import load_dotenv; load_dotenv()

# 1. Define the desired output structure WITH validation
class ActionItem(BaseModel):
    task: str = Field(..., description="The specific action item description.")
    assignee_email: EmailStr = Field(..., description="The email address of the assignee.") # Use Pydantic types for validation!
    due_date: Optional[str] = Field(None, description="Optional due date (YYYY-MM-DD).")

    @field_validator('due_date')
    def check_date_format(cls, v):
        if v and not (len(v) == 10 and v[4] == '-' and v[7] == '-'): # Simple format check
             raise ValueError("Due date must be in YYYY-MM-DD format")
        return v

class StructuredMeetingSummary(BaseModel):
    summary: str = Field(..., description="A concise summary of the meeting.")
    action_items: List[ActionItem] = Field(..., description="A list of all action items.")
    # 2. Easier to extend for CoT: Add a field for reasoning!
    reasoning: Optional[str] = Field(None, description="Step-by-step thinking process to reach the summary and action items.")

# 3. Define a prompt asking for the structured output and potentially reasoning
SUMMARY_PROMPT = """
SYSTEM: You are an expert meeting summarizer. Analyze the provided meeting notes.
Provide a concise summary and extract all action items with assignees (email) and due dates.
{include_reasoning}

MEETING NOTES:
{meeting_notes}
"""

# 4. Use @response_model to enforce the structure
@llm("openai", model="gpt-4o") # Use a model good at tool use/structured output
@prompt_template(SUMMARY_PROMPT)
# Mirascope uses the Pydantic model to guide the LLM (via tools/functions)
@response_model(StructuredMeetingSummary, retries=2)
def get_structured_summary(meeting_notes: str, reasoning: bool = False):
    # Conditionally ask for reasoning based on the input flag
    include_reasoning = "Include your step-by-step reasoning process before the final output." if reasoning else ""
    # Return dictionary matching template variables not in function signature
    return {"include_reasoning": include_reasoning}

# --- Usage ---
notes = "Meeting notes text... John (john.doe@example.com) needs to update slides by 2025-05-10. Jane (jane.smith@example.com) will schedule follow-up (no date yet)."

try:
    # Mirascope handles instructing the LLM, parsing the response, running Pydantic validation, and retrying if needed.
    result: StructuredMeetingSummary = get_structured_summary(meeting_notes=notes, reasoning=True)

    # 5. Reliable Integration: Access data via attributes
    print("Summary:", result.summary)
    for item in result.action_items:
        # Pydantic already validated assignee_email format and due_date format!
        print(f"- Task: {item.task}, Assignee: {item.assignee_email}, Due: {item.due_date or 'N/A'}")

    if result.reasoning:
        print("\nReasoning:", result.reasoning) # CoT easily accessible if requested

except Exception as e:
    # Handles errors after retries (e.g., final validation failure)
    print(f"Error getting structured summary: {e}")

# 6. Parsing Flexibility: Mirascope abstracts whether it used OpenAI's JSON mode,
#    tool calling, or other techniques to get the structured data. You can often
#    change underlying settings without altering this core logic.

```

**Why this is better:**

* **Reliable Integration:** Your application code interacts with a predictable Python object (`StructuredMeetingSummary`), not fragile text. Access data cleanly (e.g., `result.action_items[0].assignee_email`).
* **Built-in Validation:** Pydantic models let you define validation rules (like `EmailStr` or custom validators) directly on the data schema. Mirascope ensures validation runs *after* successful parsing.
* **Easier Extensibility:** Need Chain-of-Thought? Just add a `reasoning` field to the Pydantic model and adjust the prompt. Downstream code accessing `result.summary` or `result.action_items` remains unchanged.
* **Parsing Flexibility:** Frameworks like Mirascope can leverage the best available method (tool calling, JSON mode) to enforce the structure, often insulating your code from the specifics of *how* the LLM generated it.

**The Takeaway:**

Stop treating LLMs like mere text generators when their output needs to integrate with code. **Design for structured outputs using schemas (like Pydantic models) and tools like Mirascope from the start.** It makes your AI integrations more robust, easier to validate, and simpler to extend.