import os
import secrets


# --- Persistence de la SECRET_KEY entre les redémarrages ---
_instance_dir = os.path.join(os.path.dirname(__file__), 'instance')
_key_file = os.path.join(_instance_dir, 'secret.key')


def _load_or_create_secret_key() -> str:
    """Génère la SECRET_KEY une seule fois et la persiste dans instance/secret.key."""
    os.makedirs(_instance_dir, exist_ok=True)
    if os.path.exists(_key_file):
        with open(_key_file, 'r') as f:
            return f.read().strip()
    key = secrets.token_hex(32)
    with open(_key_file, 'w') as f:
        f.write(key)
    return key


class Config:
    SECRET_KEY = _load_or_create_secret_key()

    # Base de données SQLite embarquée
    SQLALCHEMY_DATABASE_URI = 'sqlite:///community.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Limite upload : 2 Mo
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024

    # Dossier racine de la photothèque (persistante)
    PHOTOS_FOLDER = os.path.join(os.path.dirname(__file__), 'app', 'static', 'photos')

    # Types MIME acceptés pour les uploads
    ALLOWED_MIME_TYPES = {'image/jpeg', 'image/png', 'image/webp'}

    # CSRF actif sur toutes les requêtes POST
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600  # 1 heure
