Okay, creating Tip #8 on effective chunking strategies makes perfect sense after introducing simple RAG in Tip #5 and discussing retrieval evaluation in Tip #6. Bad chunking is often a root cause of poor retrieval performance.

---

**Tip #8: Better RAG - Create Semantically Focused Chunks**

**Subject: Effective AI #8: Garbage In, Garbage Out - Effective Chunking for RAG**

Hey team,

In Tip #5, we introduced RAG using whole documents for simplicity. While that's a good starting point, feeding entire documents (especially long ones) directly into a retriever often leads to suboptimal results. Why? Because **retrieval works best when the indexed units are focused.** This is where effective **chunking** comes in.

**The Problem with Whole Documents (or Bad Chunks):**

* **Diluted Relevance:** A long document might contain many different topics. If only one small section answers the user's query, keyword (BM25) or semantic (embedding) searches might struggle to identify that specific section if the rest of the document discusses unrelated things. The overall document might not seem highly relevant, even if a small part is perfect.
* **Context Window Limits:** Retrieving multiple long documents can easily exceed the LLM's context window limit.
* **"Lost in the Middle":** Even if documents fit, LLMs sometimes struggle to effectively use information buried deep within long contexts.
* **Too Small / Fragmented:** Conversely, chopping documents arbitrarily into tiny pieces (e.g., single sentences) might mean that no single chunk contains enough surrounding context for the LLM to understand it properly, or the answer might be split across multiple chunks that aren't retrieved together.
* **Low Information Chunks:** Naive splitting can also produce useless chunks (e.g., just whitespace, navigation menus, or page numbers).

**The Goal: Semantically Focused Chunks**

Ideally, each chunk you index should represent a reasonably self-contained unit of meaning – a specific topic, a paragraph answering a particular question, a distinct section. This allows the retriever to pinpoint relevant information much more accurately.

**Chunking Strategies (Moving Beyond Fixed Size):**

* **Fixed-Size Splitting:** The simplest method (e.g., every 500 characters). Easy but often breaks sentences/ideas mid-stream, leading to poor semantic coherence. Use with caution, maybe with significant overlap.
* **Recursive Character Splitting:** A common and often better approach. It tries to split based on a priority list of separators (e.g., `\n\n` for paragraphs, then `\n` for lines, then spaces). This respects document structure more effectively.
* **Document-Aware Splitting:** Consider the *type* of document. Splitting code, markdown tables, or structured text requires different logic than splitting prose paragraphs. Use specialized splitters where appropriate.
* **Semantic Chunking (Advanced):** Techniques that group sentences based on semantic similarity (using embeddings) to create chunks that are topically coherent, even if their lengths vary.

**Improving Query-Chunk Matching with Metadata:**

Sometimes, even well-chunked document text doesn't use the same "language" as a user's query. You can improve matching by enriching your chunks with **metadata** during indexing:

* **Summaries:** Add a brief summary sentence to each chunk's metadata.
* **Hypothetical Questions:** Generate potential questions that the chunk answers and add them to the metadata.
* **Keywords/Topics:** Add relevant keywords or topic tags.

Your retriever can then search over both the chunk content *and* this metadata, increasing the chances of finding the right chunk even if the query phrasing differs.

**Example (Conceptual Chunking and Adding Metadata):**

This example uses `langchain_text_splitters` conceptually for illustration, as it provides common splitter types. The focus is on the *pattern* of splitting and adding metadata.

```python
import os
from pydantic import BaseModel, Field
from typing import List, Dict, Any

# Assume necessary libraries are installed:
# pip install langchain-text-splitters pydantic python-dotenv
# (No direct Mirascope/Lilypad usage in this preprocessing step)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from dotenv import load_dotenv

# Load environment variables if needed elsewhere
load_dotenv()

# --- Define a Chunk Structure with Metadata ---
class Chunk(BaseModel):
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    # Example metadata fields: source_doc_id, chunk_index, summary, questions

# --- Sample Document ---
sample_document = """
Project Phoenix: User Interface Overhaul

**Goals:**
The primary goal of Project Phoenix is to modernize the application's user interface (UI), focusing on improved usability and performance. We aim for a page load time under 500ms.

**Technology Stack:**
The frontend will be built using React and TypeScript. Backend dependencies will be minimized. State management will rely on Zustand.

**Timeline:**
- Q1: Design mockups finalization.
- Q2: Core component development.
- Q3: Integration and testing.
- Q4: Launch.

**Contact:** For UI/UX questions, contact Design Lead (design@example.com). For technical implementation, reach out to Frontend Lead (frontend@example.com).
"""
doc_id = "project_phoenix_brief.txt"

# --- Chunking Logic ---
def create_chunks_with_metadata(document_text: str, source_id: str) -> List[Chunk]:
    """Chunks document using RecursiveCharacterTextSplitter and adds basic metadata."""
    print(f"Chunking document: {source_id}")

    # Using RecursiveCharacterTextSplitter for better structure awareness
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=300, # Target size (adjust based on testing)
        chunk_overlap=30, # Overlap helps maintain context between chunks
        separators=["\n\n", "\n", ". ", ", ", " ", ""], # Prioritize splitting on paragraphs/lines
        length_function=len,
    )

    split_texts = text_splitter.split_text(document_text)
    print(f"Split into {len(split_texts)} raw chunks.")

    chunks = []
    for i, text in enumerate(split_texts):
        metadata = {
            "source_doc_id": source_id,
            "chunk_index": i,
            # Add more metadata here (e.g., using an LLM to generate summary/questions)
            "hypothetical_question": f"What part of {source_id} discusses '{text[:30]}...'?",
            "keywords": ["project phoenix", "ui", "react"] # Example static keywords
        }
        chunks.append(Chunk(content=text, metadata=metadata))

    print(f"Created {len(chunks)} Chunk objects with metadata.")
    return chunks

# --- Usage ---
created_chunks = create_chunks_with_metadata(sample_document, doc_id)

# Show an example chunk with metadata
if created_chunks:
    print("\nExample Chunk 0:")
    print(f"  Content: {created_chunks[0].content[:100]}...") # Show start of content
    print(f"  Metadata: {created_chunks[0].metadata}")

# --- Next Steps ---
# These `created_chunks` (content + metadata) would then be indexed in your
# retrieval system (e.g., BM25 index, vector database). Your retrieval function
# (like in Tip #6) would query this index, potentially searching both content
# and metadata fields, before passing the *content* of the retrieved chunks
# to your Mirascope RAG prompt (Tip #5).

```

**The Takeaway:**

Effective chunking is non-negotiable for high-quality RAG. Moving beyond naive fixed-size splitting to **methods that respect semantic boundaries (like recursive splitting)** is crucial. Aim for chunks that are focused yet contain enough context. Furthermore, **enriching chunks with metadata** (summaries, hypothetical questions, keywords) can significantly bridge the gap between user query language and document language, leading to better retrieval relevance. Experiment and evaluate (Tip #6) to find the best strategy for your data!