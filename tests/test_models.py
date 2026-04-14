"""
Tests unitaires des modèles SQLAlchemy.

Couvre :
- Session : get_fictive_minutes, get_fictive_time_str, real_to_fictive, fictive_start_str
- Message  : fictive_time_str, comment_count
- Comment  : fictive_time_str
- Config   : clé primaire string
"""

from datetime import datetime, timedelta, timezone

import pytest

from app import db
from app.models import Comment, Config as AppConfig
from app.models import Message, Session as SimSession


# ---------------------------------------------------------------------------
# Session
# ---------------------------------------------------------------------------

class TestSessionFictiveMinutes:

    def test_get_fictive_minutes_when_inactive_returns_start(self, app):
        """Session inactive : retourne exactement fictive_start_minutes."""
        with app.app_context():
            s = SimSession(fictive_start_minutes=600, is_active=False)
            assert s.get_fictive_minutes() == 600.0

    def test_get_fictive_minutes_active_no_started_at_returns_start(self, app):
        """Session active mais sans real_started_at : retourne fictive_start_minutes."""
        with app.app_context():
            s = SimSession(fictive_start_minutes=540, is_active=True, real_started_at=None)
            assert s.get_fictive_minutes() == 540.0

    def test_get_fictive_minutes_active_includes_elapsed(self, app):
        """Session active depuis 30 min : minutes fictives ≈ start + 30."""
        with app.app_context():
            started = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(minutes=30)
            s = SimSession(
                fictive_start_minutes=600,
                is_active=True,
                real_started_at=started,
            )
            result = s.get_fictive_minutes()
            assert 629.0 < result < 631.0


class TestSessionFormatMinutes:

    def test_format_zero_minutes(self, app):
        with app.app_context():
            assert SimSession._format_minutes(0) == '00:00'

    def test_format_nine_hundred_minutes(self, app):
        with app.app_context():
            assert SimSession._format_minutes(540) == '09:00'

    def test_format_last_minute_of_day(self, app):
        with app.app_context():
            assert SimSession._format_minutes(1439) == '23:59'

    def test_format_midnight_wraps_around(self, app):
        """1440 min = 24:00 → 00:00 (modulo 24h)."""
        with app.app_context():
            assert SimSession._format_minutes(1440) == '00:00'


class TestSessionGetFictiveTimeStr:

    def test_returns_hhmm_format(self, app):
        with app.app_context():
            s = SimSession(fictive_start_minutes=570, is_active=False)
            assert s.get_fictive_time_str() == '09:30'


class TestSessionRealToFictive:

    def test_no_started_at_returns_current_fictive(self, app):
        """Sans real_started_at, retourne l'heure fictive courante (= start)."""
        with app.app_context():
            s = SimSession(fictive_start_minutes=600, is_active=False, real_started_at=None)
            result = s.real_to_fictive(datetime.now(timezone.utc).replace(tzinfo=None))
            assert result == '10:00'

    def test_with_45_min_offset(self, app):
        """real_dt = started_at + 45 min → fictif = start + 45 min."""
        with app.app_context():
            started = datetime(2024, 6, 1, 8, 0, 0)
            real_dt = datetime(2024, 6, 1, 8, 45, 0)
            s = SimSession(fictive_start_minutes=600, is_active=True, real_started_at=started)
            assert s.real_to_fictive(real_dt) == '10:45'

    def test_with_zero_offset(self, app):
        """real_dt = started_at → fictif = start."""
        with app.app_context():
            started = datetime(2024, 6, 1, 8, 0, 0)
            s = SimSession(fictive_start_minutes=600, is_active=True, real_started_at=started)
            assert s.real_to_fictive(started) == '10:00'


class TestSessionFictiveStartStr:

    def test_property_returns_hhmm(self, app):
        with app.app_context():
            s = SimSession(fictive_start_minutes=480)  # 08:00
            assert s.fictive_start_str == '08:00'


# ---------------------------------------------------------------------------
# Message
# ---------------------------------------------------------------------------

class TestMessageFictiveTimeStr:

    def test_no_published_at_returns_placeholder(self, app):
        """Message sans real_published_at retourne '--:--'."""
        with app.app_context():
            s = SimSession(fictive_start_minutes=600, is_active=False)
            db.session.add(s)
            db.session.flush()
            m = Message(
                session_id=s.id,
                role='officiel',
                content='test',
                real_published_at=None,
            )
            db.session.add(m)
            db.session.flush()
            assert m.fictive_time_str == '--:--'

    def test_with_published_at_returns_hhmm(self, app):
        """Message avec real_published_at retourne l'heure fictive correcte."""
        with app.app_context():
            started = datetime(2024, 6, 1, 8, 0, 0)
            pub = datetime(2024, 6, 1, 8, 30, 0)  # +30 min → fictif 10:30
            s = SimSession(
                fictive_start_minutes=600,
                is_active=True,
                real_started_at=started,
            )
            db.session.add(s)
            db.session.flush()
            m = Message(
                session_id=s.id,
                role='officiel',
                content='test',
                is_published=True,
                real_published_at=pub,
            )
            db.session.add(m)
            db.session.flush()
            assert m.fictive_time_str == '10:30'


class TestMessageCommentCount:

    def test_count_zero_when_no_comments(self, app):
        with app.app_context():
            s = SimSession(fictive_start_minutes=600, is_active=False)
            db.session.add(s)
            db.session.flush()
            m = Message(
                session_id=s.id,
                role='officiel',
                content='test',
                real_published_at=None,
            )
            db.session.add(m)
            db.session.flush()
            assert m.comment_count == 0

    def test_count_reflects_added_comments(self, app):
        with app.app_context():
            s = SimSession(fictive_start_minutes=600, is_active=False)
            db.session.add(s)
            db.session.flush()
            m = Message(
                session_id=s.id,
                role='officiel',
                content='test',
                real_published_at=datetime.now(timezone.utc).replace(tzinfo=None),
            )
            db.session.add(m)
            db.session.flush()
            c1 = Comment(
                message_id=m.id, role='population',
                content='rep1', real_created_at=datetime.now(timezone.utc).replace(tzinfo=None),
            )
            c2 = Comment(
                message_id=m.id, role='officiel',
                content='rep2', real_created_at=datetime.now(timezone.utc).replace(tzinfo=None),
            )
            db.session.add_all([c1, c2])
            db.session.flush()
            assert m.comment_count == 2


# ---------------------------------------------------------------------------
# Comment
# ---------------------------------------------------------------------------

class TestCommentFictiveTimeStr:

    def test_returns_correct_fictive_time(self, app):
        """Commentaire créé 15 min après le démarrage → fictif = start + 15 min."""
        with app.app_context():
            started = datetime(2024, 6, 1, 8, 0, 0)
            s = SimSession(
                fictive_start_minutes=600,
                is_active=True,
                real_started_at=started,
            )
            db.session.add(s)
            db.session.flush()
            m = Message(
                session_id=s.id,
                role='officiel',
                content='test',
                real_published_at=started,
            )
            db.session.add(m)
            db.session.flush()
            c = Comment(
                message_id=m.id,
                role='population',
                content='réponse',
                real_created_at=datetime(2024, 6, 1, 8, 15, 0),
            )
            db.session.add(c)
            db.session.flush()
            assert c.fictive_time_str == '10:15'

    def test_returns_placeholder_when_no_session(self, app):
        """Comment sans message·session rattaché retourne '--:--'."""
        with app.app_context():
            c = Comment(
                message_id=9999,  # id inexistant — relation None
                role='population',
                content='orphan',
                real_created_at=datetime.now(timezone.utc).replace(tzinfo=None),
            )
            # Sans flush (pas en base) : message est None → '--:--'
            assert c.fictive_time_str == '--:--'


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

class TestConfig:

    def test_string_primary_key_insert_and_get(self, app):
        """Config accepte une clé string comme PK et est interrogeable par get()."""
        with app.app_context():
            c = AppConfig(key='test_key', value='test_value')
            db.session.add(c)
            db.session.flush()
            result = db.session.get(AppConfig, 'test_key')
            assert result is not None
            assert result.value == 'test_value'

    def test_default_codes_are_initialized(self, app):
        """_init_defaults() insère les codes par défaut au démarrage."""
        with app.app_context():
            cfg_o = db.session.get(AppConfig, 'code_officiel')
            cfg_p = db.session.get(AppConfig, 'code_population')
            cfg_a = db.session.get(AppConfig, 'code_admin')
            assert cfg_o is not None and cfg_o.value == 'MAIRIE2026'
            assert cfg_p is not None and cfg_p.value == 'CITOYEN2026'
            assert cfg_a is not None  # hash bcrypt, non vide
            assert cfg_a.value != ''
