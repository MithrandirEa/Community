import threading
import time
from datetime import datetime, timezone


def _publish_scheduled_messages() -> None:
    """
    Publie les messages programmés dont l'heure fictive cible est atteinte.
    Doit être appelée dans un app_context actif.
    """
    from app.models import db, Session, Message

    active_session = Session.query.filter_by(is_active=True).first()
    if not active_session or not active_session.real_started_at:
        return

    current_fictive = active_session.get_fictive_minutes()

    pending = (
        Message.query
        .filter_by(session_id=active_session.id, is_published=False)
        .filter(Message.scheduled_for_minutes <= current_fictive)
        .all()
    )

    if not pending:
        return

    now = datetime.now(timezone.utc).replace(tzinfo=None)
    for msg in pending:
        msg.is_published = True
        msg.real_published_at = now

    db.session.commit()


def _scheduler_loop(app) -> None:
    """Boucle infinie du thread démon — vérification toutes les 5 secondes."""
    while True:
        try:
            with app.app_context():
                _publish_scheduled_messages()
        except Exception:
            # Ne jamais planter le thread démon
            pass
        time.sleep(5)


def start_scheduler(app) -> None:
    """Démarre le thread démon de publication des messages programmés."""
    thread = threading.Thread(
        target=_scheduler_loop,
        args=(app,),
        daemon=True,
        name='community-scheduler',
    )
    thread.start()
