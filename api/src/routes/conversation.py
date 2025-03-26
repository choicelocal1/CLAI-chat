from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from models import db, Conversation, Message, ChatBot, User
from services.conversation_service import ConversationService
from utils.permissions import has_organization_access

conversation_routes = Blueprint('conversation', __name__, url_prefix='/api/conversations')

@conversation_routes.route('/', methods=['POST'])
def start_conversation():
    """Start a new conversation"""
    data = request.json
    
    # Validate required fields
    if not data.get('chatbot_id'):
        return jsonify({'error': 'chatbot_id is required'}), 400
    
    # Get chatbot
    chatbot = ChatBot.query.get(data.get('chatbot_id'))
    if not chatbot:
        return jsonify({'error': 'Chatbot not found'}), 404
    
    # Create conversation service
    conversation_service = ConversationService(
        chatbot=chatbot,
        organization_id=chatbot.organization_id,
        visitor_id=data.get('visitor_id')
    )
    
    # Extract UTM parameters
    utm_params = {
        'source': data.get('utm_source'),
        'medium': data.get('utm_medium'),
        'campaign': data.get('utm_campaign')
    }
    
    # Start conversation
    conversation = conversation_service.start_conversation(
        utm_params=utm_params,
        referrer=data.get('referrer')
    )
    
    return jsonify({
        'conversation_id': conversation.id,
        'status': 'active'
    }), 201

@conversation_routes.route('/<int:conversation_id>/messages', methods=['POST'])
def send_message(conversation_id):
    """Send a message to a conversation"""
    data = request.json
    
    # Validate required fields
    if not data.get('content'):
        return jsonify({'error': 'message content is required'}), 400
    
    # Get conversation
    conversation = Conversation.query.get(conversation_id)
    if not conversation:
        return jsonify({'error': 'Conversation not found'}), 404
    
    # Get chatbot
    chatbot = ChatBot.query.get(conversation.chatbot_id)
    
    # Create conversation service
    conversation_service = ConversationService(
        chatbot=chatbot,
        organization_id=chatbot.organization_id,
        visitor_id=conversation.visitor_id
    )
    
    # Process message
    result = conversation_service.process_message(
        conversation_id=conversation_id,
        message_content=data.get('content')
    )
    
    if 'error' in result:
        return jsonify(result), 400
    
    return jsonify(result), 200

@conversation_routes.route('/<int:conversation_id>', methods=['GET'])
@jwt_required()
def get_conversation(conversation_id):
    """Get conversation details (requires authentication)"""
    user_id = get_jwt_identity()
    
    # Get conversation
    conversation = Conversation.query.get(conversation_id)
    if not conversation:
        return jsonify({'error': 'Conversation not found'}), 404
    
    # Get chatbot
    chatbot = ChatBot.query.get(conversation.chatbot_id)
    
    # Check permissions
    if not has_organization_access(chatbot.organization_id):
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Create conversation service
    conversation_service = ConversationService(
        chatbot=chatbot,
        organization_id=chatbot.organization_id
    )
    
    # Get conversation
    result = conversation_service.get_conversation(conversation_id)
    
    if 'error' in result:
        return jsonify(result), 404
    
    return jsonify(result), 200

@conversation_routes.route('/<int:conversation_id>/end', methods=['POST'])
def end_conversation(conversation_id):
    """End a conversation"""
    # Get conversation
    conversation = Conversation.query.get(conversation_id)
    if not conversation:
        return jsonify({'error': 'Conversation not found'}), 404
    
    # Get chatbot
    chatbot = ChatBot.query.get(conversation.chatbot_id)
    
    # Create conversation service
    conversation_service = ConversationService(
        chatbot=chatbot,
        organization_id=chatbot.organization_id
    )
    
    # End conversation
    result = conversation_service.end_conversation(conversation_id)
    
    if 'error' in result:
        return jsonify(result), 400
    
    return jsonify({'status': 'ended'}), 200

@conversation_routes.route('/', methods=['GET'])
@jwt_required()
def list_conversations():
    """List conversations for an organization (requires authentication)"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    # Get query parameters
    organization_id = request.args.get('organization_id', type=int) or user.organization_id
    chatbot_id = request.args.get('chatbot_id', type=int)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    # Check permissions
    if not has_organization_access(organization_id):
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Build query
    query = Conversation.query.filter_by(organization_id=organization_id)
    
    if chatbot_id:
        query = query.filter_by(chatbot_id=chatbot_id)
    
    # Paginate
    paginated = query.order_by(Conversation.started_at.desc()).paginate(
        page=page, per_page=per_page
    )
    
    return jsonify({
        'total': paginated.total,
        'pages': paginated.pages,
        'current_page': page,
        'per_page': per_page,
        'items': [{
            'id': conv.id,
            'started_at': conv.started_at.isoformat(),
            'ended_at': conv.ended_at.isoformat() if conv.ended_at else None,
            'status': conv.status,
            'visitor_id': conv.visitor_id,
            'utm_source': conv.utm_source,
            'utm_medium': conv.utm_medium,
            'utm_campaign': conv.utm_campaign
        } for conv in paginated.items]
    }), 200
