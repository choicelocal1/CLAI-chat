from datetime import datetime
import json

from .db import db

class Lead(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'), nullable=False)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversation.id'))
    
    # Basic lead info
    name = db.Column(db.String(255))
    email = db.Column(db.String(255))
    phone = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Additional data
    _custom_fields = db.Column(db.Text, default='{}')
    _enrichment_data = db.Column(db.Text, default='{}')
    
    # UTM tracking
    utm_source = db.Column(db.String(100))
    utm_medium = db.Column(db.String(100))
    utm_campaign = db.Column(db.String(100))
    
    # Status
    status = db.Column(db.String(50), default='new')
    
    @property
    def custom_fields(self):
        return json.loads(self._custom_fields)
    
    @custom_fields.setter
    def custom_fields(self, data):
        self._custom_fields = json.dumps(data)
    
    @property
    def enrichment_data(self):
        return json.loads(self._enrichment_data)
    
    @enrichment_data.setter
    def enrichment_data(self, data):
        self._enrichment_data = json.dumps(data)
