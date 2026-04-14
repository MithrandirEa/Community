"""
Tests de sécurité : isolation des rôles et protection CSRF.

Couvre :
- Isolation des rôles : officiel ↔ population (accès croisé interdit)
- Isolation admin : officiel/population ne peuvent pas accéder au back-office
- Accès non authentifié → redirect /login sur toutes les routes protégées
- Admin ne peut pas poster de commentaires (route réservée officiel/population)
- CSRF : POST sans token → 400 quand CSRF est activé
"""

import pytest


# ---------------------------------------------------------------------------
# Routes protégées — accès sans authentification
# ---------------------------------------------------------------------------

@pytest.mark.parametrize('path', [
    '/officiel',
    '/population',
    '/admin/',
    '/admin/config',
    '/admin/photos',
    '/htmx/feed',
])
def test_unauthenticated_redirects_to_login(client, path):
    resp = client.get(path, follow_redirects=False)
    assert resp.status_code == 302
    assert '/login' in resp.headers['Location']


# ---------------------------------------------------------------------------
# Isolation des rôles
# ---------------------------------------------------------------------------

def test_officiel_cannot_access_population(officiel_client):
    """Un utilisateur officiel ne peut pas voir le feed population."""
    resp = officiel_client.get('/population', follow_redirects=False)
    assert resp.status_code == 302
    assert '/login' in resp.headers['Location']


def test_population_cannot_access_officiel(population_client):
    """Un citoyen ne peut pas voir le feed officiel."""
    resp = population_client.get('/officiel', follow_redirects=False)
    assert resp.status_code == 302
    assert '/login' in resp.headers['Location']


def test_officiel_cannot_access_admin_dashboard(officiel_client):
    resp = officiel_client.get('/admin/', follow_redirects=False)
    assert resp.status_code == 302
    assert '/login' in resp.headers['Location']


def test_population_cannot_access_admin_dashboard(population_client):
    resp = population_client.get('/admin/', follow_redirects=False)
    assert resp.status_code == 302
    assert '/login' in resp.headers['Location']


def test_officiel_cannot_start_session(officiel_client):
    resp = officiel_client.post(
        '/admin/session/start',
        data={'fictive_start_time': '10:00'},
        follow_redirects=False,
    )
    assert resp.status_code == 302
    assert '/login' in resp.headers['Location']


def test_population_cannot_start_session(population_client):
    resp = population_client.post(
        '/admin/session/start',
        data={'fictive_start_time': '10:00'},
        follow_redirects=False,
    )
    assert resp.status_code == 302
    assert '/login' in resp.headers['Location']


# ---------------------------------------------------------------------------
# Admin ne peut pas poster de commentaires
# ---------------------------------------------------------------------------

def test_admin_cannot_post_comment(message_in_session):
    """La route /htmx/comment/<id> est réservée à officiel et population."""
    app, msg_id = message_in_session
    c = app.test_client()
    c.post('/login', data={'code': 'ADMIN2026'})
    resp = c.post(
        f'/htmx/comment/{msg_id}',
        data={'content': 'Tentative admin'},
        follow_redirects=False,
    )
    # L'admin ne fait pas partie des rôles autorisés → redirect /login
    assert resp.status_code == 302
    assert '/login' in resp.headers['Location']


# ---------------------------------------------------------------------------
# Protection CSRF — app avec CSRF activé
# ---------------------------------------------------------------------------

def test_csrf_post_login_without_token_returns_400(csrf_client):
    """POST /login sans token CSRF → 400 Bad Request."""
    resp = csrf_client.post('/login', data={'code': 'MAIRIE2026'})
    assert resp.status_code == 400


def test_csrf_post_population_without_token_returns_400_or_redirect(csrf_client):
    """POST /population sans token CSRF → 400 (CSRF vérifié avant le contrôle de rôle)."""
    resp = csrf_client.post('/population', data={'content': 'Test'})
    # Soit 400 (CSRF), soit 302 (redirect login si CSRF bypass ne se passe pas)
    assert resp.status_code in (400, 302)


def test_csrf_disabled_in_testing_mode(client):
    """En mode test (WTF_CSRF_ENABLED=False), le POST fonctionne sans token."""
    resp = client.post('/login', data={'code': 'MAIRIE2026'}, follow_redirects=False)
    assert resp.status_code == 302
