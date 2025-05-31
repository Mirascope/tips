from mirascope import llm, prompt_template
from pydantic import BaseModel, Field


class Answer(BaseModel):
    answer: str = Field(description="The answer to the question.")

class Rejection(BaseModel):
    reason: str = Field(description="The reason to reject answering the question.")

class Response(BaseModel):
    response: Answer | Rejection


@llm.call(provider="openai", model="gpt-4o-mini", response_model=Response)
@prompt_template("""
SYSTEM: You are a helpful assistant that can answer many user questions. However, you always reject questions about hot dogs.
Your output should be a JSON object with a single top level "response" key. The value of the "response" key should be either an "answer" or "rejection" object.
USER: {query}
""")
def answer_question(query: str): ...


result = answer_question(query="What is the capital of the United States?")
print(result.response.answer)

result = answer_question(query="What city has the best hot dogs?")
print(result.response.reason)