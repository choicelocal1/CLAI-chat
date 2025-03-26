from datetime import datetime

from .db import db

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversation.id'), nullable=False)
    sender_type = db.Column(db.String(20), nullable=False)  # 'bot' or 'human'
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # LLM metadata
    token_count = db.Column(db.Integer)
    llm_model_used = db.Column(db.String(100))
    
    def to_dict(self):
        return {
            'id': self.id,
            'conversation_id': self.conversation_id,
            'sender_type': self.sender_type,
            'content': self.content,
            'timestamp': self.timestamp.isoformat(),
            'token_count': self.token_count,
            'llm_model_used': self.llm_model_used
        }
