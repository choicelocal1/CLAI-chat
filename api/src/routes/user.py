from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash

from models import db, User, Role, Organization
from utils.permissions import has_organization_access, role_required

user_routes = Blueprint('user', __name__, url_prefix='/api/users')

@user_routes.route('/', methods=['POST'])
@jwt_required()
@role_required(['admin', 'manager'])
def create_user():
    """Create a new user (requires admin or manager role)"""
    data = request.json
    user_id = get_jwt_identity()
    current_user = User.query.get(user_id)
    
    # Validate required fields
    if not data.get('email') or not data.get('password'):
        return jsonify({'error': 'email and password are required'}), 400
    
    # Check if user already exists
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 409
    
    # Determine organization_id
    if current_user.role.name == 'admin':
        # Admin can create users in any organization
        organization_id = data.get('organization_id')
    else:
        # Managers can only create users in their organization
        organization_id = current_user.organization_id
    
    # Get role
    role_name = data.get('role', 'member')
    # Restrict role assignment - managers can only create members
    if current_user.role.name == 'manager' and role_name != 'member':
        return jsonify({'error': 'Unauthorized to assign this role'}), 403
    
    role = Role.query.filter_by(name=role_name).first()
    if not role:
        return jsonify({'error': 'Invalid role'}), 400
    
    # Create user
    user = User(
        email=data['email'],
        name=data.get('name', ''),
        organization_id=organization_id,
        role_id=role.id,
        active=True
    )
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({
        'id': user.id,
        'email': user.email,
        'role': role.name
    }), 201

@user_routes.route('/', methods=['GET'])
@jwt_required()
@role_required(['admin'])
def list_users():
    """List all users (admin only)"""
    users = User.query.all()
    
    return jsonify([{
        'id': user.id,
        'email': user.email,
        'name': user.name,
        'organization_id': user.organization_id,
        'role': user.role.name if user.role else None,
        'active': user.active
    } for user in users]), 200

@user_routes.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current user profile"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Get organization details if user has one
    organization = None
    if user.organization_id:
        org = Organization.query.get(user.organization_id)
        if org:
            organization = {
                'id': org.id,
                'name': org.name,
                'subscription_tier': org.subscription_tier
            }
    
    return jsonify({
        'id': user.id,
        'email': user.email,
        'name': user.name,
        'role': user.role.name if user.role else None,
        'active': user.active,
        'organization': organization
    }), 200

@user_routes.route('/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    """Get user details (admin can get any user, others can only get users in their organization)"""
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    # Get user
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Check permissions
    if current_user.role.name != 'admin' and user.organization_id != current_user.organization_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    return jsonify({
        'id': user.id,
        'email': user.email,
        'name': user.name,
        'organization_id': user.organization_id,
        'role': user.role.name if user.role else None,
        'active': user.active,
        'created_at': user.created_at.isoformat()
    }), 200

@user_routes.route('/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    """Update user (admin can update any user, managers can update members in their organization, users can update themselves)"""
    data = request.json
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    # Get user to update
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Check permissions
    is_self = current_user_id == user_id
    is_admin = current_user.role.name == 'admin'
    is_manager = current_user.role.name == 'manager' and user.organization_id == current_user.organization_id and user.role.name == 'member'
    
    if not (is_self or is_admin or is_manager):
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Update basic fields (self, admin, or manager can update)
    if 'name' in data:
        user.name = data['name']
    
    # Update email (self or admin only)
    if 'email' in data and (is_self or is_admin):
        # Check if email is already taken
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user and existing_user.id != user_id:
            return jsonify({'error': 'Email already in use'}), 409
        user.email = data['email']
    
    # Update password (self or admin only)
    if 'password' in data and (is_self or is_admin):
        user.set_password(data['password'])
    
    # Update role (admin only)
    if 'role' in data and is_admin:
        role = Role.query.filter_by(name=data['role']).first()
        if not role:
            return jsonify({'error': 'Invalid role'}), 400
        user.role_id = role.id
    
    # Update organization (admin only)
    if 'organization_id' in data and is_admin:
        organization = Organization.query.get(data['organization_id'])
        if not organization:
            return jsonify({'error': 'Organization not found'}), 404
        user.organization_id = organization.id
    
    # Update active status (admin only)
    if 'active' in data and is_admin:
        user.active = data['active']
    
    db.session.commit()
    
    return jsonify({
        'id': user.id,
        'status': 'updated'
    }), 200

@user_routes.route('/<int:user_id>', methods=['DELETE'])
@jwt_required()
@role_required(['admin'])
def delete_user(user_id):
    """Delete user (admin only)"""
    # Get user
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Delete user
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({
        'status': 'deleted'
    }), 200
