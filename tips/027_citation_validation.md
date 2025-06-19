## Effective AI Engineering #27: Citation Validation

Your AI is making stuff up again. Another user complaint comes through. You let your face fall into your hands. Feeling the forehead wrinkles get deeper.
Wasn't this RAG pipeline supposed to "ground" the AI answers? What now?

LLMs are great at giving answers that pass the eye test, but not the smell test. Answers seem reasonable, but are often wrong.
Put an end to unchecked hallucination.

### The Problem

Many developers request citations without validating their accuracy or relevance. This creates challenges that aren't immediately obvious:

```python
# BEFORE: Simple RAG without citation validation
from mirascope.core import llm

@llm.call(provider="openai", model="gpt-4o-mini")
def answer_question(question: str, documents: list[str]) -> str:
    return f"""
    Answer this question using the provided documents: {question}
    
    Documents:
    {documents}
    """

# Usage
documents = "Climate Research 2023: Global temperatures increased 1.1°C..."
response = answer_question("What is global temperature change?", documents)
```

**Why this approach falls short:**

- **Fabricated References:** AI generates realistic but non-existent citations that users can't verify
- **Misattributed Claims:** Real sources get cited for information they don't actually contain
- **Broken Trust:** Users lose confidence when they discover inaccurate citations

### The Solution: Citation Verification Pipeline

A better approach is to validate citations against provided sources and verify their relevance to claims. This pattern ensures citations are both real and accurately support the generated content.

```python
# AFTER: Citation validation pipeline
from mirascope.core import llm
from pydantic import BaseModel
from typing import List, Dict

class Citation(BaseModel):
    source_title: str
    claim: str

class CitedResponse(BaseModel):
    answer: str
    citations: List[Citation]

@llm.call(provider="openai", model="gpt-4o-mini", response_model=bool)
def validate_citation(claim: str, source_content: str) -> bool:
    return f"""
    Does this source content support the claim?
    
    Claim: "{claim}"
    Source: "{source_content}"
    
    Return true if the source supports the claim, false otherwise.
    """

@llm.call(provider="openai", model="gpt-4o-mini", response_model=CitedResponse)
def generate_cited_response(question: str, documents: list[str]) -> CitedResponse:
    return f"""
    Answer this question with citations: {question}
    
    Documents:
    {documents}
    
    Include citations for all claims.
    """

def answer_with_validated_citations(question: str, documents: Dict[str, str]) -> str:
    docs = [f"# {k}\n{v}" for k, v in documents.items()]
    # Generate response with citations
    response = generate_cited_response(question, docs)
    
    # Validate each citation
    valid_citations = []
    for citation in response.citations:
        if citation.source_title in documents:
            source_content = documents[citation.source_title]
            is_valid = validate_citation(citation.claim, source_content)
            if is_valid:
                valid_citations.append(citation)
    
    # Return answer with only validated citations
    if valid_citations:
        citations_text = "\n".join([f"- {c.claim} [Source: {c.source_title}]" 
                                   for c in valid_citations])
        return f"{response.answer}\n\nValidated Citations:\n{citations_text}"
    else:
        return f"{response.answer}\n\nNote: No citations could be validated."

# Usage
documents = {
    "Climate Report 2023": "Global temperatures increased 1.1°C since pre-industrial times...",
    "Energy Analysis": "Renewable sources account for 30% of electricity generation..."
}

result = answer_with_validated_citations(
    "What percentage of electricity comes from renewables?", 
    documents
)
```

**Why this approach works better:**

- **Citation Accuracy:** Each citation is validated against actual source content to prevent fabrication
- **Relevance Scoring:** Claims are matched to supporting text with confidence scores
- **Trust Building:** Users can verify citations knowing they've been pre-validated for accuracy

### The Takeaway

Citation validation prevents hallucinated references and ensures claims are properly supported by source material. This pattern builds user trust by guaranteeing that citations are both real and relevant.

---
*Part of the "Effective AI Engineering" series - practical tips for building better applications with AI components.*