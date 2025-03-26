from models import User, Role, Organization, ChatBot, Conversation, Message
from werkzeug.security import generate_password_hash

def test_user_password_hashing():
    """Test user password hashing"""
    user = User()
    user.set_password('password')
    assert user.check_password('password')
    assert not user.check_password('wrong-password')

def test_organization_llm_settings():
    """Test organization LLM settings JSON serialization"""
    org = Organization(name='Test Org')
    
    # Test setting and getting LLM settings
    test_settings = {
        'provider': 'openai',
        'model': 'gpt-3.5-turbo',
        'temperature': 0.7
    }
    
    org.llm_settings = test_settings
    assert org.llm_settings == test_settings

def test_chatbot_config():
    """Test chatbot config JSON serialization"""
    chatbot = ChatBot(name='Test Bot', organization_id=1)
    
    # Test setting and getting config
    test_config = {
        'theme': {
            'primaryColor': '#0088CC',
            'textColor': '#333333'
        },
        'leadCapture': {
            'enabled': True,
            'fields': ['name', 'email', 'phone']
        }
    }
    
    chatbot.config = test_config
    assert chatbot.config == test_config
