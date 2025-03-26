from functools import wraps
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from flask import jsonify

from models.user import User, Role

def role_required(role_names):
    """
    Decorator for role-based access control
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            
            if not user:
                return jsonify({"error": "User not found"}), 404
            
            # Convert to list if single role provided
            roles = role_names if isinstance(role_names, list) else [role_names]
            
            if user.role and user.role.name in roles:
                return fn(*args, **kwargs)
            
            return jsonify({"error": "Insufficient permissions"}), 403
        return wrapper
    return decorator

def has_organization_access(org_id, allow_admin=True):
    """
    Check if current user has access to the organization
    """
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return False
    
    # Admin users have access to all organizations if allowed
    if allow_admin and user.role and user.role.name == 'admin':
        return True
    
    # Users have access to their own organization
    return user.organization_id == org_id
