import chromadb
from sentence_transformers import SentenceTransformer
import os  # Import os for persistent ChromaDB path if needed

# --- Embedding Model Initialization ---
def load_embedding_model(model_name="all-mpnet-base-v2"):
    """Loads the Sentence Transformer embedding model."""
    return SentenceTransformer(model_name)

# --- ChromaDB Client and Collection Loading ---
def load_chroma_collection(collection_name="space_engineers_api_docs", persist_directory="vectordb"): # Added persist_directory
    """Loads the ChromaDB collection (assuming persistent client)."""
    # Use persistent client to load from disk
    client = chromadb.PersistentClient(path=persist_directory) # Use persist_directory here
    collection = client.get_collection(name=collection_name)
    return collection

# --- Retrieval Function ---
def retrieve_relevant_chunks(query, embedding_model, collection, top_k=5):
    """
    Retrieves relevant chunks from ChromaDB based on a user query.

    Args:
        query (str): The user query.
        embedding_model: The Sentence Transformer embedding model.
        collection: The ChromaDB collection.
        top_k (int, optional): The number of top chunks to retrieve. Defaults to 5.

    Returns:
        list: A list of dictionaries, where each dictionary represents a retrieved chunk
              and contains 'content' and 'source' keys.
    """
    query_embedding = embedding_model.encode(query)
    results = collection.query(
        query_embeddings=[query_embedding.tolist()],
        n_results=top_k,
        include=["metadatas", "documents", "distances"]  # Include distances
    )

    retrieved_chunks = []
    if results and results["ids"] and results["documents"]: # Check if results are not empty
        for i in range(len(results["ids"][0])): # Iterate through results for the first query (we only sent one)
            retrieved_chunks.append({
                "content": results["documents"][0][i],
                "source": results["metadatas"][0][i]["source"],
                "block_type": results["metadatas"][0][i]["block_type"], # Include block_type
                "distance": results["distances"][0][i] # Include distance score
            })
    else:
        print("No relevant chunks found.")
    return retrieved_chunks

# --- (Optional) Test Retrieval Function (for testing helpers.py independently) ---
def test_retrieval(query, embedding_model, collection):
    """
    Tests the retrieval function and prints the retrieved chunks.
    """
    print(f"\n--- Retrieval Test in helpers.py ---")
    print(f"Query: '{query}'")

    retrieved_chunks = retrieve_relevant_chunks(query, embedding_model, collection)

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
    collection = load_chroma_collection() # Assumes persistent ChromaDB in 'chroma_db' folder

    if collection: # Only test if collection loaded successfully
        test_query = "How do I get the current grid in MDK-SE?"
        test_retrieval(test_query, embedding_model, collection)
    else:
        print("ChromaDB collection not loaded. Make sure the database exists at 'chroma_db'.")