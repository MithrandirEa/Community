"""
Tests du back-office admin.

Couvre :
- GET  /admin/                  → protégé (redirect si non admin)
- GET  /admin/                  → 200 pour admin
- POST /admin/session/start     → crée une session active
- POST /admin/session/start     → heure invalide → pas de session créée
- POST /admin/session/stop      → stoppe la session active
- POST /admin/session/stop      → sans session active → flash d'erreur
- POST /admin/session/reset     → supprime toutes les sessions
- GET  /admin/config            → 200
- POST /admin/config            → met à jour les codes officiel/population
- GET  /admin/photos            → 200
"""

import pytest

from app import db
from app.models import Session as SimSession, Config as AppConfig


# ---------------------------------------------------------------------------
# Protection des routes admin
# ---------------------------------------------------------------------------

def test_admin_dashboard_not_logged_in_redirects(client):
    resp = client.get('/admin/', follow_redirects=False)
    assert resp.status_code == 302
    assert '/login' in resp.headers['Location']


def test_admin_dashboard_officiel_cannot_access(officiel_client):
    resp = officiel_client.get('/admin/', follow_redirects=False)
    assert resp.status_code == 302
    assert '/login' in resp.headers['Location']


def test_admin_dashboard_population_cannot_access(population_client):
    resp = population_client.get('/admin/', follow_redirects=False)
    assert resp.status_code == 302
    assert '/login' in resp.headers['Location']


def test_admin_dashboard_returns_200_for_admin(admin_client):
    resp = admin_client.get('/admin/')
    assert resp.status_code == 200


# ---------------------------------------------------------------------------
# POST /admin/session/start
# ---------------------------------------------------------------------------

def test_admin_session_start_creates_active_session(app, admin_client):
    resp = admin_client.post(
        '/admin/session/start',
        data={'fictive_start_time': '09:00'},
        follow_redirects=False,
    )
    assert resp.status_code == 302
    with app.app_context():
        session = SimSession.query.filter_by(is_active=True).first()
        assert session is not None
        assert session.fictive_start_minutes == 9 * 60


def test_admin_session_start_sets_correct_start_time(app, admin_client):
    admin_client.post(
        '/admin/session/start',
        data={'fictive_start_time': '14:30'},
    )
    with app.app_context():
        session = SimSession.query.filter_by(is_active=True).first()
        assert session is not None
        assert session.fictive_start_minutes == 14 * 60 + 30


def test_admin_session_start_deactivates_previous_session(app, admin_client):
    """Démarrer une nouvelle session désactive la précédente."""
    admin_client.post('/admin/session/start', data={'fictive_start_time': '08:00'})
    admin_client.post('/admin/session/start', data={'fictive_start_time': '12:00'})
    with app.app_context():
        active = SimSession.query.filter_by(is_active=True).all()
        assert len(active) == 1
        assert active[0].fictive_start_minutes == 12 * 60


def test_admin_session_start_invalid_time_redirects_without_session(app, admin_client):
    """Heure invalide : flash d'erreur, pas de session créée."""
    admin_client.post(
        '/admin/session/start',
        data={'fictive_start_time': 'INVALID'},
    )
    with app.app_context():
        session = SimSession.query.filter_by(is_active=True).first()
        assert session is None


# ---------------------------------------------------------------------------
# POST /admin/session/stop
# ---------------------------------------------------------------------------

def test_admin_session_stop_deactivates_session(app, session_admin_client):
    resp = session_admin_client.post(
        '/admin/session/stop',
        follow_redirects=False,
    )
    assert resp.status_code == 302
    with app.app_context():
        session = SimSession.query.filter_by(is_active=True).first()
        assert session is None


def test_admin_session_stop_sets_ended_at(app, session_admin_client):
    session_admin_client.post('/admin/session/stop')
    with app.app_context():
        session = SimSession.query.order_by(SimSession.id.desc()).first()
        assert session is not None
        assert session.ended_at is not None


def test_admin_session_stop_no_active_session_still_redirects(admin_client):
    """Sans session active, stop redirige quand même (flash erreur)."""
    resp = admin_client.post('/admin/session/stop', follow_redirects=False)
    assert resp.status_code == 302


# ---------------------------------------------------------------------------
# POST /admin/session/reset
# ---------------------------------------------------------------------------

def test_admin_session_reset_deletes_all_sessions(app, session_admin_client):
    session_admin_client.post('/admin/session/reset', follow_redirects=False)
    with app.app_context():
        assert SimSession.query.count() == 0


def test_admin_session_reset_redirects(session_admin_client):
    resp = session_admin_client.post(
        '/admin/session/reset',
        follow_redirects=False,
    )
    assert resp.status_code == 302


# ---------------------------------------------------------------------------
# GET /admin/config  +  POST /admin/config
# ---------------------------------------------------------------------------

def test_admin_config_get_returns_200(admin_client):
    resp = admin_client.get('/admin/config')
    assert resp.status_code == 200


def test_admin_config_post_updates_codes(app, admin_client):
    resp = admin_client.post(
        '/admin/config',
        data={
            'code_officiel': 'NOUVEAU_OFFICIEL',
            'code_population': 'NOUVEAU_POPULATION',
            'new_admin_code': '',
        },
        follow_redirects=False,
    )
    assert resp.status_code == 302
    with app.app_context():
        cfg_o = db.session.get(AppConfig, 'code_officiel')
        cfg_p = db.session.get(AppConfig, 'code_population')
        assert cfg_o.value == 'NOUVEAU_OFFICIEL'
        assert cfg_p.value == 'NOUVEAU_POPULATION'


# ---------------------------------------------------------------------------
# GET /admin/photos
# ---------------------------------------------------------------------------

def test_admin_photos_returns_200(admin_client):
    resp = admin_client.get('/admin/photos')
    assert resp.status_code == 200
