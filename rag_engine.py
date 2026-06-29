import os
import logging
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FinancialRAGEngine:
    def __init__(self, data_dir="./data", db_dir="./chroma_db"):
        self.data_dir = data_dir
        self.db_dir = db_dir
        self.vector_store = None
        
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            logger.info(f"Created data directory at {self.data_dir}")

    def extract_and_chunk_docs(self):
        """Loads PDFs from the data directory and splits them into clean text chunks."""
        try:
            logger.info("Parsing PDF documents from the data directory...")
            loader = PyPDFDirectoryLoader(self.data_dir)
            documents = loader.load()
            
            if not documents:
                logger.warning("No PDF files found in the data directory.")
                return []
                
            logger.info(f"Successfully read {len(set(doc.metadata.get('page', 0) for doc in documents))} total pages.")
            
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                length_function=len
            )
            
            chunks = text_splitter.split_documents(documents)
            logger.info(f"Created {len(chunks)} text chunks for indexing.")
            return chunks
            
        except Exception as e:
            logger.error(f"Failed to process documents: {str(e)}")
            return []

    def build_vector_index(self, chunks):
        """Builds a local Chroma vector store instantly using Hugging Face offline embeddings."""
        if not chunks:
            return False

        try:
            logger.info("Initializing high-performance local Hugging Face embedding model...")
            embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
            
            logger.info(f"Processing all {len(chunks)} chunks instantly into local vector engine...")
            self.vector_store = Chroma.from_documents(
                documents=chunks,
                embedding=embeddings,
                persist_directory=self.db_dir
            )
                
            logger.info("Vector database successfully built and stored locally via Hugging Face!")
            return True
            
        except Exception as e:
            logger.error(f"Error building vector database: {str(e)}")
            return False

    def format_docs(self, docs):
        """Helper to format retrieved documents cleanly into text context blocks."""
        formatted = []
        for doc in docs:
            page_info = f" (Page {doc.metadata.get('page', 'Unknown')})" if 'page' in doc.metadata else ""
            source_info = os.path.basename(doc.metadata.get('source', 'Document'))
            formatted.append(f"Content: {doc.page_content}\nSource: {source_info}{page_info}\n---")
        return "\n\n".join(formatted)

    def get_response(self, query):
        """Queries the vector database using pure LCEL and generates an answer via Gemini LLM."""
        try:
            if not self.vector_store:
                embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
                if os.path.exists(self.db_dir):
                    self.vector_store = Chroma(persist_directory=self.db_dir, embedding_function=embeddings)
                else:
                    return "System error: Vector index has not been built yet. Please upload files."

            # Initialize LLM with production fallback name
            llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
            retriever = self.vector_store.as_retriever(search_kwargs={"k": 5})
            
            system_prompt = (
                "You are an expert enterprise financial intelligence assistant.\n"
                "Use the following pieces of retrieved context to answer the question.\n"
                "If you don't know the answer, say that you don't know.\n"
                "Always cite the exact document name or page number if available in the context.\n\n"
                "Context:\n{context}\n\n"
                "Question: {question}\n"
                "Answer:"
            )
            
            prompt = ChatPromptTemplate.from_template(system_prompt)
            
            # MODERN LCEL PIPELINE: Zero wrapper classes, zero validation mismatches!
            rag_chain = (
                {"context": retriever | self.format_docs, "question": RunnablePassthrough()}
                | prompt
                | llm
                | StrOutputParser()
            )
            
            logger.info(f"Executing LCEL retrieval pipeline for query: '{query}'")
            response = rag_chain.invoke(query)
            return response
            
        except Exception as e:
            logger.error(f"Error querying RAG system: {str(e)}")
            return f"Error executing search query: {str(e)}"