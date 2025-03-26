from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from models import db, Organization, User
from utils.permissions import has_organization_access, role_required

organization_routes = Blueprint('organization', __name__, url_prefix='/api/organizations')

@organization_routes.route('/', methods=['POST'])
@jwt_required()
@role_required(['admin'])
def create_organization():
    """Create a new organization (requires admin role)"""
    data = request.json
    
    # Validate required fields
    if not data.get('name'):
        return jsonify({'error': 'name is required'}), 400
    
    # Create organization
    organization = Organization(
        name=data.get('name'),
        website=data.get('website', '')
    )
    
    # Set subscription tier if provided
    if data.get('subscription_tier'):
        organization.subscription_tier = data.get('subscription_tier')
    
    # Set LLM settings if provided
    if data.get('llm_settings'):
        organization.llm_settings = data.get('llm_settings')
    
    db.session.add(organization)
    db.session.commit()
    
    return jsonify({
        'id': organization.id,
        'name': organization.name
    }), 201

@organization_routes.route('/', methods=['GET'])
@jwt_required()
def list_organizations():
    """List organizations (admin sees all, others see only their own)"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    # Admin sees all organizations, others see only their own
    if user.role and user.role.name == 'admin':
        organizations = Organization.query.all()
    else:
        organizations = [Organization.query.get(user.organization_id)] if user.organization_id else []
    
    return jsonify([{
        'id': org.id,
        'name': org.name,
        'website': org.website,
        'subscription_tier': org.subscription_tier,
        'created_at': org.created_at.isoformat()
    } for org in organizations]), 200

@organization_routes.route('/<int:organization_id>', methods=['GET'])
@jwt_required()
def get_organization(organization_id):
    """Get organization details (requires access to the organization)"""
    # Check permissions
    if not has_organization_access(organization_id):
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Get organization
    organization = Organization.query.get(organization_id)
    if not organization:
        return jsonify({'error': 'Organization not found'}), 404
    
    return jsonify({
        'id': organization.id,
        'name': organization.name,
        'website': organization.website,
        'subscription_tier': organization.subscription_tier,
        'llm_settings': organization.llm_settings,
        'created_at': organization.created_at.isoformat(),
        'updated_at': organization.updated_at.isoformat()
    }), 200

@organization_routes.route('/<int:organization_id>', methods=['PUT'])
@jwt_required()
def update_organization(organization_id):
    """Update organization (requires access to the organization)"""
    data = request.json
    
    # Check permissions
    if not has_organization_access(organization_id):
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Get organization
    organization = Organization.query.get(organization_id)
    if not organization:
        return jsonify({'error': 'Organization not found'}), 404
    
    # Update fields
    if 'name' in data:
        organization.name = data['name']
    if 'website' in data:
        organization.website = data['website']
    if 'llm_settings' in data:
        # Only admin or manager can update LLM settings
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if user.role and user.role.name in ['admin', 'manager']:
            organization.llm_settings = data['llm_settings']
        else:
            return jsonify({'error': 'Unauthorized to update LLM settings'}), 403
    
    db.session.commit()
    
    return jsonify({
        'id': organization.id,
        'status': 'updated'
    }), 200

@organization_routes.route('/<int:organization_id>/users', methods=['GET'])
@jwt_required()
def list_organization_users(organization_id):
    """List users in an organization (requires access to the organization)"""
    # Check permissions
    if not has_organization_access(organization_id):
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Get users
    users = User.query.filter_by(organization_id=organization_id).all()
    
    return jsonify([{
        'id': user.id,
        'email': user.email,
        'name': user.name,
        'role': user.role.name if user.role else None,
        'active': user.active
    } for user in users]), 200
