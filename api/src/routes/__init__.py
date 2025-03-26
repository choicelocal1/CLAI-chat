from flask import Blueprint

from .auth import auth_routes
from .user import user_routes
from .organization import organization_routes
from .chatbot import chatbot_routes
from .conversation import conversation_routes
from .lead import lead_routes
from .analytics import analytics_routes
from .widget import widget_routes

def register_routes(app):
    """Register all blueprint routes with the app."""
    app.register_blueprint(auth_routes)
    app.register_blueprint(user_routes)
    app.register_blueprint(organization_routes)
    app.register_blueprint(chatbot_routes)
    app.register_blueprint(conversation_routes)
    app.register_blueprint(lead_routes)
    app.register_blueprint(analytics_routes)
    app.register_blueprint(widget_routes)
