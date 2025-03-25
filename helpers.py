import faiss
import numpy as np
import json # To load metadata
from sentence_transformers import SentenceTransformer
import os  # Import os for persistent ChromaDB path if needed

index_file_path = "faiss_index.bin" # Make sure this matches where you saved your index
metadata_file_path = "metadata.json" # Make sure this matches where you saved your metadata

# --- Embedding Model Initialization ---
def load_embedding_model(model_name="all-mpnet-base-v2"):
    """Loads the Sentence Transformer embedding model."""
    return SentenceTransformer(model_name)

# --- FAISS Index and Metadata Loading ---
def load_faiss_index(index_path=index_file_path, metadata_path=metadata_file_path):
    """Loads the FAISS index and metadata from files."""
    try:
        loaded_index = faiss.read_index(index_path)
    except RuntimeError as e: # Catch FAISS errors if index file is not found or corrupted
        print(f"Error loading FAISS index from {index_path}: {e}")
        return None, None

    try:
        with open(metadata_path, 'r') as f:
            loaded_metadata = json.load(f)
    except FileNotFoundError:
        print(f"Metadata file not found at {metadata_path}")
        return loaded_index, None # Return index even if metadata is missing, handle None metadata later
    except json.JSONDecodeError as e:
        print(f"Error decoding metadata JSON from {metadata_path}: {e}")
        return loaded_index, None # Return index even if metadata is corrupted, handle None metadata later
    return loaded_index, loaded_metadata

# --- Retrieval Function (FAISS Version) ---
def retrieve_relevant_chunks(query, embedding_model, faiss_index, faiss_metadata, top_k=5): # Renamed collection to faiss_index and faiss_metadata
    """
    Retrieves relevant chunks from FAISS index based on a user query.

    Args:
        query (str): The user query.
        embedding_model: The Sentence Transformer embedding model.
        faiss_index: The loaded FAISS index. # Changed from collection
        faiss_metadata: The loaded metadata from JSON. # Added faiss_metadata
        top_k (int, optional): The number of top chunks to retrieve. Defaults to 5.

    Returns:
        list: A list of dictionaries, where each dictionary represents a retrieved chunk
              and contains 'content' and 'source' keys.
    """
    if faiss_index is None or faiss_metadata is None: # Check if index or metadata failed to load
        print("FAISS index or metadata not loaded. Retrieval cannot be performed.")
        return []

    query_embedding = embedding_model.encode(query).astype('float32').reshape(1, -1) # Encode query and reshape for FAISS
    distances, indices = faiss_index.search(query_embedding, top_k)

    retrieved_chunks = []
    if indices.any() and indices[0][0] != -1: # Check if results are found
        for i in range(len(indices[0])):
            index_result = indices[0][i]
            if index_result != -1: # Double check for valid index, although should be valid in this setup
                distance = distances[0][i]
                metadata_result = faiss_metadata[index_result] # Access metadata using the FAISS index
                retrieved_chunks.append({
                    "content": metadata_result['document'], # Get document content from metadata
                    "source": metadata_result['metadata']['source'], # Get source from metadata
                    "block_type": metadata_result['metadata']['block_type'], # Get block_type from metadata
                    "distance": distance
                })
    else:
        print("No relevant chunks found.")
    return retrieved_chunks

# --- (Optional) Test Retrieval Function (for testing helpers.py independently) ---
def test_retrieval(query, embedding_model, faiss_index, faiss_metadata): # Updated to take faiss_index and faiss_metadata
    """
    Tests the retrieval function and prints the retrieved chunks.
    """
    print(f"\n--- Retrieval Test in helpers.py (FAISS) ---") # Updated print statement
    print(f"Query: '{query}'")

    retrieved_chunks = retrieve_relevant_chunks(query, embedding_model, faiss_index, faiss_metadata) # Updated function call

    if retrieved_chunks:
        print(f"\nRetrieved Chunks (Top {len(retrieved_chunks)}):")
        for i, chunk in enumerate(retrieved_chunks):
            print(f"\nChunk {i+1}:")
            print(f"  Source: {chunk['source']}")
            print(f"  Block Type: {chunk['block_type']}")
            print(f"  Distance: {chunk['distance']:.4f}")
            print(f"  Content:\n{chunk['content']}")
    else:
        print("No relevant chunks retrieved for this query.")


if __name__ == "__main__":
    # --- Example usage when running helpers.py directly ---
    embedding_model = load_embedding_model()
    faiss_index, faiss_metadata = load_faiss_index() # Load FAISS index and metadata

    if faiss_index and faiss_metadata: # Only test if index and metadata loaded successfully
        test_query = "How do I get the current grid in MDK-SE?"
        test_retrieval(test_query, embedding_model, faiss_index, faiss_metadata) # Updated test_retrieval call
    else:
        print("FAISS index or metadata not loaded. Make sure the files exist and are valid.")