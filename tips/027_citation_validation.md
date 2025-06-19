## Effective AI Engineering #27: Citation Validation

**Is your AI making up sources that don't exist?** Users trust responses with citations, but when they click that link to "Scientific Study #347" they find a 404 error and lose faith in your entire system.

LLMs excel at generating plausible-sounding references that match the tone and format of real citations. This makes hallucinated sources particularly dangerous - they look legitimate until someone tries to verify them.

### The Problem

Many developers request citations without validating their accuracy or relevance. This creates challenges that aren't immediately obvious:

```python
# BEFORE: No citation validation
from mirascope.core import llm
from pydantic import BaseModel
from typing import List

class CitedResponse(BaseModel):
    answer: str
    citations: List[str]

@llm.call(provider="openai", model="gpt-4o-mini", response_model=CitedResponse)
def answer(question: str, documents: str) -> CitedResponse:
    return f"""
    Answer this question using the provided documents: {question}
    
    Documents:
    {documents}
    
    Include citations for all claims using format [Source: document_title]
    """
```

**Why this approach falls short:**

- **Fabricated References:** AI generates realistic but non-existent citations that users can't verify
- **Misattributed Claims:** Real sources get cited for information they don't actually contain
- **Broken Trust:** Users lose confidence when they discover inaccurate citations

### The Solution: Citation Verification Pipeline

A better approach is to validate citations against provided sources and verify their relevance to claims. This pattern ensures citations are both real and accurately support the generated content.

```python
# AFTER: Validated citation system
from mirascope.core import llm
from pydantic import BaseModel
import lilypad
from typing import List, Dict, Optional
from dataclasses import dataclass

@dataclass
class Document:
    title: str
    content: str
    url: Optional[str] = None

class Citation(BaseModel):
    source_title: str
    claim: str
    page_reference: Optional[str] = None

class ValidatedCitation(BaseModel):
    citation: Citation
    is_valid: bool
    supporting_text: str

class CitedResponse(BaseModel):
    answer: str
    citations: List[Citation]

@lilypad.trace()
@llm.call(provider="openai", model="gpt-4o-mini", response_model=ValidatedCitation)
def validate_citation(claim: str, source_title: str, source_content: str) -> ValidatedCitation:
    return f"""
    Validate this citation against the source document:
    
    Claim: "{claim}"
    Cited Source: "{source_title}"
    
    Source Content: "{source_content}"
    
    Check if:
    1. The source actually supports this claim
    2. The information is accurately represented
    3. The claim isn't misattributed
    
    Provide the specific text that supports (or contradicts) the claim.
    """

@lilypad.trace()
def verify_all_citations(response: CitedResponse, documents: Dict[str, Document]) -> List[ValidatedCitation]:
    validated_citations = []
    
    for citation in response.citations:
        # Find the referenced document
        if citation.source_title in documents:
            doc = documents[citation.source_title]
            validation = validate_citation(
                citation.claim,
                citation.source_title,
                doc.content
            )
            validated_citations.append(validation)
        else:
            # Citation references non-existent document
            fake_validation = ValidatedCitation(
                citation=citation,
                is_valid=False,
                supporting_text="Source document not found"
            )
            validated_citations.append(fake_validation)
    
    return validated_citations

@lilypad.trace()
@llm.call(provider="openai", model="gpt-4o-mini", response_model=CitedResponse)
def generate_cited_response(question: str, document_list: str, documents: str) -> CitedResponse:
    return f"""
    Answer this question using ONLY the provided documents: {question}
    
    Available Documents:
    {document_list}
    
    Document Contents:
    {documents}
    
    Requirements:
    - Only cite sources that are provided above
    - Use exact document titles for citations
    - Format: [Source: exact_document_title]
    - Do not invent or hallucinate sources
    """

@lilypad.trace()
def research_with_verified_citations(question: str, documents: Dict[str, Document]) -> str:
    # Prepare document strings for prompting
    doc_list = "\n".join([f"- {title}" for title in documents.keys()])
    doc_content = "\n\n".join([f"{title}:\n{doc.content}" for title, doc in documents.items()])
    
    # Generate response with citations
    response = generate_cited_response(question, doc_list, doc_content)
    
    # Validate all citations
    validations = verify_all_citations(response, documents)
    
    # Filter out invalid citations
    valid_citations = [v for v in validations if v.is_valid]
    invalid_citations = [v for v in validations if not v.is_valid]
    
    # Log validation results
    if invalid_citations:
        print(f"Removed {len(invalid_citations)} invalid citations:")
        for invalid in invalid_citations:
            print(f"- {invalid.citation.source_title}: {invalid.supporting_text}")
    
    # Reconstruct response with only valid citations
    citation_text = "\n".join([
        f"[{i+1}] {v.citation.source_title}: {v.supporting_text[:100]}..."
        for i, v in enumerate(valid_citations)
    ])
    
    if citation_text:
        return f"{response.answer}\n\nVerified Sources:\n{citation_text}"
    else:
        return f"{response.answer}\n\nNote: No verifiable citations could be confirmed for this response."

# Example usage
documents = {
    "Climate Research 2023": Document(
        "Climate Research 2023",
        "Global temperatures have increased by 1.1°C since pre-industrial times...",
        "https://example.com/climate-2023"
    ),
    "Energy Policy Analysis": Document(
        "Energy Policy Analysis", 
        "Renewable energy sources now account for 30% of global electricity generation...",
        "https://example.com/energy-policy"
    )
}

verified_answer = research_with_verified_citations(
    "What percentage of electricity comes from renewable sources?",
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