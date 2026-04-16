"""
Tests des routes officiel.

Couvre :
- GET  /officiel → protégé (redirect /login si non authentifié)
- GET  /officiel → 200 si connecté en tant qu'officiel
- POST /officiel → erreur si pas de session active
- POST /officiel → redirect après publication réussie
- POST /officiel → message programmé valide
- POST /officiel → message programmé sans heure → erreur
- POST /officiel → sender_avatar_filename rempli depuis NameEntry
"""

import pytest

from app import db
from app.models import Message, NameEntry, NamePack, Session as SimSession


# ---------------------------------------------------------------------------
# Protection de la route
# ---------------------------------------------------------------------------

def test_officiel_not_logged_in_redirects_to_login(client):
    resp = client.get('/officiel', follow_redirects=False)
    assert resp.status_code == 302
    assert '/login' in resp.headers['Location']


def test_officiel_get_returns_200_when_authenticated(officiel_client):
    resp = officiel_client.get('/officiel')
    assert resp.status_code == 200


# ---------------------------------------------------------------------------
# POST /officiel — sans session active
# ---------------------------------------------------------------------------

def test_officiel_post_no_active_session_shows_error(officiel_client):
    resp = officiel_client.post('/officiel', data={'content': 'Bonjour'})
    assert resp.status_code == 200
    body = resp.data.decode()
    assert 'Aucune session active' in body


# ---------------------------------------------------------------------------
# POST /officiel — avec session active
# ---------------------------------------------------------------------------

def test_officiel_post_message_redirects(session_officiel_client):
    resp = session_officiel_client.post(
        '/officiel',
        data={'content': 'Alerte météo en cours.'},
        follow_redirects=False,
    )
    assert resp.status_code == 302
    assert '/officiel' in resp.headers['Location']


def test_officiel_post_message_is_saved(app_with_session, session_officiel_client):
    session_officiel_client.post(
        '/officiel',
        data={'content': 'Message sauvegardé'},
        follow_redirects=False,
    )
    with app_with_session.app_context():
        msg = Message.query.filter_by(content='Message sauvegardé').first()
        assert msg is not None
        assert msg.role == 'officiel'
        assert msg.is_published is True
        assert msg.real_published_at is not None


def test_officiel_post_scheduled_message_redirects(session_officiel_client):
    resp = session_officiel_client.post(
        '/officiel',
        data={
            'content': 'Coupure eau à 14h.',
            'is_scheduled': 'y',
            'scheduled_time': '14:30',
        },
        follow_redirects=False,
    )
    assert resp.status_code == 302


def test_officiel_post_scheduled_message_not_immediately_published(
    app_with_session, session_officiel_client
):
    """Un message programmé doit avoir is_published=False tant que l'heure n'est pas atteinte."""
    session_officiel_client.post(
        '/officiel',
        data={
            'content': 'Message différé',
            'is_scheduled': 'y',
            'scheduled_time': '23:59',
        },
    )
    with app_with_session.app_context():
        msg = Message.query.filter_by(content='Message différé').first()
        assert msg is not None
        assert msg.is_published is False
        assert msg.is_scheduled is True
        assert msg.scheduled_for_minutes == 23 * 60 + 59


def test_officiel_post_scheduled_missing_time_shows_error(session_officiel_client):
    resp = session_officiel_client.post(
        '/officiel',
        data={
            'content': 'Message sans heure',
            'is_scheduled': 'y',
            'scheduled_time': '',
        },
    )
    assert resp.status_code == 200
    assert "heure de programmation" in resp.data.decode()


def test_officiel_post_empty_content_stays_on_page(session_officiel_client):
    """Contenu vide : WTForms refuse → reste sur la page (200)."""
    resp = session_officiel_client.post('/officiel', data={'content': ''})
    assert resp.status_code == 200


# ---------------------------------------------------------------------------
# POST /officiel — sender_avatar_filename (Issue #13)
# ---------------------------------------------------------------------------

@pytest.fixture
def app_with_session_and_avatar(app):
    """Session active avec un NamePack dont une entrée 'officiel' possède un avatar."""
    from datetime import datetime, timezone
    with app.app_context():
        pack = NamePack(name='Pack Avatar Test')
        db.session.add(pack)
        db.session.flush()
        entry = NameEntry(
            pack_id=pack.id,
            role='officiel',
            label='Maire Dupont',
            avatar_filename='avatar_test.png',
        )
        db.session.add(entry)
        s = SimSession(
            fictive_start_minutes=600,
            real_started_at=datetime.now(timezone.utc).replace(tzinfo=None),
            is_active=True,
            name_pack_id=pack.id,
        )
        db.session.add(s)
        db.session.commit()
    return app


def test_officiel_post_sender_avatar_populated(app_with_session_and_avatar):
    """Quand sender_name est valide et a un avatar, sender_avatar_filename est rempli."""
    c = app_with_session_and_avatar.test_client()
    c.post('/login', data={'code': 'MAIRIE2026'})
    c.post(
        '/officiel',
        data={'content': 'Test avatar', 'sender_name': 'Maire Dupont'},
        follow_redirects=False,
    )
    with app_with_session_and_avatar.app_context():
        msg = Message.query.filter_by(content='Test avatar').first()
        assert msg is not None
        assert msg.sender_name == 'Maire Dupont'
        assert msg.sender_avatar_filename == 'avatar_test.png'


def test_officiel_post_sender_avatar_none_when_no_avatar(app_with_session_and_avatar):
    """Un sender_name sans avatar → sender_avatar_filename reste None."""
    with app_with_session_and_avatar.app_context():
        pack = NamePack.query.filter_by(name='Pack Avatar Test').first()
        entry = NameEntry(pack_id=pack.id, role='officiel', label='Sans Avatar', avatar_filename=None)
        db.session.add(entry)
        db.session.commit()

    c = app_with_session_and_avatar.test_client()
    c.post('/login', data={'code': 'MAIRIE2026'})
    c.post(
        '/officiel',
        data={'content': 'Test sans avatar', 'sender_name': 'Sans Avatar'},
        follow_redirects=False,
    )
    with app_with_session_and_avatar.app_context():
        msg = Message.query.filter_by(content='Test sans avatar').first()
        assert msg is not None
        assert msg.sender_avatar_filename is None
