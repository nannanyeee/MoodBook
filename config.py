import os
from dotenv import load_dotenv
load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "bookocr-secret")
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
    THUMBNAIL_FOLDER = os.path.join(UPLOAD_FOLDER, "thumbnails")
    MAX_CONTENT_LENGTH = 20 * 1024 * 1024  # 20MB
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(BASE_DIR, "app.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    OCR_ENGINES = ["tesseract", "easyocr"]

