# agents/sme_agent.py
import json
import logging
import os
from typing import Dict, Any
from utils.gemini_client import GeminiClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SMEAgent:
    """
    Subject Matter Expert agent that provides answers based on expert knowledge bases
    """
    
    def __init__(self):
        self.gemini_client = GeminiClient()
        
        # Map expert names to their JSON files
        self.expert_files = {
            'op-awasthi-mosambi': 'data/op-awasthi-mosambi.json',
            'ms-swaminathan-wheat': 'data/ms-swaminathan-wheat.json'
        }
        
        logger.info("SMEAgent initialized")
    
    def query_expert(self, sme_expert: str, query: str, farm_settings: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Query a specific expert's knowledge base
        
        Args:
            sme_expert: Expert identifier
            query: User question
            farm_settings: Farm settings for context
            
        Returns:
            Dict with expert response
        """
        
        try:
            # Check if expert exists
            if sme_expert not in self.expert_files:
                available_experts = list(self.expert_files.keys())
                return {
                    'success': False,
                    'message': f"Expert '{sme_expert}' not found. Available experts: {', '.join(available_experts)}",
                    'type': 'sme_error',
                    'agent': 'sme_agent'
                }
            
            # Load expert knowledge base
            json_file_path = self.expert_files[sme_expert]
            
            if not os.path.exists(json_file_path):
                return {
                    'success': False,
                    'message': f"Knowledge base file not found for expert '{sme_expert}'",
                    'type': 'sme_error',
                    'agent': 'sme_agent'
                }
            
            with open(json_file_path, 'r', encoding='utf-8') as f:
                expert_data = json.load(f)
            
            logger.info(f"Loaded knowledge base for expert: {sme_expert}")
            
            # Create prompt for LLM with expert data
            prompt = f"""
            You are answering on behalf of agricultural expert: {sme_expert}
            
            USER QUERY: {query}
            
            EXPERT KNOWLEDGE BASE:
            {json.dumps(expert_data, indent=2)}
            
            Instructions:
            1. Use ONLY the information provided in the expert knowledge base above
            2. If the knowledge base contains relevant information to answer the query, provide a comprehensive answer
            3. If the knowledge base does NOT contain sufficient information to answer the query, respond with:
               "This expert agent does not have answers to the question: {query}"
            4. Be specific and cite relevant details from the knowledge base when answering
            5. Maintain the expert's perspective and expertise area
            6. Provide practical, actionable advice when possible
            
            Answer:
            """
            
            # Get response from LLM
            response = self.gemini_client.generate_text_flash(prompt)
            
            # Check if response indicates no answer available
            if "does not have answers to the question" in response:
                return {
                    'success': False,
                    'message': response.strip(),
                    'type': 'sme_no_answer',
                    'expert': sme_expert,
                    'agent': 'sme_agent'
                }
            
            return {
                'success': True,
                'message': response.strip(),
                'type': 'sme_response',
                'expert': sme_expert,
                'agent': 'sme_agent'
            }
            
        except Exception as e:
            logger.error(f"SME agent query failed: {e}")
            return {
                'success': False,
                'message': f"Error querying expert {sme_expert}: {str(e)}",
                'type': 'sme_error',
                'expert': sme_expert,
                'agent': 'sme_agent'
            }
    
    def get_available_experts(self) -> Dict[str, str]:
        """Get list of available experts"""
        return self.expert_files