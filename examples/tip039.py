#!/usr/bin/env python3
"""
Example for Tip 039: Query Rewriting for RAG

This example demonstrates how to improve RAG retrieval by rewriting queries
before embedding search using simple functions.
"""

from mirascope import llm, prompt_template
import numpy as np

@llm.call(provider='openai', model='gpt-4o-mini')
@prompt_template("""
Rewrite this user query to improve document retrieval: {original_query}

Generate 3 alternative search queries that use specific technical terms likely to appear in documentation.
Return as a comma-separated list.
""")
def rewrite_query(original_query: str) -> str: ...

def get_embedding(text: str):
    # Mock embedding generation for demonstration
    return np.random.rand(384)

def search_documents_with_rewriting(query: str, documents: list[str], embeddings: list) -> dict:
    # Rewrite query first
    rewritten_queries_str = rewrite_query(query)
    rewritten_queries = [q.strip() for q in rewritten_queries_str.split(',')]
    
    print(f"Original query: {query}")
    print(f"Rewritten queries: {rewritten_queries}")
    
    # In a real implementation, you would:
    # 1. Generate embeddings for rewritten queries
    # 2. Search against document embeddings
    # 3. Return most relevant documents
    
    # For demo, return mock relevant documents
    mock_results = [
        "Database query optimization techniques",
        "Network latency troubleshooting guide", 
        "Application performance monitoring best practices"
    ]
    
    return {
        "original_query": query,
        "rewritten_queries": rewritten_queries,
        "retrieved_documents": mock_results
    }

def main():
    print("=== Query Rewriting for RAG Example ===\n")
    
    # Test queries that would benefit from rewriting
    test_queries = [
        "My app is really slow, what should I do?",
        "Users are complaining about response times",
        "How to make my website faster?"
    ]
    
    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"Testing query: {query}")
        print('='*60)
        
        result = search_documents_with_rewriting(query, [], [])
        
        print(f"\nRetrieved documents:")
        for i, doc in enumerate(result["retrieved_documents"], 1):
            print(f"{i}. {doc}")
        
        print("\n" + "-"*60)

if __name__ == "__main__":
    main()