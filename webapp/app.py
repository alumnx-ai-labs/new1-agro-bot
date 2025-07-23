from flask import Flask, render_template, request, jsonify
import requests
import json
import os
import base64
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuration
CLOUD_FUNCTION_URL = os.getenv('CLOUD_FUNCTION_URL', 'http://localhost:8080')  # For local testing

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze():
    """Main API endpoint for frontend"""
    try:
        data = request.get_json()
        
        # Validate input
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        input_type = data.get('inputType')
        if not input_type:
            return jsonify({'error': 'inputType is required'}), 400
        
        logger.info(f"Received analysis request: {input_type}")
        
        # Call Cloud Function
        response = requests.post(
            f'{CLOUD_FUNCTION_URL}/farmer_assistant',
            json=data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            logger.info(f"Analysis successful: {result.get('session_id')}")
            return jsonify(result)
        else:
            logger.error(f"Cloud function error: {response.status_code} - {response.text}")
            return jsonify({
                'error': 'Analysis service unavailable',
                'details': response.text
            }), response.status_code
            
    except requests.exceptions.Timeout:
        logger.error("Request timeout")
        return jsonify({'error': 'Request timeout. Please try again.'}), 504
        
    except Exception as e:
        logger.error(f"Analysis endpoint error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/session/<session_id>')
def get_session(session_id):
    """Get session details (for debugging)"""
    try:
        # In a real app, you'd query Firestore directly
        # For now, return a simple response
        return jsonify({
            'session_id': session_id,
            'status': 'This endpoint will show session details in full implementation'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health():
    """Health check endpoint"""
    try:
        # Test connection to Cloud Function
        response = requests.get(f'{CLOUD_FUNCTION_URL}/health_check', timeout=5)
        
        if response.status_code == 200:
            return jsonify({
                'status': 'healthy',
                'cloud_function': 'connected',
                'services': response.json()
            })
        else:
            return jsonify({
                'status': 'unhealthy',
                'cloud_function': 'disconnected'
            }), 503
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)