import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Google Cloud Settings
    PROJECT_ID = os.getenv('GOOGLE_CLOUD_PROJECT')
    REGION = os.getenv('GOOGLE_CLOUD_REGION', 'us-central1')
    
    # Firestore Settings
    FIRESTORE_DATABASE = os.getenv('FIRESTORE_DATABASE', '(default)')
    
    # Gemini Model Settings
    GEMINI_PRO_MODEL = "gemini-1.5-pro"
    GEMINI_FLASH_MODEL = "gemini-1.5-flash"
    
    # App Settings
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        if not cls.PROJECT_ID:
            raise ValueError("GOOGLE_CLOUD_PROJECT environment variable is required")
        return True

# Validate config on import
Config.validate()
