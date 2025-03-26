import pytest
from app import create_app
from models import db, User, Role, Organization
from werkzeug.security import generate_password_hash
import os
import tempfile

@pytest.fixture
def app():
    """Create application for testing"""
    # Create a temporary file to isolate the database for each test
    db_fd, db_path = tempfile.mkstemp()
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{db_path}',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'SECRET_KEY': 'test-key',
        'JWT_SECRET_KEY': 'test-jwt-key'
    })

    # Create the database and load test data
    with app.app_context():
        db.create_all()
        init_test_data()

    yield app

    # Close and remove the temporary database
    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """A test CLI runner for the app."""
    return app.test_cli_runner()

def init_test_data():
    """Initialize test data"""
    # Create roles
    roles = ['admin', 'manager', 'member']
    for role_name in roles:
        role = Role(name=role_name)
        db.session.add(role)
    
    db.session.commit()
    
    # Create test organization
    org = Organization(name='Test Organization', subscription_tier='free')
    db.session.add(org)
    db.session.commit()
    
    # Create test users
    admin_role = Role.query.filter_by(name='admin').first()
    manager_role = Role.query.filter_by(name='manager').first()
    member_role = Role.query.filter_by(name='member').first()
    
    # Admin user
    admin = User(
        email='admin@test.com',
        password_hash=generate_password_hash('password'),
        name='Admin User',
        role_id=admin_role.id,
        organization_id=org.id,
        active=True
    )
    
    # Manager user
    manager = User(
        email='manager@test.com',
        password_hash=generate_password_hash('password'),
        name='Manager User',
        role_id=manager_role.id,
        organization_id=org.id,
        active=True
    )
    
    # Member user
    member = User(
        email='member@test.com',
        password_hash=generate_password_hash('password'),
        name='Member User',
        role_id=member_role.id,
        organization_id=org.id,
        active=True
    )
    
    db.session.add_all([admin, manager, member])
    db.session.commit()
