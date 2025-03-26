from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime

from models import db, Lead, Conversation, User
from utils.permissions import has_organization_access

lead_routes = Blueprint('lead', __name__, url_prefix='/api/leads')

@lead_routes.route('/', methods=['POST'])
def create_lead():
    """Create a new lead from chat widget"""
    data = request.json
    
    # Validate required fields
    if not data.get('organization_id'):
        return jsonify({'error': 'organization_id is required'}), 400
    
    # Create lead
    lead = Lead(
        organization_id=data.get('organization_id'),
        conversation_id=data.get('conversation_id'),
        name=data.get('name'),
        email=data.get('email'),
        phone=data.get('phone'),
        utm_source=data.get('utm_source'),
        utm_medium=data.get('utm_medium'),
        utm_campaign=data.get('utm_campaign'),
        status='new'
    )
    
    # Set custom fields if provided
    if data.get('custom_fields'):
        lead.custom_fields = data.get('custom_fields')
    
    db.session.add(lead)
    db.session.commit()
    
    # TODO: If organization has integrations enabled, trigger those
    
    return jsonify({
        'lead_id': lead.id,
        'status': 'created'
    }), 201

@lead_routes.route('/', methods=['GET'])
@jwt_required()
def list_leads():
    """List leads for an organization (requires authentication)"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    # Get query parameters
    organization_id = request.args.get('organization_id', type=int) or user.organization_id
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status')
    
    # Check permissions
    if not has_organization_access(organization_id):
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Build query
    query = Lead.query.filter_by(organization_id=organization_id)
    
    if status:
        query = query.filter_by(status=status)
    
    # Paginate
    paginated = query.order_by(Lead.created_at.desc()).paginate(
        page=page, per_page=per_page
    )
    
    return jsonify({
        'total': paginated.total,
        'pages': paginated.pages,
        'current_page': page,
        'per_page': per_page,
        'items': [{
            'id': lead.id,
            'name': lead.name,
            'email': lead.email,
            'phone': lead.phone,
            'status': lead.status,
            'created_at': lead.created_at.isoformat(),
            'utm_source': lead.utm_source,
            'utm_medium': lead.utm_medium,
            'utm_campaign': lead.utm_campaign,
            'custom_fields': lead.custom_fields
        } for lead in paginated.items]
    }), 200

@lead_routes.route('/<int:lead_id>', methods=['GET'])
@jwt_required()
def get_lead(lead_id):
    """Get lead details (requires authentication)"""
    # Get lead
    lead = Lead.query.get(lead_id)
    if not lead:
        return jsonify({'error': 'Lead not found'}), 404
    
    # Check permissions
    if not has_organization_access(lead.organization_id):
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Get associated conversation if exists
    conversation = None
    if lead.conversation_id:
        conv = Conversation.query.get(lead.conversation_id)
        if conv:
            conversation = {
                'id': conv.id,
                'started_at': conv.started_at.isoformat(),
                'ended_at': conv.ended_at.isoformat() if conv.ended_at else None
            }
    
    return jsonify({
        'id': lead.id,
        'name': lead.name,
        'email': lead.email,
        'phone': lead.phone,
        'status': lead.status,
        'created_at': lead.created_at.isoformat(),
        'utm_source': lead.utm_source,
        'utm_medium': lead.utm_medium,
        'utm_campaign': lead.utm_campaign,
        'custom_fields': lead.custom_fields,
        'enrichment_data': lead.enrichment_data,
        'conversation': conversation
    }), 200

@lead_routes.route('/<int:lead_id>', methods=['PUT'])
@jwt_required()
def update_lead(lead_id):
    """Update lead (requires authentication)"""
    data = request.json
    
    # Get lead
    lead = Lead.query.get(lead_id)
    if not lead:
        return jsonify({'error': 'Lead not found'}), 404
    
    # Check permissions
    if not has_organization_access(lead.organization_id):
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Update fields
    if 'name' in data:
        lead.name = data['name']
    if 'email' in data:
        lead.email = data['email']
    if 'phone' in data:
        lead.phone = data['phone']
    if 'status' in data:
        lead.status = data['status']
    if 'custom_fields' in data:
        lead.custom_fields = data['custom_fields']
    
    db.session.commit()
    
    return jsonify({
        'id': lead.id,
        'status': 'updated'
    }), 200
