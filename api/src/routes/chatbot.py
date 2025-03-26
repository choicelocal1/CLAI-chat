from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from models import db, ChatBot, Organization, User
from utils.permissions import has_organization_access

chatbot_routes = Blueprint('chatbot', __name__, url_prefix='/api/chatbots')

@chatbot_routes.route('/', methods=['POST'])
@jwt_required()
def create_chatbot():
    """Create a new chatbot (requires authentication)"""
    data = request.json
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    # Get organization_id from request or use user's organization
    organization_id = data.get('organization_id') or user.organization_id
    
    # Check permissions
    if not has_organization_access(organization_id):
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Validate required fields
    if not data.get('name'):
        return jsonify({'error': 'name is required'}), 400
    
    # Create chatbot
    chatbot = ChatBot(
        name=data.get('name'),
        organization_id=organization_id,
        allowed_responses=data.get('allowed_responses', ''),
        forbidden_responses=data.get('forbidden_responses', '')
    )
    
    # Set config if provided
    if data.get('config'):
        chatbot.config = data.get('config')
    
    db.session.add(chatbot)
    db.session.commit()
    
    return jsonify({
        'id': chatbot.id,
        'name': chatbot.name,
        'organization_id': chatbot.organization_id
    }), 201

@chatbot_routes.route('/', methods=['GET'])
@jwt_required()
def list_chatbots():
    """List chatbots for an organization (requires authentication)"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    # Get organization_id from query params or use user's organization
    organization_id = request.args.get('organization_id', type=int) or user.organization_id
    
    # Check permissions
    if not has_organization_access(organization_id):
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Get chatbots
    chatbots = ChatBot.query.filter_by(organization_id=organization_id).all()
    
    return jsonify([{
        'id': chatbot.id,
        'name': chatbot.name,
        'organization_id': chatbot.organization_id,
        'created_at': chatbot.created_at.isoformat()
    } for chatbot in chatbots]), 200

@chatbot_routes.route('/<int:chatbot_id>', methods=['GET'])
@jwt_required()
def get_chatbot(chatbot_id):
    """Get chatbot details (requires authentication)"""
    # Get chatbot
    chatbot = ChatBot.query.get(chatbot_id)
    if not chatbot:
        return jsonify({'error': 'Chatbot not found'}), 404
    
    # Check permissions
    if not has_organization_access(chatbot.organization_id):
        return jsonify({'error': 'Unauthorized'}), 403
    
    return jsonify({
        'id': chatbot.id,
        'name': chatbot.name,
        'organization_id': chatbot.organization_id,
        'config': chatbot.config,
        'allowed_responses': chatbot.allowed_responses,
        'forbidden_responses': chatbot.forbidden_responses,
        'created_at': chatbot.created_at.isoformat(),
        'updated_at': chatbot.updated_at.isoformat()
    }), 200

@chatbot_routes.route('/<int:chatbot_id>', methods=['PUT'])
@jwt_required()
def update_chatbot(chatbot_id):
    """Update chatbot (requires authentication)"""
    data = request.json
    
    # Get chatbot
    chatbot = ChatBot.query.get(chatbot_id)
    if not chatbot:
        return jsonify({'error': 'Chatbot not found'}), 404
    
    # Check permissions
    if not has_organization_access(chatbot.organization_id):
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Update fields
    if 'name' in data:
        chatbot.name = data['name']
    if 'allowed_responses' in data:
        chatbot.allowed_responses = data['allowed_responses']
    if 'forbidden_responses' in data:
        chatbot.forbidden_responses = data['forbidden_responses']
    if 'config' in data:
        chatbot.config = data['config']
    
    db.session.commit()
    
    return jsonify({
        'id': chatbot.id,
        'status': 'updated'
    }), 200

@chatbot_routes.route('/<int:chatbot_id>', methods=['DELETE'])
@jwt_required()
def delete_chatbot(chatbot_id):
    """Delete chatbot (requires authentication)"""
    # Get chatbot
    chatbot = ChatBot.query.get(chatbot_id)
    if not chatbot:
        return jsonify({'error': 'Chatbot not found'}), 404
    
    # Check permissions
    if not has_organization_access(chatbot.organization_id):
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Delete chatbot
    db.session.delete(chatbot)
    db.session.commit()
    
    return jsonify({
        'status': 'deleted'
    }), 200

@chatbot_routes.route('/<int:chatbot_id>/clone', methods=['POST'])
@jwt_required()
def clone_chatbot(chatbot_id):
    """Clone an existing chatbot (requires authentication)"""
    data = request.json
    
    # Get source chatbot
    source_chatbot = ChatBot.query.get(chatbot_id)
    if not source_chatbot:
        return jsonify({'error': 'Source chatbot not found'}), 404
    
    # Check permissions
    if not has_organization_access(source_chatbot.organization_id):
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Get target organization_id (default to same organization)
    target_org_id = data.get('target_organization_id', source_chatbot.organization_id)
    
    # Check permissions for target organization
    if not has_organization_access(target_org_id):
        return jsonify({'error': 'Unauthorized for target organization'}), 403
    
    # Create new chatbot with cloned data
    new_name = data.get('name', f"{source_chatbot.name} (Clone)")
    
    new_chatbot = ChatBot(
        name=new_name,
        organization_id=target_org_id,
        allowed_responses=source_chatbot.allowed_responses,
        forbidden_responses=source_chatbot.forbidden_responses
    )
    
    # Clone config
    new_chatbot.config = source_chatbot.config
    
    db.session.add(new_chatbot)
    db.session.commit()
    
    return jsonify({
        'id': new_chatbot.id,
        'name': new_chatbot.name,
        'organization_id': new_chatbot.organization_id,
        'status': 'cloned'
    }), 201

@chatbot_routes.route('/<int:chatbot_id>/embed-code', methods=['GET'])
@jwt_required()
def get_embed_code(chatbot_id):
    """Get the embed code for a chatbot (requires authentication)"""
    # Get chatbot
    chatbot = ChatBot.query.get(chatbot_id)
    if not chatbot:
        return jsonify({'error': 'Chatbot not found'}), 404
    
    # Check permissions
    if not has_organization_access(chatbot.organization_id):
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Generate embed code
    embed_code = f"""
<!-- CLAI Chat Widget -->
<script>
(function(w, d, s, o) {{
    // Create chat widget container
    var c = d.createElement('div');
    c.id = 'clai-chat-widget';
    d.body.appendChild(c);
    
    // Create script element to load widget
    var t = d.createElement(s);
    t.async = 1;
    t.src = 'https://api.clai-chat.com/widget/{chatbot.id}/loader.js';
    t.onload = function() {{
        CLAIChat.init({{
            containerId: 'clai-chat-widget',
            chatbotId: '{chatbot.id}',
            theme: o.theme || {{}},
            utm: {{
                source: new URLSearchParams(window.location.search).get('utm_source'),
                medium: new URLSearchParams(window.location.search).get('utm_medium'),
                campaign: new URLSearchParams(window.location.search).get('utm_campaign')
            }}
        }});
    }};
    var s = d.getElementsByTagName(s)[0];
    s.parentNode.insertBefore(t, s);
}})(window, document, 'script', {{
    theme: {{
        primaryColor: '#0088CC',
        textColor: '#333333',
        position: 'right'
    }}
}});
</script>
<!-- End CLAI Chat Widget -->
    """
    
    return jsonify({
        'embed_code': embed_code.strip()
    }), 200
