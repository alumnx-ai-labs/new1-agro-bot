
# import jsonutils/firestore_client.py
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from google.cloud import firestore
from config.settings import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FirestoreClient:
    """Client for Firestore database operations"""
    
    def __init__(self):
        self.db = firestore.Client(
            project=Config.PROJECT_ID,
            database=Config.FIRESTORE_DATABASE
        )
        logger.info("FirestoreClient initialized successfully")
    
    def create_session(self, user_id: str, input_data: Dict[str, Any]) -> str:
        """Create a new session and return session ID"""
        try:
            session_ref = self.db.collection('sessions').document()
            session_id = session_ref.id
            
            session_data = {
                'user_id': user_id,
                'input_data': input_data,
                'status': 'processing',
                'manager_thoughts': [],
                'agent_responses': {},
                'created_at': firestore.SERVER_TIMESTAMP,
                'updated_at': firestore.SERVER_TIMESTAMP
            }
            
            session_ref.set(session_data)
            logger.info(f"Session created: {session_id}")
            return session_id
            
        except Exception as e:
            logger.error(f"Failed to create session: {e}")
            raise
    
    def add_manager_thought(self, session_id: str, thought: str):
        """Add a manager thought to session for transparency"""
        try:
            session_ref = self.db.collection('sessions').document(session_id)
            
            # Add thought with timestamp
            thought_entry = {
                'thought': thought,
                'timestamp': datetime.now().isoformat()
            }
            
            session_ref.update({
                'manager_thoughts': firestore.ArrayUnion([thought_entry]),
                'updated_at': firestore.SERVER_TIMESTAMP
            })
            
            logger.info(f"Manager thought added to session {session_id}: {thought}")
            
        except Exception as e:
            logger.error(f"Failed to add manager thought: {e}")
    
    def save_agent_response(self, session_id: str, agent_name: str, response: Dict[str, Any]):
        """Save agent response to session"""
        try:
            session_ref = self.db.collection('sessions').document(session_id)
            
            session_ref.update({
                f'agent_responses.{agent_name}': response,
                'updated_at': firestore.SERVER_TIMESTAMP
            })
            
            logger.info(f"Agent response saved: {session_id} - {agent_name}")
            
        except Exception as e:
            logger.error(f"Failed to save agent response: {e}")
    
    def update_session_status(self, session_id: str, status: str, final_response: Optional[str] = None):
        """Update session status"""
        try:
            session_ref = self.db.collection('sessions').document(session_id)
            
            update_data = {
                'status': status,
                'updated_at': firestore.SERVER_TIMESTAMP
            }
            
            if final_response:
                update_data['final_response'] = final_response
            
            session_ref.update(update_data)
            logger.info(f"Session status updated: {session_id} - {status}")
            
        except Exception as e:
            logger.error(f"Failed to update session status: {e}")
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data"""
        try:
            session_ref = self.db.collection('sessions').document(session_id)
            doc = session_ref.get()
            
            if doc.exists:
                return doc.to_dict()
            return None
            
        except Exception as e:
            logger.error(f"Failed to get session: {e}")
            return None
    
    def test_connection(self) -> bool:
        """Test Firestore connection"""
        try:
            # Try to read from a test collection
            test_ref = self.db.collection('_test').document('connection')
            test_ref.set({'test': True, 'timestamp': firestore.SERVER_TIMESTAMP})
            
            # Try to read it back
            doc = test_ref.get()
            success = doc.exists
            
            # Clean up
            test_ref.delete()
            
            return success
        except:
            return False