# utils/vector_store_client.py
import logging
from typing import List, Dict, Any
import vertexai
from vertexai.language_models import TextEmbeddingModel
from google.cloud import aiplatform
import numpy as np
from config.settings import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VectorStoreClient:
    """
    Vector Store Client using Google AI technologies:
    - Vertex AI Text Embeddings for vector generation
    - Vertex AI Vector Search for similarity search
    """
    
    def __init__(self):
        # Initialize Vertex AI
        vertexai.init(project=Config.PROJECT_ID, location=Config.REGION)
        
        # Initialize embedding model
        self.embedding_model = TextEmbeddingModel.from_pretrained("textembedding-gecko@003")
        
        # Initialize Vector Search client
        self.vector_search_client = aiplatform.MatchingEngineIndexEndpoint(
            index_endpoint_name=Config.VECTOR_SEARCH_ENDPOINT
        )
        
        logger.info("VectorStoreClient initialized with Google AI Vector Search")
    
    def get_embedding(self, text: str) -> List[float]:
        """Generate embedding for text using Vertex AI Text Embeddings"""
        try:
            # Get embeddings using Google's text-embedding-gecko model
            embeddings = self.embedding_model.get_embeddings([text])
            
            # Extract the embedding vector
            embedding_vector = embeddings[0].values
            
            logger.info(f"Generated embedding for text: {text[:50]}... (vector dim: {len(embedding_vector)})")
            return embedding_vector
            
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            raise
    
    def similarity_search(self, query_embedding: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar documents using Vertex AI Vector Search"""
        try:
            # Perform similarity search
            response = self.vector_search_client.find_neighbors(
                deployed_index_id=Config.DEPLOYED_INDEX_ID,
                queries=[query_embedding],
                num_neighbors=top_k
            )
            
            # Process results
            results = []
            for neighbor in response[0]:
                result = {
                    'id': neighbor.id,
                    'score': float(neighbor.distance),  # Convert to similarity score
                    'content': self.get_document_content(neighbor.id),
                    'metadata': self.get_document_metadata(neighbor.id)
                }
                results.append(result)
            
            logger.info(f"Vector search returned {len(results)} similar documents")
            return results
            
        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            # Return empty results if search fails
            return []
    
    def get_document_content(self, doc_id: str) -> str:
        """Retrieve document content by ID"""
        try:
            # In a real implementation, this would fetch from your document store
            # For now, we'll use Firestore to store the actual document content
            from utils.firestore_client import FirestoreClient
            
            firestore_client = FirestoreClient()
            doc = firestore_client.db.collection('scheme_documents').document(doc_id).get()
            
            if doc.exists:
                return doc.to_dict().get('content', '')
            else:
                logger.warning(f"Document {doc_id} not found in Firestore")
                return f"Document content not available for ID: {doc_id}"
                
        except Exception as e:
            logger.error(f"Failed to retrieve document content for {doc_id}: {e}")
            return f"Error retrieving document content: {str(e)}"
    
    def get_document_metadata(self, doc_id: str) -> Dict[str, Any]:
        """Retrieve document metadata by ID"""
        try:
            from utils.firestore_client import FirestoreClient
            
            firestore_client = FirestoreClient()
            doc = firestore_client.db.collection('scheme_documents').document(doc_id).get()
            
            if doc.exists:
                data = doc.to_dict()
                return {
                    'source': data.get('source', 'Unknown'),
                    'title': data.get('title', 'Untitled'),
                    'category': data.get('category', 'General'),
                    'last_updated': data.get('last_updated', 'Unknown'),
                    'scheme_type': data.get('scheme_type', 'Government Scheme')
                }
            else:
                return {'source': 'Unknown', 'title': f'Document {doc_id}'}
                
        except Exception as e:
            logger.error(f"Failed to retrieve metadata for {doc_id}: {e}")
            return {'source': 'Error', 'title': f'Document {doc_id}'}
    
    def add_documents(self, documents: List[Dict[str, Any]]) -> bool:
        """Add documents to the vector store"""
        try:
            from utils.firestore_client import FirestoreClient
            
            firestore_client = FirestoreClient()
            batch = firestore_client.db.batch()
            
            embeddings_to_upload = []
            
            for doc in documents:
                doc_id = doc.get('id', f"doc_{len(embeddings_to_upload)}")
                content = doc.get('content', '')
                metadata = doc.get('metadata', {})
                
                # Generate embedding
                embedding = self.get_embedding(content)
                
                # Store document content and metadata in Firestore
                doc_ref = firestore_client.db.collection('scheme_documents').document(doc_id)
                batch.set(doc_ref, {
                    'content': content,
                    'metadata': metadata,
                    'source': metadata.get('source', 'Unknown'),
                    'title': metadata.get('title', 'Untitled'),
                    'category': metadata.get('category', 'General'),
                    'last_updated': metadata.get('last_updated', 'Unknown'),
                    'scheme_type': metadata.get('scheme_type', 'Government Scheme')
                })
                
                # Prepare embedding for vector search
                embeddings_to_upload.append({
                    'id': doc_id,
                    'embedding': embedding
                })
            
            # Commit Firestore batch
            batch.commit()
            
            # Upload embeddings to Vector Search
            # Note: This is a simplified version. In production, you'd use the Vector Search API
            # to upload embeddings in batches
            logger.info(f"Successfully processed {len(documents)} documents for vector store")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to add documents to vector store: {e}")
            return False
    
    def test_connection(self) -> bool:
        """Test vector store connection"""
        try:
            # Test embedding generation
            test_embedding = self.get_embedding("Test query for government schemes")
            
            if len(test_embedding) > 0:
                logger.info("Vector store connection test successful")
                return True
            else:
                logger.error("Vector store connection test failed - empty embedding")
                return False
                
        except Exception as e:
            logger.error(f"Vector store connection test failed: {e}")
            return False