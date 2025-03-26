from flask_socketio import SocketIO, emit, join_room, leave_room
from flask import request
import json

from models import ChatBot, Conversation
from services.conversation_service import ConversationService

socketio = SocketIO()

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print(f"Client connected: {request.sid}")

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print(f"Client disconnected: {request.sid}")

@socketio.on('join')
def handle_join(data):
    """Handle client joining a conversation room"""
    conversation_id = data.get('conversation_id')
    if conversation_id:
        join_room(f"conversation_{conversation_id}")
        emit('joined', {'conversation_id': conversation_id}, room=request.sid)

@socketio.on('leave')
def handle_leave(data):
    """Handle client leaving a conversation room"""
    conversation_id = data.get('conversation_id')
    if conversation_id:
        leave_room(f"conversation_{conversation_id}")
        emit('left', {'conversation_id': conversation_id}, room=request.sid)

@socketio.on('message')
def handle_message(data):
    """Handle incoming messages"""
    conversation_id = data.get('conversation_id')
    content = data.get('content')
    
    if not conversation_id or not content:
        emit('error', {'message': 'Missing required fields'}, room=request.sid)
        return
    
    # Get conversation
    conversation = Conversation.query.get(conversation_id)
    if not conversation:
        emit('error', {'message': 'Conversation not found'}, room=request.sid)
        return
    
    # Get chatbot
    chatbot = ChatBot.query.get(conversation.chatbot_id)
    
    # Create conversation service
    conversation_service = ConversationService(
        chatbot=chatbot,
        organization_id=chatbot.organization_id,
        visitor_id=conversation.visitor_id
    )
    
    # Process message
    emit('typing', {'status': 'started'}, room=f"conversation_{conversation_id}")
    
    result = conversation_service.process_message(
        conversation_id=conversation_id,
        message_content=content
    )
    
    emit('typing', {'status': 'stopped'}, room=f"conversation_{conversation_id}")
    
    if 'error' in result:
        emit('error', {'message': result['error']}, room=request.sid)
        return
    
    # Broadcast message to all clients in the conversation room
    emit('message', {
        'id': result['message_id'],
        'content': result['content'],
        'sender': 'bot',
        'timestamp': json.dumps({"$date": {"$numberLong": str(int(datetime.now().timestamp() * 1000))}})
    }, room=f"conversation_{conversation_id}")

def send_system_message(conversation_id, content):
    """Send a system message to all clients in a conversation room"""
    emit('system', {
        'content': content,
        'timestamp': json.dumps({"$date": {"$numberLong": str(int(datetime.now().timestamp() * 1000))}})
    }, room=f"conversation_{conversation_id}", namespace='/')
