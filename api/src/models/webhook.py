from datetime import datetime
import json

from .db import db

class Webhook(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(255), nullable=False)
    secret = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Events to trigger webhook
    _events = db.Column(db.Text, default='[]')
    
    # Headers to include with request
    _headers = db.Column(db.Text, default='{}')
    
    @property
    def events(self):
        return json.loads(self._events)
    
    @events.setter
    def events(self, event_list):
        self._events = json.dumps(event_list)
    
    @property
    def headers(self):
        return json.loads(self._headers)
    
    @headers.setter
    def headers(self, headers_dict):
        self._headers = json.dumps(headers_dict)

class WebhookLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    webhook_id = db.Column(db.Integer, db.ForeignKey('webhook.id'), nullable=False)
    event = db.Column(db.String(100), nullable=False)
    request_data = db.Column(db.Text)
    response_status = db.Column(db.Integer)
    response_body = db.Column(db.Text)
    success = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    webhook = db.relationship('Webhook', backref='logs')
