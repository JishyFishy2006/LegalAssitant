import os
import json

# Define base paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFESTS_DIR = os.path.join(BASE_DIR, 'data', 'sources', 'manifests')

def fix_manifests():
    """Iterates through all manifests and corrects the source_id field."""
    print("Starting manifest correction process...")
    manifest_files = [f for f in os.listdir(MANIFESTS_DIR) if f.endswith('.json')]
    
    corrected_count = 0
    for manifest_file in manifest_files:
        file_path = os.path.join(MANIFESTS_DIR, manifest_file)
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)

            source_id = data.get('source_id')
            file_type = data.get('type')

            if not source_id or not file_type:
                print(f"[SKIP] '{manifest_file}' is missing 'source_id' or 'type'.")
                continue

            # Check if the extension is missing
            if not source_id.endswith(f'.{file_type}'):
                original_id = source_id
                new_id = f"{source_id}.{file_type}"
                data['source_id'] = new_id

                # Write the corrected data back to the file
                with open(file_path, 'w') as f:
                    json.dump(data, f, indent=4)
                
                print(f"[FIXED] '{manifest_file}': Changed source_id from '{original_id}' to '{new_id}'.")
                corrected_count += 1

        except json.JSONDecodeError:
            print(f"[ERROR] Could not decode JSON from '{manifest_file}'.")
        except Exception as e:
            print(f"[ERROR] An unexpected error occurred with '{manifest_file}': {e}")

    print(f"\nManifest correction complete. {corrected_count} file(s) were updated.")

if __name__ == "__main__":
    fix_manifests()
