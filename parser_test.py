import cloudscraper
from bs4 import BeautifulSoup
import json
import time
import random
import re
import os

# Initialize the scraper (mimics a real Chrome browser)
scraper = cloudscraper.create_scraper(
    browser={
        'browser': 'chrome',
        'platform': 'windows',
        'desktop': True
    }
)

# Configuration
INPUT_FILE = 'test.txt'
OUTPUT_FILE = 'mbfc_data_test.json'

def get_soup(url):
    """
    Fetches URL using Cloudscraper to bypass 403/429/Disconnects.
    """
    retries = 3
    for i in range(retries):
        try:
            # Random sleep to look human
            time.sleep(random.uniform(2.0, 5.0))
            
            # cloudscraper handles the request automatically
            response = scraper.get(url, timeout=20)
            
            if response.status_code == 200:
                return BeautifulSoup(response.content, 'html.parser')
            elif response.status_code == 429:
                print(f"  [!] Rate limited (429). Sleeping 60s...")
                time.sleep(60)
            else:
                print(f"  [!] Error {response.status_code} for {url}")
        
        except Exception as e:
            print(f"  [!] Connection issue: {e}. Retrying...")
            time.sleep(10)
            
    return None

def save_json_data(data):
    """Save parsed data to JSON file."""
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def parse_source_page(url):
    """
    Parses a single MBFC source page and extracts all available information.
    Maintains exact JSON structure as the original parser.
    """
    soup = get_soup(url)
    if not soup:
        return None

    data = {
        'mbfc_url': url,
        'name': None,
        'source_url': None,

        # Ratings
        'bias_rating': None,
        'bias_score': None,
        'factual_reporting': None,
        'factual_score': None,
        'credibility_rating': None,

        # Metadata
        'country': None,
        'country_freedom_rating': None,
        'media_type': None,
        'traffic_popularity': None,

        # Content sections
        'bias_category_description': None,
        'overall_summary': None,
        'history': None,
        'ownership': None,
        'analysis': None,

        # Fact checks
        'failed_fact_checks': [],

        # Timestamp
        'last_updated': None
    }

    # Extract name from h1
    h1 = soup.find('h1', class_='entry-title')
    if h1:
        name = h1.get_text(strip=True)
        # Clean up common suffixes
        for suffix in [' – Bias and Credibility', ' - Bias and Credibility',
                       ' – Media Bias/Fact Check', ' - Media Bias/Fact Check']:
            name = name.replace(suffix, '')
        data['name'] = name.strip()

    # Get the main content area
    entry_content = soup.find('div', class_='entry-content')
    if not entry_content:
        return data

    # Get full text for regex extraction
    full_text = entry_content.get_text(" ", strip=True)

    # === EXTRACT DETAILED REPORT FIELDS ===

    # Bias Rating with score
    bias_match = re.search(r'Bias Rating:\s*([A-Z\-\s]+?)\s*\(([+-]?\d+\.?\d*)\)', full_text)
    if bias_match:
        data['bias_rating'] = bias_match.group(1).strip()
        try:
            data['bias_score'] = float(bias_match.group(2))
        except:
            pass
    else:
        # Fallback: just get the rating without score
        bias_match = re.search(r'Bias Rating:\s*([A-Z][A-Z\-\s]*?)(?:\s*Factual|\s*Country|\s*Press|\s*MBFC|\s*Media|\s*Traffic|$)', full_text)
        if bias_match:
            data['bias_rating'] = bias_match.group(1).strip()

    # Factual Reporting with score
    factual_match = re.search(r'Factual Reporting:\s*([A-Z][A-Z\s]*?)\s*\(([+-]?\d+\.?\d*)\)', full_text)
    if factual_match:
        data['factual_reporting'] = factual_match.group(1).strip()
        try:
            data['factual_score'] = float(factual_match.group(2))
        except:
            pass
    else:
        factual_match = re.search(r'Factual Reporting:\s*([A-Z][A-Z\s]*?)(?:\s*Country|\s*Press|\s*MBFC|\s*Media|\s*Traffic|$)', full_text)
        if factual_match:
            data['factual_reporting'] = factual_match.group(1).strip()

    # Country
    country_match = re.search(r'Country:\s*([A-Za-z][A-Za-z\s,]*?)(?=(?:\s*(?:Press|MBF|Media|Traffic|World|Factual)|$))', full_text, re.IGNORECASE)
    if country_match:
        data['country'] = country_match.group(1).strip()
        
    # Press Freedom Rating
    freedom_match = re.search(r'(?:Press Freedom Rating|MBF[Cc][’\']s Country Freedom (?:Rating|Rank)):\s*([A-Z][A-Z\s]*?)(?:\s*Media|\s*Traffic|\s*MBFC|$)', full_text)
    if freedom_match:
        data['country_freedom_rating'] = freedom_match.group(1).strip()
        
    # Media Type
    media_match = re.search(r'Media Type:\s*([A-Za-z][A-Za-z\s/,]*?)(?:\s*Traffic|\s*MBFC Credibility|$)', full_text)
    if media_match:
        data['media_type'] = media_match.group(1).strip()

    # Traffic/Popularity
    traffic_match = re.search(r'Traffic/Popularity:\s*([A-Za-z][A-Za-z\s]*?)(?:\s*MBFC Credibility|\s*History|\s*Funded|$)', full_text)
    if traffic_match:
        data['traffic_popularity'] = traffic_match.group(1).strip()

    # Credibility Rating
    cred_match = re.search(r'MBFC Credibility Rating:\s*([A-Z][A-Z\s]*?)(?:\s*History|\s*Funded|\s*Analysis|\s*Source|$)', full_text)
    if cred_match:
        data['credibility_rating'] = cred_match.group(1).strip()

    # === EXTRACT CONTENT SECTIONS ===
    all_elements = entry_content.find_all(['p', 'h2', 'h3', 'h4'])

    current_section = None
    section_content = {
        'history': [],
        'ownership': [],
        'analysis': [],
        'fact_checks': []
    }

    for elem in all_elements:
        text = elem.get_text(strip=True)

        # Detect section headers
        if elem.name in ['h2', 'h3', 'h4']:
            text_lower = text.lower()
            if 'history' in text_lower:
                current_section = 'history'
            elif 'funded' in text_lower or 'ownership' in text_lower:
                current_section = 'ownership'
            elif 'analysis' in text_lower or 'bias' in text_lower:
                current_section = 'analysis'
            elif 'fact check' in text_lower or 'failed' in text_lower:
                current_section = 'fact_checks'
            else:
                current_section = None
        elif current_section and elem.name == 'p' and len(text) > 20:
            section_content[current_section].append(text)

    # Combine section content
    if section_content['history']:
        data['history'] = ' '.join(section_content['history'])
    if section_content['ownership']:
        data['ownership'] = ' '.join(section_content['ownership'])
    if section_content['analysis']:
        data['analysis'] = ' '.join(section_content['analysis'])

    # === EXTRACT FAILED FACT CHECKS ===
    fact_check_section = entry_content.find(string=re.compile(r'Failed Fact Check', re.I))
    if fact_check_section:
        parent = fact_check_section.find_parent()
        if parent:
            next_list = parent.find_next(['ul', 'ol'])
            if next_list:
                for li in next_list.find_all('li'):
                    fc_text = li.get_text(strip=True)
                    if fc_text and len(fc_text) > 10:
                        data['failed_fact_checks'].append(fc_text)
            else:
                for sibling in parent.find_next_siblings('p'):
                    sibling_text = sibling.get_text(strip=True)
                    if sibling_text and ('–' in sibling_text or '-' in sibling_text) and len(sibling_text) > 20:
                        if 'Overall' in sibling_text:
                            break
                        data['failed_fact_checks'].append(sibling_text)

    # === EXTRACT OVERALL SUMMARY ===
    overall_match = re.search(r'(Overall,?\s+.*?(?:\.[^.]+){0,3}\.)', full_text)
    if overall_match:
        data['overall_summary'] = overall_match.group(1).strip()
    
    if not data['overall_summary']:
        list_items = entry_content.find_all('li')
        for li in list_items:
            li_text = li.get_text(strip=True)
            if ('is rated' in li_text or 'we rate' in li_text) and len(li_text) > 50:
                if any(x in li_text for x in ['Left', 'Right', 'Center', 'Satire', 'Bias', 'Factual']):
                    data['overall_summary'] = li_text
                    break

    # === EXTRACT BIAS CATEGORY DESCRIPTION ===
    first_paras = entry_content.find_all('p', limit=3)
    for p in first_paras:
        p_text = p.get_text(strip=True)
        if 'BIAS' in p_text.upper() and ('media sources' in p_text.lower() or 'these sources' in p_text.lower()):
            data['bias_category_description'] = p_text
            break

    # === EXTRACT SOURCE URL ===
    source_match = re.search(r'Source:\s*(https?://[^\s<>"]+)', full_text)
    if source_match:
        data['source_url'] = source_match.group(1).strip()
    else:
        source_link = entry_content.find('a', href=re.compile(r'^https?://(?!mediabiasfactcheck)'))
        if source_link and 'href' in source_link.attrs:
            potential_url = source_link['href']
            if not any(x in potential_url for x in ['facebook.com', 'twitter.com', 'linkedin.com', 'patreon.com']):
                data['source_url'] = potential_url

    # === EXTRACT LAST UPDATED ===
    updated_match = re.search(r'Last Updated on ([A-Za-z]+ \d+, \d+)', full_text)
    if updated_match:
        data['last_updated'] = updated_match.group(1)

    return data

def main():
    print(f"--- Starting Test Parser ---")
    print(f"Reading URLs from: {INPUT_FILE}")
    print(f"Output will be saved to: {OUTPUT_FILE}")

    # Check if input file exists
    if not os.path.exists(INPUT_FILE):
        print(f"[!] Error: {INPUT_FILE} not found. Please create this file with your URLs.")
        return

    # Read URLs
    urls_to_process = []
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            url = line.strip()
            # Simple validation to skip empty lines or headers
            if url and url.startswith('http'):
                urls_to_process.append(url)
    
    if not urls_to_process:
        print("[!] No valid URLs found in file.")
        return

    print(f"Found {len(urls_to_process)} URLs to process.")

    results = []
    failed_urls = []

    for i, url in enumerate(urls_to_process):
        print(f"[{i+1}/{len(urls_to_process)}] Parsing: {url}")

        try:
            info = parse_source_page(url)
            if info:
                results.append(info)
            else:
                failed_urls.append(url)
                print(f"  [!] Failed to parse: {url}")
        except Exception as e:
            failed_urls.append(url)
            print(f"  [!] Error parsing {url}: {e}")

        # Save checkpoint every 5 items
        if (i + 1) % 5 == 0:
            save_json_data(results)
            print(f"  [Checkpoint] Saved {len(results)} records")

    # Final Save
    save_json_data(results)
    print(f"\nDone! Successfully parsed {len(results)} sources.")
    print(f"Data saved to {OUTPUT_FILE}")

    if failed_urls:
        print(f"\n[!] Failed to parse {len(failed_urls)} URLs:")
        for url in failed_urls:
            print(f"    - {url}")

if __name__ == "__main__":
    main()