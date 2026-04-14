"""
Tests des routes d'authentification.

Couvre :
- GET  /         → redirect /login
- GET  /login    → 200
- POST /login    → code correct   → redirect vers le bon feed
- POST /login    → code incorrect → 200 + message d'erreur
- GET  /logout   → clear session + redirect /login
- GET  /login    → déjà connecté  → redirect vers son feed
"""

import pytest


# ---------------------------------------------------------------------------
# GET /  et  GET /login
# ---------------------------------------------------------------------------

def test_index_redirects_to_login(client):
    resp = client.get('/', follow_redirects=False)
    assert resp.status_code == 302
    assert '/login' in resp.headers['Location']


def test_login_get_returns_200(client):
    resp = client.get('/login')
    assert resp.status_code == 200


def test_login_page_contains_form(client):
    resp = client.get('/login')
    body = resp.data.decode()
    assert 'form' in body.lower()
    assert 'code' in body.lower()


# ---------------------------------------------------------------------------
# POST /login — codes corrects
# ---------------------------------------------------------------------------

def test_login_officiel_code_redirects_to_officiel(client):
    resp = client.post('/login', data={'code': 'MAIRIE2026'}, follow_redirects=False)
    assert resp.status_code == 302
    assert '/officiel' in resp.headers['Location']


def test_login_population_code_redirects_to_population(client):
    resp = client.post('/login', data={'code': 'CITOYEN2026'}, follow_redirects=False)
    assert resp.status_code == 302
    assert '/population' in resp.headers['Location']


def test_login_admin_code_redirects_to_admin(client):
    resp = client.post('/login', data={'code': 'ADMIN2026'}, follow_redirects=False)
    assert resp.status_code == 302
    assert '/admin' in resp.headers['Location']


# ---------------------------------------------------------------------------
# POST /login — code incorrect
# ---------------------------------------------------------------------------

def test_login_wrong_code_returns_200(client):
    resp = client.post('/login', data={'code': 'MAUVAISCODE'})
    assert resp.status_code == 200


def test_login_wrong_code_shows_error_message(client):
    resp = client.post('/login', data={'code': 'MAUVAISCODE'})
    assert 'Code incorrect' in resp.data.decode()


def test_login_empty_code_returns_200(client):
    """Code vide : validation WTForms échoue (DataRequired) → 200 sans redirect."""
    resp = client.post('/login', data={'code': ''})
    assert resp.status_code == 200


# ---------------------------------------------------------------------------
# GET /logout
# ---------------------------------------------------------------------------

def test_logout_redirects_to_login(officiel_client):
    resp = officiel_client.get('/logout', follow_redirects=False)
    assert resp.status_code == 302
    assert '/login' in resp.headers['Location']


def test_logout_clears_role_officiel(officiel_client):
    officiel_client.get('/logout')
    resp = officiel_client.get('/officiel', follow_redirects=False)
    assert resp.status_code == 302
    assert '/login' in resp.headers['Location']


def test_logout_clears_role_population(population_client):
    population_client.get('/logout')
    resp = population_client.get('/population', follow_redirects=False)
    assert resp.status_code == 302
    assert '/login' in resp.headers['Location']


# ---------------------------------------------------------------------------
# Déjà connecté → redirect vers son propre feed
# ---------------------------------------------------------------------------

def test_already_officiel_login_redirects_to_officiel(officiel_client):
    resp = officiel_client.get('/login', follow_redirects=False)
    assert resp.status_code == 302
    assert '/officiel' in resp.headers['Location']


def test_already_population_login_redirects_to_population(population_client):
    resp = population_client.get('/login', follow_redirects=False)
    assert resp.status_code == 302
    assert '/population' in resp.headers['Location']


def test_already_admin_login_redirects_to_admin(admin_client):
    resp = admin_client.get('/login', follow_redirects=False)
    assert resp.status_code == 302
    assert '/admin' in resp.headers['Location']
