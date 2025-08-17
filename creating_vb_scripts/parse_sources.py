import os
import json
from bs4 import BeautifulSoup
import pypdf

# Define base paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFESTS_DIR = os.path.join(BASE_DIR, 'data', 'sources', 'manifests')
SOURCES_DIR = os.path.join(BASE_DIR, 'data', 'sources')
OUTPUT_DIR = os.path.join(BASE_DIR, 'data', 'processed', 'text')

def get_source_filename_from_manifest(manifest_filename):
    """Derives the source filename from the manifest filename."""
    base_name = os.path.splitext(manifest_filename)[0]
    # Handle the one inconsistent name we fixed earlier
    if base_name == 'cfpb_complaints_credit_reporting':
        return f"{base_name}.json"

    # Read the manifest to get file type, though we can often infer it
    with open(os.path.join(MANIFESTS_DIR, manifest_filename), 'r') as f:
        manifest_data = json.load(f)
    file_type = manifest_data.get('type', 'html') # Default to html if not specified

    return f"{base_name}.{file_type}"

def parse_pdf(file_path):
    """Extracts text from a PDF file."""
    text = ""
    try:
        with open(file_path, 'rb') as f:
            reader = pypdf.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() + '\n\n'
        return text
    except Exception as e:
        return f"Error parsing PDF {os.path.basename(file_path)}: {e}"

def parse_html(file_path):
    """Extracts text from an HTML file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'lxml')
            return soup.get_text(separator='\n', strip=True)
    except Exception as e:
        return f"Error parsing HTML {os.path.basename(file_path)}: {e}"

def parse_json(file_path):
    """Formats a JSON file into a readable string."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return json.dumps(data, indent=2)
    except Exception as e:
        return f"Error parsing JSON {os.path.basename(file_path)}: {e}"

def main():
    """Main function to parse all source files based on manifests."""
    print(f"Starting parsing process...")
    print(f"Manifests directory: {MANIFESTS_DIR}")
    print(f"Output directory: {OUTPUT_DIR}")

    manifest_files = [f for f in os.listdir(MANIFESTS_DIR) if f.endswith('.json')]
    print(f"Found {len(manifest_files)} manifests to process.")

    for manifest_file in manifest_files:
        try:
            with open(os.path.join(MANIFESTS_DIR, manifest_file), 'r') as f:
                manifest = json.load(f)
            
            file_type = manifest.get('type')
            source_id = manifest.get('source_id')

            if not file_type or not source_id:
                print(f"[SKIP] Manifest '{manifest_file}' is missing 'type' or 'source_id'.")
                continue

            source_path = os.path.join(SOURCES_DIR, file_type.lower(), source_id)
            output_filename = os.path.splitext(source_id)[0] + '.txt'
            output_path = os.path.join(OUTPUT_DIR, output_filename)

            if not os.path.exists(source_path):
                print(f"[ERROR] Source file not found for manifest '{manifest_file}': {source_path}")
                continue

            print(f"Processing '{source_id}'...")
            content = ""
            if file_type == 'pdf':
                content = parse_pdf(source_path)
            elif file_type == 'html':
                content = parse_html(source_path)
            elif file_type == 'json':
                content = parse_json(source_path)
            else:
                print(f"[WARN] Unsupported file type '{file_type}' for manifest '{manifest_file}'.")
                continue

            with open(output_path, 'w', encoding='utf-8') as f_out:
                f_out.write(content)
            
            print(f"  -> Saved parsed text to '{output_filename}'")

        except json.JSONDecodeError:
            print(f"[ERROR] Could not decode JSON from manifest '{manifest_file}'.")
        except Exception as e:
            print(f"[ERROR] An unexpected error occurred while processing '{manifest_file}': {e}")

    print("\nParsing process complete.")

if __name__ == "__main__":
    main()
