from models import db, Role, User, Organization
from werkzeug.security import generate_password_hash

def init_db(app):
    """Initialize database with required initial data"""
    with app.app_context():
        # Create tables if they don't exist
        db.create_all()
        
        # Create roles if they don't exist
        roles = ['admin', 'manager', 'member']
        for role_name in roles:
            if not Role.query.filter_by(name=role_name).first():
                role = Role(name=role_name)
                db.session.add(role)
        
        # Commit roles to get IDs
        db.session.commit()
        
        # Create admin user if it doesn't exist
        admin_email = 'admin@clai-chat.com'
        if not User.query.filter_by(email=admin_email).first():
            admin_role = Role.query.filter_by(name='admin').first()
            admin = User(
                email=admin_email,
                password_hash=generate_password_hash('admin123'),  # Change in production
                name='Admin User',
                role_id=admin_role.id,
                active=True
            )
            db.session.add(admin)
            
            # Create default organization
            default_org = Organization(
                name='Default Organization',
                subscription_tier='free'
            )
            db.session.add(default_org)
            db.session.commit()
            
            # Update admin with organization
            admin.organization_id = default_org.id
            db.session.commit()
            
            print("Created admin user and default organization")
        
        print("Database initialized")
