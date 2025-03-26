from flask import Blueprint, send_from_directory, render_template, jsonify, request
import os
import json

from models import ChatBot, Organization

widget_routes = Blueprint('widget', __name__, url_prefix='/widget')

@widget_routes.route('/<int:chatbot_id>/loader.js')
def get_widget_loader(chatbot_id):
    """Serve the widget loader script"""
    # Get chatbot
    chatbot = ChatBot.query.get_or_404(chatbot_id)
    
    # Set content type and cache headers
    headers = {
        'Content-Type': 'application/javascript',
        'Cache-Control': 'max-age=3600'  # Cache for 1 hour
    }
    
    # Get organization
    organization = Organization.query.get(chatbot.organization_id)
    
    # Generate widget configuration
    config = {
        'chatbotId': chatbot_id,
        'organizationId': chatbot.organization_id,
        'name': chatbot.name,
        'apiUrl': request.host_url.rstrip('/')
    }
    
    # Render loader script with configuration
    return render_template('widget_loader.js', config=json.dumps(config)), 200, headers

@widget_routes.route('/<int:chatbot_id>/bundle.js')
def get_widget_bundle(chatbot_id):
    """Serve the widget bundle script"""
    # Set content type and cache headers
    headers = {
        'Content-Type': 'application/javascript',
        'Cache-Control': 'max-age=3600'  # Cache for 1 hour
    }
    
    # Serve the bundled widget script
    return send_from_directory('static/widget', 'bundle.js'), 200, headers

@widget_routes.route('/<int:chatbot_id>/styles.css')
def get_widget_styles(chatbot_id):
    """Serve the widget styles"""
    # Get chatbot
    chatbot = ChatBot.query.get_or_404(chatbot_id)
    
    # Set content type and cache headers
    headers = {
        'Content-Type': 'text/css',
        'Cache-Control': 'max-age=3600'  # Cache for 1 hour
    }
    
    # Get theme configuration from chatbot
    theme = chatbot.config.get('theme', {})
    
    # Render CSS template with theme variables
    return render_template('widget_styles.css', theme=theme), 200, headers

@widget_routes.route('/<int:chatbot_id>/config')
def get_widget_config(chatbot_id):
    """Get widget configuration"""
    # Get chatbot
    chatbot = ChatBot.query.get_or_404(chatbot_id)
    
    # Build configuration object
    config = {
        'chatbotId': chatbot.id,
        'organizationId': chatbot.organization_id,
        'name': chatbot.name,
        'theme': chatbot.config.get('theme', {}),
        'features': {
            'leadCapture': chatbot.config.get('leadCapture', {}),
            'scheduling': chatbot.config.get('scheduling', {})
        }
    }
    
    return jsonify(config)
