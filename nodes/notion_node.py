import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import json
from notion_client import Client, APIResponseError

# Function to fetch blocks from a Notion page
def fetch_page_blocks(notion_api, page_id):
    notion = Client(auth=notion_api)
    results = []
    start_cursor = None

    while True:
        try:
            response = notion.blocks.children.list(
                block_id=page_id,
                start_cursor=start_cursor
            )
            results.extend(response['results'])
            if not response['has_more']:
                break
            start_cursor = response['next_cursor']
        except APIResponseError as e:
            print(f"An error occurred: {e}")
            break

    return results

# Function to fetch page title
def fetch_page_title(notion_api, page_id):
    notion = Client(auth=notion_api)
    try:
        response = notion.pages.retrieve(page_id)
        title = response['properties']['title']['title'][0]['plain_text']
    except APIResponseError as e:
        print(f"An error occurred: {e}")
        title = "Unknown Title"
    return title

# Function to fetch all child pages recursively
def fetch_all_child_pages(notion_api, page_id):
    notion = Client(auth=notion_api)
    pages_to_process = [page_id]
    all_page_ids = set()

    while pages_to_process:
        current_page_id = pages_to_process.pop()
        all_page_ids.add(current_page_id)
        blocks = fetch_page_blocks(notion_api, current_page_id)

        for block in blocks:
            if block['type'] == 'child_page':
                child_page_id = block['id']
                if child_page_id not in all_page_ids:
                    pages_to_process.append(child_page_id)
            elif block['type'] == 'link_to_page':
                if 'page_id' in block['link_to_page']:
                    linked_page_id = block['link_to_page']['page_id']
                    if linked_page_id not in all_page_ids:
                        pages_to_process.append(linked_page_id)

    return list(all_page_ids)

# Function to extract content from blocks
def extract_content_from_blocks(blocks):
    content_list = []

    for block in blocks:
        block_type = block['type']
        try:
            if block_type == 'paragraph':
                text = block['paragraph']['rich_text']
                content = ''.join([t['plain_text'] for t in text])
                content_list.append(content)
            elif block_type == 'heading_1':
                text = block['heading_1']['rich_text']
                content = ''.join([t['plain_text'] for t in text])
                content_list.append(content)
            elif block_type == 'heading_2':
                text = block['heading_2']['rich_text']
                content = ''.join([t['plain_text'] for t in text])
                content_list.append(content)
            elif block_type == 'heading_3':
                text = block['heading_3']['rich_text']
                content = ''.join([t['plain_text'] for t in text])
                content_list.append(content)
            elif block_type == 'bulleted_list_item':
                text = block['bulleted_list_item']['rich_text']
                content = ''.join([t['plain_text'] for t in text])
                content_list.append(f"• {content}")
            elif block_type == 'numbered_list_item':
                text = block['numbered_list_item']['rich_text']
                content = ''.join([t['plain_text'] for t in text])
                content_list.append(f"{block['numbered_list_item'].get('number', '1')}. {content}")
            elif block_type == 'to_do':
                text = block['to_do']['rich_text']
                content = ''.join([t['plain_text'] for t in text])
                content_list.append(f"[{'x' if block['to_do']['checked'] else ' '}] {content}")
            # Add more block types as needed
        except KeyError as e:
            print(f"KeyError: {e} in block type: {block_type}")

    return content_list

# Function to chunk text
def chunk_text(text, chunk_size=200, overlap=30):
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunks.append(' '.join(words[i:i + chunk_size]))
    return chunks

# Function to create JSON structure
def create_json_structure(content_list, source, identifier):
    data = []
    chunk_num = 0
    for content in content_list:
        chunks = chunk_text(content)
        for chunk in chunks:
            chunk_num += 1
            metadata = {
                "source": source,
                "identifier": identifier,
                "location": f"Chunk {chunk_num}"
            }
            data.append({
                "content": chunk,
                "metadata": metadata
            })
    return data

# Function to process multiple Notion pages
def extract_and_chunk_notion_pages(notion_api, notion_page_ids, output_file_path, source_metadata):
    all_extracted_data = []

    for page_id in notion_page_ids:
        # Fetch page blocks
        page_blocks = fetch_page_blocks(notion_api, page_id)

        # Fetch page title
        page_title = fetch_page_title(notion_api, page_id)

        # Extract content from the blocks
        content_list = extract_content_from_blocks(page_blocks)

        # Create JSON structure
        extracted_data = create_json_structure(content_list, source=source_metadata, identifier=page_title)

        all_extracted_data.extend(extracted_data)

    # Write to JSON file
    with open(output_file_path, 'w', encoding='utf-8') as json_file:
        json.dump(all_extracted_data, json_file, ensure_ascii=False, indent=4)

    return all_extracted_data

def read_notion_ids_from_json(file_path: str):
    with open(file_path, "r") as file:
        return json.load(file)

# Example usage
if __name__ == "__main__":
    source_metadata = "Notion"
    notion_ids_file_path = "user_kb/imports/notion_ids.json"
    extracted_notion_file_path = "user_kb/extracted/extracted_notion.json"

    # Read Notion page IDs from JSON
    notion_page_ids = read_notion_ids_from_json(notion_ids_file_path)

    # Read API key from config.json instead of config.json
    with open("utilities/config.json", 'r') as f:
        config = json.load(f)
    notion_api = config['notion_api_key']

    # Fetch all child pages recursively starting from the main page
    all_page_ids = []
    for page_id in notion_page_ids:
        all_page_ids.extend(fetch_all_child_pages(notion_api, page_id))

    # Extract and chunk content from Notion pages
    extract_and_chunk_notion_pages(notion_api, all_page_ids, extracted_notion_file_path, source_metadata)
