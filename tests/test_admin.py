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
- POST /admin/namepacks/<id>/entries/<entry_id>/avatar → upload/suppression avatar
"""

import io
from unittest.mock import mock_open, patch

import pytest

from app import db
from app.models import Session as SimSession, Config as AppConfig, NamePack, NameEntry


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


# ---------------------------------------------------------------------------
# POST /admin/namepacks/<pack_id>/entries
# ---------------------------------------------------------------------------

@pytest.fixture
def pack_in_db(app):
    """Crée un NamePack vide en base et retourne (app, pack_id)."""
    with app.app_context():
        pack = NamePack(name='Pack Test')
        db.session.add(pack)
        db.session.commit()
        pack_id = pack.id
    return app, pack_id


def test_namepack_add_entry_adds_new_entry(pack_in_db, admin_client):
    """Ajout nominal : l'entrée est bien créée en base."""
    app, pack_id = pack_in_db
    resp = admin_client.post(
        f'/admin/namepacks/{pack_id}/entries',
        data={'entry-role': 'officiel', 'entry-label': 'Jean Dupont'},
        follow_redirects=False,
    )
    assert resp.status_code == 302
    with app.app_context():
        entry = NameEntry.query.filter_by(pack_id=pack_id, role='officiel', label='Jean Dupont').first()
        assert entry is not None


def test_namepack_add_entry_duplicate_flashes_error(pack_in_db, admin_client):
    """Doublon (même pack, même rôle, même label) → flash d'erreur, pas d'insert."""
    app, pack_id = pack_in_db
    # Première insertion
    admin_client.post(
        f'/admin/namepacks/{pack_id}/entries',
        data={'entry-role': 'officiel', 'entry-label': 'Marie Curie'},
        follow_redirects=False,
    )
    # Tentative de doublon
    resp = admin_client.post(
        f'/admin/namepacks/{pack_id}/entries',
        data={'entry-role': 'officiel', 'entry-label': 'Marie Curie'},
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert 'Marie Curie' in resp.get_data(as_text=True)
    with app.app_context():
        count = NameEntry.query.filter_by(pack_id=pack_id, role='officiel', label='Marie Curie').count()
        assert count == 1


def test_namepack_add_entry_invalid_role_flashes_error(pack_in_db, admin_client):
    """Rôle invalide → redirection sans insert."""
    app, pack_id = pack_in_db
    resp = admin_client.post(
        f'/admin/namepacks/{pack_id}/entries',
        data={'entry-role': 'inconnu', 'entry-label': 'Test'},
        follow_redirects=False,
    )
    assert resp.status_code == 302
    with app.app_context():
        assert NameEntry.query.filter_by(pack_id=pack_id).count() == 0


def test_namepack_add_entry_empty_label_flashes_error(pack_in_db, admin_client):
    """Label vide → redirection sans insert."""
    app, pack_id = pack_in_db
    resp = admin_client.post(
        f'/admin/namepacks/{pack_id}/entries',
        data={'entry-role': 'population', 'entry-label': '   '},
        follow_redirects=False,
    )
    assert resp.status_code == 302
    with app.app_context():
        assert NameEntry.query.filter_by(pack_id=pack_id).count() == 0


# ---------------------------------------------------------------------------
# POST /admin/namepacks/<pack_id>/entries/<entry_id>/avatar
# ---------------------------------------------------------------------------

# Magic bytes PNG minimaux (< 512 Ko, mime valide)
_FAKE_PNG = b'\x89PNG\r\n\x1a\n' + b'\x00' * 50
# Bytes invalides (pas de magic bytes reconnus)
_FAKE_TXT = b'This is not an image file.' + b'\x00' * 10


@pytest.fixture
def entry_in_db(pack_in_db):
    """Crée un NameEntry dans le pack et retourne (app, pack_id, entry_id)."""
    app, pack_id = pack_in_db
    with app.app_context():
        entry = NameEntry(pack_id=pack_id, role='officiel', label='Dupont')
        db.session.add(entry)
        db.session.commit()
        entry_id = entry.id
    return app, pack_id, entry_id


def test_namepack_entry_avatar_no_file_flashes_error(entry_in_db, admin_client):
    """Aucun fichier joint → flash erreur, redirect."""
    app, pack_id, entry_id = entry_in_db
    resp = admin_client.post(
        f'/admin/namepacks/{pack_id}/entries/{entry_id}/avatar',
        data={},
        content_type='multipart/form-data',
        follow_redirects=False,
    )
    assert resp.status_code == 302
    with app.app_context():
        entry = db.session.get(NameEntry, entry_id)
        assert entry.avatar_filename is None


def test_namepack_entry_avatar_invalid_mime_flashes_error(entry_in_db, admin_client):
    """Fichier sans magic bytes valides → flash erreur, avatar_filename inchangé."""
    app, pack_id, entry_id = entry_in_db
    with patch('app.routes.admin.os.makedirs'):
        resp = admin_client.post(
            f'/admin/namepacks/{pack_id}/entries/{entry_id}/avatar',
            data={'avatar': (io.BytesIO(_FAKE_TXT), 'file.txt')},
            content_type='multipart/form-data',
            follow_redirects=False,
        )
    assert resp.status_code == 302
    with app.app_context():
        entry = db.session.get(NameEntry, entry_id)
        assert entry.avatar_filename is None


def test_namepack_entry_avatar_too_large_flashes_error(entry_in_db, admin_client):
    """Fichier > 512 Ko → flash erreur, avatar_filename inchangé."""
    app, pack_id, entry_id = entry_in_db
    oversized = _FAKE_PNG + b'\x00' * (512 * 1024)  # > 512 Ko
    with patch('app.routes.admin.os.makedirs'):
        resp = admin_client.post(
            f'/admin/namepacks/{pack_id}/entries/{entry_id}/avatar',
            data={'avatar': (io.BytesIO(oversized), 'big.png')},
            content_type='multipart/form-data',
            follow_redirects=False,
        )
    assert resp.status_code == 302
    with app.app_context():
        entry = db.session.get(NameEntry, entry_id)
        assert entry.avatar_filename is None


def test_namepack_entry_avatar_upload_saves_filename(entry_in_db, admin_client):
    """Upload PNG valide → avatar_filename renseigné et se termine par .png."""
    app, pack_id, entry_id = entry_in_db
    with patch('app.routes.admin.os.makedirs'), \
         patch('app.routes.admin.open', mock_open(), create=True):
        resp = admin_client.post(
            f'/admin/namepacks/{pack_id}/entries/{entry_id}/avatar',
            data={'avatar': (io.BytesIO(_FAKE_PNG), 'avatar.png')},
            content_type='multipart/form-data',
            follow_redirects=False,
        )
    assert resp.status_code == 302
    with app.app_context():
        entry = db.session.get(NameEntry, entry_id)
        assert entry.avatar_filename is not None
        assert entry.avatar_filename.endswith('.png')


def test_namepack_entry_avatar_delete_clears_filename(entry_in_db, admin_client):
    """POST delete_avatar=1 → avatar_filename remis à None."""
    app, pack_id, entry_id = entry_in_db
    # Pré-remplir un avatar fictif en base (sans fichier réel sur disque)
    with app.app_context():
        entry = db.session.get(NameEntry, entry_id)
        entry.avatar_filename = 'abc123.png'
        db.session.commit()

    with patch('app.routes.admin.os.path.exists', return_value=False):
        resp = admin_client.post(
            f'/admin/namepacks/{pack_id}/entries/{entry_id}/avatar',
            data={'delete_avatar': '1'},
            follow_redirects=False,
        )
    assert resp.status_code == 302
    with app.app_context():
        entry = db.session.get(NameEntry, entry_id)
        assert entry.avatar_filename is None
