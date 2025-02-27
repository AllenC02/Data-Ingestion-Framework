import json
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
from openai import AzureOpenAI
import os
from utilities.chatbot_setup import load_config

# Initialize Azure OpenAI client
config = load_config()
azure_config = config.get('azure', {})

client = AzureOpenAI(
    api_key=azure_config['api_key'],
    api_version=azure_config['api_version'],
    azure_endpoint=azure_config['api_base']
)

# Load the FAISS index and metadata
def load_faiss_index(index_filename='vector_db.faiss', metadata_filename='metadata.json'):
    """
    Load the FAISS index and metadata.
    """
    # Construct the paths to the index and metadata files
    vector_db_path = "user_kb/vector_db"
    index_path = os.path.join(vector_db_path, index_filename)
    metadata_path = os.path.join(vector_db_path, metadata_filename)
    
    # Load the FAISS index
    index = faiss.read_index(index_path)
    
    # Load the metadata
    with open(metadata_path, 'r', encoding='utf-8') as f:
        metadata = json.load(f)
    
    return index, metadata

# Function for similarity search
def similarity_search(query, model, index, metadata, top_k=15):
    query_vector = model.encode([query])[0].astype('float32')
    distances, indices = index.search(np.array([query_vector]), top_k)
    results = [metadata[i] for i in indices[0]]
    return results

# Universal system prompt
system_prompt_universal = """
    You are a helpful assistant who answers users' questions based on multiple contexts given to you.
    Keep your answers short and to the point.
    The evidence provided is the context of the extracts from various sources with metadata.
    Carefully focus on the metadata, especially 'source', 'identifier', and 'location' whenever answering.
    Make sure to add the source (PDF/Link), identifier (filename/URL), and location (page no) at the end of the sentence you are citing.
    Reply "Not applicable" if the text is irrelevant.
    The content provided is:
    {extract}
"""

# Function for chatbot conversation
def conversation(user_query, chat_history):
    # Load FAISS index and metadata
    index, metadata = load_faiss_index()

    # Load SentenceTransformer model for encoding queries
    model = SentenceTransformer('all-MiniLM-L6-v2')

    # Retrieve similar document chunks to the user query
    docs = similarity_search(user_query, model, index, metadata, top_k=15)

    # Format the document chunks for the system prompt
    extract = "\n\n".join([
        f"Source: {doc['metadata']['source']} - Identifier: {doc['metadata']['identifier']} - {doc['metadata']['location']}\n\n{doc['content']}"
        for doc in docs
    ])

    # Initialize system prompt to be added to the model
    system = {"role": "system", "content": system_prompt_universal.format(extract=extract)}

    # Add the user query to chat history 
    chat_history.append({"role": "user", "content": user_query})

    # Call Azure OpenAI API
    completion = client.chat.completions.create(
        model="gpt-35-turbo-2",  # Azure OpenAI model deployment name
        messages=[system] + chat_history,
        temperature=0,
        max_tokens=200,
        frequency_penalty=0
    )

    chatbot_response = completion.choices[0].message.content
    chat_history.append({"role": "assistant", "content": chatbot_response})
    return chatbot_response

if __name__ == "__main__":
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
