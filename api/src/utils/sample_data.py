from models import db, ChatBot, KnowledgeBase, KnowledgeItem, Organization, User, Role
from services.knowledge_service import KnowledgeService
from werkzeug.security import generate_password_hash

def load_sample_data(app):
    """Load sample data for demo purposes"""
    with app.app_context():
        # Check if data already exists
        if ChatBot.query.count() > 0:
            print("Sample data already loaded. Skipping.")
            return
            
        print("Loading sample data...")
        
        # Create a test organization if it doesn't exist
        org = Organization.query.filter_by(name="Demo Organization").first()
        if not org:
            org = Organization(
                name="Demo Organization",
                website="https://example.com",
                subscription_tier="premium"
            )
            db.session.add(org)
            db.session.commit()
            
        # Create roles if they don't exist
        admin_role = Role.query.filter_by(name="admin").first()
        manager_role = Role.query.filter_by(name="manager").first()
        member_role = Role.query.filter_by(name="member").first()
        
        if not admin_role:
            admin_role = Role(name="admin")
            db.session.add(admin_role)
        
        if not manager_role:
            manager_role = Role(name="manager")
            db.session.add(manager_role)
            
        if not member_role:
            member_role = Role(name="member")
            db.session.add(member_role)
            
        db.session.commit()
        
        # Create a demo user if it doesn't exist
        demo_user = User.query.filter_by(email="demo@clai-chat.com").first()
        if not demo_user:
            demo_user = User(
                email="demo@clai-chat.com",
                name="Demo User",
                organization_id=org.id,
                role_id=manager_role.id,
                active=True
            )
            demo_user.set_password("demo123")
            db.session.add(demo_user)
            db.session.commit()
        
        # Create sample chatbot
        chatbot = ChatBot(
            name="Demo Chat Bot",
            organization_id=org.id,
            allowed_responses="Be friendly and helpful. Provide clear and concise information.",
            forbidden_responses="Don't be rude or dismissive. Don't provide inaccurate information."
        )
        
        # Set config
        chatbot.config = {
            "theme": {
                "primaryColor": "#4CAF50",
                "textColor": "#333333",
                "position": "right"
            },
            "leadCapture": {
                "enabled": True,
                "fields": ["name", "email", "phone"]
            },
            "scheduling": {
                "enabled": True,
                "calendarUrl": "https://calendly.com/demo"
            }
        }
        
        db.session.add(chatbot)
        db.session.commit()
        
        # Create knowledge base
        knowledge_service = KnowledgeService()
        kb = knowledge_service.create_knowledge_base(
            name="Demo Knowledge Base",
            organization_id=org.id,
            chatbot_id=chatbot.id
        )
        
        # Add sample knowledge items
        sample_items = [
            {
                "question": "What is CLAI Chat?",
                "answer": "CLAI Chat is an AI-powered chatbot platform that helps businesses engage with website visitors, generate leads, and provide automated customer support."
            },
            {
                "question": "How do I install the chat widget on my website?",
                "answer": "You can install the chat widget by copying the embed code from your dashboard and pasting it into your website's HTML, just before the closing </body> tag."
            },
            {
                "question": "What features does CLAI Chat offer?",
                "answer": "CLAI Chat offers features like AI-powered conversations, lead generation forms, appointment scheduling, analytics, multi-channel support, and integration capabilities with CRMs and other tools."
            },
            {
                "question": "How much does CLAI Chat cost?",
                "answer": "CLAI Chat offers several pricing tiers to fit different business needs. Please contact our sales team for detailed pricing information."
            },
            {
                "question": "Can I customize the appearance of the chat widget?",
                "answer": "Yes, you can customize the colors, position, and behavior of the chat widget through the admin dashboard."
            }
        ]
        
        for item in sample_items:
            knowledge_service.add_knowledge_item(
                knowledge_base_id=kb.id,
                question=item["question"],
                answer=item["answer"]
            )
        
        print("Sample data loaded successfully!")
