# agents/manager.py
import json
import logging
import os
from typing import Dict, Any
from datetime import datetime
from utils.gemini_client import GeminiClient
from utils.firestore_client import FirestoreClient
from agents.disease_detection import DiseaseDetectionAgent
from agents.stt_agent import STTAgent
from agents.rag_agent import RAGAgent

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
        self.stt_agent = STTAgent()
        
        # Initialize RAG agent with error handling
        try:
            self.rag_agent = RAGAgent()
            rag_available = True
        except Exception as e:
            logger.warning(f"RAG agent initialization failed: {e}")
            self.rag_agent = None
            rag_available = False
        
        # Agent registry for easy expansion
        self.agents = {
            'disease_detection': self.disease_agent,
            'speech_to_text': self.stt_agent,
        }
        
        if rag_available:
            self.agents['government_schemes'] = self.rag_agent
        
        available_agents = list(self.agents.keys())
        logger.info(f"ManagerAgent initialized with agents: {', '.join(available_agents)}")
    
    def classify_intent(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Classify user intent using Gemini Flash"""
        
        # Create classification prompt
        classification_prompt = f"""
        You are an AI assistant helping Indian farmers. Analyze this input and classify the intent.
        
        Available categories:
        1. "disease_detection" - Image of plant/crop with disease, pest, or health issues
        2. "government_schemes" - Questions about government schemes, subsidies, loans, policies for farmers
        3. "speech_to_text" - Audio file for transcription
        4. "general_query" - Any other farming question
        
        Input Data: {json.dumps(input_data, indent=2)}
        
        Classification Rules:
        - If there's audio data (audio_data present), classify as "speech_to_text"
        - If there's an image (image_data present), it's likely "disease_detection"
        - If queryType is "government_schemes", classify as "government_schemes"
        - If text mentions schemes, subsidies, loans, policies, PM-KISAN, government support, etc., classify as "government_schemes"
        - If text mentions diseases, pests, problems with crops, classify as "disease_detection"
        - Everything else is "general_query"
                
        Respond with ONLY valid JSON (no markdown, no code blocks) in this format:
        {{
            "intent": "government_schemes",
            "confidence": 0.95,
            "reasoning": "User is asking about government subsidies for farmers",
            "entities": {{
                "has_image": false,
                "query_type": "schemes",
                "crop_mentioned": "rice",
                "scheme_type": "subsidy"
            }}
        }}
        """
        
        try:
            response = self.gemini_client.generate_text_flash(classification_prompt)
            
            # Clean JSON response (remove markdown wrappers)
            cleaned_response = self.clean_json_response(response)
            
            # Try to parse JSON response
            classification = json.loads(cleaned_response)
            
            # Validate required fields
            if 'intent' not in classification:
                raise ValueError("Missing 'intent' field in classification")
            
            logger.info(f"Intent classified: {classification['intent']} (confidence: {classification.get('confidence', 'unknown')})")
            return classification
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse classification JSON: {e}")
            logger.error(f"Raw response: {response}")
            
            # Fallback classification based on input analysis
            fallback_intent = self.fallback_classification(input_data)
            
            fallback = {
                "intent": fallback_intent,
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
    
    def fallback_classification(self, input_data: Dict[str, Any]) -> str:
        """Simple fallback classification logic"""
        
        # Check for explicit query type
        if input_data.get('queryType') == 'government_schemes':
            return 'government_schemes'
        
        # Check for image data
        if input_data.get('image_data'):
            return 'disease_detection'
        
        # Check text content for keywords
        text_content = input_data.get('text', input_data.get('content', '')).lower()
        
        scheme_keywords = ['scheme', 'subsidy', 'loan', 'pm-kisan', 'government', 'policy', 'support', 'benefit']
        disease_keywords = ['disease', 'pest', 'problem', 'sick', 'dying', 'spot', 'infection']
        
        if any(keyword in text_content for keyword in scheme_keywords):
            return 'government_schemes'
        elif any(keyword in text_content for keyword in disease_keywords):
            return 'disease_detection'
        
        return 'general_query'
    
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
                
            elif intent == 'government_schemes':
                if self.rag_agent:
                    self.firestore_client.add_manager_thought(
                        session_id,
                        "🏛️ Searching government schemes database..."
                    )
                    
                    # Extract query text from input
                    query_text = input_data.get('text', input_data.get('content', ''))
                    
                    agent_response = self.rag_agent.query(
                        query_text,
                        classification.get('entities', {})
                    )
                else:
                    self.firestore_client.add_manager_thought(
                        session_id,
                        "⚠️ Government schemes functionality not available..."
                    )
                    
                    agent_response = {
                        'type': 'error',
                        'message': 'Government schemes functionality is not available. Vector search is not configured. Please contact support.',
                        'agent': 'manager_fallback'
                    }
                
            elif intent == 'speech_to_text':
                self.firestore_client.add_manager_thought(
                    session_id,
                    "🎤 Transcribing your audio..."
                )
                
                # Extract audio data and language
                audio_data = input_data.get('audio_data', '')
                language = input_data.get('language', 'english')
                
                agent_response = self.stt_agent.transcribe_audio(audio_data, language)

            else:  # general_query or fallback
                self.firestore_client.add_manager_thought(
                    session_id,
                    "💬 Providing general assistance..."
                )
                
                agent_response = {
                    'type': 'general_response',
                    'message': """Thank you for your question! I can help you with:
                    
                    🔬 **Crop Disease Detection** - Upload an image of your crop to identify diseases and get treatment advice
                    🏛️ **Government Schemes** - Ask about subsidies, loans, and support schemes for farmers

                    Please specify what you'd like help with!""",
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

            final_result = {
                'session_id': session_id,
                'classification': classification,
                'agent_response': agent_response,
                'final_response': final_response,
                'status': 'success',
                'debug_info': {
                    'model_used': 'gemini-2.5-flash',
                    'processing_time': 'calculated_in_production',
                    'confidence': agent_response.get('confidence', 'unknown') if agent_response else 'unknown'
                }
            }

            # Log full response (can be disabled via environment variable)
            enable_logging = os.getenv('ENABLE_RESPONSE_LOGGING', 'true').lower() == 'true'
            self.log_full_response(session_id, final_result, enable_logging)

            return final_result
                        
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
        
        # For government schemes responses
        elif classification['intent'] == 'government_schemes':
            message = agent_response.get('message', 'Government schemes information retrieved.')
            
            # Add scheme summary if available
            if agent_response.get('schemes'):
                scheme_count = len(agent_response['schemes'])
                message = f"Found {scheme_count} relevant scheme(s) for your query.\n\n{message}"
            
            return {
                'message': message,
                'type': 'government_schemes',
                'schemes': agent_response.get('schemes', []),
                'sources': agent_response.get('sources', []),
                'confidence': agent_response.get('confidence', 'medium')
            }
        
        elif classification['intent'] == 'speech_to_text':
            if agent_response.get('success'):
                message = f"🎤 **Transcription**: {agent_response['transcript']}"
                if agent_response.get('confidence'):
                    message += f"\n📊 **Confidence**: {agent_response['confidence']:.2f}"
            else:
                message = f"❌ **Transcription failed**: {agent_response.get('error', 'Unknown error')}"
            
            return {
                'message': message,
                'type': 'speech_to_text',
                'transcript': agent_response.get('transcript', ''),
                'confidence': agent_response.get('confidence', 0),
                'success': agent_response.get('success', False)
            }

        # For general responses
        return {
            'message': agent_response.get('message', 'Request processed.'),
            'type': agent_response.get('type', 'general'),
        }
    
    def log_full_response(self, session_id: str, response_data: Dict[str, Any], enable_logging: bool = True):
        """Log complete response for debugging"""
        if not enable_logging:
            return
            
        try:
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'session_id': session_id,
                'response_type': response_data.get('final_response', {}).get('type', 'unknown'),
                'full_response': response_data
            }
            
            # Log to console
            logger.info(f"FULL_RESPONSE_LOG: {json.dumps(log_entry, indent=2)}")
            
            # Save to Firestore for debugging
            self.firestore_client.db.collection('response_logs').document(session_id).set(log_entry)
            
        except Exception as e:
            logger.error(f"Failed to log response: {e}")

    def clean_json_response(self, response: str) -> str:
        """Clean JSON response by removing markdown code blocks"""
        import re
        
        # Remove ```json and ``` wrappers
        cleaned = re.sub(r'^```json\s*', '', response.strip(), flags=re.MULTILINE)
        cleaned = re.sub(r'\s*```$', '', cleaned.strip(), flags=re.MULTILINE)
        
        return cleaned.strip()