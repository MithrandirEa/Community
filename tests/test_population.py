"""
Tests des routes population.

Couvre :
- GET  /population → protégé (redirect /login si non authentifié)
- GET  /population → 200 si connecté
- POST /population → erreur si pas de session active
- POST /population → redirect après publication réussie
- POST /population → contenu vide → 200 (erreur WTForms)
- POST /population → contenu trop long → 200 (erreur WTForms)
- POST /population → sender_avatar_filename rempli depuis NameEntry
"""

import pytest

from app import db
from app.models import Message, NameEntry, NamePack, Session as SimSession


# ---------------------------------------------------------------------------
# Protection de la route
# ---------------------------------------------------------------------------

def test_population_not_logged_in_redirects_to_login(client):
    resp = client.get('/population', follow_redirects=False)
    assert resp.status_code == 302
    assert '/login' in resp.headers['Location']


def test_population_get_returns_200_when_authenticated(population_client):
    resp = population_client.get('/population')
    assert resp.status_code == 200


# ---------------------------------------------------------------------------
# POST /population — sans session active
# ---------------------------------------------------------------------------

def test_population_post_no_active_session_shows_error(population_client):
    resp = population_client.post('/population', data={'content': 'Bonjour'})
    assert resp.status_code == 200
    assert 'Aucune session active' in resp.data.decode()


# ---------------------------------------------------------------------------
# POST /population — avec session active
# ---------------------------------------------------------------------------

def test_population_post_message_redirects(session_population_client):
    resp = session_population_client.post(
        '/population',
        data={'content': 'La route est inondée.'},
        follow_redirects=False,
    )
    assert resp.status_code == 302
    assert '/population' in resp.headers['Location']


def test_population_post_message_is_saved(app_with_session, session_population_client):
    session_population_client.post(
        '/population',
        data={'content': 'Message citoyen'},
        follow_redirects=False,
    )
    with app_with_session.app_context():
        msg = Message.query.filter_by(content='Message citoyen').first()
        assert msg is not None
        assert msg.role == 'population'
        assert msg.is_published is True
        assert msg.real_published_at is not None


def test_population_post_empty_content_stays_on_page(session_population_client):
    """Contenu vide : WTForms refuse → 200."""
    resp = session_population_client.post('/population', data={'content': ''})
    assert resp.status_code == 200


def test_population_post_content_too_long_stays_on_page(session_population_client):
    """Contenu > 500 caractères : WTForms refuse → 200."""
    resp = session_population_client.post(
        '/population',
        data={'content': 'A' * 501},
    )
    assert resp.status_code == 200


# ---------------------------------------------------------------------------
# POST /population — sender_avatar_filename (Issue #13)
# ---------------------------------------------------------------------------

@pytest.fixture
def app_with_session_and_avatar(app):
    """Session active avec un NamePack dont une entrée 'population' possède un avatar."""
    from datetime import datetime, timezone
    with app.app_context():
        pack = NamePack(name='Pack Pop Avatar Test')
        db.session.add(pack)
        db.session.flush()
        entry = NameEntry(
            pack_id=pack.id,
            role='population',
            label='Citoyen Martin',
            avatar_filename='citoyen_avatar.png',
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


def test_population_post_sender_avatar_populated(app_with_session_and_avatar):
    """Quand sender_name est valide et a un avatar, sender_avatar_filename est rempli."""
    c = app_with_session_and_avatar.test_client()
    c.post('/login', data={'code': 'CITOYEN2026'})
    c.post(
        '/population',
        data={'content': 'Test avatar pop', 'sender_name': 'Citoyen Martin'},
        follow_redirects=False,
    )
    with app_with_session_and_avatar.app_context():
        msg = Message.query.filter_by(content='Test avatar pop').first()
        assert msg is not None
        assert msg.sender_name == 'Citoyen Martin'
        assert msg.sender_avatar_filename == 'citoyen_avatar.png'


def test_population_post_sender_avatar_none_when_no_avatar(app_with_session_and_avatar):
    """Un sender_name sans avatar → sender_avatar_filename reste None."""
    with app_with_session_and_avatar.app_context():
        pack = NamePack.query.filter_by(name='Pack Pop Avatar Test').first()
        entry = NameEntry(pack_id=pack.id, role='population', label='Sans Avatar', avatar_filename=None)
        db.session.add(entry)
        db.session.commit()

    c = app_with_session_and_avatar.test_client()
    c.post('/login', data={'code': 'CITOYEN2026'})
    c.post(
        '/population',
        data={'content': 'Test pop sans avatar', 'sender_name': 'Sans Avatar'},
        follow_redirects=False,
    )
    with app_with_session_and_avatar.app_context():
        msg = Message.query.filter_by(content='Test pop sans avatar').first()
        assert msg is not None
        assert msg.sender_avatar_filename is None
