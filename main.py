# app/main.py

import os
from flask import Flask
from routes import bp as main_blueprint
from config import UPLOAD_FOLDER

def create_app():
    """Factory function to create and configure the Flask app."""
    app = Flask(__name__)
    
    # Configure file uploads
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    
    # Register blueprints (routes)
    app.register_blueprint(main_blueprint)

    # Ensure upload directory exists
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    
    return app

if __name__ == '__main__':
    # Add project root to path for imports
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    app = create_app()
    # Run in debug mode for development
    print(f"App running at http://127.0.0.1:5000")
    app.run(debug=True, host='0.0.0.0')