# app/utils/pdf_loader.py
"""
Load PDFs and convert to LangChain Document objects.
We use PyPDF2 or LangChain's loader if available.
"""

from langchain.document_loaders import PyPDFLoader
from langchain.docstore.document import Document
from typing import List
import os

def load_pdf(file_path):
    """
    Load a single PDF and return a list of LangChain Document objects (one per page by default).
    """
    loader = PyPDFLoader(file_path)
    docs = loader.load()
    # docs are LangChain Document objects with page_content and metadata
    return docs