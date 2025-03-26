from datetime import datetime
import json

from .db import db

class KnowledgeBase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'), nullable=False)
    chatbot_id = db.Column(db.Integer, db.ForeignKey('chat_bot.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Knowledge items relationship
    items = db.relationship('KnowledgeItem', backref='knowledge_base', lazy='dynamic', cascade='all, delete-orphan')

class KnowledgeItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    knowledge_base_id = db.Column(db.Integer, db.ForeignKey('knowledge_base.id'), nullable=False)
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Vector embedding for similarity search
    _embedding = db.Column(db.Text)
    
    @property
    def embedding(self):
        if self._embedding:
            return json.loads(self._embedding)
        return None
    
    @embedding.setter
    def embedding(self, data):
        self._embedding = json.dumps(data) if data is not None else None
