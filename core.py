# app/utils/core.py

import os
from typing import List, Optional
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from config import (
    FAISS_INDEX_PATH,
    GEMINI_EMBEDDING_MODEL,
    GEMINI_QNA_MODEL,
    CHUNK_SIZE,
    CHUNK_OVERLAP
)

# Initialize embeddings and LLM globally for efficiency
# API key is automatically picked up by LangChain from the environment
EMBEDDINGS = GoogleGenerativeAIEmbeddings(model=GEMINI_EMBEDDING_MODEL)
LLM = ChatGoogleGenerativeAI(model=GEMINI_QNA_MODEL)


def load_and_chunk_pdf(file_path: str) -> List[Document]:
    """Load a PDF, split it into pages, and then chunk the content."""
    try:
        loader = PyPDFLoader(file_path)
        pages = loader.load()

        # Splitter configuration for text chunks
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            separators=["\n\n", "\n", ".", "!", "?", " ", ""]
        )
        chunks = splitter.split_documents(pages)
        return chunks
    except Exception as e:
        print(f"Error loading or chunking PDF: {e}")
        return []

def create_or_update_vector_store(chunks: List[Document]) -> bool:
    """
    Creates a new FAISS index from chunks or updates an existing one.
    The index is persisted to disk.
    """
    if not chunks:
        return False

    try:
        # Check if the FAISS index already exists
        if os.path.exists(FAISS_INDEX_PATH):
            # Load existing store
            vectorstore = FAISS.load_local(
                FAISS_INDEX_PATH,
                EMBEDDINGS,
                allow_dangerous_deserialization=True
            )
            # Add new documents to the existing store
            vectorstore.add_documents(chunks)
        else:
            # Create a new store
            vectorstore = FAISS.from_documents(chunks, EMBEDDINGS)

        # Save the updated/new index to the local directory
        vectorstore.save_local(FAISS_INDEX_PATH)
        return True
    except Exception as e:
        print(f"Error creating/updating FAISS store: {e}")
        return False


def get_contextual_answer(query: str, k: int = 4) -> str:
    """
    Retrieves the most relevant chunks from the FAISS store and uses the LLM
    to generate a contextual answer.
    """
    # 1. Check for persisted index
    if not os.path.exists(FAISS_INDEX_PATH):
        return "Error: Document index not found. Please upload a PDF first."

    try:
        # 2. Load the vector store
        vectorstore = FAISS.load_local(
            FAISS_INDEX_PATH,
            EMBEDDINGS,
            allow_dangerous_deserialization=True
        )

        # 3. Retrieval (Similarity Search)
        # Retrieve top 'k' most similar documents
        retrieved_docs = vectorstore.similarity_search(query, k=k)
        
        # 4. Context Preparation
        context = "\n---\n".join([doc.page_content for doc in retrieved_docs])
        
        # 5. RAG Prompt Template
        prompt_template = PromptTemplate(
            template=(
                "You are an expert Q&A system for insurance policies. "
                "Answer the user's question based ONLY on the provided context below. "
                "If the answer is not found in the context, state 'The required information is not available in the uploaded documents.'\n\n"
                "CONTEXT:\n---\n{context}\n---\n\n"
                "QUESTION: {question}"
            ),
            input_variables=['question', 'context']
        )
        
        # 6. LLM Invocation
        final_prompt = prompt_template.invoke({'context': context, 'question': query})
        
        response = LLM.invoke(final_prompt)
        return response.content

    except Exception as e:
        print(f"Error during RAG process: {e}")
        return "An internal error occurred while processing the question."