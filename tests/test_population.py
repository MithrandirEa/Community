"""
Tests des routes population.

Couvre :
- GET  /population → protégé (redirect /login si non authentifié)
- GET  /population → 200 si connecté
- POST /population → erreur si pas de session active
- POST /population → redirect après publication réussie
- POST /population → contenu vide → 200 (erreur WTForms)
- POST /population → contenu trop long → 200 (erreur WTForms)
"""

import pytest

from app.models import Message


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
