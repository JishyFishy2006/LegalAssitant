import os
import sqlite3
import numpy as np
import faiss
import argparse
import pickle
from dotenv import load_dotenv

# Add project root to Python path for imports
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import sys
sys.path.append(project_root)

from src.core.llm.ollama_client import OllamaClient

# --- Configuration ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
DATA_DIR = os.path.join(BASE_DIR, 'data')
INDEX_DIR = os.path.join(DATA_DIR, 'index')
FAISS_INDEX_FILE = os.path.join(INDEX_DIR, 'faiss.index')
SQLITE_DB_FILE = os.path.join(INDEX_DIR, 'meta.sqlite')
BM25_INDEX_FILE = os.path.join(INDEX_DIR, 'bm25.pkl')
EMBEDDING_MODEL = 'nomic-embed-text'

class Retriever:
    def __init__(self):
        """Initializes the Retriever, loading all indexes and databases."""
        print("Loading all indexes...")
        if not all(os.path.exists(f) for f in [FAISS_INDEX_FILE, SQLITE_DB_FILE, BM25_INDEX_FILE]):
            raise FileNotFoundError("One or more index files not found. Please run build_index.py")

        self.faiss_index = faiss.read_index(FAISS_INDEX_FILE)
        with open(BM25_INDEX_FILE, 'rb') as f:
            self.bm25_index = pickle.load(f)
        self.db_conn = sqlite3.connect(SQLITE_DB_FILE)

        cursor = self.db_conn.cursor()
        cursor.execute("SELECT id FROM metadata ORDER BY rowid")
        self.idx_to_id = [row[0] for row in cursor.fetchall()]
        self.id_to_idx = {id_: i for i, id_ in enumerate(self.idx_to_id)}
        
        # Initialize Ollama client for embeddings
        self.ollama_client = OllamaClient()

    def embed_query(self, query: str) -> np.ndarray:
        """Generate embeddings for the query using the modernized OllamaClient."""
        embeddings = self.ollama_client.embed(query, model=EMBEDDING_MODEL)
        return np.array(embeddings, dtype='float32')

    def search(self, query: str, k: int = 5, filter_source_id: str = None, k_semantic: int = 10, k_keyword: int = 10, similarity_threshold: float = 0.0, rrf_beta: float = 0.7) -> list[dict]:
        """Retrieves the top k most relevant documents using a hybrid approach."""
        print(f"\nRetrieving top {k} results for query: '{query}'")
        if filter_source_id:
            print(f"Filtering by source_id: '{filter_source_id}'")

        # 1. Semantic Search (FAISS)
        query_embedding = np.array([self.embed_query(query)], dtype='float32')
        distances, indices = self.faiss_index.search(query_embedding, k_semantic)
        
        semantic_results = []
        for i, idx in enumerate(indices[0]):
            if idx != -1:
                similarity = 1 - (distances[0][i]**2 / 2) # Cosine similarity from L2
                if similarity >= similarity_threshold:
                    semantic_results.append({'id': self.idx_to_id[idx], 'score': similarity})

        # 2. Keyword Search (BM25)
        tokenized_query = query.lower().split(" ")
        bm25_scores = self.bm25_index.get_scores(tokenized_query)
        top_n_indices = np.argsort(bm25_scores)[::-1][:k_keyword]
        keyword_results = [{'id': self.idx_to_id[i], 'score': bm25_scores[i]} for i in top_n_indices if bm25_scores[i] > 0]

        # 3. Metadata Filtering (if applicable)
        allowed_ids = None
        if filter_source_id:
            cursor = self.db_conn.cursor()
            cursor.execute("SELECT id FROM metadata WHERE source_id = ?", (filter_source_id,))
            allowed_ids = {row[0] for row in cursor.fetchall()}

        # 4. Reciprocal Rank Fusion (RRF)
        rrf_scores = {}
        k_rrf = 60  # RRF constant

        # Process semantic results with beta weight
        for rank, res in enumerate(semantic_results):
            if allowed_ids is None or res['id'] in allowed_ids:
                rrf_scores[res['id']] = rrf_scores.get(res['id'], 0) + rrf_beta * (1 / (k_rrf + rank + 1))

        # Process keyword results with (1 - beta) weight
        for rank, res in enumerate(keyword_results):
            if allowed_ids is None or res['id'] in allowed_ids:
                rrf_scores[res['id']] = rrf_scores.get(res['id'], 0) + (1 - rrf_beta) * (1 / (k_rrf + rank + 1))

        # Sort by RRF score
        sorted_results = sorted(rrf_scores.items(), key=lambda item: item[1], reverse=True)

        # 5. Fetch metadata for top k results
        final_results = []
        cursor = self.db_conn.cursor()
        for doc_id, score in sorted_results[:k]:
            cursor.execute("SELECT title, text, source_url FROM metadata WHERE id = ?", (doc_id,))
            row = cursor.fetchone()
            if row:
                final_results.append({
                    'id': doc_id,
                    'rrf_score': score,
                    'title': row[0],
                    'text': row[1],
                    'source_url': row[2]
                })
        return final_results

    def close(self):
        self.db_conn.close()

def main():
    load_dotenv() # Load environment variables from .env file

    parser = argparse.ArgumentParser(description="Retrieve relevant documents for a query.")
    parser.add_argument("query", help="The search query.")
    parser.add_argument("--k", type=int, default=5, help="The number of final results to return.")
    parser.add_argument("--filter_source", type=str, default=None, help="A source_id to filter the results by.")
    parser.add_argument("--k_semantic", type=int, default=int(os.getenv("K_SEMANTIC", 10)), help="Number of candidates from semantic search.")
    parser.add_argument("--k_keyword", type=int, default=int(os.getenv("K_KEYWORD", 10)), help="Number of candidates from keyword search.")
    parser.add_argument("--similarity_threshold", type=float, default=float(os.getenv("SIMILARITY_THRESHOLD", 0.0)), help="Semantic similarity cutoff (0.0 to 1.0).")
    parser.add_argument("--rrf_beta", type=float, default=float(os.getenv("RRF_BETA", 0.7)), help="Weight for semantic search in RRF (0.0 to 1.0).")
    args = parser.parse_args()


    try:
        retriever = Retriever()
        results = retriever.search(
            args.query, 
            k=args.k, 
            filter_source_id=args.filter_source,
            k_semantic=args.k_semantic,
            k_keyword=args.k_keyword,
            similarity_threshold=args.similarity_threshold,
            rrf_beta=args.rrf_beta
        )
        retriever.close()
        
        print("\n--- Hybrid Retrieval Results ---")
        if not results:
            print("No results found.")
        else:
            for i, res in enumerate(results):
                print(f"\nResult {i+1}:")
                print(f"  RRF Score: {res['rrf_score']:.4f}")
                print(f"  ID: {res['id']}")
                print(f"  Title: {res['title']}")
                print(f"  Source: {res['source_url']}")
                print(f"  Text: {res['text'][:400]}...")
        print("------------------------------")

    except FileNotFoundError as e:
        print(f"[ERROR] {e}")
    except Exception as e:
        print(f"[ERROR] An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
