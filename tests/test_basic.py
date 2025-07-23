# tests/test_basic.py
import pytest
import json
from unittest.mock import Mock, patch
from agents.manager import ManagerAgent
from agents.disease_detection import DiseaseDetectionAgent

class TestBasicFunctionality:
    
    def test_manager_agent_initialization(self):
        """Test that manager agent initializes properly"""
        manager = ManagerAgent()
        assert manager is not None
        assert hasattr(manager, 'gemini_client')
        assert hasattr(manager, 'firestore_client')
        assert hasattr(manager, 'disease_agent')
    
    def test_disease_detection_agent_initialization(self):
        """Test that disease detection agent initializes properly"""
        agent = DiseaseDetectionAgent()
        assert agent is not None
        assert hasattr(agent, 'gemini_client')
    
    @patch('utils.gemini_client.GeminiClient.generate_text_flash')
    def test_intent_classification(self, mock_gemini):
        """Test intent classification"""
        # Mock Gemini response
        mock_response = json.dumps({
            "intent": "disease_detection",
            "confidence": 0.95,
            "reasoning": "Image provided with crop issues",
            "entities": {"has_image": True}
        })
        mock_gemini.return_value = mock_response
        
        manager = ManagerAgent()
        input_data = {"image_data": "fake_base64_data"}
        
        result = manager.classify_intent(input_data)
        
        assert result['intent'] == 'disease_detection'
        assert result['confidence'] == 0.95
        assert mock_gemini.called
    
    def test_fallback_classification(self):
        """Test fallback when classification fails"""
        with patch('utils.gemini_client.GeminiClient.generate_text_flash') as mock_gemini:
            mock_gemini.return_value = "Invalid JSON response"
            
            manager = ManagerAgent()
            result = manager.classify_intent({"text": "test"})
            
            assert 'intent' in result
            assert result['confidence'] == 0.5
    
    def test_disease_agent_no_image_error(self):
        """Test disease agent handles missing image"""
        agent = DiseaseDetectionAgent()
        result = agent.analyze({"text": "test"}, {})
        
        assert result['type'] == 'error'
        assert 'image' in result['message'].lower()

if __name__ == '__main__':
    pytest.main([__file__])