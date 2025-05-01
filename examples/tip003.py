from mirascope import llm, prompt_template
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime


SUMMARY_PROMPT = """
SYSTEM: You are an expert in summarizing meetings.

USER: Please summarize the following meeting notes and extract action items: {meeting_notes}
"""

# 1. Define the desired output structure WITH validation
class ActionItem(BaseModel):
    task: str = Field(..., description="The specific action item description.")
    assignee_email: EmailStr = Field(..., description="The email address of the assignee.")
    due_date: datetime | None = Field(None, description="Optional due date (YYYY-MM-DD).")


class StructuredMeetingSummary(BaseModel):
    reasoning: str | None = Field(None, description="Step-by-step thinking process.")
    summary: str = Field(description="A concise summary of the meeting.")
    action_items: list[ActionItem] = Field(description="A list of all action items.")

# The structured function with enforced output format
@llm.call(provider="openai", model="gpt-4o-mini", response_model=StructuredMeetingSummary)
@prompt_template(SUMMARY_PROMPT)
def get_structured_summary(meeting_notes: str): ...

notes = "Project is overall on track. skylar@gmail.com needs to email requirements to Jeff for review."
# Usage is now simple and reliable
result = get_structured_summary(meeting_notes=notes)
print(f"Task: {result.action_items[0].task}, Assignee: {result.action_items[0].assignee_email}")