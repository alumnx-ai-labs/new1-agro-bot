# agents/price_agent.py
import json
import logging
import os
from typing import Dict, Any, List
from datetime import datetime, timedelta
from utils.gemini_client import GeminiClient
from vertexai.preview import agent_builder

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PriceAgent:
    """
    Market Price Agent using Vertex AI Agent Builder for crop price information
    """
    
    def __init__(self):
        self.gemini_client = GeminiClient()
        
        # Try to initialize Vertex AI Agent Builder
        try:
            self.project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
            self.location = os.getenv('GOOGLE_CLOUD_REGION', 'us-central1')
            
            # Initialize Agent Builder client
            self.agent_client = agent_builder.AgentBuilderClient()
            self.agent_app_id = os.getenv('PRICE_AGENT_APP_ID', 'farmer-price-assistant')
            
            # Load price data
            self.price_data = self.load_price_data()
            
            self.agent_builder_available = True
            logger.info("PriceAgent initialized with Vertex AI Agent Builder")
            
        except Exception as e:
            logger.warning(f"Vertex AI Agent Builder not available: {e}")
            self.agent_builder_available = False
            self.price_data = self.load_price_data()
            logger.info("PriceAgent initialized in fallback mode")
    
    def load_price_data(self) -> Dict[str, Any]:
        """Load crop price data from JSON file"""
        try:
            # Try to load from data directory
            data_file_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'crop_prices.json')
            
            if os.path.exists(data_file_path):
                with open(data_file_path, 'r', encoding='utf-8') as file:
                    return json.load(file)
            else:
                logger.warning("Price data file not found, using fallback data")
                return self.get_fallback_price_data()
                
        except Exception as e:
            logger.error(f"Error loading price data: {e}")
            return self.get_fallback_price_data()
    
    def get_fallback_price_data(self) -> Dict[str, Any]:
        """Fallback price data if file is not available"""
        return {
            "last_updated": datetime.now().isoformat(),
            "crops": {
                "rice": {
                    "name": "Rice (Paddy)",
                    "unit": "quintal",
                    "current_price": 2150,
                    "currency": "INR"
                },
                "wheat": {
                    "name": "Wheat",
                    "unit": "quintal", 
                    "current_price": 2300,
                    "currency": "INR"
                }
            }
        }
    
    def analyze_price_query(self, input_data: Dict[str, Any], entities: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze user query for crop price information"""
        
        try:
            # Extract query text
            query_text = input_data.get('text', input_data.get('content', ''))
            
            if self.agent_builder_available:
                return self.process_with_agent_builder(query_text, entities)
            else:
                return self.process_with_fallback(query_text, entities)
                
        except Exception as e:
            logger.error(f"Price query analysis failed: {e}")
            return {
                'type': 'error',
                'message': f'Sorry, I had trouble finding price information: {str(e)}',
                'agent': 'price_agent'
            }
    
    def process_with_agent_builder(self, query: str, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Process query using Vertex AI Agent Builder"""
        
        try:
            # Create conversation request for Agent Builder
            conversation_request = {
                'query': {
                    'text': query
                },
                'conversation_id': f"price_query_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'user_pseudo_id': entities.get('user_id', 'anonymous'),
                'user_info': {
                    'user_agent': 'farmer-assistant'
                }
            }
            
            # Add crop price data as context
            context_data = self.prepare_context_data(query)
            if context_data:
                conversation_request['query']['context'] = context_data
            
            # Call Agent Builder
            parent = f"projects/{self.project_id}/locations/{self.location}/agents/{self.agent_app_id}"
            
            response = self.agent_client.converse_conversation(
                parent=parent,
                query=conversation_request['query'],
                conversation_id=conversation_request['conversation_id']
            )
            
            # Process Agent Builder response
            return self.process_agent_builder_response(response, query)
            
        except Exception as e:
            logger.error(f"Agent Builder processing failed: {e}")
            # Fallback to direct Gemini processing
            return self.process_with_fallback(query, entities)
    
    def process_with_fallback(self, query: str, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Process query using direct Gemini with price data"""
        
        # Prepare context from price data
        context = self.prepare_context_data(query)
        
        # Create comprehensive prompt
        prompt = f"""
        You are a market price expert helping Indian farmers with crop price information.
        
        USER QUERY: {query}
        
        AVAILABLE PRICE DATA:
        {json.dumps(context, indent=2)}
        
        TASK:
        Analyze the user's query and provide relevant crop price information based on the available data.
        
        RESPONSE FORMAT (JSON only):
        {{
            "price_analysis": {{
                "crop_found": "rice/wheat/tomato etc or null if not found",
                "current_price": 2150,
                "unit": "quintal",
                "currency": "INR",
                "price_trend": "increasing/decreasing/stable",
                "market_outlook": "Brief outlook based on data"
            }},
            "answer": "Comprehensive answer about the crop prices",
            "recommendations": [
                "When to sell for better prices",
                "Market timing suggestions"
            ],
            "additional_info": "Any relevant market information"
        }}
        
        INSTRUCTIONS:
        1. Focus on the specific crop mentioned in the query
        2. Provide current prices with units (per quintal, per kg, etc.)
        3. Include historical trend analysis if data available
        4. Give practical advice for farmers
        5. Use simple language farmers can understand
        6. If no specific crop mentioned, provide general market overview
        
        CRITICAL: Return ONLY the JSON object. No markdown formatting.
        """
        
        try:
            response_text = self.gemini_client.generate_text_flash(prompt)
            cleaned_response = self.clean_json_response(response_text)
            response_data = json.loads(cleaned_response)
            
            return {
                'type': 'price_analysis',
                'message': response_data.get('answer', 'Price information processed'),
                'price_data': response_data.get('price_analysis', {}),
                'recommendations': response_data.get('recommendations', []),
                'additional_info': response_data.get('additional_info', ''),
                'agent': 'price_agent_fallback',
                'data_source': 'local_database'
            }
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse price response JSON: {e}")
            return {
                'type': 'price_analysis',
                'message': response_text if len(response_text) > 10 else "I can help you with crop price information. Please specify which crop you're interested in.",
                'price_data': {},
                'recommendations': [],
                'agent': 'price_agent_fallback'
            }
    
    def prepare_context_data(self, query: str) -> Dict[str, Any]:
        """Prepare relevant price data based on query"""
        
        query_lower = query.lower()
        
        # Extract mentioned crops from query
        mentioned_crops = []
        for crop_key in self.price_data.get('crops', {}).keys():
            if crop_key in query_lower or self.price_data['crops'][crop_key]['name'].lower() in query_lower:
                mentioned_crops.append(crop_key)
        
        # If no specific crop mentioned, include all data
        if not mentioned_crops:
            return self.price_data
        
        # Return data for mentioned crops only
        filtered_data = {
            'last_updated': self.price_data.get('last_updated'),
            'crops': {crop: self.price_data['crops'][crop] for crop in mentioned_crops if crop in self.price_data['crops']}
        }
        
        return filtered_data
    
    def process_agent_builder_response(self, response, query: str) -> Dict[str, Any]:
        """Process response from Vertex AI Agent Builder"""
        
        try:
            # Extract response text
            response_text = response.reply.summary.summary_text if hasattr(response, 'reply') else str(response)
            
            # Extract any structured data if available
            price_info = self.extract_price_info_from_response(response_text)
            
            return {
                'type': 'price_analysis',
                'message': response_text,
                'price_data': price_info,
                'agent': 'price_agent_vertex_ai',
                'conversation_id': getattr(response, 'conversation_id', None),
                'data_source': 'vertex_ai_agent_builder'
            }
            
        except Exception as e:
            logger.error(f"Error processing Agent Builder response: {e}")
            return {
                'type': 'error',
                'message': 'Price information processed but response formatting failed',
                'agent': 'price_agent_vertex_ai'
            }
    
    def extract_price_info_from_response(self, response_text: str) -> Dict[str, Any]:
        """Extract structured price information from response text"""
        
        # Simple extraction logic - can be enhanced with NER
        price_info = {}
        
        # Look for price patterns (₹1000, Rs. 2000, etc.)
        import re
        price_patterns = re.findall(r'₹\s*(\d+(?:,\d+)*(?:\.\d+)?)', response_text)
        if not price_patterns:
            price_patterns = re.findall(r'Rs\.?\s*(\d+(?:,\d+)*(?:\.\d+)?)', response_text)
        
        if price_patterns:
            # Remove commas and convert to float
            prices = [float(p.replace(',', '')) for p in price_patterns]
            price_info['mentioned_prices'] = prices
            price_info['primary_price'] = prices[0] if prices else None
        
        return price_info
    
    def clean_json_response(self, response: str) -> str:
        """Clean JSON response by removing markdown wrappers"""
        import re
        
        # Remove markdown wrappers
        cleaned = re.sub(r'^```json\s*', '', response.strip(), flags=re.MULTILINE)
        cleaned = re.sub(r'\s*```$', '', cleaned.strip(), flags=re.MULTILINE)
        
        # Try to find a complete JSON object
        if not cleaned.strip().startswith('{'):
            start_idx = cleaned.find('{')
            if start_idx != -1:
                cleaned = cleaned[start_idx:]
        
        return cleaned.strip()
    
    def get_supported_crops(self) -> List[str]:
        """Get list of supported crops"""
        return list(self.price_data.get('crops', {}).keys())
    
    def get_crop_info(self, crop_name: str) -> Dict[str, Any]:
        """Get specific crop price information"""
        crop_name_lower = crop_name.lower()
        
        # Direct match
        if crop_name_lower in self.price_data.get('crops', {}):
            return self.price_data['crops'][crop_name_lower]
        
        # Search in crop display names
        for crop_key, crop_data in self.price_data.get('crops', {}).items():
            if crop_name_lower in crop_data.get('name', '').lower():
                return crop_data
        
        return None