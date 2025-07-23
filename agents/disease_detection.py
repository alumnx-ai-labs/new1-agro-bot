# agents/disease_detection.py
import json
import logging
from typing import Dict, Any
from utils.gemini_client import GeminiClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DiseaseDetectionAgent:
    """
    Specialized agent for crop disease detection and treatment advice
    """
    
    def __init__(self):
        self.gemini_client = GeminiClient()
        logger.info("DiseaseDetectionAgent initialized")
    
    def analyze(self, input_data: Dict[str, Any], entities: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze crop disease from image and/or text description"""
        
        # Check if we have an image to analyze
        if not input_data.get('image_data'):
            return {
                'type': 'error',
                'message': 'Please provide an image of your crop for disease detection.',
                'agent': 'disease_detection'
            }
        
        try:
            # Create comprehensive analysis prompt
            analysis_prompt = self.create_analysis_prompt(input_data, entities)
            
            # Analyze image using Gemini Pro Vision with retry logic
            max_retries = 2
            for attempt in range(max_retries):
                analysis_result = self.gemini_client.analyze_image(
                    analysis_prompt, 
                    input_data['image_data']
                )
                
                # Check if response seems complete
                if len(analysis_result) > 100 and analysis_result.strip().endswith('}'):
                    break
                
                logger.warning(f"Attempt {attempt + 1}: Response seems incomplete, retrying...")
                
                if attempt == max_retries - 1:
                    logger.error(f"Final response after {max_retries} attempts: {analysis_result}")
                        
                        # Try to parse structured response
            try:
                # Clean JSON response (remove markdown wrappers)
                cleaned_response = self.clean_json_response(analysis_result)
                structured_response = json.loads(cleaned_response)
                
                # Validate and enhance response
                enhanced_response = self.enhance_response(structured_response)
                
                return {
                    'type': 'disease_analysis',
                    'analysis': enhanced_response,
                    'raw_response': analysis_result,
                    'agent': 'disease_detection',
                    'confidence': enhanced_response.get('confidence', 'medium')
                }
                
            except json.JSONDecodeError:
                # If JSON parsing fails, create structured response from plain text
                logger.warning("Could not parse JSON response, creating structured fallback")
                
                fallback_response = self.create_fallback_response(analysis_result)
                
                return {
                    'type': 'disease_analysis',
                    'analysis': fallback_response,
                    'raw_response': analysis_result,
                    'agent': 'disease_detection',
                    'confidence': 'low',
                    'note': 'Structured analysis not available, showing general advice'
                }
                
        except Exception as e:
            logger.error(f"Disease analysis failed: {e}")
            
            return {
                'type': 'error',
                'message': f'Sorry, I had trouble analyzing the image: {str(e)}',
                'agent': 'disease_detection'
            }
    
    def create_analysis_prompt(self, input_data: Dict[str, Any], entities: Dict[str, Any]) -> str:
        """Create a comprehensive prompt for disease analysis"""
        
        # Get additional context
        text_description = input_data.get('text', input_data.get('translated_text', ''))
        location = entities.get('location', 'India')
        crop_type = entities.get('crop_mentioned', 'crop')
        
        prompt = f"""
        You are Dr. AgriExpert, a leading plant pathologist specializing in Indian agriculture.
        
        TASK: Analyze this {crop_type} image for diseases, pests, or health issues.
        
        CONTEXT:
        - Location: {location}
        - Additional description: {text_description}
        
        RESPONSE FORMAT (JSON only):
        {{
            "disease_name": "Specific disease/pest name or 'Healthy plant' if no issues",
            "confidence": "high/medium/low",
            "severity": "mild/moderate/severe/none",
            "affected_parts": ["leaves", "stem", "fruit"],
            "symptoms_observed": [
                "Yellow spots on leaves",
                "Brown patches on stem"
            ],
            "immediate_action": "Most urgent action farmer should take right now",
            "treatment_summary": "Brief treatment in simple terms",
            "organic_solutions": [
                {{
                    "name": "Neem oil spray",
                    "preparation": "5ml neem oil + 1L water",
                    "application": "Spray in evening every 3 days"
                }}
            ],
            "prevention_tips": [
                "Ensure proper drainage",
                "Regular plant inspection"
            ],
            "cost_estimate": "₹50-100 for treatment",
            "warning_signs": "When to seek urgent help",
            "success_timeline": "Expected improvement timeframe"
        }}
        
        IMPORTANT RULES:
        1. Use simple Hindi/English terms farmers understand
        2. Focus on locally available, affordable solutions
        3. Be specific about quantities and timing
        4. If plant looks healthy, say so clearly
        5. Always provide actionable advice
        6. Consider Indian climate and farming practices
        
        CRITICAL: Return ONLY the JSON object. Do not wrap in ```json or ``` blocks. Start directly with {{ and end with }}.
        """
        
        return prompt
    

    def enhance_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance and validate the structured response"""
        
        # Ensure all required fields exist
        enhanced = {
            'disease_name': response.get('disease_name', 'Unknown condition'),
            'confidence': response.get('confidence', 'medium'),
            'severity': response.get('severity', 'unknown'),
            'affected_parts': response.get('affected_parts', []),
            'symptoms_observed': response.get('symptoms_observed', []),
            'immediate_action': response.get('immediate_action', 'Monitor plant closely'),
            'treatment_summary': response.get('treatment_summary', 'Consult local agricultural expert'),
            'organic_solutions': response.get('organic_solutions', []),
            'prevention_tips': response.get('prevention_tips', []),
            'cost_estimate': response.get('cost_estimate', 'Cost varies'),
            'warning_signs': response.get('warning_signs', 'Rapid spread to other plants'),
            'success_timeline': response.get('success_timeline', '1-2 weeks with proper treatment')
        }
        
        # Add helpful defaults if lists are empty
        if not enhanced['organic_solutions']:
            enhanced['organic_solutions'] = [{
                'name': 'General care',
                'preparation': 'Maintain proper watering and sunlight',
                'application': 'Daily monitoring'
            }]
        
        if not enhanced['prevention_tips']:
            enhanced['prevention_tips'] = [
                'Regular inspection of plants',
                'Proper spacing between plants',
                'Good drainage management'
            ]
        
        return enhanced
    
    def create_fallback_response(self, raw_text: str) -> Dict[str, Any]:
        """Create a basic structured response from plain text"""
        
        return {
            'disease_name': 'Analysis available in description',
            'confidence': 'low',
            'severity': 'unknown',
            'affected_parts': [],
            'symptoms_observed': ['See detailed analysis below'],
            'immediate_action': 'Review the detailed analysis',
            'treatment_summary': raw_text[:200] + '...' if len(raw_text) > 200 else raw_text,
            'organic_solutions': [{
                'name': 'General advice',
                'preparation': 'Follow detailed analysis',
                'application': 'As described'
            }],
            'prevention_tips': ['Regular plant monitoring', 'Good agricultural practices'],
            'cost_estimate': 'Varies based on treatment needed',
            'warning_signs': 'Rapid deterioration of plant health',
            'success_timeline': 'Depends on treatment approach',
            'detailed_text': raw_text
        }
    
    def clean_json_response(self, response: str) -> str:
        """Clean and validate JSON response"""
        import re
        
        # Log the raw response for debugging
        logger.info(f"Raw response length: {len(response)}")
        logger.info(f"Raw response preview: {response[:300]}")
        
        # Remove markdown wrappers
        cleaned = re.sub(r'^```json\s*', '', response.strip(), flags=re.MULTILINE)
        cleaned = re.sub(r'\s*```$', '', cleaned.strip(), flags=re.MULTILINE)
        
        # Try to find a complete JSON object
        if not cleaned.strip().startswith('{'):
            # Look for the first { and try to extract JSON
            start_idx = cleaned.find('{')
            if start_idx != -1:
                cleaned = cleaned[start_idx:]
        
        # Check if JSON seems complete
        if not cleaned.strip().endswith('}'):
            logger.warning("JSON response appears incomplete")
            logger.warning(f"Response ends with: {cleaned[-50:]}")
        
        return cleaned.strip()