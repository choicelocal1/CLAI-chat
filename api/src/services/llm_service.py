import os
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.prompts.chat import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate

class LLMService:
    def __init__(self, api_key=None, model_name=None):
        """
        Initialize the LLM service with API key and model name
        """
        self.api_key = api_key or os.environ.get('OPENAI_API_KEY')
        self.model_name = model_name or os.environ.get('LLM_MODEL', 'gpt-3.5-turbo')
        
        self.chat_model = ChatOpenAI(
            model_name=self.model_name,
            temperature=0.7,
            api_key=self.api_key,
            request_timeout=60
        )
    
    def create_prompt_template(self, system_template, human_template):
        """
        Create a chat prompt template with system and human messages
        """
        system_message = SystemMessagePromptTemplate.from_template(system_template)
        human_message = HumanMessagePromptTemplate.from_template(human_template)
        
        return ChatPromptTemplate.from_messages([system_message, human_message])
    
    def get_chat_response(self, prompt, **kwargs):
        """
        Get a response from the chat model using the provided prompt and variables
        """
        try:
            formatted_prompt = prompt.format_prompt(**kwargs)
            response = self.chat_model(formatted_prompt.to_messages())
            return {
                'content': response.content,
                'model': self.model_name,
                'success': True
            }
        except Exception as e:
            return {
                'content': f"I'm having trouble connecting right now. Please try again in a moment.",
                'model': self.model_name,
                'error': str(e),
                'success': False
            }
    
    def get_completion(self, prompt, **kwargs):
        """
        Get a completion from the model using a simple prompt
        """
        system_template = "You are a helpful assistant."
        human_template = "{prompt}"
        
        chat_prompt = self.create_prompt_template(system_template, human_template)
        
        return self.get_chat_response(chat_prompt, prompt=prompt, **kwargs)
