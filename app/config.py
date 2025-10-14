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
    SENDER_EMAIL = "sounaksarkar45@gmail.com"
    SENDER_PASSWORD = "iivx kxep xqqv jlns"
    RECEIVER_EMAIL = "sounaksarkar47@gmail.com"