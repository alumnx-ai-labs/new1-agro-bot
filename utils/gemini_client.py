# utils/gemini_client.py
import base64
import json
import logging
from typing import Dict, Any, Optional
import vertexai
from vertexai.generative_models import GenerativeModel, Part
import vertexai.preview.generative_models as generative_models
from config.settings import Config

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GeminiClient:
    """Client for interacting with Google's Gemini models"""
    
    def __init__(self):
        # Initialize Vertex AI
        vertexai.init(project=Config.PROJECT_ID, location=Config.REGION)
        
        # Initialize models
        self.pro_model = GenerativeModel(Config.GEMINI_PRO_MODEL)
        self.flash_model = GenerativeModel(Config.GEMINI_FLASH_MODEL)
        
        # Safety settings
        self.safety_config = {
            generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: 
                generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: 
                generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: 
                generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: 
                generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        }
        
        logger.info("GeminiClient initialized successfully")
    
    def generate_text_flash(self, prompt: str) -> str:
        """Fast text generation using Gemini Flash"""
        try:
            response = self.flash_model.generate_content(
                prompt,
                safety_settings=self.safety_config,
                generation_config={
                    "max_output_tokens": 1024,
                    "temperature": 0.2,
                    "top_p": 0.8,
                }
            )
            
            logger.info(f"Flash generation successful, prompt length: {len(prompt)}")
            return response.text
            
        except Exception as e:
            logger.error(f"Flash generation failed: {e}")
            return f"I'm having trouble processing your request: {str(e)}"
    
    def generate_text_pro(self, prompt: str) -> str:
        """Complex reasoning using Gemini Pro"""
        try:
            response = self.pro_model.generate_content(
                prompt,
                safety_settings=self.safety_config,
                generation_config={
                    "max_output_tokens": 2048,
                    "temperature": 0.1,
                    "top_p": 0.8,
                }
            )
            
            logger.info(f"Pro generation successful, prompt length: {len(prompt)}")
            return response.text
            
        except Exception as e:
            logger.error(f"Pro generation failed: {e}")
            return f"I'm having trouble with complex analysis: {str(e)}"
    
    def analyze_image(self, prompt: str, image_data: str) -> str:
        """Image analysis using Gemini Pro Vision"""
        try:
            # Convert base64 to Part object
            image_bytes = base64.b64decode(image_data)
            image_part = Part.from_data(
                mime_type="image/jpeg",
                data=image_bytes
            )
            
            response = self.pro_model.generate_content(
                [prompt, image_part],
                safety_settings=self.safety_config,
                generation_config={
                    "max_output_tokens": 2048,
                    "temperature": 0.1,
                }
            )
            
            logger.info("Image analysis successful")
            return response.text
            
        except Exception as e:
            logger.error(f"Image analysis failed: {e}")
            return f"I couldn't analyze the image properly: {str(e)}"
    
    def test_connection(self) -> bool:
        """Test if Gemini connection is working"""
        try:
            test_response = self.generate_text_flash("Say 'Connection successful' if you can read this.")
            return "successful" in test_response.lower()
        except:
            return False