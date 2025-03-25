import streamlit as st
from helpers import load_embedding_model, load_chroma_collection, retrieve_relevant_chunks
from gemini_helper import generate_answer_gemini  # Assuming gemini_helper.py is in the same directory
import os  # For potential environment variable access

# --- Page Configuration ---
st.set_page_config(
    page_title="KYLEWARE",  # Updated page title
    page_icon="assets/logo_helmet.ico",  # Updated favicon
    layout="wide",
    initial_sidebar_state="expanded"  # Sidebar now open by default
)

# --- App Title Image in Main Content ---
col1, col2, col3 = st.columns([1, 2, 9])
with col1:
    st.image("assets/logo_helmet_100.png")  # Display KYLEWARE title image, adjust width as needed
with col2:
    st.title("KYLEWARE")
with col3:
    st.empty()  # Empty column for spacing
st.markdown("Ask me anything about Space Engineers Code!")
st.markdown("This chatbot uses Retrieval-Augmented Generation (RAG) to answer your questions based on the content of the [MDK-SE Wiki](https://github.com/malware-dev/MDK-SE/wiki).")

# --- Sidebar Content ---

# Buy Me A Coffee Button (Replace with your actual link/button code)
st.sidebar.markdown("""
    <a href="https://www.buymeacoffee.com/labadorf" target="_blank">
        <img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 5px !important;" >
    </a>
""", unsafe_allow_html=True)
st.sidebar.markdown("**Support the development of this app!**")
st.sidebar.markdown("---") # Separator line in sidebar

# Footer in Sidebar (Moved About section to sidebar)
st.sidebar.header("About This App")
st.sidebar.markdown(
    """
    This Streamlit app is a demo of a Retrieval-Augmented Generation (RAG) system built on top of the
    [MDK-SE Wiki](https://github.com/malware-dev/MDK-SE/wiki).

    **How it works:**

    1.  **Data Ingestion:** The app uses the MDK-SE Wiki as its knowledge base. The data is stored in a ChromaDB vector database.
    2.  **Embedding Generation:** The app uses the Sentence Transformers library to generate embeddings for the text data.
    3.  **Retrieval-Augmented Generation (RAG):** When a user asks a question, the app retrieves relevant chunks of text from the ChromaDB based on the user's query.
    4.  **Answer Generation:** The app uses the Gemini API to generate an answer based on the retrieved context chunks.
    5.  **User Interface:** The app is built using Streamlit, providing an interactive web interface for users to ask questions and receive answers.

    **Libraries Used:**

    *   Streamlit: for the web app framework and deploying.
    *   ChromaDB: for the vector database.
    *   Sentence Transformers: for embedding generation.
    *   Gemini API: for the generative model.

    **Source Code:**

    [Link to your GitHub repository (if you make it public)] - *Replace with your repo link if you want to share the code*

    **Thanks and Acknowledgements:**
    *   [Malware-dev](https://github.com/malware-dev/)MDK-SE/wiki - for the MDK-SE Wiki content and for licensing the data under MIT.
    *   Perkins and Matt: for playing Space Engineers with me and for the inspiration to build this app.
    *   Kyle: my 9-month-old son, for waking me up at 3 AM and making me realize I need to build this app to answer my questions about Space Engineers code faster.
    *   You: for using this app and for your support!

    """
)

#add a fooder to the main page
st.markdown("""
    <style>
        .footer {
            position: fixed;
            left: 0;
            bottom: 0;
            width: 100%;
            background-color: #f1f1f1;
            text-align: center;
            padding: 10px;
        }
    </style>
    <div class="footer">
        <p>Made with ❤️ by <a href="jamesthedatascientist.com" target="_blank">James the Data Scientist</a></p>
    </div>
""", unsafe_allow_html=True)
# --- Initialize embedding model and ChromaDB collection ONCE when app starts (using st.cache_resource) ---
@st.cache_resource
def load_resources():
    embedding_model = load_embedding_model()
    collection = load_chroma_collection()
    if not collection:
        st.error("Failed to load ChromaDB collection. Please check if the database exists at 'chroma_db' (or the specified persist directory).")
        return None, None  # Return None for both if loading fails
    return embedding_model, collection

embedding_model, collection = load_resources()

if not collection: # Stop if collection failed to load in load_resources
    st.stop()

# --- Gemini API Key Check ---
if not os.environ.get("GEMINI_API_KEY"):
    st.error("Please set the GEMINI_API_KEY environment variable to use the Gemini API.")
    st.stop()

# --- User Query Input ---
user_query = st.text_input("Ask your question here:", placeholder="e.g., How do I create a custom action in MDK-SE?", key="user_query_input")

# --- RAG Process on Query Submission ---
if user_query:
    if not embedding_model or not collection: # Double check in case of race conditions or issues with st.cache_resource
        st.error("Embedding model or ChromaDB collection not loaded correctly. Please refresh the app.")
        st.stop()

    with st.spinner("Retrieving relevant information from the MDK-SE Wiki..."):
        retrieved_context = retrieve_relevant_chunks(user_query, embedding_model, collection)

    if retrieved_context:
        with st.spinner("Generating answer using Gemini..."):
            gemini_answer = generate_answer_gemini(user_query, retrieved_context)

        st.subheader("Answer:")
        st.write(gemini_answer)

        with st.expander("Show Retrieved Context Chunks"):
            st.markdown("Context chunks retrieved from the MDK-SE Wiki that were used to generate the answer:")
            for chunk in retrieved_context:
                st.info(f"Source: `{chunk['source']}`  |  Block Type: `{chunk['block_type']}` | Distance: `{chunk['distance']:.4f}`") # Use st.info for better visual separation
                st.code(chunk['content'], language='csharp' if chunk['block_type'] == 'code' else None) # Use st.code for code blocks
                st.write("---") # Separator

    else:
        st.warning("No relevant information found in the MDK-SE Wiki for your query. Please try a different question.")
