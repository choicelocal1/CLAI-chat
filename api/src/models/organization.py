from datetime import datetime
import json

from .db import db

class Organization(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    website = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Subscription data
    subscription_tier = db.Column(db.String(50), default='free')
    subscription_id = db.Column(db.String(255))
    
    # LLM settings
    _llm_settings = db.Column(db.Text, default='{}')
    
    # Relationships
    users = db.relationship('User', backref='organization', lazy='dynamic')
    chatbots = db.relationship('ChatBot', backref='organization', lazy='dynamic')
    
    @property
    def llm_settings(self):
        return json.loads(self._llm_settings)
    
    @llm_settings.setter
    def llm_settings(self, settings):
        self._llm_settings = json.dumps(settings)
