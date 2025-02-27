import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import json
from utilities.personal_kb_web_crawler import run_spider
import spacy
import logging

def read_links_from_json(file_path: str):
    with open(file_path, "r") as file:
        return json.load(file)

def chunk_clean_links(file_path: str, source_metadata: str):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    nlp = spacy.load('en_core_web_sm')

    def clean_text(text):
        text = text.replace('\n', ' ').replace('\r', ' ')
        doc = nlp(text)
        tokens = [token.lemma_ for token in doc if not token.is_stop and not token.is_punct]
        return ' '.join(tokens)

    def chunk_text(text, chunk_size=200, overlap=30):
        words = text.split()
        chunks = []
        for i in range(0, len(words), chunk_size - overlap):
            chunks.append(' '.join(words[i:i + chunk_size]))
        return chunks

    all_chunks = []
    for entry in data:
        clean_content = clean_text(entry['content'])
        chunks = chunk_text(clean_content)
        for i, chunk in enumerate(chunks):
            chunk_data = {
                "content": chunk,
                "metadata": {
                    "source": source_metadata,
                    "identifier": entry['metadata']['identifier'],
                    "location": f"Chunk {i + 1}"
                }
            }
            logging.warning(f"Adding chunk: {chunk_data}")
            all_chunks.append(chunk_data)

    return all_chunks

def extract_and_chunk_links(links_file_path: str, extracted_links_file_path: str, source_metadata: str):
    # Get the URLs used for scraping
    urls_list = read_links_from_json(links_file_path)

    # Run spider to scrape the URLs
    run_spider(urls_list, source_metadata, extracted_links_file_path)

    # Chunk and clean the extracted data from links
    chunked_links_data = chunk_clean_links(extracted_links_file_path, source_metadata)

    # Output result to file for inspection [optional]
    with open(extracted_links_file_path, "w", encoding="utf-8") as f:
        json.dump(chunked_links_data, f, ensure_ascii=False, indent=4)

    return chunked_links_data

# Example usage
if __name__ == "__main__":
    source_metadata = "Link"
    links_file_path = "user_kb\imports\links.json"
    extracted_links_file_path = "user_kb\extracted\extracted_links.json"

    extract_and_chunk_links(links_file_path, extracted_links_file_path, source_metadata)