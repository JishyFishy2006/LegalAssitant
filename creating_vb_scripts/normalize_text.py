import os
import json
import re

# Define base paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFESTS_DIR = os.path.join(BASE_DIR, 'data', 'sources', 'manifests')
PARSED_TEXT_DIR = os.path.join(BASE_DIR, 'data', 'processed', 'text')
OUTPUT_FILE = os.path.join(BASE_DIR, 'data', 'processed', 'records.jsonl')

def chunk_text(text):
    """A simple text chunking strategy. Splits by paragraphs."""
    # Split by double newline, which typically separates paragraphs
    paragraphs = text.split('\n\n')
    # Filter out any empty strings or paragraphs with only whitespace
    chunks = [p.strip() for p in paragraphs if p.strip()]
    return chunks

def main():
    """Main function to normalize parsed text into structured records."""
    print("Starting normalization process...")
    
    # Ensure the output file is cleared before writing
    if os.path.exists(OUTPUT_FILE):
        os.remove(OUTPUT_FILE)

    manifest_files = [f for f in os.listdir(MANIFESTS_DIR) if f.endswith('.json')]
    print(f"Found {len(manifest_files)} manifests to process.")

    total_records = 0
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f_out:
        for manifest_file in manifest_files:
            try:
                manifest_path = os.path.join(MANIFESTS_DIR, manifest_file)
                with open(manifest_path, 'r') as f:
                    manifest = json.load(f)

                source_id = manifest.get('source_id')
                if not source_id:
                    print(f"[SKIP] Manifest '{manifest_file}' is missing 'source_id'.")
                    continue

                doc_id = os.path.splitext(source_id)[0]
                parsed_text_filename = f"{doc_id}.txt"
                parsed_text_path = os.path.join(PARSED_TEXT_DIR, parsed_text_filename)

                if not os.path.exists(parsed_text_path):
                    print(f"[WARN] Parsed text file not found for manifest '{manifest_file}'. Skipping.")
                    continue
                
                print(f"Processing '{parsed_text_filename}'...")
                with open(parsed_text_path, 'r', encoding='utf-8') as f_text:
                    text_content = f_text.read()
                
                chunks = chunk_text(text_content)
                
                for i, chunk in enumerate(chunks):
                    record = {
                        'id': f"{doc_id}#chunk{i:04d}",
                        'doc_id': doc_id,
                        'source_id': source_id, # Add the source_id here
                        'source_url': manifest.get('url'),
                        'title': manifest.get('title'),
                        'agency': manifest.get('agency'),
                        'published_date': manifest.get('date'),
                        'tags': manifest.get('tags', []),
                        'text': chunk
                    }
                    f_out.write(json.dumps(record) + '\n')
                
                total_records += len(chunks)
                print(f"  -> Created {len(chunks)} records.")

            except Exception as e:
                print(f"[ERROR] An unexpected error occurred while processing '{manifest_file}': {e}")

    print(f"\nNormalization complete. Total records created: {total_records}")
    print(f"Output saved to: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
