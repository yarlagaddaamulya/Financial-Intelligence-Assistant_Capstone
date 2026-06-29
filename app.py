import os
import streamlit as st
import logging
from rag_engine import FinancialRAGEngine

# Setup page configurations
st.set_page_config(page_title="FinVista Financial Assistant", page_icon="💼", layout="wide")

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the RAG Engine in the session state so it persists across button clicks
if "rag_engine" not in st.session_state:
    st.session_state.rag_engine = FinancialRAGEngine()

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Title & Description
st.title("💼 FinVista Capital - Financial Intelligence Assistant")
st.markdown("Interact with enterprise annual reports, financial research, and compliance documents using natural language.")

# --- SIDEBAR: Document Management ---
with st.sidebar:
    st.header("📁 Document Ingestion")
    
    # File Uploader
    uploaded_files = st.file_uploader(
        "Upload Financial PDFs", 
        type=["pdf"], 
        accept_multiple_files=True,
        help="Upload enterprise documents to index into the Chroma Vector Database"
    )
    
    if st.button("Process & Index Documents", use_container_width=True):
        if not uploaded_files:
            st.warning("Please upload at least one PDF file first.")
        else:
            with st.spinner("Processing documents into local vector store..."):
                # Save uploaded files into the data folder
                for uploaded_file in uploaded_files:
                    file_path = os.path.join(st.session_state.rag_engine.data_dir, uploaded_file.name)
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    st.info(f"Saved: {uploaded_file.name}")
                
                # Run Chunking and Local Indexing
                chunks = st.session_state.rag_engine.extract_and_chunk_docs()
                if chunks:
                    success = st.session_state.rag_engine.build_vector_index(chunks)
                    if success:
                        st.success("Vector database built successfully!")
                    else:
                        st.error("Failed to build the vector index.")
                else:
                    st.error("No text chunks could be extracted from the uploaded files.")

# --- MAIN SCREEN: Chat Interface ---
st.subheader("💬 AI Conversation Interface")

# Display historical messages
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User prompt input box
if user_query := st.chat_input("Ask a question about the uploaded financial metrics..."):
    
    # 1. Display user query in chat
    with st.chat_message("user"):
        st.markdown(user_query)
    st.session_state.chat_history.append({"role": "user", "content": user_query})
    
    # 2. Get response from the pipeline
    with st.chat_message("assistant"):
        with st.spinner("Searching knowledge base and formulating response..."):
            # Call your LCEL engine directly
            response_text = st.session_state.rag_engine.get_response(user_query)
            st.markdown(response_text)
            
    # 3. Save assistant response to chat history
    st.session_state.chat_history.append({"role": "assistant", "content": response_text})