## Effective AI Engineering #8: Create Semantically Focused Chunks for RAG

**Are you getting poor relevance from your RAG system?** Your chunking strategy could be sabotaging your retrieval quality, even with the best embeddings and models.

Raw documents, especially long ones, often make terrible retrieval units. When chunks are too large, too small, or arbitrarily split, your RAG system struggles to find the right information. This directly impacts answer quality and user experience.

### The Problem

Many developers implement RAG using simplistic chunking approaches that prioritize convenience over quality:

```python
# BEFORE: Naive Fixed-Size Chunking
documents = load_documents("knowledge_base/")
chunks = []

for doc in documents:
    # Arbitrary splitting every 1000 characters
    text = doc.text
    for i in range(0, len(text), 1000):
        chunks.append(text[i:i+1000])

# Index these fixed-size chunks
index_chunks(chunks)
```

**Example of chunking failure:**

Consider a user query: "What were food conditions like after World War 2?"

With naive chunking, you might get a chunk containing: "In 1946, food was scarce across Europe. Rationing continued for several years..."

This relevant chunk might not be retrieved because:
1. The chunk doesn't explicitly mention "World War 2" - only "1946"
2. The temporal relationship between 1946 and World War 2 is lost
3. Embedding-based similarity might not recognize this connection

**Why this approach falls short:**

- **Diluted Relevance:** Long chunks contain multiple topics, making it hard for retrievers to match user queries with the specific relevant sections.
- **Context Fragmentation:** Fixed-size splitting often cuts mid-sentence or breaks logical units, destroying semantic coherence and context.
- **Lost Information:** When chunks are too small, the answer to a question might be split across multiple fragments that aren't retrieved together.
- **Wasted Context Budget:** Large, undifferentiated chunks waste valuable context window space with irrelevant information.
- **Low Information Chunks:** Naive splitting often produces useless chunks with navigation elements, whitespace, or partial information.
- **Semantic Gaps:** Without additional context, chunks may fail to match conceptually related queries (like years vs. event names).

### The Solution: Semantic-Aware Chunking

A better approach is to create cohesive, topic-focused chunks that respect natural document boundaries. This ensures each retrieval unit contains complete, self-contained information.

```python
# AFTER: Document-Aware Chunking with Metadata for Multiple Documents
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from mirascope import llm, prompt_template

class Document(BaseModel):
    content: str
    doc_id: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

class EnrichedChunk(BaseModel):
    content: str
    doc_id: str
    document_summary: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

# Generate questions that a chunk would be relevant for answering
@llm.call(provider="openai", model="gpt-4o-mini")
@prompt_template("Generate questions that the following text would be relevant to answer:\n{chunk_content}")
def generate_questions_for_chunk(chunk_content: str): ...

# Generate a summary for the whole document
@llm.call(provider='openai', model='gpt-4o-mini')
@prompt_template("Summarize the following document:\n{document}")
def summarize_document(document: str): ...

def process_documents(documents: List[Document]) -> List[EnrichedChunk]:
    # Configure the text splitter once
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "\n", ". ", ", ", " ", ""],  # Prioritize natural breaks
    )

    summaries = [summarize_document(doc) for doc in documents]
    return [
        EnrichedChunk(
            content=chunk,
            doc_id=doc.doc_id,
            document_summary=summary,
            metadata={
                "source_id": doc.doc_id,
                "chunk_index": i,
                "hypothetical_questions": generate_questions_for_chunk(chunk)
            }
        )
        for doc, summary in zip(documents, summaries)
        for i, chunk in enumerate(text_splitter.split_text(doc.content))
]
    
```

**Why this approach works better:**

- **Improved Relevance:** Chunks align with semantic boundaries, preserving logical units of information that better match user queries.
- **Context Preservation:** Natural splitting respects document structure, keeping related information together.
- **Enhanced Retrieval:** Metadata like document summaries and hypothetical questions bridges the vocabulary gap between queries and documents.
- **Context Efficiency:** Including document-level summaries in each chunk provides broader context without repeating the entire document.
- **Cross-Document Understanding:** Processing multiple documents allows the system to recognize related information across different sources.
- **Better RAG Performance:** Semantic chunking with document context directly improves answer quality by ensuring retrievers can find complete, focused information with appropriate document-level context.

### The Takeaway

Effective RAG requires semantically meaningful chunks, not arbitrary text fragments. By implementing document-aware chunking strategies and enriching chunks with metadata, you'll dramatically improve retrieval quality and maximize the value of your knowledge base.

---
*Part of the "Effective AI Engineering" series - practical tips for building better applications with AI components.*