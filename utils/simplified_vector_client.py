# utils/simplified_vector_client.py
import logging
import json
from typing import List, Dict, Any
import numpy as np
import vertexai
from vertexai.language_models import TextEmbeddingModel
from utils.firestore_client import FirestoreClient
from config.settings import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimplifiedVectorClient:
    """
    Simplified Vector Store Client using:
    - Vertex AI Text Embeddings for vector generation
    - Firestore for storage with cosine similarity search
    """
    
    def __init__(self):
        # Initialize Vertex AI
        vertexai.init(project=Config.PROJECT_ID, location=Config.REGION)
        
        # Try different embedding models (from newest to oldest)
        embedding_models_to_try = [
            "text-embedding-004",
            "textembedding-gecko@003", 
            "textembedding-gecko@002",
            "textembedding-gecko@001",
            "textembedding-gecko"
        ]
        
        self.embedding_model = None
        self.model_name = None
        
        for model_name in embedding_models_to_try:
            try:
                logger.info(f"Trying embedding model: {model_name}")
                self.embedding_model = TextEmbeddingModel.from_pretrained(model_name)
                
                # Test the model with a simple query
                test_embeddings = self.embedding_model.get_embeddings(["test"])
                if test_embeddings and len(test_embeddings[0].values) > 0:
                    self.model_name = model_name
                    logger.info(f"✅ Successfully initialized embedding model: {model_name}")
                    break
                    
            except Exception as e:
                logger.warning(f"Failed to initialize {model_name}: {e}")
                continue
        
        if not self.embedding_model:
            raise Exception("No embedding model could be initialized. Please check your project setup and API access.")
        
        # Initialize Firestore client
        self.firestore_client = FirestoreClient()
        
        # Collection name for vector storage
        self.collection_name = "vector_embeddings"
        
        logger.info(f"SimplifiedVectorClient initialized with {self.model_name} + Firestore")
    
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
    
    def add_documents(self, documents: List[Dict[str, Any]]) -> bool:
        """Add documents to the vector store"""
        try:
            batch = self.firestore_client.db.batch()
            
            for doc in documents:
                doc_id = doc.get('id', f"doc_{len(documents)}")
                content = doc.get('content', '')
                metadata = doc.get('metadata', {})
                
                # Generate embedding
                embedding = self.get_embedding(content)
                
                # Store document with embedding in Firestore
                doc_ref = self.firestore_client.db.collection(self.collection_name).document(doc_id)
                
                doc_data = {
                    'id': doc_id,
                    'content': content,
                    'metadata': metadata,
                    'embedding': embedding,
                    'embedding_model': self.model_name,
                    'created_at': self.firestore_client.get_server_timestamp()
                }
                
                batch.set(doc_ref, doc_data)
                
                # Also store in the original scheme_documents collection for compatibility
                scheme_doc_ref = self.firestore_client.db.collection('scheme_documents').document(doc_id)
                scheme_doc_data = {
                    'content': content,
                    'metadata': metadata,
                    'source': metadata.get('source', 'Unknown'),
                    'title': metadata.get('title', 'Untitled'),
                    'category': metadata.get('category', 'General'),
                    'last_updated': metadata.get('last_updated', 'Unknown'),
                    'scheme_type': metadata.get('scheme_type', 'Government Scheme')
                }
                batch.set(scheme_doc_ref, scheme_doc_data)
            
            # Commit batch
            batch.commit()
            
            logger.info(f"Successfully added {len(documents)} documents to vector store")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add documents to vector store: {e}")
            return False
    
    def similarity_search(self, query_embedding: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar documents using cosine similarity"""
        try:
            # Get all documents with embeddings
            docs = self.firestore_client.db.collection(self.collection_name).stream()
            
            similarities = []
            
            for doc in docs:
                doc_data = doc.to_dict()
                stored_embedding = doc_data.get('embedding', [])
                
                if not stored_embedding:
                    continue
                
                # Calculate cosine similarity
                similarity = self.cosine_similarity(query_embedding, stored_embedding)
                
                similarities.append({
                    'id': doc_data.get('id'),
                    'content': doc_data.get('content', ''),
                    'metadata': doc_data.get('metadata', {}),
                    'score': similarity
                })
            
            # Sort by similarity score (descending)
            similarities.sort(key=lambda x: x['score'], reverse=True)
            
            # Return top_k results
            results = similarities[:top_k]
            
            logger.info(f"Vector search returned {len(results)} similar documents")
            return results
            
        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            return []
    
    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        try:
            # Convert to numpy arrays
            a = np.array(vec1)
            b = np.array(vec2)
            
            # Calculate cosine similarity
            dot_product = np.dot(a, b)
            norm_a = np.linalg.norm(a)
            norm_b = np.linalg.norm(b)
            
            if norm_a == 0 or norm_b == 0:
                return 0.0
            
            similarity = dot_product / (norm_a * norm_b)
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Error calculating cosine similarity: {e}")
            return 0.0
    
    def get_document_content(self, doc_id: str) -> str:
        """Retrieve document content by ID"""
        try:
            doc = self.firestore_client.db.collection('scheme_documents').document(doc_id).get()
            
            if doc.exists:
                return doc.to_dict().get('content', '')
            else:
                logger.warning(f"Document {doc_id} not found")
                return f"Document content not available for ID: {doc_id}"
                
        except Exception as e:
            logger.error(f"Failed to retrieve document content for {doc_id}: {e}")
            return f"Error retrieving document content: {str(e)}"
    
    def get_document_metadata(self, doc_id: str) -> Dict[str, Any]:
        """Retrieve document metadata by ID"""
        try:
            doc = self.firestore_client.db.collection('scheme_documents').document(doc_id).get()
            
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
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector collection"""
        try:
            docs = list(self.firestore_client.db.collection(self.collection_name).stream())
            
            stats = {
                'total_documents': len(docs),
                'embedding_model': self.model_name,
                'vector_dimensions': 768,  # Most models use 768, but this varies
                'collection_name': self.collection_name
            }
            
            if docs:
                # Get sample metadata
                sample_doc = docs[0].to_dict()
                stats['sample_metadata'] = sample_doc.get('metadata', {})
                stats['last_updated'] = sample_doc.get('created_at')
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get collection stats: {e}")
            return {'error': str(e)}