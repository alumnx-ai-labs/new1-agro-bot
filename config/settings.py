# config/settings.py
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
    GEMINI_PRO_MODEL = "gemini-2.5-flash"
    GEMINI_FLASH_MODEL = "gemini-2.5-flash-lite"
    
    # Vector Search Settings (Google AI)
    VECTOR_SEARCH_ENDPOINT = os.getenv('VECTOR_SEARCH_ENDPOINT')
    DEPLOYED_INDEX_ID = os.getenv('DEPLOYED_INDEX_ID', 'government_schemes_index')
    EMBEDDING_MODEL = "textembedding-gecko@003"
    
    # App Settings
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    ENABLE_RESPONSE_LOGGING = os.getenv('ENABLE_RESPONSE_LOGGING', 'true').lower() == 'true'
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        # Only validate if PROJECT_ID is actually needed
        if not cls.PROJECT_ID:
            print("Warning: GOOGLE_CLOUD_PROJECT not set. Some features may be limited.")
            # Don't raise error - allow local development
        
        # Warn about optional but recommended variables
        optional_vars = ['VECTOR_SEARCH_ENDPOINT']
        for var in optional_vars:
            if not getattr(cls, var, None):
                print(f"Info: {var} not set. Vector search functionality will be limited.")
        
        return True

# Validate config on import
Config.validate()