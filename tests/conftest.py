"""
Fixtures partagées pour toute la suite de tests Community.

Chaque test obtient une application Flask fraîche avec SQLite en mémoire,
garantissant un isolement complet entre les tests.
"""

from datetime import datetime, timezone
from unittest.mock import patch

import pytest

from app import create_app
from app import db as _db
from app.models import Session as SimSession, Message


# ---------------------------------------------------------------------------
# Application et client de base
# ---------------------------------------------------------------------------

@pytest.fixture
def app():
    """Application Flask de test : in-memory DB, CSRF désactivé."""
    with patch('app.utils.scheduler.start_scheduler'):
        _app = create_app({
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
            'WTF_CSRF_ENABLED': False,
            'SECRET_KEY': 'test-secret-key-not-used-in-production',
        })
    yield _app


@pytest.fixture
def client(app):
    """Client HTTP de test (par défaut : non authentifié)."""
    return app.test_client()


# ---------------------------------------------------------------------------
# Clients authentifiés (sans session active)
# ---------------------------------------------------------------------------

@pytest.fixture
def officiel_client(client):
    """Client authentifié avec le rôle officiel."""
    client.post('/login', data={'code': 'MAIRIE2026'})
    return client


@pytest.fixture
def population_client(client):
    """Client authentifié avec le rôle population."""
    client.post('/login', data={'code': 'CITOYEN2026'})
    return client


@pytest.fixture
def admin_client(client):
    """Client authentifié avec le rôle admin."""
    client.post('/login', data={'code': 'ADMIN2026'})
    return client


# ---------------------------------------------------------------------------
# App avec session de simulation active
# ---------------------------------------------------------------------------

@pytest.fixture
def app_with_session(app):
    """Même app, avec une session de simulation active démarrée à 10:00 fictif."""
    with app.app_context():
        s = SimSession(
            fictive_start_minutes=600,  # 10:00
            real_started_at=datetime.now(timezone.utc).replace(tzinfo=None),
            is_active=True,
        )
        _db.session.add(s)
        _db.session.commit()
    return app


# ---------------------------------------------------------------------------
# Clients authentifiés AVEC session active
# ---------------------------------------------------------------------------

@pytest.fixture
def session_officiel_client(app_with_session):
    """Client officiel avec session active."""
    c = app_with_session.test_client()
    c.post('/login', data={'code': 'MAIRIE2026'})
    return c


@pytest.fixture
def session_population_client(app_with_session):
    """Client population avec session active."""
    c = app_with_session.test_client()
    c.post('/login', data={'code': 'CITOYEN2026'})
    return c


@pytest.fixture
def session_admin_client(app_with_session):
    """Client admin avec session active."""
    c = app_with_session.test_client()
    c.post('/login', data={'code': 'ADMIN2026'})
    return c


# ---------------------------------------------------------------------------
# Message existant en base (nécessaire pour les tests htmx/comments)
# ---------------------------------------------------------------------------

@pytest.fixture
def message_in_session(app_with_session):
    """
    Crée un message publié dans la session active.
    Retourne (app, message_id).
    """
    with app_with_session.app_context():
        session_obj = SimSession.query.filter_by(is_active=True).first()
        msg = Message(
            session_id=session_obj.id,
            role='officiel',
            content='Message de test fixture',
            is_published=True,
            real_published_at=datetime.now(timezone.utc).replace(tzinfo=None),
        )
        _db.session.add(msg)
        _db.session.commit()
        msg_id = msg.id
    return app_with_session, msg_id


# ---------------------------------------------------------------------------
# App avec CSRF activé (pour test_security)
# ---------------------------------------------------------------------------

@pytest.fixture
def csrf_app():
    """App avec CSRF réellement activé pour tester la protection."""
    with patch('app.utils.scheduler.start_scheduler'):
        _app = create_app({
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
            'WTF_CSRF_ENABLED': True,
            'SECRET_KEY': 'test-csrf-secret-key',
            'WTF_CSRF_TIME_LIMIT': None,
        })
    yield _app


@pytest.fixture
def csrf_client(csrf_app):
    """Client avec CSRF activé."""
    return csrf_app.test_client()
