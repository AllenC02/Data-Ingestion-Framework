import json

# Function to combine PDF and Link data and save to JSON
def save_to_json(pdf_data,
                 link_data,
                 bookmarks_data,
                 notion_data,
                 output_file):        
    combined_data = pdf_data + link_data + bookmarks_data + notion_data
    
    with open(output_file, "w", encoding='utf-8') as f:
        json.dump(combined_data, f, indent=4)