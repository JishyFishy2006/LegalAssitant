import os
import json
import sqlite3
import numpy as np
import faiss
import pickle
from ollama import embed
from rank_bm25 import BM25Okapi

# --- Configuration ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
DATA_DIR = os.path.join(BASE_DIR, 'data')
RECORDS_FILE = os.path.join(DATA_DIR, 'processed', 'records.jsonl')
INDEX_DIR = os.path.join(DATA_DIR, 'index')
FAISS_INDEX_FILE = os.path.join(INDEX_DIR, 'faiss.index')
SQLITE_DB_FILE = os.path.join(INDEX_DIR, 'meta.sqlite')
BM25_INDEX_FILE = os.path.join(INDEX_DIR, 'bm25.pkl')
EMBEDDING_MODEL = 'nomic-embed-text'
# Nomic-embed-text has a dimension of 768
EMBEDDING_DIMENSION = 768

# --- Database Setup ---
def setup_database():
    """Creates and sets up the SQLite database and table."""
    if os.path.exists(SQLITE_DB_FILE):
        os.remove(SQLITE_DB_FILE)
    conn = sqlite3.connect(SQLITE_DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE metadata (
            id TEXT PRIMARY KEY,
            source_id TEXT,
            doc_id TEXT,
            source_url TEXT,
            title TEXT,
            text TEXT
        )
    ''')
    conn.commit()
    return conn

# --- Main Indexing Logic ---
def build_index():
    """Builds the FAISS index and SQLite metadata database."""
    print("Starting index build process...")
    if not os.path.exists(RECORDS_FILE):
        print(f"[ERROR] Records file not found at: {RECORDS_FILE}")
        return

    conn = setup_database()
    cursor = conn.cursor()
    index = faiss.IndexFlatL2(EMBEDDING_DIMENSION)
    
    records_to_process = []
    with open(RECORDS_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            records_to_process.append(json.loads(line))

    if not records_to_process:
        print("[WARN] No records found to index.")
        conn.close()
        return

    print(f"Found {len(records_to_process)} records to process. Generating embeddings...")
    
    try:
        all_embeddings = []
        metadata_to_store = []
        for i, record in enumerate(records_to_process):
            # Generate embedding for the text
            response = embed(model=EMBEDDING_MODEL, input=record['text'])
            # The embedding vector is the first element of the 'embeddings' list
            all_embeddings.append(response.embeddings[0])
            
            # Prepare metadata for storage
            metadata_to_store.append((
                record['id'],
                record.get('source_id'),
                record['doc_id'],
                record.get('source_url'),
                record.get('title'),
                record['text']
            ))
            print(f"  - Embedded record {i+1}/{len(records_to_process)}", end='\r')

        print("\nEmbedding generation complete.")

        # Add embeddings to FAISS and metadata to SQLite
        embeddings_np = np.array(all_embeddings, dtype='float32')
        index.add(embeddings_np)
        cursor.executemany('INSERT INTO metadata VALUES (?, ?, ?, ?, ?, ?)', metadata_to_store)
        conn.commit()

        print(f"Successfully stored {index.ntotal} embeddings and metadata records.")

    except Exception as e:
        print(f"\n[ERROR] Failed during embedding or storage: {e}")
        conn.close()
        return

    # Save the FAISS index
    faiss.write_index(index, FAISS_INDEX_FILE)
    print(f"FAISS index saved to: {FAISS_INDEX_FILE}")

    # Build and save the BM25 index
    print("Building and saving BM25 index...")
    tokenized_corpus = [record['text'].lower().split(" ") for record in records_to_process]
    bm25 = BM25Okapi(tokenized_corpus)
    with open(BM25_INDEX_FILE, 'wb') as f_out:
        pickle.dump(bm25, f_out)
    print(f"BM25 index saved to: {BM25_INDEX_FILE}")

    conn.close()
    print("Index build process complete.")

if __name__ == "__main__":
    build_index()
