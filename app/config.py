import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    HOSPITAL_API_BASE_URL = os.environ.get("HOSPITAL_API_BASE_URL", "https://hospital-directory.onrender.com")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///app.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CSV_ROWS = int(os.environ.get("MAX_CSV_ROWS", 20))
    # Adjust based on server capacity
    MAX_CONCURRENT_REQUESTS = int(os.environ.get("MAX_CONCURRENT_REQUESTS", 10))

    API_TITLE = "Hospital Bulk Processor API"
    API_VERSION = "v1"
    OPENAPI_VERSION = "3.0.2"
    OPENAPI_URL_PREFIX = "/"
    OPENAPI_SWAGGER_UI_PATH = "/docs"
    OPENAPI_SWAGGER_UI_URL = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
