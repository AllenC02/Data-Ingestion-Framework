import json
from sentence_transformers import SentenceTransformer
import faiss

# Load combined data
def load_combined_data(file_path: str):
    with open(file_path, "r", encoding="utf-8") as f:
        combined_data = json.load(f)
    return combined_data

# Create embeddings
def create_embeddings(data, model_name='all-MiniLM-L6-v2'):
    model = SentenceTransformer(model_name)
    texts = [item.get("content", "") for item in data if item.get("content", "").strip()]
    
    # Debugging: Print the number of texts and a sample
    print(f"Number of texts to encode: {len(texts)}")
    if len(texts) == 0:
        print("No valid content found in the combined data.")
    
    embeddings = model.encode(texts, convert_to_numpy=True)
    return embeddings, data

# Create FAISS index
def create_faiss_index(embeddings):
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)
    return index

# Save FAISS index and metadata
def save_faiss_index(index, metadata, index_path, metadata_path):
    faiss.write_index(index, index_path)
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=4)

def create_vectordb(combined_data_path, vector_db_path, metadata_path):
    combined_data = load_combined_data(combined_data_path)
    embeddings, metadata = create_embeddings(combined_data)
    if embeddings.size == 0:
        print("No embeddings created, skipping FAISS index creation.")
        return
    
    index = create_faiss_index(embeddings)
    save_faiss_index(index, metadata, vector_db_path, metadata_path)