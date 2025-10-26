# app/utils/logger.py

import logging

# Configure a basic logger
logging.basicConfig(
    filename='app_activity.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def log_activity(activity_type: str, details: str):
    """Logs user questions, uploads, and model responses."""
    if activity_type == "QUESTION":
        logging.info(f"USER_QUESTION: {details}")
    elif activity_type == "RESPONSE":
        logging.info(f"MODEL_RESPONSE: {details}")
    elif activity_type == "UPLOAD":
        logging.info(f"FILE_UPLOADED: {details}")
    else:
        logging.info(f"ACTIVITY: {activity_type} - {details}")