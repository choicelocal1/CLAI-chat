import json
import time
from datetime import datetime

from models import db, Conversation, Message, ConversationMetrics, ChatBot, KnowledgeBase
from .llm_service import LLMService
from .knowledge_service import KnowledgeService

class ConversationService:
    def __init__(self, chatbot, organization_id, visitor_id=None):
        """
        Initialize conversation service for a specific chatbot
        """
        self.chatbot = chatbot
        self.organization_id = organization_id
        self.visitor_id = visitor_id
        self.llm_service = LLMService()
        self.knowledge_service = KnowledgeService()
    
    def start_conversation(self, utm_params=None, referrer=None):
        """
        Start a new conversation and return the conversation object
        """
        # Create conversation
        conversation = Conversation(
            chatbot_id=self.chatbot.id,
            visitor_id=self.visitor_id,
            status='active',
            utm_source=utm_params.get('source') if utm_params else None,
            utm_medium=utm_params.get('medium') if utm_params else None,
            utm_campaign=utm_params.get('campaign') if utm_params else None,
            referrer_url=referrer
        )
        
        db.session.add(conversation)
        db.session.commit()
        
        # Create metrics entry
        metrics = self._create_metrics_entry(conversation)
        
        return conversation
    
    def process_message(self, conversation_id, message_content):
        """
        Process a user message and generate a response
        """
        # Get conversation
        conversation = Conversation.query.get(conversation_id)
        if not conversation or conversation.status != 'active':
            return {'error': 'Conversation not found or inactive'}
        
        # Save user message
        user_message = Message(
            conversation_id=conversation_id,
            sender_type='human',
            content=message_content
        )
        db.session.add(user_message)
        db.session.commit()
        
        # Get conversation history
        history = self._get_conversation_history(conversation_id)
        
        # Check knowledge base first
        kb_response = self._check_knowledge_base(message_content)
        
        if kb_response:
            response_content = kb_response
            model_used = "knowledge_base"
        else:
            # Generate bot response using LLM
            system_template = f"""
            You are a helpful assistant for {self.chatbot.name}.
            
            DO SAY:
            {self.chatbot.allowed_responses}
            
            DO NOT SAY:
            {self.chatbot.forbidden_responses}
            """
            
            human_template = "{message}"
            
            prompt = self.llm_service.create_prompt_template(system_template, human_template)
            response = self.llm_service.get_chat_response(prompt, message=message_content)
            
            response_content = response['content']
            model_used = response['model']
        
        # Save bot response
        bot_message = Message(
            conversation_id=conversation_id,
            sender_type='bot',
            content=response_content,
            token_count=len(response_content.split()) * 1.3,  # Rough estimate
            llm_model_used=model_used
        )
        db.session.add(bot_message)
        
        # Update metrics
        self._update_metrics(conversation)
        
        db.session.commit()
        
        return {
            'message_id': bot_message.id,
            'content': bot_message.content
        }
    
    def _check_knowledge_base(self, query):
        """
        Check if the query can be answered from the knowledge base
        """
        # Get knowledge bases for this chatbot
        knowledge_bases = KnowledgeBase.query.filter_by(chatbot_id=self.chatbot.id).all()
        
        if not knowledge_bases:
            return None
        
        # Search all knowledge bases for this chatbot
        for kb in knowledge_bases:
            results = self.knowledge_service.search_knowledge_base(
                knowledge_base_id=kb.id,
                query=query,
                threshold=0.8  # Higher threshold for more confident matches
            )
            
            if results:
                # Use the highest similarity match
                best_match = results[0]
                return best_match['answer']
        
        return None
    
    def end_conversation(self, conversation_id):
        """
        End a conversation
        """
        conversation = Conversation.query.get(conversation_id)
        if not conversation:
            return {'error': 'Conversation not found'}
        
        conversation.status = 'ended'
        conversation.ended_at = datetime.utcnow()
        
        # Update metrics
        metrics = ConversationMetrics.query.filter_by(conversation_id=conversation_id).first()
        if metrics:
            metrics.duration_seconds = conversation.duration
            metrics.completed = True
        
        db.session.commit()
        
        return {'success': True}
    
    def get_conversation(self, conversation_id):
        """
        Get a conversation and its messages
        """
        conversation = Conversation.query.get(conversation_id)
        if not conversation:
            return {'error': 'Conversation not found'}
        
        messages = Message.query.filter_by(conversation_id=conversation_id).order_by(Message.timestamp).all()
        
        return {
            'conversation': {
                'id': conversation.id,
                'started_at': conversation.started_at.isoformat(),
                'ended_at': conversation.ended_at.isoformat() if conversation.ended_at else None,
                'status': conversation.status,
                'visitor_id': conversation.visitor_id,
                'utm_source': conversation.utm_source,
                'utm_medium': conversation.utm_medium,
                'utm_campaign': conversation.utm_campaign,
                'referrer_url': conversation.referrer_url
            },
            'messages': [message.to_dict() for message in messages]
        }
    
    def _get_conversation_history(self, conversation_id, limit=10):
        """
        Get the recent message history for a conversation
        """
        messages = Message.query.filter_by(conversation_id=conversation_id).order_by(Message.timestamp.desc()).limit(limit).all()
        messages.reverse()  # Get in chronological order
        
        return messages
    
    def _create_metrics_entry(self, conversation):
        """
        Create a new metrics entry for a conversation
        """
        now = datetime.utcnow()
        hour = now.hour
        
        # Determine time of day
        if 9 <= hour < 17:  # 9 AM - 5 PM
            time_of_day = 'business'
        elif 17 <= hour < 22:  # 5 PM - 10 PM
            time_of_day = 'evening'
        else:
            time_of_day = 'night'
        
        # Weekend check
        day_of_week = now.weekday()
        if day_of_week >= 5:  # Saturday or Sunday
            time_of_day = 'weekend'
        
        metrics = ConversationMetrics(
            organization_id=self.organization_id,
            chatbot_id=self.chatbot.id,
            conversation_id=conversation.id,
            message_count=0,
            lead_captured=False,
            completed=False,
            time_of_day=time_of_day,
            day_of_week=day_of_week,
            hour_of_day=hour,
            utm_source=conversation.utm_source,
            utm_medium=conversation.utm_medium,
            utm_campaign=conversation.utm_campaign
        )
        
        db.session.add(metrics)
        db.session.commit()
        
        return metrics
    
    def _update_metrics(self, conversation):
        """
        Update metrics for a conversation
        """
        metrics = ConversationMetrics.query.filter_by(conversation_id=conversation.id).first()
        if metrics:
            message_count = Message.query.filter_by(conversation_id=conversation.id).count()
            metrics.message_count = message_count
            
            # Update in database
            db.session.add(metrics)
