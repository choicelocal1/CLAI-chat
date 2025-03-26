from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from models import User
from services.webhook_service import WebhookService
from utils.permissions import has_organization_access

webhook_routes = Blueprint('webhook', __name__, url_prefix='/api/webhooks')
webhook_service = WebhookService()

@webhook_routes.route('/', methods=['GET'])
@jwt_required()
def get_webhooks():
    """Get webhooks for organization"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    # Get organization_id from query params or use user's organization
    organization_id = request.args.get('organization_id', type=int) or user.organization_id
    
    # Check permissions
    if not has_organization_access(organization_id):
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Get webhooks
    webhooks = webhook_service.get_webhooks(organization_id)
    
    return jsonify([{
        'id': webhook.id,
        'name': webhook.name,
        'url': webhook.url,
        'events': webhook.events,
        'is_active': webhook.is_active,
        'created_at': webhook.created_at.isoformat()
    } for webhook in webhooks]), 200

@webhook_routes.route('/', methods=['POST'])
@jwt_required()
def create_webhook():
    """Create webhook"""
    data = request.json
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    # Get organization_id from request or use user's organization
    organization_id = data.get('organization_id') or user.organization_id
    
    # Check permissions
    if not has_organization_access(organization_id):
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Validate required fields
    if not data.get('name') or not data.get('url'):
        return jsonify({'error': 'name and url are required'}), 400
    
    if not data.get('events') or not isinstance(data.get('events'), list):
        return jsonify({'error': 'events must be a non-empty array'}), 400
    
    # Create webhook
    webhook = webhook_service.create_webhook(
        organization_id=organization_id,
        name=data.get('name'),
        url=data.get('url'),
        events=data.get('events'),
        secret=data.get('secret'),
        headers=data.get('headers')
    )
    
    return jsonify({
        'id': webhook.id,
        'name': webhook.name,
        'url': webhook.url,
        'events': webhook.events,
        'created_at': webhook.created_at.isoformat()
    }), 201

@webhook_routes.route('/<int:webhook_id>', methods=['GET'])
@jwt_required()
def get_webhook(webhook_id):
    """Get webhook details"""
    # Get webhook
    webhook = webhook_service.get_webhook(webhook_id)
    if not webhook:
        return jsonify({'error': 'Webhook not found'}), 404
    
    # Check permissions
    if not has_organization_access(webhook.organization_id):
        return jsonify({'error': 'Unauthorized'}), 403
    
    return jsonify({
        'id': webhook.id,
        'name': webhook.name,
        'url': webhook.url,
        'events': webhook.events,
        'headers': webhook.headers,
        'is_active': webhook.is_active,
        'created_at': webhook.created_at.isoformat(),
        'updated_at': webhook.updated_at.isoformat()
    }), 200

@webhook_routes.route('/<int:webhook_id>', methods=['PUT'])
@jwt_required()
def update_webhook(webhook_id):
    """Update webhook"""
    data = request.json
    
    # Get webhook
    webhook = webhook_service.get_webhook(webhook_id)
    if not webhook:
        return jsonify({'error': 'Webhook not found'}), 404
    
    # Check permissions
    if not has_organization_access(webhook.organization_id):
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Update webhook
    updated_webhook = webhook_service.update_webhook(
        webhook_id=webhook_id,
        name=data.get('name'),
        url=data.get('url'),
        events=data.get('events'),
        secret=data.get('secret'),
        headers=data.get('headers'),
        is_active=data.get('is_active')
    )
    
    return jsonify({
        'id': updated_webhook.id,
        'status': 'updated'
    }), 200

@webhook_routes.route('/<int:webhook_id>', methods=['DELETE'])
@jwt_required()
def delete_webhook(webhook_id):
    """Delete webhook"""
    # Get webhook
    webhook = webhook_service.get_webhook(webhook_id)
    if not webhook:
        return jsonify({'error': 'Webhook not found'}), 404
    
    # Check permissions
    if not has_organization_access(webhook.organization_id):
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Delete webhook
    success = webhook_service.delete_webhook(webhook_id)
    
    if success:
        return jsonify({'status': 'deleted'}), 200
    else:
        return jsonify({'error': 'Failed to delete webhook'}), 500

@webhook_routes.route('/<int:webhook_id>/logs', methods=['GET'])
@jwt_required()
def get_webhook_logs(webhook_id):
    """Get webhook logs"""
    # Get webhook
    webhook = webhook_service.get_webhook(webhook_id)
    if not webhook:
        return jsonify({'error': 'Webhook not found'}), 404
    
    # Check permissions
    if not has_organization_access(webhook.organization_id):
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Get logs
    limit = request.args.get('limit', 100, type=int)
    logs = webhook_service.get_webhook_logs(webhook_id, limit)
    
    return jsonify([{
        'id': log.id,
        'event': log.event,
        'success': log.success,
        'response_status': log.response_status,
        'created_at': log.created_at.isoformat()
    } for log in logs]), 200

@webhook_routes.route('/<int:webhook_id>/test', methods=['POST'])
@jwt_required()
def test_webhook(webhook_id):
    """Test webhook with a test event"""
    # Get webhook
    webhook = webhook_service.get_webhook(webhook_id)
    if not webhook:
        return jsonify({'error': 'Webhook not found'}), 404
    
    # Check permissions
    if not has_organization_access(webhook.organization_id):
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Prepare test payload
    payload = {
        'event': 'test',
        'message': 'This is a test webhook event',
        'organization_id': webhook.organization_id
    }
    
    # Send test webhook
    result = webhook_service._send_webhook_request(webhook, 'test', payload)
    
    return jsonify(result), 200
