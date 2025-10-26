# app/utils/config.py

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Core RAG Configuration ---
# Models
GEMINI_EMBEDDING_MODEL = "models/embedding-001"
GEMINI_QNA_MODEL = "gemini-2.5-flash"

# Document Processing
CHUNK_SIZE = 1000  # Target size of text chunks
CHUNK_OVERLAP = 200 # Overlap between consecutive chunks

# FAISS Vector Store
FAISS_INDEX_PATH = os.getenv("FAISS_INDEX_PATH", "vector_store/faiss_index")

# --- Flask Configuration ---
UPLOAD_FOLDER = 'uploaded_pdfs'
ALLOWED_EXTENSIONS = {'pdf'}

# Create the necessary directories if they don't exist
os.makedirs(FAISS_INDEX_PATH, exist_ok=True)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)