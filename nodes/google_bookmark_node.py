# import json
# import os

# # Function to extract links from the JSON structure
# def get_links(bookmark_node):
#     links = []
#     if 'url' in bookmark_node:
#         links.append(bookmark_node['url'])
#     if 'children' in bookmark_node:
#         for child in bookmark_node['children']:
#             links.extend(get_links(child))
#     return links

# def extract_bookmarks(bookmarks_file_path):
#     """
#     Extract all links from a Google Chrome bookmarks JSON file and save them.

#     :param bookmarks_file_path: Path to the bookmarks file
#     """
#     # Read the bookmarks file
#     with open(bookmarks_file_path, 'r', encoding='utf-8') as f:
#         bookmarks_data = json.load(f)

#     # Extract the links using the get_links function
#     bookmark_links = get_links(bookmarks_data['roots']['bookmark_bar'])

#     bookmark_links = bookmark_links[:10]  # TEMPORARY MEASURE - only extracting 10 links for testing

#     # Save the extracted links to a JSON file
#     output_file_path = "user_kb/imports/bookmarked_links.json"
#     os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
    
#     with open(output_file_path, 'w', encoding='utf-8') as output_file:
#         json.dump(bookmark_links, output_file, indent=4)

#     print(f"Extracted {len(bookmark_links)} links and saved to {output_file_path}")

# # Example usage
# if __name__ == "__main__":
#     # Path to your exported bookmarks JSON file
#     bookmarks_json_file = r"/Users/allenchou/UCIrvine/Qiri/dataIngestionPipeline/Data-Ingestion-Framework/user_kb/extracted/extracted_bookmarks.json"
#     extract_bookmarks(bookmarks_json_file)
