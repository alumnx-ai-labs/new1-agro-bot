# agents/rag_agent.py
import json
import logging
from typing import Dict, Any, List
from utils.gemini_client import GeminiClient
from utils.vector_store_client import VectorStoreClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RAGAgent:
    """
    RAG (Retrieval-Augmented Generation) Agent for Government Schemes queries
    Uses Google AI technologies: Vertex AI Vector Search + Gemini
    """
    
    def __init__(self):
        self.gemini_client = GeminiClient()
        
        # Try to initialize vector store, but don't fail if it's not available
        try:
            self.vector_store_client = VectorStoreClient()
            self.vector_search_available = True
            logger.info("RAGAgent initialized with Google AI Vector Search")
        except Exception as e:
            logger.warning(f"Vector search not available: {e}")
            self.vector_store_client = None
            self.vector_search_available = False
            logger.info("RAGAgent initialized in fallback mode (no vector search)")
    
    def query(self, user_query: str, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Process government schemes query using RAG approach or fallback"""
        
        try:
            logger.info(f"Processing query: {user_query[:100]}")
            
            if self.vector_search_available:
                return self.process_with_vector_search(user_query, entities)
            else:
                return self.process_with_fallback(user_query, entities)
                
        except Exception as e:
            logger.error(f"Query processing failed: {e}")
            return {
                'type': 'error',
                'message': f'Sorry, I had trouble finding information about government schemes: {str(e)}',
                'agent': 'rag_agent'
            }
    
    def process_with_vector_search(self, user_query: str, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Process with full vector search functionality"""
        
        # Step 1: Generate embedding for user query
        query_embedding = self.vector_store_client.get_embedding(user_query)
        
        # Step 2: Search for relevant chunks in vector database
        relevant_chunks = self.vector_store_client.similarity_search(
            query_embedding=query_embedding,
            top_k=5
        )
        
        # Step 3: Create context from retrieved chunks
        context = self.create_context_from_chunks(relevant_chunks)
        
        # Step 4: Generate response using Gemini with retrieved context
        response = self.generate_rag_response(user_query, context, entities)
        
        return {
            'type': 'rag_response',
            'message': response['answer'],
            'schemes': response.get('schemes', []),
            'sources': self.extract_sources(relevant_chunks),
            'confidence': self.calculate_confidence(relevant_chunks),
            'agent': 'rag_agent',
            'retrieved_chunks': len(relevant_chunks)
        }
    
    def process_with_fallback(self, user_query: str, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Process with fallback when vector search is not available"""
        
        # Use static knowledge base for common schemes
        static_context = self.get_static_schemes_context(user_query)
        
        # Generate response using Gemini with static context
        response = self.generate_fallback_response(user_query, static_context, entities)
        
        return {
            'type': 'rag_response',
            'message': response['answer'],
            'schemes': response.get('schemes', []),
            'sources': ['Static Knowledge Base'],
            'confidence': 'medium',
            'agent': 'rag_agent_fallback',
            'note': 'Using fallback mode - vector search not available'
        }
    
    def create_context_from_chunks(self, chunks: List[Dict]) -> str:
        """Combine retrieved chunks into context for generation"""
        
        context_parts = []
        
        for i, chunk in enumerate(chunks, 1):
            chunk_text = chunk.get('content', '')
            chunk_metadata = chunk.get('metadata', {})
            
            # Add chunk with metadata
            context_part = f"Document {i}:\n"
            context_part += f"Source: {chunk_metadata.get('source', 'Unknown')}\n"
            context_part += f"Content: {chunk_text}\n"
            context_parts.append(context_part)
        
        return "\n---\n".join(context_parts)
    
    def generate_rag_response(self, query: str, context: str, entities: Dict) -> Dict[str, Any]:
        """Generate response using Gemini with retrieved context"""
        
        prompt = f"""
        You are a helpful assistant specializing in Indian government schemes and agricultural policies.
        
        USER QUERY: {query}
        
        RETRIEVED CONTEXT:
        {context}
        
        TASK:
        Using ONLY the information provided in the retrieved context above, answer the user's query about government schemes.
        
        RESPONSE FORMAT (JSON only):
        {{
            "answer": "Comprehensive answer based on retrieved information",
            "schemes": [
                {{
                    "name": "Scheme Name",
                    "description": "Brief description",
                    "eligibility": "Who can apply",
                    "benefits": "What benefits are provided",
                    "application_process": "How to apply"
                }}
            ],
            "key_points": [
                "Important point 1",
                "Important point 2"
            ],
            "additional_info": "Any additional relevant information"
        }}
        
        IMPORTANT RULES:
        1. Use ONLY information from the retrieved context
        2. If information is not in the context, say "Information not available in current database"
        3. Be specific about scheme names, eligibility criteria, and benefits
        4. Format financial amounts in Indian Rupees (₹)
        5. Mention if schemes are central or state government schemes
        6. Provide actionable information for farmers
        
        CRITICAL: Return ONLY the JSON object. Do not wrap in ```json or ``` blocks.
        """
        
        try:
            # Use Gemini Pro for complex reasoning with retrieved context
            response_text = self.gemini_client.generate_text_pro(prompt)
            
            # Clean and parse JSON response
            cleaned_response = self.clean_json_response(response_text)
            response_data = json.loads(cleaned_response)
            
            return response_data
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse RAG response JSON: {e}")
            logger.error(f"Raw response: {response_text}")
            
            # Fallback response
            return {
                "answer": response_text if len(response_text) > 10 else "Unable to process the query properly.",
                "schemes": [],
                "key_points": [],
                "additional_info": "Note: Structured response was not available."
            }
    
    def extract_sources(self, chunks: List[Dict]) -> List[str]:
        """Extract source information from retrieved chunks"""
        
        sources = []
        for chunk in chunks:
            metadata = chunk.get('metadata', {})
            source = metadata.get('source', 'Unknown source')
            
            if source not in sources:
                sources.append(source)
        
        return sources[:3]  # Return top 3 unique sources
    
    def calculate_confidence(self, chunks: List[Dict]) -> str:
        """Calculate confidence based on retrieval quality"""
        
        if not chunks:
            return 'low'
        
        # Simple confidence scoring based on number and quality of chunks
        avg_score = sum(chunk.get('score', 0) for chunk in chunks) / len(chunks)
        
        if avg_score > 0.8:
            return 'high'
        elif avg_score > 0.6:
            return 'medium'
        else:
            return 'low'
    
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
    
    def get_static_schemes_context(self, query: str) -> str:
        """Get static context for common schemes when vector search is not available"""
        
        query_lower = query.lower()
        
        # Static knowledge base for common schemes
        schemes_info = {
            'pm-kisan': """
PM-KISAN (Pradhan Mantri Kisan Samman Nidhi) Scheme:
- Financial benefit of Rs. 6000 per year to eligible farmer families
- Payment in three equal installments of Rs. 2000 each
- For landholding farmer families with cultivable land
- Direct cash transfer to bank accounts
- Apply at pmkisan.gov.in
            """,
            'drip irrigation': """
Drip Irrigation Subsidy Scheme:
- Up to 55% subsidy for small and marginal farmers
- Up to 45% subsidy for other farmers
- Additional 10% subsidy for SC/ST farmers
- Minimum area: 0.5 hectares, Maximum: 5 hectares
- Apply through state horticulture department
            """,
            'organic farming': """
Paramparagat Krishi Vikas Yojana (PKVY):
- Rs. 50,000 per hectare over 3 years for organic farming
- Rs. 31,000 for organic inputs and cultivation
- Rs. 8,800 for certification and organic premium
- Minimum 50 farmers in each cluster
- Participatory Guarantee System (PGS) certification
            """,
            'crop insurance': """
Pradhan Mantri Fasal Bima Yojana (PMFBY):
- Comprehensive crop insurance coverage
- Kharif crops: Maximum 2% premium
- Rabi crops: Maximum 1.5% premium
- Coverage for natural calamities and post-harvest losses
- Quick settlement within 45 days
            """,
            'dairy farming': """
National Livestock Mission - Dairy Development:
- Bank loans up to Rs. 10 lakhs for individual farmers
- 25% subsidy for general category, 33.33% for SC/ST
- Support for milch animals, cattle shed, processing equipment
- Artificial insemination services and breed improvement
            """
        }
        
        # Find relevant schemes based on query keywords
        relevant_context = []
        
        for scheme_key, scheme_info in schemes_info.items():
            if any(keyword in query_lower for keyword in scheme_key.split()):
                relevant_context.append(scheme_info)
        
        # If no specific match, include general schemes
        if not relevant_context:
            relevant_context = [
                schemes_info['pm-kisan'],
                schemes_info['crop insurance']
            ]
        
        return "\n---\n".join(relevant_context)
    
    def generate_fallback_response(self, query: str, context: str, entities: Dict) -> Dict[str, Any]:
        """Generate response using static context"""
        
        prompt = f"""
        You are a helpful assistant specializing in Indian government schemes for farmers.
        
        USER QUERY: {query}
        
        AVAILABLE SCHEMES INFORMATION:
        {context}
        
        TASK:
        Based on the schemes information provided above, answer the user's query.
        
        RESPONSE FORMAT (JSON only):
        {{
            "answer": "Comprehensive answer based on available information",
            "schemes": [
                {{
                    "name": "Scheme Name",
                    "description": "Brief description",
                    "eligibility": "Who can apply",
                    "benefits": "What benefits are provided",
                    "application_process": "How to apply"
                }}
            ],
            "key_points": [
                "Important point 1",
                "Important point 2"
            ]
        }}
        
        IMPORTANT:
        - Use simple language that farmers can understand
        - Provide specific amounts in Indian Rupees (₹)
        - Give actionable advice
        - If information is limited, say so clearly
        
        CRITICAL: Return ONLY the JSON object. No markdown formatting.
        """
        
        try:
            response_text = self.gemini_client.generate_text_pro(prompt)
            cleaned_response = self.clean_json_response(response_text)
            response_data = json.loads(cleaned_response)
            return response_data
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse fallback response JSON: {e}")
            return {
                "answer": response_text if len(response_text) > 10 else "I can help you with government schemes information, but I need more specific details about what you're looking for.",
                "schemes": [],
                "key_points": ["Contact your local agriculture department for detailed information"]
            }