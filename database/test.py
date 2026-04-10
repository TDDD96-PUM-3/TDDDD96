import tempfile
import os
import pytest
from io import BytesIO
from app import create_app
from extensions import db, bcrypt
from models.user import User


@pytest.fixture()
def app():
    # Create temporary SQLite database for testing
    db_fd, db_path = tempfile.mkstemp()
    test_app = create_app()
    test_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
    test_app.config['TESTING'] = True

    with test_app.app_context():
        db.drop_all()
        db.create_all()

    yield test_app

    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture()
def client(app):
    return app.test_client()


# --- User tests ---

def test_create_user(client):
    # Test creating a new user
    rv = client.post(
        '/register', json={'username': 'Nisse', 'password': 'Struts123'})
    assert rv.status_code == 201
    assert rv.get_json()['message'] == 'Användare skapad'

    # Test creating the same user again should fail
    rv = client.post(
        '/register', json={'username': 'Nisse', 'password': 'Struts123'})
    assert rv.status_code == 409
    assert rv.get_json()['message'] == 'Användarnamnet är redan taget'


def test_login_logout(client):
    # Create a user
    client.post(
        '/register', json={'username': 'Nisse', 'password': 'Struts123'})

    # Test login with wrong password
    rv = client.post('/login', json={'username': 'Nisse', 'password': 'Wrong'})
    assert rv.status_code == 401

    # Test login with unknown username
    rv = client.post(
        '/login', json={'username': 'Unknown', 'password': 'Struts123'})
    assert rv.status_code == 401

    # Test successful login
    rv = client.post(
        '/login', json={'username': 'Nisse', 'password': 'Struts123'})
    token = rv.get_json()['access_token']
    assert rv.status_code == 200
    assert 'access_token' in rv.get_json()

    # Test logout without token
    rv = client.post('/logout')
    assert rv.status_code == 401

    # Test logout with invalid token
    rv = client.post(
        '/logout', headers={'Authorization': 'Bearer invalidtoken'})
    assert rv.status_code == 422

    # Test successful logout
    rv = client.post('/logout', headers={'Authorization': f'Bearer {token}'})
    assert rv.status_code == 200
    assert rv.get_json()['message'] == 'Utloggning lyckades'

    # Token should now be blacklisted
    rv = client.post('/logout', headers={'Authorization': f'Bearer {token}'})
    assert rv.status_code == 401


def test_hash_and_salt():
    # Ensure password hashes are unique even for same input
    pw1 = bcrypt.generate_password_hash("Struts123")
    pw2 = bcrypt.generate_password_hash("Struts123")
    assert pw1 != pw2


def test_multiple_tokens(client):
    # Ensure different login sessions produce different tokens
    client.post(
        '/register', json={'username': 'Nisse', 'password': 'Struts123'})
    token1 = client.post(
        '/login', json={'username': 'Nisse', 'password': 'Struts123'}).get_json()['access_token']
    token2 = client.post(
        '/login', json={'username': 'Nisse', 'password': 'Struts123'}).get_json()['access_token']
    assert token1 != token2
