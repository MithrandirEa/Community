from datetime import datetime, timezone

from flask import Blueprint, redirect, render_template, session as flask_session, url_for
from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional, Regexp

from app import db
from app.models import Config, Message, Photo
from app.models import Session as SimSession
from app.utils.helpers import require_role

officiel_bp = Blueprint('officiel', __name__)


class OfficielMessageForm(FlaskForm):
    content = TextAreaField(
        'Message',
        validators=[
            DataRequired(message='Le message ne peut pas être vide.'),
            Length(max=1000, message='Message trop long (max 1000 caractères).'),
        ],
    )
    # Chemin relatif depuis static/photos/ (ex: "scenario1/uuid_photo.jpg")
    photo_filename = StringField(validators=[Optional()])
    is_scheduled = BooleanField('Programmer')
    scheduled_time = StringField(
        validators=[
            Optional(),
            Regexp(r'^\d{2}:\d{2}$', message='Format HH:MM attendu.'),
        ]
    )
    submit = SubmitField('Publier')


@officiel_bp.route('/officiel', methods=['GET', 'POST'])
@require_role('officiel')
def feed():
    form = OfficielMessageForm()
    active_session = SimSession.query.filter_by(is_active=True).first()
    error = None

    if form.validate_on_submit():
        if not active_session:
            error = 'Aucune session active. Contactez votre animateur.'
        else:
            is_scheduled = form.is_scheduled.data
            scheduled_minutes = None

            if is_scheduled:
                raw = (form.scheduled_time.data or '').strip()
                if not raw:
                    error = "Indiquez l'heure de programmation (HH:MM)."
                else:
                    try:
                        h, m = raw.split(':')
                        scheduled_minutes = int(h) * 60 + int(m)
                    except (ValueError, AttributeError):
                        error = "Format d'heure invalide (attendu HH:MM)."

            if not error:
                photo_fn = (form.photo_filename.data or '').strip() or None

                # Validation : la photo doit exister en base (prévient le path traversal)
                if photo_fn:
                    parts = photo_fn.split('/', 1)
                    if len(parts) == 2:
                        p_scenario, p_filename = parts
                        valid_photo = Photo.query.filter_by(
                            scenario_folder=p_scenario, filename=p_filename
                        ).first()
                        if not valid_photo:
                            photo_fn = None
                    else:
                        photo_fn = None

                msg = Message(
                    session_id=active_session.id,
                    role='officiel',
                    content=form.content.data.strip(),
                    photo_filename=photo_fn,
                    is_scheduled=is_scheduled,
                    scheduled_for_minutes=scheduled_minutes,
                    is_published=not is_scheduled,
                    real_published_at=datetime.now(timezone.utc).replace(tzinfo=None) if not is_scheduled else None,
                )
                db.session.add(msg)
                db.session.commit()
                return redirect(url_for('officiel.feed'))

    messages = []
    pending_messages = []
    fictive_time = '--:--'
    if active_session:
        fictive_time = active_session.get_fictive_time_str()
        messages = (
            Message.query
            .filter_by(session_id=active_session.id, is_published=True)
            .order_by(Message.real_published_at.desc())
            .all()
        )
        pending_messages = (
            Message.query
            .filter_by(session_id=active_session.id, is_published=False, is_scheduled=True)
            .order_by(Message.scheduled_for_minutes.asc())
            .all()
        )

    # Photos disponibles dans le scénario actif
    cfg_scenario = db.session.get(Config, 'scenario_actif')
    scenario = cfg_scenario.value if cfg_scenario else ''
    photos = []
    if scenario:
        photos = (
            Photo.query
            .filter_by(scenario_folder=scenario)
            .order_by(Photo.uploaded_at.desc())
            .all()
        )

    return render_template(
        'officiel/feed.html',
        form=form,
        messages=messages,
        pending_messages=pending_messages,
        active_session=active_session,
        fictive_time=fictive_time,
        error=error,
        photos=photos,
        scenario=scenario,
    )

