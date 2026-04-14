from datetime import datetime, timezone

from app import db


class Session(db.Model):
    """Session de simulation. Une seule session active à la fois."""
    __tablename__ = 'session'

    id = db.Column(db.Integer, primary_key=True)
    # Heure fictive de début en minutes depuis minuit (ex. 540 = 09:00)
    fictive_start_minutes = db.Column(db.Integer, default=540, nullable=False)
    # Heure réelle de démarrage de la session (None = session non démarrée)
    real_started_at = db.Column(db.DateTime, nullable=True)
    ended_at = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=False, nullable=False)

    messages = db.relationship(
        'Message', backref='session', lazy='dynamic', cascade='all, delete-orphan'
    )

    # --- Helpers horloge fictive ---

    def get_fictive_minutes(self) -> float:
        """Retourne l'heure fictive courante en minutes depuis minuit."""
        if not self.is_active or not self.real_started_at:
            return float(self.fictive_start_minutes)
        elapsed = (datetime.now(timezone.utc).replace(tzinfo=None) - self.real_started_at).total_seconds() / 60
        return self.fictive_start_minutes + elapsed

    @staticmethod
    def _format_minutes(total_minutes: float) -> str:
        """Formate des minutes en chaîne HH:MM."""
        m = int(total_minutes)
        return f'{(m // 60) % 24:02d}:{m % 60:02d}'

    def get_fictive_time_str(self) -> str:
        """Retourne l'heure fictive courante au format HH:MM."""
        return self._format_minutes(self.get_fictive_minutes())

    def real_to_fictive(self, real_dt: datetime) -> str:
        """Convertit une datetime réelle en heure fictive HH:MM."""
        if not self.real_started_at:
            return self.get_fictive_time_str()
        elapsed = (real_dt - self.real_started_at).total_seconds() / 60
        return self._format_minutes(self.fictive_start_minutes + elapsed)

    @property
    def fictive_start_str(self) -> str:
        """Retourne l'heure de début fictive configurée au format HH:MM."""
        return self._format_minutes(self.fictive_start_minutes)


class Message(db.Model):
    """Message publié par la cellule de crise ou la population."""
    __tablename__ = 'message'

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('session.id'), nullable=False)
    # Rôle de l'auteur : 'officiel' | 'population'
    role = db.Column(db.String(20), nullable=False)
    content = db.Column(db.Text, nullable=False)
    # Nom du fichier photo (format UUID_nomfichier.ext) ou None
    photo_filename = db.Column(db.String(255), nullable=True)
    # Heure réelle de publication (None si programmé mais pas encore publié)
    real_published_at = db.Column(db.DateTime, nullable=True)
    # True = message créé via le bouton "Programmer"
    is_scheduled = db.Column(db.Boolean, default=False, nullable=False)
    # Heure fictive cible en minutes depuis minuit (None si publication immédiate)
    scheduled_for_minutes = db.Column(db.Integer, nullable=True)
    # False = en attente de publication (message programmé non encore déclenché)
    is_published = db.Column(db.Boolean, default=True, nullable=False)

    comments = db.relationship(
        'Comment', backref='message', lazy='dynamic', cascade='all, delete-orphan'
    )

    @property
    def fictive_time_str(self) -> str:
        """Heure fictive de publication au format HH:MM."""
        try:
            if not self.real_published_at or not self.session:
                return '--:--'
            return self.session.real_to_fictive(self.real_published_at)
        except Exception:
            return '--:--'

    @property
    def comment_count(self) -> int:
        return self.comments.count()


class Comment(db.Model):
    """Réponse à un message (croisée : officiel ↔ population)."""
    __tablename__ = 'comment'

    id = db.Column(db.Integer, primary_key=True)
    message_id = db.Column(db.Integer, db.ForeignKey('message.id'), nullable=False)
    # Rôle de l'auteur de la réponse : 'officiel' | 'population'
    role = db.Column(db.String(20), nullable=False)
    content = db.Column(db.Text, nullable=False)
    real_created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    @property
    def fictive_time_str(self) -> str:
        """Heure fictive de création de la réponse au format HH:MM."""
        try:
            if not self.message or not self.message.session:
                return '--:--'
            return self.message.session.real_to_fictive(self.real_created_at)
        except Exception:
            return '--:--'


class Photo(db.Model):
    """Photo de la photothèque persistante, organisée par dossier de scénario."""
    __tablename__ = 'photo'

    id = db.Column(db.Integer, primary_key=True)
    scenario_folder = db.Column(db.String(255), nullable=False)
    # Nom sur disque : UUID_nomoriginal.ext (sécurisé)
    filename = db.Column(db.String(255), nullable=False)
    original_name = db.Column(db.String(255), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


class Config(db.Model):
    """Configuration clé/valeur de l'application (codes, scénario actif…)."""
    __tablename__ = 'config'

    key = db.Column(db.String(50), primary_key=True)
    value = db.Column(db.Text, nullable=False)
