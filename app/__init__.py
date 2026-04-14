import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_wtf.csrf import CSRFProtect

# Extensions partagées — initialisées sans app (pattern factory)
db = SQLAlchemy()
bcrypt = Bcrypt()
csrf = CSRFProtect()


def create_app(test_config: dict | None = None) -> Flask:
    """Factory principale de l'application Community."""
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object('config.Config')

    if test_config is not None:
        app.config.update(test_config)

    # Création du dossier instance/ si absent
    os.makedirs(app.instance_path, exist_ok=True)

    # Création du dossier photothèque si absent
    os.makedirs(app.config['PHOTOS_FOLDER'], exist_ok=True)

    # Initialisation des extensions
    db.init_app(app)
    bcrypt.init_app(app)
    csrf.init_app(app)

    # Enregistrement des blueprints
    from app.routes.auth import auth_bp
    from app.routes.admin import admin_bp
    from app.routes.officiel import officiel_bp
    from app.routes.population import population_bp
    from app.routes.htmx import htmx_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(officiel_bp)
    app.register_blueprint(population_bp)
    app.register_blueprint(htmx_bp, url_prefix='/htmx')

    # Création des tables et valeurs par défaut
    with app.app_context():
        from app import models  # noqa — enregistre les modèles dans les métadonnées SQLAlchemy
        db.create_all()
        _init_defaults()

    # Démarrage du thread scheduler (publication messages programmés)
    from app.utils.scheduler import start_scheduler
    start_scheduler(app)

    return app


def _init_defaults() -> None:
    """Insère les clés de configuration par défaut si elles sont absentes."""
    from app.models import Config

    defaults = [
        ('code_officiel', 'MAIRIE2026'),
        ('code_population', 'CITOYEN2026'),
        ('scenario_actif', ''),
    ]
    for key, value in defaults:
        if db.session.get(Config, key) is None:
            db.session.add(Config(key=key, value=value))

    # Code admin hashé bcrypt — jamais stocké en clair
    if db.session.get(Config, 'code_admin') is None:
        hashed = bcrypt.generate_password_hash('ADMIN2026').decode('utf-8')
        db.session.add(Config(key='code_admin', value=hashed))

    db.session.commit()
