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
from agents.translator_agent import TranslatorAgent
from agents.general_agent import GeneralAgent

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
        self.translator_agent = TranslatorAgent()
        self.general_agent = GeneralAgent()  # ADD THIS LINE

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
            'translator': self.translator_agent,
            'general_farming': self.general_agent,  # ADD THIS LINE
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
        """Main orchestration method with translation flow"""
        
        try:
            # Add initial manager thought
            self.firestore_client.add_manager_thought(
                session_id, 
                "🤔 Analyzing your request..."
            )
            
            # Step 1: Input Processing
            processed_input, original_language = self.process_input_stage(session_id, input_data)
            
            # Step 2: Logic Processing  
            logic_result = self.process_logic_stage(session_id, processed_input)
            
            # Step 3: Output Formation
            final_response = self.process_output_stage(session_id, logic_result, original_language)
            
            # Update session status
            self.firestore_client.update_session_status(
                session_id, 
                'completed', 
                final_response['message']
            )
            
            logger.info(f"Request processed successfully for session: {session_id}")

            final_result = {
                'session_id': session_id,
                'original_language': original_language,
                'final_response': final_response,
                'status': 'success',
                'debug_info': {
                    'model_used': 'gemini-2.5-flash',
                    'processing_time': 'calculated_in_production',
                    'confidence': logic_result.get('confidence', 'unknown') if logic_result else 'unknown'
                }
            }

            # Log full response
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

    def process_input_stage(self, session_id: str, input_data: Dict[str, Any]) -> tuple:
        """Stage 1: Input Processing"""
        
        original_language = input_data.get('language', 'english')
        
        # Handle image input
        if input_data.get('image_data'):
            self.firestore_client.add_manager_thought(
                session_id,
                "📸 Processing image for disease detection..."
            )
            return input_data, original_language
        
        # Handle audio input  
        elif input_data.get('audio_data'):
            self.firestore_client.add_manager_thought(
                session_id,
                "🎤 Transcribing audio..."
            )
            
            # Transcribe audio
            stt_result = self.stt_agent.transcribe_audio(
                input_data['audio_data'], 
                original_language
            )
            
            if stt_result.get('success'):
                transcript = stt_result['transcript']
                
                # Translate to English if needed
                if original_language.lower() not in ['english', 'en']:
                    self.firestore_client.add_manager_thought(
                        session_id,
                        "🌐 Translating to English for processing..."
                    )
                    
                    translation_result = self.translator_agent.translate(
                        original_language, 'english', transcript
                    )
                    
                    if translation_result.get('success'):
                        english_text = translation_result['translated_text']
                    else:
                        english_text = transcript  # Fallback to original
                else:
                    english_text = transcript
                
                # Return processed text input
                return {
                    'type': 'text',
                    'text': english_text,
                    'content': english_text,
                    'original_transcript': transcript,
                    'language': 'english'
                }, original_language
            else:
                raise Exception(f"Audio transcription failed: {stt_result.get('error')}")
        
        # Handle text input
        else:
            text_content = input_data.get('text', input_data.get('content', ''))
            
            # Translate to English if needed
            if original_language.lower() not in ['english', 'en']:
                self.firestore_client.add_manager_thought(
                    session_id,
                    "🌐 Translating to English for processing..."
                )
                
                translation_result = self.translator_agent.translate(
                    original_language, 'english', text_content
                )
                
                if translation_result.get('success'):
                    english_text = translation_result['translated_text']
                else:
                    english_text = text_content  # Fallback to original
            else:
                english_text = text_content
            
            return {
                'type': 'text',
                'text': english_text,
                'content': english_text,
                'original_text': text_content,
                'language': 'english',
                'queryType': input_data.get('queryType')
            }, original_language

    def process_logic_stage(self, session_id: str, processed_input: Dict[str, Any]) -> Dict[str, Any]:
        """Stage 2: Logic Processing"""
        
        # Handle image (disease detection)
        if processed_input.get('image_data'):
            self.firestore_client.add_manager_thought(
                session_id,
                "🔬 Analyzing crop disease..."
            )
            
            farm_settings = processed_input.get('farm_settings', {})
            return self.disease_agent.analyze(processed_input, {}, farm_settings)
        
        # Handle text queries
        else:
            text_content = processed_input.get('text', '')
            
            # Check if it's about government schemes
            if self.is_government_schemes_query(text_content, processed_input.get('queryType')):
                if self.rag_agent:
                    self.firestore_client.add_manager_thought(
                        session_id,
                        "🏛️ Searching government schemes..."
                    )
                    
                    farm_settings = processed_input.get('farm_settings', {})
                    return self.rag_agent.query(text_content, {'farm_settings': farm_settings}, farm_settings)
                else:
                    return {
                        'type': 'error',
                        'message': 'Government schemes functionality is not available.',
                        'agent': 'manager_fallback'
                    }
            else:
                # General farming query
                self.firestore_client.add_manager_thought(
                    session_id,
                    "💬 Providing personalized farming assistance..."
                )
                
                # Extract farm settings for personalization
                farm_settings = processed_input.get('farm_settings', {})
                
                return self.general_agent.query(text_content, farm_settings)

    def process_output_stage(self, session_id: str, logic_result: Dict[str, Any], original_language: str) -> Dict[str, Any]:
        """Stage 3: Output Formation"""
        
        # Create response in English first
        english_response = self.synthesize_response({}, logic_result)
        
        # Translate back to original language if needed
        if original_language.lower() not in ['english', 'en']:
            self.firestore_client.add_manager_thought(
                session_id,
                f"🌐 Translating response to {original_language}..."
            )
            
            translation_result = self.translator_agent.translate(
                'english', original_language, english_response['message']
            )
            
            if translation_result.get('success'):
                # Create translated response
                translated_response = english_response.copy()
                translated_response['message'] = translation_result['translated_text']
                translated_response['original_english'] = english_response['message']
                translated_response['language'] = original_language
                return translated_response
            else:
                # Fallback to English if translation fails
                english_response['translation_note'] = 'Translation failed, showing in English'
                return english_response
        
        return english_response

    def is_government_schemes_query(self, text: str, query_type: str = None) -> bool:
        """Determine if query is about government schemes"""
        
        # Check explicit query type
        if query_type == 'government_schemes':
            return True
        
        # Check for scheme-related keywords
        text_lower = text.lower()
        scheme_keywords = [
            'scheme', 'subsidy', 'loan', 'pm-kisan', 'government', 'policy', 
            'support', 'benefit', 'pradhan mantri', 'yojana', 'grant', 
            'financial assistance', 'central government', 'state government'
        ]
        
        return any(keyword in text_lower for keyword in scheme_keywords)


    def synthesize_response(self, classification: Dict, agent_response: Dict) -> Dict[str, Any]:
        """Create a unified response from agent outputs"""
        
        if not agent_response:
            return {
                'message': "I couldn't process your request properly. Please try again.",
                'type': 'error'
            }
        
        agent_type = agent_response.get('agent', agent_response.get('type', 'unknown'))
        
        # For disease detection responses
        if 'disease' in agent_type and agent_response.get('analysis'):
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
        elif 'rag' in agent_type or agent_response.get('schemes'):
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