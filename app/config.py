import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploaded_data")
    ALLOWED_EXTENSIONS = {'csv'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    
    # Email settings
    SMTP_SERVER = 'smtp.gmail.com'
    SMTP_PORT = 465
    SENDER_EMAIL = os.getenv('SENDER_EMAIL')
    SENDER_PASSWORD = os.getenv('SENDER_PASSWORD')
    RECEIVER_EMAIL = os.getenv('RECEIVER_EMAIL')