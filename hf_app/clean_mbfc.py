import json
import os

# Configuration
URLS_FILE = 'found_urls.txt'
JSON_FILE = 'mbfc_data.json'
OUTPUT_URLS_FILE = 'found_urls_cleaned.txt'
OUTPUT_JSON_FILE = 'mbfc_data_cleaned.json'

def is_fact_check_url(url):
    """
    Checks if the URL is a specific fact-check article.
    Target pattern: https://mediabiasfactcheck.com/fact-check-.../
    """
    if not url:
        return False
    # We look for '/fact-check-' specifically in the URL structure
    return '/fact-check-' in url

def clean_txt_file():
    print(f"Processing {URLS_FILE}...")
    
    if not os.path.exists(URLS_FILE):
        print(f"Error: {URLS_FILE} not found.")
        return

    with open(URLS_FILE, 'r', encoding='utf-8') as f:
        urls = f.readlines()

    original_count = len(urls)
    # Filter out lines that contain the fact-check pattern
    cleaned_urls = [url for url in urls if not is_fact_check_url(url)]
    removed_count = original_count - len(cleaned_urls)

    with open(OUTPUT_URLS_FILE, 'w', encoding='utf-8') as f:
        f.writelines(cleaned_urls)

    print(f" -> Removed {removed_count} URLs. Saved to {OUTPUT_URLS_FILE}")

def clean_json_file():
    print(f"Processing {JSON_FILE}...")

    if not os.path.exists(JSON_FILE):
        print(f"Error: {JSON_FILE} not found.")
        return

    try:
        with open(JSON_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError:
        print("Error: Failed to decode JSON. Please check the file format.")
        return

    original_count = len(data)
    cleaned_data = []

    for entry in data:
        # We strictly check only the 'mbfc_url' key
        url_to_check = entry.get('mbfc_url', '')
        
        if is_fact_check_url(url_to_check):
            # Skip this entry (delete it)
            continue
        
        # Keep this entry
        cleaned_data.append(entry)

    removed_count = original_count - len(cleaned_data)

    with open(OUTPUT_JSON_FILE, 'w', encoding='utf-8') as f:
        json.dump(cleaned_data, f, indent=4, ensure_ascii=False)

    print(f" -> Removed {removed_count} entries. Saved to {OUTPUT_JSON_FILE}")

if __name__ == "__main__":
    clean_txt_file()
    print("-" * 30)
    clean_json_file()
    print("-" * 30)
    print("Done. Please verify the '_cleaned' files before replacing your originals.")