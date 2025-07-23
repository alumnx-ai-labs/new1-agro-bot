
import json
import logging
from typing import Dict, Any
from utils.gemini_client import GeminiClient
from utils.firestore_client import FirestoreClient
from agents.disease_detection import DiseaseDetectionAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ManagerAgent:
    """
    The orchestrator agent that manages all other agents
    """
    
    def __init__(self):
        self.gemini_client = GeminiClient()
        self.firestore_client = FirestoreClient()
        
        # Initialize available agents
        self.disease_agent = DiseaseDetectionAgent()
        
        # Agent registry for easy expansion
        self.agents = {
            'disease_detection': self.disease_agent,
            # Future agents will be added here
        }
        
        logger.info("ManagerAgent initialized with available agents: disease_detection")
    
    def classify_intent(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Classify user intent using Gemini Flash"""
        
        # Create classification prompt
        classification_prompt = f"""
        You are an AI assistant helping Indian farmers. Analyze this input and classify the intent.
        
        Available categories:
        1. "disease_detection" - Image of plant/crop with disease, pest, or health issues
        2. "general_query" - Any other farming question (for now, we'll handle this simply)
        
        Input Data: {json.dumps(input_data, indent=2)}
        
        Rules:
        - If there's an image, it's likely disease_detection
        - If text mentions diseases, pests, problems with crops, it's disease_detection
        - Everything else is general_query for now
        
        Respond ONLY with valid JSON in this format:
        {{
            "intent": "disease_detection",
            "confidence": 0.95,
            "reasoning": "Image provided showing plant with visible issues",
            "entities": {{
                "has_image": true,
                "crop_mentioned": "tomato",
                "problem_type": "disease"
            }}
        }}
        """
        
        try:
            response = self.gemini_client.generate_text_flash(classification_prompt)
            
            # Try to parse JSON response
            classification = json.loads(response)
            
            # Validate required fields
            if 'intent' not in classification:
                raise ValueError("Missing 'intent' field in classification")
            
            logger.info(f"Intent classified: {classification['intent']} (confidence: {classification.get('confidence', 'unknown')})")
            return classification
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse classification JSON: {e}")
            logger.error(f"Raw response: {response}")
            
            # Fallback classification
            fallback = {
                "intent": "disease_detection" if input_data.get('image_data') else "general_query",
                "confidence": 0.5,
                "reasoning": "Fallback classification due to JSON parsing error",
                "entities": {},
                "error": "Classification parsing failed"
            }
            return fallback
            
        except Exception as e:
            logger.error(f"Classification failed: {e}")
            return {
                "intent": "general_query",
                "confidence": 0.1,
                "reasoning": "Error in classification",
                "entities": {},
                "error": str(e)
            }
    
    def process_request(self, session_id: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Main orchestration method"""
        
        try:
            # Add initial manager thought
            self.firestore_client.add_manager_thought(
                session_id, 
                "🤔 Analyzing your request..."
            )
            
            # Classify the intent
            classification = self.classify_intent(input_data)
            
            self.firestore_client.add_manager_thought(
                session_id,
                f"🎯 Identified intent: {classification['intent']} "
                f"(confidence: {classification.get('confidence', 'unknown')})"
            )
            
            # Route to appropriate agent
            intent = classification['intent']
            agent_response = None
            
            if intent == 'disease_detection':
                self.firestore_client.add_manager_thought(
                    session_id,
                    "🔬 Calling disease detection specialist..."
                )
                
                agent_response = self.disease_agent.analyze(
                    input_data, 
                    classification.get('entities', {})
                )
                
            else:  # general_query or fallback
                self.firestore_client.add_manager_thought(
                    session_id,
                    "💬 Providing general assistance..."
                )
                
                agent_response = {
                    'type': 'general_response',
                    'message': "Thank you for your question! Currently, I specialize in crop disease detection. Please share an image of your crop if you suspect any disease or pest issues.",
                    'agent': 'manager_fallback'
                }
            
            # Save agent response
            if agent_response:
                self.firestore_client.save_agent_response(
                    session_id, 
                    intent, 
                    agent_response
                )
            
            self.firestore_client.add_manager_thought(
                session_id,
                "✅ Analysis complete! Preparing response..."
            )
            
            # Create final response
            final_response = self.synthesize_response(classification, agent_response)
            
            # Update session status
            self.firestore_client.update_session_status(
                session_id, 
                'completed', 
                final_response['message']
            )
            
            logger.info(f"Request processed successfully for session: {session_id}")
            
            return {
                'session_id': session_id,
                'classification': classification,
                'agent_response': agent_response,
                'final_response': final_response,
                'status': 'success'
            }
            
        except Exception as e:
            logger.error(f"Request processing failed: {e}")
            
            # Update session with error
            self.firestore_client.update_session_status(session_id, 'error')
            self.firestore_client.add_manager_thought(
                session_id,
                f"❌ Error occurred: {str(e)}"
            )
            
            return {
                'session_id': session_id,
                'error': str(e),
                'status': 'error'
            }
    
    def synthesize_response(self, classification: Dict, agent_response: Dict) -> Dict[str, Any]:
        """Create a unified response from agent outputs"""
        
        if not agent_response:
            return {
                'message': "I couldn't process your request properly. Please try again.",
                'type': 'error'
            }
        
        # For disease detection responses
        if classification['intent'] == 'disease_detection' and agent_response.get('analysis'):
            analysis = agent_response['analysis']
            
            # Create farmer-friendly summary
            summary_parts = []
            
            if analysis.get('disease_name'):
                summary_parts.append(f"🔍 **Detected Issue**: {analysis['disease_name']}")
            
            if analysis.get('severity'):
                summary_parts.append(f"📊 **Severity**: {analysis['severity']}")
            
            if analysis.get('immediate_action'):
                summary_parts.append(f"⚡ **Immediate Action**: {analysis['immediate_action']}")
            
            if analysis.get('treatment_summary'):
                summary_parts.append(f"💊 **Treatment**: {analysis['treatment_summary']}")
            
            message = "\n\n".join(summary_parts) if summary_parts else agent_response.get('message', 'Analysis completed.')
            
            return {
                'message': message,
                'type': 'disease_analysis',
                'detailed_analysis': analysis,
                'confidence': agent_response.get('confidence', 'medium')
            }
        
        # For general responses
        return {
            'message': agent_response.get('message', 'Request processed.'),
            'type': agent_response.get('type', 'general'),
        }