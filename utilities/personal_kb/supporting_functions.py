import os
import json

# Function to extract JSON content    
def extract_json(file_path):
    """
    Extract JSON content from a file. If the file is empty or does not exist, return an empty list.

    :param file_path: Path to the JSON file.
    :return: Parsed JSON data or an empty list if the file is empty or not found.
    """
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            # Check if the file is empty
            if os.stat(file_path).st_size == 0:
                return []  # Return an empty list if the file is empty
            return json.load(file)
    else:
        return []  # Return an empty list if the file does not exist
    
# Function to save links to JSON
def dump_to_json(file_path, links):
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(links, file, indent=4)


def read_config():
    """Read configuration from config.json"""
    config_path = "user_kb/config.json"
    with open(config_path, 'r') as f:
        return json.load(f)

    

