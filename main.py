# cloud_functions/main.py
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
def new_farmer_assistant(request: Request):
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
        query_type = request_data.get('queryType')  # New field for scheme queries
        text_description = request_data.get('textDescription', '')  # For disease detection context
        farm_settings = request_data.get('farmSettings', {})  # Farm personalization context

        logger.info(f"Processing request: type={input_type}, user={user_id}, queryType={query_type}")

        # Process different input types
        processed_input = process_input(input_type, content, language, query_type, text_description, farm_settings)
        
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

def process_input(input_type: str, content: str, language: str, query_type: str = None, text_description: str = '', farm_settings: dict = None) -> dict:
    """Process different types of input"""
    
    if input_type == 'image':
        # For crop disease detection
        return {
            'type': 'image',
            'image_data': content,
            'language': language,
            'text': text_description,  # Additional context for disease detection
            'input_type': input_type,
            'farm_settings': farm_settings
        }
    
    elif input_type == 'audio':
        # For speech-to-text
        return {
            'type': 'audio',
            'audio_data': content,
            'language': language,
            'input_type': input_type,
            'farm_settings': farm_settings
        }
    
    elif input_type == 'text':
        # For text queries (including government schemes)
        processed = {
            'type': 'text',
            'text': content,
            'content': content,  # Alias for compatibility
            'language': language,
            'input_type': input_type,
            'farm_settings': farm_settings
        }
        
        # Add query type if specified (helps with routing)
        if query_type:
            processed['queryType'] = query_type
        
        return processed
    
    else:
        raise ValueError(f"Unsupported input type: {input_type}")

# Health check endpoint
@functions_framework.http
def health_check(request: Request):
    """Health check endpoint"""
    
    # Handle CORS preflight
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': '3600'
        }
        return ('', 204, headers)
    
    headers = {'Access-Control-Allow-Origin': '*', 'Content-Type': 'application/json'}
    
    try:
        # Test connections
        gemini_ok = manager_agent.gemini_client.test_connection()
        firestore_ok = firestore_client.test_connection()
        
        # Test vector store connection if RAG agent is available
        vector_store_ok = True
        try:
            if hasattr(manager_agent, 'rag_agent') and manager_agent.rag_agent:
                vector_store_ok = manager_agent.rag_agent.vector_store_client.test_connection() if manager_agent.rag_agent.vector_search_available else True
            else:
                vector_store_ok = None  # Not applicable
        except Exception as e:
            logger.warning(f"Vector store test failed: {e}")
            vector_store_ok = False
        
        # Determine overall health
        all_healthy = gemini_ok and firestore_ok and (vector_store_ok is not False)
        
        services_status = {
            'gemini': 'ok' if gemini_ok else 'error',
            'firestore': 'ok' if firestore_ok else 'error',
        }
        
        if vector_store_ok is not None:
            services_status['vector_store'] = 'ok' if vector_store_ok else 'error'
        else:
            services_status['vector_store'] = 'not_configured'
        
        # Determine available capabilities
        capabilities = ['crop_disease_detection']
        if hasattr(manager_agent, 'rag_agent') and manager_agent.rag_agent:
            capabilities.append('government_schemes_query')
        
        status = {
            'status': 'healthy' if all_healthy else 'unhealthy',
            'services': services_status,
            'timestamp': firestore_client.get_server_timestamp(),
            'capabilities': capabilities
        }
        
        return json.dumps(status), 200, headers
        
    except Exception as e:
        error_status = {
            'status': 'error',
            'error': str(e),
            'timestamp': firestore_client.get_server_timestamp()
        }
        return json.dumps(error_status), 500, headers

# Data ingestion endpoint (for admin use)
@functions_framework.http
def ingest_schemes_data(request: Request):
    """Admin endpoint to ingest government schemes data"""
    
    # Handle CORS
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
            'Access-Control-Max-Age': '3600'
        }
        return ('', 204, headers)
    
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Content-Type': 'application/json'
    }
    
    if request.method != 'POST':
        return json.dumps({'error': 'Only POST method allowed'}), 405, headers
    
    try:
        # Simple admin authentication (in production, use proper auth)
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer admin_'):
            return json.dumps({'error': 'Unauthorized'}), 401, headers
        
        # Import and run data ingestion
        from scripts.ingest_schemes_data import SchemesDataIngestion
        
        ingestion = SchemesDataIngestion()
        
        # Get request parameters
        request_data = request.get_json() or {}
        ingestion_type = request_data.get('type', 'sample')  # 'sample' or 'file'
        
        if ingestion_type == 'sample':
            success = ingestion.ingest_sample_data()
        else:
            file_path = request_data.get('file_path')
            if not file_path:
                return json.dumps({'error': 'file_path required for file ingestion'}), 400, headers
            success = ingestion.ingest_from_json_file(file_path)
        
        if success:
            # Verify ingestion
            ingestion.verify_ingestion()
            
            result = {
                'status': 'success',
                'message': f'{ingestion_type} data ingestion completed successfully',
                'ingestion_type': ingestion_type
            }
            return json.dumps(result), 200, headers
        else:
            return json.dumps({
                'status': 'error',
                'message': 'Data ingestion failed'
            }), 500, headers
            
    except Exception as e:
        logger.error(f"Data ingestion failed: {e}")
        return json.dumps({
            'status': 'error',
            'error': str(e)
        }), 500, headers