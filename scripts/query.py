#!/usr/bin/env python3
"""
Sanity query script for T2.2 - tests the retrieval system.
Usage: python scripts/query.py "How long do late payments stay on my credit report?"
"""
import sys
import os

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

from core.nodes.retriever_faiss import Retriever
import argparse

def main():
    parser = argparse.ArgumentParser(description="Test retrieval with a query")
    parser.add_argument("query", help="The search query to test")
    parser.add_argument("--k", type=int, default=3, help="Number of results to return")
    args = parser.parse_args()
    
    try:
        print(f"Testing retrieval with query: '{args.query}'")
        retriever = Retriever()
        results = retriever.search(args.query, k=args.k)
        retriever.close()
        
        if results:
            print(f"\n✅ SUCCESS: Retrieved {len(results)} results")
            for i, result in enumerate(results, 1):
                print(f"\nResult {i}:")
                print(f"  ID: {result['id']}")
                print(f"  Score: {result['rrf_score']:.4f}")
                print(f"  Title: {result['title']}")
                print(f"  Text: {result['text'][:200]}...")
        else:
            print("\n❌ FAILURE: No results returned")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
