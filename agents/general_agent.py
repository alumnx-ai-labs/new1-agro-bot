# agents/general_agent.py
import json
import logging
from typing import Dict, Any
from utils.gemini_client import GeminiClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GeneralAgent:
    """
    General purpose agent for farming queries with farm settings personalization
    """
    
    def __init__(self):
        self.gemini_client = GeminiClient()
        logger.info("GeneralAgent initialized")
    
    def query(self, user_query: str, farm_settings: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Process general farming query with personalized farm context
        
        Args:
            user_query: The user's farming question
            farm_settings: Farmer's specific settings and context
            
        Returns:
            Dict with response and metadata
        """
        
        try:
            # Create personalized response prompt
            prompt = self.create_personalized_prompt(user_query, farm_settings)
            
            # Generate response using Gemini Pro for comprehensive advice
            response = self.gemini_client.generate_text_pro(prompt)
            
            # Parse structured response
            try:
                cleaned_response = self.clean_json_response(response)
                structured_response = json.loads(cleaned_response)
                
                return {
                    'type': 'general_response',
                    'message': structured_response.get('answer', response),
                    'advice': structured_response.get('advice', []),
                    'recommendations': structured_response.get('recommendations', []),
                    'next_steps': structured_response.get('next_steps', []),
                    'confidence': structured_response.get('confidence', 'medium'),
                    'agent': 'general_agent',
                    'personalized': bool(farm_settings)
                }
                
            except json.JSONDecodeError:
                # Fallback to plain text response
                logger.warning("Could not parse JSON response, using plain text")
                
                return {
                    'type': 'general_response',
                    'message': response,
                    'agent': 'general_agent',
                    'personalized': bool(farm_settings),
                    'note': 'Structured response not available'
                }
                
        except Exception as e:
            logger.error(f"General query processing failed: {e}")
            
            return {
                'type': 'error',
                'message': f'Sorry, I had trouble processing your farming question: {str(e)}',
                'agent': 'general_agent'
            }
    
    def create_personalized_prompt(self, user_query: str, farm_settings: Dict[str, Any] = None) -> str:
        """Create a personalized prompt based on farm settings"""
        
        # Base prompt without personalization
        if not farm_settings:
            prompt = f"""
            You are Dr. AgriExpert, a leading agricultural advisor specializing in Indian farming practices.
            
            FARMER'S QUESTION: {user_query}
            
            Provide comprehensive farming advice in JSON format:
            {{
                "answer": "Direct answer to the farmer's question",
                "advice": [
                    "Practical advice point 1",
                    "Practical advice point 2"
                ],
                "recommendations": [
                    "Specific recommendation 1",
                    "Specific recommendation 2"
                ],
                "next_steps": [
                    "Immediate action 1",
                    "Follow-up action 2"
                ],
                "confidence": "high/medium/low"
            }}
            
            Guidelines:
            - Use simple language that farmers understand
            - Provide actionable advice
            - Consider Indian climate and farming conditions
            - Include cost-effective solutions
            
            CRITICAL: Return ONLY the JSON object. No markdown formatting.
            """
        else:
            # Personalized prompt with farm context
            farm_context = self.build_farm_context(farm_settings)
            
            prompt = f"""
            You are Dr. AgriExpert, a leading agricultural advisor specializing in Indian farming practices.
            
            FARMER'S PROFILE:
            {farm_context}
            
            FARMER'S QUESTION: {user_query}
            
            Provide PERSONALIZED farming advice based on the farmer's specific context in JSON format:
            {{
                "answer": "Direct answer personalized to farmer's context",
                "advice": [
                    "Advice specific to their crop/farm situation",
                    "Recommendations considering their current stage"
                ],
                "recommendations": [
                    "Specific to their soil type and crop",
                    "Considering their acreage and resources"
                ],
                "next_steps": [
                    "Immediate actions for their current stage",
                    "Timeline-based follow-up actions"
                ],
                "seasonal_guidance": "Advice for current season/stage",
                "cost_estimate": "Estimated costs in Indian Rupees",
                "confidence": "high/medium/low"
            }}
            
            PERSONALIZATION GUIDELINES:
            - Address farmer by name if provided
            - Reference their specific crop type and current stage
            - Consider their acreage for scaling recommendations
            - Account for their soil type in advice
            - Address their current challenges specifically
            - Provide timeline-based guidance
            - Use their preferred language tone
            
            CRITICAL: Return ONLY the JSON object. No markdown formatting.
            """
        
        return prompt
    
    def build_farm_context(self, farm_settings: Dict[str, Any]) -> str:
        """Build a readable farm context from settings"""
        
        context_parts = []
        
        # Farmer details
        if farm_settings.get('farmerName'):
            context_parts.append(f"Farmer Name: {farm_settings['farmerName']}")
        
        # Crop information
        if farm_settings.get('cropType'):
            context_parts.append(f"Crop: {farm_settings['cropType']}")
        
        if farm_settings.get('acreage'):
            context_parts.append(f"Farm Size: {farm_settings['acreage']} acres")
        
        if farm_settings.get('soilType'):
            context_parts.append(f"Soil Type: {farm_settings['soilType']}")
        
        # Crop stage and timing
        if farm_settings.get('sowingDate'):
            context_parts.append(f"Sowing Date: {farm_settings['sowingDate']}")
        
        if farm_settings.get('currentStage'):
            context_parts.append(f"Current Growth Stage: {farm_settings['currentStage']}")
        
        # Current challenges
        if farm_settings.get('currentChallenges'):
            context_parts.append(f"Current Challenges: {farm_settings['currentChallenges']}")
        
        # Language preferences
        if farm_settings.get('preferredLanguages'):
            languages = ', '.join(farm_settings['preferredLanguages'])
            context_parts.append(f"Preferred Languages: {languages}")
        
        return '\n'.join(context_parts) if context_parts else "No specific farm context provided"
    
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