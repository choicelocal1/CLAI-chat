import json
import requests
import hmac
import hashlib
import time
from datetime import datetime

from models import db, Webhook, WebhookLog, Organization

class WebhookService:
    def __init__(self):
        pass
    
    def create_webhook(self, organization_id, name, url, events, secret=None, headers=None):
        """Create a new webhook"""
        webhook = Webhook(
            organization_id=organization_id,
            name=name,
            url=url,
            secret=secret,
            events=events,
            headers=headers or {}
        )
        
        db.session.add(webhook)
        db.session.commit()
        
        return webhook
    
    def get_webhooks(self, organization_id):
        """Get all webhooks for an organization"""
        return Webhook.query.filter_by(
            organization_id=organization_id,
            is_active=True
        ).all()
    
    def get_webhook(self, webhook_id):
        """Get a specific webhook"""
        return Webhook.query.get(webhook_id)
    
    def update_webhook(self, webhook_id, **kwargs):
        """Update webhook properties"""
        webhook = Webhook.query.get(webhook_id)
        
        if not webhook:
            return None
        
        # Update allowed fields
        if 'name' in kwargs:
            webhook.name = kwargs['name']
        
        if 'url' in kwargs:
            webhook.url = kwargs['url']
        
        if 'secret' in kwargs:
            webhook.secret = kwargs['secret']
        
        if 'events' in kwargs:
            webhook.events = kwargs['events']
        
        if 'headers' in kwargs:
            webhook.headers = kwargs['headers']
        
        if 'is_active' in kwargs:
            webhook.is_active = kwargs['is_active']
        
        db.session.commit()
        
        return webhook
    
    def delete_webhook(self, webhook_id):
        """Delete a webhook"""
        webhook = Webhook.query.get(webhook_id)
        
        if not webhook:
            return False
        
        db.session.delete(webhook)
        db.session.commit()
        
        return True
    
    def trigger_webhook_event(self, organization_id, event, payload):
        """Trigger webhooks for a specific event"""
        # Get all active webhooks for this organization that listen to this event
        webhooks = Webhook.query.filter(
            Webhook.organization_id == organization_id,
            Webhook.is_active == True,
            Webhook._events.like(f'%"{event}"%')
        ).all()
        
        results = []
        
        for webhook in webhooks:
            # Add timestamp to payload
            payload['timestamp'] = int(time.time())
            payload['event'] = event
            
            # Send webhook request
            result = self._send_webhook_request(webhook, event, payload)
            results.append(result)
        
        return results
    
    def _send_webhook_request(self, webhook, event, payload):
        """Send a webhook request and log the result"""
        # Prepare headers
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'CLAI-Chat-Webhook/1.0',
            'X-CLAI-Event': event
        }
        
        # Add custom headers
        headers.update(webhook.headers)
        
        # Add signature if secret is set
        if webhook.secret:
            signature = self._generate_signature(webhook.secret, payload)
            headers['X-CLAI-Signature'] = signature
        
        # Convert payload to JSON
        json_payload = json.dumps(payload)
        
        # Create log entry
        log_entry = WebhookLog(
            webhook_id=webhook.id,
            event=event,
            request_data=json_payload
        )
        
        try:
            # Send request
            response = requests.post(
                webhook.url,
                headers=headers,
                data=json_payload,
                timeout=5  # 5 second timeout
            )
            
            # Update log with response
            log_entry.response_status = response.status_code
            log_entry.response_body = response.text[:1000]  # Limit response size
            log_entry.success = 200 <= response.status_code < 300
            
            # Save log
            db.session.add(log_entry)
            db.session.commit()
            
            return {
                'webhook_id': webhook.id,
                'event': event,
                'success': log_entry.success,
                'status_code': response.status_code
            }
        
        except Exception as e:
            # Log error
            log_entry.response_status = 0
            log_entry.response_body = str(e)[:1000]
            log_entry.success = False
            
            # Save log
            db.session.add(log_entry)
            db.session.commit()
            
            return {
                'webhook_id': webhook.id,
                'event': event,
                'success': False,
                'error': str(e)
            }
    
    def _generate_signature(self, secret, payload):
        """Generate HMAC signature for webhook payload"""
        json_payload = json.dumps(payload)
        signature = hmac.new(
            secret.encode(),
            json_payload.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return signature
    
    def get_webhook_logs(self, webhook_id, limit=100):
        """Get logs for a specific webhook"""
        return WebhookLog.query.filter_by(webhook_id=webhook_id).order_by(WebhookLog.created_at.desc()).limit(limit).all()
