# test_credentials.py
#!/usr/bin/env python3
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("🔍 Testing credentials setup...")

# Test environment variables
project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
print(f"✅ Project ID: {project_id}")

# Test credentials file
creds_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
if os.path.exists(creds_path):
    print(f"✅ Credentials file found: {creds_path}")
    
    # Check file size (should be > 1KB)
    file_size = os.path.getsize(creds_path)
    print(f"✅ Credentials file size: {file_size} bytes")
else:
    print(f"❌ Credentials file not found: {creds_path}")

# Test basic Google Cloud authentication
try:
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = creds_path
    
    # Test Vertex AI (for Gemini)
    import vertexai
    vertexai.init(project=project_id, location="us-central1")
    print("✅ Vertex AI initialized successfully")
    
except Exception as e:
    print(f"❌ Vertex AI initialization failed: {e}")

# Test Firestore connection (might fail if not set up yet)
try:
    from google.cloud import firestore
    db = firestore.Client(project=project_id)
    print("✅ Firestore client created successfully")
    
    # Try a simple operation
    test_ref = db.collection('_test').document('connection')
    test_ref.set({'test': True, 'timestamp': firestore.SERVER_TIMESTAMP})
    
    print("✅ Firestore write test successful")
    
    # Clean up
    test_ref.delete()
    print("✅ Firestore cleanup successful")
    
except Exception as e:
    print(f"⚠️  Firestore test failed (database might not be set up yet): {e}")
    print("   You can set up Firestore later through Firebase Console")

print("\n🎉 Basic setup test complete!")
