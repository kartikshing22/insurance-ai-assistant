# app/routes.py

import os
from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from werkzeug.utils import secure_filename
from core import load_and_chunk_pdf, create_or_update_vector_store, get_contextual_answer
from config import UPLOAD_FOLDER, ALLOWED_EXTENSIONS, FAISS_INDEX_PATH
from utils.logger import log_activity

# Define the blueprint
bp = Blueprint('main', __name__)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/')
def index():
    """Renders the main application page."""
    # Check if a FAISS index exists to inform the user
    index_exists = os.path.exists(FAISS_INDEX_PATH)
    return render_template('index.html', index_exists=index_exists)


@bp.route('/upload', methods=['POST'])
def upload_file():
    """Handles PDF file uploads, chunking, embedding, and vector store update."""
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    if file and allowed_file(file.filename):
        # 1. Secure and save the file
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        log_activity("UPLOAD", filename)

        # 2. Load, chunk, and embed
        try:
            chunks = load_and_chunk_pdf(file_path)
            if not chunks:
                return jsonify({"error": "Could not process PDF. It may be empty or corrupted."}), 500
            
            # 3. Create or update the vector store
            success = create_or_update_vector_store(chunks)

            if success:
                return jsonify({
                    "message": f"Successfully processed '{filename}'. Index updated with {len(chunks)} chunks.",
                    "chunks": len(chunks)
                })
            else:
                return jsonify({"error": "Failed to create/update vector store."}), 500

        except Exception as e:
            return jsonify({"error": f"Internal server error during processing: {str(e)}"}), 500
    
    return jsonify({"error": "File type not allowed"}), 400


@bp.route('/ask', methods=['POST'])
def ask_question():
    """Handles user questions and returns the RAG-generated answer."""
    data = request.get_json()
    query = data.get('question')

    if not query:
        return jsonify({"error": "No question provided"}), 400

    log_activity("QUESTION", query)
    
    # Check if the FAISS index exists before querying
    if not os.path.exists(FAISS_INDEX_PATH):
        return jsonify({
            "answer": "Please upload an insurance policy PDF first to create the searchable index."
        })

    # Get answer from the RAG system
    answer = get_contextual_answer(query)
    
    log_activity("RESPONSE", answer[:100] + "...") # Log first 100 chars

    return jsonify({"answer": answer})