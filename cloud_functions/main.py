import functions_framework
import json
import logging
from flask import Request
from agents.manager import ManagerAgent
from utils.firestore_client import FirestoreClient

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize components
manager_agent = ManagerAgent()
firestore_client = FirestoreClient()

@functions_framework.http
def farmer_assistant(request: Request):
    """
    Main Cloud Function entry point for the Farmer Assistant MVP
    """
    
    # Handle CORS
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': '3600'
        }
        return ('', 204, headers)
    
    # Set CORS headers for actual request
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Content-Type': 'application/json'
    }
    
    if request.method != 'POST':
        return json.dumps({'error': 'Only POST method allowed'}), 405, headers
    
    try:
        # Parse request
        request_data = request.get_json()
        
        if not request_data:
            return json.dumps({'error': 'No JSON data provided'}), 400, headers
        
        # Validate required fields
        required_fields = ['inputType', 'content']
        for field in required_fields:
            if field not in request_data:
                return json.dumps({'error': f'Missing required field: {field}'}), 400, headers
        
        # Extract data
        input_type = request_data.get('inputType')
        content = request_data.get('content')
        user_id = request_data.get('userId', 'anonymous')
        language = request_data.get('language', 'en')
        
        logger.info(f"Processing request: type={input_type}, user={user_id}")
        
        # Process different input types
        processed_input = process_input(input_type, content, language)
        
        # Create session
        session_id = firestore_client.create_session(user_id, processed_input)
        
        # Process through manager agent
        result = manager_agent.process_request(session_id, processed_input)
        
        logger.info(f"Request processed successfully: {session_id}")
        
        return json.dumps(result), 200, headers
        
    except Exception as e:
        logger.error(f"Request processing failed: {e}")
        
        error_response = {
            'error': str(e),
            'status': 'error'
        }
        
        return json.dumps(error_response), 500, headers

def process_input(input_type: str, content: str, language: str) -> dict:
    """Process different types of input"""
    
    if input_type == 'image':
        # For MVP, assume content is base64 image data
        return {
            'type': 'image',
            'image_data': content,
            'language': language
        }
    
    elif input_type == 'text':
        return {
            'type': 'text',
            'text': content,
            'language': language
        }
    
    else:
        raise ValueError(f"Unsupported input type: {input_type}")

# Health check endpoint
@functions_framework.http
def health_check(request: Request):
    """Health check endpoint"""
    
    headers = {'Access-Control-Allow-Origin': '*', 'Content-Type': 'application/json'}
    
    try:
        # Test connections
        gemini_ok = manager_agent.gemini_client.test_connection()
        firestore_ok = firestore_client.test_connection()
        
        status = {
            'status': 'healthy' if (gemini_ok and firestore_ok) else 'unhealthy',
            'services': {
                'gemini': 'ok' if gemini_ok else 'error',
                'firestore': 'ok' if firestore_ok else 'error'
            },
            'timestamp': firestore_ok.SERVER_TIMESTAMP   # needs fixing.
        }
        
        return json.dumps(status), 200, headers
        
    except Exception as e:
        error_status = {
            'status': 'error',
            'error': str(e)
        }
        return json.dumps(error_status), 500, headers