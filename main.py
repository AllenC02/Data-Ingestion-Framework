import os
import json
from nodes.pdf_node import extract_and_chunk_pdfs
from nodes.link_node import extract_and_chunk_links
# from nodes.google_bookmark_node import extract_bookmarks
from nodes.notion_node import fetch_all_child_pages, extract_and_chunk_notion_pages, read_notion_ids_from_json
from utilities.personal_kb.combine import save_to_json
from utilities.personal_kb.vectordb import create_vectordb
from utilities.personal_kb.conversation import conversation

def process_knowledge_base():
    """Process all knowledge base sources and create vector database."""
    print("Starting knowledge base processing...")
    with open("utilities/config.json", 'r') as f:
        config = json.load(f)
    
    # Process PDFs
    print("\n1. Processing PDFs...")
    pdf_data = extract_and_chunk_pdfs(
        "user_kb/imports/pdfs",
        "user_kb/extracted/extracted_pdfs.json"
    )
    
    # Process Links
    print("\n2. Processing Links...")
    link_data = extract_and_chunk_links(
        "user_kb/imports/links.json",
        "user_kb/extracted/extracted_links.json",
        "Link"
    )
    
    # Process Bookmarks
    print("\n3. Processing Bookmarks...")
    # First extract bookmarks to JSON
    # extract_bookmarks(config['bookmarks_json_url'])
    # Then process them like regular links
    bookmarks_data = extract_and_chunk_links(
        "user_kb/imports/bookmarked_links.json",
        "user_kb/extracted/extracted_bookmarks.json",
        "Google Chrome Bookmark"
    )
    
    # Process Notion
    print("\n4. Processing Notion pages...")
    notion_data = []
    if config['notion_api_key']:
        notion_ids_file_path = "user_kb/imports/notion_ids.json"
        extracted_notion_file_path = "user_kb/extracted/extracted_notion.json"
        notion_page_ids = read_notion_ids_from_json(notion_ids_file_path)
        
        # Fetch all child pages recursively
        all_page_ids = []
        for page_id in notion_page_ids:
            all_page_ids.extend(fetch_all_child_pages(config['notion_api_key'], page_id))
        
        notion_data = extract_and_chunk_notion_pages(
            config['notion_api_key'],
            all_page_ids,  # Use the expanded list of page IDs
            extracted_notion_file_path,
            "Notion"
        )
        print(f"Processed {len(all_page_ids)} Notion pages")

    # Combine all data
    print("\n5. Combining all data...")
    save_to_json(
        pdf_data,
        link_data,
        bookmarks_data,
        notion_data,
        "user_kb/extracted/combined_data.json"
    )
    
    # Create vector database
    print("\n6. Creating vector database...")
    os.makedirs("user_kb/vector_db", exist_ok=True)
    create_vectordb(
        "user_kb/extracted/combined_data.json",
        "user_kb/vector_db/vector_db.faiss",
        "user_kb/vector_db/metadata.json"
    )
    print("\nKnowledge base processing complete!")

def chat_with_knowledge_base():
    """Start an interactive chat session with the knowledge base."""
    print("\nWelcome to your Knowledge Base Chat!")
    print("Type 'exit' to end the conversation\n")
    
    chat_history = []
    while True:
        user_input = input("\nYou: ").strip()
        if user_input.lower() == 'exit':
            print("\nGoodbye!")
            break
            
        try:
            response = conversation(user_input, chat_history)
            print("\nAssistant:", response)
        except Exception as e:
            print("\nError:", str(e))
            print("Please try again.")

def main():
    while True:
        print("\nKnowledge Base Menu:")
        print("1. Process/Update Knowledge Base")
        print("2. Chat with Knowledge Base")
        print("3. Exit")
        
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == '1':
            process_knowledge_base()
        elif choice == '2':
            chat_with_knowledge_base()
        elif choice == '3':
            print("\nGoodbye!")
            break
        else:
            print("\nInvalid choice. Please try again.")

if __name__ == "__main__":
    main()
