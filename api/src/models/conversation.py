from datetime import datetime
import json

from .db import db

class Conversation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chatbot_id = db.Column(db.Integer, db.ForeignKey('chat_bot.id'), nullable=False)
    visitor_id = db.Column(db.String(255))
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    ended_at = db.Column(db.DateTime)
    status = db.Column(db.String(50), default='active')
    
    # UTM tracking
    utm_source = db.Column(db.String(100))
    utm_medium = db.Column(db.String(100))
    utm_campaign = db.Column(db.String(100))
    referrer_url = db.Column(db.String(500))
    
    # Visitor data
    _visitor_data = db.Column(db.Text, default='{}')
    
    # Relationships
    messages = db.relationship('Message', backref='conversation', lazy='dynamic', cascade='all, delete-orphan')
    
    @property
    def visitor_data(self):
        return json.loads(self._visitor_data)
    
    @visitor_data.setter
    def visitor_data(self, data):
        self._visitor_data = json.dumps(data)
    
    @property
    def duration(self):
        """Calculate conversation duration in seconds"""
        if not self.ended_at:
            return None
        return (self.ended_at - self.started_at).total_seconds()
