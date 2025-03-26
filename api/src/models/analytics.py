from datetime import datetime
import json

from .db import db

class ConversationMetrics(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'), nullable=False)
    chatbot_id = db.Column(db.Integer, db.ForeignKey('chat_bot.id'), nullable=False)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversation.id'), nullable=False)
    
    # Metrics
    message_count = db.Column(db.Integer, default=0)
    duration_seconds = db.Column(db.Integer)
    lead_captured = db.Column(db.Boolean, default=False)
    completed = db.Column(db.Boolean, default=False)
    
    # User timing
    time_of_day = db.Column(db.String(20))  # 'business', 'evening', 'weekend'
    day_of_week = db.Column(db.Integer)
    hour_of_day = db.Column(db.Integer)
    
    # Source tracking
    utm_source = db.Column(db.String(100))
    utm_medium = db.Column(db.String(100))
    utm_campaign = db.Column(db.String(100))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class DailyMetrics(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'), nullable=False)
    chatbot_id = db.Column(db.Integer, db.ForeignKey('chat_bot.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    
    # Aggregated metrics
    conversation_count = db.Column(db.Integer, default=0)
    message_count = db.Column(db.Integer, default=0)
    lead_count = db.Column(db.Integer, default=0)
    avg_conversation_duration = db.Column(db.Float)
    completion_rate = db.Column(db.Float)
    
    # Source breakdown
    _source_breakdown = db.Column(db.Text, default='{}')
    
    # Time of day breakdown
    _time_breakdown = db.Column(db.Text, default='{}')
    
    @property
    def source_breakdown(self):
        return json.loads(self._source_breakdown)
    
    @source_breakdown.setter
    def source_breakdown(self, data):
        self._source_breakdown = json.dumps(data)
    
    @property
    def time_breakdown(self):
        return json.loads(self._time_breakdown)
    
    @time_breakdown.setter
    def time_breakdown(self, data):
        self._time_breakdown = json.dumps(data)
