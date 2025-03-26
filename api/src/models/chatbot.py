from datetime import datetime
import json

from .db import db

class ChatBot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Configuration
    _config = db.Column(db.Text, default='{}')
    allowed_responses = db.Column(db.Text, default='')
    forbidden_responses = db.Column(db.Text, default='')
    
    # Relationships
    conversations = db.relationship('Conversation', backref='chatbot', lazy='dynamic')
    
    @property
    def config(self):
        return json.loads(self._config)
    
    @config.setter
    def config(self, config_dict):
        self._config = json.dumps(config_dict)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'organization_id': self.organization_id,
            'config': self.config,
            'allowed_responses': self.allowed_responses,
            'forbidden_responses': self.forbidden_responses,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
