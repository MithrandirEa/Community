"""
Tests des fragments HTMX.

Couvre :
- GET  /htmx/ping                    → 200 (point de vie, sans auth)
- GET  /htmx/feed                    → protégé (redirect si non connecté)
- GET  /htmx/feed                    → 200 pour officiel, population, admin
- GET  /htmx/comments/<id>           → protégé / 200 si connecté
- POST /htmx/comment/<id>            → protégé (officiel/population seulement)
- POST /htmx/comment/<id>            → crée un commentaire + 200
- POST /htmx/comment/<id>            → 403 si pas de session active
"""

import pytest

from app import db
from app.models import Comment


# ---------------------------------------------------------------------------
# /htmx/ping — accessible sans auth
# ---------------------------------------------------------------------------

def test_htmx_ping_returns_pong(client):
    resp = client.get('/htmx/ping')
    assert resp.status_code == 200
    assert resp.data == b'pong'


# ---------------------------------------------------------------------------
# /htmx/feed
# ---------------------------------------------------------------------------

def test_htmx_feed_redirects_when_not_logged_in(client):
    resp = client.get('/htmx/feed', follow_redirects=False)
    assert resp.status_code == 302
    assert '/login' in resp.headers['Location']


def test_htmx_feed_returns_200_for_officiel(session_officiel_client):
    resp = session_officiel_client.get('/htmx/feed')
    assert resp.status_code == 200


def test_htmx_feed_returns_200_for_population(session_population_client):
    resp = session_population_client.get('/htmx/feed')
    assert resp.status_code == 200


def test_htmx_feed_returns_200_for_admin(session_admin_client):
    resp = session_admin_client.get('/htmx/feed')
    assert resp.status_code == 200


# ---------------------------------------------------------------------------
# /htmx/comments/<id>
# ---------------------------------------------------------------------------

def test_htmx_comments_redirects_when_not_logged_in(client, message_in_session):
    _, msg_id = message_in_session
    resp = client.get(f'/htmx/comments/{msg_id}', follow_redirects=False)
    assert resp.status_code == 302
    assert '/login' in resp.headers['Location']


def test_htmx_comments_returns_200_for_officiel(message_in_session):
    app, msg_id = message_in_session
    c = app.test_client()
    c.post('/login', data={'code': 'MAIRIE2026'})
    resp = c.get(f'/htmx/comments/{msg_id}')
    assert resp.status_code == 200


def test_htmx_comments_404_for_unknown_message(session_officiel_client):
    resp = session_officiel_client.get('/htmx/comments/99999')
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# POST /htmx/comment/<id>
# ---------------------------------------------------------------------------

def test_htmx_post_comment_redirects_when_not_logged_in(client, message_in_session):
    _, msg_id = message_in_session
    resp = client.post(
        f'/htmx/comment/{msg_id}',
        data={'content': 'Réponse test'},
        follow_redirects=False,
    )
    assert resp.status_code == 302
    assert '/login' in resp.headers['Location']


def test_htmx_post_comment_creates_comment(message_in_session):
    """Un POST valide crée un commentaire en base."""
    app, msg_id = message_in_session
    c = app.test_client()
    c.post('/login', data={'code': 'MAIRIE2026'})
    resp = c.post(
        f'/htmx/comment/{msg_id}',
        data={'content': 'Commentaire officiel'},
    )
    assert resp.status_code == 200
    with app.app_context():
        comment = Comment.query.filter_by(
            message_id=msg_id, content='Commentaire officiel'
        ).first()
        assert comment is not None
        assert comment.role == 'officiel'


def test_htmx_post_comment_by_population(message_in_session):
    """Un citoyen peut aussi commenter."""
    app, msg_id = message_in_session
    c = app.test_client()
    c.post('/login', data={'code': 'CITOYEN2026'})
    resp = c.post(
        f'/htmx/comment/{msg_id}',
        data={'content': 'Avis citoyen'},
    )
    assert resp.status_code == 200
    with app.app_context():
        comment = Comment.query.filter_by(
            message_id=msg_id, content='Avis citoyen'
        ).first()
        assert comment is not None
        assert comment.role == 'population'


def test_htmx_post_comment_no_active_session_returns_403(app, message_in_session):
    """Sans session active, poster un commentaire doit retourner 403."""
    app_fixture, msg_id = message_in_session
    # Désactiver la session
    from app.models import Session as SimSession
    with app_fixture.app_context():
        s = SimSession.query.filter_by(is_active=True).first()
        if s:
            s.is_active = False
            db.session.commit()

    c = app_fixture.test_client()
    c.post('/login', data={'code': 'MAIRIE2026'})
    resp = c.post(
        f'/htmx/comment/{msg_id}',
        data={'content': 'Test sans session'},
    )
    assert resp.status_code == 403
