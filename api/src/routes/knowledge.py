from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from models import User, KnowledgeBase, ChatBot
from services.knowledge_service import KnowledgeService
from utils.permissions import has_organization_access

knowledge_routes = Blueprint('knowledge', __name__, url_prefix='/api/knowledge')
knowledge_service = KnowledgeService()

@knowledge_routes.route('/bases', methods=['GET'])
@jwt_required()
def get_knowledge_bases():
    """Get knowledge bases for organization"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    # Get organization_id from query params or use user's organization
    organization_id = request.args.get('organization_id', type=int) or user.organization_id
    
    # Check permissions
    if not has_organization_access(organization_id):
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Get chatbot_id if provided
    chatbot_id = request.args.get('chatbot_id', type=int)
    
    # Get knowledge bases
    knowledge_bases = knowledge_service.get_knowledge_bases(organization_id, chatbot_id)
    
    return jsonify([{
        'id': kb.id,
        'name': kb.name,
        'organization_id': kb.organization_id,
        'chatbot_id': kb.chatbot_id,
        'created_at': kb.created_at.isoformat(),
        'updated_at': kb.updated_at.isoformat(),
        'item_count': kb.items.count()
    } for kb in knowledge_bases]), 200

@knowledge_routes.route('/bases', methods=['POST'])
@jwt_required()
def create_knowledge_base():
    """Create knowledge base"""
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
    
    # Check if chatbot exists if provided
    chatbot_id = data.get('chatbot_id')
    if chatbot_id:
        chatbot = ChatBot.query.get(chatbot_id)
        if not chatbot or chatbot.organization_id != organization_id:
            return jsonify({'error': 'Invalid chatbot_id'}), 400
    
    # Create knowledge base
    knowledge_base = knowledge_service.create_knowledge_base(
        name=data.get('name'),
        organization_id=organization_id,
        chatbot_id=chatbot_id
    )
    
    return jsonify({
        'id': knowledge_base.id,
        'name': knowledge_base.name,
        'organization_id': knowledge_base.organization_id,
        'chatbot_id': knowledge_base.chatbot_id,
        'created_at': knowledge_base.created_at.isoformat()
    }), 201

@knowledge_routes.route('/bases/<int:base_id>', methods=['GET'])
@jwt_required()
def get_knowledge_base(base_id):
    """Get knowledge base details"""
    # Get knowledge base
    knowledge_base = knowledge_service.get_knowledge_base(base_id)
    if not knowledge_base:
        return jsonify({'error': 'Knowledge base not found'}), 404
    
    # Check permissions
    if not has_organization_access(knowledge_base.organization_id):
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Get knowledge items
    items = knowledge_service.get_knowledge_items(base_id)
    
    return jsonify({
        'id': knowledge_base.id,
        'name': knowledge_base.name,
        'organization_id': knowledge_base.organization_id,
        'chatbot_id': knowledge_base.chatbot_id,
        'created_at': knowledge_base.created_at.isoformat(),
        'updated_at': knowledge_base.updated_at.isoformat(),
        'items': [{
            'id': item.id,
            'question': item.question,
            'answer': item.answer,
            'created_at': item.created_at.isoformat(),
            'updated_at': item.updated_at.isoformat()
        } for item in items]
    }), 200

@knowledge_routes.route('/bases/<int:base_id>', methods=['PUT'])
@jwt_required()
def update_knowledge_base(base_id):
    """Update knowledge base"""
    data = request.json
    
    # Get knowledge base
    knowledge_base = knowledge_service.get_knowledge_base(base_id)
    if not knowledge_base:
        return jsonify({'error': 'Knowledge base not found'}), 404
    
    # Check permissions
    if not has_organization_access(knowledge_base.organization_id):
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Update knowledge base
    updated_kb = knowledge_service.update_knowledge_base(
        knowledge_base_id=base_id,
        name=data.get('name'),
        chatbot_id=data.get('chatbot_id')
    )
    
    return jsonify({
        'id': updated_kb.id,
        'status': 'updated'
    }), 200

@knowledge_routes.route('/bases/<int:base_id>', methods=['DELETE'])
@jwt_required()
def delete_knowledge_base(base_id):
    """Delete knowledge base"""
    # Get knowledge base
    knowledge_base = knowledge_service.get_knowledge_base(base_id)
    if not knowledge_base:
        return jsonify({'error': 'Knowledge base not found'}), 404
    
    # Check permissions
    if not has_organization_access(knowledge_base.organization_id):
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Delete knowledge base
    success = knowledge_service.delete_knowledge_base(base_id)
    
    if success:
        return jsonify({'status': 'deleted'}), 200
    else:
        return jsonify({'error': 'Failed to delete knowledge base'}), 500

@knowledge_routes.route('/bases/<int:base_id>/items', methods=['POST'])
@jwt_required()
def create_knowledge_item(base_id):
    """Add item to knowledge base"""
    data = request.json
    
    # Get knowledge base
    knowledge_base = knowledge_service.get_knowledge_base(base_id)
    if not knowledge_base:
        return jsonify({'error': 'Knowledge base not found'}), 404
    
    # Check permissions
    if not has_organization_access(knowledge_base.organization_id):
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Validate required fields
    if not data.get('question') or not data.get('answer'):
        return jsonify({'error': 'question and answer are required'}), 400
    
    # Add knowledge item
    item = knowledge_service.add_knowledge_item(
        knowledge_base_id=base_id,
        question=data.get('question'),
        answer=data.get('answer')
    )
    
    return jsonify({
        'id': item.id,
        'question': item.question,
        'answer': item.answer,
        'created_at': item.created_at.isoformat()
    }), 201

@knowledge_routes.route('/bases/<int:base_id>/bulk', methods=['POST'])
@jwt_required()
def bulk_import(base_id):
    """Bulk import knowledge items"""
    data = request.json
    
    # Get knowledge base
    knowledge_base = knowledge_service.get_knowledge_base(base_id)
    if not knowledge_base:
        return jsonify({'error': 'Knowledge base not found'}), 404
    
    # Check permissions
    if not has_organization_access(knowledge_base.organization_id):
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Validate items
    items = data.get('items', [])
    if not isinstance(items, list):
        return jsonify({'error': 'items must be an array'}), 400
    
    # Bulk import
    knowledge_service.bulk_import(base_id, items)
    
    return jsonify({
        'status': 'imported',
        'count': len(items)
    }), 200

@knowledge_routes.route('/items/<int:item_id>', methods=['PUT'])
@jwt_required()
def update_knowledge_item(item_id):
    """Update knowledge item"""
    data = request.json
    
    # Get item's knowledge base
    item = KnowledgeItem.query.get(item_id)
    if not item:
        return jsonify({'error': 'Knowledge item not found'}), 404
    
    knowledge_base = knowledge_service.get_knowledge_base(item.knowledge_base_id)
    
    # Check permissions
    if not has_organization_access(knowledge_base.organization_id):
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Update item
    updated_item = knowledge_service.update_knowledge_item(
        item_id=item_id,
        question=data.get('question'),
        answer=data.get('answer')
    )
    
    return jsonify({
        'id': updated_item.id,
        'status': 'updated'
    }), 200

@knowledge_routes.route('/items/<int:item_id>', methods=['DELETE'])
@jwt_required()
def delete_knowledge_item(item_id):
    """Delete knowledge item"""
    # Get item's knowledge base
    item = KnowledgeItem.query.get(item_id)
    if not item:
        return jsonify({'error': 'Knowledge item not found'}), 404
    
    knowledge_base = knowledge_service.get_knowledge_base(item.knowledge_base_id)
    
    # Check permissions
    if not has_organization_access(knowledge_base.organization_id):
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Delete item
    success = knowledge_service.delete_knowledge_item(item_id)
    
    if success:
        return jsonify({'status': 'deleted'}), 200
    else:
        return jsonify({'error': 'Failed to delete knowledge item'}), 500

@knowledge_routes.route('/bases/<int:base_id>/search', methods=['POST'])
@jwt_required()
def search_knowledge_base(base_id):
    """Search knowledge base"""
    data = request.json
    
    # Get knowledge base
    knowledge_base = knowledge_service.get_knowledge_base(base_id)
    if not knowledge_base:
        return jsonify({'error': 'Knowledge base not found'}), 404
    
    # Check permissions
    if not has_organization_access(knowledge_base.organization_id):
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Validate required fields
    if not data.get('query'):
        return jsonify({'error': 'query is required'}), 400
    
    # Search knowledge base
    threshold = data.get('threshold', 0.7)
    results = knowledge_service.search_knowledge_base(
        knowledge_base_id=base_id,
        query=data.get('query'),
        threshold=threshold
    )
    
    return jsonify({
        'query': data.get('query'),
        'threshold': threshold,
        'results': results
    }), 200
