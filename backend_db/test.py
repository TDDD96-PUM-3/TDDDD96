"""Pytest suite for auth and saved-data stats endpoints.

These tests are intended to run in CI/local using a temporary SQLite database.
"""

import tempfile
import os
from datetime import date
import pytest
from io import BytesIO
from app import create_app
from extensions import db, bcrypt
from models.user import User
from models.saved_data import SavedData


@pytest.fixture()
def app():
    """Create a test Flask app backed by a temporary SQLite database."""
    # Create temporary SQLite database for test isolation.
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


def test_get_stats(client, app):
    with app.app_context():
        first = SavedData(
            webname='Latest site',
            link='https://latest.example',
            counterfeit_count=2.0,
            tot_image_count=5.0,
            date=date(2024, 2, 1),
        )
        second = SavedData(
            webname='Highest site',
            link='https://highest.example',
            counterfeit_count=7.0,
            tot_image_count=10.0,
            date=date(2024, 1, 1),
        )
        db.session.add_all([first, second])
        db.session.commit()

    rv = client.get('/data/stats')

    assert rv.status_code == 200
    payload = rv.get_json()
    assert payload['found_counterfeits_per_web'] == {
        'flagged_web': 2,
        'total_web': 2,
    }
    assert payload['found_counterfeits_tot_img'] == {
        'flagged_img': 9.0,
        'total_img': 15.0,
    }
    assert payload['result_from_prev_scrape']['web_url'] == 'https://latest.example'
    assert payload['highest_flagged_count']['web_url'] == 'https://highest.example'
